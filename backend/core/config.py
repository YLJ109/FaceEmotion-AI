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

    # ✅ 新增: 获取性能模式配置
    def get_performance_config(self) -> Dict[str, Any]:
        """根据当前性能模式返回对应的配置参数"""
        mode = self.config.get('performance_mode', 'high')

        # 四级性能模式配置表 - 差异更明显
        PERFORMANCE_PROFILES = {
            'ultra': {
                'use_gpu': True,
                'send_width': 256,
                'send_height': 192,
                'frame_skip_threshold': 1,  # 不跳帧，每帧都检测
                'ema_alpha': 0.3,  # 快速响应，低延迟
                'inference_threads': 4,
                'enable_multimodal': True,
                'enable_adaptive_learning': True,
                'enable_realtime_charts': True,
                'quality_preset': 'high',
                'description': '极致画质，零延迟'
            },
            'high': {
                'use_gpu': True,
                'send_width': 192,
                'send_height': 144,
                'frame_skip_threshold': 2,  # 每2帧检测一次
                'ema_alpha': 0.2,  # 平衡响应与平滑
                'inference_threads': 3,
                'enable_multimodal': True,
                'enable_adaptive_learning': True,
                'enable_realtime_charts': True,
                'quality_preset': 'medium',
                'description': '高性能，流畅体验'
            },
            'medium': {
                'use_gpu': False,  # 强制CPU模式
                'send_width': 128,
                'send_height': 96,
                'frame_skip_threshold': 4,  # 每4帧检测一次
                'ema_alpha': 0.15,  # 更平滑，响应稍慢
                'inference_threads': 2,
                'enable_multimodal': False,  # 禁用多模态处理
                'enable_adaptive_learning': False,  # 禁用自适应学习
                'enable_realtime_charts': True,
                'quality_preset': 'low',
                'description': '平衡性能，稳定运行'
            },
            'low': {
                'use_gpu': False,  # 强制CPU模式
                'send_width': 80,
                'send_height': 60,
                'frame_skip_threshold': 8,  # 每8帧检测一次
                'ema_alpha': 0.1,  # 极致平滑，响应较慢
                'inference_threads': 1,
                'enable_multimodal': False,
                'enable_adaptive_learning': False,
                'enable_realtime_charts': False,  # 禁用实时图表
                'quality_preset': 'basic',
                'description': '节能模式，最低资源占用'
            }
        }

        # 返回对应模式的配置，如果模式不存在则使用 high 作为默认值
        profile = PERFORMANCE_PROFILES.get(mode, PERFORMANCE_PROFILES['high'])
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
            'model_path': os.getenv('MODEL_PATH', 'weights/pytorch_final_3060.pth'),
            'face_detector_model': os.getenv('FACE_DETECTOR_MODEL', 'weights/res10_300x300_ssd_iter_140000_fp16.caffemodel'),
            # ✅ 修改: 禁用ONNX RFB，使用 Caffe SSD 模型
            'use_onnx_face_detector': os.getenv('USE_ONNX_FACE_DETECTOR', 'false').lower() == 'false',
            'emotion_model': os.getenv('EMOTION_MODEL', 'weights/emotion_model.onnx'),
            #  修改: 降低置信度阈值到 0.45，提高 Caffe SSD 检出率
            'confidence_threshold': float(os.getenv('CONFIDENCE_THRESHOLD', '0.45')),

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

            # UI配置
            'camera_index': 2,
            'frame_width': 640,
            'frame_height': 480,
            'face_detect_confidence': 0.5,
            'detect_every_n_frames': 2,
            'emotion_confidence_threshold': 0.3,
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
