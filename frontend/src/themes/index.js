/**
 * 十种精美主题配置
 * 7种表情主题 + 3个特殊主题（守望先锋/赛博朋克/极简）
 * 参考优秀UI设计：Dribbble, Behance, Material Design
 */

// ==================== 7种表情主题 ====================

// 😊 开心 - 森林绿（自然活力）
export const sunny = {
    name: 'Sunny',
    emotion: 'happy',
    emoji: '😊',
    primary: '#2ED573',
    secondary: '#7BED9F',
    accent: '#1E90FF',
    highlight: '#26DE81',
    background: 'linear-gradient(135deg, #E8F8F5 0%, #D5F5E3 100%)',
    // ✅ 每个主题使用不同的卡片背景色，确保导航栏和侧边栏有独特颜色
    card_bg: 'rgba(232, 248, 245, 0.9)',
    text: '#2D3436',
    text_secondary: '#636E72',
    border: '#ABEBC6',
    success: '#2ED573',
    warning: '#F7DC6F',
    error: '#EC7063',
    gradient: 'linear-gradient(135deg, #2ED573 0%, #26DE81 50%, #7BED9F 100%)',
    shadow: '0 8px 32px rgba(46, 213, 115, 0.25)',
    glow: '0 0 20px rgba(46, 213, 115, 0.5)'
}

// 😢 悲伤 - 雨天蓝（忧郁沉静）
export const rainy = {
    name: 'Rainy',
    emotion: 'sad',
    emoji: '😢',
    primary: '#54A0FF',
    secondary: '#2E86DE',
    accent: '#48DBFB',
    highlight: '#0ABDE3',
    background: 'linear-gradient(135deg, #E8F4FD 0%, #D6EAF8 100%)',
    // ✅ 雨天蓝色卡片背景
    card_bg: 'rgba(232, 244, 253, 0.9)',
    text: '#2C3E50',
    text_secondary: '#5D6D7E',
    border: '#AED6F1',
    success: '#58D68D',
    warning: '#F7DC6F',
    error: '#EC7063',
    gradient: 'linear-gradient(135deg, #54A0FF 0%, #2E86DE 50%, #48DBFB 100%)',
    shadow: '0 8px 32px rgba(84, 160, 255, 0.25)',
    glow: '0 0 20px rgba(84, 160, 255, 0.5)'
}

// 😠 愤怒 - 火焰红（激情能量）
export const fire = {
    name: 'Fire',
    emotion: 'angry',
    emoji: '😠',
    primary: '#FF4757',
    secondary: '#FF6B81',
    accent: '#FFA502',
    highlight: '#FF6348',
    background: 'linear-gradient(135deg, #FFE5E5 0%, #FFD6D6 100%)',
    // ✅ 火焰红卡片背景
    card_bg: 'rgba(255, 229, 229, 0.9)',
    text: '#2F3542',
    text_secondary: '#57606F',
    border: '#FFC3C3',
    success: '#7BED9F',
    warning: '#FFA502',
    error: '#FF4757',
    gradient: 'linear-gradient(135deg, #FF4757 0%, #FF6348 50%, #FFA502 100%)',
    shadow: '0 8px 32px rgba(255, 71, 87, 0.3)',
    glow: '0 0 25px rgba(255, 71, 87, 0.6)'
}

// 😲 惊讶 - 银河紫（神秘奇幻）
export const galaxy = {
    name: 'Galaxy',
    emotion: 'surprise',
    emoji: '😲',
    primary: '#A55EEA',
    secondary: '#8854D0',
    accent: '#FD79A8',
    highlight: '#E056FD',
    background: 'linear-gradient(135deg, #F3E5F5 0%, #E1D5E7 100%)',
    // ✅ 银河紫卡片背景
    card_bg: 'rgba(243, 229, 245, 0.9)',
    text: '#2D3436',
    text_secondary: '#636E72',
    border: '#D7BDE2',
    success: '#58D68D',
    warning: '#F7DC6F',
    error: '#EC7063',
    gradient: 'linear-gradient(135deg, #A55EEA 0%, #E056FD 50%, #FD79A8 100%)',
    shadow: '0 8px 32px rgba(165, 94, 234, 0.3)',
    glow: '0 0 25px rgba(165, 94, 234, 0.6)'
}

// 😨 恐惧 - 迷雾灰（朦胧紧张）
export const mist = {
    name: 'Mist',
    emotion: 'fear',
    emoji: '😨',
    primary: '#747D8C',
    secondary: '#A4B0BE',
    accent: '#57606F',
    highlight: '#2F3542',
    background: 'linear-gradient(135deg, #F1F2F6 0%, #E5E7EB 100%)',
    // ✅ 恐惧灰卡片背景
    card_bg: 'rgba(241, 242, 246, 0.9)',
    text: '#2F3542',
    text_secondary: '#57606F',
    border: '#D5D8DC',
    success: '#58D68D',
    warning: '#F7DC6F',
    error: '#EC7063',
    gradient: 'linear-gradient(135deg, #747D8C 0%, #A4B0BE 50%, #57606F 100%)',
    shadow: '0 8px 32px rgba(116, 125, 140, 0.25)',
    glow: '0 0 20px rgba(116, 125, 140, 0.5)'
}

// 🤢 厌恶 - 阳光橙（排斥警告）
export const forest = {
    name: 'Forest',
    emotion: 'disgust',
    emoji: '🤢',
    primary: '#FF9F43',
    secondary: '#FECA57',
    accent: '#FF6B6B',
    highlight: '#FFA502',
    background: 'linear-gradient(135deg, #FFF5E6 0%, #FFE8CC 100%)',
    // ✅ 厌恶橙卡片背景
    card_bg: 'rgba(255, 245, 230, 0.9)',
    text: '#2D3436',
    text_secondary: '#636E72',
    border: '#FFEAA7',
    success: '#00B894',
    warning: '#FDCB6E',
    error: '#FF7675',
    gradient: 'linear-gradient(135deg, #FF9F43 0%, #FECA57 50%, #FF6B6B 100%)',
    shadow: '0 8px 32px rgba(255, 159, 67, 0.25)',
    glow: '0 0 20px rgba(255, 159, 67, 0.5)'
}

// 😐 平静 - 禅意白（平和简约）
export const zen = {
    name: 'Zen',
    emotion: 'neutral',
    emoji: '😐',
    primary: '#DFE4EA',
    secondary: '#F1F2F6',
    accent: '#A4B0BE',
    highlight: '#747D8C',
    background: 'linear-gradient(135deg, #FFFFFF 0%, #F8F9FA 100%)',
    // ✅ 平静白卡片背景
    card_bg: 'rgba(248, 249, 250, 0.95)',
    text: '#2F3542',
    text_secondary: '#57606F',
    border: '#DFE4EA',
    success: '#2ED573',
    warning: '#F7DC6F',
    error: '#EC7063',
    gradient: 'linear-gradient(135deg, #DFE4EA 0%, #F1F2F6 50%, #A4B0BE 100%)',
    shadow: '0 8px 32px rgba(0, 0, 0, 0.08)',
    glow: '0 0 15px rgba(0, 0, 0, 0.1)'
}

// ==================== 3个特殊主题 ====================

// 🎮 守望先锋 - 暗紫色特勤主题（炫酷科技感）
export const overwatch = {
    name: 'Overwatch',
    emotion: 'special',
    emoji: '🎮',
    // 核心颜色
    primary: '#A259FF',
    secondary: '#6E2EFF',
    accent: '#C47CFF',
    highlight: '#E9DEFF',
    // 背景渐变
    background: 'linear-gradient(135deg, #05020A 0%, #1A0B2E 50%, #05020A 100%)',
    // 玻璃拟态卡片背景
    card_bg: 'rgba(26, 11, 46, 0.7)',
    // 字体颜色
    text: '#E9DEFF',
    text_secondary: '#C8B8DB',
    // 边框 - 紫罗兰发光
    border: 'rgba(156, 78, 255, 0.4)',
    // 状态色
    success: '#00D9FF',
    warning: '#F99E1A',
    error: '#FF4757',
    // 主渐变
    gradient: 'linear-gradient(135deg, #A259FF 0%, #6E2EFF 100%)',
    // 阴影 - 紫色光晕
    shadow: '0 10px 25px -5px rgba(110, 46, 255, 0.3)',
    // 发光效果
    glow: '0 0 20px rgba(162, 89, 255, 0.6), 0 0 40px rgba(110, 46, 255, 0.3)',
    // 玻璃拟态特效
    glassmorphism: {
        backdropFilter: 'blur(12px)',
        border: '1px solid rgba(156, 78, 255, 0.4)',
        boxShadow: '0 10px 25px -5px rgba(110, 46, 255, 0.3)'
    },
    // Hover状态
    hover: {
        border: '1px solid rgba(196, 124, 255, 0.8)',
        glow: '0 0 30px rgba(196, 124, 255, 0.8)'
    }
}

// 🌃 赛博朋克 - 霓虹蓝紫（未来科技）
export const cyberpunk = {
    name: 'Cyberpunk',
    emotion: 'special',
    emoji: '🌃',
    primary: '#00F5FF',
    secondary: '#FF00FF',
    accent: '#FF006E',
    highlight: '#00F5FF',
    background: 'linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0a0e27 100%)',
    card_bg: 'rgba(10, 14, 39, 0.9)',
    text: '#00F5FF',
    text_secondary: '#FF00FF',
    border: '#00F5FF',
    success: '#00FF9F',
    warning: '#FFEA00',
    error: '#FF0055',
    gradient: 'linear-gradient(135deg, #00F5FF 0%, #FF00FF 50%, #FF006E 100%)',
    shadow: '0 8px 32px rgba(0, 245, 255, 0.3)',
    glow: '0 0 20px rgba(0, 245, 255, 0.8), 0 0 40px rgba(255, 0, 255, 0.4)'
}

// ⚪ 极简白 - 纯净优雅（现代简约）
export const minimal = {
    name: 'Minimal',
    emotion: 'special',
    emoji: '⚪',
    primary: '#2C3E50',
    secondary: '#34495E',
    accent: '#95A5A6',
    highlight: '#3498DB',
    background: 'linear-gradient(135deg, #FAFAFA 0%, #F5F5F5 100%)',
    card_bg: 'rgba(255, 255, 255, 0.98)',
    text: '#2C3E50',
    text_secondary: '#7F8C8D',
    border: '#ECF0F1',
    success: '#27AE60',
    warning: '#F39C12',
    error: '#E74C3C',
    gradient: 'linear-gradient(135deg, #2C3E50 0%, #3498DB 100%)',
    shadow: '0 4px 20px rgba(0, 0, 0, 0.06)',
    glow: '0 0 15px rgba(52, 152, 219, 0.2)'
}

// 主题映射
export const THEMES = {
    sunny,
    rainy,
    fire,
    galaxy,
    mist,
    forest,
    zen,
    overwatch,
    cyberpunk,
    minimal
}

// 情绪到主题的映射
export const EMOTION_TO_THEME = {
    happy: 'sunny',
    sad: 'rainy',
    angry: 'fire',
    surprise: 'galaxy',
    fear: 'mist',
    disgust: 'forest',
    neutral: 'zen'
}

// 获取主题
export function getTheme(themeName) {
    return THEMES[themeName] || zen
}

// 根据情绪获取主题
export function getThemeByEmotion(emotion) {
    const themeName = EMOTION_TO_THEME[emotion] || 'zen'
    return THEMES[themeName]
}
