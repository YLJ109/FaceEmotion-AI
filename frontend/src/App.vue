<template>
  <div id="app" class="app-container">
    <!-- 动态光晕背景 -->
    <div class="bg-aura"></div>
    <div class="bg-glow-1"></div>
    <div class="bg-glow-2"></div>
    <div class="bg-glow-3"></div>

    <!-- 粒子背景 -->
    <div class="particles-container">
      <div v-for="i in particleCount" :key="i" class="particle" :style="getParticleStyle(i)"></div>
    </div>

    <!-- 主布局 -->
    <div class="main-layout">
      <!-- 顶部导航 (提取为组件) -->
      <AppHeader :music-on="musicOn" @navigate="navigateTo" @toggle-performance="togglePerformanceMonitor"
        @toggle-music-panel="toggleMusicPanel" />

      <!-- 主体 -->
      <div class="main-content">
        <!-- 侧边栏 (提取为组件) -->
        <AppSidebar />

        <!-- 内容区 -->
        <main class="content-area">
          <!-- ✅ 修复: 排除主题和设置页面,避免双重渲染 -->
          <RouterView v-if="$route.path !== '/theme' && $route.path !== '/settings'" v-slot="{ Component }">
            <transition name="page-fade" mode="out-in">
              <component :is="Component" :key="$route.fullPath" />
            </transition>
          </RouterView>

          <!-- 主题切换页面 (内联渲染) -->
          <div v-if="$route.path === '/theme'" class="page theme-page">
            <div class="theme-page-container">
              <div class="page-header">
                <h2><el-icon>
                    <Brush />
                  </el-icon> 主题切换</h2>
                <p>选择你喜欢的主题风格，系统将自动应用</p>
              </div>
              <div class="theme-grid-large">
                <div v-for="(theme, key) in themeStore.allThemes" :key="key" class="theme-card-large"
                  :class="{ active: themeStore.currentThemeName === key }" @click="themeStore.setTheme(key)"
                  :style="activeCardStyle(key)">
                  <div class="theme-preview-large" :style="{ background: theme.gradient }"></div>
                  <div class="theme-info-large">
                    <span class="theme-emoji-large">{{ theme.emoji }}</span>
                    <span class="theme-name-large">{{ theme.name }}</span>
                    <span class="theme-desc">{{ getThemeDesc(key) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 系统设置页面 (特殊处理,保留内联) -->
          <div v-if="$route.path === '/settings'" class="page settings-page">
            <div class="settings-container">
              <div class="page-header">
                <h2><el-icon>
                    <Setting />
                  </el-icon> 系统设置</h2>
                <p>配置系统参数，优化使用体验</p>
              </div>
              <div class="settings-form-panel">
                <el-form label-position="top" size="large">
                  <el-form-item label="摄像头分辨率">
                    <el-select v-model="resolution" style="width:100%">
                      <el-option label="320×240 (流畅)" value="320x240" />
                      <el-option label="640×480 (清晰)" value="640x480" />
                      <el-option label="1280×720 (高清)" value="1280x720" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="检测频率">
                    <div class="slider-group">
                      <el-slider v-model="config.detect_every_n_frames" :min="1" :max="5" show-stops />
                      <span class="slider-hint">每 {{ config.detect_every_n_frames }} 帧检测一次</span>
                    </div>
                  </el-form-item>
                  <el-form-item label="主题模式">
                    <el-radio-group v-model="themeStore.themeMode" size="large">
                      <el-radio-button value="auto">自动切换（根据情绪）</el-radio-button>
                      <el-radio-button value="manual">手动选择</el-radio-button>
                    </el-radio-group>
                  </el-form-item>
                  <el-form-item label="WebSocket 服务器地址">
                    <el-input v-model="config.ws_url" placeholder="ws://localhost:8000/ws" />
                  </el-form-item>
                  <el-form-item>
                    <el-divider />
                  </el-form-item>
                  <div class="settings-actions">
                    <el-button type="primary" round @click="saveConfig">保存设置</el-button>
                  </div>
                </el-form>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>

    <!-- 性能监控面板 -->
    <PerformanceMonitor />

    <!-- AI音乐监控面板 -->
    <MusicMonitor v-model:music-on="musicOn" v-model:volume="musicVolume"
      :current-emotion="getEmotionName(currentEmotion)" :current-bpm="currentBpm" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { ElMessage } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'
import { useNavigation } from '@/composables/useNavigation'
import { AppHeader, AppSidebar } from '@/components/layout'
import PerformanceMonitor from '@/components/PerformanceMonitor.vue'
import MusicMonitor from '@/components/MusicMonitor.vue'
import wsManager from '@/api/websocket'
// ✅ 新增: AI 生成式音频引擎
import generativeAudio from '@/utils/generativeAudio'
import { getEmotionName } from '@/utils/emotion'

const themeStore = useThemeStore()
const router = useRouter()
const route = useRoute()
const { navigateTo, getThemeDesc } = useNavigation()

const resolution = ref('640x480')

const config = reactive({
  camera_index: 0,
  detect_every_n_frames: 2,
  ws_url: 'ws://localhost:8000/ws/stream'
})

const particleCount = window.innerWidth < 768 ? 15 : 40

// WebSocket 连接
// ✅ 新增: AI 生成式音乐状态
const musicOn = ref(false)
const currentEmotion = ref('neutral')
const currentBpm = ref(100)
const musicVolume = ref(50) // 默认音量50%
let latestMusicParams = null

onMounted(async () => {
  // themeStore.init() 已在 main.js 中执行
  wsManager.connect().catch(() => { })

  // ✅ 新增: 监听音乐参数
  wsManager.onMessage((data) => {
    if (data.type === 'result' && data.music_params) {
      latestMusicParams = data.music_params
      currentEmotion.value = data.music_params.emotion || 'neutral'
      currentBpm.value = data.music_params.bpm || 100

      // 如果音乐已开启,实时更新参数
      if (musicOn.value) {
        generativeAudio.playMusic(data.music_params)
      }
    }
  })
})

onUnmounted(() => {
  wsManager.disconnect()
  // ✅ 新增: 销毁音频引擎
  generativeAudio.destroy()
})

// ✅ 新增: 性能监控切换
const togglePerformanceMonitor = () => {
  // 触发自定义事件,通知 PerformanceMonitor 组件切换显示
  window.dispatchEvent(new CustomEvent('toggle-performance-monitor'))
}

// ✅ 新增: 音乐控制面板切换
const toggleMusicPanel = () => {
  // 触发自定义事件,通知 MusicMonitor 组件切换显示
  window.dispatchEvent(new CustomEvent('toggle-music-panel'))
}

// 保存设置
const saveConfig = () => {
  localStorage.setItem('app_config', JSON.stringify(config))
  ElMessage.success('✅ 设置已保存')
}

// 主题卡片样式
const activeCardStyle = (key) => ({
  border: themeStore.currentThemeName === key
    ? `3px solid ${themeStore.currentTheme.primary}`
    : '3px solid transparent',
  boxShadow: themeStore.currentThemeName === key
    ? `0 0 30px ${themeStore.currentTheme.primary}40`
    : 'none'
})

// 粒子样式
const getParticleStyle = (index) => ({
  left: `${Math.random() * 100}%`,
  animationDelay: `${Math.random() * 20}s`,
  animationDuration: `${15 + Math.random() * 10}s`,
  width: `${1 + Math.random() * 3}px`,
  height: `${1 + Math.random() * 3}px`
})
</script>

<style>
/* ===== 全局重置 ===== */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'CustomFont', 'Inter', 'PingFang SC', 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, sans-serif;
  overflow: hidden;
  background: var(--background);
  color: var(--text);
  /* ✅ 添加背景过渡效果,防止主题切换时闪烁 */
  transition: background 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

#app {
  width: 100vw;
  height: 100vh;
}

/* ===== 主容器 ===== */
.app-container {
  width: 100vw;
  height: 100vh;
  position: relative;
}

/* ===== 布局 ===== */
.main-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: relative;
  z-index: 1;
}

/* ===== 主体 ===== */
.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* ===== 内容区 ===== */
.content-area {
  flex: 1;
  overflow: hidden;
  padding: 20px;
  height: 100%;
  background: transparent;
  position: relative;
}

.page {
  height: 100%;
  overflow: hidden;
  animation: fadeIn 0.3s ease;
}

/* ===== 页面过渡 ===== */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* ===== 主题页面 ===== */
.theme-page {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 10px;
  overflow-y: auto;
}

.theme-page-container {
  max-width: 1100px;
  width: 100%;
}

.page-header {
  text-align: center;
  margin-bottom: 28px;
}

.page-header h2 {
  font-size: 22px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #ffffff;
  margin: 0 0 8px;
}

.page-header p {
  font-size: 16px;
  color: var(--text-secondary);
  opacity: 0.7;
}

.theme-grid-large {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  gap: 14px;
}

.theme-card-large {
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: pointer;
  /* ✅ 统一过渡时间,与背景切换同步 */
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  background: var(--card-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 2px solid transparent;
}

.theme-card-large:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: var(--shadow-lg);
}

.theme-card-large.active {
  transform: scale(1.03);
  box-shadow: 0 0 30px color-mix(in srgb, var(--primary) 30%, transparent);
}

.theme-preview-large {
  height: 120px;
  width: 100%;
}

.theme-info-large {
  padding: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.theme-emoji-large {
  font-size: 30px;
  line-height: 1;
}

.theme-name-large {
  font-size: 15px;
  font-weight: 700;
  color: var(--text);
}

.theme-desc {
  font-size: 12px;
  color: var(--text-secondary);
  opacity: 0.7;
}

/* ===== 设置页面 ===== */
.settings-page {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 10px;
  overflow-y: auto;
}

.settings-container {
  max-width: 650px;
  width: 100%;
}

.settings-form-panel {
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: var(--radius-xl);
  padding: 32px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
}

.slider-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.slider-hint {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.settings-actions {
  display: flex;
  justify-content: center;
}

/* ===== 分析页 ===== */
.analytics-wrapper {
  overflow-y: auto !important;
  padding: 0 !important;
}

/* ===== 历史记录页 ===== */
.history-wrapper {
  overflow-y: auto !important;
  padding: 0 !important;
}

/* ===== 关键帧动画 ===== */
@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

@keyframes pulseGlow {

  0%,
  100% {
    box-shadow: 0 0 8px var(--primary), 0 0 16px var(--primary);
  }

  50% {
    box-shadow: 0 0 20px var(--primary), 0 0 32px var(--primary);
  }
}
</style>
