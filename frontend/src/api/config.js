/**
 * API 配置 - 统一管理所有后端请求地址
 */
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/stream'

export const API = {
  baseUrl: API_BASE_URL, // ✅ 新增: 基础 URL
  config: `${API_BASE_URL}/api/config`,
  detectImage: `${API_BASE_URL}/api/detect/image`,
  detectBatch: `${API_BASE_URL}/api/detect/batch`,
  detectVideo: `${API_BASE_URL}/api/detect/video`,
  detectBatchVideo: `${API_BASE_URL}/api/detect/batch-video`, // ✅ 新增: 批量视频检测
  history: `${API_BASE_URL}/api/history`,
  historySave: `${API_BASE_URL}/api/history/save`,
  historyStats: `${API_BASE_URL}/api/history/stats`,
  stats: `${API_BASE_URL}/api/stats`,
  feedback: `${API_BASE_URL}/api/feedback`,
  feedbackHistory: `${API_BASE_URL}/api/feedback/history`, // ✅ 新增: 反馈历史
  health: `${API_BASE_URL}/api/health`,
}
