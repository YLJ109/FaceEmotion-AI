"""人脸检测器 - 双模型支持（Caffe SSD + ONNX RFB）"""
import cv2
import numpy as np
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class FaceDetector:
    """人脸检测器 - 支持Caffe SSD和ONNX RFB双模型"""

    def __init__(self, proto_file: str, model_file: str, onnx_model_path: Optional[str] = None, use_onnx: bool = False):
        self.use_onnx = use_onnx
        self.onnx_detector = None

        # ✅ 优化1: 支持ONNX RFB模型（更高精度）
        if use_onnx and onnx_model_path:
            try:
                from models.face_detector_onnx import FaceDetectorONNX
                self.onnx_detector = FaceDetectorONNX(
                    model_path=onnx_model_path,
                    input_size=(320, 240)  # RFB-320 输入尺寸
                )
                logger.info("✅ 使用ONNX RFB人脸检测器 (高精度)")
                return
            except Exception as e:
                logger.warning(f"⚠️ ONNX RFB模型加载失败，降级到Caffe: {e}")

        # 默认使用Caffe SSD
        self.face_net = cv2.dnn.readNetFromCaffe(proto_file, model_file)
        if self.face_net.empty():
            raise RuntimeError("无法加载Caffe模型")

        # 安全检测 CUDA 是否真正可用（setPreferableBackend 不报错，forward() 才报）
        use_cuda = False
        try:
            if hasattr(cv2, 'cuda'):
                use_cuda = cv2.cuda.getCudaEnabledDeviceCount() > 0
        except Exception:
            pass

        if use_cuda:
            self.face_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.face_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
            logger.info("✅ 人脸检测器使用 CUDA 加速 (Caffe)")
        else:
            self.face_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.face_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            # 不设置线程数，让 OpenCV 自动管理，避免与 asyncio 线程池冲突
            logger.info("⚠️ 人脸检测器使用 CPU（OpenCV未内置CUDA支持）")

        # 缓存blob创建参数
        self._target_size = (300, 300)
        self._mean = (104.0, 177.0, 123.0)
        self._scale_factor = 1.0

        logger.info("✅ Caffe人脸检测器初始化完成")

    def detect(self, frame: np.ndarray, confidence_threshold: float = 0.6, max_faces: int = 10) -> List[Dict]:
        """
        人脸检测

        参数:
            frame: 输入图像
            confidence_threshold: 置信度阈值
            max_faces: ✅ 修改: 最多处理的人脸数量(默认10)

        返回:
            检测到的人脸列表(按置信度排序,最多max_faces个)
        """
        # ✅ 优化1: 优先使用ONNX RFB模型
        if self.onnx_detector:
            faces = self.onnx_detector.detect(frame, confidence_threshold)
        else:
            faces = self._detect_caffe(frame, confidence_threshold)

        # ✅ 优化2: bbox坐标后处理优化
        faces = self._postprocess_bboxes(faces, frame.shape[:2])

        # ✅ 按置信度排序并限制最多处理max_faces个人脸
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

    # ✅ 优化2: bbox坐标后处理优化
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

    # ✅ 优化3: 人脸对齐功能
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
