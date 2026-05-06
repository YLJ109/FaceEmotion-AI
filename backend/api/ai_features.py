"""AI 功能相关 API 路由"""
from core.database import DatabaseManager
from optimizer.dynamic_inference import DynamicInferenceOptimizer
from analytics.user_analytics import UserAnalytics
from adaptation.active_learner import AdaptiveLearner
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, validator
from typing import Dict, Optional
import base64
import time
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

# 已移除音乐生成模块
# from music.music_generator import generate_music_params, generate_note_sequence, EMOTION_SCALES, EMOTION_BPM, EMOTION_ROOT

router = APIRouter(prefix="/api", tags=["ai-features"])

_adaptive_learner = None
_user_analytics = None
_inference_optimizer = None
_db_manager = None

# ✅ 新增: 内存缓存(防重复提交)
_feedback_cache = {}  # key: "predicted:correct", value: timestamp
_FEEDBACK_CACHE_TTL = 5  # 5秒

# ✅ 新增: 限流器
_rate_limits = defaultdict(list)  # key: client_ip, value: [timestamps]
_RATE_LIMIT_WINDOW = 60  # 60秒
_RATE_LIMIT_MAX = 10  # 最多10次


def init_ai_router(
    adaptive_learner: AdaptiveLearner,
    user_analytics: UserAnalytics,
    inference_optimizer: DynamicInferenceOptimizer,
    db_manager: DatabaseManager
):
    """初始化路由依赖"""
    global _adaptive_learner, _user_analytics, _inference_optimizer, _db_manager
    _adaptive_learner = adaptive_learner
    _user_analytics = user_analytics
    _inference_optimizer = inference_optimizer
    _db_manager = db_manager


# === Pydantic 模型 ===

# 已移除 MusicParamsRequest (音乐功能已删除)
# class MusicParamsRequest(BaseModel):
#     scores: Dict[str, float]


class FeedbackModel(BaseModel):
    emotion: Optional[str] = None
    predicted_emotion: Optional[str] = None
    correct_emotion: Optional[str] = None
    feedback_type: str = Field(..., pattern=r'^(correct|incorrect)$')
    notes: Optional[str] = Field(None, max_length=500)
    # ✅ 新增: 静态快照相关字段
    confidence: Optional[float] = None
    bbox: Optional[list] = None
    snapshot: Optional[str] = None  # Base64 图片数据
    timestamp: Optional[int] = None

    @validator('correct_emotion', 'predicted_emotion', pre=True, always=True)
    def validate_emotion(cls, v):
        """✅ 新增: 验证情绪值是否合法（支持多种别名）"""
        if v is None:
            return v

        # ✅ 修复: 支持前后端所有情绪名称变体
        valid_emotions = [
            'happy', 'enjoy',           # 开心
            'sad',                       # 悲伤
            'angry',                     # 愤怒
            'surprise', 'surprised',     # 惊讶
            'fear', 'fearful',           # 恐惧
            'disgust', 'disgusted',      # 厌恶
            'neutral', 'calm'            # 平静
        ]

        if v not in valid_emotions:
            raise ValueError(
                f'Invalid emotion: {v}. Must be one of {valid_emotions}')
        return v


class FeatureLogModel(BaseModel):
    feature: str
    session_id: str = ''
    duration_ms: int = 0
    metadata: Optional[dict] = {}


# === 音乐生成 (已移除) ===
# 音乐生成功能已从项目中删除

# @router.post("/music/params")
# async def get_music_params_endpoint(req: MusicParamsRequest):
#     """获取音乐参数"""
#     try:
#         params = generate_music_params(req.scores)
#         notes = generate_note_sequence(params, num_notes=16)
#         return {"status": "success", "params": params, "notes": notes}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# @router.get("/music/emotion_scales")
# async def get_emotion_scales():
#     """获取情绪音阶配置"""
#     return {
#         "emotion_scales": {k: list(v) for k, v in EMOTION_SCALES.items()},
#         "emotion_bpm": {k: list(v) for k, v in EMOTION_BPM.items()},
#         "emotion_root": {k: list(v) for k, v in EMOTION_ROOT.items()},
#     }


# === 自适应学习 ===

@router.get("/learner/status")
async def get_learner_status():
    """获取学习器状态"""
    if not _adaptive_learner:
        return {"status": "not_initialized"}

    # ✅ 修复: 确保返回完整的统计数据
    stats = _adaptive_learner.get_stats()

    # 如果是基础版学习器，补充缺失的字段
    if 'top_corrections' not in stats:
        # 手动计算纠正模式
        from collections import defaultdict
        correction_counts = defaultdict(int)
        matrix = stats.get('calibration_matrix', [])
        emotion_order = stats.get('emotion_order', [])

        for i, row in enumerate(matrix):
            for j, value in enumerate(row):
                if i != j and value > 0.5:
                    correction_counts[f"{emotion_order[i]}->{emotion_order[j]}"] = float(
                        value)

        top_corrections = []
        for key, count in sorted(correction_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            from_emotion, to_emotion = key.split('->')
            top_corrections.append({
                'from': from_emotion,
                'to': to_emotion,
                'count': count
            })

        stats['top_corrections'] = top_corrections

        # 添加矩阵统计信息
        import numpy as np
        matrix_np = np.array(matrix)
        stats['matrix_statistics'] = {
            'max_value': float(matrix_np.max()) if matrix_np.size > 0 else 0,
            'sum': float(matrix_np.sum()),
            'sparsity': float((matrix_np > 0.5).sum() / 49) if matrix_np.size > 0 else 0
        }

        stats['calibration_ready'] = stats.get('total_corrections', 0) >= 3

    return {"status": "success", "learner": stats}


@router.post("/feedback")
async def submit_feedback(feedback: FeedbackModel, request: Request):
    """提交用户反馈"""
    try:
        # ✅ 新增: 防重复提交(5秒内相同反馈忽略)
        cache_key = f"{feedback.predicted_emotion}:{feedback.correct_emotion}"
        current_time = time.time()

        if cache_key in _feedback_cache:
            last_submit_time = _feedback_cache[cache_key]
            if current_time - last_submit_time < _FEEDBACK_CACHE_TTL:
                return {
                    "status": "ignored",
                    "message": f"重复反馈，请{_FEEDBACK_CACHE_TTL - int(current_time - last_submit_time)}秒后再试"
                }

        # 更新缓存
        _feedback_cache[cache_key] = current_time

        # 清理过期缓存
        expired_keys = [k for k, v in _feedback_cache.items(
        ) if current_time - v > _FEEDBACK_CACHE_TTL]
        for key in expired_keys:
            del _feedback_cache[key]

        # ✅ 新增: 限流(每IP每分钟最多10次反馈)
        client_ip = request.client.host
        current_time = time.time()

        # 清理过期的请求记录
        _rate_limits[client_ip] = [
            t for t in _rate_limits[client_ip]
            if current_time - t < _RATE_LIMIT_WINDOW
        ]

        # 检查是否超过限制
        if len(_rate_limits[client_ip]) >= _RATE_LIMIT_MAX:
            raise HTTPException(
                status_code=429,
                detail=f"反馈过于频繁，请稍后再试（每分钟最多{_RATE_LIMIT_MAX}次）"
            )

        # 记录本次请求
        _rate_limits[client_ip].append(current_time)

        # 保存反馈数据
        _db_manager.save_feedback(feedback.dict())

        # 更新自适应学习器
        if feedback.feedback_type == 'incorrect' and feedback.predicted_emotion and feedback.correct_emotion:
            if _adaptive_learner:
                _adaptive_learner.update_from_feedback(
                    feedback.predicted_emotion, feedback.correct_emotion)

        return {
            "status": "success",
            "learner_corrections": _adaptive_learner.total_corrections if _adaptive_learner else 0
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"反馈提交失败: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


# === 用户分析 ===

@router.post("/analytics/log")
async def log_feature_usage(data: FeatureLogModel):
    """记录功能使用"""
    _user_analytics.log_feature_usage(
        data.feature, data.session_id, data.duration_ms, data.metadata)
    return {"status": "success"}


@router.get("/analytics/stats")
async def get_analytics_stats(days: int = 30):
    """获取分析统计"""
    return _user_analytics.get_feature_stats(days)


@router.get("/analytics/insights")
async def get_analytics_insights(days: int = 30):
    """获取分析洞察"""
    return {"insights": _user_analytics.get_insights(days)}


@router.get("/analytics/emotion_trend")
async def get_emotion_trend(days: int = 30):
    """获取情绪趋势"""
    return _user_analytics.get_emotion_trend_analysis(days)


@router.get("/analytics/emotion_transitions")
async def get_emotion_transitions(limit: int = 1000):
    """
    获取情绪转换矩阵数据
    分析历史记录中连续检测之间的情绪变化
    """
    try:
        # 获取最近的历史记录（按时间排序）
        records = _db_manager.get_history(limit=limit, offset=0)

        if not records or len(records) < 2:
            return {"status": "success", "transitions": [], "total": 0}

        # 统计情绪转换次数
        transition_counts = defaultdict(int)

        for i in range(len(records) - 1):
            current_emotion = records[i].get('dominant_emotion')
            next_emotion = records[i + 1].get('dominant_emotion')

            if current_emotion and next_emotion and current_emotion != next_emotion:
                # 只统计不同情绪之间的转换
                key = f"{current_emotion}->{next_emotion}"
                transition_counts[key] += 1

        # 转换为前端需要的格式
        transitions = []
        for key, count in transition_counts.items():
            source, target = key.split('->')
            transitions.append({
                "source": source,
                "target": target,
                "value": count
            })

        # 按转换次数排序
        transitions.sort(key=lambda x: x['value'], reverse=True)

        return {
            "status": "success",
            "transitions": transitions,
            "total": sum(t['value'] for t in transitions),
            "record_count": len(records)
        }
    except Exception as e:
        logger.error(f"获取情绪转换数据失败: {e}")
        return {"status": "error", "detail": str(e)}


# === 推理优化 ===

@router.get("/optimizer/status")
async def get_optimizer_status():
    """获取优化器状态"""
    if not _inference_optimizer:
        return {"status": "not_initialized"}
    return {"status": "success", "config": _inference_optimizer.get_inference_config()}


@router.post("/optimizer/toggle")
async def toggle_optimizer(enabled: bool = True):
    """切换优化器"""
    if _inference_optimizer:
        _inference_optimizer.enabled = enabled
    return {"status": "success", "enabled": enabled}


# === 反馈历史 ===

@router.get("/feedback/history")
async def get_feedback_history(
    limit: int = 50,
    offset: int = 0,
    emotion: str = None,
    start_date: str = None,
    end_date: str = None
):
    """获取反馈历史记录"""
    try:
        records = _db_manager.get_feedback_history(
            limit=limit,
            offset=offset,
            emotion_filter=emotion,
            start_date=start_date,
            end_date=end_date
        )
        total = _db_manager.get_feedback_count(
            emotion_filter=emotion,
            start_date=start_date,
            end_date=end_date
        )
        return {
            "status": "success",
            "records": records,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"获取反馈历史失败: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.delete("/feedback/{feedback_id}")
async def delete_feedback(feedback_id: int):
    """删除反馈记录"""
    try:
        success = _db_manager.delete_feedback(feedback_id)
        if success:
            return {
                "status": "success",
                "message": "反馈记录已删除"
            }
        else:
            raise HTTPException(status_code=404, detail="反馈记录不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除反馈记录失败: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")
