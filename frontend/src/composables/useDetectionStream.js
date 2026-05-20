import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { getEmotionName, getEmotionColor, EMOTION_KEYS } from '@/constants/emotions'
import { logFeatureUsage } from '@/utils/analytics'
import logger from '@/utils/logger'
import { workerDetectionService } from '@/services/workerDetection'

export function useDetectionStream() {
    const isEmotionDetectionOn = ref(false)
    const currentEmotion = ref('neutral')
    const currentConfidence = ref(0)
    const emotionScores = reactive(
        Object.fromEntries(EMOTION_KEYS.map(k => [k, 0]))
    )
    const currentFaces = ref([])
    const detectionMode = ref('worker') // 'worker' | 'websocket'

    let ws = null
    let wsReconnectTimer = null
    let wsReconnectAttempts = 0
    const WS_MAX_RECONNECT_ATTEMPTS = 5
    const WS_RECONNECT_DELAY = 2000

    // Web Worker 检测
    const detectWithWorker = async (imageData, width, height) => {
        try {
            const result = await workerDetectionService.detect(imageData, width, height)
            return result
        } catch (error) {
            logger.error('Worker 检测失败:', error)
            return null
        }
    }

    // WebSocket 连接
    const connectWebSocket = (onMessage) => {
        const savedUrl = localStorage.getItem('server_url')
        const wsUrl = savedUrl ? savedUrl.replace(/^http/, 'ws') + '/ws/detect' : (localStorage.getItem('ws_url') || 'ws://localhost:8000/ws/detect')
        ws = new WebSocket(wsUrl)

        ws.onopen = () => {
            wsReconnectAttempts = 0
            logger.info('[WebSocket] 连接成功')
        }

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data)
                if (onMessage) onMessage(data)
            } catch (error) {
                logger.error('WebSocket 消息解析失败:', error)
            }
        }

        ws.onerror = (error) => {
            logger.error('WebSocket 错误:', error)
        }

        ws.onclose = (event) => {
            if (isEmotionDetectionOn.value && wsReconnectAttempts < WS_MAX_RECONNECT_ATTEMPTS) {
                wsReconnectAttempts++
                wsReconnectTimer = setTimeout(() => {
                    connectWebSocket(onMessage)
                }, WS_RECONNECT_DELAY * wsReconnectAttempts)
            }
        }
    }

    const disconnectWebSocket = () => {
        if (wsReconnectTimer) {
            clearTimeout(wsReconnectTimer)
            wsReconnectTimer = null
        }
        if (ws) {
            ws.onclose = null
            ws.close()
            ws = null
        }
    }

    const sendFrame = (blob) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(blob)
            return true
        }
        return false
    }

    const handleDetectionResult = (data, emaAlpha) => {
        if (data.type === 'result' || data.faces) {
            const result = data.type === 'result' ? data : { faces: data.faces }

            if (result.dominant_emotion) {
                currentEmotion.value = result.dominant_emotion
            } else if (result.faces && result.faces.length > 0) {
                currentEmotion.value = result.faces[0].emotion || 'neutral'
            }

            if (result.faces && result.faces.length > 0) {
                const firstFace = result.faces[0]
                if (firstFace.confidence !== undefined) {
                    currentConfidence.value = firstFace.confidence
                }
                if (firstFace.scores) {
                    Object.keys(firstFace.scores).forEach(key => {
                        if (key in emotionScores) {
                            emotionScores[key] = firstFace.scores[key]
                        }
                    })
                }
            }
            if (result.faces) {
                currentFaces.value = result.faces
            }
        }
    }

    const toggleEmotionDetection = async () => {
        isEmotionDetectionOn.value = !isEmotionDetectionOn.value
        
        if (isEmotionDetectionOn.value) {
            logFeatureUsage('realtime', { action: 'start_detection' })
            
            // 如果使用 Web Worker，初始化服务
            if (detectionMode.value === 'worker') {
                try {
                    await workerDetectionService.initialize()
                    logger.info('[Detection] Web Worker 模式已启动')
                } catch (error) {
                    logger.error('Worker 初始化失败，切换到 WebSocket 模式')
                    detectionMode.value = 'websocket'
                }
            }
        } else {
            // 停止检测时清理资源
            if (detectionMode.value === 'worker') {
                workerDetectionService.destroy()
            } else {
                disconnectWebSocket()
            }
        }
    }

    const setDetectionMode = (mode) => {
        if (mode !== detectionMode.value) {
            // 先停止当前模式
            if (isEmotionDetectionOn.value) {
                if (detectionMode.value === 'worker') {
                    workerDetectionService.destroy()
                } else {
                    disconnectWebSocket()
                }
            }
            
            detectionMode.value = mode
            
            // 如果检测正在运行，重新启动
            if (isEmotionDetectionOn.value) {
                if (mode === 'worker') {
                    workerDetectionService.initialize()
                } else {
                    connectWebSocket(handleDetectionResult)
                }
            }
        }
    }

    const resetEmotionState = () => {
        currentEmotion.value = 'neutral'
        currentConfidence.value = 0
        EMOTION_KEYS.forEach(k => { emotionScores[k] = 0 })
        currentFaces.value = []
    }

    return {
        isEmotionDetectionOn,
        currentEmotion,
        currentConfidence,
        emotionScores,
        currentFaces,
        detectionMode,
        connectWebSocket,
        disconnectWebSocket,
        sendFrame,
        detectWithWorker,
        handleDetectionResult,
        toggleEmotionDetection,
        setDetectionMode,
        resetEmotionState
    }
}