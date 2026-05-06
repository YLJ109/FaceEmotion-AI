"""
AI情感检测系统 - 共享常量
"""

import logging

# 情绪类别名称
EMOTION_NAMES = ['angry', 'disgust', 'fear',
                 'happy', 'neutral', 'sad', 'surprise']

# 情绪中文名称
EMOTION_CHINESE = {
    'angry': '愤怒',
    'disgust': '厌恶',
    'fear': '恐惧',
    'happy': '开心',
    'neutral': '平静',
    'sad': '悲伤',
    'surprise': '惊讶'
}

# 情绪颜色 (BGR) — 与前端的 EMOTION_COLORS 保持一致
EMOTION_COLORS = {
    'angry': (72, 99, 255),     # #FF6348 火焰红
    'disgust': (2, 165, 255),   # #FFA502 阳光橙
    'fear': (66, 53, 47),       # #2F3542 迷雾灰
    'happy': (129, 222, 38),    # #26DE81 森林绿
    'neutral': (140, 125, 116),  # 747D8C 禅意灰
    'sad': (227, 189, 10),      # #0ABDE3 雨天蓝
    'surprise': (253, 86, 224),  # E056FD 银河紫
}

# 允许上传的文件类型
ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
ALLOWED_VIDEO_TYPES = {'video/mp4', 'video/avi', 'video/quicktime'}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB

# 日志配置
LOGGING_CONFIG = {
    'level': logging.INFO,  # 默认 INFO 级别
    'format': '%(asctime)s | %(levelname)-7s | %(name)s - %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S',
}
