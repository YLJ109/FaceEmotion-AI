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
        f"WebSocket 处理器已初始化 | 置信度阈值: {config_manager.config.get('confidence_threshold', 0.6)}")
    if _inference_optimizer:
        logger.info("WebSocket 推理优化器已启用")


def get_gpu_memory_usage():
    try:
        import pynvml as nvidia_smi
        handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)
        mem_info = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)
        return round(mem_info.used / 1024**2, 1)
    except Exception:
        return 0.0


@router.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    logger.info("WebSocket 连接请求到达")
    await websocket.accept()
    logger.info("WebSocket 连接已建立")

    frame_queue = asyncio.Queue(maxsize=3)
    result_queue = asyncio.Queue(maxsize=5)
    stop_event = asyncio.Event()
    last_pong = time.time()
    connection_closed = False

    global_state_lock = asyncio.Lock()
    detection_state = {'enabled': True}

    async def heartbeat():
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
        nonlocal last_pong
        nonlocal connection_closed
        frame_count = 0
        try:
            while not stop_event.is_set():
                msg = await websocket.receive()
                if "bytes" in msg and msg["bytes"]:
                    data = msg["bytes"]
                    frame_count += 1

                    try:
                        if len(data) >= 4:
                            offset = 1 if data[0] == 0x01 else 0
                            w = int(data[offset]) | (int(data[offset + 1]) << 8)
                            h = int(data[offset + 2]) | (int(data[offset + 3]) << 8)

                            expected_size = h * w * 4 + offset + 4
                            if len(data) < expected_size:
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
                            continue
                    except Exception as e:
                        logger.error(f"帧解析失败: {e}")
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
                            f"检测开关: {'开启' if detection_state['enabled'] else '关闭'}")
        except (WebSocketDisconnect, RuntimeError):
            connection_closed = True
            stop_event.set()
        except Exception as e:
            logger.error(f"Receiver 异常: {e}")
            connection_closed = True
            stop_event.set()

    async def processor():
        nonlocal last_pong
        loop = asyncio.get_event_loop()
        executor = _shared_executor

        # 帧计数与间隔控制
        _detect_counter = 0
        use_gpu_mode = _config_manager.get('use_gpu', False) or _config_manager.get('performance_mode', 'cpu') == 'gpu'

        if use_gpu_mode:
            FACE_DETECT_INTERVAL = 1
            EMOTION_INFER_INTERVAL = 1
            logger.info("GPU模式: 每帧检测+识别")
        else:
            FACE_DETECT_INTERVAL = 3
            EMOTION_INFER_INTERVAL = 1
            logger.info("CPU模式: 每3帧检测人脸，每帧识别情绪")

        # 人脸框平滑
        _smoothed_bbox = None
        SMOOTH_ALPHA = 0.65
        _consecutive_misses = 0
        _max_misses = 10

        # 情绪EMA平滑（单层，简洁高效）
        _ema_probs = None
        EMA_ALPHA = 0.35
        _last_emotion_result = None

        # 结果去重
        _last_sent_time = 0
        _last_sent_emotion = None

        try:
            while not stop_event.is_set():
                if time.time() - last_pong > 30:
                    break

                try:
                    frame = await asyncio.wait_for(frame_queue.get(), timeout=5.0)
                except asyncio.TimeoutError:
                    continue

                # 跳过积压的旧帧
                while not frame_queue.empty():
                    try:
                        frame = frame_queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break

                if _face_detector is None or _emotion_model is None:
                    try:
                        result_queue.put_nowait({
                            'type': 'result',
                            'faces': [],
                            'dominant_emotion': None,
                            'timestamp': datetime.now().isoformat()
                        })
                    except asyncio.QueueFull:
                        pass
                    continue

                _detect_counter += 1

                if not detection_state['enabled']:
                    continue

                # ============================================================
                # 人脸检测：间隔检测 + ROI跟踪加速
                # ============================================================
                should_detect = (_detect_counter % FACE_DETECT_INTERVAL == 0) or (_smoothed_bbox is None)

                if should_detect:
                    try:
                        confidence_threshold = _config_manager.get('face_detect_confidence', 0.4)
                        faces = await loop.run_in_executor(
                            executor,
                            _face_detector.detect_with_tracking,
                            frame,
                            confidence_threshold
                        )
                    except Exception as e:
                        logger.error(f"人脸检测失败: {e}")
                        faces = []

                    if faces:
                        _consecutive_misses = 0
                        current_bbox = faces[0]['bbox']

                        if _smoothed_bbox is None:
                            _smoothed_bbox = list(current_bbox)
                        else:
                            _smoothed_bbox = [
                                int(SMOOTH_ALPHA * current_bbox[i] + (1 - SMOOTH_ALPHA) * _smoothed_bbox[i])
                                for i in range(4)
                            ]
                    else:
                        _consecutive_misses += 1
                        if _consecutive_misses > _max_misses:
                            _smoothed_bbox = None
                            _ema_probs = None
                            _last_emotion_result = None

                # ============================================================
                # 无人脸框 → 发送空结果
                # ============================================================
                if _smoothed_bbox is None:
                    try:
                        result_queue.put_nowait({
                            'type': 'result',
                            'faces': [],
                            'dominant_emotion': None,
                            'timestamp': datetime.now().isoformat()
                        })
                    except asyncio.QueueFull:
                        pass
                    continue

                # ============================================================
                # 情绪识别：每帧识别 + EMA平滑
                # ============================================================
                should_infer = (_detect_counter % EMOTION_INFER_INTERVAL == 0)

                if should_infer:
                    x, y, w, h = _smoothed_bbox
                    hh, ww = frame.shape[:2]

                    # 提取人脸ROI（带20%边距保留上下文）
                    margin_w = int(w * 0.2)
                    margin_h = int(h * 0.2)
                    x1 = max(0, x - margin_w)
                    y1 = max(0, y - margin_h)
                    x2 = min(ww, x + w + margin_w)
                    y2 = min(hh, y + h + margin_h)

                    if x2 > x1 and y2 > y1:
                        face_img = frame[y1:y2, x1:x2]
                        if face_img.size > 0 and face_img.shape[0] > 10 and face_img.shape[1] > 10:
                            try:
                                emotion, confidence, scores = await loop.run_in_executor(
                                    executor,
                                    _emotion_model.predict_fast,
                                    face_img
                                )

                                # EMA平滑概率分布
                                current_probs = np.array(list(scores.values()))
                                if _ema_probs is None:
                                    _ema_probs = current_probs
                                else:
                                    _ema_probs = EMA_ALPHA * current_probs + (1 - EMA_ALPHA) * _ema_probs

                                # 从平滑概率中取最高情绪
                                emotion_names = list(scores.keys())
                                best_idx = int(np.argmax(_ema_probs))
                                smoothed_emotion = emotion_names[best_idx]
                                smoothed_conf = float(_ema_probs[best_idx])
                                smoothed_scores = {
                                    name: float(_ema_probs[i])
                                    for i, name in enumerate(emotion_names)
                                }

                                _last_emotion_result = {
                                    'bbox': [int(x), int(y), int(w), int(h)],
                                    'emotion': smoothed_emotion,
                                    'confidence': smoothed_conf,
                                    'scores': smoothed_scores
                                }
                            except Exception as e:
                                logger.debug(f"情绪识别失败: {e}")

                # ============================================================
                # 构建响应
                # ============================================================
                if _last_emotion_result is None:
                    try:
                        result_queue.put_nowait({
                            'type': 'result',
                            'faces': [],
                            'dominant_emotion': None,
                            'timestamp': datetime.now().isoformat()
                        })
                    except asyncio.QueueFull:
                        pass
                    continue

                result = _last_emotion_result.copy()

                # 结果去重：相同情绪+稳定框 → 降低发送频率
                current_time = time.time()
                should_send = True
                if (_last_sent_emotion == result['emotion'] and
                        (current_time - _last_sent_time) < 0.08):
                    should_send = False

                if should_send:
                    _last_sent_time = current_time
                    _last_sent_emotion = result['emotion']

                response = {
                    'type': 'result',
                    'faces': [result],
                    'dominant_emotion': result['emotion'],
                    'timestamp': datetime.now().isoformat(),
                    'process_time': current_time,
                    'gpu_memory': get_gpu_memory_usage()
                }

                # 音乐参数生成
                if _music_generator:
                    try:
                        scores = result['scores']
                        music_params = _music_generator.generate_music_params(scores)
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
            logger.warning("Processor: WebSocket断开或运行时错误")
            stop_event.set()
        except Exception as e:
            logger.error(f"Processor 异常: {e}", exc_info=True)
            stop_event.set()

    async def sender():
        try:
            while not stop_event.is_set():
                try:
                    result = await asyncio.wait_for(result_queue.get(), timeout=1.0)
                    await websocket.send_json(result)
                except asyncio.TimeoutError:
                    continue
                except (WebSocketDisconnect, RuntimeError):
                    break
                except Exception as e:
                    logger.error(f"Sender 异常: {e}")
                    break
        except Exception as e:
            logger.error(f"Sender 异常: {e}")

    tasks = [
        asyncio.create_task(heartbeat()),
        asyncio.create_task(receiver()),
        asyncio.create_task(processor()),
        asyncio.create_task(sender())
    ]

    try:
        done, pending = await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()
    except Exception as e:
        logger.error(f"WebSocket 任务异常: {e}")
    finally:
        stop_event.set()
        for task in tasks:
            if not task.done():
                task.cancel()
        try:
            await websocket.close()
        except Exception:
            pass
        logger.info("WebSocket 连接已关闭")