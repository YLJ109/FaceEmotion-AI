"""人脸检测器 - OpenCV DNN SSD"""
import cv2
import numpy as np
from typing import List, Dict, Optional
import logging
import os

logger = logging.getLogger(__name__)


class FaceDetector:
    """基于 OpenCV DNN SSD 的人脸检测器"""

    def __init__(self,
                 min_detection_confidence: float = 0.5,
                 max_num_faces: int = 10,
                 use_gpu: bool = True):
        self.max_num_faces = max_num_faces
        self.min_detection_confidence = min_detection_confidence

        proto_file = os.path.join(os.path.dirname(__file__), '..', 'configs', 'deploy.prototxt')
        model_file = os.path.join(os.path.dirname(__file__), '..', 'weights', 'res10_300x300_ssd_iter_140000_fp16.caffemodel')

        if not os.path.exists(proto_file):
            raise RuntimeError(f"Caffe prototxt 文件不存在: {proto_file}")
        if not os.path.exists(model_file):
            raise RuntimeError(f"Caffe 模型文件不存在: {model_file}")

        self.face_net = cv2.dnn.readNetFromCaffe(proto_file, model_file)
        if self.face_net.empty():
            raise RuntimeError("无法加载 Caffe SSD 模型")

        if use_gpu and cv2.cuda.getCudaEnabledDeviceCount() > 0:
            self.face_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.face_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
            logger.info("SSD 使用 GPU (CUDA) 加速")
        else:
            self.face_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.face_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            logger.info("SSD 使用 CPU")

        self._target_size = (300, 300)
        self._mean = (104.0, 177.0, 123.0)
        logger.info(f"人脸检测器就绪 | SSD | GPU: {use_gpu} | 置信度: {min_detection_confidence}")

    def get_face_roi(self, image: np.ndarray, bbox: List[int], margin_ratio: float = 0.0) -> Optional[np.ndarray]:
        x, y, w, h = bbox
        hh, ww = image.shape[:2]
        mw = int(w * margin_ratio)
        mh = int(h * margin_ratio)
        x1, y1 = max(0, x - mw), max(0, y - mh)
        x2, y2 = min(ww, x + w + mw), min(hh, y + h + mh)
        roi = image[y1:y2, x1:x2]
        return roi if roi.size > 0 and roi.shape[0] > 0 and roi.shape[1] > 0 else None

    def detect(self, frame: np.ndarray, confidence_threshold: float = None, max_faces: int = None) -> List[Dict]:
        if confidence_threshold is None:
            confidence_threshold = self.min_detection_confidence
        if max_faces is None:
            max_faces = self.max_num_faces

        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, self._target_size), 1.0, self._target_size, self._mean, False, False)
        self.face_net.setInput(blob)
        detections = self.face_net.forward()

        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > confidence_threshold:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                x1, y1, x2, y2 = box.astype(int)
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                bw, bh = x2 - x1, y2 - y1
                if bw > 0 and bh > 0:
                    faces.append({'bbox': [x1, y1, bw, bh], 'confidence': float(confidence)})

        faces.sort(key=lambda x: x['confidence'], reverse=True)
        return faces[:max_faces]
