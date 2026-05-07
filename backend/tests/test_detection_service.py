"""
检测服务单元测试
"""

import pytest
import base64
import cv2
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.detection_service import DetectionService, get_detection_service


class TestDetectionService:
    """检测服务测试类"""
    
    @pytest.fixture(scope="class")
    def service(self):
        """创建检测服务实例"""
        service = DetectionService()
        yield service
    
    def test_service_initialization(self, service):
        """测试服务初始化"""
        assert service is not None
        assert service.face_detector is not None
        assert service.emotion_classifier is not None
        assert service.optimizer is not None
    
    def test_service_singleton(self):
        """测试单例模式"""
        service1 = get_detection_service()
        service2 = get_detection_service()
        
        assert service1 is service2
    
    def test_decode_base64_image(self, service):
        """测试Base64图像解码"""
        # 创建测试图像
        test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # 编码为Base64
        _, buffer = cv2.imencode('.jpg', cv2.cvtColor(test_image, cv2.COLOR_RGB2BGR))
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # 解码
        decoded_image = service._decode_base64_image(image_base64)
        
        # 验证解码结果
        assert decoded_image is not None
        assert len(decoded_image.shape) == 3
        assert decoded_image.shape[2] == 3  # RGB
    
    def test_detect_empty_image(self, service):
        """测试空图像检测"""
        # 创建空图像的Base64编码
        empty_image = np.zeros((10, 10, 3), dtype=np.uint8)
        _, buffer = cv2.imencode('.jpg', empty_image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        result = service.detect_emotion(image_base64)
        
        # 验证结果结构
        assert isinstance(result, dict)
        assert 'faces' in result
        assert isinstance(result['faces'], list)
    
    def test_get_detection_stats(self, service):
        """测试获取检测统计信息"""
        stats = service.get_detection_stats()
        
        assert isinstance(stats, dict)
        assert 'total_frames_processed' in stats
        assert 'frames_skipped' in stats
        assert 'avg_latency_ms' in stats
        assert 'current_threshold' in stats
        
        # 验证统计值类型
        assert isinstance(stats['total_frames_processed'], int)
        assert isinstance(stats['frames_skipped'], int)
        assert isinstance(stats['avg_latency_ms'], (int, float))
        assert isinstance(stats['current_threshold'], float)
    
    def test_update_optimizer_params(self, service):
        """测试更新优化器参数"""
        original_threshold = service.optimizer.confidence_threshold
        
        # 更新参数
        service.update_optimizer_params({
            'target_latency_ms': 60,
            'max_skip_frames': 3,
            'confidence_threshold': 0.7
        })
        
        # 验证更新结果
        assert service.optimizer.target_latency == 60
        assert service.optimizer.max_skip_frames == 3
        assert service.optimizer.confidence_threshold == 0.7
        
        # 恢复原值
        service.update_optimizer_params({
            'confidence_threshold': original_threshold
        })


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
