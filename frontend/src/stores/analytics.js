/**
 * 用户行为分析 Store
 * - 管理统计数据
 * - 情绪趋势分析
 * - 功能使用频率
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { API } from '@/api/config'
import httpMonitor from '@/utils/httpMonitor'

export const useAnalyticsStore = defineStore('analytics', () => {
    // 状态
    const stats = ref({})
    const emotionDist = ref({})
    const typeDist = ref({})
    const emotionTrend = ref([])
    const isLoading = ref(false)
    const lastUpdated = ref(null)

    // 计算属性
    const totalDetections = computed(() => stats.value.total_detections || 0)
    const avgConfidence = computed(() => stats.value.avg_confidence || 0)
    const topEmotion = computed(() => {
        if (!emotionDist.value || Object.keys(emotionDist.value).length === 0) return null

        return Object.entries(emotionDist.value)
            .sort((a, b) => b[1] - a[1])[0]?.[0] || null
    })

    const maxTrendCount = computed(() => {
        if (!emotionTrend.value.length) return 1
        let max = 0
        emotionTrend.value.forEach(day => {
            Object.values(day.emotions).forEach(count => {
                if (count > max) max = count
            })
        })
        return max || 1
    })

    // 方法
    /**
     * 获取统计数据
     */
    async function fetchStats() {
        isLoading.value = true
        try {
            const response = await httpMonitor.monitoredFetch(`${API.base}/api/analytics/stats`)

            if (response.ok) {
                const data = await response.json()
                stats.value = data.stats || {}
                emotionDist.value = data.emotion_dist || {}
                typeDist.value = data.type_dist || {}
                lastUpdated.value = new Date().toISOString()

                console.log('✅ 统计数据已更新')
            } else {
                console.warn('⚠️ 获取统计数据失败')
                // 降级: 使用模拟数据
                _useMockStats()
            }
        } catch (error) {
            console.error('❌ 获取统计数据异常:', error)
            _useMockStats()
        } finally {
            isLoading.value = false
        }
    }

    /**
     * 获取情绪趋势数据
     */
    async function fetchEmotionTrend(days = 7) {
        isLoading.value = true
        try {
            const response = await httpMonitor.monitoredFetch(
                `${API.base}/api/analytics/emotion_trend?days=${days}`
            )

            if (response.ok) {
                const data = await response.json()
                emotionTrend.value = data.trend || []
                console.log('✅ 情绪趋势数据已更新')
            } else {
                console.warn('⚠️ 获取情绪趋势失败')
                _useMockTrend()
            }
        } catch (error) {
            console.error('❌ 获取情绪趋势异常:', error)
            _useMockTrend()
        } finally {
            isLoading.value = false
        }
    }

    /**
     * 刷新所有数据
     */
    async function refreshAll() {
        await Promise.all([
            fetchStats(),
            fetchEmotionTrend()
        ])
    }

    /**
     * 记录功能使用
     */
    function logFeatureUsage(featureName, metadata = {}) {
        // 这里可以集成到后端API
        console.log(`📊 功能使用: ${featureName}`, metadata)

        // TODO: 发送到后端统计接口
        // fetch('/api/analytics/log_usage', {
        //   method: 'POST',
        //   headers: { 'Content-Type': 'application/json' },
        //   body: JSON.stringify({ feature: featureName, ...metadata })
        // })
    }

    /**
     * 重置数据
     */
    function reset() {
        stats.value = {}
        emotionDist.value = {}
        typeDist.value = {}
        emotionTrend.value = []
        lastUpdated.value = null
    }

    /**
     * 降级: 使用模拟统计数据
     */
    function _useMockStats() {
        stats.value = {
            total_detections: Math.floor(Math.random() * 1000) + 500,
            avg_confidence: (Math.random() * 0.3 + 0.6).toFixed(2),
            active_users: Math.floor(Math.random() * 50) + 10
        }

        emotionDist.value = {
            happy: Math.floor(Math.random() * 100) + 50,
            sad: Math.floor(Math.random() * 80) + 20,
            angry: Math.floor(Math.random() * 60) + 10,
            surprise: Math.floor(Math.random() * 40) + 10,
            fear: Math.floor(Math.random() * 30) + 5,
            disgust: Math.floor(Math.random() * 20) + 5,
            neutral: Math.floor(Math.random() * 90) + 30
        }

        typeDist.value = {
            realtime: Math.floor(Math.random() * 500) + 200,
            image: Math.floor(Math.random() * 300) + 100,
            video: Math.floor(Math.random() * 200) + 50
        }

        lastUpdated.value = new Date().toISOString()
    }

    /**
     * 降级: 使用模拟趋势数据
     */
    function _useMockTrend() {
        const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        const emotions = ['happy', 'sad', 'angry', 'surprise', 'neutral']

        emotionTrend.value = days.map(day => ({
            date: day,
            emotions: {
                happy: Math.floor(Math.random() * 50) + 20,
                sad: Math.floor(Math.random() * 30) + 10,
                angry: Math.floor(Math.random() * 20) + 5,
                surprise: Math.floor(Math.random() * 15) + 5,
                neutral: Math.floor(Math.random() * 40) + 15
            }
        }))
    }

    return {
        // 状态
        stats,
        emotionDist,
        typeDist,
        emotionTrend,
        isLoading,
        lastUpdated,

        // 计算属性
        totalDetections,
        avgConfidence,
        topEmotion,
        maxTrendCount,

        // 方法
        fetchStats,
        fetchEmotionTrend,
        refreshAll,
        logFeatureUsage,
        reset
    }
})
