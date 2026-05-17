import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { getEmotionName, getEmotionColor, EMOTION_KEYS } from '@/constants/emotions'
import { logFeatureUsage } from '@/utils/analytics'
import logger from '@/utils/logger'

export function useDetectionStream() {
    const isEmotionDetectionOn = ref(false)
    const currentEmotion = ref('neutral')
    const currentConfidence = ref(0)
    const emotionScores = reactive(
        Object.fromEntries(EMOTION_KEYS.map(k => [k, 0]))
    )
    const currentFaces = ref([])

    let ws = null
    let wsReconnectTimer = null
    let wsReconnectAttempts = 0
    const WS_MAX_RECONNECT_ATTEMPTS = 5
    const WS_RECONNECT_DELAY = 2000

    const connectWebSocket = (onMessage) => {
        const savedUrl = localStorage.getItem('server_url')
        const wsUrl = savedUrl ? savedUrl.replace(/^http/, 'ws') + '/ws/detect' : (localStorage.getItem('ws_url') || 'ws://localhost:8000/ws/detect')
        ws = new WebSocket(wsUrl)

        ws.onopen = () => {
            
            wsReconnectAttempts = 0
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
        console.log('收到WebSocket消息:', JSON.stringify(data).substring(0, 200), '...')
        if (data.type === 'result') {
            const result = data

            if (result.dominant_emotion) {
                currentEmotion.value = result.dominant_emotion
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
                // 调试：检查关键点数据
                if (firstFace.landmarks) {
                    console.log('关键点数据:', firstFace.landmarks.length, '个关键点')
                    console.log('关键点示例:', JSON.stringify(firstFace.landmarks[0]))
                } else {
                    console.log('没有关键点数据')
                }
            }
            if (result.faces) {
                currentFaces.value = result.faces
            }
        }
    }

    const toggleEmotionDetection = () => {
        isEmotionDetectionOn.value = !isEmotionDetectionOn.value
        if (isEmotionDetectionOn.value) {
            logFeatureUsage('realtime', { action: 'start_detection' })
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
        connectWebSocket,
        disconnectWebSocket,
        sendFrame,
        handleDetectionResult,
        toggleEmotionDetection,
        resetEmotionState
    }
}