<template>
  <div v-if="visible" class="loading-overlay" :class="{ 'loading-overlay--fullscreen': fullscreen }">
    <div class="loading-overlay__content">
      <div class="loading-spinner">
        <div class="loading-ring"></div>
        <div class="loading-ring loading-ring--delay-1"></div>
        <div class="loading-ring loading-ring--delay-2"></div>
      </div>
      <p v-if="text" class="loading-text">{{ text }}</p>
      <div v-if="showProgress" class="loading-progress">
        <div class="loading-progress__bar">
          <div class="loading-progress__fill" :style="{ width: `${progress}%` }"></div>
        </div>
        <span class="loading-progress__text">{{ progress.toFixed(0) }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  text: {
    type: String,
    default: '加载中...'
  },
  fullscreen: {
    type: Boolean,
    default: true
  },
  showProgress: {
    type: Boolean,
    default: false
  },
  progress: {
    type: Number,
    default: 0
  }
})
</script>

<style scoped>
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.loading-overlay--fullscreen {
  position: fixed;
}

.loading-overlay__content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-lg);
}

.loading-spinner {
  position: relative;
  width: 64px;
  height: 64px;
}

.loading-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 3px solid transparent;
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-ring--delay-1 {
  animation-delay: 0.1s;
  border-top-color: var(--color-primary-light);
}

.loading-ring--delay-2 {
  animation-delay: 0.2s;
  border-top-color: var(--color-primary-dark);
}

.loading-text {
  font-size: var(--text-base);
  color: var(--text-secondary);
}

.loading-progress {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
  width: 200px;
}

.loading-progress__bar {
  width: 100%;
  height: 6px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.loading-progress__fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary), var(--color-primary-light));
  border-radius: var(--radius-full);
  transition: width 0.3s ease;
}

.loading-progress__text {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>