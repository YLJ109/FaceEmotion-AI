"""
下载 wav2vec2 模型到本地
使用代理或镜像源下载
"""
from transformers import pipeline
import os

# 如果你有代理，取消注释并设置你的代理地址
# os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
# os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# 设置模型缓存目录
os.environ['TRANSFORMERS_CACHE'] = 'd:/front-back/FaceEmotion-AI/backend/.cache/huggingface'


print("开始下载 wav2vec2 模型...")
print("模型: audeering/wav2vec2-large-robust-12-ft-emotion-msp-dim")
print("大小: 约 1.2GB")
print()

try:
    # 下载并加载模型
    classifier = pipeline(
        "audio-classification",
        model="audeering/wav2vec2-large-robust-12-ft-emotion-msp-dim"
    )
    print("✅ 模型下载成功！")
    print(f"模型缓存位置: {os.environ['TRANSFORMERS_CACHE']}")

except Exception as e:
    print(f"❌ 下载失败: {e}")
    print()
    print("可能的原因:")
    print("1. 网络无法访问 HuggingFace")
    print("2. 需要配置代理")
    print()
    print("解决方案:")
    print("- 取消注释脚本开头的代理设置")
    print("- 或者使用 hf-mirror.com 镜像（需要修改代码）")
