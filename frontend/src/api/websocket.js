/**
 * WebSocket连接管理 V2 — 支持心跳、指数退避重连
 */
import { ElMessage } from 'element-plus'
import logger from '@/utils/logger'

class WebSocketManager {
  constructor(url) {
    this.ws = null
    this.reconnectInterval = 1000
    this.maxReconnectAttempts = 20
    this.reconnectAttempts = 0
    this.messageHandlers = []
    this.isConnected = false
    this._onConnectCallbacks = []
    this._onDisconnectCallbacks = []
    this._pingTimer = null
    this._expectingPong = false
    this._pongTimeout = null
    this.url = url
    this._isReconnecting = false
    this._shouldReconnect = true
  }

  getUrl() {
    return this.url || 'ws://localhost:8000/ws/stream'
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
              if (data.type === 'ping') {
                this.ws.send(JSON.stringify({ type: 'pong' }))
                return
              }
              if (data.type === 'pong') {
                this._expectingPong = false
                if (this._pongTimeout) {
                  clearTimeout(this._pongTimeout)
                  this._pongTimeout = null
                }
                return
              }
              this.notifyHandlers(data)
            } catch (e) {
              logger.warn('WebSocket消息解析失败:', e)
            }
          }
        }

        this.ws.onerror = () => {}

        this.ws.onclose = () => {
          this.isConnected = false
          this._stopHeartbeat()
          this.notifyHandlers({ type: 'disconnected' })
          this._onDisconnectCallbacks.forEach(cb => cb())
          if (this._shouldReconnect) {
            this.reconnect()
          }
        }
      } catch (error) {
        console.error('WebSocket连接失败:', error)
        reject(error)
      }
    })
  }

  reconnect() {
    if (this._isReconnecting) return
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WebSocket] 达到最大重连次数')
      ElMessage.error('WebSocket连接失败，请刷新页面重试')
      return
    }
    
    this._isReconnecting = true
    this.reconnectAttempts++
    const delay = Math.min(10000, this.reconnectInterval * Math.pow(1.3, this.reconnectAttempts - 1))
    
    setTimeout(() => {
      this.connect().catch((error) => {
        console.warn(`[WebSocket] 重连失败 (${this.reconnectAttempts}/${this.maxReconnectAttempts}):`, error)
      }).finally(() => {
        this._isReconnecting = false
      })
    }, delay)
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

  close() {
    this._shouldReconnect = false
    this._stopHeartbeat()
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      this.ws.close(1000, '主动关闭')
    }
    this.ws = null
  }

  resetReconnect() {
    this._shouldReconnect = true
    this.reconnectAttempts = 0
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
      try { handler(data) } catch (error) { logger.error('消息处理器错误:', error) }
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

  _startHeartbeat() {
    this._stopHeartbeat()
    this._expectingPong = false
    this._pingTimer = setInterval(() => {
      if (!this.isConnected || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
        this._stopHeartbeat()
        return
      }
      
      if (this._expectingPong) {
        console.warn('[WebSocket] 未收到pong响应，断开连接')
        this.ws.close(1000, '心跳超时')
        return
      }
      
      this._expectingPong = true
      this.ws.send(JSON.stringify({ type: 'ping' }))
      
      this._pongTimeout = setTimeout(() => {
        if (this._expectingPong && this.isConnected) {
          logger.warn('[WebSocket] Pong超时，断开连接')
          this.ws.close(1000, 'Pong超时')
        }
      }, 15000)
    }, 15000)
  }

  _stopHeartbeat() {
    if (this._pingTimer) {
      clearInterval(this._pingTimer)
      this._pingTimer = null
    }
    if (this._pongTimeout) {
      clearTimeout(this._pongTimeout)
      this._pongTimeout = null
    }
    this._expectingPong = false
  }
}

export { WebSocketManager }
export const wsManager = new WebSocketManager()
export default wsManager
