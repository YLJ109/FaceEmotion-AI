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

    global_state_lock = asyncio.Lock()
    detection_state = {'enabled': True}

    async def heartbeat():
        """心跳检测"""
        while not stop_event.is_set():
            await asyncio.sleep(15)
            try:
                await websocket.send_json({"type": "ping"})
            except Exception:
                stop_event.set()
                break

    async def receiver():
        """接收帧数据"""
        nonlocal last_pong
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
                    if message.get('type') == 'pong':
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
            stop_event.set()
        except Exception as e:
            logger.error(f"❌ Receiver 异常: {e}")
            stop_event.set()

    async def processor():
        """处理帧并检测情绪"""
        nonlocal last_pong
        loop = asyncio.get_event_loop()
        executor = _shared_executor
        _save_counter = 0
        _calibration_strength = 0.0
        _last_face_bbox = None
        _last_emotion_cache = None
        _detect_counter = 0
        DETECT_INTERVAL = 2
        TRACKING_THRESHOLD = 5
        SMOOTH_ALPHA = 0.7
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

                should_detect = (_detect_counter % DETECT_INTERVAL == 0) or (
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
                        _last_confidence_history.append(face_conf)
                        if len(_last_confidence_history) > 5:
                            _last_confidence_history.pop(0)

                        if _smoothed_bbox is None:
                            _smoothed_bbox = faces[0]['bbox'].copy()
                        else:
                            current_bbox = faces[0]['bbox']
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

                        if _last_face_bbox and _consecutive_misses <= _max_cache_frames:
                            avg_confidence = sum(_last_confidence_history) / len(
                                _last_confidence_history) if _last_confidence_history else 0

                            if avg_confidence < 0.4 and _consecutive_misses >= 3:
                                _last_face_bbox = None
                                _smoothed_bbox = None
                                _last_confidence_history.clear()
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
                                            executor, _emotion_model.predict, face_img)
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
                        emotions = await asyncio.wait_for(
                            asyncio.to_thread(_emotion_model.predict_batch, face_images),
                            timeout=2.0
                        )
                    elif face_images:
                        tasks = []
                        for face_img in face_images:
                            tasks.append(asyncio.to_thread(_emotion_model.predict, face_img))
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
                if _adaptive_learner and _adaptive_learner.total_corrections >= 3:
                    _calibration_strength = min(
                        1.0, _calibration_strength + 0.1)
                else:
                    _calibration_strength = max(
                        0.0, _calibration_strength - 0.05)

                for face, (emotion, confidence, scores) in zip(faces, emotions):
                    x, y, w, h = face['bbox']

                    if _calibration_strength > 0 and _adaptive_learner:
                        raw_calibrated = _adaptive_learner.calibrate(scores)
                        calibrated_scores = {}
                        for k in scores:
                            raw_val = raw_calibrated.get(
                                k, scores[k]) if raw_calibrated else scores[k]
                            orig_val = scores[k]
                            calibrated_scores[k] = orig_val * (
                                1 - _calibration_strength) + raw_val * _calibration_strength
                        calibrated_emotion = max(
                            calibrated_scores, key=calibrated_scores.get)
                        calibrated_conf = calibrated_scores[calibrated_emotion]
                    else:
                        calibrated_scores = scores
                        calibrated_emotion = emotion
                        calibrated_conf = confidence

                    results.append({
                        'bbox': [int(x), int(y), int(w), int(h)],
                        'emotion': calibrated_emotion,
                        'confidence': float(calibrated_conf),
                        'scores': {k: float(v) for k, v in calibrated_scores.items()}
                    })

                if results:
                    _last_emotion_cache = results[0].copy()

                dominant_emotion = max(results, key=lambda x: x['confidence'])[
                    'emotion'] if results else None

                response = {
                    'type': 'result',
                    'faces': results,
                    'dominant_emotion': dominant_emotion,
                    'timestamp': datetime.now().isoformat(),
                    'process_time': time.time(),
                    'gpu_memory': get_gpu_memory_usage()
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
        try:
            while not stop_event.is_set():
                try:
                    result_data = await asyncio.wait_for(result_queue.get(), timeout=1.0)
                    try:
                        await websocket.send_json(result_data)
                    except WebSocketDisconnect:
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
        logger.error(f"❌ WebSocket主循环异常: {e}")
        stop_event.set()
        for t in [receiver_task, processor_task, sender_task, heartbeat_task]:
            t.cancel()
