"""
AI 自适应学习引擎 - 增强版
基于用户反馈动态校准情绪分类置信度，提升低强度表情识别精度。

新增功能:
1. 场景自适应：根据使用场景（光线、角度、距离）调整校准策略
2. 增量学习：新反馈自动更新校准矩阵，无需重启
3. 遗忘机制：旧反馈权重随时间衰减，适应模型变化
4. 低强度表情优化：专门针对置信度 0.3-0.5 的表情增强校准
"""
import json
import logging
import os
import numpy as np
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# 情绪顺序与 ONNX 模型输出一致
EMOTION_ORDER = ['angry', 'disgust', 'fear',
                 'happy', 'neutral', 'sad', 'surprise']

# 低强度表情阈值
LOW_CONFIDENCE_THRESHOLD = 0.5


class EnhancedAdaptiveLearner:
    """
    增强版自适应学习器

    功能特性:
    - 从 user_feedback 表读取校正记录
    - 维护 7×7 校准矩阵 M[i][j] = 模型输出 i → 用户纠正为 j 的次数
    - 场景自适应：根据光线、角度等场景特征调整校准强度
    - 遗忘机制：旧反馈权重随时间指数衰减
    - 低强度表情优先：置信度 < 0.5 时增强校准效果
    - 在线学习：用户提交反馈时实时更新

    用法:
        learner = EnhancedAdaptiveLearner(db_manager)
        learner.load_from_database()
        calibrated = learner.calibrate(scores_dict, scene_features)
    """

    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        # 校准矩阵: M[predicted][correct] = 频次
        self.calibration_matrix: np.ndarray = np.ones(
            (7, 7), dtype=np.float32) * 0.1
        self.total_corrections = 0
        self._calibration_path = Path(
            __file__).parent / "calibration_state.json"

        # ✅ 新增: 遗忘机制参数
        self.half_life_days = 30  # 反馈半衰期（30天）
        self.min_samples_for_calibration = 10  # ✅ 提高阈值: 最少10个样本才触发校准

    # ── 持久化 ─────────────────────────────────────────────

    def save_state(self):
        """保存校准状态到 JSON"""
        state = {
            'matrix': self.calibration_matrix.tolist(),
            'total_corrections': self.total_corrections,
            'last_updated': datetime.now().isoformat(),
            'version': '2.0'  # 版本号，便于后续扩展
        }
        try:
            with open(self._calibration_path, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
            logger.info(f"✅ 校准状态已保存 ({self.total_corrections} 条校正)")
        except Exception as e:
            logger.warning(f"️ 保存校准状态失败: {e}")

    def load_state(self) -> bool:
        """从 JSON 恢复校准状态"""
        if not self._calibration_path.exists():
            return False
        try:
            with open(self._calibration_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            self.calibration_matrix = np.array(
                state['matrix'], dtype=np.float32)
            self.total_corrections = state.get('total_corrections', 0)
            logger.info(f"✅ 校准状态已加载 ({self.total_corrections} 条校正)")
            return True
        except Exception as e:
            logger.warning(f"⚠️ 加载校准状态失败: {e}")
            return False

    # ─ 从数据库加载反馈 ──────────────────────────────────

    def load_from_database(self):
        """从数据库 user_feedback 表加载所有校正记录"""
        if not self.db_manager:
            logger.warning("⚠️ db_manager 未设置，跳过数据库加载")
            return False

        try:
            conn = self.db_manager._get_conn()
            cursor = conn.cursor()

            # ✅ 增强: 获取带时间戳的反馈记录
            cursor.execute('''
                SELECT predicted_emotion, correct_emotion, feedback_type, timestamp
                FROM user_feedback 
                WHERE feedback_type = 'incorrect'
                ORDER BY timestamp ASC
            ''')

            # ✅ 新增: 应用遗忘机制
            now = datetime.now()
            count = 0

            for row in cursor.fetchall():
                pred = row['predicted_emotion']
                correct = row['correct_emotion']
                timestamp_str = row.get('timestamp')

                if pred in EMOTION_ORDER and correct in EMOTION_ORDER:
                    pi = EMOTION_ORDER.index(pred)
                    ci = EMOTION_ORDER.index(correct)

                    # ✅ 新增: 计算时间衰减权重
                    weight = 1.0
                    if timestamp_str:
                        try:
                            feedback_time = datetime.fromisoformat(
                                timestamp_str)
                            days_ago = (now - feedback_time).days
                            # 指数衰减: weight = 0.5^(days / half_life)
                            weight = 0.5 ** (days_ago / self.half_life_days)
                        except:
                            pass

                    self.calibration_matrix[pi][ci] += weight
                    count += 1

            self.total_corrections = count
            logger.info(f"✅ 从数据库加载了 {count} 条校正记录（带时间衰减）")
            self.save_state()
            return True

        except Exception as e:
            logger.error(f" 从数据库加载校正记录失败: {e}")
            return False

    # ── 在线更新（实时反馈） ──────────────────────────────

    def update_from_feedback(self, predicted: str, correct: str, timestamp: str = None):
        """
        用户提交一条反馈时实时更新校准矩阵

        参数:
            predicted: 模型预测的情绪
            correct: 用户纠正的正确情绪
            timestamp: 反馈时间（ISO 格式）
        """
        if predicted not in EMOTION_ORDER or correct not in EMOTION_ORDER:
            logger.warning(f"️ 无效的情绪标签: {predicted} -> {correct}")
            return

        pi = EMOTION_ORDER.index(predicted)
        ci = EMOTION_ORDER.index(correct)

        # ✅ 增强: 新反馈赋予较高权重（最近反馈更重要）
        weight = 1.5  # 新反馈权重提升 50%

        self.calibration_matrix[pi][ci] += weight
        self.total_corrections += 1

        logger.info(f" 在线更新校准: {predicted} → {correct} (权重: {weight})")
        self.save_state()

    # ── 核心校准方法 ──────────────────────────────────────

    def calibrate(self, scores: Dict[str, float], scene_features: Dict = None) -> Dict[str, float]:
        """
        对原始置信度分数进行校准

        策略:
        1. 将 scores dict 转为 7 维向量
        2. 根据场景特征动态调整校准强度
        3. 与校准矩阵的转置相乘: calibrated = matrix^T · raw
        4. 归一化回总和为 1
        5. 对低强度预测（原始置信度 < 0.5）增强校准效果

        参数:
            scores: 原始情绪分数 {emotion: score}
            scene_features: 场景特征（可选）
                - lighting: 光线条件 (0-1, 1=良好)
                - angle: 面部角度 (0-1, 1=正面)
                - distance: 距离适中 (0-1, 1=适中)

        返回:
            校准后的情绪分数
        """
        if self.total_corrections < self.min_samples_for_calibration:
            # 数据量太少，直接返回原始分数
            logger.debug(
                f"📊 校正样本不足 ({self.total_corrections} < {self.min_samples_for_calibration})，跳过校准")
            return scores

        # 转为向量
        idx_map = {e: i for i, e in enumerate(EMOTION_ORDER)}
        raw = np.array([scores.get(e, 0.0)
                       for e in EMOTION_ORDER], dtype=np.float32)

        # ✅ 增强: 动态计算校准强度
        max_conf = raw.max()

        # 基础校准强度
        base_strength = 0.3 if max_conf > LOW_CONFIDENCE_THRESHOLD else 0.8

        # ✅ 新增: 场景自适应调整
        scene_multiplier = 1.0
        if scene_features:
            lighting = scene_features.get('lighting', 1.0)
            angle = scene_features.get('angle', 1.0)
            distance = scene_features.get('distance', 1.0)

            # 光线差、角度偏、距离远时，降低校准强度（信任原始模型）
            scene_quality = (lighting + angle + distance) / 3.0
            if scene_quality < 0.5:
                scene_multiplier = 0.5  # 降低 50%
                logger.debug(f" 场景质量较低 ({scene_quality:.2f})，降低校准强度")

        # ✅ 新增: 低强度表情特别优化
        low_confidence_boost = 1.0
        if max_conf < LOW_CONFIDENCE_THRESHOLD:
            low_confidence_boost = 1.5  # 低强度表情增强 50%
            logger.debug(f"📊 低强度表情 (置信度: {max_conf:.2f})，增强校准")

        calibration_strength = base_strength * scene_multiplier * low_confidence_boost

        # 限制校准强度范围
        calibration_strength = np.clip(calibration_strength, 0.1, 1.0)

        # 校准: calibrated = (I + alpha * M^T) · raw
        identity = np.eye(7, dtype=np.float32)

        # 归一化校准矩阵每行
        row_sums = self.calibration_matrix.sum(axis=1, keepdims=True)
        row_sums = np.maximum(row_sums, 1e-6)
        norm_matrix = self.calibration_matrix / row_sums

        transform = identity + calibration_strength * norm_matrix.T
        calibrated = transform @ raw

        # 转为 dict 并归一化
        result = {e: float(calibrated[i]) for i, e in enumerate(EMOTION_ORDER)}
        total = sum(result.values())
        if total > 0:
            result = {k: v / total for k, v in result.items()}

        logger.debug(
            f"📊 校准: {max(raw):.3f} → {max(calibrated):.3f} (强度: {calibration_strength:.2f})")
        return result

    def get_stats(self) -> Dict:
        """获取学习统计"""
        # ✅ 增强: 返回更详细的统计信息
        matrix_max = self.calibration_matrix.max()
        matrix_sum = self.calibration_matrix.sum()

        # 找出最常见的纠正模式
        top_corrections = []
        for i in range(7):
            for j in range(7):
                if i != j and self.calibration_matrix[i][j] > 0.1:
                    top_corrections.append({
                        'from': EMOTION_ORDER[i],
                        'to': EMOTION_ORDER[j],
                        'count': float(self.calibration_matrix[i][j])
                    })

        top_corrections.sort(key=lambda x: x['count'], reverse=True)

        return {
            'total_corrections': self.total_corrections,
            'calibration_matrix': self.calibration_matrix.tolist(),
            'emotion_order': EMOTION_ORDER,
            'matrix_statistics': {
                'max_value': float(matrix_max),
                'sum': float(matrix_sum),
                'sparsity': float((self.calibration_matrix > 0.5).sum() / 49)
            },
            'top_corrections': top_corrections[:5],  # 前5个最常见的纠正
            'calibration_ready': self.total_corrections >= self.min_samples_for_calibration
        }
