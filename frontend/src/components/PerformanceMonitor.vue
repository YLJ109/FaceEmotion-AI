<template>
    <div class="performance-monitor" v-if="isVisible">
        <div class="monitor-header">
            <span class="monitor-title">📊 性能监控</span>
            <el-button link size="small" @click="toggleVisible">
                <el-icon>
                    <Close />
                </el-icon>
            </el-button>
        </div>

        <div class="monitor-content">
            <!-- FPS -->
            <div class="metric-item">
                <div class="metric-label">
                    <span class="metric-icon">⚡</span>
                    FPS
                </div>
                <div class="metric-value" :class="getFpsClass(fps)">
                    {{ fps.toFixed(1) }}
                </div>
            </div>

            <!-- 延迟 -->
            <div class="metric-item">
                <div class="metric-label">
                    <span class="metric-icon">⏱️</span>
                    延迟
                </div>
                <div class="metric-value" :class="getLatencyClass(latency)">
                    {{ latency.toFixed(0) }}ms
                </div>
            </div>

            <!-- 跳帧率 -->
            <div class="metric-item">
                <div class="metric-label">
                    <span class="metric-icon">🔄</span>
                    跳帧率
                </div>
                <div class="metric-value" :class="getSkipRateClass(skipRate)">
                    {{ skipRate.toFixed(1) }}%
                </div>
            </div>

            <!-- GPU显存 -->
            <div class="metric-item">
                <div class="metric-label">
                    <span class="metric-icon">🎮</span>
                    GPU显存
                </div>
                <div class="metric-value" :class="getGpuClass(gpuMemory)">
                    {{ gpuMemory.toFixed(0) }}MB
                </div>
            </div>

            <!-- 检测间隔 -->
            <div class="metric-item">
                <div class="metric-label">
                    <span class="metric-icon">🎯</span>
                    检测间隔
                </div>
                <div class="metric-value">
                    {{ detectInterval }}帧
                </div>
            </div>

            <!-- ✅ 新增: HTTP延迟 -->
            <div class="metric-item">
                <div class="metric-label">
                    <span class="metric-icon">🌐</span>
                    HTTP延迟
                </div>
                <div class="metric-value" :class="getHttpLatencyClass(httpLatency)">
                    {{ httpLatency.toFixed(0) }}ms
                </div>
            </div>

            <!-- ✅ 新增: 错误率 -->
            <div class="metric-item">
                <div class="metric-label">
                    <span class="metric-icon">❌</span>
                    错误率
                </div>
                <div class="metric-value" :class="getErrorRateClass(errorRate)">
                    {{ errorRate.toFixed(1) }}%
                </div>
            </div>
        </div>

        <!-- 性能建议 -->
        <div v-if="suggestions.length" class="suggestions">
            <div v-for="(suggestion, idx) in suggestions" :key="idx" class="suggestion-item">
                <el-icon color="#F99E1A">
                    <Warning />
                </el-icon>
                <span>{{ suggestion }}</span>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Close, Warning, Monitor } from '@element-plus/icons-vue'

const props = defineProps({
    fps: { type: Number, default: 0 },
    latency: { type: Number, default: 0 },
    skipRate: { type: Number, default: 0 },
    gpuMemory: { type: Number, default: 0 },
    detectInterval: { type: Number, default: 2 },
    // ✅ 新增: HTTP延迟和错误率
    httpLatency: { type: Number, default: 0 },
    errorRate: { type: Number, default: 0 }
})

const isVisible = ref(false)

// ✅ 性能建议
const suggestions = computed(() => {
    const tips = []

    if (props.fps < 10) {
        tips.push('FPS过低，建议降低分辨率或关闭其他程序')
    }

    if (props.latency > 300) {
        tips.push('延迟过高，尝试增加跳帧间隔')
    }

    if (props.skipRate > 50) {
        tips.push('跳帧率过高，后端处理可能过载')
    }

    if (props.gpuMemory > 4000) {
        tips.push('GPU显存占用较高，注意内存泄漏')
    }

    // ✅ 新增: HTTP延迟和错误率建议
    if (props.httpLatency > 150) {
        tips.push('HTTP请求延迟过高，检查网络连接')
    }

    if (props.errorRate > 5) {
        tips.push('错误率过高，检查后端服务状态')
    }

    return tips
})

// ✅ FPS等级
const getFpsClass = (fps) => {
    if (fps >= 25) return 'good'
    if (fps >= 15) return 'medium'
    return 'bad'
}

// ✅ 延迟等级
const getLatencyClass = (latency) => {
    if (latency < 100) return 'good'
    if (latency < 200) return 'medium'
    return 'bad'
}

// ✅ 跳帧率等级
const getSkipRateClass = (rate) => {
    if (rate < 20) return 'good'
    if (rate < 40) return 'medium'
    return 'bad'
}

// ✅ GPU显存等级
const getGpuClass = (memory) => {
    if (memory < 2000) return 'good'
    if (memory < 4000) return 'medium'
    return 'bad'
}

// ✅ 新增: HTTP延迟等级
const getHttpLatencyClass = (latency) => {
    if (latency < 50) return 'good'
    if (latency < 150) return 'medium'
    return 'bad'
}

// ✅ 新增: 错误率等级
const getErrorRateClass = (rate) => {
    if (rate < 1) return 'good'
    if (rate < 5) return 'medium'
    return 'bad'
}

const toggleVisible = () => {
    isVisible.value = !isVisible.value
}

// ✅ 键盘快捷键 Ctrl+P 切换显示
onMounted(() => {
    const handleKeydown = (e) => {
        if (e.ctrlKey && e.key === 'p') {
            e.preventDefault()
            toggleVisible()
        }
    }
    window.addEventListener('keydown', handleKeydown)

    // ✅ 新增: 监听导航栏的事件
    const handleToggle = () => {
        toggleVisible()
    }
    window.addEventListener('toggle-performance-monitor', handleToggle)

    onUnmounted(() => {
        window.removeEventListener('keydown', handleKeydown)
        window.removeEventListener('toggle-performance-monitor', handleToggle)
    })
})
</script>

<style scoped>
.performance-monitor {
    position: fixed;
    top: 60px;
    /* ✅ 调整: 显示在顶部导航栏下方 */
    right: 110px;
    /* ✅ 调整: 靠右对齐 */
    width: 280px;
    background: rgba(0, 0, 0, 0.85);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 12px;
    z-index: 9999;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    animation: slideIn 0.3s ease;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.monitor-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.monitor-title {
    font-size: 13px;
    font-weight: 700;
    color: #fff;
}

.monitor-content {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.metric-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 8px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 6px;
    transition: all 0.2s ease;
}

.metric-item:hover {
    background: rgba(255, 255, 255, 0.08);
}

.metric-label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: rgba(255, 255, 255, 0.7);
    font-weight: 600;
}

.metric-icon {
    font-size: 14px;
}

.metric-value {
    font-size: 14px;
    font-weight: 800;
    font-family: 'Consolas', 'Monaco', monospace;
}

/* 等级颜色 */
.metric-value.good {
    color: #26DE81;
    text-shadow: 0 0 8px rgba(38, 222, 129, 0.4);
}

.metric-value.medium {
    color: #F99E1A;
    text-shadow: 0 0 8px rgba(249, 158, 26, 0.4);
}

.metric-value.bad {
    color: #FF4757;
    text-shadow: 0 0 8px rgba(255, 71, 87, 0.4);
}

/* 性能建议 */
.suggestions {
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.suggestion-item {
    display: flex;
    align-items: flex-start;
    gap: 6px;
    font-size: 11px;
    color: rgba(255, 255, 255, 0.8);
    line-height: 1.4;
}
</style>
