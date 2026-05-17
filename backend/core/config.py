"""配置管理器 - 支持热更新、持久化和环境变量"""
import json
import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# frame_skip_threshold: 每隔N帧检测1次（1=每帧检测，2=每2帧检测1次，以此类推）
# ema_alpha: 情绪概率平滑系数，值越小越平滑（0.1-0.3之间推荐）
# inference_threads: ONNX Runtime线程数，建议≤4

PERFORMANCE_PROFILES = {
    'gpu': {
        'use_gpu': True,
        'send_width': 320,           # 帧发送给模型的宽度
        'send_height': 240,          # 帧发送给模型的高度
        'frame_skip_threshold': 2,    # GPU性能好，每2帧检测1次
        'ema_alpha': 0.25,           # 情绪平滑系数，GPU延迟低可稍大
        'inference_threads': 4,      # 4线程推理
        'enable_multimodal': True,
        'enable_adaptive_learning': True,
        'enable_realtime_charts': True,
        'quality_preset': 'high',
        'description': 'GPU加速，最佳性能'
    },
    'cpu_high': {
        'use_gpu': False,
        'send_width': 256,           # 帧宽度，降低分辨率提升性能
        'send_height': 192,          # 帧高度
        'frame_skip_threshold': 3,    # CPU性能中等，每3帧检测1次
        'ema_alpha': 0.2,           # 情绪平滑系数
        'inference_threads': 3,      # 3线程推理
        'enable_multimodal': True,
        'enable_adaptive_learning': True,
        'enable_realtime_charts': True,
        'quality_preset': 'medium',
        'description': 'CPU高性能，流畅体验'
    },
    'cpu_low': {
        'use_gpu': False,
        'send_width': 128,           # 帧宽度，大幅降低提升性能
        'send_height': 96,           # 帧高度
        'frame_skip_threshold': 5,    # CPU性能弱，每5帧检测1次
        'ema_alpha': 0.15,           # 情绪平滑系数，较低值减少抖动
        'inference_threads': 1,      # 单线程推理，节能稳定
        'enable_multimodal': False,
        'enable_adaptive_learning': False,
        'enable_realtime_charts': True,
        'quality_preset': 'low',
        'description': 'CPU低性能，稳定运行'
    }
}


class ConfigManager:
    """配置管理器 - 支持热更新和JSON持久化"""

    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return self.get_default_config()
        except Exception as e:
            logger.warning(f"加载配置失败: {e}，使用默认配置")
            return self.get_default_config()

    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存配置失败: {e}")

    def update_config(self, updates: Dict[str, Any]):
        self.config.update(updates)
        self.save_config()
        return {"status": "success", "config": self.config}

    def get(self, key: str, default=None):
        return self.config.get(key, default)

    def get_performance_config(self) -> Dict[str, Any]:
        mode = self.config.get('performance_mode', 'cpu_high')
        return PERFORMANCE_PROFILES.get(mode, PERFORMANCE_PROFILES['cpu_high'])

    def get_default_config(self) -> Dict[str, Any]:
        return {
            'host': os.getenv('HOST', '0.0.0.0'),
            'port': int(os.getenv('PORT', '8000')),
            'debug': os.getenv('DEBUG', 'false').lower() == 'true',
            'log_level': os.getenv('LOG_LEVEL', 'info'),

            'database_url': os.getenv('DATABASE_URL', 'sqlite:///./data/emotion.db'),
            'db_pool_size': int(os.getenv('DB_POOL_SIZE', '5')),
            'db_max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '10')),

            'performance_mode': os.getenv('PERFORMANCE_MODE', 'high'),

            'use_gpu': os.getenv('USE_GPU', 'true').lower() == 'true',
            'model_path': os.getenv('MODEL_PATH', 'weights/final_model.onnx'),
            'face_detector_model': os.getenv('FACE_DETECTOR_MODEL', 'weights/res10_300x300_ssd_iter_140000_fp16.caffemodel'),
            'face_detector_proto': os.getenv('FACE_DETECTOR_PROTO', 'configs/deploy.prototxt'),
            'emotion_model': os.getenv('EMOTION_MODEL', 'weights/final_model.onnx'),
            'confidence_threshold': float(os.getenv('CONFIDENCE_THRESHOLD', '0.5')),
            'face_detect_confidence': float(os.getenv('FACE_DETECT_CONFIDENCE', '0.3')),

            'ws_max_connections': int(os.getenv('WS_MAX_CONNECTIONS', '10')),
            'ws_heartbeat_interval': int(os.getenv('WS_HEARTBEAT_INTERVAL', '30')),

            'max_workers': int(os.getenv('MAX_WORKERS', '4')),
            'send_width': int(os.getenv('SEND_WIDTH', '160')),
            'send_height': int(os.getenv('SEND_HEIGHT', '120')),
            'frame_skip_threshold': int(os.getenv('FRAME_SKIP_THRESHOLD', '2')),
            'ema_alpha': float(os.getenv('EMA_ALPHA', '0.15')),

            'cors_origins': os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(','),
            'rate_limit_per_minute': int(os.getenv('RATE_LIMIT_PER_MINUTE', '60')),

            'audio_sample_rate': int(os.getenv('AUDIO_SAMPLE_RATE', '16000')),
            'audio_channels': int(os.getenv('AUDIO_CHANNELS', '1')),
            'voice_fusion_weight': float(os.getenv('VOICE_FUSION_WEIGHT', '0.3')),

            'camera_index': 2,
            'frame_width': 640,
            'frame_height': 480,
            'detect_every_n_frames': 2,
            'emotion_confidence_threshold': float(os.getenv('EMOTION_CONFIDENCE_THRESHOLD', '0.1')),
            'max_faces': 10,
            'enable_adaptive_calibration': False,

            'theme_mode': 'auto',
            'current_theme': 'zen',
            'show_fps': True,
            'show_confidence_bar': True,
            'use_fp16': True,
            'use_onnx': False,

            'music_volume': 70,
            'emotion_sensitivity': 50,
            'rhythm_smoothness': 50,
            'timbre_style': 'sine'
        }
