#!/usr/bin/env python3
"""
性能基准测试脚本
用于评估人脸检测和情感识别的推理性能
"""

import time
import cv2
import numpy as np
import argparse
import sys
sys.path.insert(0, './backend')

from models.detector import FaceDetector
from models.emotion_classifier_onnx import EmotionClassifierONNX


def run_benchmark(image_path: str, iterations: int = 100):
    """运行性能基准测试"""
    print("🚀 启动性能基准测试...")
    
    # 加载模型
    detector = FaceDetector()
    classifier = EmotionClassifierONNX(
        model_path='./backend/weights/emotion_model.onnx',
        use_quantized=True
    )
    
    # 加载测试图像
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ 无法加载图像: {image_path}")
        return
    
    # 预热运行
    print("🔄 预热运行...")
    for _ in range(5):
        faces = detector.detect(image)
        if faces:
            for face in faces:
                x1, y1, x2, y2 = face['bbox']
                face_roi = image[y1:y2, x1:x2]
                classifier.predict(face_roi)
    
    # 正式测试
    print(f"📊 开始正式测试 ({iterations}次迭代)...")
    total_time = 0
    detect_times = []
    classify_times = []
    
    for i in range(iterations):
        # 人脸检测
        start = time.time()
        faces = detector.detect(image)
        detect_time = (time.time() - start) * 1000
        detect_times.append(detect_time)
        
        # 情感分类
        classify_time = 0
        if faces:
            start = time.time()
            for face in faces:
                x1, y1, x2, y2 = face['bbox']
                face_roi = image[y1:y2, x1:x2]
                classifier.predict(face_roi)
            classify_time = (time.time() - start) * 1000
        classify_times.append(classify_time)
        
        total_time += detect_time + classify_time
        
        if (i + 1) % 20 == 0:
            print(f"  进度: {i + 1}/{iterations}")
    
    # 计算统计数据
    avg_detect = np.mean(detect_times)
    avg_classify = np.mean(classify_times)
    avg_total = avg_detect + avg_classify
    
    min_detect = np.min(detect_times)
    min_classify = np.min(classify_times)
    min_total = min_detect + min_classify
    
    max_detect = np.max(detect_times)
    max_classify = np.max(classify_times)
    max_total = max_detect + max_classify
    
    std_detect = np.std(detect_times)
    std_classify = np.std(classify_times)
    
    # 输出结果
    print("\n" + "=" * 60)
    print("📈 性能基准测试结果")
    print("=" * 60)
    print(f"测试图像: {image_path}")
    print(f"迭代次数: {iterations}")
    print(f"检测人脸数: {len(faces) if faces else 0}")
    print("-" * 60)
    print(f"人脸检测 - 平均: {avg_detect:.2f}ms | 最小: {min_detect:.2f}ms | 最大: {max_detect:.2f}ms | 标准差: {std_detect:.2f}ms")
    print(f"情感分类 - 平均: {avg_classify:.2f}ms | 最小: {min_classify:.2f}ms | 最大: {max_classify:.2f}ms | 标准差: {std_classify:.2f}ms")
    print("-" * 60)
    print(f"总耗时   - 平均: {avg_total:.2f}ms | 最小: {min_total:.2f}ms | 最大: {max_total:.2f}ms")
    print(f"帧率     - 平均: {1000/avg_total:.2f} FPS")
    print("=" * 60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='人脸情感检测性能基准测试')
    parser.add_argument('--image', '-i', default='./test_image_video/image/happy/1.jpg', help='测试图像路径')
    parser.add_argument('--iterations', '-n', type=int, default=100, help='迭代次数')
    args = parser.parse_args()
    
    run_benchmark(args.image, args.iterations)
