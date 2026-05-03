"""情感分类器 - PyTorch MobileNetV2（优化推理路径，跳过PIL中转）"""
import cv2
import torch
import torch.nn as nn
import numpy as np
from torchvision import transforms, models
from typing import Tuple, Dict
import logging

from constants import EMOTION_NAMES

logger = logging.getLogger(__name__)


class EmotionClassifierModel(nn.Module):
    """基于MobileNetV2的情感分类模型"""

    def __init__(self, num_classes: int = 7):
        super().__init__()
        self.backbone = models.mobilenet_v2(weights=None)
        num_features = self.backbone.classifier[1].in_features

        # 单通道输入
        self.backbone.features[0][0] = nn.Conv2d(
            1, 32, kernel_size=(3, 3),
            stride=(2, 2), padding=(1, 1), bias=False
        )

        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=0.2),
            nn.Linear(num_features, num_classes)
        )

    def forward(self, x):
        return self.backbone(x)


class EmotionClassifier:
    """情感分类器 - 直接使用OpenCV/NumPy预处理，跳过PIL"""

    def __init__(self, model_path: str, device: torch.device):
        self.device = device
        self.model = EmotionClassifierModel(num_classes=7).to(device)

        checkpoint = torch.load(model_path, map_location=device, weights_only=True)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()

        # FP16加速
        if device.type == 'cuda' and torch.cuda.is_bf16_supported():
            self.model = self.model.half()
            self.use_fp16 = True
            logger.info("✅ 情感模型加载成功 (CUDA FP16加速)")
        else:
            self.use_fp16 = False
            logger.info("✅ 情感模型加载成功")

    def predict(self, face_image: np.ndarray) -> Tuple[str, float, Dict[str, float]]:
        """
        预测人脸情绪 - 使用OpenCV直接预处理，跳过PIL
        """
        try:
            # BGR → Gray → Resize → Normalize，直接使用NumPy
            if len(face_image.shape) == 3:
                gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = face_image

            gray_resized = cv2.resize(gray, (96, 96))
            # Normalize: (x/255 - 0.5) / 0.5 → (x/127.5 - 1.0)
            tensor = torch.from_numpy(gray_resized.astype(np.float32)).div(127.5).sub(1.0)
            tensor = tensor.unsqueeze(0).unsqueeze(0).to(self.device)

            if self.use_fp16:
                tensor = tensor.half()

            with torch.no_grad():
                outputs = self.model(tensor)
                probabilities = torch.softmax(outputs, dim=1)[0]

            scores = {
                name: float(probabilities[i])
                for i, name in enumerate(EMOTION_NAMES)
            }

            dominant_emotion = max(scores, key=scores.get)
            confidence = scores[dominant_emotion]

            return dominant_emotion, confidence, scores

        except Exception as e:
            logger.error(f"❌ 情感识别错误: {e}")
            return 'neutral', 0.0, {name: 0.0 for name in EMOTION_NAMES}
