"""检测相关 API 路由"""
from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import time
import cv2
import numpy as np
from typing import List
import logging
import traceback

from database import DatabaseManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/detect", tags=["detection"])

# 全局依赖
_face_detector = None
_emotion_model = None
_db_manager = None


def init_detection_router(face_detector, emotion_model, db_manager: DatabaseManager):
    """初始化路由依赖"""
    global _face_detector, _emotion_model, _db_manager
    _face_detector = face_detector
    _emotion_model = emotion_model
    _db_manager = db_manager

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
    from constants import ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE

    try:
        # ✅ 优化1: 模型可用性检查
        if _face_detector is None or _emotion_model is None:
            raise HTTPException(
                status_code=503,
                detail="AI 模型未就绪，请稍后重试"
            )

        # ✅ 优化2: 文件类型验证（不要信任客户端提供的 content_type）
        if file.content_type and file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=415,
                detail=f"不支持的文件类型: {file.content_type}。支持的格式: {', '.join(ALLOWED_IMAGE_TYPES)}"
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

        faces = _face_detector.detect(frame)
        results = []

        for face in faces:
            x, y, w, h = face['bbox']
            face_img = frame[y:y+h, x:x+w]
            if face_img.size > 0 and _emotion_model:
                emotion, confidence, scores = _emotion_model.predict(face_img)
                results.append({
                    'bbox': [int(x), int(y), int(w), int(h)],
                    'emotion': emotion,
                    'confidence': float(confidence),
                    'scores': {k: float(v) for k, v in scores.items()}
                })

        # ✅ 修复: 移除后端的重复保存逻辑,由前端统一调用 /api/history/save 保存
        # _db_manager.save_detection_result('image', results, source='单张图片检测')
        return {"status": "success", "faces": results, "count": len(results)}

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
    from constants import MAX_IMAGE_SIZE

    results = []
    for file in files:
        try:
            contents = await file.read()
            if len(contents) > MAX_IMAGE_SIZE:
                continue

            nparr = np.frombuffer(contents, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is not None:
                faces = _face_detector.detect(frame)
                for face in faces:
                    x, y, w, h = face['bbox']
                    face_img = frame[y:y+h, x:x+w]
                    if face_img.size > 0 and _emotion_model:
                        emotion, confidence, scores = _emotion_model.predict(
                            face_img)
                        results.append({
                            'filename': file.filename,
                            'bbox': [int(x), int(y), int(w), int(h)],
                            'emotion': emotion,
                            'confidence': float(confidence)
                        })
        except Exception:
            pass

    # ✅ 修复: 移除后端的重复保存逻辑,由前端统一调用 /api/history/save 保存
    # _db_manager.save_detection_result('batch', results, source='批量图片检测')
    return {"status": "success", "results": results, "total": len(results)}


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

        frame_interval = max(1, int(fps))
        key_frames = []
        frame_index = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_index % frame_interval == 0:
                faces = _face_detector.detect(frame)
                frame_data = {
                    "frame": frame_index,
                    "timestamp": frame_index / fps if fps > 0 else 0,
                    "faces": []
                }

                for face in faces:
                    x, y, w, h = face['bbox']
                    face_roi = frame[y:y+h, x:x+w]
                    emotion, confidence, scores = _emotion_model.predict(
                        face_roi)

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
