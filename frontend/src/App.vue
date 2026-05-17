<template>
  <div id="app" class="app-container">
    <div class="main-layout">
      <AppHeader :music-on="musicOn" @navigate="navigateTo" @toggle-music-panel="toggleMusicPanel" />

      <div class="main-content" :class="{ 'sidebar-collapsed': isCollapsed }">
        <AppSidebar />

        <main class="content-area">
          <RouterView v-slot="{ Component }">
            <transition name="page-fade" mode="out-in">
              <keep-alive
                :include="['ImageDetector', 'RealtimeDetector', 'VideoDetector', 'BatchDetector', 'BatchVideoDetector']">
                <component :is="Component" :key="$route.fullPath" />
              </keep-alive>
            </transition>
          </RouterView>
        </main>
      </div>
    </div>

    <MusicMonitor v-model:music-on="musicOn" v-model:volume="musicVolume"
      :current-emotion="getEmotionName(currentEmotion)" :current-bpm="currentBpm" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, provide } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useNavigation } from '@/composables/useNavigation'
import { AppHeader, AppSidebar } from '@/components/layout'
import MusicMonitor from '@/components/feedback/MusicMonitor.vue'
import wsManager from '@/api/websocket'
import generativeAudio from '@/utils/generativeAudio'
import { getEmotionName } from '@/constants/emotions'

const router = useRouter()
const route = useRoute()
const { navigateTo } = useNavigation()

const isCollapsed = ref(false)
provide('sidebarCollapsed', isCollapsed)

const musicOn = ref(false)
const currentEmotion = ref('neutral')
const currentBpm = ref(100)
const musicVolume = ref(50)
let latestMusicParams = null

onMounted(async () => {
  wsManager.connect().catch(() => { })

  wsManager.onMessage((data) => {
    if (data.type === 'result' && data.music_params) {
      latestMusicParams = data.music_params
      currentEmotion.value = data.music_params.emotion || 'neutral'
      currentBpm.value = data.music_params.bpm || 100

      if (musicOn.value) {
        generativeAudio.playMusic(data.music_params)
      }
    }
  })

  const handleMusicParamsUpdate = (event) => {
    const musicParams = event.detail
    if (musicParams) {
      latestMusicParams = musicParams
      currentEmotion.value = musicParams.emotion || 'neutral'
      currentBpm.value = musicParams.bpm || 100

      if (musicOn.value) {
        generativeAudio.playMusic(musicParams)
      }
    }
  }

  window.addEventListener('music-params-updated', handleMusicParamsUpdate)

  onUnmounted(() => {
    wsManager.disconnect()
    generativeAudio.destroy()
    window.removeEventListener('music-params-updated', handleMusicParamsUpdate)
  })
})

const toggleMusicPanel = (visible) => {
  window.dispatchEvent(new CustomEvent('toggle-music-panel', { detail: visible }))
}
</script>
