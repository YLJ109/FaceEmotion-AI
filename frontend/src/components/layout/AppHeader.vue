<template>
    <header class="top-navbar">
        <div class="navbar-left">
            <div class="logo-icon-mini">
                <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"
                    stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10" />
                    <path d="M8 14s1.5 2 4 2 4-2 4-2" />
                    <line x1="9" y1="9" x2="9.01" y2="9" />
                    <line x1="15" y1="9" x2="15.01" y2="9" />
                </svg>
            </div>
            <div class="logo-text-wrapper">
                <h1 class="logo">AI情感检测系统</h1>
                <span class="logo-sub">智能情绪识别平台</span>
            </div>
        </div>
        <div class="navbar-right">
            <!-- ✅ 性能监控按钮 -->
            <el-tooltip content="性能监控 (Ctrl+P)" placement="bottom">
                <button class="nav-tool-btn" :class="{ active: performancePanelVisible }" @click="togglePerformanceMonitor">
                    <span class="btn-icon">🖥️</span>
                    <span class="btn-label">性能监控</span>
                    <span class="btn-arrow">{{ performancePanelVisible ? '▲' : '▼' }}</span>
                </button>
            </el-tooltip>

            <!-- ✅ 新增: AI音乐按钮 -->
            <el-tooltip :content="musicOn ? 'AI音乐控制面板' : '开启AI音乐'" placement="bottom">
                <button class="nav-tool-btn" :class="{ active: musicPanelVisible }" @click="toggleMusicPanel">
                    <span class="btn-icon">🎵</span>
                    <span class="btn-label">{{ musicOn ? 'AI音乐 ON' : 'AI音乐' }}</span>
                    <span v-if="musicOn" class="music-badge"></span>
                    <span class="btn-arrow">{{ musicPanelVisible ? '▲' : '▼' }}</span>
                </button>
            </el-tooltip>

            <!-- 情绪分析按钮 -->
            <EmotionAnalyzer 
                :show-panel="emotionPanelVisible"
                @toggle="toggleEmotionPanel"
            />

        </div>
    </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import EmotionAnalyzer from '@/components/header/EmotionAnalyzer.vue'

// ✅ 新增: 音乐状态
defineProps({
    musicOn: {
        type: Boolean,
        default: false
    }
})

const emit = defineEmits(['navigate', 'toggle-music-panel'])

// 面板可见状态
const performancePanelVisible = ref(false)
const musicPanelVisible = ref(false)
const emotionPanelVisible = ref(false)

// 隐藏其他面板
const hideOtherPanels = (exceptPanel) => {
    if (exceptPanel !== 'performance') {
        performancePanelVisible.value = false
        window.dispatchEvent(new CustomEvent('toggle-performance-monitor', { detail: { visible: false } }))
    }
    if (exceptPanel !== 'music') {
        musicPanelVisible.value = false
        emit('toggle-music-panel', false)
    }
    if (exceptPanel !== 'emotion') {
        emotionPanelVisible.value = false
    }
}

// 性能监控切换 - 发送全局事件
const togglePerformanceMonitor = () => {
    const newState = !performancePanelVisible.value
    if (newState) {
        hideOtherPanels('performance')
    }
    performancePanelVisible.value = newState
    window.dispatchEvent(new CustomEvent('toggle-performance-monitor', { detail: { visible: newState } }))
}

// AI音乐面板切换
const toggleMusicPanel = () => {
    const newState = !musicPanelVisible.value
    if (newState) {
        hideOtherPanels('music')
    }
    musicPanelVisible.value = newState
    emit('toggle-music-panel', newState)
}

// 情绪分析面板切换
const toggleEmotionPanel = () => {
    const newState = !emotionPanelVisible.value
    if (newState) {
        hideOtherPanels('emotion')
    }
    emotionPanelVisible.value = newState
}

// 监听性能监控面板状态变化
const handlePerformanceToggle = (e) => {
    performancePanelVisible.value = e.detail?.visible ?? !performancePanelVisible.value
}

// 监听AI音乐面板状态变化
const handleMusicToggle = (e) => {
    musicPanelVisible.value = e.detail?.visible ?? !musicPanelVisible.value
}

// 监听点击外部区域关闭面板
const handleClickOutside = (e) => {
    const target = e.target
    if (!target.closest('.navbar-right')) {
        hideOtherPanels(null)
    }
}

onMounted(() => {
    window.addEventListener('performance-monitor-toggled', handlePerformanceToggle)
    window.addEventListener('music-panel-toggled', handleMusicToggle)
    document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
    window.removeEventListener('performance-monitor-toggled', handlePerformanceToggle)
    window.removeEventListener('music-panel-toggled', handleMusicToggle)
    document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* ===== 顶部导航栏 ===== */
.top-navbar {
    height: 64px;
    padding: 0 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    /* ✅ 优化: 使用主题背景色,添加明显边框验证主题切换 */
    background: var(--card-bg);
    border-bottom: 2px solid var(--primary);
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.15);
    z-index: 100;
    /* ✅ 优化: 背景色和边框色跟随主题切换,0.3s 与主题动画同步 */
    transition: background 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
    flex-shrink: 0;
    position: relative;
}

.top-navbar::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 5%;
    width: 90%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--primary), transparent);
    opacity: 0.4;
}

.navbar-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.logo-icon-mini {
    width: 45px;
    height: 45px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    /* font-weight: 800; */
    color: var(--text);
    background: var(--gradient);
    /* box-shadow: 0 0 20px rgba(113, 57, 255, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2); */
    transition: all 0.3s ease;
}

.logo-icon-mini:hover {
    transform: scale(1.05);
    /* box-shadow: 0 0 24px rgba(113, 57, 255, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.3); */
}

.logo-text-wrapper {
    display: flex;
    flex-direction: column;
}

.logo {
    font-size: 1.2rem;
    font-weight: 100;
    letter-spacing: -0.3px;
    /* ✅ 使用主题色变量,确保在所有主题下都清晰可见 */
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin: 0;
    /* 添加文字阴影提升对比度 */
    /* filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1)); */
}

.logo-sub {
    font-size: 14px;
    color: var(--text-secondary);
    /* font-weight: 500; */
    letter-spacing: 0.8px;
    opacity: 0.7;
}

.navbar-right {
    display: flex;
    gap: 8px;
    align-items: center;
}

/* ✅ 工具按钮样式 - 与情绪分析按钮保持一致 */
.nav-tool-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 14px;
    background: rgba(139, 92, 246, 0.1);
    border: 1px solid rgba(139, 92, 246, 0.2);
    border-radius: 20px;
    color: var(--text);
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 14px;
    font-weight: 500;
}

.nav-tool-btn:hover {
    background: rgba(139, 92, 246, 0.2);
    border-color: rgba(139, 92, 246, 0.4);
}

.nav-tool-btn.active {
    background: rgba(139, 92, 246, 0.2);
    border-color: rgba(139, 92, 246, 0.5);
}

.nav-tool-btn .btn-icon {
    font-size: 16px;
}

.nav-tool-btn .btn-label {
    white-space: nowrap;
}

.nav-tool-btn .btn-arrow {
    font-size: 12px;
    opacity: 0.7;
}

.music-badge {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #67C23A;
    animation: musicPulse 2s ease-in-out infinite;
}

@keyframes musicPulse {

    0%,
    100% {
        /* box-shadow: 0 0 4px rgba(103, 194, 58, 0.6); */
    }

    50% {
        /* box-shadow: 0 0 8px rgba(103, 194, 58, 1); */
    }
}
</style>
