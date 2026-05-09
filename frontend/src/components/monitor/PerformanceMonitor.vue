<template>
    <div class="performance-monitor" v-if="isVisible">
        <div class="monitor-header">
            <span class="monitor-title">📊 性能监控</span>
        </div>

        <div class="monitor-content">
            <!-- ✅ 摄像头帧率 -->
            <div class="metric-item">
                <div class="metric-label">
                    <span class="metric-icon">📷</span>
                    摄像头帧率
                </div>
                <div class="metric-value" :class="getFpsClass(cameraFps)">
                    {{ cameraFps.toFixed(1) }} FPS
                </div>
            </div>

            <!-- ✅ 模型推理时间 -->
            <div class="metric-item">
                <div class="metric-label">
                    <span class="metric-icon">🧠</span>
                    推理时间
                </div>
                <div class="metric-value" :class="getInferenceClass(inferenceTime)">
                    {{ inferenceTime.toFixed(1) }}ms
                </div>
            </div>

            <!-- ✅ 检测延迟 -->
            <div class="metric-item">
                <div class="metric-label">
                    <span class="metric-icon">🎯</span>
                    检测延迟
                </div>
                <div class="metric-value" :class="getLatencyClass(detectionLatency)">
                    {{ detectionLatency.toFixed(0) }}ms
                </div>
            </div>

            <!-- ✅ 网络延迟(Ping) -->
            <div class="metric-item">
                <div class="metric-label">
                    <span class="metric-icon">🌐</span>
                    网络延迟
                </div>
                <div class="metric-value" :class="getPingClass(networkLatency)">
                    {{ networkLatency.toFixed(0) }}ms
                </div>
            </div>

            <!-- ✅ 运行设备 (CPU/GPU) -->
            <div class="metric-item">
                <div class="metric-label">
                    <span class="metric-icon">{{ isUsingGpu ? '🎮' : '💻' }}</span>
                    运行设备
                </div>
                <div class="metric-value" :class="isUsingGpu ? 'good' : 'medium'">
                    {{ isUsingGpu ? 'GPU' : 'CPU' }}
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

// ✅ 真实性能数据 props
const props = defineProps({
    cameraFps: { type: Number, default: 0 },      // 摄像头帧率
    inferenceTime: { type: Number, default: 0 },  // 模型推理时间(ms)
    detectionLatency: { type: Number, default: 0 }, // 检测延迟(ms)
    networkLatency: { type: Number, default: 0 },  // 网络延迟(Ping)(ms)
    isUsingGpu: { type: Boolean, default: false }  // 是否使用GPU
})

const isVisible = ref(false)

// ✅ 性能建议
const suggestions = computed(() => {
    const tips = []

    if (props.cameraFps < 15) {
        tips.push('摄像头帧率过低，检查摄像头连接')
    }

    if (props.inferenceTime > 100) {
        tips.push('推理时间过长，建议降低分辨率')
    }

    if (props.detectionLatency > 200) {
        tips.push('检测延迟过高，后端处理可能过载')
    }

    if (props.networkLatency > 100) {
        tips.push('网络延迟过高，检查网络连接')
    }

    return tips
})

// ✅ 帧率等级
const getFpsClass = (fps) => {
    if (fps >= 25) return 'good'
    if (fps >= 15) return 'medium'
    return 'bad'
}

// ✅ 推理时间等级
const getInferenceClass = (time) => {
    if (time < 30) return 'good'
    if (time < 60) return 'medium'
    return 'bad'
}

// ✅ 检测延迟等级
const getLatencyClass = (latency) => {
    if (latency < 100) return 'good'
    if (latency < 200) return 'medium'
    return 'bad'
}

// ✅ 网络延迟(Ping)等级
const getPingClass = (latency) => {
    if (latency < 50) return 'good'
    if (latency < 100) return 'medium'
    return 'bad'
}

const toggleVisible = () => {
    isVisible.value = !isVisible.value
}

// ✅ 事件处理函数（需要保存引用以便清理）
let handleKeydown = null
let handleToggle = null

// ✅ 键盘快捷键 Ctrl+P 切换显示
onMounted(() => {
    handleKeydown = (e) => {
        if (e.ctrlKey && e.key === 'p') {
            e.preventDefault()
            toggleVisible()
        }
    }
    window.addEventListener('keydown', handleKeydown)

    // ✅ 监听导航栏的事件
    handleToggle = (e) => {
        if (e.detail?.visible !== undefined) {
            isVisible.value = e.detail.visible
        } else {
            toggleVisible()
        }
    }
    window.addEventListener('toggle-performance-monitor', handleToggle)
})

onUnmounted(() => {
    if (handleKeydown) {
        window.removeEventListener('keydown', handleKeydown)
    }
    if (handleToggle) {
        window.removeEventListener('toggle-performance-monitor', handleToggle)
    }
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
    background: color-mix(in srgb, var(--card-bg) 95%, transparent);
    backdrop-filter: blur(12px);
    border: 1px solid color-mix(in srgb, var(--border) 30%, transparent);
    border-radius: 12px;
    padding: 12px;
    z-index: 9999;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 40px color-mix(in srgb, var(--primary) 10%, transparent);
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
    border-bottom: 1px solid color-mix(in srgb, var(--border) 20%, transparent);
}

.monitor-title {
    font-size: 13px;
    font-weight: 100;
    color: var(--text);
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
    background: color-mix(in srgb, var(--primary) 5%, transparent);
    border-radius: 6px;
    transition: all 0.2s ease;
}

.metric-item:hover {
    background: color-mix(in srgb, var(--primary) 10%, transparent);
}

.metric-label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: var(--text-secondary);
    /* font-weight: 100; */
}

.metric-icon {
    font-size: 14px;
}

.metric-hint {
    font-size: 11px;
    color: var(--success);
    opacity: 0.7;
    margin-left: 4px;
}

.metric-value {
    font-size: 14px;
    /* font-weight: 800; */
    font-family: 'Consolas', 'Monaco', monospace;
}

/* 等级颜色 */
.metric-value.good {
    color: var(--success);
    text-shadow: 0 0 8px color-mix(in srgb, var(--success) 40%, transparent);
}

.metric-value.medium {
    color: var(--warning);
    text-shadow: 0 0 8px color-mix(in srgb, var(--warning) 40%, transparent);
}

.metric-value.bad {
    color: var(--error);
    text-shadow: 0 0 8px color-mix(in srgb, var(--error) 40%, transparent);
}

/* 性能建议 */
.suggestions {
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid color-mix(in srgb, var(--border) 20%, transparent);
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.suggestion-item {
    display: flex;
    align-items: flex-start;
    gap: 6px;
    font-size: 11px;
    color: var(--text);
    line-height: 1.4;
}
</style>
