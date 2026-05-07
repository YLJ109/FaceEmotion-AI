"""人脸检测功能测试脚本"""
import cv2
import numpy as np
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.detector import FaceDetector
from models.emotion_classifier_onnx import EmotionClassifierONNX

def test_face_detector():
    """测试人脸检测器"""
    print("=" * 60)
    print("🔍 测试人脸检测器")
    print("=" * 60)
    
    try:
        proto_file = os.path.join(os.path.dirname(__file__), 'configs', 'deploy.prototxt')
        model_file = os.path.join(os.path.dirname(__file__), 'weights', 'res10_300x300_ssd_iter_140000_fp16.caffemodel')
        
        print(f"📁 模型路径: {model_file}")
        print(f"📁 Prototxt路径: {proto_file}")
        
        if not os.path.exists(model_file):
            print("❌ 人脸检测模型文件不存在")
            return False
        
        if not os.path.exists(proto_file):
            print("❌ Prototxt文件不存在")
            return False
        
        # 加载检测器
        detector = FaceDetector(proto_file, model_file)
        print("✅ 人脸检测器加载成功")
        
        # 创建测试图像（模拟人脸）
        test_img = np.zeros((480, 640, 3), dtype=np.uint8)
        # 绘制一个简单的人脸轮廓
        cv2.circle(test_img, (320, 240), 80, (255, 255, 255), -1)  # 脸
        cv2.circle(test_img, (290, 220), 10, (0, 0, 0), -1)  # 左眼
        cv2.circle(test_img, (350, 220), 10, (0, 0, 0), -1)  # 右眼
        cv2.ellipse(test_img, (320, 260), (20, 15), 0, 0, 360, (0, 0, 0), 2)  # 嘴巴
        
        # 测试检测
        print("\n🧪 测试人脸检测...")
        for threshold in [0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6]:
            faces = detector.detect(test_img, confidence_threshold=threshold)
            print(f"   阈值={threshold:.2f}: 检测到 {len(faces)} 个人脸")
        
        return True
        
    except Exception as e:
        print(f"❌ 人脸检测器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_emotion_model():
    """测试情绪识别模型"""
    print("\n" + "=" * 60)
    print("🔍 测试情绪识别模型")
    print("=" * 60)
    
    try:
        model_path = os.path.join(os.path.dirname(__file__), 'weights', 'emotion_model.onnx')
        
        print(f"📁 模型路径: {model_path}")
        
        if not os.path.exists(model_path):
            print("❌ 情绪识别模型文件不存在")
            return False
        
        # 加载模型
        emotion_model = EmotionClassifierONNX(model_path)
        print("✅ 情绪识别模型加载成功")
        
        # 创建测试人脸图像
        test_face = np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8)
        
        # 测试推理
        emotion, confidence, scores = emotion_model.predict(test_face)
        print(f"✅ 推理成功: 情绪={emotion}, 置信度={confidence:.4f}")
        print(f"📊 所有情绪分数: {scores}")
        
        return True
        
    except Exception as e:
        print(f"❌ 情绪识别模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_camera_access():
    """测试摄像头访问"""
    print("\n" + "=" * 60)
    print("🔍 测试摄像头访问")
    print("=" * 60)
    
    try:
        # 尝试打开摄像头
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ 无法打开摄像头 (索引0)")
            
            # 尝试其他索引
            for i in range(1, 5):
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    print(f"✅ 成功打开摄像头 (索引{i})")
                    break
            else:
                print("❌ 未检测到可用摄像头")
                return False
        else:
            print("✅ 成功打开摄像头 (索引0)")
        
        # 读取一帧
        ret, frame = cap.read()
        if ret:
            print(f"✅ 成功读取帧: {frame.shape}")
        else:
            print("❌ 无法读取帧")
            
        cap.release()
        return True
        
    except Exception as e:
        print(f"❌ 摄像头测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_websocket_server():
    """测试WebSocket服务器配置"""
    print("\n" + "=" * 60)
    print("🔍 测试WebSocket服务器配置")
    print("=" * 60)
    
    try:
        # 检查配置文件
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        if os.path.exists(config_path):
            import json
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            print("📋 当前配置:")
            print(f"   - 主机: {config.get('host', '未设置')}")
            print(f"   - 端口: {config.get('port', '未设置')}")
            print(f"   - 置信度阈值: {config.get('confidence_threshold', '未设置')}")
            print(f"   - 调试模式: {config.get('debug', False)}")
            
            # 验证阈值范围
            threshold = config.get('confidence_threshold', 0.5)
            if threshold < 0.1 or threshold > 0.9:
                print(f"⚠️ 警告: 置信度阈值 {threshold} 超出推荐范围 [0.1, 0.9]")
            else:
                print(f"✅ 置信度阈值 {threshold} 在正常范围内")
                
            return True
        else:
            print("❌ 配置文件不存在")
            return False
            
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 人脸检测系统全面诊断")
    print("=" * 60)
    
    results = []
    
    results.append(("人脸检测器", test_face_detector()))
    results.append(("情绪识别模型", test_emotion_model()))
    results.append(("摄像头访问", test_camera_access()))
    results.append(("WebSocket配置", test_websocket_server()))
    
    print("\n" + "=" * 60)
    print("📊 诊断结果汇总")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"   {name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查相关组件")
