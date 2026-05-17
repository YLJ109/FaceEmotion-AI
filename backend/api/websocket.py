"""WebSocket 流处理路由"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import asyncio
import time
import uuid
import concurrent.futures
import json
import cv2
import numpy as np
from datetime import datetime
from contextlib import contextmanager
import logging

from core.config import ConfigManager
from core.database import DatabaseManager
from adaptation.active_learner import AdaptiveLearner
from music.generative_music import MusicGenerator
from optimizer.dynamic_inference import DynamicInferenceOptimizer

logger = logging.getLogger(__name__)
router = APIRouter()

_config_manager = None
_db_manager = None
_face_detector = None
_emotion_model = None
_adaptive_learner = None
_shared_executor = None
_music_generator = None
_inference_optimizer = None


def init_ws_router(
    config_manager: ConfigManager,
    db_manager: DatabaseManager,
    face_detector,
    emotion_model,
    adaptive_learner: AdaptiveLearner,
    executor: concurrent.futures.ThreadPoolExecutor,
    inference_optimizer: DynamicInferenceOptimizer = None
):
    """初始化路由依赖"""
    global _config_manager, _db_manager, _face_detector, _emotion_model, _adaptive_learner, _shared_executor, _music_generator, _inference_optimizer
    _config_manager = config_manager
    _db_manager = db_manager
    _face_detector = face_detector
    _emotion_model = emotion_model
    _adaptive_learner = adaptive_learner
    _shared_executor = executor
    _music_generator = MusicGenerator()
    _inference_optimizer = inference_optimizer
    logger.info(
        f"✅ WebSocket 处理器已初始化 | 置信度阈值: {config_manager.config.get('confidence_threshold', 0.6)}")
    if _inference_optimizer:
        logger.info("✅ WebSocket 推理优化器已启用")


def get_gpu_memory_usage():
    """获取 GPU 内存使用量"""
    try:
        import pynvml as nvidia_smi
        handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)
        mem_info = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)
        return round(mem_info.used / 1024**2, 1)
    except Exception:
        return 0.0


@router.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 实时视频流端点"""
    logger.info("🔌 WebSocket 连接请求到达")
    await websocket.accept()
    logger.info("✅ WebSocket 连接已建立")

    frame_queue = asyncio.Queue(maxsize=3)
    result_queue = asyncio.Queue(maxsize=5)
    stop_event = asyncio.Event()
    last_pong = time.time()
    connection_closed = False

    global_state_lock = asyncio.Lock()
    detection_state = {'enabled': True}

    async def heartbeat():
        """心跳检测"""
        while not stop_event.is_set():
            await asyncio.sleep(15)
            if connection_closed:
                break
            try:
                await websocket.send_json({"type": "ping"})
            except Exception:
                stop_event.set()
                break

    async def receiver():
        """接收帧数据"""
        nonlocal last_pong
        nonlocal connection_closed
        frame_count = 0
        try:
            while not stop_event.is_set():
                msg = await websocket.receive()
                if "bytes" in msg and msg["bytes"]:
                    data = msg["bytes"]
                    frame_count += 1
                    logger.debug(f"📥 收到第 {frame_count} 帧, 长度={len(data)} bytes")

                    try:
                        if len(data) >= 4:
                            offset = 1 if data[0] == 0x01 else 0
                            w = int(data[offset]) | (int(data[offset + 1]) << 8)
                            h = int(data[offset + 2]) | (int(data[offset + 3]) << 8)

                            expected_size = h * w * 4 + offset + 4
                            if len(data) < expected_size:
                                logger.error(f"❌ 帧数据不足: 期望={expected_size}, 实际={len(data)}")
                                continue

                            rgba = np.frombuffer(
                                data[offset + 4:], dtype=np.uint8).reshape(h, w, 4)
                            frame = rgba[:, :, :3][:, :, ::-1].copy()

                            if frame_queue.full():
                                try:
                                    frame_queue.get_nowait()
                                except asyncio.QueueEmpty:
                                    pass

                            try:
                                frame_queue.put_nowait(frame)
                            except asyncio.QueueFull:
                                pass
                        else:
                            logger.error(f"❌ 帧数据不足: len(data)={len(data)}")
                            continue
                    except Exception as e:
                        logger.error(f"❌ 帧解析失败: {e}, data_len={len(data)}")
                        continue
                elif "text" in msg and msg["text"]:
                    try:
                        message = json.loads(msg["text"])
                    except (json.JSONDecodeError, TypeError):
                        continue
                    if message.get('type') == 'ping':
                        await websocket.send_json({'type': 'pong'})
                    elif message.get('type') == 'pong':
                        last_pong = time.time()
                    elif message.get('type') == 'config_update':
                        _config_manager.update_config(
                            message.get('config', {}))
                        await websocket.send_json({'type': 'config_updated', 'status': 'success'})
                    elif message.get('type') == 'detection_control':
                        detection_state['enabled'] = message.get(
                            'enabled', True)
                        logger.info(
                            f"🎛️ 检测开关: {'开启' if detection_state['enabled'] else '关闭'}")
        except (WebSocketDisconnect, RuntimeError):
            connection_closed = True
            stop_event.set()
        except Exception as e:
            logger.error(f"❌ Receiver 异常: {e}")
            connection_closed = True
            stop_event.set()

    async def processor():
        """处理帧并检测情绪"""
        nonlocal last_pong
        loop = asyncio.get_event_loop()
        executor = _shared_executor
        _save_counter = 0
        _calibration_strength = 0.0  # ✅ 禁用自适应校准，使用原始置信度
        _last_face_bbox = None
        _last_emotion_cache = None
        _detect_counter = 0
        
        # ✅ 帧间隔配置
        # GPU模式: 不调帧，每帧都检测和识别
        # CPU模式: 帧间隔优化（行业标准）
        #   人脸检测: 每 4 帧检测 1 次 → 15fps 检测
        #   情绪识别: 每 2 帧识别 1 次 → 30fps 识别
        
        # 判断是否使用GPU模式
        use_gpu_mode = _config_manager.get('use_gpu', False) or _config_manager.get('performance_mode', 'cpu') == 'gpu'
        
        if use_gpu_mode:
            # GPU模式: 不调帧，每帧都处理
            FACE_DETECT_INTERVAL = 1  # 每帧都检测
            EMOTION_INFER_INTERVAL = 1  # 每帧都识别
            logger.info("🎮 GPU模式: 不调帧，每帧都进行人脸检测和情绪识别")
        else:
            # CPU模式: 使用帧间隔优化
            FACE_DETECT_INTERVAL = 4  # CPU 人脸检测间隔
            EMOTION_INFER_INTERVAL = 2  # CPU 情绪识别间隔
            logger.info("💻 CPU模式: 使用帧间隔优化")
        
        TRACKING_THRESHOLD = 5
        # ✅ 人脸框平滑系数（降低以减少框飞）
        # SMOOTH_ALPHA 越低，平滑效果越强，框越稳定
        SMOOTH_ALPHA = 0.7  # 从 0.95 降低到 0.7，增强平滑
        _smoothed_bbox = None
        _last_process_time = 0
        _last_result_cache = None
        _last_result_time = 0
        BBOX_CHANGE_THRESHOLD = 5
        _consecutive_detections = 0
        _consecutive_misses = 0
        _adaptive_threshold = 0.25
        MIN_THRESHOLD = 0.20
        MAX_THRESHOLD = 0.40
        _max_cache_frames = 8
        _last_confidence_history = []
        
        # ✅ 启动阶段稳定性检查（防止初始帧框飞）
        _startup_frames = 0  # 启动阶段帧数计数
        _startup_stable_count = 0  # 连续稳定检测计数
        _startup_threshold = 3  # 需要连续稳定检测3次才确认人脸框
        _startup_bbox_history = []  # 启动阶段检测框历史
        _startup_max_jump = 50  # 启动阶段框跳变阈值（像素）
        
        # ✅ 情绪标签防抖机制
        _emotion_history = []  # 情绪历史记录
        _emotion_history_maxlen = 5  # 历史记录长度
        _emotion_ema_alpha = 0.3  # EMA平滑系数
        _emotion_ema_probs = None  # EMA平滑后的概率
        _current_emotion = None  # 当前保持的情绪
        _emotion_hysteresis = 0.15  # 迟滞切换阈值（15%）

        try:
            while not stop_event.is_set():
                if time.time() - last_pong > 30:
                    break

                try:
                    frame = await asyncio.wait_for(frame_queue.get(), timeout=5.0)
                except asyncio.TimeoutError:
                    continue

                current_time = time.time()
                if _last_process_time > 0 and (current_time - _last_process_time) > 0.2:
                    try:
                        frame = frame_queue.get_nowait()
                    except asyncio.QueueEmpty:
                        pass
                _last_process_time = current_time

                if _face_detector is None or _emotion_model is None:
                    try:
                        result_queue.put_nowait({
                            'type': 'result',
                            'faces': [],
                            'fps': 0,
                            'dominant_emotion': None,
                            'timestamp': datetime.now().isoformat()
                        })
                    except asyncio.QueueFull:
                        pass
                    continue

                _detect_counter += 1

                if not detection_state['enabled']:
                    continue

                # ✅ 人脸检测：每 4 帧检测 1 次（15fps），初始状态立即检测
                should_detect = (_detect_counter % FACE_DETECT_INTERVAL == 0) or (
                    _last_face_bbox is None)

                if should_detect:
                    try:
                        confidence_threshold = _config_manager.get('face_detect_confidence', 0.3)
                        faces = await loop.run_in_executor(executor, _face_detector.detect, frame, confidence_threshold)
                        logger.debug(f"🔍 人脸检测: 阈值={confidence_threshold:.2f}, 检测到={len(faces)}个人脸")
                    except Exception as e:
                        logger.error(f"人脸检测失败: {e}")
                        continue

                    if faces:
                        _consecutive_misses = 0

                        face_conf = faces[0].get('confidence', 0)
                        current_bbox = faces[0]['bbox']
                        
                        # ✅ 启动阶段稳定性检查
                        if _last_face_bbox is None:
                            _startup_frames += 1
                            _startup_bbox_history.append(current_bbox.copy())
                            
                            # 检查是否连续稳定检测
                            if len(_startup_bbox_history) >= 2:
                                prev_bbox = _startup_bbox_history[-2]
                                # 计算框的移动距离
                                center_x_prev = (prev_bbox[0] + prev_bbox[2]) / 2
                                center_y_prev = (prev_bbox[1] + prev_bbox[3]) / 2
                                center_x_curr = (current_bbox[0] + current_bbox[2]) / 2
                                center_y_curr = (current_bbox[1] + current_bbox[3]) / 2
                                distance = ((center_x_curr - center_x_prev)**2 + 
                                           (center_y_curr - center_y_prev)**2)**0.5
                                
                                if distance < _startup_max_jump:
                                    _startup_stable_count += 1
                                else:
                                    _startup_stable_count = 0  # 跳变过大，重置计数
                                    _startup_bbox_history = [current_bbox.copy()]
                            
                            # 只有连续稳定检测达到阈值，才确认人脸框
                            if _startup_stable_count >= _startup_threshold:
                                logger.info(f"✅ 启动阶段稳定检测完成，确认人脸框")
                                _smoothed_bbox = current_bbox.copy()
                                _last_face_bbox = current_bbox.copy()
                                _last_confidence_history.append(face_conf)
                                _consecutive_detections = 1
                                # ✅ 启动阶段完成，重置情绪防抖状态
                                _emotion_history.clear()
                                _emotion_ema_probs = None
                                _current_emotion = None
                            else:
                                # 启动阶段未稳定，不更新人脸框
                                logger.debug(f"⏳ 启动阶段第{_startup_frames}帧，稳定计数: {_startup_stable_count}/{_startup_threshold}")
                                _last_face_bbox = None  # 保持未确认状态
                                # ✅ 启动阶段重置情绪防抖状态
                                _emotion_history.clear()
                                _emotion_ema_probs = None
                                _current_emotion = None
                                continue  # 跳过后续处理
                        else:
                            # 正常跟踪阶段
                            _last_confidence_history.append(face_conf)
                            if len(_last_confidence_history) > 5:
                                _last_confidence_history.pop(0)

                            if _smoothed_bbox is None:
                                _smoothed_bbox = current_bbox.copy()
                            else:
                                _smoothed_bbox = [
                                    int(SMOOTH_ALPHA *
                                        current_bbox[i] + (1 - SMOOTH_ALPHA) * _smoothed_bbox[i])
                                    for i in range(4)
                                ]

                            _last_face_bbox = _smoothed_bbox.copy()

                            _consecutive_detections += 1
                            if _consecutive_detections >= 8:
                                _consecutive_detections = 0
                    else:
                        _consecutive_detections = 0
                        _consecutive_misses += 1

                        if _consecutive_misses > _max_cache_frames:
                            _last_face_bbox = None
                            _smoothed_bbox = None
                            # ✅ 重置情绪防抖状态
                            _emotion_history.clear()
                            _emotion_ema_probs = None
                            _current_emotion = None

                        if _last_face_bbox and _consecutive_misses <= _max_cache_frames:
                            avg_confidence = sum(_last_confidence_history) / len(
                                _last_confidence_history) if _last_confidence_history else 0

                            if avg_confidence < 0.4 and _consecutive_misses >= 3:
                                _last_face_bbox = None
                                _smoothed_bbox = None
                                _last_confidence_history.clear()
                                # ✅ 重置情绪防抖状态
                                _emotion_history.clear()
                                _emotion_ema_probs = None
                                _current_emotion = None
                            else:
                                cached_face = {
                                    'bbox': _last_face_bbox.copy(),
                                    'confidence': 0.0,
                                    '_cached': True
                                }

                                x, y, w, h = _last_face_bbox
                                hh, ww = frame.shape[:2]
                                x = max(0, min(int(x), ww - 1))
                                y = max(0, min(int(y), hh - 1))
                                w = max(1, min(int(w), ww - x))
                                h = max(1, min(int(h), hh - y))

                                face_img = frame[y:y+h, x:x+w]
                                if face_img.size > 0 and face_img.shape[0] > 0 and face_img.shape[1] > 0:
                                    try:
                                        emotion_result = await loop.run_in_executor(
                                            executor, lambda: _emotion_model.predict(face_img, use_stabilization=False))
                                        emotion, confidence, scores = emotion_result

                                        cached_face['emotion'] = emotion
                                        cached_face['confidence'] = confidence
                                        cached_face['scores'] = scores

                                        response = {
                                            'type': 'result',
                                            'faces': [cached_face],
                                            'dominant_emotion': emotion,
                                            'timestamp': datetime.now().isoformat(),
                                            'process_time': time.time(),
                                            'gpu_memory': get_gpu_memory_usage()
                                        }

                                        try:
                                            result_queue.put_nowait(response)
                                        except asyncio.QueueFull:
                                            pass

                                        _last_emotion_cache = cached_face.copy()
                                        continue
                                    except Exception as e:
                                        logger.debug(f"缓存帧情绪分类失败: {e}")

                        if _consecutive_misses > _max_cache_frames:
                            _last_face_bbox = None
                            _smoothed_bbox = None
                            # ✅ 重置情绪防抖状态
                            _emotion_history.clear()
                            _emotion_ema_probs = None
                            _current_emotion = None

                        try:
                            result_queue.put_nowait({
                                'type': 'result',
                                'faces': [],
                                'fps': 0,
                                'dominant_emotion': None,
                                'timestamp': datetime.now().isoformat(),
                                'process_time': time.time()
                            })
                        except asyncio.QueueFull:
                            pass
                        continue
                else:
                    if _last_face_bbox and _last_emotion_cache:
                        response = {
                            'type': 'result',
                            'faces': [_last_emotion_cache],
                            'dominant_emotion': _last_emotion_cache['emotion'],
                            'timestamp': datetime.now().isoformat(),
                            'process_time': time.time(),
                            'gpu_memory': get_gpu_memory_usage(),
                            '_cached': True
                        }

                        try:
                            result_queue.put_nowait(response)
                        except asyncio.QueueFull:
                            pass

                        continue

                    try:
                        result_queue.put_nowait({
                            'type': 'result',
                            'faces': [],
                            'fps': 0,
                            'dominant_emotion': None,
                            'timestamp': datetime.now().isoformat(),
                            'process_time': time.time()
                        })
                    except asyncio.QueueFull:
                        pass
                    continue

                if not faces:
                    try:
                        result_queue.put_nowait({
                            'type': 'result',
                            'faces': [],
                            'fps': 0,
                            'dominant_emotion': None,
                            'timestamp': datetime.now().isoformat()
                        })
                    except asyncio.QueueFull:
                        pass
                    continue

                # ✅ 情绪识别：每 2 帧识别 1 次（30fps），使用缓存结果
                should_infer_emotion = (_detect_counter % EMOTION_INFER_INTERVAL == 0)
                
                if not should_infer_emotion and _last_emotion_cache:
                    # 使用缓存的情绪结果
                    response = {
                        'type': 'result',
                        'faces': [_last_emotion_cache],
                        'dominant_emotion': _last_emotion_cache['emotion'],
                        'timestamp': datetime.now().isoformat(),
                        'process_time': time.time(),
                        'gpu_memory': get_gpu_memory_usage(),
                        '_cached': True
                    }
                    try:
                        result_queue.put_nowait(response)
                    except asyncio.QueueFull:
                        pass
                    continue

                max_faces = _config_manager.get('max_faces', 10)
                if len(faces) > max_faces:
                    logger.debug(f'检测到{len(faces)}张人脸，仅处理前{max_faces}张')
                    faces = faces[:max_faces]

                face_images = []
                for face in faces:
                    x, y, w, h = face['bbox']
                    x, y, w, h = int(x), int(y), int(w), int(h)
                    hh, ww = frame.shape[:2]
                    x = max(0, min(x, ww - 1))
                    y = max(0, min(y, hh - 1))
                    w = max(1, min(w, ww - x))
                    h = max(1, min(h, hh - y))

                    face_img = frame[y:y+h, x:x+w]
                    if face_img.size > 0 and face_img.shape[0] > 0 and face_img.shape[1] > 0:
                        face_images.append(face_img)

                emotions = []
                try:
                    if face_images and hasattr(_emotion_model, 'predict_batch'):
                        # ✅ WebSocket有自己的防抖逻辑，批量检测不使用模型级防抖
                        emotions = await asyncio.wait_for(
                            asyncio.to_thread(_emotion_model.predict_batch, face_images),
                            timeout=2.0
                        )
                    elif face_images:
                        tasks = []
                        for face_img in face_images:
                            # ✅ WebSocket有自己的防抖逻辑，单个检测不使用模型级防抖
                            tasks.append(asyncio.to_thread(lambda img=face_img: _emotion_model.predict(img, use_stabilization=False)))
                        emotions = await asyncio.wait_for(
                            asyncio.gather(*tasks),
                            timeout=2.0
                        )
                    else:
                        logger.warning("⚠️ 无人脸图像可用于情绪推理")
                except asyncio.TimeoutError:
                    logger.error(f"❌ 情绪推理超时(>2s)，跳过此帧")
                    emotions = []
                except Exception as e:
                    logger.error(f"❌ 情绪推理失败: {e}", exc_info=True)
                    emotions = []

                if not emotions and faces:
                    logger.warning(f"⚠️ 情绪推理无结果，使用默认值")
                    emotions = [('neutral', 0.0, {name: 0.0 for name in ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']}) for _ in faces]

                results = []
                
                # ✅ 根据配置动态调整校准强度
                enable_calibration = _config_manager.get('enable_adaptive_calibration', False)
                if enable_calibration and _adaptive_learner and _adaptive_learner.total_corrections >= 3:
                    _calibration_strength = min(1.0, _calibration_strength + 0.1)
                elif enable_calibration:
                    _calibration_strength = max(0.0, _calibration_strength - 0.05)
                else:
                    _calibration_strength = 0.0  # 禁用校准

                for face, (emotion, confidence, scores) in zip(faces, emotions):
                    x, y, w, h = face['bbox']
                    
                    # ✅ 情绪标签防抖处理
                    # 1. EMA平滑
                    if _emotion_ema_probs is None:
                        _emotion_ema_probs = np.array(list(scores.values()))
                    else:
                        current_probs = np.array(list(scores.values()))
                        _emotion_ema_probs = _emotion_ema_alpha * current_probs + \
                                            (1 - _emotion_ema_alpha) * _emotion_ema_probs
                    
                    # 2. 历史帧平均
                    _emotion_history.append(_emotion_ema_probs.copy())
                    if len(_emotion_history) > _emotion_history_maxlen:
                        _emotion_history.pop(0)
                    
                    # 计算平均概率
                    avg_probs = np.mean(_emotion_history, axis=0)
                    emotion_names = list(scores.keys())
                    
                    # 找出平均概率最高的情绪
                    new_emotion_idx = int(np.argmax(avg_probs))
                    new_emotion = emotion_names[new_emotion_idx]
                    
                    # 3. 迟滞切换机制
                    if _current_emotion is None:
                        _current_emotion = new_emotion
                    
                    current_idx = emotion_names.index(_current_emotion)
                    current_prob = avg_probs[current_idx]
                    new_prob = avg_probs[new_emotion_idx]
                    
                    if new_emotion != _current_emotion:
                        # 只有新情绪概率明显高于当前情绪时才切换
                        if (new_prob - current_prob) >= _emotion_hysteresis:
                            _current_emotion = new_emotion
                    
                    # 使用防抖后的情绪作为输出
                    smoothed_emotion = _current_emotion
                    smoothed_idx = emotion_names.index(smoothed_emotion)
                    smoothed_conf = avg_probs[smoothed_idx]
                    
                    # 构建平滑后的scores
                    smoothed_scores = {name: float(avg_probs[i]) for i, name in enumerate(emotion_names)}

                    # ✅ 根据配置决定是否使用自适应校准
                    if enable_calibration and _calibration_strength > 0 and _adaptive_learner:
                        raw_calibrated = _adaptive_learner.calibrate(smoothed_scores)
                        calibrated_scores = {}
                        for k in smoothed_scores:
                            raw_val = raw_calibrated.get(k, smoothed_scores[k]) if raw_calibrated else smoothed_scores[k]
                            orig_val = smoothed_scores[k]
                            calibrated_scores[k] = orig_val * (1 - _calibration_strength) + raw_val * _calibration_strength
                        calibrated_emotion = max(calibrated_scores, key=calibrated_scores.get)
                        calibrated_conf = calibrated_scores[calibrated_emotion]
                    else:
                        calibrated_scores = smoothed_scores
                        calibrated_emotion = smoothed_emotion
                        calibrated_conf = smoothed_conf

                    results.append({
                        'bbox': [int(x), int(int(y)), int(w), int(h)],
                        'emotion': calibrated_emotion,
                        'confidence': float(calibrated_conf),
                        'scores': {k: float(v) for k, v in calibrated_scores.items()}
                    })

                if results:
                    _last_emotion_cache = results[0].copy()

                dominant_emotion = max(results, key=lambda x: x['confidence'])[
                    'emotion'] if results else None

                # ✅ 计算实际处理时间
                current_time = time.time()
                process_duration_ms = (current_time - _last_process_time) * 1000 if _last_process_time > 0 else 0
                _last_process_time = current_time
                
                response = {
                    'type': 'result',
                    'faces': results,
                    'dominant_emotion': dominant_emotion,
                    'timestamp': datetime.now().isoformat(),
                    'process_time': current_time,
                    'process_duration_ms': process_duration_ms,  # ✅ 实际处理耗时(ms)
                    'gpu_memory': get_gpu_memory_usage(),
                    'frame_count': _detect_counter,  # ✅ 当前帧计数
                    'detection_interval': FACE_DETECT_INTERVAL,  # ✅ 人脸检测间隔
                    'inference_interval': EMOTION_INFER_INTERVAL  # ✅ 情绪识别间隔
                }

                should_send = True
                if _last_result_cache and results:
                    last_faces = _last_result_cache.get('faces', [])
                    if len(last_faces) == len(results):
                        bbox_stable = True
                        for last_face, curr_face in zip(last_faces, results):
                            for i in range(4):
                                if abs(last_face['bbox'][i] - curr_face['bbox'][i]) > BBOX_CHANGE_THRESHOLD:
                                    bbox_stable = False
                                    break
                            if not bbox_stable:
                                break

                        if bbox_stable and last_faces[0]['emotion'] == results[0]['emotion']:
                            if (time.time() - _last_result_time) < 0.05:
                                should_send = False

                if should_send:
                    _last_result_cache = response.copy()
                    _last_result_time = time.time()

                if results and _music_generator:
                    try:
                        scores = results[0]['scores']
                        music_params = _music_generator.generate_music_params(
                            scores)
                        response['music_params'] = music_params
                    except Exception as e:
                        logger.debug(f"生成音乐参数失败: {e}")

                try:
                    result_queue.put_nowait(response)
                except asyncio.QueueFull:
                    try:
                        result_queue.get_nowait()
                        result_queue.put_nowait(response)
                    except asyncio.QueueEmpty:
                        pass

        except (WebSocketDisconnect, RuntimeError):
            logger.warning("🔌 Processor: WebSocket断开或运行时错误")
            stop_event.set()
        except Exception as e:
            logger.error(f"❌ Processor 异常崩溃: {e}", exc_info=True)
            stop_event.set()

    async def result_sender():
        """异步发送结果"""
        nonlocal connection_closed
        try:
            while not stop_event.is_set():
                if connection_closed:
                    break
                try:
                    result_data = await asyncio.wait_for(result_queue.get(), timeout=1.0)
                    if connection_closed:
                        break
                    try:
                        await websocket.send_json(result_data)
                    except WebSocketDisconnect:
                        connection_closed = True
                        logger.warning("🔌 WebSocket 连接已断开，停止发送")
                        stop_event.set()
                        break
                    except Exception as e:
                        logger.error(f"❌ 发送结果失败: {e}")
                except asyncio.TimeoutError:
                    continue
        except Exception as e:
            logger.error(f"❌ result_sender 异常: {e}")

    heartbeat_task = asyncio.create_task(heartbeat())
    receiver_task = asyncio.create_task(receiver())
    processor_task = asyncio.create_task(processor())
    sender_task = asyncio.create_task(result_sender())

    try:
        await asyncio.gather(receiver_task, processor_task, sender_task)
    except (WebSocketDisconnect, Exception) as e:
        connection_closed = True
        logger.error(f"❌ WebSocket主循环异常: {e}")
        stop_event.set()
    finally:
        connection_closed = True
        stop_event.set()
        for t in [receiver_task, processor_task, sender_task, heartbeat_task]:
            t.cancel()
