"""使用真实摄像头图像测试人脸检测"""
import cv2
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.detector import FaceDetector

def test_with_real_camera():
    """使用真实摄像头图像测试人脸检测"""
    print("=" * 60)
    print("🔍 使用真实摄像头图像测试人脸检测")
    print("=" * 60)
    
    # 加载检测器
    proto_file = os.path.join(os.path.dirname(__file__), 'configs', 'deploy.prototxt')
    model_file = os.path.join(os.path.dirname(__file__), 'weights', 'res10_300x300_ssd_iter_140000_fp16.caffemodel')
    
    detector = FaceDetector(proto_file, model_file)
    print("✅ 人脸检测器加载成功")
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ 无法打开摄像头")
        return
    
    print("📷 正在捕获图像... (按 'q' 退出)")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ 无法读取帧")
            break
            
        # 测试不同阈值
        thresholds = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]
        results = []
        
        for thresh in thresholds:
            faces = detector.detect(frame, confidence_threshold=thresh)
            results.append((thresh, len(faces)))
        
        # 显示结果
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 60)
        print("🎯 人脸检测结果")
        print("=" * 60)
        
        max_faces = 0
        best_thresh = 0
        for thresh, count in results:
            status = "✅" if count > 0 else "❌"
            print(f"   {status} 阈值={thresh:.2f}: 检测到 {count} 个人脸")
            if count > max_faces:
                max_faces = count
                best_thresh = thresh
        
        # 在图像上绘制检测结果
        if max_faces > 0:
            faces = detector.detect(frame, confidence_threshold=best_thresh)
            for face in faces:
                x, y, w, h = face['bbox']
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"{face['confidence']:.2f}", (x, y - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # 显示图像
        cv2.imshow('Face Detection Test', frame)
        
        # 按 q 退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

def test_image_file(image_path):
    """测试图像文件"""
    print(f"\n📁 测试图像文件: {image_path}")
    
    if not os.path.exists(image_path):
        print("❌ 图像文件不存在")
        return
    
    frame = cv2.imread(image_path)
    if frame is None:
        print("❌ 无法读取图像")
        return
    
    proto_file = os.path.join(os.path.dirname(__file__), 'configs', 'deploy.prototxt')
    model_file = os.path.join(os.path.dirname(__file__), 'weights', 'res10_300x300_ssd_iter_140000_fp16.caffemodel')
    
    detector = FaceDetector(proto_file, model_file)
    
    thresholds = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]
    for thresh in thresholds:
        faces = detector.detect(frame, confidence_threshold=thresh)
        print(f"   阈值={thresh:.2f}: 检测到 {len(faces)} 个人脸")

if __name__ == "__main__":
    # 测试摄像头
    test_with_real_camera()
    
    # 测试示例图像（如果存在）
    test_image_file("test_face.jpg")
