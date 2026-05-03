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
  neutral: '平静'
}

export const EMOTION_EMOJI = {
  happy: '😊',
  sad: '😢',
  angry: '😠',
  surprise: '😲',
  fear: '😨',
  disgust: '🤢',
  neutral: '😐'
}

export const EMOTION_LIST = ['happy', 'sad', 'angry', 'surprise', 'fear', 'disgust', 'neutral']

/** 情绪对应的颜色映射（与主题配色统一） */
export const EMOTION_COLORS = {
  happy: '#26DE81',
  enjoy: '#26DE81',  // enjoy 使用 happy 的颜色
  sad: '#0ABDE3',
  angry: '#FF6348',
  surprise: '#E056FD',
  surprised: '#E056FD',  // 兼容后端数据库
  fear: '#2F3542',
  fearful: '#2F3542',    // 兼容后端数据库
  disgust: '#FFA502',
  disgusted: '#FFA502',  // 兼容后端数据库
  neutral: '#747D8C'
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
