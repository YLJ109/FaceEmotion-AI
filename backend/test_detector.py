"""测试后端检测器"""
from models.detector import FaceDetector
import config as cfg
import sys
sys.path.insert(0, '.')

# 导入配置
config_manager = cfg.ConfigManager()

# 导入检测器

# 测试初始化
onnx_face_model_path = './models/version-RFB-320.onnx'
use_onnx_detector = config_manager.get('use_onnx_face_detector', False)

print(f"使用ONNX检测器: {use_onnx_detector}")

detector = FaceDetector(
    proto_file='./models/deploy.prototxt',
    model_file='./models/res10_300x300_ssd_iter_140000_fp16.caffemodel',
    onnx_model_path=onnx_face_model_path,
    use_onnx=use_onnx_detector
)

print(f"检测器类型: {type(detector)}")
print(f"有ONNX检测器: {detector.onnx_detector is not None}")
