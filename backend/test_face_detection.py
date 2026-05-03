"""测试人脸检测功能"""
import time
from models.detector import FaceDetector
import numpy as np
import cv2
import sys
import os
sys.path.insert(0, '.')


# 初始化检测器
print("初始化检测器...")
detector = FaceDetector(
    proto_file='./models/deploy.prototxt',
    model_file='./models/res10_300x300_ssd_iter_140000_fp16.caffemodel',
    onnx_model_path='./models/version-RFB-320.onnx',
    use_onnx=True
)

# 创建测试图像（模拟摄像头画面）
print("创建测试图像...")
test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

# 测试检测
print("开始检测...")
start_time = time.time()
faces = detector.detect(test_frame, confidence_threshold=0.5, max_faces=10)
end_time = time.time()

print(f"检测耗时: {(end_time - start_time)*1000:.2f} ms")
print(f"检测到人脸数: {len(faces)}")

if faces:
    for i, face in enumerate(faces[:3]):  # 只显示前3个
        print(
            f"  人脸{i+1}: bbox={face['bbox']}, confidence={face['confidence']:.3f}")

print("\n检测器工作正常!")
