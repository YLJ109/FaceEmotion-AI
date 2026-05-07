"""
情感分类器单元测试
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.emotion_classifier_onnx import EmotionClassifierONNX
from core.constants import EMOTION_NAMES


class TestEmotionClassifierONNX:
    """情感分类器测试类"""
    
    @pytest.fixture(scope="class")
    def classifier(self):
        """创建分类器实例"""
        model_path = './backend/weights/emotion_model.onnx'
        if not os.path.exists(model_path):
            pytest.skip("模型文件不存在，跳过测试")
        
        classifier = EmotionClassifierONNX(model_path, use_quantized=False)
        yield classifier
    
    def test_model_initialization(self, classifier):
        """测试模型初始化"""
        assert classifier is not None
        assert classifier.session is not None
        assert classifier.input_name is not None
        assert classifier.output_name is not None
    
    def test_predict_single_face(self, classifier):
        """测试单张人脸预测"""
        # 创建随机测试图像（96x96灰度图）
        test_image = np.random.randint(0, 255, (96, 96, 3), dtype=np.uint8)
        
        result = classifier.predict(test_image)
        
        # 验证返回值结构
        assert isinstance(result, tuple)
        assert len(result) == 3
        
        emotion, confidence, scores = result
        
        # 验证情感标签
        assert emotion in EMOTION_NAMES
        
        # 验证置信度范围
        assert 0 <= confidence <= 1
        
        # 验证分数字典
        assert isinstance(scores, dict)
        assert len(scores) == len(EMOTION_NAMES)
        
        # 验证所有分数在合理范围内
        for name, score in scores.items():
            assert name in EMOTION_NAMES
            assert 0 <= score <= 1
        
        # 验证分数总和约等于1
        assert abs(sum(scores.values()) - 1.0) < 0.01
    
    def test_predict_batch(self, classifier):
        """测试批量预测"""
        # 创建多张测试图像
        test_images = [
            np.random.randint(0, 255, (96, 96, 3), dtype=np.uint8)
            for _ in range(3)
        ]
        
        results = classifier.predict_batch(test_images)
        
        # 验证结果数量
        assert len(results) == 3
        
        # 验证每个结果的结构
        for result in results:
            assert isinstance(result, tuple)
            assert len(result) == 3
            emotion, confidence, scores = result
            assert emotion in EMOTION_NAMES
            assert 0 <= confidence <= 1
            assert isinstance(scores, dict)
    
    def test_predict_empty_batch(self, classifier):
        """测试空批量预测"""
        results = classifier.predict_batch([])
        assert results == []
    
    def test_fp16_quantization(self):
        """测试FP16量化模式"""
        model_path = './backend/weights/emotion_model.onnx'
        if not os.path.exists(model_path):
            pytest.skip("模型文件不存在，跳过测试")
        
        classifier = EmotionClassifierONNX(model_path, use_quantized=True)
        
        assert classifier.use_quantized is True
        assert classifier.session is not None
        
        # 测试量化模式下的预测
        test_image = np.random.randint(0, 255, (96, 96, 3), dtype=np.uint8)
        emotion, confidence, scores = classifier.predict(test_image)
        
        assert emotion in EMOTION_NAMES
        assert 0 <= confidence <= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
