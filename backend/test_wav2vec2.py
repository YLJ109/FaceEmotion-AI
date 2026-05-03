"""测试 wav2vec2 模型是否能正常加载"""
from transformers import pipeline

print("开始测试 wav2vec2 模型加载...")

try:
    print("正在加载模型 audeering/wav2vec2-large-robust-12-ft-emotion-msp-dim ...")
    classifier = pipeline(
        "audio-classification",
        model="audeering/wav2vec2-large-robust-12-ft-emotion-msp-dim"
    )
    print("✅ 模型加载成功！")

    # 测试一下推理
    import numpy as np
    dummy_audio = np.random.randn(16000).astype(np.float32)  # 1秒音频
    print("开始测试推理...")
    result = classifier(dummy_audio, sampling_rate=16000)
    print(f"推理结果: {result}")

except Exception as e:
    print(f"❌ 模型加载失败: {e}")
    import traceback
    traceback.print_exc()
