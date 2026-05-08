"""情绪趋势分析 API 路由"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
import json

router = APIRouter(prefix="/api/emotion-trend", tags=["emotion-trend"])

# 情绪名称映射
EMOTION_NAMES = {
    'happy': '开心',
    'sad': '难过',
    'angry': '生气',
    'surprise': '惊讶',
    'fear': '害怕',
    'disgust': '厌恶',
    'neutral': '平静'
}

# 情绪波动模式映射
FLUCTUATION_PATTERNS = {
    'stable': '情绪稳定',
    'slight_fluctuation': '轻微波动',
    'moderate_fluctuation': '中度波动',
    'severe_fluctuation': '剧烈波动',
    'unknown': '未知'
}

# 强度变化映射
INTENSITY_CHANGES = {
    'increasing': '上升',
    'decreasing': '下降',
    'stable': '稳定'
}

# 风险等级映射
RISK_LEVELS = {
    'none': '无风险',
    'low': '低风险',
    'medium': '中等风险',
    'high': '高风险'
}

# 积极情绪关键词
POSITIVE_WORDS = [
    '开心', '快乐', '高兴', '幸福', '满足', '满意', '愉悦', '兴奋',
    '喜悦', '欣慰', '温暖', '感动', '乐观', '自信', '平和', '平静',
    '放松', '舒适', '安心', '希望', '期待', '憧憬', '美好', '顺利',
    '成功', '进步', '成长', '收获', '感恩', '感谢', '爱', '喜欢',
    '微笑', '大笑', '拥抱', '加油', '努力', '坚持', '勇敢', '坚强'
]

# 消极情绪关键词
NEGATIVE_WORDS = [
    '难过', '伤心', '悲伤', '痛苦', '失望', '沮丧', '郁闷', '烦躁',
    '焦虑', '紧张', '压力', '担心', '害怕', '恐惧', '愤怒', '生气',
    '不满', '抱怨', '委屈', '孤独', '寂寞', '无助', '迷茫', '困惑',
    '绝望', '失落', '空虚', '疲惫', '累', '厌倦', '无聊', '烦躁'
]

# 警告词
WARNING_WORDS = [
    '自杀', '想死', '活着没意思', '太累了', '撑不住了', '放弃',
    '结束', '伤害自己', '割腕', '跳楼', '吃药', '失眠', '食欲',
    '体重', '哭泣', '崩溃', '失控', '麻木', '冷漠', '无意义'
]


def analyze_text_content(text: str) -> Dict:
    """分析文本内容中的情绪关键词"""
    if not text or not isinstance(text, str):
        return {
            "positive_count": 0,
            "negative_count": 0,
            "warning_count": 0,
            "positive_words": [],
            "negative_words": [],
            "warning_words": [],
            "sentiment_score": 0,
            "emotion_level": "neutral"
        }

    lower_text = text.lower()
    result = {
        "positive_count": 0,
        "negative_count": 0,
        "warning_count": 0,
        "positive_words": [],
        "negative_words": [],
        "warning_words": [],
        "sentiment_score": 0,
        "emotion_level": "neutral"
    }

    for word in POSITIVE_WORDS:
        if word.lower() in lower_text:
            result["positive_count"] += 1
            result["positive_words"].append(word)

    for word in NEGATIVE_WORDS:
        if word.lower() in lower_text:
            result["negative_count"] += 1
            result["negative_words"].append(word)

    for word in WARNING_WORDS:
        if word.lower() in lower_text:
            result["warning_count"] += 1
            result["warning_words"].append(word)

    total = result["positive_count"] + result["negative_count"]
    if total > 0:
        result["sentiment_score"] = round(
            ((result["positive_count"] - result["negative_count"]) / total) * 100, 2
        )

    if result["warning_count"] > 0:
        result["emotion_level"] = "warning"
    elif result["sentiment_score"] > 30:
        result["emotion_level"] = "positive"
    elif result["sentiment_score"] < -30:
        result["emotion_level"] = "negative"
    else:
        result["emotion_level"] = "neutral"

    return result


def extract_text_key_info(text: str, emotion_analysis: Dict) -> List[str]:
    """提取文字中与情绪趋势相关的关键信息"""
    key_info = []

    if not text or not isinstance(text, str):
        return key_info

    text_analysis = analyze_text_content(text)

    if text_analysis["positive_count"] > 0:
        key_info.append(f"文字中包含{text_analysis['positive_count']}个积极情绪词")

    if text_analysis["negative_count"] > 0:
        key_info.append(f"文字中包含{text_analysis['negative_count']}个消极情绪词")

    if text_analysis["warning_count"] > 0:
        key_info.append(f"文字中包含{text_analysis['warning_count']}个警告词")

    if emotion_analysis.get("main_emotion"):
        main_emotion = emotion_analysis["main_emotion"]
        emotion_name = EMOTION_NAMES.get(main_emotion, main_emotion)

        if main_emotion in ["happy", "surprise"] and text_analysis["positive_count"] > 0:
            key_info.append("文字情绪与面部情绪一致，呈现积极状态")
        elif main_emotion in ["sad", "angry", "fear", "disgust"] and text_analysis["negative_count"] > 0:
            key_info.append("文字情绪与面部情绪一致，呈现消极状态")
        elif main_emotion == "neutral" and text_analysis["positive_count"] > 0:
            key_info.append("面部情绪平静，但文字表达积极情绪")
        elif main_emotion == "neutral" and text_analysis["negative_count"] > 0:
            key_info.append("面部情绪平静，但文字表达消极情绪")

    return key_info


def generate_analysis_opinion(emotion_analysis: Dict, text_analysis: Dict, risk_info: Dict) -> str:
    """生成具有针对性的分析意见"""
    opinions = []

    fluctuation_pattern = emotion_analysis.get("fluctuation_pattern", "unknown")
    pattern_name = FLUCTUATION_PATTERNS.get(fluctuation_pattern, "未知")
    opinions.append(f"情绪趋势{pattern_name}")

    main_emotion = emotion_analysis.get("main_emotion")
    if main_emotion:
        emotion_name = EMOTION_NAMES.get(main_emotion, main_emotion)
        intensity = emotion_analysis.get("main_emotion_intensity", 0)
        intensity_percent = round(intensity * 100)
        opinions.append(f"主要情绪为{emotion_name}，强度{intensity_percent}%")

    intensity_change = emotion_analysis.get("intensity_change", "stable")
    change_name = INTENSITY_CHANGES.get(intensity_change, "稳定")
    opinions.append(f"情绪强度{change_name}")

    if text_analysis.get("positive_count", 0) > 0:
        opinions.append("文字内容表达积极情绪")
    elif text_analysis.get("negative_count", 0) > 0:
        opinions.append("文字内容表达消极情绪")

    if risk_info.get("has_risk", False):
        risk_level = risk_info.get("risk_level", "low")
        risk_name = RISK_LEVELS.get(risk_level, "未知")
        opinions.append(f"当前情绪状态存在{risk_name}")

    return "；".join(opinions) + "。"


def generate_warning_message(emotion_analysis: Dict, text_analysis: Dict, risk_info: Dict) -> Optional[str]:
    """根据情绪趋势的异常变化或潜在风险点，发出明确且具体的警告提示"""
    warnings = []

    fluctuation_pattern = emotion_analysis.get("fluctuation_pattern")
    if fluctuation_pattern == "severe_fluctuation":
        warnings.append("💫 情绪有些起伏，试着做几次深呼吸，放松一下")

    main_emotion = emotion_analysis.get("main_emotion")
    main_intensity = emotion_analysis.get("main_emotion_intensity", 0)

    if main_emotion in ["sad", "angry", "fear", "disgust"]:
        if main_intensity > 0.7:
            emotion_name = EMOTION_NAMES.get(main_emotion, main_emotion)
            warnings.append(f"💕 检测到{emotion_name}情绪较高，保持冷静，一切都会好起来的")
        elif main_intensity > 0.5:
            emotion_name = EMOTION_NAMES.get(main_emotion, main_emotion)
            warnings.append(f"💖 感受到{emotion_name}情绪，记得照顾好自己，适当休息")

    intensity_change = emotion_analysis.get("intensity_change")
    if intensity_change == "increasing" and main_intensity > 0.5:
        if main_emotion in ["sad", "angry", "fear", "disgust"]:
            warnings.append("🌱 情绪正在变化，试着做些让自己开心的事情吧")

    emotion_changes = emotion_analysis.get("emotion_changes", [])
    if len(emotion_changes) > 5:
        warnings.append("✨ 情绪变化较多，给自己一些时间，慢慢来")

    if text_analysis.get("warning_count", 0) > 0:
        warnings.append("💝 文字内容中包含需要特别关注的表达")

    if text_analysis.get("negative_count", 0) > 3:
        warnings.append("🌻 文字内容表达较多情绪，建议与亲友聊聊天")

    if risk_info.get("has_risk", False):
        risk_level = risk_info.get("risk_level")
        if risk_level == "high":
            warnings.append("🌈 当前情绪状态需要关注，记得及时与亲友沟通")

    if warnings:
        return warnings[0]

    return None


def generate_recommendation(emotion_analysis: Dict, text_analysis: Dict, risk_info: Dict) -> str:
    """生成情绪管理建议"""
    main_emotion = emotion_analysis.get("main_emotion")
    fluctuation_pattern = emotion_analysis.get("fluctuation_pattern")
    risk_level = risk_info.get("risk_level", "none")

    if risk_level == "high":
        recommendations = [
            "💕 试着放下手头的事情，做几次深呼吸（吸气4秒，保持4秒，呼气6秒）",
            "💫 与信任的亲友聊聊天，分享你的感受，你并不孤单",
            "🌈 记住，困难只是暂时的，阳光总会照耀到你"
        ]
        return recommendations[0]

    if risk_level == "medium":
        recommendations = [
            "✨ 建议听一首舒缓的音乐，放松一下身心",
            "🌻 适当休息片刻，给自己一些时间调整状态",
            "🌸 做一些喜欢的事情，转移一下注意力"
        ]
        return recommendations[0]

    if fluctuation_pattern == "severe_fluctuation":
        return "💖 情绪有些起伏，试着深呼吸，让自己慢慢平静下来"

    if fluctuation_pattern == "moderate_fluctuation":
        return "🌱 情绪有一些波动，关注自己的感受，适当调节就好"

    if main_emotion in ["happy", "surprise"]:
        return "🎉 保持这份好心情，快乐是最好的礼物！"

    if main_emotion in ["sad", "angry", "fear", "disgust"]:
        return "💝 情绪波动很正常，给自己一些时间和空间，一切都会好的"

    if text_analysis.get("positive_count", 0) > 0:
        return "🌟 你的积极心态很棒，继续保持！"

    if text_analysis.get("negative_count", 0) > 0:
        return "💫 文字表达了一些情绪，记得好好照顾自己"

    return "😊 当前情绪状态平稳，保持这份平和，你做得很好！"


@router.post("/analyze")
async def analyze_emotion_trend(data: Dict):
    """
    分析情绪趋势并生成综合分析意见
    
    请求体：
    {
        "emotion_analysis": {
            "time_window": 3,
            "data_points": 3,
            "fluctuation_pattern": "stable",
            "main_emotion": "happy",
            "main_emotion_intensity": 0.8,
            "intensity_change": "increasing",
            "emotion_changes": [...],
            "intensity_trends": {...},
            "key_info": [...],
            "analysis": "..."
        },
        "text_content": "用户输入的文字内容",
        "risk_info": {
            "has_risk": false,
            "risk_level": "none",
            "risk_message": ""
        },
        "timestamp": 1234567890
    }
    """
    try:
        emotion_analysis = data.get("emotion_analysis", {})
        text_content = data.get("text_content", "")
        risk_info = data.get("risk_info", {})

        text_analysis = analyze_text_content(text_content)

        text_key_info = extract_text_key_info(text_content, emotion_analysis)

        analysis_opinion = generate_analysis_opinion(emotion_analysis, text_analysis, risk_info)

        warning_message = generate_warning_message(emotion_analysis, text_analysis, risk_info)

        recommendation = generate_recommendation(emotion_analysis, text_analysis, risk_info)

        result = {
            "status": "success",
            "timestamp": data.get("timestamp"),
            "emotion_trend_analysis": {
                "time_window": emotion_analysis.get("time_window"),
                "data_points": emotion_analysis.get("data_points"),
                "fluctuation_pattern": emotion_analysis.get("fluctuation_pattern"),
                "fluctuation_pattern_name": FLUCTUATION_PATTERNS.get(
                    emotion_analysis.get("fluctuation_pattern"), "未知"
                ),
                "main_emotion": emotion_analysis.get("main_emotion"),
                "main_emotion_name": EMOTION_NAMES.get(
                    emotion_analysis.get("main_emotion"), emotion_analysis.get("main_emotion")
                ),
                "main_emotion_intensity": emotion_analysis.get("main_emotion_intensity"),
                "intensity_change": emotion_analysis.get("intensity_change"),
                "intensity_change_name": INTENSITY_CHANGES.get(
                    emotion_analysis.get("intensity_change"), "稳定"
                ),
                "emotion_changes_count": len(emotion_analysis.get("emotion_changes", [])),
                "key_info": emotion_analysis.get("key_info", [])
            },
            "text_analysis": {
                "has_text": bool(text_content),
                "positive_count": text_analysis["positive_count"],
                "negative_count": text_analysis["negative_count"],
                "warning_count": text_analysis["warning_count"],
                "positive_words": text_analysis["positive_words"],
                "negative_words": text_analysis["negative_words"],
                "warning_words": text_analysis["warning_words"],
                "sentiment_score": text_analysis["sentiment_score"],
                "emotion_level": text_analysis["emotion_level"],
                "key_info": text_key_info
            },
            "comprehensive_analysis": {
                "analysis_opinion": analysis_opinion,
                "warning_message": warning_message,
                "recommendation": recommendation
            },
            "risk_assessment": {
                "has_risk": risk_info.get("has_risk", False),
                "risk_level": risk_info.get("risk_level", "none"),
                "risk_level_name": RISK_LEVELS.get(
                    risk_info.get("risk_level"), "无风险"
                ),
                "risk_message": risk_info.get("risk_message", ""),
                "enhanced_warning": warning_message
            }
        }

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "emotion-trend-analysis"
    }
