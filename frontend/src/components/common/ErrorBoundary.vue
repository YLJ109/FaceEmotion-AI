<template>
  <div class="error-boundary">
    <div v-if="hasError" class="error-container">
      <div class="error-icon">
        <svg viewBox="0 0 24 24" width="64" height="64" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
      </div>
      <h2 class="error-title">页面出现异常</h2>
      <p class="error-message">{{ errorMessage }}</p>
      <div class="error-actions">
        <button class="btn-retry" @click="retry">重试</button>
        <button class="btn-home" @click="goHome">返回首页</button>
      </div>
      <details v-if="showDetails" class="error-details">
        <summary>错误详情</summary>
        <pre>{{ errorStack }}</pre>
      </details>
    </div>
    <slot v-else />
  </div>
</template>

<script setup>
import { ref, onErrorCaptured } from 'vue'
import { useRouter } from 'vue-router'
import logger from '@/utils/logger'

const props = defineProps({
  showDetails: { type: Boolean, default: false },
  fallbackMessage: { type: String, default: '页面加载异常，请稍后重试' }
})

const router = useRouter()
const hasError = ref(false)
const errorMessage = ref('')
const errorStack = ref('')

onErrorCaptured((err, instance, info) => {
  hasError.value = true
  errorMessage.value = err.message || props.fallbackMessage
  errorStack.value = err.stack || ''

  logger.error(`[ErrorBoundary] ${info}:`, err)
  return false
})

const retry = () => {
  hasError.value = false
  errorMessage.value = ''
  errorStack.value = ''
}

const goHome = () => {
  router.push('/').catch(() => {})
}
</script>

<style scoped>
.error-boundary {
  width: 100%;
  height: 100%;
}

.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 40px 20px;
  text-align: center;
}

.error-icon {
  color: var(--el-color-danger, #f56c6c);
  margin-bottom: 20px;
  opacity: 0.8;
}

.error-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary, #303133);
  margin: 0 0 12px;
}

.error-message {
  font-size: 14px;
  color: var(--el-text-color-secondary, #909399);
  margin: 0 0 24px;
  max-width: 400px;
  line-height: 1.6;
}

.error-actions {
  display: flex;
  gap: 12px;
}

.btn-retry,
.btn-home {
  padding: 8px 20px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  border: 1px solid var(--el-border-color, #dcdfe6);
  background: var(--el-bg-color, #fff);
  color: var(--el-text-color-regular, #606266);
  transition: all 0.2s;
}

.btn-retry {
  background: var(--el-color-primary, #409eff);
  color: #fff;
  border-color: var(--el-color-primary, #409eff);
}

.btn-retry:hover {
  opacity: 0.85;
}

.btn-home:hover {
  border-color: var(--el-color-primary, #409eff);
  color: var(--el-color-primary, #409eff);
}

.error-details {
  margin-top: 24px;
  max-width: 600px;
  text-align: left;
}

.error-details summary {
  cursor: pointer;
  color: var(--el-text-color-secondary, #909399);
  font-size: 13px;
  margin-bottom: 8px;
}

.error-details pre {
  background: var(--el-fill-color-light, #f5f7fa);
  padding: 12px;
  border-radius: 6px;
  font-size: 12px;
  overflow-x: auto;
  max-height: 200px;
  line-height: 1.5;
}
</style>