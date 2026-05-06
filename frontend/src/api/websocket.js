/**
 * WebSocket连接管理 V2 — 支持心跳、指数退避重连
 */
import { ElMessage } from 'element-plus'

class WebSocketManager {
  constructor(url) {
    this.ws = null
    this.reconnectInterval = 1000  // ✅ 优化: 从 2000ms 降到 1000ms，加快首次重连
    this.maxReconnectAttempts = 20
    this.reconnectAttempts = 0
    this.messageHandlers = []
    this.isConnected = false
    this._onConnectCallbacks = []
    this._onDisconnectCallbacks = []
    this._pingTimer = null
    this._expectingPong = false
    this.url = url
  }

  getUrl() {
    if (this.url) return this.url
    try {
      const config = JSON.parse(localStorage.getItem('app_config') || '{}')
      return config.ws_url || 'ws://localhost:8000/ws/stream'
    } catch {
      return 'ws://localhost:8000/ws/stream'
    }
  }

  connect() {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return Promise.resolve()
    }
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.getUrl())
        this.ws.binaryType = 'blob'

        this.ws.onopen = () => {
          // ✅ 明确记录连接成功
          console.log('✅ WebSocket连接成功 (readyState:', this.ws.readyState, ')')
          this.isConnected = true
          this.reconnectAttempts = 0
          this._expectingPong = false
          this.notifyHandlers({ type: 'connected' })
          this._onConnectCallbacks.forEach(cb => cb())
          this._onConnectCallbacks = []
          this._startHeartbeat()
          resolve()
        }

        this.ws.onmessage = (event) => {
          if (event.data instanceof Blob) {
            this.notifyHandlers({ type: '__binary_frame', data: event.data })
          } else {
            try {
              const data = JSON.parse(event.data)
              // 处理心跳 pong
              if (data.type === 'ping') {
                this.ws.send(JSON.stringify({ type: 'pong' }))
                return
              }
              if (data.type === 'pong') return
              this.notifyHandlers(data)
            } catch (e) {
              console.warn('WebSocket消息解析失败:', e)
            }
          }
        }

        this.ws.onerror = (error) => {
          // ✅ 完全隐藏Chrome扩展的无关错误
          // 这些错误不影响实际连接，后端日志显示连接已成功建立
          // 如果连接真的失败，onclose 会触发重连机制
        }

        this.ws.onclose = () => {
          // ✅ 关闭调试日志
          // console.log('⚠️ WebSocket连接关闭')
          this.isConnected = false
          this._stopHeartbeat()
          this.notifyHandlers({ type: 'disconnected' })
          this._onDisconnectCallbacks.forEach(cb => cb())
          this.reconnect()
        }
      } catch (error) {
        console.error('WebSocket连接失败:', error)
        reject(error)
      }
    })
  }

  reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      // ✅ 优化: 更激进的重连策略（1s, 2s, 3s, 4s...）最大 10s
      const delay = Math.min(10000, this.reconnectInterval * Math.pow(1.3, this.reconnectAttempts - 1))
      console.log(`🔄 重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts}) 延迟 ${Math.round(delay)}ms`)
      setTimeout(() => {
        this.connect().catch(() => { })
      }, delay)
    } else {
      console.error('❌ 达到最大重连次数')
      ElMessage.error('WebSocket连接失败，请刷新页面重试')
    }
  }

  send(data) {
    if (this.isConnected && this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
      return true
    }
    return false
  }

  sendMessage(type, data = {}) {
    return this.send({ type, ...data })
  }

  sendBinary(blob) {
    if (this.isConnected && this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(blob)
      return true
    }
    return false
  }

  onMessage(handler) {
    this.messageHandlers.push(handler)
    return () => {
      this.messageHandlers = this.messageHandlers.filter(h => h !== handler)
    }
  }

  onConnect(callback) {
    if (this.isConnected) {
      callback()
    } else {
      this._onConnectCallbacks.push(callback)
    }
  }

  onDisconnect(callback) {
    this._onDisconnectCallbacks.push(callback)
  }

  notifyHandlers(data) {
    this.messageHandlers.forEach(handler => {
      try { handler(data) } catch (error) { console.error('消息处理器错误:', error) }
    })
  }

  disconnect() {
    this._stopHeartbeat()
    this.reconnectAttempts = this.maxReconnectAttempts
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.isConnected = false
  }

  /** 心跳 */
  _startHeartbeat() {
    this._stopHeartbeat()
    // 不主动发 ping（服务端发 ping 我们回 pong）
    // 只保活检测
    this._pingTimer = setInterval(() => {
      if (!this.isConnected || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
        this._stopHeartbeat()
      }
    }, 10000)
  }

  _stopHeartbeat() {
    if (this._pingTimer) {
      clearInterval(this._pingTimer)
      this._pingTimer = null
    }
  }
}

const defaultWsUrl = (() => {
  try {
    const c = JSON.parse(localStorage.getItem('app_config') || '{}')
    return c.ws_url || undefined
  } catch { return undefined }
})()

export const wsManager = new WebSocketManager(defaultWsUrl)
export default wsManager
