"""
AI 语音情绪识别 - wav2vec2 预训练模型版本
使用 HuggingFace Transformers 库的预训练模型进行高精度语音情绪识别

工作流程:
1. 前端通过 WebSocket 发送 PCM16 音频数据
2. 后端累积音频并转换为 numpy array
3. wav2vec2-large-robust 模型进行情绪分类
4. 返回 7 种情绪的分数分布
"""
from transformers import pipeline
import logging
import numpy as np
from typing import Dict, List
import os

# 抑制 transformers 库的警告和加载报告
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'


logger = logging.getLogger(__name__)

# ── 情绪映射 ──────────────────────────────────

# 模型输出的英文标签 → 中文情绪
EMOTION_MAP = {
    'angry': '愤怒',
    'calm': '平静',
    'disgust': '厌恶',
    'fearful': '恐惧',
    'happy': '开心',
    'sad': '悲伤',
    'neutral': '平静',  # ✅ 合并: neutral 映射到平静
    'surprised': '惊讶',
}

# 英文标签 → 系统内部标签（7种情绪）
EMOTION_LABEL_MAP = {
    'angry': 'angry',
    'calm': 'neutral',      # ✅ 合并: calm 映射到 neutral
    'disgust': 'disgust',
    'fearful': 'fearful',
    'happy': 'happy',
    'sad': 'sad',
    'neutral': 'neutral',   # ✅ 保留: neutral
    'surprised': 'surprised',
}


class Wav2Vec2VoiceAnalyzer:
    """
    基于 wav2vec2 的语音情绪分析器

    使用 audeering/wav2vec2-large-robust-12-ft-emotion-msp-dim 预训练模型
    该模型在 MSP-Podcast 数据集上微调，能识别 7 种情绪
    """

    def __init__(self):
        self._pipeline = None
        self._model_loaded = False
        self._sample_rate = 16000
        self._audio_buffer = []  # 累积音频样本

    def _load_model(self):
        """加载本地预训练模型（懒加载）"""
        if not self._model_loaded:
            try:
                # 使用本地模型路径
                model_path = "d:/front-back/FaceEmotion-AI/wav2vac2"

                logger.info(f"正在加载 wav2vec2 模型...")

                self._pipeline = pipeline(
                    "audio-classification",
                    model=model_path,
                    local_files_only=True
                )

                self._model_loaded = True
                logger.info("wav2vec2 模型加载成功")

            except Exception as e:
                logger.error(f" 模型加载失败: {e}")
                print(f"❌ 模型加载失败: {e}")
                raise

    def _pcm16_to_float(self, data: bytes) -> np.ndarray:
        """PCM16 小端字节序 → float32 [-1, 1]"""
        import struct
        count = len(data) // 2
        ints = struct.unpack(f'<{count}h', data[:count * 2])
        return np.array(ints, dtype=np.float32) / 32768.0

    def add_audio_chunk(self, audio_data: bytes):
        """
        添加音频数据块到缓冲区

        参数:
            audio_data: PCM16 原始字节
        """
        samples = self._pcm16_to_float(audio_data)
        self._audio_buffer.extend(samples.tolist())

    def get_audio_energy(self) -> float:
        """
        计算音频能量（用于检测是否有有效语音）

        返回:
            能量值 (0-1)，值越高表示声音越大
        """
        if len(self._audio_buffer) == 0:
            return 0.0

        audio_array = np.array(self._audio_buffer, dtype=np.float32)
        # 计算 RMS 能量
        energy = np.sqrt(np.mean(audio_array ** 2))
        return min(1.0, energy * 5.0)  # 归一化到 0-1

    def clear_buffer(self):
        """清空音频缓冲区"""
        self._audio_buffer = []

    def predict_emotion(self) -> Dict[str, float]:
        """
        使用当前缓冲区中的音频进行情绪识别

        返回:
            8 种情绪的分数分布 {emotion: score}
        """
        if len(self._audio_buffer) == 0:
            # 返回默认分布
            return self._default_distribution()

        # 转换为 numpy array
        audio_array = np.array(self._audio_buffer, dtype=np.float32)

        # 至少需要 1 秒音频 (16000 样本)
        if len(audio_array) < 16000:
            return self._default_distribution()

        try:
            # 加载模型（如果还没加载）
            self._load_model()

            # 使用模型进行预测
            import time
            start_time = time.time()

            results = self._pipeline(
                audio_array, sampling_rate=self._sample_rate)

            inference_time = time.time() - start_time

            # ✅ 新增: 应用温度调节增强分数差异（使模型输出更锐利）
            temperature = 0.5  # 温度越低，差异越明显
            raw_scores = {item['label']: item['score'] for item in results}

            # 应用温度调节
            exp_scores = {k: np.exp(v / temperature)
                          for k, v in raw_scores.items()}
            sum_exp = sum(exp_scores.values())
            normalized_scores = {k: v / sum_exp for k, v in exp_scores.items()}

            # 转换为系统使用的格式
            emotion_scores = {}
            for label, score in normalized_scores.items():
                # 映射到系统标签（calm -> neutral）
                system_label = EMOTION_LABEL_MAP.get(label, 'neutral')

                # 如果已存在（如 calm 和 neutral 都映射到 neutral），累加分数
                if system_label in emotion_scores:
                    emotion_scores[system_label] += score
                else:
                    emotion_scores[system_label] = score

            # 确保所有 7 种情绪都有分数
            all_emotions = ['happy', 'sad', 'angry',
                            'surprised', 'fearful', 'disgust', 'neutral']
            for emotion in all_emotions:
                if emotion not in emotion_scores:
                    emotion_scores[emotion] = 0.0

            # 清空缓冲区（为下一次分析准备）
            self.clear_buffer()

            return emotion_scores

        except Exception as e:
            logger.error(f"❌ 语音情绪识别失败: {e}")
            import traceback
            traceback.print_exc()

            # 发生错误时清空缓冲区并返回默认分布
            self.clear_buffer()
            return self._default_distribution()

    def _default_distribution(self) -> Dict[str, float]:
        """返回默认情绪分布（平静主导）

        ✅ 修复: 使用 7 种情绪（不含 calm，合并到 neutral）
        """
        return {
            'happy': 0.05,
            'sad': 0.05,
            'angry': 0.05,
            'surprised': 0.05,
            'fearful': 0.05,
            'disgust': 0.05,
            'neutral': 0.70,  # ✅ 修复: calm 合并到 neutral，提高权重
        }

    def fuse_scores(self, face_scores: Dict[str, float],
                    voice_scores: Dict[str, float],
                    voice_weight: float = 0.4) -> Dict[str, float]:
        """
        融合人脸和语音分数

        参数:
            face_scores:  视觉情感分数
            voice_scores: 语音情感分数
            voice_weight: 语音权重 (有麦克风时启用)

        融合策略:
            final = (1 - voice_weight) * face + voice_weight * voice

        ✅ 新增: wav2vec2 版本的多模态融合
        """
        has_voice = any(v > 0 for v in voice_scores.values())
        if not has_voice:
            return face_scores

        # ✅ 修复: 使用 7 种情绪（不含 calm，合并到 neutral）
        wav2vec2_emotions = ['happy', 'sad', 'angry',
                             'surprised', 'fearful', 'disgust', 'neutral']

        fused = {}
        for emotion in wav2vec2_emotions:
            f = face_scores.get(emotion, 0)
            v = voice_scores.get(emotion, 0)
            fused[emotion] = (1 - voice_weight) * f + voice_weight * v

        return fused
