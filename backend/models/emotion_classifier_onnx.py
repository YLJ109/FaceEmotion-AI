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

    def __init__(self, model_path: str, use_quantized: bool = False):
        """
        初始化情感分类器
        
        Args:
            model_path: ONNX模型路径
            use_quantized: 是否启用FP16量化推理（可提升性能）
        """
        self.use_quantized = use_quantized
        self.img_size = 96  # ✅ 参考realtime_inference.py，模型输入尺寸
        
        # ✅ 用于标签平滑的历史记录（解决标签乱跳问题）
        self.smooth_buffer = deque(maxlen=5)
        
        # ✅ 迟滞切换机制参数
        self.hysteresis_threshold = 0.15  # 切换阈值：新类别概率需比当前类别高出15%
        self.current_emotion = 'neutral'  # 当前保持的情绪标签
        self.current_confidence = 0.0     # 当前情绪的置信度
        
        # ✅ EMA指数移动平均参数
        self.ema_alpha = 0.3  # EMA权重，越小越平滑（0~1）
        self.ema_probs = None  # EMA平滑后的概率分布

        # 配置ONNX Runtime会话选项
        session_options = ort.SessionOptions()
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        session_options.enable_cpu_mem_arena = True

        # FP16量化支持
        if use_quantized:
            session_options.add_session_config_entry('session.enable_fp16', '1')
            session_options.add_session_config_entry('session.intra_op_thread_spinning', '1')
            logger.info("✅ 已启用FP16量化推理")

        # 根据CPU核心数配置线程数（最多4个）
        cpu_count = multiprocessing.cpu_count()
        session_options.intra_op_num_threads = min(cpu_count, 4)
        session_options.inter_op_num_threads = min(cpu_count, 2)

        # ✅ 固定使用 GPU（行业标准配置）
        # 情绪 ONNX 模型算力需求大，必须放 GPU 才不卡
        # 3060 6G 跑情绪模型绰绰有余，显存占用极低
        available_providers = ort.get_available_providers()
        logger.info(f'📊 ONNX Runtime providers: {available_providers}')

        if 'CUDAExecutionProvider' in available_providers:
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
            self.use_cuda = True
            logger.info("✅ ONNX情绪识别模型: 固定使用 CUDA (3060 6G)")
        else:
            providers = ['CPUExecutionProvider']
            self.use_cuda = False
            logger.warning("⚠️ ONNX情绪识别模型: 未检测到CUDA，降级使用 CPU")

        logger.info(
            f"✅ ONNX CPU线程配置: intra={session_options.intra_op_num_threads}, inter={session_options.inter_op_num_threads}")

        self.session = ort.InferenceSession(
            model_path,
            providers=providers,
            sess_options=session_options
        )
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        logger.info(
            f"📊 ONNX Input: {self.input_name}, Output: {self.output_name}")
        logger.info(f"✅ ONNX情绪识别模型加载成功 ({'GPU' if self.use_cuda else 'CPU'}{' + FP16' if use_quantized else ''})")

    def predict(self, face_image: np.ndarray, use_stabilization: bool = True) -> Tuple[str, float, Dict[str, float]]:
        """
        单张人脸情绪分类（完全匹配 realtime_inference.py 的逻辑）

        参数:
            face_image: 人脸图像
            use_stabilization: 是否使用防抖（实时检测用True，图片/视频检测用False）

        返回:
            (主导情绪, 置信度, 所有情绪分数)
        """
        try:
            input_tensor = self._preprocess(face_image)
            outputs = self.session.run(
                [self.output_name], {self.input_name: input_tensor})
            raw_probabilities = self._softmax(outputs[0][0])

            if use_stabilization:
                # ✅ 实时检测：使用历史帧平均平滑（与 realtime_inference.py 一致）
                self.smooth_buffer.append(raw_probabilities)
                
                # 计算最近几帧的平均概率（解决标签乱跳问题）
                if len(self.smooth_buffer) > 0:
                    avg_probs = np.mean(self.smooth_buffer, axis=0)
                else:
                    avg_probs = raw_probabilities
                
                # 使用平均概率确定情绪
                new_emotion_idx = int(np.argmax(avg_probs))
                new_emotion = EMOTION_NAMES[new_emotion_idx]
                new_confidence = float(avg_probs[new_emotion_idx])
                
                # 更新当前状态
                self.current_emotion = new_emotion
                self.current_confidence = new_confidence
                
                # ✅ 使用平均概率作为分数（与 realtime_inference.py 一致）
                scores = {
                    name: float(avg_probs[i])
                    for i, name in enumerate(EMOTION_NAMES)
                }
            else:
                # ✅ 非实时检测（图片/视频/批量）：直接返回原始结果
                new_emotion_idx = int(np.argmax(raw_probabilities))
                new_emotion = EMOTION_NAMES[new_emotion_idx]
                new_confidence = float(raw_probabilities[new_emotion_idx])
                
                # 使用原始概率作为分数
                scores = {
                    name: float(raw_probabilities[i])
                    for i, name in enumerate(EMOTION_NAMES)
                }

            return new_emotion, new_confidence, scores

        except Exception as e:
            logger.error(f"❌ ONNX推理错误: {e}")
            return 'neutral', 0.0, {name: 0.0 for name in EMOTION_NAMES}
    
    def reset_state(self):
        """重置防抖状态（用于人脸切换或重新开始）"""
        self.current_emotion = 'neutral'
        self.current_confidence = 0.0
        self.ema_probs = None
        self.smooth_buffer.clear()

    def predict_batch(self, face_images: list) -> list:
        """
        批量人脸情绪分类（带防抖处理）

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

            # 解析结果（批量检测不使用防抖，直接返回原始结果）
            results = []
            for i in range(len(face_images)):
                raw_probabilities = self._softmax(outputs[0][i])
                
                # ✅ 批量检测不使用防抖，直接返回原始结果
                new_emotion_idx = int(np.argmax(raw_probabilities))
                new_emotion = EMOTION_NAMES[new_emotion_idx]
                new_confidence = float(raw_probabilities[new_emotion_idx])
                
                # ✅ 使用原始概率作为分数
                scores = {
                    name: float(raw_probabilities[j])
                    for j, name in enumerate(EMOTION_NAMES)
                }
                
                results.append((new_emotion, new_confidence, scores))

            return results

        except Exception as e:
            logger.error(f"❌ ONNX批量推理错误: {e}")
            # 降级到单个处理（批量检测不使用防抖）
            return [self.predict(img, use_stabilization=False) for img in face_images]

    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        """图像预处理 - 转为灰度图并归一化（参考realtime_inference.py）"""
        # 确保输入是 BGR 格式
        if len(image.shape) == 3:
            if image.shape[2] == 4:
                # RGBA 转 BGR
                image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
            # 转为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # 调整大小（使用与训练一致的插值方式）
        resized = cv2.resize(gray, (self.img_size, self.img_size), interpolation=cv2.INTER_LINEAR)
        
        # ✅ 完全匹配 realtime_inference.py 的 ToTensor() 行为
        # ToTensor() 会将 uint8 转为 float 并除以 255
        normalized = resized.astype(np.float32) / 255.0
        
        # 添加通道维度并扩展 batch 维度
        tensor = normalized.reshape(1, 1, self.img_size, self.img_size)

        return tensor

    @staticmethod
    def _softmax(x: np.ndarray) -> np.ndarray:
        exp_x = np.exp(x - np.max(x))
        return exp_x / exp_x.sum(axis=0)
