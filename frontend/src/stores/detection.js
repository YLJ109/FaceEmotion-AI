/**
 * 检测状态管理 - 全局共享检测数据
 * 
 * 【优化】
 * - 统一管理检测状态，避免组件间重复实现
 * - EMA 平滑逻辑集中管理
 * - 提供计算属性简化组件逻辑
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useDetectionStore = defineStore('detection', () => {
    // === 状态 ===
    const currentFaces = ref([])
    const currentEmotion = ref(null)
    const currentConfidence = ref(0)
    const emotionScores = ref({})
    const inferenceFps = ref(0)

    // EMA 平滑缓冲区
    const _emaScores = ref({})
    const _lastGoodEmotion = ref(null)
    const _lastGoodScores = ref({})
    const _consecutiveEmpty = ref(0)

    const EMA_ALPHA = 0.15  // EMA 平滑系数 (降低以减少情绪波动)

    // === 计算属性 ===
    const dominantEmotion = computed(() => currentEmotion.value)
    const hasFaces = computed(() => currentFaces.value.length > 0)
    const faceCount = computed(() => currentFaces.value.length)

    // 获取主要情绪 (过滤低置信度)
    const mainEmotions = computed(() => {
        return Object.entries(emotionScores.value)
            .filter(([_, score]) => score > 0.05)
            .sort((a, b) => b[1] - a[1])
    })

    // === 方法 ===

    /**
     * 更新检测结果 (带 EMA 平滑)
     */
    const updateDetection = (faces, emotion, scores) => {
        if (!faces?.length) {
            // 没有检测到人脸
            _consecutiveEmpty.value++

            if (_consecutiveEmpty.value >= 2) {
                // 连续 2 次没有人脸，清除所有数据
                clearDetection()
            } else if (_lastGoodEmotion.value) {
                // 第 1 次没有人脸，快速降低置信度
                currentConfidence.value = Math.max(0, currentConfidence.value - 0.2)
            }
            return
        }

        // 重置空检测计数器
        _consecutiveEmpty.value = 0

        const rawScores = faces[0].scores

        // EMA 平滑
        if (Object.keys(_emaScores.value).length === 0) {
            // 首次检测，直接赋值
            Object.keys(rawScores).forEach(k => {
                _emaScores.value[k] = rawScores[k]
            })
            _lastGoodScores.value = { ...rawScores }
        } else {
            // 后续检测，EMA 平滑
            Object.entries(rawScores).forEach(([k, v]) => {
                _emaScores.value[k] = (_emaScores.value[k] !== undefined ? _emaScores.value[k] : 0) * (1 - EMA_ALPHA) + v * EMA_ALPHA
            })
        }

        // 计算平滑后的情绪
        const smoothedEmotion = Object.keys(_emaScores.value).reduce((a, b) =>
            _emaScores.value[a] > _emaScores.value[b] ? a : b
        )
        const smoothedConf = _emaScores.value[smoothedEmotion]

        // 更新状态
        _lastGoodEmotion.value = smoothedEmotion
        _lastGoodScores.value = { ..._emaScores.value }

        currentEmotion.value = smoothedEmotion
        currentConfidence.value = smoothedConf
        emotionScores.value = { ..._emaScores.value }
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
        _emaScores.value = {}
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
        _emaScores.value = {}
        _lastGoodEmotion.value = null
        _lastGoodScores.value = {}
    }

    return {
        // 状态
        currentFaces,
        currentEmotion,
        currentConfidence,
        emotionScores,
        inferenceFps,

        // 计算属性
        dominantEmotion,
        hasFaces,
        faceCount,
        mainEmotions,

        // 方法
        updateDetection,
        clearDetection,
        updateInferenceFps,
        resetEma
    }
})
