<template>
  <div id="app" class="app-container">
    <!-- 主布局 -->
    <div class="main-layout">
      <!-- 顶部导航 (提取为组件) -->
      <AppHeader :music-on="musicOn" @navigate="navigateTo" @toggle-music-panel="toggleMusicPanel" />

      <!-- 主体 -->
      <div class="main-content">
        <!-- 侧边栏 (提取为组件) -->
        <AppSidebar />

        <!-- 内容区 -->
        <main class="content-area">
          <!-- ✅ 使用 keep-alive 缓存检测组件,避免切换时丢失状态 -->
          <RouterView v-slot="{ Component }">
            <transition name="page-fade" mode="out-in">
              <keep-alive :include="['ImageDetector', 'RealtimeDetector', 'VideoDetector', 'BatchDetector']">
                <component :is="Component" :key="$route.fullPath" />
              </keep-alive>
            </transition>
          </RouterView>
        </main>
      </div>
    </div>

    <!-- AI音乐监控面板 -->
    <MusicMonitor v-model:music-on="musicOn" v-model:volume="musicVolume"
      :current-emotion="getEmotionName(currentEmotion)" :current-bpm="currentBpm" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNavigation } from '@/composables/useNavigation'
import { AppHeader, AppSidebar } from '@/components/layout'
import MusicMonitor from '@/components/feedback/MusicMonitor.vue'
import wsManager from '@/api/websocket'
import generativeAudio from '@/utils/generativeAudio'
import { getEmotionName } from '@/utils/emotion'

const router = useRouter()
const { navigateTo } = useNavigation()

// AI 生成式音乐状态
const musicOn = ref(false)
const currentEmotion = ref('neutral')
const currentBpm = ref(100)
const musicVolume = ref(50) // 默认音量50%
let latestMusicParams = null

onMounted(async () => {
  wsManager.connect().catch(() => { })

  // 监听音乐参数
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
  generativeAudio.destroy()
})

// 音乐控制面板切换
const toggleMusicPanel = () => {
  window.dispatchEvent(new CustomEvent('toggle-music-panel'))
}
</script>
