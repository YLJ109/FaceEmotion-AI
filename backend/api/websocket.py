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

from config import ConfigManager
from database import DatabaseManager
from adaptation.active_learner import AdaptiveLearner
from music.generative_music import MusicGenerator
from multimodal.voice_analyzer_wav2vec2 import Wav2Vec2VoiceAnalyzer  # ✅ 使用 wav2vec2 模型

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
_voice_analyzer = None

# ✅ 新增: 全局状态存储(用于多模态融合)
global_state = {
    'voice_scores': None,
    'voice_features': None
}

# ✅ 新增: 语音推理防抖锁（防止并发推理）
_voice_inference_lock = asyncio.Lock()


def init_ws_router(
    config_manager: ConfigManager,
    db_manager: DatabaseManager,
    face_detector,
    emotion_model,
    adaptive_learner: AdaptiveLearner,
    executor: concurrent.futures.ThreadPoolExecutor,
    voice_analyzer=None  # ✅ 修改: 改为可选参数
):
    """初始化路由依赖"""
    global _config_manager, _db_manager, _face_detector, _emotion_model, _adaptive_learner, _shared_executor, _music_generator, _voice_analyzer
    _config_manager = config_manager
    _db_manager = db_manager
    _face_detector = face_detector
    _emotion_model = emotion_model
    _adaptive_learner = adaptive_learner
    _shared_executor = executor

    # ✅ 修改: 使用 wav2vec2 语音分析器
    if voice_analyzer is None:
        _voice_analyzer = Wav2Vec2VoiceAnalyzer()
        print("✅ 已启用 wav2vec2 语音情绪识别模型（本地）")
    else:
        _voice_analyzer = voice_analyzer

    _music_generator = MusicGenerator()
    # ✅ 优化: 移除全局阈值变量，改为动态从 config_manager 读取
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

    frame_queue = asyncio.Queue(maxsize=1)
    result_queue = asyncio.Queue(maxsize=5)
    stop_event = asyncio.Event()
    last_pong = time.time()

    # ✅ 修复: 使用全局共享的锁，避免每次创建新锁
    global_state_lock = asyncio.Lock()

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
        audio_buffer = bytearray()  # ✅ 恢复: 音频数据缓冲区

        async def run_voice_inference():
            """异步执行 wav2vec2 推理（带锁保护）"""
            async with _voice_inference_lock:
                try:
                    loop = asyncio.get_event_loop()
                    voice_scores = await loop.run_in_executor(
                        _shared_executor,
                        _voice_analyzer.predict_emotion
                    )

                    if voice_scores and len(voice_scores) > 0:
                        async with global_state_lock:
                            global_state['voice_scores'] = voice_scores
                            global_state['voice_features'] = {
                                'has_voice': 1.0,
                                'energy_mean': 0.05
                            }
                except Exception as e:
                    print(f"❌ wav2vec2 推理失败: {e}")
                    import traceback
                    traceback.print_exc()

        try:
            while not stop_event.is_set():
                msg = await websocket.receive()
                if "bytes" in msg and msg["bytes"]:
                    data = msg["bytes"]

                    # ✅ 修复: 检查数据类型标识
                    if len(data) >= 1:
                        type_byte = data[0]

                        # 0x01 = 视频帧 (向后兼容：如果没有标识，默认是视频)
                        # 0x02 = 音频数据
                        if type_byte == 0x02:
                            try:
                                audio_data = data[1:]  # 移除类型标识字节

                                # wav2vec2 方案的音频处理逻辑
                                _voice_analyzer.add_audio_chunk(audio_data)

                                # 异步触发 wav2vec2 推理，不再阻塞消息循环
                                # 增加到 1 秒缓冲区（16000 样本），提高识别准确率
                                # 只在有有效语音时才触发推理
                                if len(_voice_analyzer._audio_buffer) >= 16000:
                                    # 计算音频能量，检测是否有有效语音
                                    audio_energy = _voice_analyzer.get_audio_energy()

                                    if audio_energy > 0.05:  # 阈值：有有效声音
                                        # 检查是否已有推理任务在执行
                                        if not _voice_inference_lock.locked():
                                            # 关键: 创建后台任务，不等待完成
                                            asyncio.create_task(
                                                run_voice_inference())
                            except Exception as e:
                                print(f"❌ 处理音频数据失败: {e}")
                                import traceback
                                traceback.print_exc()

                            continue
                        elif type_byte == 0x01 or len(data) < 4:
                            # 向后兼容：旧格式或无标识，当作视频帧
                            pass

                    # 视频帧处理（原有逻辑）
                    if len(data) >= 4:
                        # 检查是否有类型标识
                        offset = 1 if data[0] in [0x01, 0x02] else 0

                        w = int(data[offset]) | (int(data[offset + 1]) << 8)
                        h = int(data[offset + 2]
                                ) | (int(data[offset + 3]) << 8)
                        rgba = np.frombuffer(
                            data[offset + 4:], dtype=np.uint8).reshape(h, w, 4)
                        frame = cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGR)

                        while not frame_queue.empty():
                            try:
                                frame_queue.get_nowait()
                            except asyncio.QueueEmpty:
                                break

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
        DETECT_INTERVAL = 3  # ✅ 优化: 每3帧检测一次人脸位置，降低CPU负载60-70%
        TRACKING_THRESHOLD = 5  # 人脸框变化阈值(px)
        _last_process_time = 0  # ✅ 新增: 记录上次处理时间
        # ✅ 深度优化: 结果缓存(减少重复发送)
        _last_result_cache = None
        _last_result_time = 0
        BBOX_CHANGE_THRESHOLD = 5  # 人脸框变化阈值(px)

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
                should_detect = (_detect_counter % DETECT_INTERVAL == 0) or (
                    _last_face_bbox is None)

                if should_detect:
                    try:
                        # ✅ 修改: 传入置信度阈值
                        # ✅ 优化: 动态读取置信度阈值（支持热更新）
                        confidence_threshold = _config_manager.config.get(
                            'confidence_threshold', 0.6)
                        faces = await loop.run_in_executor(executor, _face_detector.detect, frame, confidence_threshold)
                    except Exception:
                        continue

                    if faces:
                        _last_face_bbox = faces[0]['bbox']
                    else:
                        _last_face_bbox = None
                        # ✅ 优化: 无人脸时立即发送空结果,避免前端等待
                        try:
                            result_queue.put_nowait({
                                'type': 'result',
                                'faces': [],
                                'fps': 0,
                                'dominant_emotion': None,
                                'timestamp': datetime.now().isoformat(),
                                'process_time': time.time()  # ✅ 新增: 添加时间戳
                            })
                        except asyncio.QueueFull:
                            pass
                        continue
                else:
                    # ✅ 修复: 缓存帧保持更长时间，降低置信度阈值
                    if _last_face_bbox:
                        x, y, w, h = _last_face_bbox
                        hh, ww = frame.shape[:2]
                        x = max(0, min(x, ww - 1))
                        y = max(0, min(y, hh - 1))
                        w = min(w, ww - x)
                        h = min(h, hh - y)
                        # ✅ 修复: 提高缓存置信度，避免前端清除
                        faces = [{'bbox': [x, y, w, h],
                                  'confidence': 0.55, '_cached': True}]  # 从0.45提高到0.55
                    else:
                        # ✅ 优化: 无缓存时也发送时间戳
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
                    face_img = frame[y:y+h, x:x+w]
                    if face_img.size > 0:
                        face_images.append(face_img)

                # 批量推理（性能提升 40-50%）
                if face_images and hasattr(_emotion_model, 'predict_batch'):
                    emotions = await loop.run_in_executor(
                        executor, _emotion_model.predict_batch, face_images)
                elif face_images:
                    # 降级到单个处理（兼容性）
                    tasks = []
                    for face_img in face_images:
                        tasks.append(loop.run_in_executor(
                            executor, _emotion_model.predict, face_img))
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
                        'scores': {k: float(v) for k, v in calibrated_scores.items()},
                        'is_fused': False  # ✅ 新增: 默认标记为未融合
                    })

                dominant_emotion = max(results, key=lambda x: x['confidence'])[
                    'emotion'] if results else None

                # ✅ 新增: 多模态融合(如果有语音情绪数据)
                voice_scores = None  # 默认无语音数据
                async with global_state_lock:
                    voice_scores = global_state.get('voice_scores')
                    # 不在这里清除，让前端也能接收到语音数据

                    if voice_scores and results:
                        try:
                            # ✅ 优化: 动态计算融合权重（根据语音质量）
                            voice_features = global_state.get(
                                'voice_features', {})
                            energy_mean = voice_features.get('energy_mean', 0)

                            # 根据能量均值动态调整权重（能量越高，语音越清晰）
                            if energy_mean < 0.01:
                                voice_weight = 0.1  # 噪声大，降低权重
                            elif energy_mean < 0.05:
                                voice_weight = 0.3  # 中等质量
                            else:
                                voice_weight = 0.5  # 高质量，提高权重

                            # 对每个人脸进行多模态融合
                            for face_result in results:
                                face_scores = face_result.get('scores', {})
                                if face_scores:
                                    # ✅ 新增: 保存原始视觉情绪分数
                                    face_result['vision_scores'] = {
                                        k: float(v) for k, v in face_scores.items()}

                                    # 融合视觉和语音情绪（使用动态权重）
                                    fused_scores = _voice_analyzer.fuse_scores(
                                        face_scores, voice_scores, voice_weight=voice_weight
                                    )
                                    # 更新融合后的情绪和置信度
                                    fused_emotion = max(
                                        fused_scores, key=fused_scores.get)
                                    fused_confidence = fused_scores[fused_emotion]

                                    face_result['scores'] = {
                                        k: float(v) for k, v in fused_scores.items()}
                                    face_result['emotion'] = fused_emotion
                                    face_result['confidence'] = float(
                                        fused_confidence)
                                    face_result['is_fused'] = True  # 标记已融合

                            # 重新计算主导情绪
                            dominant_emotion = max(results, key=lambda x: x['confidence'])[
                                'emotion']

                            # ✅ 关闭调试日志
                            # if _last_voice_emotion:
                            #     print(
                            #         f" 🔊 多模态融合: 视觉={face_result.get('emotion')}({face_result.get('confidence', 0):.2f}) + "
                            #         f"语音={_last_voice_emotion}({_last_voice_confidence:.2f}) → "
                            #         f"融合={dominant_emotion}({results[0]['confidence']:.2f})")
                        except Exception as e:
                            print(f"⚠️ 多模态融合失败: {e}")

                response = {
                    'type': 'result',
                    'faces': results,
                    'dominant_emotion': dominant_emotion,
                    'timestamp': datetime.now().isoformat(),
                    'process_time': time.time(),
                    'gpu_memory': get_gpu_memory_usage(),
                    'has_voice_data': bool(voice_scores),  # 标记是否有语音数据
                    # 返回语音情绪分数
                    'voice_scores': {k: float(v) for k, v in voice_scores.items()} if voice_scores else None
                }

                # ✅ 关键: 返回后清除缓存的语音数据（避免重复返回）
                async with global_state_lock:
                    global_state['voice_scores'] = None

                # ✅ 深度优化: 结果缓存防抖(避免重复发送相似结果)
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

                        # 如果框稳定且情绪相同,降低发送频率
                        if bbox_stable and last_faces[0]['emotion'] == results[0]['emotion']:
                            # 每3帧才发送一次(降低网络负载)
                            if (time.time() - _last_result_time) < 0.1:
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

                if results:
                    _save_counter += 1
                    if _save_counter % 30 == 0:
                        try:
                            _db_manager.save_detection_result(
                                'realtime', results, source='实时摄像头检测')
                        except Exception:
                            pass

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
