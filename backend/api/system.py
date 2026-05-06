"""系统配置和健康检查路由"""
from fastapi import APIRouter
from core.config import ConfigManager
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
    # ✅ 新增: 性能模式
    performance_mode: Optional[str] = None

    # AI 模型配置（✅ 修复: 移除已废弃的模型切换参数）
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

    # AI 音乐配置
    music_volume: Optional[int] = Field(None, ge=0, le=100)
    emotion_sensitivity: Optional[int] = Field(None, ge=0, le=100)
    rhythm_smoothness: Optional[int] = Field(None, ge=0, le=100)
    timbre_style: Optional[str] = None


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

    # ✅ 修复: 热加载机制 - 仅支持有效的配置项
    try:
        # 1. 置信度阈值调整（实时生效）
        if 'confidence_threshold' in updates:
            logger.debug(f"更新置信度阈值: {updates['confidence_threshold']}")
            # 该值会被 websocket.py 实时读取，无需重启

        # 2. 检测频率调整（实时生效）
        if 'detect_every_n_frames' in updates:
            logger.debug(
                f"更新检测频率: 每 {updates['detect_every_n_frames']} 帧检测一次")

        # 3. 性能模式切换（需要前端重新加载配置）
        if 'performance_mode' in updates:
            perf_config = _config_manager.get_performance_config()
            logger.info(f"🚀 性能模式已切换: {updates['performance_mode'].upper()}")
            logger.debug(
                f"   分辨率: {perf_config['send_width']}x{perf_config['send_height']}")
            logger.debug(f"   跳帧阈值: {perf_config['frame_skip_threshold']}")
            logger.debug(f"   EMA Alpha: {perf_config['ema_alpha']}")

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


@router.get("/performance/recommend")
async def recommend_performance_mode():
    """根据硬件配置智能推荐性能模式"""
    try:
        gpu_info = None
        gpu_memory_gb = 0
        cpu_cores = 0
        recommended_mode = 'high'  # 默认推荐

        # 1. 检测 GPU
        try:
            import pynvml as nvidia_smi
            nvidia_smi.nvmlInit()
            device_count = nvidia_smi.nvmlDeviceGetCount()
            if device_count > 0:
                handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)
                gpu_name = nvidia_smi.nvmlDeviceGetName(handle)
                mem_info = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)
                gpu_memory_gb = mem_info.total / 1024**3
                gpu_info = f"{gpu_name} ({gpu_memory_gb:.1f}GB)"
                logger.info(f"🔍 检测到 GPU: {gpu_info}")
        except Exception as e:
            logger.info(f"⚠️ 未检测到 GPU: {e}")

        # 2. 检测 CPU
        import multiprocessing
        cpu_cores = multiprocessing.cpu_count()
        try:
            import platform
            cpu_info = platform.processor()
        except:
            cpu_info = "未知"

        # 3. 智能推荐逻辑
        if gpu_info and gpu_memory_gb >= 4:
            # GPU 显存 >= 4GB，推荐 Ultra 或 High
            if gpu_memory_gb >= 8:
                recommended_mode = 'ultra'
            else:
                recommended_mode = 'high'
        elif gpu_info and gpu_memory_gb >= 2:
            # GPU 显存 >= 2GB，推荐 High
            recommended_mode = 'high'
        elif cpu_cores >= 4:
            # CPU 4核心以上，推荐 Medium
            recommended_mode = 'medium'
        else:
            # 低配设备，推荐 Low
            recommended_mode = 'low'

        result = {
            "gpu": gpu_info,
            "cpu": cpu_info,
            "gpu_memory_gb": round(gpu_memory_gb, 1),
            "cpu_cores": cpu_cores,
            "recommended_mode": recommended_mode,
            "recommendation_reason": _get_recommendation_reason(recommended_mode, gpu_info, gpu_memory_gb, cpu_cores)
        }

        # ✅ 优化: 仅在 DEBUG 模式下打印详细日志
        logger.debug(f"性能模式推荐: {result}")
        return result

    except Exception as e:
        logger.error(f"❌ 性能推荐失败: {e}")
        return {
            "gpu": None,
            "cpu": "未知",
            "gpu_memory_gb": 0,
            "cpu_cores": 0,
            "recommended_mode": "high",
            "recommendation_reason": "检测失败，使用默认推荐"
        }


def _get_recommendation_reason(mode, gpu_info, gpu_memory_gb, cpu_cores):
    """获取推荐理由"""
    reasons = {
        'ultra': f'检测到高端 GPU ({gpu_info})，显存充足，推荐使用 Ultra 模式以获得最佳性能',
        'high': f'检测到中端 GPU ({gpu_info})，推荐使用 High 模式平衡性能和画质',
        'medium': f'未检测到 GPU 或显存不足，但 CPU 性能良好 ({cpu_cores} 核心)，推荐使用 Medium 模式',
        'low': f'硬件配置较低 (CPU {cpu_cores} 核心)，推荐使用 Low 模式确保流畅运行'
    }
    return reasons.get(mode, '使用默认 High 模式')
