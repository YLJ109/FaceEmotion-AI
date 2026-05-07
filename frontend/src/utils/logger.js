/**
 * 统一日志工具
 * 根据环境变量控制日志输出，生产环境自动禁用调试日志
 */

const isDev = import.meta.env.DEV
const logLevel = import.meta.env.VITE_LOG_LEVEL || 'info'

const levels = {
  debug: 0,
  log: 1,
  info: 2,
  warn: 3,
  error: 4
}

const currentLevel = levels[logLevel] || levels.info

const logger = {
  /**
   * 调试日志 - 仅开发环境输出
   */
  debug(...args) {
    if (isDev && levels.debug >= currentLevel) {
      console.debug(`🟦 [DEBUG]`, ...args)
    }
  },

  /**
   * 普通日志 - 仅开发环境输出
   */
  log(...args) {
    if (isDev && levels.log >= currentLevel) {
      console.log(`⬜ [LOG]`, ...args)
    }
  },

  /**
   * 信息日志 - 开发和生产环境都输出
   */
  info(...args) {
    if (levels.info >= currentLevel) {
      console.info(`🟩 [INFO]`, ...args)
    }
  },

  /**
   * 警告日志 - 开发和生产环境都输出
   */
  warn(...args) {
    if (levels.warn >= currentLevel) {
      console.warn(`🟨 [WARN]`, ...args)
    }
  },

  /**
   * 错误日志 - 始终输出
   */
  error(...args) {
    console.error(`🟥 [ERROR]`, ...args)
  },

  /**
   * 分组日志
   */
  group(label) {
    if (isDev) {
      console.group(`📦 ${label}`)
    }
  },

  groupEnd() {
    if (isDev) {
      console.groupEnd()
    }
  },

  /**
   * API请求日志
   */
  apiRequest(method, url, data) {
    if (isDev) {
      console.log(`📤 [API] ${method.toUpperCase()} ${url}`, data || '')
    }
  },

  /**
   * API响应日志
   */
  apiResponse(status, url, data) {
    if (isDev) {
      console.log(`📥 [API] ${status} ${url}`, data || '')
    }
  },

  /**
   * WebSocket消息日志
   */
  wsMessage(type, data) {
    if (isDev) {
      console.log(`🔌 [WS] ${type}`, data || '')
    }
  },

  /**
   * 性能监控日志
   */
  perf(name, duration) {
    if (isDev) {
      console.log(`⏱️ [PERF] ${name}: ${duration.toFixed(2)}ms`)
    }
  }
}

export default logger
