"""人脸检测器 - Caffe SSD（支持自动检测后端）"""
import cv2
import numpy as np
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class FaceDetector:
    """基于 Caffe SSD 的人脸检测器"""

    def __init__(self, proto_file: str = None, model_file: str = None):
        if proto_file is None:
            proto_file = 'configs/deploy.prototxt'
        if model_file is None:
            model_file = 'weights/res10_300x300_ssd_iter_140000_fp16.caffemodel'

        self.face_net = cv2.dnn.readNetFromCaffe(proto_file, model_file)
        if self.face_net.empty():
            raise RuntimeError("无法加载Caffe模型")

        self.face_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.face_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        logger.info("Caffe 人脸检测器使用 CPU")

        self._target_size = (300, 300)
        self._mean = (104.0, 177.0, 123.0)
        self._scale_factor = 1.0
        self.conf_threshold = 0.5
        self._min_face_size = 20

        self._last_face_bbox = None
        self._tracking_lost_frames = 0
        self._max_tracking_lost = 15
        self._roi_margin_ratio = 0.4

        logger.info(f"Caffe人脸检测器初始化完成 | 置信度阈值: {self.conf_threshold}")

    def detect(self, frame: np.ndarray, confidence_threshold: float = 0.5, max_faces: int = 10) -> List[Dict]:
        faces = self._detect_caffe(frame, confidence_threshold)
        faces = self._postprocess_bboxes(faces, frame.shape[:2])

        faces.sort(key=lambda x: x['confidence'], reverse=True)
        if len(faces) > max_faces:
            faces = faces[:max_faces]

        if faces:
            self._last_face_bbox = faces[0]['bbox'].copy()
            self._tracking_lost_frames = 0
        else:
            self._tracking_lost_frames += 1
            if self._tracking_lost_frames > self._max_tracking_lost:
                self._last_face_bbox = None

        return faces

    def detect_with_tracking(self, frame: np.ndarray, confidence_threshold: float = 0.5, max_faces: int = 10) -> List[Dict]:
        """带ROI跟踪的快速检测：有人脸跟踪时仅在ROI区域内检测"""
        if self._last_face_bbox is not None and self._tracking_lost_frames < 5:
            x, y, w, h = self._last_face_bbox
            h_img, w_img = frame.shape[:2]

            margin_w = int(w * self._roi_margin_ratio)
            margin_h = int(h * self._roi_margin_ratio)

            roi_x1 = max(0, x - margin_w)
            roi_y1 = max(0, y - margin_h)
            roi_x2 = min(w_img, x + w + margin_w)
            roi_y2 = min(h_img, y + h + margin_h)

            if roi_x2 > roi_x1 and roi_y2 > roi_y1:
                roi = frame[roi_y1:roi_y2, roi_x1:roi_x2]
                faces = self._detect_caffe(roi, confidence_threshold)

                for face in faces:
                    face['bbox'][0] += roi_x1
                    face['bbox'][1] += roi_y1

                faces = self._postprocess_bboxes(faces, frame.shape[:2])
                faces.sort(key=lambda x: x['confidence'], reverse=True)

                if faces:
                    self._last_face_bbox = faces[0]['bbox'].copy()
                    self._tracking_lost_frames = 0
                    return faces[:max_faces]

        return self.detect(frame, confidence_threshold, max_faces)

    def _detect_caffe(self, frame: np.ndarray, confidence_threshold: float) -> List[Dict]:
        h, w = frame.shape[:2]

        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, self._target_size),
            self._scale_factor,
            self._target_size,
            self._mean,
            False,
            False
        )

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

                bbox_width = x2 - x1
                bbox_height = y2 - y1

                faces.append({
                    'bbox': [x1, y1, bbox_width, bbox_height],
                    'confidence': float(confidence)
                })

        return faces

    def _postprocess_bboxes(self, faces: List[Dict], image_shape: tuple) -> List[Dict]:
        h, w = image_shape

        filtered_faces = []
        for face in faces:
            x1, y1, bw, bh = face['bbox']
            x2, y2 = x1 + bw, y1 + bh

            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(w, x2)
            y2 = min(h, y2)

            bw = x2 - x1
            bh = y2 - y1

            if bw < self._min_face_size or bh < self._min_face_size:
                continue

            aspect_ratio = bw / bh if bh > 0 else 0
            if aspect_ratio < 0.4 or aspect_ratio > 2.0:
                continue

            filtered_faces.append({
                'bbox': [x1, y1, bw, bh],
                'confidence': face['confidence']
            })

        return filtered_faces

    def get_face_roi(self, frame: np.ndarray, bbox: list, margin_ratio: float = 0.2) -> Optional[np.ndarray]:
        """提取人脸ROI，带边距以保留更多上下文信息"""
        x, y, w, h = bbox
        h_img, w_img = frame.shape[:2]

        margin_w = int(w * margin_ratio)
        margin_h = int(h * margin_ratio)

        x1 = max(0, x - margin_w)
        y1 = max(0, y - margin_h)
        x2 = min(w_img, x + w + margin_w)
        y2 = min(h_img, y + h + margin_h)

        if x2 <= x1 or y2 <= y1:
            return None

        return frame[y1:y2, x1:x2]

    @staticmethod
    def align_face(frame: np.ndarray, bbox: list, target_size: tuple = (112, 112)) -> np.ndarray:
        x, y, w, h = bbox

        margin = int(max(w, h) * 0.25)
        x1 = max(0, x - margin)
        y1 = max(0, y - margin)
        x2 = min(frame.shape[1], x + w + margin)
        y2 = min(frame.shape[0], y + h + margin)

        face_crop = frame[y1:y2, x1:x2]
        aligned_face = cv2.resize(
            face_crop, target_size, interpolation=cv2.INTER_CUBIC)

        return aligned_face