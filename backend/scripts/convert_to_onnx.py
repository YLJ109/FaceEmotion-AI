"""
将PyTorch情感分类模型转换为ONNX格式
更新: 使用共享常量结构引用
"""
import torch
import torch.nn as nn
from torchvision import models
import os
import sys

# 动态引入共享常量路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class EmotionClassifierModel(nn.Module):
    """与 emotion_classifier.py 保持一致的模型结构"""

    def __init__(self, num_classes: int = 7):
        super().__init__()
        self.backbone = models.mobilenet_v2(weights=None)
        num_features = self.backbone.classifier[1].in_features

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


def convert_to_onnx():
    """转换PyTorch模型为ONNX格式"""

    print("=" * 60)
    print("🔄 PyTorch → ONNX 模型转换")
    print("=" * 60)

    pth_path = './models/pytorch_final_3060.pth'
    onnx_path = './models/emotion_model.onnx'

    if not os.path.exists(pth_path):
        print(f"❌ 模型文件不存在: {pth_path}")
        return

    device = torch.device('cpu')
    print("\n📥 加载PyTorch模型...")

    checkpoint = torch.load(pth_path, map_location=device, weights_only=True)
    model = EmotionClassifierModel(num_classes=7).to(device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    print("✅ 模型加载成功")

    dummy_input = torch.randn(1, 1, 96, 96).to(device)
    print("\n🔄 开始转换...")

    torch.onnx.export(
        model, dummy_input, onnx_path,
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )

    print(f"✅ ONNX模型已保存: {onnx_path}")

    # 验证
    print("\n🔍 验证ONNX模型...")
    try:
        import onnx
        onnx_model = onnx.load(onnx_path)
        onnx.checker.check_model(onnx_model)
        print("✅ ONNX模型验证通过")

        file_size = os.path.getsize(onnx_path) / (1024 * 1024)
        print(f"   文件大小: {file_size:.2f} MB")

        pth_size = os.path.getsize(pth_path) / (1024 * 1024)
        print(f"   PyTorch大小: {pth_size:.2f} MB")
        print(f"   压缩率: {(1 - file_size/pth_size) * 100:.1f}%")
    except ImportError:
        print("⚠️ 未安装 onnx 库，跳过验证 (pip install onnx onnxruntime)")
    except Exception as e:
        print(f"❌ ONNX验证失败: {e}")

    print("\n" + "=" * 60)
    print("✅ 转换完成！")
    print("=" * 60)


if __name__ == '__main__':
    convert_to_onnx()
