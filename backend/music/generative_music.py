"""
AI 生成式音乐引擎 - 基于情绪特征动态生成音乐参数
根据检测到的情绪类型、强度及组合特征，动态调整音乐的旋律、节奏、和声及音色。
"""
import random
import math
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# ── 情绪到音乐参数映射表 ──────────────────────────────

EMOTION_MUSIC_MAP = {
    'happy': {
        'mode': 'major',
        'bpm': 120,
        'root_note': 60,  # C4
        # C-F-G-F
        'chord_progression': [[60, 64, 67], [65, 69, 72], [67, 71, 74], [65, 69, 72]],
        'waveform': 'sine',
        'filter_cutoff': 2000,
        'reverb_mix': 0.3,
        'melody_complexity': 0.7,
    },
    'sad': {
        'mode': 'minor',
        'bpm': 70,
        'root_note': 48,  # C3
        # Am-Dm-Em-Dm
        'chord_progression': [[48, 51, 55], [53, 56, 60], [55, 58, 62], [53, 56, 60]],
        'waveform': 'triangle',
        'filter_cutoff': 1200,
        'reverb_mix': 0.6,
        'melody_complexity': 0.4,
    },
    'angry': {
        'mode': 'minor',
        'bpm': 140,
        'root_note': 43,  # G#2
        # G#m-Bm-C#m-Bm
        'chord_progression': [[43, 46, 50], [48, 51, 55], [50, 53, 57], [48, 51, 55]],
        'waveform': 'square',
        'filter_cutoff': 3000,
        'reverb_mix': 0.2,
        'melody_complexity': 0.8,
    },
    'surprise': {
        'mode': 'major',
        'bpm': 130,
        'root_note': 65,  # F4
        # F-C-G-F
        'chord_progression': [[65, 69, 72], [60, 64, 67], [67, 71, 74], [65, 69, 72]],
        'waveform': 'sawtooth',
        'filter_cutoff': 2500,
        'reverb_mix': 0.4,
        'melody_complexity': 0.9,
    },
    'fear': {
        'mode': 'minor',
        'bpm': 110,
        'root_note': 55,  # G3
        # Gm-Bb-C-Bb
        'chord_progression': [[55, 58, 62], [60, 63, 67], [62, 65, 69], [60, 63, 67]],
        'waveform': 'sine',
        'filter_cutoff': 1500,
        'reverb_mix': 0.5,
        'melody_complexity': 0.6,
    },
    'disgust': {
        'mode': 'minor',
        'bpm': 90,
        'root_note': 50,  # D#3
        # D#m-Fm-Gm-Fm
        'chord_progression': [[50, 53, 57], [55, 58, 62], [57, 60, 64], [55, 58, 62]],
        'waveform': 'triangle',
        'filter_cutoff': 1800,
        'reverb_mix': 0.35,
        'melody_complexity': 0.5,
    },
    'neutral': {
        'mode': 'major',
        'bpm': 100,
        'root_note': 57,  # A3
        # Am-Dm-Em-Dm
        'chord_progression': [[57, 61, 64], [62, 66, 69], [64, 68, 71], [62, 66, 69]],
        'waveform': 'sine',
        'filter_cutoff': 1800,
        'reverb_mix': 0.3,
        'melody_complexity': 0.5,
    },
}

# MIDI 音符到大调/小调音阶间隔
SCALE_INTERVALS = {
    'major': [0, 2, 4, 5, 7, 9, 11],   # 大调: 全全半全全全半
    'minor': [0, 2, 3, 5, 7, 8, 10],   # 自然小调: 全半全全半全全
}


class MusicGenerator:
    """AI 生成式音乐引擎"""

    def __init__(self):
        self._prev_params = None  # 用于平滑过渡
        self._transition_counter = 0

    def generate_music_params(self, scores: Dict[str, float]) -> Dict:
        """
        根据情绪分数生成音乐参数

        策略:
        1. 找到主导情绪和第二情绪
        2. 如果第二情绪置信度 > 0.3,混合两种情绪的音乐特征
        3. 生成旋律种子(基于音阶和和弦)
        4. 应用平滑过渡逻辑

        参数:
            scores: 情绪分数字典 {'happy': 0.8, 'sad': 0.1, ...}

        返回:
            音乐参数字典,包含 BPM、根音、旋律、音色等
        """
        if not scores or all(v == 0 for v in scores.values()):
            return self._get_default_params()

        # 排序情绪
        sorted_emotions = sorted(
            scores.items(), key=lambda x: x[1], reverse=True)
        dominant_emotion = sorted_emotions[0][0]
        dominant_score = sorted_emotions[0][1]

        # 获取基础参数
        base_params = EMOTION_MUSIC_MAP.get(
            dominant_emotion, EMOTION_MUSIC_MAP['neutral']).copy()

        # 混合第二情绪(如果置信度足够高)
        second_emotion = None
        second_score = 0
        if len(sorted_emotions) > 1 and sorted_emotions[1][1] > 0.3:
            second_emotion = sorted_emotions[1][0]
            second_score = sorted_emotions[1][1]
            second_params = EMOTION_MUSIC_MAP.get(
                second_emotion, EMOTION_MUSIC_MAP['neutral'])

            # 计算混合比例
            total_score = dominant_score + second_score
            mix_ratio = second_score / total_score

            # 混合音乐参数
            base_params = self._blend_params(
                base_params, second_params, mix_ratio)
            logger.debug(
                f"🎵 混合情绪: {dominant_emotion}({dominant_score:.2f}) + {second_emotion}({second_score:.2f}), 混合比={mix_ratio:.2f}")

        # 生成旋律种子
        melody = self._generate_melody(
            base_params['chord_progression'],
            base_params['mode'],
            base_params['melody_complexity'],
            dominant_score
        )

        # 构建返回参数
        music_params = {
            'emotion': dominant_emotion,
            'confidence': dominant_score,
            'bpm': int(base_params['bpm']),
            'root_note': int(base_params['root_note']),
            'mode': base_params['mode'],
            'melody': melody,
            'waveform': base_params['waveform'],
            'filter_cutoff': int(base_params['filter_cutoff']),
            'reverb_mix': round(base_params['reverb_mix'], 2),
            # 限制音量范围 0.3-1.0
            'volume': min(1.0, max(0.3, dominant_score * 1.2)),
            'chord_index': 0,  # 当前和弦索引(用于循环播放)
        }

        # 平滑过渡处理
        if self._prev_params:
            music_params = self._apply_smoothing(
                music_params, self._prev_params)

        self._prev_params = music_params.copy()
        logger.debug(
            f"🎼 生成音乐参数: {dominant_emotion}, BPM={music_params['bpm']}, 旋律长度={len(melody)}")

        return music_params

    def _blend_params(self, params1: Dict, params2: Dict, ratio: float) -> Dict:
        """混合两个音乐参数集"""
        blended = params1.copy()

        # 数值型参数线性插值
        for key in ['bpm', 'root_note', 'filter_cutoff', 'reverb_mix', 'melody_complexity']:
            if key in params1 and key in params2:
                blended[key] = params1[key] * \
                    (1 - ratio) + params2[key] * ratio

        # 波形选择:使用主导情绪的波形
        # 和弦进行:保持第一个的

        return blended

    def _generate_melody(self, chord_progression: List[List[int]], mode: str,
                         complexity: float, confidence: float) -> List[int]:
        """
        基于和弦进行生成旋律种子

        策略:
        1. 从当前和弦的音符中选择旋律音
        2. 根据复杂度决定音符数量(4-12个)
        3. 添加音阶内的经过音
        4. 根据置信度调整旋律活跃度

        参数:
            chord_progression: 和弦进行列表 [[60,64,67], ...]
            mode: 调式 ('major' 或 'minor')
            complexity: 复杂度 (0.0-1.0)
            confidence: 情绪置信度 (0.0-1.0)

        返回:
            MIDI 音符序列
        """
        scale_intervals = SCALE_INTERVALS.get(mode, SCALE_INTERVALS['major'])
        num_notes = int(4 + complexity * 8)  # 4-12 个音符
        melody = []

        for i in range(num_notes):
            # 选择和弦(循环使用和弦进行)
            chord_idx = i % len(chord_progression)
            chord = chord_progression[chord_idx]

            # 70% 概率使用和弦内音,30% 概率使用音阶经过音
            if random.random() < 0.7 or not chord:
                # 使用和弦内音
                note = random.choice(chord)
            else:
                # 使用音阶经过音
                root = chord[0] if chord else 60
                interval = random.choice(scale_intervals)
                octave_offset = random.choice([0, 12, -12])  # 可能跨八度
                note = root + interval + octave_offset

            # 根据置信度微调音符(高置信度时更活跃)
            if confidence > 0.7 and random.random() < 0.3:
                note += random.choice([2, -2, 5, -5])  # 添加装饰音

            melody.append(note)

        return melody

    def _apply_smoothing(self, new_params: Dict, old_params: Dict) -> Dict:
        """
        应用平滑过渡逻辑

        策略:
        1. BPM 渐变(每次最多变化 ±10)
        2. 音量渐变(避免突变)
        3. 滤波器截止频率渐变
        4. 混响混合比渐变

        参数:
            new_params: 新生成的音乐参数
            old_params: 上一帧的音乐参数

        返回:
            平滑后的音乐参数
        """
        smoothed = new_params.copy()

        # BPM 平滑(每次最多变化 ±10)
        bpm_diff = new_params['bpm'] - old_params['bpm']
        if abs(bpm_diff) > 10:
            smoothed['bpm'] = old_params['bpm'] + (10 if bpm_diff > 0 else -10)

        # 音量平滑(每次最多变化 ±0.1)
        vol_diff = new_params['volume'] - old_params['volume']
        if abs(vol_diff) > 0.1:
            smoothed['volume'] = old_params['volume'] + \
                (0.1 if vol_diff > 0 else -0.1)

        # 滤波器截止频率平滑(每次最多变化 ±300Hz)
        cutoff_diff = new_params['filter_cutoff'] - old_params['filter_cutoff']
        if abs(cutoff_diff) > 300:
            smoothed['filter_cutoff'] = old_params['filter_cutoff'] + \
                (300 if cutoff_diff > 0 else -300)

        # 混响混合比平滑(每次最多变化 ±0.1)
        reverb_diff = new_params['reverb_mix'] - old_params['reverb_mix']
        if abs(reverb_diff) > 0.1:
            smoothed['reverb_mix'] = old_params['reverb_mix'] + \
                (0.1 if reverb_diff > 0 else -0.1)

        return smoothed

    def _get_default_params(self) -> Dict:
        """返回默认音乐参数(中性情绪)"""
        return {
            'emotion': 'neutral',
            'confidence': 0.5,
            'bpm': 100,
            'root_note': 57,
            'mode': 'major',
            'melody': [57, 62, 64, 62, 57, 60, 62, 60],
            'waveform': 'sine',
            'filter_cutoff': 1800,
            'reverb_mix': 0.3,
            'volume': 0.5,
            'chord_index': 0,
        }

    def reset_state(self):
        """重置状态(用于会话重新开始)"""
        self._prev_params = None
        self._transition_counter = 0
        logger.info("🔄 音乐引擎状态已重置")
