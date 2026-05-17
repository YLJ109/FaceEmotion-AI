/**
 * 检测相关 API
 */
import http from '../http'

/**
 * 上传图片进行情绪检测
 * @param {FormData} formData - 包含图片文件的 FormData
 * @returns {Promise<Object>}
 */
export const detectImage = (formData) => {
    return http.post('/api/detect/image', formData)
}

/**
 * 批量检测图片
 * @param {FormData} formData - 包含多个图片文件的 FormData
 * @returns {Promise<Object>}
 */
export const detectBatch = (formData) => {
    return http.post('/api/detect/batch', formData)
}

/**
 * 上传视频进行情绪检测
 * @param {FormData} formData - 包含视频文件的 FormData
 * @returns {Promise<Object>}
 */
export const detectVideo = (formData) => {
    return http.post('/api/detect/video', formData)
}

/**
 * 获取实时检测流（WebSocket）
 * @returns {string} WebSocket URL
 */
export const getRealtimeStreamUrl = () => {
    try {
      const saved = localStorage.getItem('server_url')
      if (saved) return saved.replace(/^http/, 'ws') + '/ws/stream'
    } catch { /* ignore */ }
    return import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/stream'
}
