"""检测相关 API 路由"""
from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import time
import cv2
import numpy as np
from typing import List
import logging
import traceback

from core.database import DatabaseManager
from music.generative_music import MusicGenerator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/detect", tags=["detection"])

# 全局依赖
_face_detector = None
_emotion_model = None
_db_manager = None
_music_generator = None


def init_detection_router(face_detector, emotion_model, db_manager: DatabaseManager):
    """初始化路由依赖"""
    global _face_detector, _emotion_model, _db_manager, _music_generator
    _face_detector = face_detector
    _emotion_model = emotion_model
    _db_manager = db_manager
    _music_generator = MusicGenerator()

    # 验证依赖是否正确注入
    if _face_detector is None:
        logger.error("❌ FaceDetector 未初始化!")
    else:
        logger.info(f"✅ FaceDetector 已初始化: {type(_face_detector).__name__}")

    if _emotion_model is None:
        logger.error("❌ EmotionModel 未初始化!")
    else:
        logger.info(f"✅ EmotionModel 已初始化: {type(_emotion_model).__name__}")

    if _db_manager is None:
        logger.error("❌ DatabaseManager 未初始化!")
    else:
        logger.info(f"✅ DatabaseManager 已初始化")


@router.post("/image")
async def detect_image(file: UploadFile = File(...)):
    """单张图片情绪检测"""
    from core.constants import ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE

    try:
        # ✅ 优化1: 模型可用性检查
        if _face_detector is None or _emotion_model is None:
            raise HTTPException(
                status_code=503,
                detail="AI 模型未就绪，请稍后重试"
            )

        # ✅ 优化2: 文件类型验证（基于文件扩展名，不要信任客户端提供的 content_type）
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif'}
        file_ext = '.' + \
            file.filename.split(
                '.')[-1].lower() if file.filename and '.' in file.filename else ''

        # 只验证扩展名，不依赖 content_type（浏览器可能发送不准确）
        if file_ext and file_ext not in allowed_extensions:
            # 如果扩展名不匹配，再检查 content_type 作为后备
            if file.content_type and file.content_type not in ALLOWED_IMAGE_TYPES:
                raise HTTPException(
                    status_code=415,
                    detail=f"不支持的文件类型: {file.content_type}。支持的格式: JPG, PNG, WebP"
                )

        contents = await file.read()

        # ✅ 优化3: 文件大小验证
        if len(contents) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"文件大小超过限制 ({MAX_IMAGE_SIZE//1024//1024}MB)，请压缩后重试"
            )

        # ✅ 优化4: 空文件检查
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="文件为空")

        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # ✅ 优化5: 图片解码验证
        if frame is None:
            raise HTTPException(status_code=422, detail="图片格式无效或已损坏")

        # ✅ 优化6: 图片尺寸验证
        if frame.shape[0] < 10 or frame.shape[1] < 10:
            raise HTTPException(status_code=422, detail="图片尺寸过小")

        # ✅ 图片检测使用默认参数，不受系统设置的检测参数影响
        # max_faces 使用默认值 10，确保检测所有可见人脸
        faces = _face_detector.detect(frame, max_faces=10)
        results = []

        for face in faces:
            face_img = _face_detector.get_face_roi(frame, face['bbox'], margin_ratio=0.2)
            if face_img is not None and face_img.size > 0 and _emotion_model:
                # ✅ 图片检测禁用防抖，避免多人脸检测时状态共享导致错误
                emotion, confidence, scores = _emotion_model.predict(face_img, use_stabilization=False)
                results.append({
                    'bbox': [int(face['bbox'][0]), int(face['bbox'][1]), int(face['bbox'][2]), int(face['bbox'][3])],
                    'emotion': emotion,
                    'confidence': float(confidence),
                    'scores': {k: float(v) for k, v in scores.items()}
                })

        # ✅ 新增: 生成音乐参数
        music_params = None
        if results and _music_generator:
            try:
                scores = results[0]['scores']
                music_params = _music_generator.generate_music_params(scores)
                logger.info(
                    f"🎵 图片检测生成音乐参数: emotion={music_params.get('emotion')}, bpm={music_params.get('bpm')}")
            except Exception as e:
                logger.warning(f"生成音乐参数失败: {e}")

        # ✅ 修复: 移除后端的重复保存逻辑,由前端统一调用 /api/history/save 保存
        # _db_manager.save_detection_result('image', results, source='单张图片检测')
        return {
            "status": "success",
            "faces": results,
            "count": len(results),
            "music_params": music_params
        }

    except HTTPException:
        raise
    except cv2.error as e:
        logger.error(f"❌ OpenCV 处理失败: {e}")
        raise HTTPException(status_code=422, detail="图片格式无效，请使用标准 JPG/PNG 格式")
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"❌ 图片检测失败: {e}\n{error_trace}")
        raise HTTPException(status_code=500, detail="内部服务器错误，请稍后重试")


@router.post("/batch")
async def detect_batch(files: List[UploadFile] = File(...)):
    """批量图片情绪检测"""
    from core.constants import MAX_IMAGE_SIZE

    results = []
    for file in files:
        try:
            contents = await file.read()
            if len(contents) > MAX_IMAGE_SIZE:
                continue

            nparr = np.frombuffer(contents, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is not None:
                # ✅ 批量图片检测使用默认参数，不受系统设置的检测参数影响
                faces = _face_detector.detect(frame, max_faces=10)
                for face in faces:
                    face_img = _face_detector.get_face_roi(frame, face['bbox'], margin_ratio=0.2)
                    if face_img is not None and face_img.size > 0 and _emotion_model:
                        # ✅ 批量图片检测禁用防抖，避免多人脸检测时状态共享导致错误
                        emotion, confidence, scores = _emotion_model.predict(
                            face_img, use_stabilization=False)
                        results.append({
                            'filename': file.filename,
                            'bbox': [int(face['bbox'][0]), int(face['bbox'][1]), int(face['bbox'][2]), int(face['bbox'][3])],
                            'emotion': emotion,
                            'confidence': float(confidence),
                            'scores': {k: float(v) for k, v in scores.items()}
                        })
        except Exception:
            pass

    # ✅ 新增: 生成音乐参数（使用第一个检测到的人脸）
    music_params = None
    if results and _music_generator:
        try:
            first_result = next((r for r in results if 'scores' in r), None)
            if first_result:
                scores = first_result['scores']
                music_params = _music_generator.generate_music_params(scores)
                logger.info(
                    f"🎵 批量检测生成音乐参数: emotion={music_params.get('emotion')}, bpm={music_params.get('bpm')}")
        except Exception as e:
            logger.warning(f"生成音乐参数失败: {e}")

    # ✅ 修复: 移除后端的重复保存逻辑,由前端统一调用 /api/history/save 保存
    # _db_manager.save_detection_result('batch', results, source='批量图片检测')
    return {
        "status": "success",
        "results": results,
        "total": len(results),
        "music_params": music_params
    }


@router.post("/video")
async def detect_video(file: UploadFile = File(...)):
    """视频情绪检测 - 提取关键帧分析"""
    try:
        video_path = f"./data/uploads/{int(time.time())}_{file.filename}"
        os.makedirs("./data/uploads", exist_ok=True)

        with open(video_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise HTTPException(status_code=400, detail="无法打开视频文件")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0

        # ✅ 视频检测使用帧间隔（每秒检测一次）
        frame_interval = max(1, int(fps)) if fps > 0 else 30
        key_frames = []
        frame_index = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_index % frame_interval == 0:
                # ✅ 视频检测使用默认参数，不受系统设置的检测参数影响
                faces = _face_detector.detect(frame, max_faces=10)
                frame_data = {
                    "frame": frame_index,
                    "timestamp": frame_index / fps if fps > 0 else 0,
                    "faces": []
                }

                for face in faces:
                    face_roi = _face_detector.get_face_roi(frame, face['bbox'], margin_ratio=0.2)
                    if face_roi is None:
                        continue
                    # ✅ 视频检测禁用防抖，避免多人脸检测时状态共享导致错误
                    emotion, confidence, scores = _emotion_model.predict(
                        face_roi, use_stabilization=False)

                    frame_data["faces"].append({
                        "bbox": face['bbox'],
                        "emotion": emotion,
                        "confidence": confidence,
                        "emotions": scores
                    })

                key_frames.append(frame_data)

            frame_index += 1

        cap.release()

        for frame in key_frames:
            frame['frame'] = int(frame['frame'])
            frame['timestamp'] = float(frame['timestamp'])
            for face in frame['faces']:
                face['bbox'] = [int(x) for x in face['bbox']]
                face['confidence'] = float(face['confidence'])

        # ✅ 修复: 为每个关键帧生成音乐参数（支持视频播放时实时切换）
        if _music_generator:
            for i, frame in enumerate(key_frames):
                if frame['faces']:
                    try:
                        first_face = frame['faces'][0]
                        scores = first_face.get('emotions', {})
                        music_params = _music_generator.generate_music_params(
                            scores)
                        # 将 music_params 添加到当前关键帧
                        frame['music_params'] = music_params

                        # 只为第一个和最后一个关键帧打印日志（避免日志过多）
                        if i == 0 or i == len(key_frames) - 1:
                            logger.info(
                                f"🎵 视频检测生成音乐参数 [帧{i}/{len(key_frames)-1}]: emotion={music_params.get('emotion')}, bpm={music_params.get('bpm')}")
                    except Exception as e:
                        logger.warning(f"生成关键帧{i}音乐参数失败: {e}")

        return {
            "status": "success",
            "video_info": {
                "duration": float(duration),
                "fps": float(fps),
                "total_frames": int(total_frames),
                "key_frames_count": len(key_frames)
            },
            "key_frames": key_frames
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-video")
async def detect_batch_video(files: List[UploadFile] = File(...)):
    """批量视频情绪检测"""
    from core.constants import MAX_VIDEO_SIZE

    results = []
    for file in files:
        try:
            # 保存视频文件
            video_path = f"./data/uploads/{int(time.time())}_{file.filename}"
            os.makedirs("./data/uploads", exist_ok=True)

            with open(video_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)

            # 打开视频
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                results.append({
                    'filename': file.filename,
                    'status': 'error',
                    'error': '无法打开视频文件'
                })
                continue

            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0

            # ✅ 批量视频检测使用帧间隔（每秒检测一次）
            frame_interval = max(1, int(fps)) if fps > 0 else 30
            key_frames = []
            frame_index = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_index % frame_interval == 0:
                    # ✅ 批量视频检测使用默认参数，不受系统设置的检测参数影响
                    faces = _face_detector.detect(frame, max_faces=10)
                    frame_data = {
                        "frame": frame_index,
                        "timestamp": frame_index / fps if fps > 0 else 0,
                        "faces": []
                    }

                    for face in faces:
                        face_roi = _face_detector.get_face_roi(frame, face['bbox'], margin_ratio=0.2)
                        if face_roi is None:
                            continue
                        # ✅ 批量视频检测禁用防抖，避免多人脸检测时状态共享导致错误
                        emotion, confidence, scores = _emotion_model.predict(
                            face_roi, use_stabilization=False)

                        frame_data["faces"].append({
                            "bbox": face['bbox'],
                            "emotion": emotion,
                            "confidence": confidence,
                            "emotions": scores
                        })

                    key_frames.append(frame_data)

                frame_index += 1

            cap.release()

            # 为每个关键帧生成音乐参数
            if _music_generator:
                for i, frame in enumerate(key_frames):
                    if frame['faces']:
                        try:
                            first_face = frame['faces'][0]
                            scores = first_face.get('emotions', {})
                            music_params = _music_generator.generate_music_params(
                                scores)
                            frame['music_params'] = music_params
                        except Exception as e:
                            logger.warning(f"生成关键帧{i}音乐参数失败: {e}")

            results.append({
                'filename': file.filename,
                'status': 'success',
                'video_info': {
                    'duration': float(duration),
                    'fps': float(fps),
                    'total_frames': int(total_frames),
                    'key_frames_count': len(key_frames)
                },
                'key_frames': key_frames
            })

            # 清理临时文件
            if os.path.exists(video_path):
                os.remove(video_path)

        except Exception as e:
            logger.error(f"处理视频 {file.filename} 失败: {e}")
            results.append({
                'filename': file.filename,
                'status': 'error',
                'error': str(e)
            })

    # 生成音乐参数（使用第一个视频的第一帧）
    music_params = None
    if results and _music_generator:
        try:
            first_success = next(
                (r for r in results if r['status'] ==
                 'success' and r.get('key_frames')),
                None
            )
            if first_success and first_success['key_frames']:
                first_frame = first_success['key_frames'][0]
                if first_frame.get('faces'):
                    scores = first_frame['faces'][0].get('emotions', {})
                    music_params = _music_generator.generate_music_params(
                        scores)
                    logger.info(
                        f" 批量视频检测生成音乐参数: emotion={music_params.get('emotion')}, bpm={music_params.get('bpm')}")
        except Exception as e:
            logger.warning(f"生成音乐参数失败: {e}")

    return {
        "status": "success",
        "results": results,
        "total": len(results),
        "success_count": sum(1 for r in results if r['status'] == 'success'),
        "music_params": music_params
    }
