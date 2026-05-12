"""情感分类器 - ONNX Runtime版本（支持GPU/CPU自动适配）"""
import numpy as np
import onnxruntime as ort
from typing import Tuple, Dict, Optional
import cv2
import logging
import multiprocessing
from collections import deque

from core.constants import EMOTION_NAMES

logger = logging.getLogger(__name__)


class EmotionClassifierONNX:
    """基于ONNX的情感分类器（支持GPU/CPU自动适配）"""

    IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

    def __init__(self, model_path: str, use_quantized: bool = False):
        self.use_quantized = use_quantized
        self.img_size = 128

        self.smooth_buffer = deque(maxlen=5)
        self.hysteresis_threshold = 0.15
        self.current_emotion = 'neutral'
        self.current_confidence = 0.0
        self.ema_alpha = 0.3
        self.ema_probs = None

        session_options = ort.SessionOptions()
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        session_options.enable_cpu_mem_arena = True

        if use_quantized:
            session_options.add_session_config_entry('session.enable_fp16', '1')
            session_options.add_session_config_entry('session.intra_op_thread_spinning', '1')
            logger.info("已启用FP16量化推理")

        cpu_count = multiprocessing.cpu_count()
        session_options.intra_op_num_threads = min(cpu_count, 4)
        session_options.inter_op_num_threads = min(cpu_count, 2)

        available_providers = ort.get_available_providers()
        logger.info(f'ONNX Runtime providers: {available_providers}')

        if 'CUDAExecutionProvider' in available_providers:
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
            self.use_cuda = True
            logger.info("ONNX情绪识别模型: 使用 CUDA")
        else:
            providers = ['CPUExecutionProvider']
            self.use_cuda = False
            logger.warning("ONNX情绪识别模型: 未检测到CUDA，降级使用 CPU")

        logger.info(
            f"ONNX CPU线程配置: intra={session_options.intra_op_num_threads}, inter={session_options.inter_op_num_threads}")

        self.session = ort.InferenceSession(
            model_path,
            providers=providers,
            sess_options=session_options
        )
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        logger.info(
            f"ONNX Input: {self.input_name}, Output: {self.output_name}")
        logger.info(f"ONNX情绪识别模型加载成功 ({'GPU' if self.use_cuda else 'CPU'}{' + FP16' if use_quantized else ''})")

    def predict(self, face_image: np.ndarray, use_stabilization: bool = True) -> Tuple[str, float, Dict[str, float]]:
        try:
            input_tensor = self._preprocess(face_image)
            outputs = self.session.run(
                [self.output_name], {self.input_name: input_tensor})
            raw_probabilities = self._softmax(outputs[0][0])

            if use_stabilization:
                self.smooth_buffer.append(raw_probabilities)

                if len(self.smooth_buffer) > 0:
                    avg_probs = np.mean(self.smooth_buffer, axis=0)
                else:
                    avg_probs = raw_probabilities

                new_emotion_idx = int(np.argmax(avg_probs))
                new_emotion = EMOTION_NAMES[new_emotion_idx]
                new_confidence = float(avg_probs[new_emotion_idx])

                self.current_emotion = new_emotion
                self.current_confidence = new_confidence

                scores = {
                    name: float(avg_probs[i])
                    for i, name in enumerate(EMOTION_NAMES)
                }
            else:
                new_emotion_idx = int(np.argmax(raw_probabilities))
                new_emotion = EMOTION_NAMES[new_emotion_idx]
                new_confidence = float(raw_probabilities[new_emotion_idx])

                scores = {
                    name: float(raw_probabilities[i])
                    for i, name in enumerate(EMOTION_NAMES)
                }

            return new_emotion, new_confidence, scores

        except Exception as e:
            logger.error(f"ONNX推理错误: {e}")
            return 'neutral', 0.0, {name: 0.0 for name in EMOTION_NAMES}

    def predict_fast(self, face_image: np.ndarray) -> Tuple[str, float, Dict[str, float]]:
        """快速预测模式：跳过所有防抖，直接返回原始结果（WebSocket实时流专用）"""
        try:
            input_tensor = self._preprocess(face_image)
            outputs = self.session.run(
                [self.output_name], {self.input_name: input_tensor})
            raw_probabilities = self._softmax(outputs[0][0])

            new_emotion_idx = int(np.argmax(raw_probabilities))
            new_emotion = EMOTION_NAMES[new_emotion_idx]
            new_confidence = float(raw_probabilities[new_emotion_idx])

            scores = {
                name: float(raw_probabilities[i])
                for i, name in enumerate(EMOTION_NAMES)
            }

            return new_emotion, new_confidence, scores

        except Exception as e:
            logger.error(f"ONNX快速推理错误: {e}")
            return 'neutral', 0.0, {name: 0.0 for name in EMOTION_NAMES}

    def reset_state(self):
        self.current_emotion = 'neutral'
        self.current_confidence = 0.0
        self.ema_probs = None
        self.smooth_buffer.clear()

    def predict_batch(self, face_images: list) -> list:
        if not face_images:
            return []

        try:
            tensors = [self._preprocess(img) for img in face_images]
            batch_tensor = np.concatenate(tensors, axis=0)
            outputs = self.session.run(
                [self.output_name], {self.input_name: batch_tensor})

            results = []
            for i in range(len(face_images)):
                raw_probabilities = self._softmax(outputs[0][i])

                new_emotion_idx = int(np.argmax(raw_probabilities))
                new_emotion = EMOTION_NAMES[new_emotion_idx]
                new_confidence = float(raw_probabilities[new_emotion_idx])

                scores = {
                    name: float(raw_probabilities[j])
                    for j, name in enumerate(EMOTION_NAMES)
                }

                results.append((new_emotion, new_confidence, scores))

            return results

        except Exception as e:
            logger.error(f"ONNX批量推理错误: {e}")
            return [self.predict(img, use_stabilization=False) for img in face_images]

    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        if len(image.shape) == 3:
            if image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            rgb = image
        else:
            rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        resized = cv2.resize(rgb, (self.img_size, self.img_size), interpolation=cv2.INTER_LINEAR)
        tensor = resized.astype(np.float32) / 255.0
        tensor = (tensor - self.IMAGENET_MEAN) / self.IMAGENET_STD
        tensor = np.transpose(tensor, (2, 0, 1))
        tensor = np.expand_dims(tensor, axis=0)

        return tensor

    @staticmethod
    def _softmax(x: np.ndarray) -> np.ndarray:
        exp_x = np.exp(x - np.max(x))
        return exp_x / exp_x.sum(axis=0)