/**
 * API 统一导出
 * 提供简洁的导入方式
 */

// HTTP 客户端
export { default as http } from './http'

// 配置
export { API_BASE_URL, WS_URL, API } from './config'

// WebSocket
export { default as wsManager } from './websocket'

// 业务模块 API
export * from './modules/history'
export * from './modules/analytics'
export * from './modules/detection'
export * from './modules/system'
