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
from core.config import ConfigManager


class DetectionService:
    """检测服务类"""
    
    def __init__(self):
        self.config = ConfigManager()
        
        # 加载人脸检测模型
        proto_path = self.config.get('face_detector_proto', 'configs/deploy.prototxt')
        model_path = self.config.get('face_detector_model', 'weights/res10_300x300_ssd_iter_140000_fp16.caffemodel')
        self.face_detector = FaceDetector(proto_file=proto_path, model_file=model_path)
        
        # 加载情感分类模型
        emotion_model_path = self.config.get('emotion_model', 'weights/final_model.onnx')
        self.emotion_classifier = EmotionClassifierONNX(
            model_path=emotion_model_path,
            use_quantized=self.config.get('use_fp16', True)
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
            confidence_threshold = self.config.get('face_detect_confidence', 0.5)
            faces = self.face_detector.detect(image, confidence_threshold=confidence_threshold)
            
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
        
        return image
    
    def _analyze_emotion(self, image: np.ndarray, face: dict) -> Dict:
        face_roi = self.face_detector.get_face_roi(image, face['bbox'], margin_ratio=0.2)

        if face_roi is None or face_roi.size == 0:
            return {
                'bbox': face['bbox'],
                'confidence': face['confidence'],
                'emotion': 'neutral',
                'emotion_confidence': 0.0,
                'all_emotions': {}
            }

        emotion, confidence, scores = self.emotion_classifier.predict(face_roi, use_stabilization=False)
        
        return {
            'bbox': face['bbox'],
            'confidence': face['confidence'],
            'emotion': emotion,
            'emotion_confidence': confidence,
            'all_emotions': scores
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
