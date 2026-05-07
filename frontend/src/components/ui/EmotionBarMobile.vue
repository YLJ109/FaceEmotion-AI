<template>
  <div class="emotion-bar-mobile">
    <div class="emotion-bar-mobile__scroll">
      <div 
        v-for="emotion in emotions" 
        :key="emotion.key"
        class="emotion-bar-mobile__item"
        :class="{ 'emotion-bar-mobile__item--active': emotion.key === activeEmotion }"
      >
        <div class="emotion-bar-mobile__icon" :style="{ background: emotion.bgColor }">
          {{ emotion.emoji }}
        </div>
        <div class="emotion-bar-mobile__info">
          <span class="emotion-bar-mobile__name">{{ emotion.name }}</span>
          <span class="emotion-bar-mobile__value">{{ emotion.value.toFixed(1) }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { EMOTION_KEYS, EMOTION_NAME_MAP, EMOTION_EMOJI_MAP, EMOTION_COLOR_MAP } from '@/constants/emotions'

const props = defineProps({
  emotionData: {
    type: Object,
    default: () => ({})
  }
})

const emotions = computed(() => {
  return EMOTION_KEYS.map(key => ({
    key,
    name: EMOTION_NAME_MAP[key] || key,
    emoji: EMOTION_EMOJI_MAP[key] || '😐',
    value: props.emotionData[key] || 0,
    color: EMOTION_COLOR_MAP[key] || '#6b7280',
    bgColor: `${EMOTION_COLOR_MAP[key] || '#6b7280'}20`
  }))
})

const activeEmotion = computed(() => {
  let maxKey = 'neutral'
  let maxValue = 0
  
  EMOTION_KEYS.forEach(key => {
    if (props.emotionData[key] > maxValue) {
      maxValue = props.emotionData[key]
      maxKey = key
    }
  })
  
  return maxKey
})
</script>

<style scoped>
.emotion-bar-mobile {
  position: relative;
  width: 100%;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: var(--spacing-sm);
}

.emotion-bar-mobile__scroll {
  display: flex;
  gap: var(--spacing-md);
  overflow-x: auto;
  overflow-y: hidden;
  scrollbar-width: none;
  -ms-overflow-style: none;
  padding-bottom: var(--spacing-xs);
}

.emotion-bar-mobile__scroll::-webkit-scrollbar {
  display: none;
}

.emotion-bar-mobile__item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm);
  border-radius: var(--radius-md);
  background: var(--bg-secondary);
  min-width: 72px;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.emotion-bar-mobile__item--active {
  background: var(--bg-hover);
  transform: scale(1.05);
}

.emotion-bar-mobile__icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.emotion-bar-mobile__info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.emotion-bar-mobile__name {
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

.emotion-bar-mobile__value {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--text-primary);
}

@media (min-width: 768px) {
  .emotion-bar-mobile {
    display: none;
  }
}
</style>