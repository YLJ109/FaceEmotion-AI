<template>
  <div class="base-progress">
    <div v-if="showLabel" class="base-progress__label">
      <span class="base-progress__text">{{ label }}</span>
      <span class="base-progress__value">{{ displayValue }}</span>
    </div>
    
    <div class="base-progress__bar">
      <div 
        class="base-progress__fill"
        :class="variantClasses"
        :style="{ width: `${clampedValue}%` }"
      >
        <div v-if="showGlow" class="base-progress__glow"></div>
      </div>
    </div>
    
    <div v-if="showStriped" class="base-progress__stripes"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  value: {
    type: Number,
    default: 0
  },
  max: {
    type: Number,
    default: 100
  },
  label: {
    type: String,
    default: ''
  },
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'happy', 'sad', 'angry', 'surprise', 'fear', 'disgust', 'neutral'].includes(value)
  },
  showLabel: {
    type: Boolean,
    default: true
  },
  showGlow: {
    type: Boolean,
    default: false
  },
  showStriped: {
    type: Boolean,
    default: false
  }
})

const clampedValue = computed(() => {
  return Math.min(Math.max(props.value / props.max * 100, 0), 100)
})

const displayValue = computed(() => {
  return `${props.value.toFixed(1)}%`
})

const variantClasses = computed(() => ({
  'base-progress__fill--primary': props.variant === 'primary',
  'base-progress__fill--happy': props.variant === 'happy',
  'base-progress__fill--sad': props.variant === 'sad',
  'base-progress__fill--angry': props.variant === 'angry',
  'base-progress__fill--surprise': props.variant === 'surprise',
  'base-progress__fill--fear': props.variant === 'fear',
  'base-progress__fill--disgust': props.variant === 'disgust',
  'base-progress__fill--neutral': props.variant === 'neutral'
}))
</script>

<style scoped>
.base-progress {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.base-progress__label {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.base-progress__text {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.base-progress__value {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--text-primary);
}

.base-progress__bar {
  position: relative;
  height: 6px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.base-progress__fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.base-progress__fill--primary {
  background: linear-gradient(90deg, var(--color-primary), var(--color-primary-light));
}

.base-progress__fill--happy {
  background: linear-gradient(90deg, var(--color-emotion-happy), lighten(var(--color-emotion-happy), 15%));
}

.base-progress__fill--sad {
  background: linear-gradient(90deg, var(--color-emotion-sad), lighten(var(--color-emotion-sad), 15%));
}

.base-progress__fill--angry {
  background: linear-gradient(90deg, var(--color-emotion-angry), lighten(var(--color-emotion-angry), 15%));
}

.base-progress__fill--surprise {
  background: linear-gradient(90deg, var(--color-emotion-surprise), lighten(var(--color-emotion-surprise), 15%));
}

.base-progress__fill--fear {
  background: linear-gradient(90deg, var(--color-emotion-fear), lighten(var(--color-emotion-fear), 15%));
}

.base-progress__fill--disgust {
  background: linear-gradient(90deg, var(--color-emotion-disgust), lighten(var(--color-emotion-disgust), 15%));
}

.base-progress__fill--neutral {
  background: linear-gradient(90deg, var(--color-emotion-neutral), lighten(var(--color-emotion-neutral), 15%));
}

.base-progress__glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: var(--radius-full);
  animation: progressGlow 2s ease-in-out infinite;
}

.base-progress__stripes {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 4px,
    rgba(255, 255, 255, 0.1) 4px,
    rgba(255, 255, 255, 0.1) 8px
  );
  border-radius: var(--radius-full);
  animation: stripes 1s linear infinite;
  pointer-events: none;
}

@keyframes progressGlow {
  0%, 100% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
}

@keyframes stripes {
  to {
    transform: translateX(-16px);
  }
}
</style>