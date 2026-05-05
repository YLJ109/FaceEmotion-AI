/**
 * 系统配置相关 API
 */
import http from '../http'

/**
 * 获取系统配置
 * @returns {Promise<Object>}
 */
export const getSystemConfig = () => {
    return http.get('/api/config')
}

/**
 * 更新系统配置
 * @param {Object} config - 配置对象
 * @returns {Promise<Object>}
 */
export const updateSystemConfig = (config) => {
    return http.post('/api/config', config)
}

/**
 * 获取系统健康状态
 * @returns {Promise<Object>}
 */
export const getHealthStatus = () => {
    return http.get('/api/health')
}

/**
 * 获取系统统计信息
 * @returns {Promise<Object>}
 */
export const getSystemStats = () => {
    return http.get('/api/stats')
}

/**
 * 提交用户反馈
 * @param {Object} feedback - 反馈数据
 * @returns {Promise<Object>}
 */
export const submitFeedback = (feedback) => {
    return http.post('/api/feedback', feedback)
}
