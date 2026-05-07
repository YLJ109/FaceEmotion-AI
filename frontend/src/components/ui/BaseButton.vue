<template>
  <button
    class="base-button"
    :class="[
      sizeClasses,
      variantClasses,
      { 'base-button--loading': loading },
      { 'base-button--disabled': disabled || loading },
      { 'base-button--block': block }
    ]"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="base-button__loader">
      <svg class="base-button__spinner" viewBox="0 0 24 24">
        <circle class="base-button__path" cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-dasharray="1 15" />
      </svg>
    </span>
    
    <span v-if="icon && !loading" class="base-button__icon">
      <slot name="icon" />
    </span>
    
    <span v-if="!loading" class="base-button__text">
      <slot>{{ text }}</slot>
    </span>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  text: {
    type: String,
    default: ''
  },
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'outline', 'ghost', 'danger'].includes(value)
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['xs', 'sm', 'md', 'lg'].includes(value)
  },
  loading: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  block: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click'])

const handleClick = () => {
  if (!props.disabled && !props.loading) {
    emit('click')
  }
}

const variantClasses = computed(() => ({
  'base-button--primary': props.variant === 'primary',
  'base-button--secondary': props.variant === 'secondary',
  'base-button--outline': props.variant === 'outline',
  'base-button--ghost': props.variant === 'ghost',
  'base-button--danger': props.variant === 'danger'
}))

const sizeClasses = computed(() => ({
  'base-button--xs': props.size === 'xs',
  'base-button--sm': props.size === 'sm',
  'base-button--md': props.size === 'md',
  'base-button--lg': props.size === 'lg'
}))
</script>

<style scoped>
.base-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  font-family: inherit;
  font-weight: 500;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
}

.base-button--xs {
  padding: 4px 8px;
  font-size: var(--text-xs);
}

.base-button--sm {
  padding: 6px 12px;
  font-size: var(--text-sm);
}

.base-button--md {
  padding: 8px 16px;
  font-size: var(--text-base);
}

.base-button--lg {
  padding: 12px 24px;
  font-size: var(--text-lg);
}

.base-button--block {
  width: 100%;
}

.base-button--primary {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: white;
  
  &:hover:not(:disabled) {
    background: linear-gradient(135deg, var(--color-primary-light), var(--color-primary));
    box-shadow: var(--shadow-primary);
    transform: translateY(-1px);
  }
  
  &:active:not(:disabled) {
    transform: translateY(0);
  }
}

.base-button--secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  
  &:hover:not(:disabled) {
    background: var(--bg-hover);
  }
}

.base-button--outline {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  
  &:hover:not(:disabled) {
    border-color: var(--color-primary);
    color: var(--color-primary);
    background: rgba(139, 92, 246, 0.1);
  }
}

.base-button--ghost {
  background: transparent;
  color: var(--text-secondary);
  
  &:hover:not(:disabled) {
    background: var(--bg-hover);
    color: var(--text-primary);
  }
}

.base-button--danger {
  background: linear-gradient(135deg, var(--color-error), darken(var(--color-error), 10%));
  color: white;
  
  &:hover:not(:disabled) {
    background: linear-gradient(135deg, lighten(var(--color-error), 5%), var(--color-error));
    box-shadow: 0 0 20px rgba(239, 68, 68, 0.3);
  }
}

.base-button--disabled,
.base-button--loading {
  opacity: 0.6;
  cursor: not-allowed;
}

.base-button__loader {
  display: flex;
  align-items: center;
  justify-content: center;
}

.base-button__spinner {
  width: 16px;
  height: 16px;
  animation: spin 0.8s linear infinite;
}

.base-button__path {
  animation: dash 1.5s ease-in-out infinite;
}

.base-button__icon {
  display: flex;
  align-items: center;
}

.base-button__text {
  flex: 1;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes dash {
  to {
    stroke-dashoffset: -32;
  }
}
</style>