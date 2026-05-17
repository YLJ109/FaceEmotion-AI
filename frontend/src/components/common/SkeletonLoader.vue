<template>
  <div class="skeleton-loader" :class="`skeleton-${variant}`">
    <template v-if="variant === 'card'">
      <div class="skeleton-card">
        <div class="skeleton-image skeleton-pulse" />
        <div class="skeleton-card-body">
          <div class="skeleton-line skeleton-pulse" style="width: 80%" />
          <div class="skeleton-line skeleton-pulse" style="width: 60%" />
          <div class="skeleton-line skeleton-pulse" style="width: 40%" />
        </div>
      </div>
    </template>

    <template v-else-if="variant === 'list'">
      <div v-for="i in count" :key="i" class="skeleton-list-item">
        <div class="skeleton-avatar skeleton-pulse" />
        <div class="skeleton-list-body">
          <div class="skeleton-line skeleton-pulse" style="width: 70%" />
          <div class="skeleton-line skeleton-pulse" style="width: 50%" />
        </div>
      </div>
    </template>

    <template v-else-if="variant === 'dashboard'">
      <div class="skeleton-dashboard">
        <div class="skeleton-stat skeleton-pulse" v-for="i in 4" :key="i">
          <div class="skeleton-line skeleton-pulse" style="width: 60%; height: 14px" />
          <div class="skeleton-line skeleton-pulse" style="width: 40%; height: 28px; margin-top: 8px" />
        </div>
        <div class="skeleton-chart skeleton-pulse" />
      </div>
    </template>

    <template v-else-if="variant === 'detection'">
      <div class="skeleton-detection">
        <div class="skeleton-video skeleton-pulse" />
        <div class="skeleton-controls">
          <div class="skeleton-button skeleton-pulse" />
          <div class="skeleton-button skeleton-pulse" />
        </div>
      </div>
    </template>

    <template v-else>
      <div v-for="i in count" :key="i" class="skeleton-line skeleton-pulse" :style="{ width: `${40 + Math.random() * 50}%` }" />
    </template>
  </div>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'text',
    validator: v => ['text', 'card', 'list', 'dashboard', 'detection'].includes(v)
  },
  count: {
    type: Number,
    default: 3
  }
})
</script>

<style scoped>
.skeleton-loader {
  width: 100%;
}

.skeleton-pulse {
  background: linear-gradient(90deg,
    var(--el-fill-color-light, #f0f0f0) 25%,
    var(--el-fill-color, #e0e0e0) 50%,
    var(--el-fill-color-light, #f0f0f0) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-pulse 1.5s ease-in-out infinite;
  border-radius: 4px;
}

@keyframes skeleton-pulse {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.skeleton-line {
  height: 16px;
  margin-bottom: 8px;
}

.skeleton-card {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--el-border-color-lighter, #ebeef5);
}

.skeleton-image {
  height: 180px;
  border-radius: 0;
}

.skeleton-card-body {
  padding: 16px;
}

.skeleton-list-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
}

.skeleton-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  flex-shrink: 0;
}

.skeleton-list-body {
  flex: 1;
}

.skeleton-dashboard {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.skeleton-stat {
  padding: 16px;
  border-radius: 8px;
  border: 1px solid var(--el-border-color-lighter, #ebeef5);
}

.skeleton-chart {
  grid-column: 1 / -1;
  height: 300px;
  border-radius: 8px;
  border: 1px solid var(--el-border-color-lighter, #ebeef5);
}

.skeleton-detection {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.skeleton-video {
  width: 100%;
  aspect-ratio: 4/3;
  max-height: 480px;
  border-radius: 8px;
}

.skeleton-controls {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.skeleton-button {
  width: 120px;
  height: 40px;
  border-radius: 6px;
}

@media (max-width: 768px) {
  .skeleton-dashboard {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>