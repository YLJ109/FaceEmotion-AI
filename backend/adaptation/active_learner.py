"""
AI 自适应学习引擎
基于用户反馈动态校准情绪分类置信度，提升低强度表情识别精度。
原理：统计历史反馈中每个情绪被纠正的方向和频率，生成校准矩阵。
"""
import json
import logging
import os
import numpy as np
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# 情绪顺序与 ONNX 模型输出一致
EMOTION_ORDER = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']


class AdaptiveLearner:
    """
    自适应学习器

    - 从 user_feedback 表读取校正记录
    - 维护 7×7 校准矩阵 M[i][j] = 模型输出 i → 用户纠正为 j 的次数
    - 运行时将原始置信度 scores 与校准矩阵相乘，输出校准后置信度
    - 低强度表情（置信度 0.3~0.5）优先应用校准

    用法:
        learner = AdaptiveLearner(db_manager)
        learner.load_from_database()
        calibrated = learner.calibrate(scores_dict)  # 推理时调用
    """

    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        # 校准矩阵: M[predicted][correct] = 频次
        self.calibration_matrix: np.ndarray = np.ones((7, 7), dtype=np.float32) * 0.1
        self.total_corrections = 0
        self._calibration_path = Path(__file__).parent / "calibration_state.json"

    # ── 持久化 ──────────────────────────────────────────────

    def save_state(self):
        """保存校准状态到 JSON"""
        state = {
            'matrix': self.calibration_matrix.tolist(),
            'total_corrections': self.total_corrections
        }
        try:
            with open(self._calibration_path, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
            logger.info(f"✅ 校准状态已保存 ({self.total_corrections} 条校正)")
        except Exception as e:
            logger.warning(f"⚠️ 保存校准状态失败: {e}")

    def load_state(self) -> bool:
        """从 JSON 恢复校准状态"""
        if not self._calibration_path.exists():
            return False
        try:
            with open(self._calibration_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            self.calibration_matrix = np.array(state['matrix'], dtype=np.float32)
            self.total_corrections = state.get('total_corrections', 0)
            logger.info(f"✅ 校准状态已加载 ({self.total_corrections} 条校正)")
            return True
        except Exception as e:
            logger.warning(f"⚠️ 加载校准状态失败: {e}")
            return False

    # ── 从数据库加载反馈 ──────────────────────────────────

    def load_from_database(self):
        """从数据库 user_feedback 表加载所有校正记录"""
        if not self.db_manager:
            logger.warning("⚠️ db_manager 未设置，跳过数据库加载")
            return False

        try:
            conn = self.db_manager._get_conn()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT predicted_emotion, correct_emotion, feedback_type
                FROM user_feedback WHERE feedback_type = 'incorrect'
            ''')

            count = 0
            for row in cursor.fetchall():
                pred = row['predicted_emotion']
                correct = row['correct_emotion']
                if pred in EMOTION_ORDER and correct in EMOTION_ORDER:
                    pi = EMOTION_ORDER.index(pred)
                    ci = EMOTION_ORDER.index(correct)
                    self.calibration_matrix[pi][ci] += 1.0
                    count += 1

            # 合并之前持久化的状态（避免反复从数据库全量加载时丢失累积量）
            if self._calibration_path.exists():
                self.load_state()

            self.total_corrections = count
            logger.info(f"✅ 从数据库加载了 {count} 条校正记录")
            self.save_state()
            return True

        except Exception as e:
            logger.error(f"❌ 从数据库加载校正记录失败: {e}")
            return False

    # ── 在线更新（实时反馈） ──────────────────────────────

    def update_from_feedback(self, predicted: str, correct: str):
        """用户提交一条反馈时实时更新校准矩阵"""
        if predicted not in EMOTION_ORDER or correct not in EMOTION_ORDER:
            return

        pi = EMOTION_ORDER.index(predicted)
        ci = EMOTION_ORDER.index(correct)
        self.calibration_matrix[pi][ci] += 1.0
        self.total_corrections += 1

        logger.info(f"📝 在线更新校准: {predicted} → {correct}")
        self.save_state()

    # ── 核心校准方法 ──────────────────────────────────────

    def calibrate(self, scores: Dict[str, float]) -> Dict[str, float]:
        """
        对原始置信度分数进行校准

        策略:
        1. 将 scores dict 转为 7 维向量
        2. 与校准矩阵的转置相乘: calibrated = matrix^T · raw
        3. 归一化回总和为 1
        4. 对低强度预测（原始置信度 < 0.5）增强校准效果
        """
        if self.total_corrections < 3:
            # 数据量太少，直接返回原始分数
            return scores

        # 转为向量
        idx_map = {e: i for i, e in enumerate(EMOTION_ORDER)}
        raw = np.array([scores.get(e, 0.0) for e in EMOTION_ORDER], dtype=np.float32)

        # 计算校准强度系数：低强度预测增强校准
        max_conf = raw.max()
        calibration_strength = 0.3 if max_conf > 0.5 else 0.8

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

        logger.debug(f"📊 校准前后: {max(raw):.3f} → {max(calibrated):.3f}")
        return result

    def get_stats(self) -> Dict:
        """获取学习统计"""
        return {
            'total_corrections': self.total_corrections,
            'calibration_matrix': self.calibration_matrix.tolist(),
            'emotion_order': EMOTION_ORDER
        }
