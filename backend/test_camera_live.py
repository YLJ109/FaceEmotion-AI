"""实时摄像头人脸检测测试"""
import cv2
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.detector import FaceDetector

def test_live_camera():
    """测试实时摄像头人脸检测"""
    print("=" * 60)
    print("🔍 实时摄像头人脸检测测试")
    print("=" * 60)
    
    try:
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
        
        print("✅ 摄像头已打开")
        print("📊 开始实时检测... (按 'q' 退出)")
        
        frame_count = 0
        detected_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ 无法读取帧")
                break
            
            frame_count += 1
            
            # 每5帧检测一次
            if frame_count % 5 == 0:
                # 测试不同阈值
                faces = detector.detect(frame, confidence_threshold=0.25)
                detected_count += len(faces)
                
                print(f"\r帧: {frame_count} | 检测到人脸: {len(faces)} | 累计检测: {detected_count}", end='')
                
                # 绘制人脸框
                for face in faces:
                    x, y, w, h = face['bbox']
                    conf = face['confidence']
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, f'{conf:.2f}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # 显示画面
            cv2.imshow('Face Detection Test', frame)
            
            # 按q退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        print(f"\n✅ 测试完成！共处理 {frame_count} 帧，检测到 {detected_count} 个人脸")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_live_camera()