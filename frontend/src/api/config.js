/**
 * API 配置 - 统一管理所有后端请求地址
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/stream'

export const API = {
  baseUrl: API_BASE_URL,
  config: `${API_BASE_URL}/api/config`,
  detectImage: `${API_BASE_URL}/api/detect/image`,
  detectBatch: `${API_BASE_URL}/api/detect/batch`,
  detectVideo: `${API_BASE_URL}/api/detect/video`,
  detectBatchVideo: `${API_BASE_URL}/api/detect/batch-video`,
  history: `${API_BASE_URL}/api/history`,
  historySave: `${API_BASE_URL}/api/history/save`,
  historyStats: `${API_BASE_URL}/api/history/stats`,
  historyDelete: `${API_BASE_URL}/api/history`,
  stats: `${API_BASE_URL}/api/stats`,
  feedback: `${API_BASE_URL}/api/feedback`,
  feedbackHistory: `${API_BASE_URL}/api/feedback/history`,
  health: `${API_BASE_URL}/api/health`,
  emotionTrendAnalyze: `${API_BASE_URL}/api/emotion-trend/analyze`,
  emotionTransitions: `${API_BASE_URL}/api/analytics/emotion_transitions`,
  emotionTrend: `${API_BASE_URL}/api/analytics/emotion_trend`,
  learnerStatus: `${API_BASE_URL}/api/learner/status`,
  performanceRecommend: `${API_BASE_URL}/api/performance/recommend`,
  textAnalysis: `${API_BASE_URL}/api/text-analysis/analyze`,
  textAnalysisBatch: `${API_BASE_URL}/api/text-analysis/analyze-batch`,
  textAnalysisFeedback: `${API_BASE_URL}/api/text-analysis/analyze-feedback`,
}

export { API_BASE_URL, WS_URL }
