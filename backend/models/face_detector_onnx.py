"""人脸检测器 - ONNX Runtime 版本（Ultra-Light GPU加速）"""
import numpy as np
import onnxruntime as ort
from typing import List, Dict, Tuple
import cv2
import logging

# 抑制 ONNX Runtime 内部图结构警告（模型导出遗留问题，不影响推理）
ort.set_default_logger_severity(3)

logger = logging.getLogger(__name__)


class FaceDetectorONNX:
    """基于ONNX的超轻量人脸检测器（自动GPU加速）"""

    def __init__(self, model_path: str, input_size: Tuple[int, int] = (320, 240)):
        providers = ['CPUExecutionProvider']
        try:
            if 'CUDAExecutionProvider' in ort.get_available_providers():
                providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
                logger.info("✅ 人脸检测器ONNX加载成功 (CUDA加速)")
            else:
                logger.info("✅ 人脸检测器加载成功 (CPU)")
        except:
            logger.info("✅ 人脸检测器加载成功 (CPU)")

        self.session = ort.InferenceSession(model_path, providers=providers)
        self.input_name = self.session.get_inputs()[0].name
        self.input_size = input_size
        self._init_priors()
        logger.info("✅ ONNX人脸检测器初始化完成")

    def _init_priors(self):
        """初始化先验框（PriorBox for RFB-320）"""
        w, h = self.input_size
        min_boxes = [[10, 16, 24], [32, 48], [64, 96], [128, 192, 256]]
        fm_sizes = [(w // 8, h // 8), (w // 16, h // 16),
                    (w // 32, h // 32), (w // 64, h // 64)]

        priors = []
        for idx, (fm_w, fm_h) in enumerate(fm_sizes):
            for y in range(fm_h):
                for x in range(fm_w):
                    for box_size in min_boxes[idx]:
                        priors.append([
                            (x + 0.5) / fm_w,
                            (y + 0.5) / fm_h,
                            box_size / w,
                            box_size / h,
                        ])
        self.priors = np.array(priors, dtype=np.float32)

    def detect(self, frame: np.ndarray, confidence_threshold: float = 0.6) -> List[Dict]:
        """检测人脸

        Args:
            frame: 输入图像
            confidence_threshold: 置信度阈值，默认0.6（减少误检测）
        """
        h, w = frame.shape[:2]

        # 预处理: BGR→RGB, resize→CHW, normalize
        resized = cv2.resize(frame, self.input_size)
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        tensor = rgb.astype(np.float32).transpose(2, 0, 1)[np.newaxis] / 255.0

        # ONNX 推理
        outputs = self.session.run(None, {self.input_name: tensor})
        # outputs[0]: scores [1, N, 2], outputs[1]: boxes [1, N, 4]

        face_scores = outputs[0][0, :, 1]  # face confidence
        keep = face_scores > confidence_threshold

        if not np.any(keep):
            return []

        boxes = outputs[1][0][keep]
        scores = face_scores[keep]

        # ✅ 修复: 使用实际输出的boxes数量，而不是priors
        # RFB-320模型的输出已经解码，直接使用
        priors_count = self.priors.shape[0]
        actual_count = outputs[1].shape[1]

        if actual_count != priors_count:
            # 模型输出与priors不匹配，使用简化解码
            logger.debug(
                f"️ Prior数量({priors_count})与输出({actual_count})不匹配，使用简化解码")
            # 直接使用输出的boxes，假设已经是相对坐标
            x1 = np.clip(boxes[:, 0], 0, 1)
            y1 = np.clip(boxes[:, 1], 0, 1)
            x2 = np.clip(boxes[:, 2], 0, 1)
            y2 = np.clip(boxes[:, 3], 0, 1)
        else:
            # 使用priors解码（原始逻辑）
            priors = self.priors[keep]

            # 解码框（Variance-based decoding）
            prior_cx, prior_cy = priors[:, 0], priors[:, 1]
            prior_w, prior_h = priors[:, 2], priors[:, 3]

            decode_cx = boxes[:, 0] * 0.1 * prior_w + prior_cx
            decode_cy = boxes[:, 1] * 0.1 * prior_h + prior_cy
            decode_w = np.exp(boxes[:, 2] * 0.2) * prior_w
            decode_h = np.exp(boxes[:, 3] * 0.2) * prior_h

            # 转 x1y1x2y2 + clip
            x1 = np.clip(decode_cx - decode_w / 2, 0, 1)
            y1 = np.clip(decode_cy - decode_h / 2, 0, 1)
            x2 = np.clip(decode_cx + decode_w / 2, 0, 1)
            y2 = np.clip(decode_cy + decode_h / 2, 0, 1)

        # 缩放到原图尺寸
        x1 = (x1 * w).astype(int)
        y1 = (y1 * h).astype(int)
        x2 = (x2 * w).astype(int)
        y2 = (y2 * h).astype(int)

        # NMS 去重
        # ✅ 优化: 提高 NMS 阈值从 0.3 到 0.45，更有效合并重叠框
        boxes_list = np.stack([x1, y1, x2, y2], axis=1).tolist()
        indices = cv2.dnn.NMSBoxes(boxes_list, scores.tolist(),
                                   confidence_threshold, 0.45)

        faces = []
        if len(indices) > 0:
            indices = indices.flatten()
            for idx in indices:
                bx1, by1, bx2, by2 = boxes_list[idx]
                faces.append({
                    'bbox': [int(bx1), int(by1),
                             int(bx2 - bx1), int(by2 - by1)],
                    'confidence': float(scores[idx]),
                })

        return faces
