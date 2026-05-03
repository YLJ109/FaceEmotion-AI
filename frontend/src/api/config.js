/**
 * API 配置 - 统一管理所有后端请求地址
 */
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/stream'

export const API = {
  config: `${API_BASE_URL}/api/config`,
  detectImage: `${API_BASE_URL}/api/detect/image`,
  detectBatch: `${API_BASE_URL}/api/detect/batch`,
  detectVideo: `${API_BASE_URL}/api/detect/video`,
  history: `${API_BASE_URL}/api/history`,
  historySave: `${API_BASE_URL}/api/history/save`,
  historyStats: `${API_BASE_URL}/api/history/stats`,
  stats: `${API_BASE_URL}/api/stats`,
  feedback: `${API_BASE_URL}/api/feedback`,
  health: `${API_BASE_URL}/api/health`,
}
