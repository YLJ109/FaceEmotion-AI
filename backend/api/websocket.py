"""WebSocket 流处理路由"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import asyncio
import time
import numpy as np
import concurrent.futures
import json
import cv2
from datetime import datetime
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
_detection_service = None


def init_ws_router(
    config_manager: ConfigManager,
    db_manager: DatabaseManager,
    face_detector,
    emotion_model,
    detection_service=None,
    adaptive_learner=None,
    executor=None,
    inference_optimizer=None
):
    global _config_manager, _db_manager, _face_detector, _emotion_model, _detection_service, _adaptive_learner, _shared_executor, _music_generator, _inference_optimizer
    _config_manager = config_manager
    _db_manager = db_manager
    _face_detector = face_detector
    _emotion_model = emotion_model
    _detection_service = detection_service
    _adaptive_learner = adaptive_learner
    _shared_executor = executor
    _music_generator = MusicGenerator()
    _inference_optimizer = inference_optimizer
    logger.info(f"WebSocket处理器已初始化 | 置信度阈值: {config_manager.config.get('confidence_threshold', 0.6)}")


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
    await websocket.accept()
    logger.info("WebSocket 连接已建立")

    frame_queue = asyncio.Queue(maxsize=3)
    result_queue = asyncio.Queue(maxsize=5)
    stop_event = asyncio.Event()
    last_pong = time.time()
    connection_closed = False
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
        nonlocal last_pong, connection_closed
        frame_count = 0
        try:
            while not stop_event.is_set():
                msg = await websocket.receive()
                if "bytes" in msg and msg["bytes"]:
                    data = msg["bytes"]
                    frame_count += 1
                    try:
                        if len(data) >= 6:
                            frame_flag = data[0]
                            if frame_flag == 0x01:
                                offset = 1
                                w = int(data[offset]) | (int(data[offset + 1]) << 8)
                                h = int(data[offset + 2]) | (int(data[offset + 3]) << 8)
                                header_size = 5
                            elif frame_flag == 0x02:
                                offset = 0
                                w = int(data[2]) | (int(data[3]) << 8)
                                h = int(data[4]) | (int(data[5]) << 8)
                                header_size = 6
                            else:
                                continue

                            expected_size = header_size + h * w * 4
                            if len(data) < expected_size:
                                continue

                            if frame_flag == 0x01:
                                rgba = np.frombuffer(data[offset + 4:], dtype=np.uint8).reshape(h, w, 4)
                            else:
                                rgba = np.frombuffer(data[6:], dtype=np.uint8).reshape(h, w, 4)
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
                    except Exception as e:
                        logger.error(f"帧解析失败: {e}, data_len={len(data)}")
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
                        _config_manager.update_config(message.get('config', {}))
                        await websocket.send_json({'type': 'config_updated', 'status': 'success'})
                    elif message.get('type') == 'detection_control':
                        detection_state['enabled'] = message.get('enabled', True)
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
        _detect_counter = 0
        _last_process_time = 0
        _last_result_cache = None
        _last_result_time = 0

        use_gpu_mode = _config_manager.get('use_gpu', False) or _config_manager.get('performance_mode', 'cpu') == 'gpu'
        if use_gpu_mode:
            FACE_DETECT_INTERVAL = 1
            EMOTION_INFER_INTERVAL = 1
            SMOOTH_ALPHA = 0.6
        else:
            FACE_DETECT_INTERVAL = 2
            EMOTION_INFER_INTERVAL = 1
            SMOOTH_ALPHA = 0.5

        BBOX_JITTER_THRESHOLD = 3
        MAX_FACES = 5
        MAX_CACHE_FRAMES = 6

        _calibration_strength = 0.0

        class FaceTracker:
            def __init__(self, bbox, smooth_alpha):
                self.smoothed_bbox = [float(v) for v in bbox]
                self.consecutive_misses = 0
                self.confidence_history = []
                self.emotion_ema_probs = None
                self.current_emotion = None
                self.smooth_alpha = smooth_alpha
                self.velocity = [0.0, 0.0, 0.0, 0.0]
                self.position_history = []
                self.last_update_time = time.time()
                self.predict_enabled = True

            def predict(self, dt):
                if not self.predict_enabled or dt <= 0:
                    return self.smoothed_bbox
                pred = []
                for i in range(4):
                    pred.append(self.smoothed_bbox[i] + self.velocity[i] * dt * 0.5)
                return pred

            def update(self, bbox):
                self.consecutive_misses = 0
                self.confidence_history.append(1.0)
                if len(self.confidence_history) > 5:
                    self.confidence_history.pop(0)

                current_time = time.time()
                dt = current_time - self.last_update_time
                self.last_update_time = current_time

                target = [float(v) for v in bbox]
                new_smoothed = []

                for i in range(4):
                    diff = target[i] - self.smoothed_bbox[i]
                    raw_diff = abs(diff)

                    if raw_diff < BBOX_JITTER_THRESHOLD:
                        new_smoothed.append(self.smoothed_bbox[i])
                    else:
                        base_alpha = self.smooth_alpha
                        if raw_diff > 15:
                            base_alpha = min(0.8, self.smooth_alpha * 1.8)
                        elif raw_diff > 8:
                            base_alpha = min(0.65, self.smooth_alpha * 1.3)

                        new_smoothed.append(self.smoothed_bbox[i] + base_alpha * diff)

                self.smoothed_bbox = new_smoothed

                if len(self.position_history) >= 3:
                    self.position_history.pop(0)
                self.position_history.append((self.smoothed_bbox[:], current_time))

                if len(self.position_history) >= 2:
                    prev_pos, prev_time = self.position_history[-2]
                    curr_pos, curr_time = self.position_history[-1]
                    if curr_time > prev_time:
                        for i in range(4):
                            self.velocity[i] = (curr_pos[i] - prev_pos[i]) / (curr_time - prev_time)

                return [int(v) for v in self.smoothed_bbox]

            def miss(self):
                self.consecutive_misses += 1
                if self.consecutive_misses > MAX_CACHE_FRAMES:
                    return 'lost'
                avg_conf = sum(self.confidence_history) / len(self.confidence_history) if self.confidence_history else 0
                if avg_conf < 0.4 and self.consecutive_misses >= 3:
                    return 'lost'
                return 'cached'

            def reset_emotion(self):
                self.emotion_ema_probs = None
                self.current_emotion = None

        trackers = []

        def match_trackers(detected_faces):
            if not trackers:
                return [(None, f) for f in detected_faces[:MAX_FACES]]

            used_trackers = set()
            matches = []

            for face in detected_faces[:MAX_FACES]:
                fx, fy, fw, fh = face['bbox']
                fcx, fcy = fx + fw / 2, fy + fh / 2
                best_idx = -1
                best_dist = float('inf')
                for ti, trk in enumerate(trackers):
                    if ti in used_trackers:
                        continue
                    sx, sy, sw, sh = trk.smoothed_bbox
                    scx, scy = sx + sw / 2, sy + sh / 2
                    dist = abs(fcx - scx) + abs(fcy - scy)
                    if dist < best_dist:
                        best_dist = dist
                        best_idx = ti
                if best_idx >= 0 and best_dist < max(fw, fh) * 2:
                    used_trackers.add(best_idx)
                    matches.append((trackers[best_idx], face))
                else:
                    matches.append((None, face))

            return matches

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
                            'type': 'result', 'faces': [], 'fps': 0,
                            'dominant_emotion': None, 'timestamp': datetime.now().isoformat()
                        })
                    except asyncio.QueueFull:
                        pass
                    continue

                _detect_counter += 1
                if not detection_state['enabled']:
                    continue

                should_detect = (_detect_counter % FACE_DETECT_INTERVAL == 0) or len(trackers) == 0

                detected_faces = None
                if should_detect:
                    try:
                        confidence_threshold = _config_manager.get('face_detect_confidence', 0.3)
                        detected_faces = await loop.run_in_executor(executor, _face_detector.detect, frame, confidence_threshold)
                    except Exception as e:
                        logger.error(f"人脸检测失败: {e}")
                        continue

                if detected_faces:
                    matches = match_trackers(detected_faces)
                    new_trackers = []
                    for tracker, face in matches:
                        if tracker is None:
                            tracker = FaceTracker(face['bbox'], SMOOTH_ALPHA)
                        else:
                            tracker.update(face['bbox'])
                        new_trackers.append(tracker)
                    trackers = new_trackers
                else:
                    surviving = []
                    for tracker in trackers:
                        status = tracker.miss()
                        if status == 'lost':
                            continue
                        surviving.append(tracker)
                    trackers = surviving

                if not trackers:
                    continue

                enable_calibration = _config_manager.get('enable_adaptive_calibration', False)
                if enable_calibration and _adaptive_learner and _adaptive_learner.total_corrections >= 3:
                    _calibration_strength = min(1.0, _calibration_strength + 0.1)
                else:
                    _calibration_strength = 0.0

                emotion_ema_alpha = 0.5
                emotion_hysteresis = 0.15

                results = []
                for tracker in trackers:
                    bbox_int = [int(v) for v in tracker.smoothed_bbox]
                    x, y, w, h = bbox_int
                    hh, ww = frame.shape[:2]
                    x = max(0, min(x, ww - 1))
                    y = max(0, min(y, hh - 1))
                    w = max(1, min(w, ww - x))
                    h = max(1, min(h, hh - y))

                    face_img = frame[y:y+h, x:x+w]
                    if face_img.size == 0 or face_img.shape[0] == 0 or face_img.shape[1] == 0:
                        continue

                    try:
                        emotion, confidence, scores = await loop.run_in_executor(
                            executor, lambda fi=face_img: _emotion_model.predict(fi, use_stabilization=False))
                    except Exception as e:
                        logger.error(f"情绪推理失败: {e}")
                        continue

                    emotion_names = list(scores.keys())
                    current_probs = np.array(list(scores.values()))

                    if tracker.emotion_ema_probs is None:
                        tracker.emotion_ema_probs = current_probs.copy()
                    else:
                        tracker.emotion_ema_probs = emotion_ema_alpha * current_probs + (1 - emotion_ema_alpha) * tracker.emotion_ema_probs

                    new_emotion_idx = int(np.argmax(tracker.emotion_ema_probs))
                    new_emotion = emotion_names[new_emotion_idx]

                    if tracker.current_emotion is None:
                        tracker.current_emotion = new_emotion

                    current_idx = emotion_names.index(tracker.current_emotion)
                    current_prob = tracker.emotion_ema_probs[current_idx]
                    new_prob = tracker.emotion_ema_probs[new_emotion_idx]

                    if new_emotion != tracker.current_emotion:
                        if (new_prob - current_prob) >= emotion_hysteresis:
                            tracker.current_emotion = new_emotion

                    smoothed_emotion = tracker.current_emotion
                    smoothed_idx = emotion_names.index(smoothed_emotion)
                    smoothed_conf = tracker.emotion_ema_probs[smoothed_idx]
                    smoothed_scores = {name: float(tracker.emotion_ema_probs[i]) for i, name in enumerate(emotion_names)}

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

                    face_data = {
                        'bbox': [x, y, w, h],
                        'emotion': calibrated_emotion,
                        'confidence': float(calibrated_conf),
                        'scores': {k: float(v) for k, v in calibrated_scores.items()},
                    }
                    results.append(face_data)

                if not results:
                    continue

                dominant_emotion = max(results, key=lambda x: x['confidence'])['emotion']

                response = {
                    'type': 'result',
                    'faces': results,
                    'dominant_emotion': dominant_emotion,
                    'timestamp': datetime.now().isoformat(),
                    'process_time': current_time,
                    'gpu_memory': get_gpu_memory_usage(),
                    'frame_count': _detect_counter,
                }

                should_send = True
                if _last_result_cache and results:
                    last_faces = _last_result_cache.get('faces', [])
                    if len(last_faces) == len(results):
                        bbox_stable = True
                        for last_face, curr_face in zip(last_faces, results):
                            for i in range(4):
                                if abs(last_face['bbox'][i] - curr_face['bbox'][i]) > BBOX_JITTER_THRESHOLD:
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
                        music_params = _music_generator.generate_music_params(results[0]['scores'])
                        response['music_params'] = music_params
                    except Exception:
                        pass

                try:
                    result_queue.put_nowait(response)
                except asyncio.QueueFull:
                    try:
                        result_queue.get_nowait()
                        result_queue.put_nowait(response)
                    except asyncio.QueueEmpty:
                        pass

        except (WebSocketDisconnect, RuntimeError):
            stop_event.set()
        except Exception as e:
            logger.error(f"Processor 异常: {e}", exc_info=True)
            stop_event.set()

    async def result_sender():
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
                        stop_event.set()
                        break
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
        connection_closed = True
        stop_event.set()
    finally:
        connection_closed = True
        stop_event.set()
        for t in [receiver_task, processor_task, sender_task, heartbeat_task]:
            t.cancel()
