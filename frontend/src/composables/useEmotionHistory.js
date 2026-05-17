import { ref } from 'vue'
import { saveHistoryRecord } from '@/api/modules/history'
import { analyzeEmotionTrend } from '@/api/modules/analytics'
import logger from '@/utils/logger'

export function useEmotionHistory() {
    const HISTORY_MAX_LENGTH = 50
    const emotionHistory = ref([])

    const trendAnalysis = ref(null)
    const textAnalysis = ref(null)
    const comprehensiveAnalysis = ref(null)

    let historyTimer = null
    let trendAnalysisTimer = null

    const addEmotionRecord = (emotion, confidence, faces) => {
        const record = {
            timestamp: Date.now(),
            emotion,
            confidence,
            faces: faces ? faces.map(f => ({
                bbox: f.bbox,
                emotion: f.emotion,
                confidence: f.confidence
            })) : []
        }

        emotionHistory.value.push(record)
        if (emotionHistory.value.length > HISTORY_MAX_LENGTH) {
            emotionHistory.value.shift()
        }
    }

    const saveHistory = async (emotion, confidence, faces) => {
        try {
            const savedFaces = faces ? faces.map(f => ({
                bbox: f.bbox,
                emotion: f.emotion,
                confidence: f.confidence
            })) : []

            await saveHistoryRecord({
                detection_type: 'realtime',
                results: savedFaces,
                source: '实时检测',
                image_path: '',
                image_type: 'realtime',
                thumbnail: '',
                dominant_emotion: emotion,
                confidence: confidence,
                detected_faces: savedFaces
            })
            
        } catch (error) {
            logger.error('保存实时检测历史记录失败:', error)
        }
    }

    const startHistoryTimer = (getCurrentEmotion, getCurrentConfidence, getCurrentFaces) => {
        stopHistoryTimer()
        historyTimer = setInterval(() => {
            const emotion = getCurrentEmotion()
            const confidence = getCurrentConfidence()
            const faces = getCurrentFaces()
            if (emotion && confidence) {
                addEmotionRecord(emotion, confidence, faces)
                saveHistory(emotion, confidence, faces)
            }
        }, 5000)
    }

    const stopHistoryTimer = () => {
        if (historyTimer) {
            clearInterval(historyTimer)
            historyTimer = null
        }
    }

    const clearEmotionHistory = () => {
        emotionHistory.value = []
        trendAnalysis.value = null
        textAnalysis.value = null
        comprehensiveAnalysis.value = null
    }

    const performTrendAnalysis = async () => {
        if (emotionHistory.value.length < 5) return

        try {
            const emotions = emotionHistory.value.map(r => r.emotion)
            const data = await analyzeEmotionTrend({ emotions })
            trendAnalysis.value = data
        } catch (error) {
            logger.warn('情绪趋势分析失败:', error)
        }
    }

    const startTrendAnalysisTimer = () => {
        stopTrendAnalysisTimer()
        trendAnalysisTimer = setInterval(() => {
            performTrendAnalysis()
        }, 15000)
    }

    const stopTrendAnalysisTimer = () => {
        if (trendAnalysisTimer) {
            clearInterval(trendAnalysisTimer)
            trendAnalysisTimer = null
        }
    }

    return {
        emotionHistory,
        trendAnalysis,
        textAnalysis,
        comprehensiveAnalysis,
        addEmotionRecord,
        saveHistory,
        startHistoryTimer,
        stopHistoryTimer,
        clearEmotionHistory,
        performTrendAnalysis,
        startTrendAnalysisTimer,
        stopTrendAnalysisTimer
    }
}