"""人脸检测器 - Caffe SSD（支持自动检测后端）"""
import cv2
import numpy as np
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class FaceDetector:
    """基于 Caffe SSD 的人脸检测器"""

    def __init__(self, proto_file: str = None, model_file: str = None):
        """
        初始化 Caffe SSD 人脸检测器

        Args:
            proto_file: Caffe prototxt 路径
            model_file: Caffe caffemodel 路径
        """
        # 设置默认路径
        if proto_file is None:
            proto_file = 'configs/deploy.prototxt'
        if model_file is None:
            model_file = 'weights/res10_300x300_ssd_iter_140000_fp16.caffemodel'

        self.face_net = cv2.dnn.readNetFromCaffe(proto_file, model_file)
        if self.face_net.empty():
            raise RuntimeError("无法加载Caffe模型")

        # ✅ 固定使用 CPU（行业标准配置）
        # Caffe 人脸模型太小、太快，CPU 完全够用，放 GPU 纯属浪费
        self.face_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.face_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        logger.info("✅ Caffe 人脸检测器固定使用 CPU")

        self._target_size = (300, 300)
        self._mean = (104.0, 177.0, 123.0)
        self._scale_factor = 1.0
        self.conf_threshold = 0.6  # ✅ 参考realtime_inference.py，稍微降低到0.6，避免漏检
        logger.info(f"✅ Caffe人脸检测器初始化完成 | 置信度阈值: {self.conf_threshold}")

    def detect(self, frame: np.ndarray, confidence_threshold: float = 0.5, max_faces: int = 10) -> List[Dict]:
        """
        人脸检测

        参数:
            frame: 输入图像
            confidence_threshold: 置信度阈值
            max_faces: 最多处理的人脸数量(默认10)

        返回:
            检测到的人脸列表(按置信度排序,最多max_faces个)
        """
        faces = self._detect_caffe(frame, confidence_threshold)
        faces = self._postprocess_bboxes(faces, frame.shape[:2])

        # 按置信度排序并限制最多处理max_faces个人脸
        faces.sort(key=lambda x: x['confidence'], reverse=True)
        if len(faces) > max_faces:
            logger.debug(f'检测到{len(faces)}张人脸，仅处理前{max_faces}张')
            faces = faces[:max_faces]

        return faces

    def _detect_caffe(self, frame: np.ndarray, confidence_threshold: float) -> List[Dict]:
        """Caffe SSD检测实现"""
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
        """
        bbox坐标后处理优化
        - 边界裁剪
        - 面积过滤
        - 坐标对齐
        """
        h, w = image_shape
        min_face_size = 20  # 最小人脸尺寸(像素)

        filtered_faces = []
        for face in faces:
            x1, y1, bw, bh = face['bbox']
            x2, y2 = x1 + bw, y1 + bh

            # 1. 边界裁剪
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(w, x2)
            y2 = min(h, y2)

            # 2. 重新计算宽高
            bw = x2 - x1
            bh = y2 - y1

            # 3. 面积过滤(太小的框可能是误检)
            if bw < min_face_size or bh < min_face_size:
                continue

            # 4. 宽高比过滤(人脸通常是0.5-1.5之间)
            aspect_ratio = bw / bh if bh > 0 else 0
            if aspect_ratio < 0.4 or aspect_ratio > 2.0:
                continue

            filtered_faces.append({
                'bbox': [x1, y1, bw, bh],
                'confidence': face['confidence']
            })

        return filtered_faces

    @staticmethod
    def align_face(frame: np.ndarray, bbox: list, target_size: tuple = (112, 112)) -> np.ndarray:
        """
        人脸对齐与裁剪

        参数:
            frame: 原始图像
            bbox: [x, y, width, height]
            target_size: 目标尺寸 (宽, 高)

        返回:
            对齐后的人脸图像
        """
        x, y, w, h = bbox

        # 1. 扩大边界框(包含更多上下文)
        margin = int(max(w, h) * 0.25)
        x1 = max(0, x - margin)
        y1 = max(0, y - margin)
        x2 = min(frame.shape[1], x + w + margin)
        y2 = min(frame.shape[0], y + h + margin)

        # 2. 裁剪人脸区域
        face_crop = frame[y1:y2, x1:x2]

        # 3. 缩放到目标尺寸
        aligned_face = cv2.resize(
            face_crop, target_size, interpolation=cv2.INTER_CUBIC)

        return aligned_face
