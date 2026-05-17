"""检测服务 - 人脸检测 + 情绪识别"""
import cv2
import numpy as np
import time
import logging
from typing import Dict, List, Optional

from models.detector import FaceDetector
from models.emotion_classifier_onnx import EmotionClassifierONNX
from core.config import ConfigManager

logger = logging.getLogger(__name__)


class DetectionService:
    """人脸检测 + 情绪识别服务"""

    def __init__(self, config_manager: ConfigManager,
                 face_detector: FaceDetector,
                 emotion_classifier: EmotionClassifierONNX):
        self.config = config_manager
        self.face_detector = face_detector
        self.emotion_classifier = emotion_classifier
        logger.info("检测服务初始化完成")

    def detect_image(self, image: np.ndarray, max_faces: int = 10) -> Dict:
        start_time = time.time()
        faces = self.face_detector.detect(image, max_faces=max_faces)
        results = []

        for face in faces:
            face_img = self.face_detector.get_face_roi(image, face['bbox'], margin_ratio=0.2)
            if face_img is None or face_img.size == 0:
                continue
            emotion, confidence, scores = self.emotion_classifier.predict(face_img)
            results.append({
                'bbox': [int(v) for v in face['bbox']],
                'emotion': emotion,
                'confidence': float(confidence),
                'scores': {k: float(v) for k, v in scores.items()},
            })

        process_time = (time.time() - start_time) * 1000
        return {
            'faces': results,
            'count': len(results),
            'process_time_ms': round(process_time, 1),
        }

    def detect_image_from_bytes(self, image_bytes: bytes, max_faces: int = 10) -> Dict:
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("无法解码图片数据")
        return self.detect_image(image, max_faces=max_faces)

    def detect_video_frame(self, frame: np.ndarray, max_faces: int = 10) -> Dict:
        return self.detect_image(frame, max_faces=max_faces)
