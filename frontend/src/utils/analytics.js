/**
 * 用户行为分析工具 - 记录功能使用情况到后端
 *
 * 使用方式:
 *   import { logFeatureUsage } from '@/utils/analytics'
 *   logFeatureUsage('实时检测', { emotion: 'happy' })
 */

import { logFeatureUsage as apiLogFeatureUsage } from '@/api/modules/analytics'

// 会话级别唯一 ID，每个浏览器标签页生成一次
let _sessionId = null
function getSessionId() {
  if (!_sessionId) {
    _sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8)
  }
  return _sessionId
}

/**
 * 记录功能使用事件 (fire-and-forget)
 * @param {string} feature - 功能名称，如 '实时检测', '图片检测', '批量检测', '视频检测'
 * @param {object} [metadata={}] - 附加元数据
 */
export function logFeatureUsage(feature, metadata = {}) {
  const body = {
    feature,
    session_id: getSessionId(),
    duration_ms: 0,
    metadata,
  }

  // 使用新的 API 模块，静默上报（不显示错误提示）
  apiLogFeatureUsage(body).catch(() => {
    /* 忽略网络错误 */
  })
}
