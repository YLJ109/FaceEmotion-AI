/**
 * 情绪常量定义
 * 统一管理情绪相关的配置和映射
 */

// 情绪键名（与后端 core/constants.py EMOTION_NAMES 严格一致）
export const EMOTION_KEYS = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

// 情绪中文名映射
export const EMOTION_NAME_MAP = {
  angry: '愤怒',
  disgust: '厌恶',
  fear: '恐惧',
  happy: '开心',
  neutral: '平静',
  sad: '悲伤',
  surprise: '惊讶'
}

// 情绪图标映射（使用emoji）
export const EMOTION_EMOJI_MAP = {
  angry: '😠',
  disgust: '🤢',
  fear: '😨',
  happy: '😊',
  neutral: '😐',
  sad: '😢',
  surprise: '😮'
}

// 情绪颜色映射（主题色）
export const EMOTION_COLOR_MAP = {
  angry: '#EF4444',    // 红色
  disgust: '#F59E0B',  // 橙色
  fear: '#9333EA',     // 深紫色
  happy: '#10B981',    // 绿色
  neutral: '#6B7280',  // 灰色
  sad: '#3B82F6',      // 蓝色
  surprise: '#8B5CF6'  // 紫色
}

// 情绪颜色十六进制数组（用于图表，顺序与 EMOTION_KEYS 一致）
export const EMOTION_COLORS = [
  '#EF4444',  // angry - 红色
  '#F59E0B',  // disgust - 橙色
  '#9333EA',  // fear - 深紫色
  '#10B981',  // happy - 绿色
  '#6B7280',  // neutral - 灰色
  '#3B82F6',  // sad - 蓝色
  '#8B5CF6'   // surprise - 紫色
]

// 兼容性导出 - 保持与旧代码的兼容性
export const EMOTION_NAMES = EMOTION_KEYS
export const EMOTION_EMOJI = EMOTION_EMOJI_MAP
export const EMOTION_LIST = EMOTION_KEYS.map(key => ({
  key,
  name: EMOTION_NAME_MAP[key],
  emoji: EMOTION_EMOJI_MAP[key],
  color: EMOTION_COLOR_MAP[key]
}))

// 获取情绪名称（中文）
export function getEmotionName(key) {
  return EMOTION_NAME_MAP[key] || key
}

// 获取情绪图标
export function getEmotionEmoji(key) {
  return EMOTION_EMOJI_MAP[key] || '😐'
}

// 获取情绪颜色
export function getEmotionColor(key) {
  return EMOTION_COLOR_MAP[key] || '#6B7280'
}

// 获取情绪索引
export function getEmotionIndex(key) {
  return EMOTION_KEYS.indexOf(key)
}

// 获取所有情绪名称列表
export function getEmotionNames() {
  return EMOTION_KEYS.map(key => EMOTION_NAME_MAP[key])
}

// 获取情绪完整信息
export function getEmotionInfo(key) {
  return {
    key,
    name: EMOTION_NAME_MAP[key] || key,
    emoji: EMOTION_EMOJI_MAP[key] || '😐',
    color: EMOTION_COLOR_MAP[key] || '#6B7280'
  }
}

// 获取情绪渐变颜色
export function getEmotionGradient(key, direction = 'to bottom') {
  const color = EMOTION_COLOR_MAP[key] || '#6B7280'
  return `linear-gradient(${direction}, ${color}, ${adjustBrightness(color, -30)})`
}

// 辅助函数：调整颜色亮度
function adjustBrightness(hex, percent) {
  const num = parseInt(hex.replace('#', ''), 16)
  const amt = Math.round(2.55 * percent)
  const R = Math.min(255, Math.max(0, (num >> 16) + amt))
  const G = Math.min(255, Math.max(0, ((num >> 8) & 0x00ff) + amt))
  const B = Math.min(255, Math.max(0, (num & 0x0000ff) + amt))
  return `#${((1 << 24) + (R << 16) + (G << 8) + B).toString(16).slice(1)}`
}
