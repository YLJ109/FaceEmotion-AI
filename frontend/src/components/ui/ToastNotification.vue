<template>
  <Teleport to="body">
    <div class="toast-container">
      <TransitionGroup name="toast">
        <div 
          v-for="toast in toasts" 
          :key="toast.id"
          class="toast"
          :class="toast.variantClasses"
        >
          <span class="toast__icon">
            <component :is="toast.icon" />
          </span>
          <span class="toast__message">{{ toast.message }}</span>
          <button class="toast__close" @click="removeToast(toast.id)">
            <X />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>import { ref, markRaw } from 'vue';
import { CheckCircle, AlertCircle, Info, AlertTriangle, X } from '@element-plus/icons-vue';
const toasts = ref([]);
let toastId = 0;
const variants = {
 success: {
 icon: markRaw(CheckCircle),
 class: 'toast--success'
 },
 error: {
 icon: markRaw(AlertCircle),
 class: 'toast--error'
 },
 warning: {
 icon: markRaw(AlertTriangle),
 class: 'toast--warning'
 },
 info: {
 icon: markRaw(Info),
 class: 'toast--info'
 }
};
const addToast = (message, variant = 'info', duration = 3000) => {
 const id = ++toastId;
 const config = variants[variant];
 const toast = {
 id,
 message,
 icon: config.icon,
 variantClasses: config.class,
 timer: setTimeout(() => {
 removeToast(id);
 }, duration)
 };
 toasts.value.push(toast);
};
const removeToast = (id) => {
 const index = toasts.value.findIndex(t => t.id === id);
 if (index !== -1) {
 const toast = toasts.value[index];
 clearTimeout(toast.timer);
 toasts.value.splice(index, 1);
 }
};
const success = (message, duration) => addToast(message, 'success', duration);
const error = (message, duration) => addToast(message, 'error', duration);
const warning = (message, duration) => addToast(message, 'warning', duration);
const info = (message, duration) => addToast(message, 'info', duration);
defineExpose({
 success,
 error,
 warning,
 info,
 addToast
});
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.toast {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  min-width: 280px;
  max-width: 400px;
  border: 1px solid var(--border-color);
}

.toast--success {
  border-color: var(--color-success);
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05));
  
  .toast__icon {
    color: var(--color-success);
  }
}

.toast--error {
  border-color: var(--color-error);
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05));
  
  .toast__icon {
    color: var(--color-error);
  }
}

.toast--warning {
  border-color: var(--color-warning);
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0.05));
  
  .toast__icon {
    color: var(--color-warning);
  }
}

.toast--info {
  border-color: var(--color-info);
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(59, 130, 246, 0.05));
  
  .toast__icon {
    color: var(--color-info);
  }
}

.toast__icon {
  font-size: 18px;
  flex-shrink: 0;
}

.toast__message {
  flex: 1;
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.toast__close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: var(--radius-md);
  background: var(--bg-hover);
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
  }
}

/* 动画 */
.toast-enter-active {
  animation: slideInRight 0.3s ease-out;
}

.toast-leave-active {
  animation: slideOutRight 0.3s ease-in;
}

.toast-move {
  transition: transform 0.3s ease;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideOutRight {
  from {
    opacity: 1;
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(100%);
  }
}

@media (max-width: 640px) {
  .toast-container {
    top: 10px;
    left: 10px;
    right: 10px;
  }
  
  .toast {
    min-width: auto;
    max-width: 100%;
  }
}
</style>