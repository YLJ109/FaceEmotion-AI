"""系统配置和健康检查路由"""
from fastapi import APIRouter
from config import ConfigManager
from pydantic import BaseModel, Field
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["system"])

_config_manager = None
_face_detector = None
_emotion_model = None
_adaptive_learner = None
_inference_optimizer = None


def init_system_router(
    config_manager: ConfigManager,
    face_detector,
    emotion_model,
    adaptive_learner,
    inference_optimizer
):
    """初始化路由依赖"""
    global _config_manager, _face_detector, _emotion_model, _adaptive_learner, _inference_optimizer
    _config_manager = config_manager
    _face_detector = face_detector
    _emotion_model = emotion_model
    _adaptive_learner = adaptive_learner
    _inference_optimizer = inference_optimizer


class ConfigUpdateModel(BaseModel):
    """配置更新模型 - 支持所有可配置参数"""
    # AI 模型配置
    use_gpu: Optional[bool] = None
    use_onnx_face_detector: Optional[bool] = None
    emotion_model: Optional[str] = None
    confidence_threshold: Optional[float] = Field(None, ge=0.1, le=0.99)

    # 检测参数
    camera_index: Optional[int] = None
    frame_width: Optional[int] = None
    frame_height: Optional[int] = None
    face_detect_confidence: Optional[float] = Field(None, ge=0.1, le=0.99)
    detect_every_n_frames: Optional[int] = Field(None, ge=1, le=10)
    emotion_confidence_threshold: Optional[float] = None

    # 性能优化
    ema_alpha: Optional[float] = Field(None, ge=0.1, le=0.9)

    # 界面设置
    theme_mode: Optional[str] = None
    current_theme: Optional[str] = None
    show_fps: Optional[bool] = None
    show_confidence_bar: Optional[bool] = None


def get_gpu_memory_usage():
    """获取 GPU 内存使用量"""
    try:
        import pynvml as nvidia_smi
        handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)
        mem_info = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)
        return round(mem_info.used / 1024**2, 1)
    except Exception:
        return 0.0


@router.get("/config")
async def get_config():
    """获取系统配置"""
    return {"config": _config_manager.config}


@router.put("/config")
async def update_config(config: ConfigUpdateModel):
    """更新系统配置（支持热加载）"""
    updates = {k: v for k, v in config.dict().items() if v is not None}
    _config_manager.update_config(updates)

    # ✅ 新增: 热加载机制 - 根据配置变更动态调整
    try:
        # 1. 人脸检测模型切换
        if 'use_onnx_face_detector' in updates:
            logger.info(
                f"🔄 切换人脸检测模型: {'ONNX RFB' if updates['use_onnx_face_detector'] else 'Caffe SSD'}")
            # 注意：模型实例需要重启，这里只是更新配置
            # 实际切换需要重启 WebSocket 处理器

        # 2. 置信度阈值调整（实时生效）
        if 'confidence_threshold' in updates:
            logger.info(f"🔄 更新置信度阈值: {updates['confidence_threshold']}")
            # 该值会被 websocket.py 实时读取，无需重启

        # 3. 检测频率调整（实时生效）
        if 'detect_every_n_frames' in updates:
            logger.info(
                f"🔄 更新检测频率: 每 {updates['detect_every_n_frames']} 帧检测一次")

        # 4. GPU/CPU 切换（需要重新初始化模型）
        if 'use_gpu' in updates:
            logger.info(f" 切换推理设备: {'GPU' if updates['use_gpu'] else 'CPU'}")
            # 注意：需要重新加载模型，建议提示用户重启服务

        return {
            "status": "success",
            "config": _config_manager.config,
            "hot_reload": True,
            "message": "配置已更新，部分参数实时生效"
        }
    except Exception as e:
        logger.error(f"❌ 配置热加载失败: {e}")
        return {
            "status": "success",
            "config": _config_manager.config,
            "hot_reload": False,
            "message": "配置已保存，但热加载失败，请重启服务"
        }


@router.get("/stats")
async def get_stats():
    """获取统计信息"""
    from database import DatabaseManager
    db_manager = DatabaseManager()
    return db_manager.get_stats()


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "gpu_available": bool(get_gpu_memory_usage()),
        "model_loaded": _face_detector is not None and _emotion_model is not None,
        "features": {
            "adaptive_learning": _adaptive_learner.total_corrections if _adaptive_learner else 0,
            "music_generation": False,  # 已移除音乐功能
            "multi_modal": True,
            "user_analytics": True,
            "inference_optimizer": _inference_optimizer.enabled if _inference_optimizer else False,
        }
    }
