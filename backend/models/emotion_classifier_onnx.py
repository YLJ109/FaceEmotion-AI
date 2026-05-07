"""情感分类器 - ONNX Runtime版本（支持FP16量化）"""
import numpy as np
import onnxruntime as ort
from typing import Tuple, Dict, Optional
import cv2
import logging
import multiprocessing

from core.constants import EMOTION_NAMES

logger = logging.getLogger(__name__)


class EmotionClassifierONNX:
    """基于ONNX的情感分类器（支持FP16量化加速）"""

    def __init__(self, model_path: str, use_quantized: bool = False):
        """
        初始化情感分类器
        
        Args:
            model_path: ONNX模型路径
            use_quantized: 是否启用FP16量化推理（可提升性能）
        """
        # ✅ 修复: 强制使用CPU，移除CUDA逻辑
        providers = ['CPUExecutionProvider']
        provider_options = [{}]
        self.use_cuda = False
        self.use_quantized = use_quantized

        # ✅ 优化: 配置ONNX Runtime CPU多线程加速
        session_options = ort.SessionOptions()
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        session_options.enable_cpu_mem_arena = True

        # ✅ 新增: FP16量化支持
        if use_quantized:
            session_options.add_session_config_entry('session.enable_fp16', '1')
            session_options.add_session_config_entry('session.intra_op_thread_spinning', '1')
            logger.info("✅ 已启用FP16量化推理")

        # 根据CPU核心数配置线程数（最多4个）
        cpu_count = multiprocessing.cpu_count()
        session_options.intra_op_num_threads = min(cpu_count, 4)
        session_options.inter_op_num_threads = min(cpu_count, 4)
        logger.info(
            f"✅ ONNX CPU线程配置: intra={session_options.intra_op_num_threads}, inter={session_options.inter_op_num_threads}")

        self.session = ort.InferenceSession(
            model_path,
            providers=providers,
            provider_options=provider_options,
            sess_options=session_options
        )
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        logger.info(
            f"📊 ONNX Input: {self.input_name}, Output: {self.output_name}")
        logger.info(f"✅ ONNX情绪识别模型加载成功 (CPU{' + FP16' if use_quantized else ''})")

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
