"""系统配置和健康检查路由"""
from fastapi import APIRouter
from config import ConfigManager
from pydantic import BaseModel, Field
from typing import Optional

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
    camera_index: Optional[int] = None
    frame_width: Optional[int] = None
    frame_height: Optional[int] = None
    face_detect_confidence: Optional[float] = Field(None, ge=0.1, le=0.99)
    detect_every_n_frames: Optional[int] = Field(None, ge=1, le=10)
    emotion_confidence_threshold: Optional[float] = None
    ema_alpha: Optional[float] = Field(None, ge=0.1, le=0.9)
    theme_mode: Optional[str] = None
    current_theme: Optional[str] = None
    show_fps: Optional[bool] = None
    show_confidence_bar: Optional[bool] = None
    # 已移除音乐配置 (音乐功能已删除)
    # ai_music_enabled: Optional[bool] = None
    # music_volume: Optional[int] = Field(None, ge=0, le=100)


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
    """更新系统配置"""
    updates = {k: v for k, v in config.dict().items() if v is not None}
    _config_manager.update_config(updates)
    return {"status": "success", "config": _config_manager.config}


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
