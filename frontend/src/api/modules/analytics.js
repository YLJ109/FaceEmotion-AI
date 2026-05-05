/**
 * 数据分析相关 API
 */
import http from '../http'

/**
 * 获取情绪趋势数据
 * @param {Object} params - 查询参数
 * @param {number} params.days - 天数（默认7天）
 * @returns {Promise<Array>}
 */
export const getEmotionTrend = (params = { days: 7 }) => {
    return http.get('/api/analytics/emotion_trend', { params })
}

/**
 * 获取情绪转换矩阵数据
 * @param {Object} params - 查询参数
 * @param {number} params.limit - 限制记录数（默认1000）
 * @returns {Promise<Array>}
 */
export const getEmotionTransitions = (params = { limit: 1000 }) => {
    return http.get('/api/analytics/emotion_transitions', { params })
}

/**
 * 记录功能使用情况（用于统计分析）
 * @param {Object} data - 使用数据
 * @param {string} data.feature - 功能名称
 * @param {Object} data.metadata - 元数据
 * @returns {Promise<Object>}
 */
export const logFeatureUsage = (data) => {
    return http.post('/api/analytics/log', data)
}

/**
 * 获取用户行为统计
 * @param {Object} params - 查询参数
 * @param {string} params.start_date - 开始日期
 * @param {string} params.end_date - 结束日期
 * @returns {Promise<Object>}
 */
export const getUserAnalytics = (params = {}) => {
    return http.get('/api/analytics/user_behavior', { params })
}
