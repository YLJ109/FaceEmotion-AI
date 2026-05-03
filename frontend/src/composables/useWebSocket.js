/**
 * WebSocket 管理 Composable - 封装 WebSocket 通信逻辑
 * 
 * 【优化】
 * - 统一管理连接、消息、断开逻辑
 * - 支持自动重连
 * - 提供帧发送接口
 */
import { ref, onUnmounted } from 'vue'
import wsManager from '@/api/websocket'

export function useWebSocket() {
    const isConnected = ref(false)
    const isConnecting = ref(false)
    const lastError = ref(null)

    // 回调函数
    let onConnectCallback = null
    let onMessageCallback = null
    let onDisconnectCallback = null

    // === 连接管理 ===
    const connect = () => {
        if (isConnecting.value || isConnected.value) return

        isConnecting.value = true

        wsManager.onConnect(() => {
            isConnected.value = true
            isConnecting.value = false
            lastError.value = null
            console.log('WebSocket 已连接')

            if (onConnectCallback) onConnectCallback()
        })

        wsManager.onMessage((data) => {
            if (onMessageCallback) onMessageCallback(data)
        })

        wsManager.onDisconnect(() => {
            isConnected.value = false
            isConnecting.value = false
            console.log('WebSocket 已断开')

            if (onDisconnectCallback) onDisconnectCallback()
        })
    }

    // === 断开连接 ===
    const disconnect = () => {
        wsManager.disconnect?.()
        isConnected.value = false
    }

    // === 发送帧数据 ===
    const sendFrame = (frameData) => {
        if (!isConnected.value) {
            console.warn('WebSocket 未连接，无法发送帧')
            return false
        }

        try {
            wsManager.sendBinary(frameData)
            return true
        } catch (error) {
            console.error('发送帧失败:', error)
            lastError.value = error
            return false
        }
    }

    // === 回调注册 ===
    const onConnect = (callback) => {
        onConnectCallback = callback
    }

    const onMessage = (callback) => {
        onMessageCallback = callback
    }

    const onDisconnect = (callback) => {
        onDisconnectCallback = callback
    }

    // === 状态查询 ===
    const getStatus = () => ({
        isConnected: isConnected.value,
        isConnecting: isConnecting.value,
        lastError: lastError.value
    })

    // 组件卸载时断开
    onUnmounted(() => {
        disconnect()
    })

    return {
        // 状态
        isConnected,
        isConnecting,
        lastError,

        // 方法
        connect,
        disconnect,
        sendFrame,
        onConnect,
        onMessage,
        onDisconnect,
        getStatus
    }
}
