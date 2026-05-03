"""重新测试 wav2vac2 模型"""
import os
from transformers import pipeline
import numpy as np

# 设置模型路径
model_path = "d:/front-back/FaceEmotion-AI/wav2vac2"

print(f"重新测试模型: {model_path}")
print()

try:
    # 加载本地模型
    print("正在加载模型...")
    classifier = pipeline(
        "audio-classification",
        model=model_path,
        local_files_only=True,
        trust_remote_code=True  # 添加这个参数
    )
    print("✅ 模型加载成功！")
    print()

    # 查看模型配置
    print("📋 模型情绪标签:")
    print(classifier.model.config.id2label)
    print()

    # 测试推理
    print("测试推理（1秒随机音频）...")
    dummy_audio = np.random.randn(16000).astype(np.float32)
    result = classifier(dummy_audio, sampling_rate=16000)

    print(f"\n 推理结果:")
    print(f"结果数量: {len(result)}")
    for item in result:
        print(f"  - {item['label']}: {item['score']:.4f}")

except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
