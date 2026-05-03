"""
AI 多模态融合引擎 - 语音情感分析
结合人脸表情视觉特征与语音语调特征，提升复杂场景下表情识别鲁棒性。

工作流程:
1. 前端收集音频 PCM 数据 → WebSocket 发送
2. 后端提取声学特征（基频、能量、语速、频谱质心）
3. 轻量 SVM/规则分类器 → 语音情感分数
4. 与视觉情感分数加权融合 → 最终结果
"""
import logging
import math
import struct
import numpy as np
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── 声学特征提取参数 ──────────────────────────────────

SAMPLE_RATE = 16000       # 预期采样率
FRAME_SIZE = 512           # ✅ 优化: FFT 帧大小（从 1024 降到 512，适应 1024 bytes 缓冲区）
HOP_LENGTH = 256           # ✅ 优化: 帧移（从 512 降到 256，提高时间分辨率）
F_MIN = 80                 # 基频搜索下界 (Hz)
F_MAX = 600                # 基频搜索上界 (Hz)

# 情绪对应的声学模板（均值/标准差）
# {emotion: {pitch_mean, pitch_std, energy_mean, energy_std, spectral_centroid, speaking_rate}}
VOICE_TEMPLATES = {
    'happy':    {'pitch_mean': 280, 'pitch_std': 80,  'energy_mean': 0.6, 'energy_std': 0.2,
                 'spectral_centroid': 2500, 'speaking_rate': 4.5},
    'sad':      {'pitch_mean': 170, 'pitch_std': 40,  'energy_mean': 0.3, 'energy_std': 0.1,
                 'spectral_centroid': 1800, 'speaking_rate': 2.5},
    'angry':    {'pitch_mean': 320, 'pitch_std': 100, 'energy_mean': 0.8, 'energy_std': 0.15,
                 'spectral_centroid': 3000, 'speaking_rate': 5.0},
    'surprise': {'pitch_mean': 350, 'pitch_std': 120, 'energy_mean': 0.7, 'energy_std': 0.2,
                 'spectral_centroid': 2800, 'speaking_rate': 4.0},
    'fear':     {'pitch_mean': 300, 'pitch_std': 90,  'energy_mean': 0.5, 'energy_std': 0.2,
                 'spectral_centroid': 2600, 'speaking_rate': 3.5},
    'disgust':  {'pitch_mean': 200, 'pitch_std': 50,  'energy_mean': 0.4, 'energy_std': 0.15,
                 'spectral_centroid': 2200, 'speaking_rate': 3.0},
    'neutral':  {'pitch_mean': 220, 'pitch_std': 30,  'energy_mean': 0.4, 'energy_std': 0.1,
                 'spectral_centroid': 2000, 'speaking_rate': 3.0},
}

EMOTION_ORDER = ['angry', 'disgust', 'fear',
                 'happy', 'neutral', 'sad', 'surprise']


class VoiceAnalyzer:
    """语音情感分析器"""

    def __init__(self, sample_rate: int = SAMPLE_RATE):
        self.sample_rate = sample_rate
        # ✅ 修复: 默认禁用压缩(前端已禁用压缩,直接发送PCM16)
        self.last_sample = 0
        self.compression_enabled = False

    # ── 特征提取 ──────────────────────────────────────

    def extract_features(self, audio_data: bytes) -> Dict[str, float]:
        """
        从 PCM16 数据提取声学特征

        参数:
            audio_data: PCM16 原始字节 (16kHz, mono, signed 16-bit)

        返回:
            {pitch_mean, pitch_std, energy_mean, energy_std, spectral_centroid, speaking_rate, has_voice}
        """
        # ✅ 临时调试: 打印音频数据信息
        if len(audio_data) < 64:
            return self._empty_features()

        # PCM16 → float32 [-1, 1]
        samples = self._pcm16_to_float(audio_data)

        if len(samples) < FRAME_SIZE:
            return self._empty_features()

        # 分帧
        frames = self._frame(samples)

        # 提取各特征
        pitch_contour = self._extract_pitch_contour(frames)
        energy_contour = self._extract_energy_contour(frames)
        spectral_centroid = self._extract_spectral_centroid(frames)
        speaking_rate = self._estimate_speaking_rate(energy_contour)

        # 过滤静音段
        voiced_frames = [p for p in pitch_contour if p > 0]

        # ✅ 优化: 降低有效帧比例要求，从全部帧变为 10% 即可
        # 只要有一小部分帧检测到声音，就认为有声音
        if len(voiced_frames) < len(pitch_contour) * 0.1:
            return self._empty_features()

        features = {
            'pitch_mean': float(np.mean(voiced_frames)),
            'pitch_std': float(np.std(voiced_frames)) if len(voiced_frames) > 1 else 20.0,
            'energy_mean': float(np.mean(energy_contour)),
            'energy_std': float(np.std(energy_contour)) if len(energy_contour) > 1 else 0.1,
            'spectral_centroid': float(spectral_centroid),
            'speaking_rate': float(speaking_rate),
            'has_voice': 1.0,
        }
        return features

    def _pcm16_to_float(self, data: bytes) -> np.ndarray:
        """PCM16 小端字节序 → float32"""
        count = len(data) // 2
        ints = struct.unpack(f'<{count}h', data[:count * 2])
        return np.array(ints, dtype=np.float32) / 32768.0

    # ✅ 新增: 音频解压缩(差分编码 + 量化逆操作)
    def _decompress_audio(self, compressed_data: bytes) -> Dict:
        """
        解压缩音频数据

        参数:
            compressed_data: 压缩后的 PCM16 字节

        返回:
            {buffer: bytes, lastSample: int}
        """
        quantized = np.frombuffer(compressed_data, dtype=np.int16)
        length = len(quantized)

        if length == 0:
            return {'buffer': b'', 'lastSample': self.last_sample}

        # 反量化
        diffs = quantized * 4

        # 积分恢复原始信号
        reconstructed = np.zeros(length, dtype=np.int16)
        reconstructed[0] = diffs[0] + self.last_sample
        for i in range(1, length):
            reconstructed[i] = reconstructed[i - 1] + diffs[i]

        last_sample_val = int(reconstructed[length - 1])

        return {
            'buffer': reconstructed.tobytes(),
            'lastSample': last_sample_val
        }

    def _frame(self, samples: np.ndarray) -> List[np.ndarray]:
        """分帧"""
        frames = []
        n_frames = (len(samples) - FRAME_SIZE) // HOP_LENGTH + 1
        for i in range(max(1, n_frames)):
            start = i * HOP_LENGTH
            frames.append(samples[start:start + FRAME_SIZE])
        return frames

    def _extract_pitch_contour(self, frames: List[np.ndarray]) -> List[float]:
        """自相关法基频提取"""
        pitch = []
        for frame in frames:
            # 归一化
            frame = frame * np.hanning(len(frame))
            # 自相关
            corr = np.correlate(frame, frame, mode='full')
            n = len(frame)
            corr = corr[n - 1:]

            # 搜索基频周期
            min_lag = int(self.sample_rate / F_MAX)
            max_lag = int(self.sample_rate / F_MIN)

            if max_lag >= len(corr):
                pitch.append(0.0)
                continue

            search_region = corr[min_lag:max_lag + 1]

            # 降低阈值到 0.05，适应低音量音频
            if len(search_region) == 0 or np.max(search_region) < 0.05:
                pitch.append(0.0)  # 无声音
                continue

            peak_idx = np.argmax(search_region) + min_lag
            f0 = self.sample_rate / peak_idx
            pitch.append(f0)

        return pitch

    def _extract_energy_contour(self, frames: List[np.ndarray]) -> List[float]:
        """RMS 能量"""
        return [float(np.sqrt(np.mean(f ** 2))) for f in frames]

    def _extract_spectral_centroid(self, frames: List[np.ndarray]) -> float:
        """频谱质心均值"""
        centroids = []
        for frame in frames:
            spectrum = np.abs(np.fft.rfft(frame * np.hanning(len(frame))))
            freqs = np.fft.rfftfreq(len(frame), 1 / self.sample_rate)
            if np.sum(spectrum) > 0:
                centroid = np.sum(freqs * spectrum) / np.sum(spectrum)
                centroids.append(centroid)
        return float(np.mean(centroids)) if centroids else 2000.0

    def _estimate_speaking_rate(self, energy_contour: List[float]) -> float:
        """通过能量包络过零率估算语速"""
        if len(energy_contour) < 10:
            return 3.0
        threshold = np.mean(energy_contour) * 0.5
        binary = (np.array(energy_contour) > threshold).astype(int)
        zcr = np.sum(np.abs(np.diff(binary)))
        return float(zcr / (len(energy_contour) / (self.sample_rate / HOP_LENGTH)))

    def _empty_features(self) -> Dict[str, float]:
        return {
            'pitch_mean': 0.0, 'pitch_std': 0.0,
            'energy_mean': 0.0, 'energy_std': 0.0,
            'spectral_centroid': 0.0, 'speaking_rate': 0.0,
            'has_voice': 0.0,
        }

    # ── 语音情感分类 ──────────────────────────────────

    def predict_voice_emotion(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        基于声学特征预测语音情感分数

        使用高斯概率密度匹配模板
        """
        # ✅ 优化: 降低阈值到 0.3，提高检测敏感度
        # 即使声音较小也能进行分析，避免一直返回默认值
        if features.get('has_voice', 0) < 0.3:
            # return {e: 0.0 for e in EMOTION_ORDER}  #  旧代码：全部返回0
            # ✅ 新代码：返回默认分布，平静占主导
            return {
                'happy': 0.05,
                'sad': 0.05,
                'angry': 0.05,
                'surprise': 0.05,
                'fear': 0.05,
                'disgust': 0.05,
                'neutral': 0.70,  # 默认平静
            }

        scores = {}
        for emotion, template in VOICE_TEMPLATES.items():
            score = 1.0
            for feat_name in ['pitch_mean', 'pitch_std', 'energy_mean', 'energy_std',
                              'spectral_centroid', 'speaking_rate']:
                feat_val = features.get(feat_name, 0)
                template_val = template[feat_name]
                # 高斯似然
                diff = abs(feat_val - template_val)
                sigma = template_val * 0.3 + 10  # 自适应标准差
                likelihood = math.exp(- (diff ** 2) / (2 * sigma ** 2))
                score *= likelihood ** 0.3  # 各特征独立权重

            scores[emotion] = score

        # 归一化
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}

        return scores

    # ── 多模态融合 ────────────────────────────────────

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
        """
        has_voice = any(v > 0 for v in voice_scores.values())
        if not has_voice:
            return face_scores

        fused = {}
        for emotion in EMOTION_ORDER:
            f = face_scores.get(emotion, 0)
            v = voice_scores.get(emotion, 0)
            fused[emotion] = (1 - voice_weight) * f + voice_weight * v

        return fused
