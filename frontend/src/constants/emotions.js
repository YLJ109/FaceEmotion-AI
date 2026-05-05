/**
 * 情绪相关常量定义
 * 统一管理所有情绪映射、颜色、图标等数据
 */

// 情绪中文名称映射
export const EMOTION_NAMES = {
    happy: '开心',
    enjoy: '开心',      // enjoy 别名映射到 happy
    sad: '悲伤',
    angry: '愤怒',
    surprise: '惊讶',
    surprised: '惊讶',  // 兼容后端数据库
    fear: '恐惧',
    fearful: '恐惧',    // 兼容后端数据库
    disgust: '厌恶',
    disgusted: '厌恶',  // 兼容后端数据库
    neutral: '平静',
    calm: '平静'        // wav2vec2 模型标签
}

// 情绪 Emoji 图标映射
export const EMOTION_EMOJI = {
    happy: '😊',
    sad: '😢',
    angry: '😠',
    surprise: '😲',
    surprised: '😲',    // 兼容 surprised 标签
    fear: '😰',
    fearful: '😰',      // 兼容 fearful 标签
    disgust: '🤢',
    disgusted: '🤢',    // 兼容 disgusted 标签
    neutral: '😐',          // 平静表情（中性）
    calm: '😌'              // calm 表情
}

// 情绪颜色映射（与主题配色统一）
export const EMOTION_COLORS = {
    happy: '#26DE81',
    enjoy: '#26DE81',   // enjoy 使用 happy 的颜色
    sad: '#0ABDE3',
    angry: '#FF6348',
    surprise: '#E056FD',
    surprised: '#E056FD',  // 兼容后端数据库
    fear: '#9B59B6',       // 恐惧使用明亮的紫色
    fearful: '#9B59B6',    // 兼容后端数据库
    disgust: '#FFA502',
    disgusted: '#FFA502',  // 兼容后端数据库
    neutral: '#747D8C',
    calm: '#A4B0BE'        // calm 颜色（浅灰色）
}

// 情绪列表（用于遍历）
export const EMOTION_LIST = [
    'happy', 'sad', 'angry', 'surprise', 'surprised',
    'fear', 'fearful', 'disgust', 'neutral', 'calm'
]

// 情绪渐变色（用于进度条等）
export const EMOTION_GRADIENTS = {
    happy: ['#26DE81', '#20E3B2'],
    enjoy: ['#26DE81', '#20E3B2'],
    sad: ['#0ABDE3', '#48DBFB'],
    angry: ['#FF6348', '#FF7979'],
    surprise: ['#E056FD', '#BE2EDD'],
    surprised: ['#E056FD', '#BE2EDD'],
    fear: ['#2F3542', '#57606F'],
    fearful: ['#2F3542', '#57606F'],
    disgust: ['#FFA502', '#FFBE76'],
    disgusted: ['#FFA502', '#FFBE76'],
    neutral: ['#747D8C', '#A4B0BE'],
    calm: ['#A4B0BE', '#D1D8E0']
}

/**
 * 获取情绪的完整信息（名称 + Emoji + 颜色）
 * @param {string} emotion - 情绪标识
 * @returns {{ name: string, emoji: string, color: string }}
 */
export function getEmotionInfo(emotion) {
    return {
        name: EMOTION_NAMES[emotion] || emotion,
        emoji: EMOTION_EMOJI[emotion] || '',
        color: EMOTION_COLORS[emotion] || '#999'
    }
}

/**
 * 获取情绪中文名称
 * @param {string} emotion - 情绪标识
 * @returns {string}
 */
export function getEmotionName(emotion) {
    return EMOTION_NAMES[emotion] || emotion
}

/**
 * 获取情绪 Emoji 图标
 * @param {string} emotion - 情绪标识
 * @returns {string}
 */
export function getEmotionEmoji(emotion) {
    return EMOTION_EMOJI[emotion] || ''
}

/**
 * 获取情绪颜色
 * @param {string} emotion - 情绪标识
 * @returns {string}
 */
export function getEmotionColor(emotion) {
    return EMOTION_COLORS[emotion] || '#999'
}

/**
 * 获取情绪渐变色
 * @param {string} emotion - 情绪标识
 * @returns {string[]}
 */
export function getEmotionGradient(emotion) {
    return EMOTION_GRADIENTS[emotion] || ['#747D8C', '#A4B0BE']
}
