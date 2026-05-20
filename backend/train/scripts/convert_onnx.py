import os
import torch
import torch.nn as nn
from torchvision import models

# ============ 配置 ============
TRAIN_MODEL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(TRAIN_MODEL_DIR, 'models')

INPUT_WEIGHTS = os.path.join(MODELS_DIR, 'deploy_weights.pth')
OUTPUT_ONNX = os.path.join(MODELS_DIR, 'emotion_model.onnx')

IMG_SIZE = 128
NUM_CLASSES = 7
OPSET_VERSION = 12  # 兼容性好，支持大多数推理框架

EMOTION_CLASSES = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']


# ============ 模型定义（和train.py完全一致） ============
class EmotionEfficientNet(nn.Module):
    def __init__(self, num_classes=7, dropout_rate=0.2):
        super(EmotionEfficientNet, self).__init__()
        self.backbone = models.efficientnet_b2(weights='IMAGENET1K_V1')
        num_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=dropout_rate),
            nn.Linear(num_features, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_rate * 0.5),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        return self.backbone(x)


def convert_to_onnx():
    print("=" * 60)
    print("PyTorch → ONNX 转换")
    print("=" * 60)

    # 1. 检查输入文件
    if not os.path.exists(INPUT_WEIGHTS):
        print(f"Error: 找不到 {INPUT_WEIGHTS}")
        print("请先运行 analyze_model_size.py 生成 deploy_weights.pth")
        return

    # 2. 加载模型
    print(f"\n加载模型: {INPUT_WEIGHTS}")
    model = EmotionEfficientNet(num_classes=NUM_CLASSES, dropout_rate=0.2)

    state_dict = torch.load(INPUT_WEIGHTS, map_location='cpu')
    model.load_state_dict(state_dict)
    model.eval()
    print("模型加载成功")

    # 3. 创建 dummy 输入
    dummy_input = torch.randn(1, 3, IMG_SIZE, IMG_SIZE)

    # 4. 先验证模型能正常推理
    print("\n验证模型推理...")
    with torch.no_grad():
        output = model(dummy_input)
        probs = torch.softmax(output, dim=1)
        pred_idx = output.argmax(1).item()
    print(f"  输出形状: {output.shape}")
    print(f"  预测类别: {EMOTION_CLASSES[pred_idx]}")
    print(f"  概率分布: {probs[0].detach().numpy().round(4)}")

    # 5. 导出 ONNX
    print(f"\n导出 ONNX...")
    print(f"  输入: {INPUT_WEIGHTS}")
    print(f"  输出: {OUTPUT_ONNX}")
    print(f"  Opset: {OPSET_VERSION}")
    print(f"  输入尺寸: [1, 3, {IMG_SIZE}, {IMG_SIZE}]")

    torch.onnx.export(
        model,                          # 模型
        dummy_input,                    # 模型输入
        OUTPUT_ONNX,                    # 输出文件路径
        export_params=True,             # 保存权重
        opset_version=OPSET_VERSION,    # ONNX 算子版本
        do_constant_folding=True,       # 优化常量折叠
        input_names=['input'],          # 输入节点名
        output_names=['output'],        # 输出节点名
        dynamic_axes={                  # 动态维度（支持不同batch_size）
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )
    print("  ✅ 导出成功")

    # 6. 验证 ONNX 模型
    print(f"\n验证 ONNX 模型...")
    try:
        import onnx
        onnx_model = onnx.load(OUTPUT_ONNX)
        onnx.checker.check_model(onnx_model)
        print("  ✅ ONNX 模型结构验证通过")
    except ImportError:
        print("  ⚠️ 未安装 onnx 库，跳过验证")
        print("  安装命令: pip install onnx")
    except Exception as e:
        print(f"  ⚠️ ONNX 验证失败: {e}")

    # 7. 用 ONNX Runtime 推理验证
    print(f"\n用 ONNX Runtime 推理验证...")
    try:
        import onnxruntime as ort
        import numpy as np

        sess = ort.InferenceSession(OUTPUT_ONNX)
        input_name = sess.get_inputs()[0].name
        output_name = sess.get_outputs()[0].name

        # ONNX Runtime 推理
        ort_input = {input_name: dummy_input.numpy()}
        ort_output = sess.run([output_name], ort_input)[0]

        # PyTorch 推理结果
        with torch.no_grad():
            pt_output = model(dummy_input).numpy()

        # 对比结果
        max_diff = np.max(np.abs(ort_output - pt_output))
        print(f"  PyTorch 输出: {pt_output[0].round(4)}")
        print(f"  ONNX 输出:    {ort_output[0].round(4)}")
        print(f"  最大差异:     {max_diff:.8f}")
        if max_diff < 1e-5:
            print("  ✅ PyTorch 与 ONNX 结果一致")
        else:
            print(f"  ⚠️ 差异较大 ({max_diff})，请检查模型")
    except ImportError:
        print("  ⚠️ 未安装 onnxruntime，跳过推理验证")
        print("  安装命令: pip install onnxruntime")
    except Exception as e:
        print(f"  ⚠️ ONNX Runtime 验证失败: {e}")

    # 8. 文件大小对比
    print(f"\n" + "=" * 60)
    print("文件大小对比")
    print("=" * 60)
    original_size = os.path.getsize(INPUT_WEIGHTS)
    onnx_size = os.path.getsize(OUTPUT_ONNX)

    def format_size(s):
        if s < 1024 * 1024:
            return f"{s / 1024:.1f} KB"
        return f"{s / (1024 * 1024):.1f} MB"

    print(f"  deploy_weights.pth:  {format_size(original_size)}")
    print(f"  emotion_model.onnx:  {format_size(onnx_size)}")

    # 9. 使用说明
    print(f"\n" + "=" * 60)
    print("ONNX 推理示例代码")
    print("=" * 60)
    print("""
import numpy as np
import onnxruntime as ort
from PIL import Image
from torchvision import transforms

EMOTION_CLASSES = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

# 加载 ONNX 模型
sess = ort.InferenceSession('emotion_model.onnx')
input_name = sess.get_inputs()[0].name

# 预处理
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# 预测单张图片
img = Image.open('test.jpg').convert('RGB')
img = img.resize((128, 128))
img_tensor = transform(img).unsqueeze(0).numpy()  # (1, 3, 128, 128)

# 推理
output = sess.run(None, {input_name: img_tensor})[0]
probs = np.exp(output) / np.exp(output).sum(axis=1, keepdims=True)  # softmax
pred_idx = output.argmax(axis=1)[0]
confidence = probs[0, pred_idx]

print(f"预测: {EMOTION_CLASSES[pred_idx]} ({confidence:.2%})")
for i, cls in enumerate(EMOTION_CLASSES):
    print(f"  {cls}: {probs[0, i]:.4f}")
""")

    print(f"\n✅ 转换完成！ONNX 模型保存到: {OUTPUT_ONNX}")


if __name__ == '__main__':
    convert_to_onnx()
