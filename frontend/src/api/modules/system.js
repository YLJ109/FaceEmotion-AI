/**
 * 系统配置相关 API
 */
import http from '../http'

export const getSystemConfig = () => {
    return http.get('/api/config', { log: false })
}

export const updateSystemConfig = (config) => {
    return http.put('/api/config', config)
}

export const getHealthStatus = () => {
    return http.get('/api/health')
}

export const getSystemStats = () => {
    return http.get('/api/stats')
}

export const submitFeedback = (feedback) => {
    return http.post('/api/feedback', feedback)
}

export const getFeedbackHistory = (params = {}) => {
    return http.get('/api/feedback/history', { params })
}

export const deleteFeedback = (id) => {
    return http.delete(`/api/feedback/${id}`)
}

export const getPerformanceRecommend = () => {
    return http.get('/api/performance/recommend')
}

export const getLearnerStatus = () => {
    return http.get('/api/learner/status')
}

export const analyzeText = (data) => {
    return http.post('/api/text-analysis/analyze', data)
}

export const analyzeTextBatch = (data) => {
    return http.post('/api/text-analysis/analyze-batch', data)
}

export const analyzeTextFeedback = (params = {}) => {
    return http.get('/api/text-analysis/analyze-feedback', { params })
}
