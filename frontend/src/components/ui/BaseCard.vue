<template>
  <div 
    class="base-card" 
    :class="[
      { 'base-card--hoverable': hoverable },
      { 'base-card--elevated': elevated },
      variantClasses
    ]"
  >
    <div v-if="$slots.header" class="base-card__header">
      <slot name="header" />
    </div>
    
    <div class="base-card__body">
      <slot />
    </div>
    
    <div v-if="$slots.footer" class="base-card__footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  hoverable: {
    type: Boolean,
    default: false
  },
  elevated: {
    type: Boolean,
    default: false
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'primary', 'secondary', 'success', 'warning', 'error'].includes(value)
  }
})

const variantClasses = computed(() => ({
  'base-card--primary': props.variant === 'primary',
  'base-card--secondary': props.variant === 'secondary',
  'base-card--success': props.variant === 'success',
  'base-card--warning': props.variant === 'warning',
  'base-card--error': props.variant === 'error'
}))
</script>

<style scoped>
.base-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.base-card--elevated {
  box-shadow: var(--shadow-lg);
}

.base-card--hoverable {
  cursor: pointer;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-xl);
    border-color: var(--border-light);
  }
}

.base-card--primary {
  border-color: var(--color-primary);
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(139, 92, 246, 0.05));
}

.base-card--secondary {
  background: var(--bg-secondary);
}

.base-card--success {
  border-color: var(--color-success);
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05));
}

.base-card--warning {
  border-color: var(--color-warning);
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0.05));
}

.base-card--error {
  border-color: var(--color-error);
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05));
}

.base-card__header {
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
  background: rgba(0, 0, 0, 0.1);
}

.base-card__body {
  padding: var(--spacing-md);
}

.base-card__footer {
  padding: var(--spacing-md);
  border-top: 1px solid var(--border-color);
  background: rgba(0, 0, 0, 0.1);
}
</style>