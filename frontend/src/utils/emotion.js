/**
 * 共享情绪常量 - 统一管理所有情绪相关数据
 * 避免在多个组件中重复定义
 */

export const EMOTION_NAMES = {
  happy: '开心',
  enjoy: '开心',  // enjoy 别名映射到 happy
  sad: '悲伤',
  angry: '愤怒',
  surprise: '惊讶',
  surprised: '惊讶',  // 兼容后端数据库
  fear: '恐惧',
  fearful: '恐惧',    // 兼容后端数据库
  disgust: '厌恶',
  disgusted: '厌恶',  // 兼容后端数据库
  neutral: '平静',
  calm: '平静'        // ✅ 新增: wav2vec2 模型标签
}

export const EMOTION_EMOJI = {
  happy: '😊',
  sad: '😢',
  angry: '😠',
  surprise: '😲',
  surprised: '😲',  // ✅ 新增: 兼容 surprised 标签
  fear: '',
  fearful: '😨',    // ✅ 新增: 兼容 fearful 标签
  disgust: '🤢',
  disgusted: '🤢',  // ✅ 新增: 兼容 disgusted 标签
  neutral: '',
  calm: '😌'        // ✅ 新增: calm 表情
}

export const EMOTION_LIST = ['happy', 'sad', 'angry', 'surprise', 'surprised', 'fear', 'fearful', 'disgust', 'neutral']

/** 情绪对应的颜色映射（与主题配色统一） */
export const EMOTION_COLORS = {
  happy: '#26DE81',
  enjoy: '#26DE81',  // enjoy 使用 happy 的颜色
  sad: '#0ABDE3',
  angry: '#FF6348',
  surprise: '#E056FD',
  surprised: '#E056FD',  // 兼容后端数据库
  fear: '#9B59B6',        // ✅ 修复: 恐惧颜色从深灰改为明亮的紫色
  fearful: '#9B59B6',     // 兼容后端数据库
  disgust: '#FFA502',
  disgusted: '#FFA502',   // 兼容后端数据库
  neutral: '#747D8C',
  calm: '#A4B0BE'         // ✅ 新增: calm 颜色（浅灰色）
}

export function getEmotionName(emotion) {
  return EMOTION_NAMES[emotion] || emotion
}

export function getEmotionEmoji(emotion) {
  return EMOTION_EMOJI[emotion] || ''
}

export function getEmotionColor(emotion) {
  return EMOTION_COLORS[emotion] || '#999'
}
