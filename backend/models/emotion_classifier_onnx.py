"""情感分类器 - ONNX Runtime版本（使用共享常量）"""
import numpy as np
import onnxruntime as ort
from typing import Tuple, Dict
import cv2
import logging

from core.constants import EMOTION_NAMES

logger = logging.getLogger(__name__)


class EmotionClassifierONNX:
    """基于ONNX的情感分类器（CPU版）"""

    def __init__(self, model_path: str):
        # ✅ 修复: 强制使用CPU，移除CUDA逻辑
        providers = ['CPUExecutionProvider']
        provider_options = [{}]
        self.use_cuda = False

        self.session = ort.InferenceSession(
            model_path,
            providers=providers,
            provider_options=provider_options
        )
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        logger.info(
            f"📊 ONNX Input: {self.input_name}, Output: {self.output_name}")
        logger.info(f"✅ ONNX情绪识别模型加载成功 (CPU)")

    def predict(self, face_image: np.ndarray) -> Tuple[str, float, Dict[str, float]]:
        """
        单张人脸情绪分类

        参数:
            face_image: 人脸图像

        返回:
            (主导情绪, 置信度, 所有情绪分数)
        """
        try:
            input_tensor = self._preprocess(face_image)
            outputs = self.session.run(
                [self.output_name], {self.input_name: input_tensor})
            probabilities = self._softmax(outputs[0][0])

            scores = {
                name: float(probabilities[i])
                for i, name in enumerate(EMOTION_NAMES)
            }

            dominant_emotion = max(scores, key=scores.get)
            confidence = scores[dominant_emotion]

            return dominant_emotion, confidence, scores

        except Exception as e:
            logger.error(f"❌ ONNX推理错误: {e}")
            return 'neutral', 0.0, {name: 0.0 for name in EMOTION_NAMES}

    # ✅ 新增: 批量推理方法
    def predict_batch(self, face_images: list) -> list:
        """
        批量人脸情绪分类

        参数:
            face_images: 人脸图像列表

        返回:
            [(主导情绪, 置信度, 所有情绪分数), ...]
        """
        if not face_images:
            return []

        try:
            # 预处理所有图像
            tensors = [self._preprocess(img) for img in face_images]

            # 合并为一个batch
            batch_tensor = np.concatenate(tensors, axis=0)

            # 批量推理
            outputs = self.session.run(
                [self.output_name], {self.input_name: batch_tensor})

            # 解析结果
            results = []
            for i in range(len(face_images)):
                probabilities = self._softmax(outputs[0][i])
                scores = {
                    name: float(probabilities[j])
                    for j, name in enumerate(EMOTION_NAMES)
                }
                dominant_emotion = max(scores, key=scores.get)
                confidence = scores[dominant_emotion]
                results.append((dominant_emotion, confidence, scores))

            return results

        except Exception as e:
            logger.error(f"❌ ONNX批量推理错误: {e}")
            # 降级到单个处理
            return [self.predict(img) for img in face_images]

    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        """直接使用OpenCV预处理"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        resized = cv2.resize(gray, (96, 96))
        normalized = resized.astype(np.float32) / 127.5 - 1.0
        tensor = normalized.reshape(1, 1, 96, 96)

        return tensor

    @staticmethod
    def _softmax(x: np.ndarray) -> np.ndarray:
        exp_x = np.exp(x - np.max(x))
        return exp_x / exp_x.sum(axis=0)
