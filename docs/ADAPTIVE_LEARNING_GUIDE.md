# AI 自适应学习系统 - 使用指南

## 📋 概述

本系统实现了**基于用户反馈的 AI 自适应学习机制**，能够根据实际使用场景持续提升表情识别的准确率，尤其针对**低强度表情**（置信度 0.3-0.5）进行优化。

---

##  核心功能

### 1. 用户反馈收集

#### 前端使用
在实时检测页面，点击面板右上角的 **"编辑"按钮**（✏️图标），即可提交反馈：

```vue
<!-- 自动集成在 RealtimeDetector.vue 中 -->
<EmotionFeedback
    v-model:visible="showFeedback"
    :predicted-emotion="currentEmotion"
    :predicted-confidence="currentConfidence"
    @submitted="handleFeedbackSubmitted"
/>
```

#### 后端 API
```python
POST /api/ai/feedback
Content-Type: application/json

{
    "emotion": "happy",              # 当前情绪
    "predicted_emotion": "neutral",  # 系统预测的情绪
    "correct_emotion": "happy",      # 用户纠正的正确情绪
    "feedback_type": "incorrect",    # 反馈类型
    "confidence": 0.45,              # 原始置信度
    "notes": "用户实际在微笑"        # 备注（可选）
}
```

---

### 2. 自适应校准机制

#### 工作原理

系统维护一个 **7×7 校准矩阵**，记录模型预测情绪与用户纠正情绪的映射关系：

```
M[predicted][correct] = 校正次数

例如:
M['neutral']['happy'] = 15.5  # 模型预测 neutral，但用户纠正为 happy（15.5次）
```

#### 校准策略

```python
# 1. 基础校准（数据充足时）
if total_corrections >= 3:
    calibrated = (I + alpha * M^T) · raw_scores

# 2. 动态校准强度
- 高强度表情（置信度 > 0.5）: alpha = 0.3（温和校准）
- 低强度表情（置信度 < 0.5）: alpha = 0.8（强力校准）

# 3. 场景自适应（可选）
if scene_quality < 0.5:  # 光线差、角度偏
    alpha *= 0.5  # 降低校准强度，更信任原始模型
```

---

### 3. 增量学习

系统支持**在线学习**，用户提交反馈后实时更新校准矩阵：

```python
# 后端自动处理（在 ai_features.py 中）
@router.post("/feedback")
async def submit_feedback(feedback: FeedbackModel):
    # 1. 保存反馈到数据库
    db_manager.save_feedback(feedback)
    
    # 2. 实时更新校准矩阵
    adaptive_learner.update_from_feedback(
        predicted=feedback.predicted_emotion,
        correct=feedback.correct_emotion
    )
    
    return {"status": "success"}
```

---

### 4. 遗忘机制

为避免旧反馈干扰当前模型，系统实现了**时间衰减权重**：

```python
# 反馈权重随时间指数衰减
weight = 0.5 ^ (days_ago / half_life_days)

# 默认半衰期: 30 天
# - 15 天前的反馈: weight = 0.71
# - 30 天前的反馈: weight = 0.50
# - 60 天前的反馈: weight = 0.25
```

---

## 🔧 配置参数

### 增强版学习器 (`enhanced_learner.py`)

```python
class EnhancedAdaptiveLearner:
    def __init__(self, db_manager=None):
        self.half_life_days = 30              # 反馈半衰期（天）
        self.min_samples_for_calibration = 3  # 最少样本数
        self.low_confidence_threshold = 0.5   # 低强度表情阈值
```

### 场景自适应参数

```python
scene_features = {
    'lighting': 0.8,    # 光线条件 (0-1, 1=良好)
    'angle': 0.9,       # 面部角度 (0-1, 1=正面)
    'distance': 0.7     # 距离适中 (0-1, 1=适中)
}

# 系统自动计算场景质量
scene_quality = (lighting + angle + distance) / 3.0
```

---

## 📊 监控与统计

### 查看学习进度

```python
# 获取学习统计
stats = adaptive_learner.get_stats()

# 返回示例
{
    "total_corrections": 42,
    "calibration_ready": True,
    "matrix_statistics": {
        "max_value": 15.5,
        "sum": 87.3,
        "sparsity": 0.24  # 24% 的矩阵元素有显著值
    },
    "top_corrections": [
        {"from": "neutral", "to": "happy", "count": 15.5},
        {"from": "sad", "to": "neutral", "count": 8.2},
        ...
    ]
}
```

---

## 🚀 使用流程

### 1. 初始化（启动时）

```python
# 在 app.py 或 __init__.py 中
from adaptation.enhanced_learner import EnhancedAdaptiveLearner

adaptive_learner = EnhancedAdaptiveLearner(db_manager)
adaptive_learner.load_from_database()  # 加载历史反馈
```

### 2. 推理时应用校准

```python
# 在 websocket.py 的推理流程中
raw_scores = emotion_classifier.predict(frame)

# 应用自适应校准
calibrated_scores = adaptive_learner.calibrate(
    raw_scores,
    scene_features={  # 可选
        'lighting': detect_lighting(frame),
        'angle': detect_angle(face_bbox),
        'distance': estimate_distance(face_bbox)
    }
)

# 使用校准后的分数
emotion = max(calibrated_scores, key=calibrated_scores.get)
confidence = calibrated_scores[emotion]
```

### 3. 用户提交反馈

前端用户点击反馈按钮 → 后端自动更新校准矩阵 → 下次推理自动应用

---

## 📈 性能优化建议

### 1. 数据积累阶段（0-10 条反馈）

- **策略**: 使用基础校准，低强度表情增强
- **预期效果**: 轻微提升准确率（2-5%）

### 2. 成熟阶段（10-50 条反馈）

- **策略**: 启用场景自适应，动态调整校准强度
- **预期效果**: 显著提升准确率（5-15%）

### 3. 稳定阶段（50+ 条反馈）

- **策略**: 启用遗忘机制，关注近期反馈
- **预期效果**: 持续优化，适应模型变化

---

## ⚠️ 注意事项

1. **数据隐私**: 用户反馈仅用于模型校准，不会上传到外部服务器
2. **防重复提交**: 5 秒内相同反馈会被忽略（防止误触）
3. **冷启动**: 前 3 条反馈不会触发校准（避免过拟合）
4. **性能开销**: 校准计算非常轻量（< 1ms），不影响实时性

---

## 🔮 未来扩展

- [ ] 多用户个性化校准（每个用户独立的校准矩阵）
- [ ] 主动学习（系统主动询问不确定的样本）
- [ ] 跨设备同步（校准状态云端备份）
- [ ] 可视化学习进度（展示校准矩阵热力图）

---

## 📚 相关文件

- **核心实现**: `backend/adaptation/enhanced_learner.py`
- **旧版实现**: `backend/adaptation/active_learner.py`
- **前端组件**: `frontend/src/components/EmotionFeedback.vue`
- **集成示例**: `backend/api/websocket.py` (第 377-391 行)
- **反馈 API**: `backend/api/ai_features.py` (第 163-200 行)
