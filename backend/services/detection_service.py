"""
人脸情感检测服务层
负责封装检测业务逻辑，与API层解耦
"""

import cv2
import base64
import numpy as np
from typing import Tuple, List, Dict, Optional

from models.detector import FaceDetector
from models.emotion_classifier_onnx import EmotionClassifierONNX
from optimizer.dynamic_inference import DynamicInferenceOptimizer
from core.config_manager import ConfigManager


class DetectionService:
    """检测服务类"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.face_detector = FaceDetector()
        self.emotion_classifier = EmotionClassifierONNX(
            model_path=self.config.get('model.path', './weights/emotion_model.onnx'),
            use_quantized=self.config.get('model.use_quantization', True)
        )
        self.optimizer = DynamicInferenceOptimizer()
        
        # 缓存上一帧结果用于运动检测复用
        self._last_frame_results = None
        self._last_frame_time = 0
        
    def detect_emotion(self, image_base64: str) -> Dict:
        """
        检测图像中的人脸情感
        
        Args:
            image_base64: Base64编码的图像数据
        
        Returns:
            检测结果字典
        """
        try:
            # 解码图像
            image = self._decode_base64_image(image_base64)
            
            # 应用动态推理优化
            if not self.optimizer.should_process():
                return self._last_frame_results or self._create_empty_result()
            
            # 人脸检测
            faces = self.face_detector.detect(image)
            
            if not faces:
                return self._create_empty_result()
            
            # 情感分析
            results = []
            for face in faces:
                emotion_result = self._analyze_emotion(image, face)
                results.append(emotion_result)
            
            # 更新缓存
            self._last_frame_results = {
                'faces': results,
                'timestamp': self.optimizer.get_current_time()
            }
            
            return self._last_frame_results
            
        except Exception as e:
            import logging
            logging.error(f"Detection error: {str(e)}")
            return self._create_empty_result(error=str(e))
    
    def _decode_base64_image(self, image_base64: str) -> np.ndarray:
        """解码Base64图像"""
        # 移除可能的 data:image 前缀
        if 'base64,' in image_base64:
            image_base64 = image_base64.split('base64,')[1]
        
        # 解码并转换为OpenCV格式
        image_bytes = base64.b64decode(image_base64)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        # 转换为RGB格式
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        return image
    
    def _analyze_emotion(self, image: np.ndarray, face: dict) -> Dict:
        """分析单张人脸的情感"""
        # 提取人脸区域
        x1, y1, x2, y2 = face['bbox']
        face_roi = image[y1:y2, x1:x2]
        
        # 调整大小以匹配模型输入
        face_roi = cv2.resize(face_roi, (96, 96))
        
        # 预处理
        face_roi = face_roi / 255.0
        face_roi = np.expand_dims(face_roi, axis=0).astype(np.float32)
        
        # 推理
        emotion_probs = self.emotion_classifier.predict(face_roi)
        
        # 获取最可能的情感
        emotion_labels = ['happy', 'sad', 'angry', 'surprise', 'fear', 'disgust', 'neutral']
        max_idx = np.argmax(emotion_probs)
        dominant_emotion = emotion_labels[max_idx]
        confidence = float(emotion_probs[max_idx])
        
        return {
            'bbox': face['bbox'],
            'confidence': face['confidence'],
            'emotion': dominant_emotion,
            'emotion_confidence': confidence,
            'all_emotions': dict(zip(emotion_labels, [float(p) for p in emotion_probs]))
        }
    
    def _create_empty_result(self, error: str = None) -> Dict:
        """创建空结果"""
        return {
            'faces': [],
            'timestamp': self.optimizer.get_current_time(),
            'error': error
        }
    
    def get_detection_stats(self) -> Dict:
        """获取检测统计信息"""
        return {
            'total_frames_processed': self.optimizer.frame_count,
            'frames_skipped': self.optimizer.skipped_frames,
            'avg_latency_ms': self.optimizer.get_avg_latency(),
            'current_threshold': self.optimizer.confidence_threshold
        }
    
    def update_optimizer_params(self, params: Dict):
        """更新优化器参数"""
        if 'target_latency_ms' in params:
            self.optimizer.target_latency = params['target_latency_ms']
        if 'max_skip_frames' in params:
            self.optimizer.max_skip_frames = params['max_skip_frames']
        if 'confidence_threshold' in params:
            self.optimizer.confidence_threshold = params['confidence_threshold']


# 单例模式
_detection_service_instance = None

def get_detection_service() -> DetectionService:
    """获取检测服务实例（单例）"""
    global _detection_service_instance
    if _detection_service_instance is None:
        _detection_service_instance = DetectionService()
    return _detection_service_instance
