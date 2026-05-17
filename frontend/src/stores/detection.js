/**
 * 检测状态管理 - 全局共享检测数据
 * 
 * 【优化】
 * - 统一管理检测状态，避免组件间重复实现
 * - EMA 平滑逻辑集中管理
 * - 提供计算属性简化组件逻辑
 * - ✅ 新增: 支持各检测模块的状态持久化
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useDetectionStore = defineStore('detection', () => {
    const currentFaces = ref([])
    const currentEmotion = ref(null)
    const currentConfidence = ref(0)
    const emotionScores = ref({})
    const inferenceFps = ref(0)

    const _lastGoodEmotion = ref(null)
    const _lastGoodScores = ref({})
    const _consecutiveEmpty = ref(0)

    const imageDetectionState = ref(null)
    const videoDetectionState = ref(null)
    const batchDetectionState = ref(null)
    const realtimeDetectionState = ref(null)

    const dominantEmotion = computed(() => currentEmotion.value)
    const hasFaces = computed(() => currentFaces.value.length > 0)
    const faceCount = computed(() => currentFaces.value.length)

    const mainEmotions = computed(() => {
        return Object.entries(emotionScores.value)
            .filter(([_, score]) => score > 0.05)
            .sort((a, b) => b[1] - a[1])
    })

    const updateDetection = (faces, emotion, scores) => {
        if (!faces?.length) {
            _consecutiveEmpty.value++

            if (_consecutiveEmpty.value >= 2) {
                clearDetection()
            } else if (_lastGoodEmotion.value) {
                currentConfidence.value = Math.max(0, currentConfidence.value - 0.2)
            }
            return
        }

        _consecutiveEmpty.value = 0

        _lastGoodEmotion.value = emotion
        _lastGoodScores.value = { ...scores }

        currentEmotion.value = emotion
        currentConfidence.value = faces[0]?.confidence || 0
        emotionScores.value = { ...scores }
        currentFaces.value = faces
    }

    /**
     * 清除检测数据
     */
    const clearDetection = () => {
        currentEmotion.value = null
        currentConfidence.value = 0
        emotionScores.value = {}
        currentFaces.value = []
        _lastGoodEmotion.value = null
        _lastGoodScores.value = {}
        _consecutiveEmpty.value = 0
    }

    /**
     * 更新推理 FPS
     */
    let lastInferenceTime = 0
    let inferenceCount = 0

    const updateInferenceFps = () => {
        const now = performance.now()
        inferenceCount++

        if (now - lastInferenceTime >= 1000) {
            inferenceFps.value = inferenceCount * (1000 / (now - lastInferenceTime))
            lastInferenceTime = now
            inferenceCount = 0
        }
    }

    /**
     * 重置 EMA 缓冲区
     */
    const resetEma = () => {
        _lastGoodEmotion.value = null
        _lastGoodScores.value = {}
    }

    // ✅ 新增: 保存各检测模块的状态
    const saveImageState = (state) => {
        imageDetectionState.value = state
        
    }

    const saveVideoState = (state) => {
        videoDetectionState.value = state
        
    }

    const saveBatchState = (state) => {
        batchDetectionState.value = state
        
    }

    const saveRealtimeState = (state) => {
        realtimeDetectionState.value = state
        
    }

    // ✅ 新增: 获取各检测模块的状态
    const getImageState = () => imageDetectionState.value
    const getVideoState = () => videoDetectionState.value
    const getBatchState = () => batchDetectionState.value
    const getRealtimeState = () => realtimeDetectionState.value

    // ✅ 新增: 清除特定模块的状态
    const clearImageState = () => {
        imageDetectionState.value = null
        
    }

    const clearVideoState = () => {
        videoDetectionState.value = null
        
    }

    const clearBatchState = () => {
        batchDetectionState.value = null
        
    }

    const clearRealtimeState = () => {
        realtimeDetectionState.value = null
        
    }

    // ✅ 新增: 清除所有检测状态
    const clearAllStates = () => {
        clearImageState()
        clearVideoState()
        clearBatchState()
        clearRealtimeState()
        
    }

    return {
        // 状态
        currentFaces,
        currentEmotion,
        currentConfidence,
        emotionScores,
        inferenceFps,

        // ✅ 新增: 各检测模块状态
        imageDetectionState,
        videoDetectionState,
        batchDetectionState,
        realtimeDetectionState,

        // 计算属性
        dominantEmotion,
        hasFaces,
        faceCount,
        mainEmotions,

        // 方法
        updateDetection,
        clearDetection,
        updateInferenceFps,
        resetEma,

        // ✅ 新增: 状态持久化方法
        saveImageState,
        saveVideoState,
        saveBatchState,
        saveRealtimeState,
        getImageState,
        getVideoState,
        getBatchState,
        getRealtimeState,
        clearImageState,
        clearVideoState,
        clearBatchState,
        clearRealtimeState,
        clearAllStates
    }
})
