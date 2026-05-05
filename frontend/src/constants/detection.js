/**
 * 检测相关常量定义
 */

// 检测类型映射
export const DETECTION_TYPES = {
    realtime: '实时检测',
    image: '单张图片',
    batch: '批量检测',
    video: '视频检测'
}

// 检测类型图标映射（Element Plus 图标名）
export const DETECTION_TYPE_ICONS = {
    realtime: 'VideoCamera',
    image: 'Picture',
    batch: 'Files',
    video: 'Film'
}

// 置信度区间定义
export const CONFIDENCE_RANGES = [
    { key: '0-20', label: '0-20%', min: 0, max: 0.2 },
    { key: '20-40', label: '20-40%', min: 0.2, max: 0.4 },
    { key: '40-60', label: '40-60%', min: 0.4, max: 0.6 },
    { key: '60-80', label: '60-80%', min: 0.6, max: 0.8 },
    { key: '80-100', label: '80-100%', min: 0.8, max: 1.0 }
]

// 人脸数量区间定义
export const FACE_COUNT_RANGES = [
    { key: '1', label: '1人' },
    { key: '2', label: '2人' },
    { key: '3', label: '3人' },
    { key: '4-5', label: '4-5人' },
    { key: '6+', label: '6人以上' }
]

/**
 * 获取检测类型中文名称
 * @param {string} type - 检测类型标识
 * @returns {string}
 */
export function getDetectionTypeLabel(type) {
    return DETECTION_TYPES[type] || type
}

/**
 * 获取检测类型图标
 * @param {string} type - 检测类型标识
 * @returns {string}
 */
export function getDetectionTypeIcon(type) {
    return DETECTION_TYPE_ICONS[type] || 'QuestionFilled'
}

/**
 * 根据置信度值获取区间标签
 * @param {number} confidence - 置信度值 (0-1)
 * @returns {string}
 */
export function getConfidenceRange(confidence) {
    if (confidence < 0.2) return '0-20'
    if (confidence < 0.4) return '20-40'
    if (confidence < 0.6) return '40-60'
    if (confidence < 0.8) return '60-80'
    return '80-100'
}
