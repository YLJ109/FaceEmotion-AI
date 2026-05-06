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

logger = logging.getLogger(__name__)
router = APIRouter()

# 全局依赖注入
_config_manager = None
_db_manager = None
_face_detector = None
_emotion_model = None
_adaptive_learner = None
_shared_executor = None
_music_generator = None


def init_ws_router(
    config_manager: ConfigManager,
    db_manager: DatabaseManager,
    face_detector,
    emotion_model,
    adaptive_learner: AdaptiveLearner,
    executor: concurrent.futures.ThreadPoolExecutor
):
    """初始化路由依赖"""
    global _config_manager, _db_manager, _face_detector, _emotion_model, _adaptive_learner, _shared_executor, _music_generator
    _config_manager = config_manager
    _db_manager = db_manager
    _face_detector = face_detector
    _emotion_model = emotion_model
    _adaptive_learner = adaptive_learner
    _shared_executor = executor
    _music_generator = MusicGenerator()
    logger.info(
        f"✅ WebSocket 处理器已初始化 | 置信度阈值: {config_manager.config.get('confidence_threshold', 0.6)}")


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
    await websocket.accept()

    frame_queue = asyncio.Queue(maxsize=3)  # ✅ 优化: 增加队列容量到3，避免模型切换时丢帧
    result_queue = asyncio.Queue(maxsize=5)
    stop_event = asyncio.Event()
    last_pong = time.time()

    # ✅ 修复: 使用全局共享的锁，避免每次创建新锁
    global_state_lock = asyncio.Lock()

    # ✅ 新增: 检测开关状态（跨协程共享）
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
        try:
            while not stop_event.is_set():
                msg = await websocket.receive()
                if "bytes" in msg and msg["bytes"]:
                    data = msg["bytes"]

                    # 视频帧处理
                    if len(data) >= 4:
                        # 检查是否有类型标识
                        offset = 1 if data[0] == 0x01 else 0

                        w = int(data[offset]) | (int(data[offset + 1]) << 8)
                        h = int(data[offset + 2]
                                ) | (int(data[offset + 3]) << 8)
                        rgba = np.frombuffer(
                            data[offset + 4:], dtype=np.uint8).reshape(h, w, 4)

                        # ✅ 优化: 直接从 RGBA 提取 BGR（避免 cv2.cvtColor 开销）
                        # RGBA → BGR: 取前 3 个通道并反转顺序
                        frame = rgba[:, :, :3][:, :, ::-
                                               1].copy()  # 使用 copy 确保内存连续

                        # ✅ 修复: 只在队列满时清空旧帧，避免频繁清空
                        if frame_queue.full():
                            try:
                                frame_queue.get_nowait()
                            except asyncio.QueueEmpty:
                                pass

                        try:
                            frame_queue.put_nowait(frame)
                        except asyncio.QueueFull:
                            pass
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
                    # ✅ 新增: 处理检测开关控制消息
                    elif message.get('type') == 'detection_control':
                        detection_state['enabled'] = message.get(
                            'enabled', True)
                        logger.info(
                            f"🎛️ 检测开关状态: {'开启' if detection_state['enabled'] else '关闭'}")
        except (WebSocketDisconnect, RuntimeError):
            stop_event.set()
        except Exception as e:
            stop_event.set()

    async def processor():
        """处理帧并检测情绪"""
        nonlocal last_pong
        loop = asyncio.get_event_loop()
        executor = _shared_executor
        _save_counter = 0
        _calibration_strength = 0.0
        _last_face_bbox = None
        _detect_counter = 0
        # ✅ 优化: 降低检测间隔，提升响应速度
        DETECT_INTERVAL = 2  # 每 2 帧检测一次（从 3 降到 2）
        TRACKING_THRESHOLD = 5  # 人脸框变化阈值(px)
        # ✅ 新增: 人脸框平滑参数
        SMOOTH_ALPHA = 0.7  # 指数移动平均系数（越大越跟随，越小越平滑）
        _smoothed_bbox = None  # 平滑后的人脸框
        _last_process_time = 0  # ✅ 新增: 记录上次处理时间
        # ✅ 深度优化: 结果缓存(减少重复发送)
        _last_result_cache = None
        _last_result_time = 0
        BBOX_CHANGE_THRESHOLD = 5  # 人脸框变化阈值(px)
        # ✅ 优化: 自适应置信度调整（关键修复：逻辑反转）
        _consecutive_detections = 0  # 连续检测到人脸的帧数
        _consecutive_misses = 0  # ✅ 新增: 连续未检测到人脸的帧数
        _adaptive_threshold = 0.45  # ✅ 修复: 初始阈值从 0.5 降到 0.45，提高检出率
        MIN_THRESHOLD = 0.35  # ✅ 修复: 最低阈值从 0.4 降到 0.35
        MAX_THRESHOLD = 0.55  # ✅ 修复: 最高阈值从 0.6 降到 0.55

        # ✅ 优化: 快速清除机制（防止误检残留）
        _max_cache_frames = 3  # ✅ 优化: 缩短到 3 帧（约 0.3 秒），无人脸时更快清除
        _last_confidence_history = []  # ✅ 新增: 记录最近 5 次的置信度，用于误检过滤

        try:
            while not stop_event.is_set():
                if time.time() - last_pong > 30:
                    break

                try:
                    frame = await asyncio.wait_for(frame_queue.get(), timeout=5.0)
                except asyncio.TimeoutError:
                    continue

                # ✅ 修复: 丢弃过旧帧（放宽到200ms，避免频繁丢帧）
                current_time = time.time()
                if _last_process_time > 0 and (current_time - _last_process_time) > 0.2:
                    # 跳过这帧,获取最新的
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

                # ✅ 新增: 检查检测开关状态
                if not detection_state['enabled']:
                    # 检测关闭时，不执行任何检测逻辑，直接跳过
                    continue

                should_detect = (_detect_counter % DETECT_INTERVAL == 0) or (
                    _last_face_bbox is None)

                if should_detect:
                    try:
                        # ✅ 修改: 传入置信度阈值
                        # ✅ 优化: 动态读取置信度阈值（支持热更新）
                        confidence_threshold = _config_manager.config.get(
                            'confidence_threshold', _adaptive_threshold)  # 使用自适应阈值
                        faces = await loop.run_in_executor(executor, _face_detector.detect, frame, confidence_threshold)
                    except Exception:
                        continue

                    if faces:
                        # ✅ 修复: 重置连续未检测计数
                        _consecutive_misses = 0

                        # ✅ 新增: 记录置信度历史（用于误检过滤）
                        face_conf = faces[0].get('confidence', 0)
                        _last_confidence_history.append(face_conf)
                        if len(_last_confidence_history) > 5:
                            _last_confidence_history.pop(0)

                        # ✅ 新增: 人脸框平滑处理（防止抖动）
                        if _smoothed_bbox is None:
                            _smoothed_bbox = faces[0]['bbox'].copy()
                        else:
                            # 指数移动平均平滑
                            current_bbox = faces[0]['bbox']
                            _smoothed_bbox = [
                                int(SMOOTH_ALPHA *
                                    current_bbox[i] + (1 - SMOOTH_ALPHA) * _smoothed_bbox[i])
                                for i in range(4)
                            ]

                        _last_face_bbox = _smoothed_bbox.copy()

                        # ✅ 修复: 自适应调整阈值（正确逻辑）
                        _consecutive_detections += 1
                        if _consecutive_detections >= 8:  # ✅ 优化: 从 3 帧提高到 8 帧，更稳定
                            # ✅ 修复: 连续检测到人脸时，保持低阈值（已经很低了，无需再降）
                            # 这里只做日志记录，不再调整阈值
                            logger.debug(
                                f"✅ 稳定检测中 (连续{_consecutive_detections}帧), 阈值: {_adaptive_threshold:.2f}")
                            _consecutive_detections = 0  # 重置计数
                    else:
                        # ✅ 修复: 无人脸时重置检测计数
                        _consecutive_detections = 0
                        _consecutive_misses += 1

                        # ✅ 关键修复: 无人脸时快速清除缓存（防止误检残留）
                        if _consecutive_misses > _max_cache_frames:
                            # 超过缓存限制，立即清除
                            logger.debug(
                                f"⚠️ 连续{_consecutive_misses}帧无人脸，清除缓存框")
                            _last_face_bbox = None
                            _smoothed_bbox = None

                        # ✅ 优化: 缓慢提高阈值（步长从 0.05 降到 0.02）
                        # 避免阈值过快上升导致漏检
                        if _consecutive_misses >= 10:
                            # 连续 10 帧无人脸才提高阈值
                            _adaptive_threshold = min(
                                MAX_THRESHOLD, _adaptive_threshold + 0.02)
                            logger.debug(
                                f"⚠️ 连续{_consecutive_misses}帧无人脸，提高阈值: {_adaptive_threshold:.2f}")

                        # ✅ 修复: 仅在缓存有效期内使用缓存帧（缩短到 3 帧）
                        if _last_face_bbox and _consecutive_misses <= _max_cache_frames:
                            # ✅ 新增: 误检过滤 - 检查最近置信度趋势
                            avg_confidence = sum(_last_confidence_history) / len(
                                _last_confidence_history) if _last_confidence_history else 0

                            # 如果平均置信度低于 0.5，说明可能是误检，不使用缓存
                            if avg_confidence < 0.5 and _consecutive_misses >= 2:
                                logger.debug(
                                    f"⚠️ 检测到误检趋势（平均置信度: {avg_confidence:.2f}），停止缓存")
                                _last_face_bbox = None
                                _smoothed_bbox = None
                                _last_confidence_history.clear()
                            else:
                                # 使用缓存的人脸框继续发送（非检测帧）
                                cached_face = {
                                    'bbox': _last_face_bbox.copy(),
                                    'confidence': 0.0,  # 标记为缓存帧
                                    '_cached': True  # 标记为缓存
                                }

                                # ✅ 修复: 对缓存帧进行情绪分类（使用上一帧的人脸区域）
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

                                        # ✅ 修复: 立即发送缓存帧结果，避免前端等待
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

                                        # 继续处理下一帧
                                        continue
                                    except Exception as e:
                                        logger.debug(f"缓存帧情绪分类失败: {e}")

                        # ✅ 修复: 缓存过期或处理失败，清除状态并发送空结果
                        if _consecutive_misses > _max_cache_frames:
                            _last_face_bbox = None
                            _smoothed_bbox = None

                        # ✅ 优化: 无人脸时立即发送空结果,避免前端等待
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
                    # ✅ 修复: 非检测帧使用缓存的人脸框（防止闪烁）
                    if _last_face_bbox:
                        # ✅ 关键修复: 对缓存帧进行情绪分类
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

                                cached_face = {
                                    'bbox': _last_face_bbox.copy(),
                                    'confidence': confidence,
                                    'emotion': emotion,
                                    'scores': scores,
                                    '_cached': True
                                }

                                # ✅ 修复: 立即发送缓存帧结果
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

                                continue
                            except Exception as e:
                                logger.debug(f"缓存帧情绪分类失败: {e}")

                    # 如果无缓存或分类失败，发送空结果
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

                # ✅ 修改: 多人脸场景优化 - 限制最多处理10张人脸
                max_faces = 10
                if len(faces) > max_faces:
                    logger.debug(f'检测到{len(faces)}张人脸，仅处理前{max_faces}张')
                    faces = faces[:max_faces]

                # ✅ 优化: 始终使用批量推理（即使只有 1 张人脸）
                face_images = []
                for face in faces:
                    x, y, w, h = face['bbox']
                    # ✅ 修复: 确保人脸区域有效，避免空数组导致卡顿
                    x, y, w, h = int(x), int(y), int(w), int(h)
                    hh, ww = frame.shape[:2]
                    x = max(0, min(x, ww - 1))
                    y = max(0, min(y, hh - 1))
                    w = max(1, min(w, ww - x))
                    h = max(1, min(h, hh - y))

                    face_img = frame[y:y+h, x:x+w]
                    if face_img.size > 0 and face_img.shape[0] > 0 and face_img.shape[1] > 0:
                        face_images.append(face_img)

                # ✅ 深度优化: 将批量推理完全卸载到线程池，避免阻塞主循环
                if face_images and hasattr(_emotion_model, 'predict_batch'):
                    # ✅ 修复: 使用 asyncio.to_thread 替代 run_in_executor，更现代的 API
                    emotions = await asyncio.to_thread(_emotion_model.predict_batch, face_images)
                elif face_images:
                    # 降级到单个处理（兼容性）
                    tasks = []
                    for face_img in face_images:
                        tasks.append(asyncio.to_thread(
                            _emotion_model.predict, face_img))
                    emotions = await asyncio.gather(*tasks)
                else:
                    emotions = []

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

                # ✅ 优化: 放宽结果缓存防抖，提升响应速度
                should_send = True
                if _last_result_cache and results:
                    last_faces = _last_result_cache.get('faces', [])
                    if len(last_faces) == len(results):
                        # 检查人脸框变化是否小于阈值
                        bbox_stable = True
                        for last_face, curr_face in zip(last_faces, results):
                            for i in range(4):
                                if abs(last_face['bbox'][i] - curr_face['bbox'][i]) > BBOX_CHANGE_THRESHOLD:
                                    bbox_stable = False
                                    break
                            if not bbox_stable:
                                break

                        # ✅ 修改: 降低防抖阈值，从 100ms 降到 50ms
                        if bbox_stable and last_faces[0]['emotion'] == results[0]['emotion']:
                            if (time.time() - _last_result_time) < 0.05:  # 从 0.1 降到 0.05
                                should_send = False

                if should_send:
                    _last_result_cache = response.copy()
                    _last_result_time = time.time()

                # ✅ 新增: 推送 AI 生成式音乐参数
                if results and _music_generator:
                    try:
                        scores = results[0]['scores']
                        music_params = _music_generator.generate_music_params(
                            scores)
                        response['music_params'] = music_params
                    except Exception as e:
                        print(f"⚠️ 生成音乐参数失败: {e}")

                try:
                    result_queue.put_nowait(response)
                except asyncio.QueueFull:
                    try:
                        result_queue.get_nowait()
                        result_queue.put_nowait(response)
                    except asyncio.QueueEmpty:
                        pass

                # ✅ 修复: 移除后端的自动保存逻辑,由前端手动触发保存
                # if results:
                #     _save_counter += 1
                #     if _save_counter % 30 == 0:
                #         try:
                #             _db_manager.save_detection_result(
                #                 'realtime', results, source='实时摄像头检测')
                #         except Exception:
                #             pass

        except (WebSocketDisconnect, RuntimeError):
            stop_event.set()
        except Exception:
            stop_event.set()

    async def result_sender():
        """异步发送结果"""
        try:
            while not stop_event.is_set():
                try:
                    result_data = await asyncio.wait_for(result_queue.get(), timeout=1.0)
                    try:
                        await websocket.send_json(result_data)
                    except Exception:
                        pass
                except asyncio.TimeoutError:
                    continue
        except Exception:
            pass

    heartbeat_task = asyncio.create_task(heartbeat())
    receiver_task = asyncio.create_task(receiver())
    processor_task = asyncio.create_task(processor())
    sender_task = asyncio.create_task(result_sender())

    try:
        await asyncio.gather(receiver_task, processor_task, sender_task)
    except (WebSocketDisconnect, Exception):
        stop_event.set()
        for t in [receiver_task, processor_task, sender_task, heartbeat_task]:
            t.cancel()
