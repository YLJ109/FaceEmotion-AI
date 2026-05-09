"""配置管理器 - 支持热更新、持久化和环境变量"""
import json
import os
import logging
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# ✅ 新增: 加载 .env 文件
load_dotenv()

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器 - 支持热更新和JSON持久化"""

    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info("✅ 配置加载成功")
                    return config
            else:
                logger.info("ℹ️ 使用默认配置")
                return self.get_default_config()
        except Exception as e:
            logger.warning(f"⚠️ 加载配置失败: {e}，使用默认配置")
            return self.get_default_config()

    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.debug("配置已保存")
        except Exception as e:
            logger.error(f"❌ 保存配置失败: {e}")

    def update_config(self, updates: Dict[str, Any]):
        self.config.update(updates)
        self.save_config()
        return {"status": "success", "config": self.config}

    def get(self, key: str, default=None):
        return self.config.get(key, default)

    # ✅ 新增: 获取性能模式配置（三级模式）
    def get_performance_config(self) -> Dict[str, Any]:
        """根据当前性能模式返回对应的配置参数"""
        mode = self.config.get('performance_mode', 'cpu_high')

        # ✅ 三级性能模式配置表
        PERFORMANCE_PROFILES = {
            'gpu': {
                'use_gpu': True,
                'send_width': 320,
                'send_height': 240,
                'frame_skip_threshold': 2,  # 每2帧检测一次
                'ema_alpha': 0.25,  # 快速响应
                'inference_threads': 4,
                'enable_multimodal': True,
                'enable_adaptive_learning': True,
                'enable_realtime_charts': True,
                'quality_preset': 'high',
                'description': 'GPU加速，最佳性能'
            },
            'cpu_high': {
                'use_gpu': False,  # 强制CPU模式
                'send_width': 256,
                'send_height': 192,
                'frame_skip_threshold': 3,  # 每3帧检测一次
                'ema_alpha': 0.2,  # 平衡响应与平滑
                'inference_threads': 3,
                'enable_multimodal': True,
                'enable_adaptive_learning': True,
                'enable_realtime_charts': True,
                'quality_preset': 'medium',
                'description': 'CPU高性能，流畅体验'
            },
            'cpu_low': {
                'use_gpu': False,  # 强制CPU模式
                'send_width': 128,
                'send_height': 96,
                'frame_skip_threshold': 5,  # 每5帧检测一次
                'ema_alpha': 0.15,  # 更平滑，响应稍慢
                'inference_threads': 1,
                'enable_multimodal': False,
                'enable_adaptive_learning': False,
                'enable_realtime_charts': True,
                'quality_preset': 'low',
                'description': 'CPU低性能，稳定运行'
            }
        }

        # 返回对应模式的配置，如果模式不存在则使用 cpu_high 作为默认值
        profile = PERFORMANCE_PROFILES.get(mode, PERFORMANCE_PROFILES['cpu_high'])
        logger.debug(
            f"性能模式: {mode.upper()} - GPU: {profile['use_gpu']}, 分辨率: {profile['send_width']}x{profile['send_height']}")
        return profile

    def get_default_config(self) -> Dict[str, Any]:
        """✅ 新增: 从环境变量获取默认配置"""
        return {
            # 服务器配置
            'host': os.getenv('HOST', '0.0.0.0'),
            'port': int(os.getenv('PORT', '8000')),
            'debug': os.getenv('DEBUG', 'false').lower() == 'true',
            'log_level': os.getenv('LOG_LEVEL', 'info'),

            # 数据库配置
            'database_url': os.getenv('DATABASE_URL', 'sqlite:///./data/emotion.db'),
            'db_pool_size': int(os.getenv('DB_POOL_SIZE', '5')),
            'db_max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '10')),

            # ✅ 新增: 性能模式配置
            # ultra/high/medium/low
            'performance_mode': os.getenv('PERFORMANCE_MODE', 'high'),

            # AI模型配置
            'use_gpu': os.getenv('USE_GPU', 'true').lower() == 'true',
            'model_path': os.getenv('MODEL_PATH', 'weights/final_model.onnx'),
            'face_detector_model': os.getenv('FACE_DETECTOR_MODEL', 'weights/res10_300x300_ssd_iter_140000_fp16.caffemodel'),
            'face_detector_proto': os.getenv('FACE_DETECTOR_PROTO', 'configs/deploy.prototxt'),
            # 使用 Caffe SSD 人脸检测模型
            'use_onnx_face_detector': os.getenv('USE_ONNX_FACE_DETECTOR', 'false').lower() == 'false',
            'emotion_model': os.getenv('EMOTION_MODEL', 'weights/final_model.onnx'),
            # 置信度阈值
            'confidence_threshold': float(os.getenv('CONFIDENCE_THRESHOLD', '0.5')),
            'face_detect_confidence': float(os.getenv('FACE_DETECT_CONFIDENCE', '0.5')),

            # WebSocket配置
            'ws_max_connections': int(os.getenv('WS_MAX_CONNECTIONS', '10')),
            'ws_heartbeat_interval': int(os.getenv('WS_HEARTBEAT_INTERVAL', '30')),
            'ws_message_timeout': int(os.getenv('WS_MESSAGE_TIMEOUT', '10')),

            # 性能优化配置
            'max_workers': int(os.getenv('MAX_WORKERS', '4')),
            'send_width': int(os.getenv('SEND_WIDTH', '160')),
            'send_height': int(os.getenv('SEND_HEIGHT', '120')),
            'frame_skip_threshold': int(os.getenv('FRAME_SKIP_THRESHOLD', '2')),
            'ema_alpha': float(os.getenv('EMA_ALPHA', '0.15')),

            # 安全配置
            'cors_origins': os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:80').split(','),
            'rate_limit_per_minute': int(os.getenv('RATE_LIMIT_PER_MINUTE', '60')),
            'feedback_cache_ttl': int(os.getenv('FEEDBACK_CACHE_TTL', '5')),

            # 多模态配置
            'audio_sample_rate': int(os.getenv('AUDIO_SAMPLE_RATE', '16000')),
            'audio_channels': int(os.getenv('AUDIO_CHANNELS', '1')),
            'voice_fusion_weight': float(os.getenv('VOICE_FUSION_WEIGHT', '0.3')),

            # 检测配置
            'camera_index': 2,
            'frame_width': 640,
            'frame_height': 480,
            # 人脸检测置信度阈值（Caffe SSD 使用，值越低检出率越高）
            'face_detect_confidence': float(os.getenv('FACE_DETECT_CONFIDENCE', '0.3')),
            'detect_every_n_frames': 2,
            # 情绪识别置信度阈值（前端过滤使用）
            'emotion_confidence_threshold': float(os.getenv('EMOTION_CONFIDENCE_THRESHOLD', '0.1')),
            'max_faces': 10,  # ✅ 新增: 最大检测人脸数量
            'enable_adaptive_calibration': False,  # ✅ 新增: 自适应校准开关（默认禁用）
            
            # UI配置
            'theme_mode': 'auto',
            'current_theme': 'zen',
            'show_fps': True,
            'show_confidence_bar': True,
            'use_fp16': True,
            'use_onnx': False,

            # AI 音乐配置
            'music_volume': 70,
            'emotion_sensitivity': 50,
            'rhythm_smoothness': 50,
            'timbre_style': 'sine'
        }
