"""文本情绪分析 API 路由"""
from fastapi import APIRouter, HTTPException
from core.database import DatabaseManager
import json

router = APIRouter(prefix="/api/text-analysis", tags=["text-analysis"])

_db_manager = None


def init_text_analysis_router(db_manager: DatabaseManager):
    """初始化路由依赖"""
    global _db_manager
    _db_manager = db_manager


# 情绪关键词定义
POSITIVE_WORDS = [
    '开心', '快乐', '高兴', '幸福', '满足', '满意', '愉悦', '兴奋',
    '喜悦', '欣慰', '温暖', '感动', '乐观', '自信', '平和', '平静',
    '放松', '舒适', '安心', '希望', '期待', '憧憬', '美好', '顺利',
    '成功', '进步', '成长', '收获', '感恩', '感谢', '爱', '喜欢',
    '微笑', '大笑', '拥抱', '加油', '努力', '坚持', '勇敢', '坚强'
]

NEGATIVE_WORDS = [
    '难过', '伤心', '悲伤', '痛苦', '失望', '沮丧', '郁闷', '烦躁',
    '焦虑', '紧张', '压力', '担心', '害怕', '恐惧', '愤怒', '生气',
    '不满', '抱怨', '委屈', '孤独', '寂寞', '无助', '迷茫', '困惑',
    '绝望', '失落', '空虚', '疲惫', '累', '厌倦', '无聊', '烦躁'
]

WARNING_WORDS = [
    '自杀', '想死', '活着没意思', '太累了', '撑不住了', '放弃',
    '结束', '伤害自己', '割腕', '跳楼', '吃药', '失眠', '食欲',
    '体重', '哭泣', '崩溃', '失控', '麻木', '冷漠', '无意义'
]


def analyze_text_emotion(text: str):
    """分析文本情绪"""
    if not text or not isinstance(text, str):
        return {
            "text": text or "",
            "positive_count": 0,
            "negative_count": 0,
            "warning_count": 0,
            "positive_words": [],
            "negative_words": [],
            "warning_words": [],
            "sentiment_score": 0,
            "emotion_level": "neutral",
            "emotion_label": "中性",
            "analysis_summary": "文本为空或无效",
            "recommendation": "请输入有效文本进行情绪分析"
        }

    lower_text = text.lower()
    result = {
        "text": text,
        "positive_count": 0,
        "negative_count": 0,
        "warning_count": 0,
        "positive_words": [],
        "negative_words": [],
        "warning_words": [],
        "sentiment_score": 0,
        "emotion_level": "neutral",
        "emotion_label": "中性",
        "analysis_summary": "",
        "recommendation": ""
    }

    # 统计积极情绪词
    for word in POSITIVE_WORDS:
        if word.lower() in lower_text:
            result["positive_count"] += 1
            result["positive_words"].append(word)

    # 统计消极情绪词
    for word in NEGATIVE_WORDS:
        if word.lower() in lower_text:
            result["negative_count"] += 1
            result["negative_words"].append(word)

    # 统计警告词
    for word in WARNING_WORDS:
        if word.lower() in lower_text:
            result["warning_count"] += 1
            result["warning_words"].append(word)

    # 计算情感分数
    total = result["positive_count"] + result["negative_count"]
    if total > 0:
        result["sentiment_score"] = round(
            ((result["positive_count"] - result["negative_count"]) / total) * 100, 2
        )

    # 确定情绪等级
    if result["warning_count"] > 0:
        result["emotion_level"] = "warning"
        result["emotion_label"] = "警告"
    elif result["sentiment_score"] > 30:
        result["emotion_level"] = "positive"
        result["emotion_label"] = "积极"
    elif result["sentiment_score"] < -30:
        result["emotion_level"] = "negative"
        result["emotion_label"] = "消极"
    else:
        result["emotion_level"] = "neutral"
        result["emotion_label"] = "中性"

    # 生成分析摘要
    parts = []
    if result["warning_count"] > 0:
        parts.append(f"检测到 {result['warning_count']} 个警告关键词")
    if result["positive_count"] > 0:
        parts.append(f"识别到 {result['positive_count']} 个积极情绪词")
    if result["negative_count"] > 0:
        parts.append(f"识别到 {result['negative_count']} 个消极情绪词")
    
    if parts:
        result["analysis_summary"] = "；".join(parts)
    else:
        result["analysis_summary"] = "文本中未明显检测到情绪相关词汇，情绪状态较为平和。"

    # 生成建议
    recommendations = {
        "positive": [
            "继续保持这份积极的心态，你的努力正在带来美好的改变！",
            "积极的情绪是最好的动力，继续保持情绪稳定！",
            "你的心态很棒，保持情绪稳定有助于身心健康！"
        ],
        "neutral": [
            "当前情绪较为平稳，保持情绪稳定是最好的状态！",
            "情绪平和是一种智慧，继续保持情绪稳定！",
            "平淡中见真章，保持情绪稳定就是最好的生活态度！"
        ],
        "negative": [
            "情绪波动是正常的，关键是学会调节，保持情绪稳定！",
            "每个人都有低谷期，给自己一些时间和空间，保持情绪稳定！",
            "困难只是暂时的，保持情绪稳定，相信一切都会好起来！"
        ],
        "warning": [
            "你的情绪状态需要特别关注，请务必保持情绪稳定！",
            "建议你及时与亲友沟通，或寻求专业帮助，保持情绪稳定！",
            "请记住，无论何时，都有人关心你，请保持情绪稳定！"
        ]
    }
    
    rec_list = recommendations.get(result["emotion_level"], recommendations["neutral"])
    result["recommendation"] = rec_list[0]

    return result


@router.post("/analyze")
async def analyze_single_text(data: dict):
    """分析单条文本的情绪"""
    text = data.get("text", "")
    result = analyze_text_emotion(text)
    return {
        "status": "success",
        "data": result
    }


@router.post("/analyze-batch")
async def analyze_batch_text(data: dict):
    """批量分析多条文本的情绪"""
    texts = data.get("texts", [])
    if not isinstance(texts, list):
        raise HTTPException(status_code=400, detail="texts must be an array")

    results = []
    for idx, text in enumerate(texts):
        result = analyze_text_emotion(text)
        result["row_index"] = idx
        results.append(result)

    # 计算整体统计
    total = len(results)
    positive_count = sum(1 for r in results if r["emotion_level"] == "positive")
    negative_count = sum(1 for r in results if r["emotion_level"] == "negative")
    neutral_count = sum(1 for r in results if r["emotion_level"] == "neutral")
    warning_count = sum(1 for r in results if r["emotion_level"] == "warning")
    avg_score = sum(r["sentiment_score"] for r in results) / total if total > 0 else 0

    return {
        "status": "success",
        "data": results,
        "summary": {
            "total_records": total,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "warning_count": warning_count,
            "average_sentiment_score": round(avg_score, 2),
            "positive_ratio": round(positive_count / total * 100, 2) if total > 0 else 0,
            "negative_ratio": round(negative_count / total * 100, 2) if total > 0 else 0,
            "neutral_ratio": round(neutral_count / total * 100, 2) if total > 0 else 0,
            "warning_ratio": round(warning_count / total * 100, 2) if total > 0 else 0
        }
    }


@router.get("/analyze-feedback")
async def analyze_feedback_records(limit: int = 100):
    """分析用户反馈记录中的文本情绪"""
    try:
        feedback_records = _db_manager.get_feedback(limit=limit)
        results = []
        
        for record in feedback_records:
            # 提取文本内容（notes字段）
            text = record.get("notes", "")
            
            # 如果notes为空，尝试从其他字段获取文本
            if not text:
                emotion_info = f"预测情绪: {record.get('predicted_emotion', '')}, 正确情绪: {record.get('correct_emotion', '')}"
                text = emotion_info
            
            result = analyze_text_emotion(text)
            result["record_id"] = record.get("id")
            result["timestamp"] = record.get("timestamp")
            result["predicted_emotion"] = record.get("predicted_emotion")
            result["correct_emotion"] = record.get("correct_emotion")
            results.append(result)

        # 计算整体统计
        total = len(results)
        positive_count = sum(1 for r in results if r["emotion_level"] == "positive")
        negative_count = sum(1 for r in results if r["emotion_level"] == "negative")
        neutral_count = sum(1 for r in results if r["emotion_level"] == "neutral")
        warning_count = sum(1 for r in results if r["emotion_level"] == "warning")
        avg_score = sum(r["sentiment_score"] for r in results) / total if total > 0 else 0

        return {
            "status": "success",
            "data": results,
            "summary": {
                "total_records": total,
                "positive_count": positive_count,
                "negative_count": negative_count,
                "neutral_count": neutral_count,
                "warning_count": warning_count,
                "average_sentiment_score": round(avg_score, 2),
                "positive_ratio": round(positive_count / total * 100, 2) if total > 0 else 0,
                "negative_ratio": round(negative_count / total * 100, 2) if total > 0 else 0,
                "neutral_ratio": round(neutral_count / total * 100, 2) if total > 0 else 0,
                "warning_ratio": round(warning_count / total * 100, 2) if total > 0 else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/emotion-keywords")
async def get_emotion_keywords():
    """获取情绪关键词列表"""
    return {
        "status": "success",
        "positive_words": POSITIVE_WORDS,
        "negative_words": NEGATIVE_WORDS,
        "warning_words": WARNING_WORDS
    }