<template>
    <header class="top-navbar"
        :style="{ background: themeStore.currentTheme.card_bg, borderBottom: `1px solid ${themeStore.currentTheme.border}` }">
        <div class="navbar-left">
            <div class="logo-icon-mini" :style="{ background: themeStore.currentTheme.gradient }">
                <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"
                    stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10" />
                    <path d="M8 14s1.5 2 4 2 4-2 4-2" />
                    <line x1="9" y1="9" x2="9.01" y2="9" />
                    <line x1="15" y1="9" x2="15.01" y2="9" />
                </svg>
            </div>
            <div class="logo-text-wrapper">
                <h1 class="logo">AI 情感检测系统</h1>
                <span class="logo-sub">智能情绪识别平台</span>
            </div>
        </div>
        <div class="navbar-right">
            <!-- ✅ 新增: 性能监控按钮 -->
            <el-tooltip content="性能监控 (Ctrl+P)" placement="bottom">
                <el-button class="nav-tool-btn" @click="$emit('toggle-performance')">
                    <el-icon :size="18">
                        <Monitor />
                    </el-icon>
                    <span>性能监控</span>
                </el-button>
            </el-tooltip>

            <!-- ✅ 新增: AI音乐按钮 -->
            <el-tooltip :content="musicOn ? 'AI音乐控制面板' : '开启AI音乐'" placement="bottom">
                <el-button class="nav-tool-btn" :class="{ active: musicOn }" @click="$emit('toggle-music-panel')">
                    <el-icon :size="18">
                        <Headset />
                    </el-icon>
                    <span>{{ musicOn ? 'AI音乐 ON' : 'AI音乐' }}</span>
                    <span v-if="musicOn" class="music-badge"></span>
                </el-button>
            </el-tooltip>

            <!-- 主题指示器 -->
            <el-tooltip content="当前主题" placement="bottom">
                <el-button class="theme-indicator" @click="$emit('navigate', 'theme')">
                    <span class="theme-emoji">{{ themeStore.currentTheme.emoji }}</span>
                    <span>{{ themeStore.currentTheme.name }}</span>
                </el-button>
            </el-tooltip>
        </div>
    </header>
</template>

<script setup>
import { useThemeStore } from '@/stores/theme'
import { Monitor, Headset } from '@element-plus/icons-vue'

// ✅ 新增: 音乐状态
defineProps({
    musicOn: {
        type: Boolean,
        default: false
    }
})

defineEmits(['navigate', 'toggle-performance', 'toggle-music-panel'])

const themeStore = useThemeStore()
</script>

<style scoped>
/* ===== 顶部导航栏 ===== */
.top-navbar {
    height: 64px;
    padding: 0 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    background: var(--card-bg);
    border-bottom: 1px solid var(--border);
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.15);
    z-index: 100;
    /* ✅ 统一过渡时间,与背景切换同步 */
    transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
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
    width: 50px;
    height: 50px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 800;
    color: white;
    box-shadow: 0 0 20px rgba(113, 57, 255, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2);
    transition: all 0.3s ease;
}

.logo-icon-mini:hover {
    transform: scale(1.05);
    box-shadow: 0 0 24px rgba(113, 57, 255, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.logo-text-wrapper {
    display: flex;
    flex-direction: column;
}

.logo {
    font-size: 1.2rem;
    font-weight: 800;
    letter-spacing: -0.3px;
    /* ✅ 使用主题色变量,确保在所有主题下都清晰可见 */
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin: 0;
    /* 添加文字阴影提升对比度 */
    filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
}

.logo-sub {
    font-size: 14px;
    color: var(--text-secondary);
    font-weight: 500;
    letter-spacing: 0.8px;
    opacity: 0.7;
}

.navbar-right {
    display: flex;
    gap: 8px;
    align-items: center;
}

.theme-indicator {
    background: color-mix(in srgb, var(--primary) 10%, transparent) !important;
    border: 1px solid color-mix(in srgb, var(--primary) 25%, transparent) !important;
    color: var(--text) !important;
    border-radius: 50px !important;
    padding: 8px 16px !important;
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.theme-indicator:hover {
    background: color-mix(in srgb, var(--primary) 22%, transparent) !important;
    border-color: var(--primary) !important;
    box-shadow: 0 0 12px color-mix(in srgb, var(--primary) 25%, transparent);
}

.theme-emoji {
    font-size: 15px;
}

/* ✅ 新增: 工具按钮样式 */
.nav-tool-btn {
    background: color-mix(in srgb, var(--primary) 8%, transparent) !important;
    border: 1px solid color-mix(in srgb, var(--primary) 20%, transparent) !important;
    color: var(--text) !important;
    border-radius: 50px !important;
    padding: 8px 14px !important;
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    position: relative;
}

.nav-tool-btn:hover {
    background: color-mix(in srgb, var(--primary) 18%, transparent) !important;
    border-color: var(--primary) !important;
    box-shadow: 0 0 12px color-mix(in srgb, var(--primary) 25%, transparent);
    transform: translateY(-1px);
}

.nav-tool-btn.active {
    background: linear-gradient(135deg, var(--primary), #9B59B6) !important;
    border-color: transparent !important;
    color: white !important;
    box-shadow: 0 0 16px rgba(113, 57, 255, 0.4);
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
        box-shadow: 0 0 4px rgba(103, 194, 58, 0.6);
    }

    50% {
        box-shadow: 0 0 8px rgba(103, 194, 58, 1);
    }
}
</style>
