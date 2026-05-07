<template>
  <div class="stat-card" :class="[variantClasses, { 'stat-card--animated': animated }]">
    <div class="stat-card__icon" :class="iconVariantClasses">
      <slot name="icon">
        <component :is="icon" />
      </slot>
    </div>
    
    <div class="stat-card__content">
      <p class="stat-card__label">{{ label }}</p>
      <p class="stat-card__value">
        <span v-if="prefix">{{ prefix }}</span>
        <span class="stat-card__number">{{ animated ? displayValue : value }}</span>
        <span v-if="suffix">{{ suffix }}</span>
      </p>
      
      <div v-if="trend !== undefined" class="stat-card__trend" :class="trendClasses">
        <component :is="trendIcon" />
        <span>{{ Math.abs(trend).toFixed(1) }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup>import { ref, computed, watch, onMounted } from 'vue';
import { TrendingUp, TrendingDown, Minus } from '@element-plus/icons-vue';
const props = defineProps({
 value: {
 type: Number,
 default: 0
 },
 label: {
 type: String,
 default: ''
 },
 prefix: {
 type: String,
 default: ''
 },
 suffix: {
 type: String,
 default: ''
 },
 variant: {
 type: String,
 default: 'default',
 validator: (value) => ['default', 'primary', 'happy', 'sad', 'angry', 'surprise', 'fear', 'disgust', 'neutral'].includes(value)
 },
 trend: {
 type: Number,
 default: undefined
 },
 animated: {
 type: Boolean,
 default: true
 },
 icon: {
 type: Object,
 default: null
 },
 decimals: {
 type: Number,
 default: 0
 }
});
const displayValue = ref(0);
const variantClasses = computed(() => ({
 'stat-card--primary': props.variant === 'primary',
 'stat-card--happy': props.variant === 'happy',
 'stat-card--sad': props.variant === 'sad',
 'stat-card--angry': props.variant === 'angry',
 'stat-card--surprise': props.variant === 'surprise',
 'stat-card--fear': props.variant === 'fear',
 'stat-card--disgust': props.variant === 'disgust',
 'stat-card--neutral': props.variant === 'neutral'
}));
const iconVariantClasses = computed(() => ({
 'stat-card__icon--primary': props.variant === 'primary',
 'stat-card__icon--happy': props.variant === 'happy',
 'stat-card__icon--sad': props.variant === 'sad',
 'stat-card__icon--angry': props.variant === 'angry',
 'stat-card__icon--surprise': props.variant === 'surprise',
 'stat-card__icon--fear': props.variant === 'fear',
 'stat-card__icon--disgust': props.variant === 'disgust',
 'stat-card__icon--neutral': props.variant === 'neutral'
}));
const trendClasses = computed(() => ({
 'stat-card__trend--up': props.trend > 0,
 'stat-card__trend--down': props.trend < 0,
 'stat-card__trend--neutral': props.trend === 0
}));
const trendIcon = computed(() => {
 if (props.trend > 0)
 return TrendingUp;
 if (props.trend < 0)
 return TrendingDown;
 return Minus;
});
const animateValue = (targetValue) => {
 const duration = 1000;
 const startTime = performance.now();
 const startValue = displayValue.value;
 const animate = (currentTime) => {
 const elapsed = currentTime - startTime;
 const progress = Math.min(elapsed / duration, 1);
 const easeOut = 1 - Math.pow(1 - progress, 3);
 displayValue.value = Number((startValue + (targetValue - startValue) * easeOut).toFixed(props.decimals));
 if (progress < 1) {
 requestAnimationFrame(animate);
 }
 };
 requestAnimationFrame(animate);
};
watch(() => props.value, (newVal) => {
 if (props.animated) {
 animateValue(newVal);
 }
 else {
 displayValue.value = newVal;
 }
});
onMounted(() => {
 if (props.animated) {
 animateValue(props.value);
 }
 else {
 displayValue.value = props.value;
 }
});
</script>

<style scoped>
.stat-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.stat-card--primary {
  border-color: var(--color-primary);
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(139, 92, 246, 0.05));
}

.stat-card--happy {
  border-color: var(--color-emotion-happy);
}

.stat-card--sad {
  border-color: var(--color-emotion-sad);
}

.stat-card--angry {
  border-color: var(--color-emotion-angry);
}

.stat-card--surprise {
  border-color: var(--color-emotion-surprise);
}

.stat-card--fear {
  border-color: var(--color-emotion-fear);
}

.stat-card--disgust {
  border-color: var(--color-emotion-disgust);
}

.stat-card--neutral {
  border-color: var(--color-emotion-neutral);
}

.stat-card__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  background: var(--bg-tertiary);
  flex-shrink: 0;
}

.stat-card__icon--primary {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.3), rgba(139, 92, 246, 0.1));
  color: var(--color-primary);
}

.stat-card__icon--happy {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.3), rgba(16, 185, 129, 0.1));
  color: var(--color-emotion-happy);
}

.stat-card__icon--sad {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.3), rgba(59, 130, 246, 0.1));
  color: var(--color-emotion-sad);
}

.stat-card__icon--angry {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.3), rgba(239, 68, 68, 0.1));
  color: var(--color-emotion-angry);
}

.stat-card__icon--surprise {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.3), rgba(139, 92, 246, 0.1));
  color: var(--color-emotion-surprise);
}

.stat-card__icon--fear {
  background: linear-gradient(135deg, rgba(147, 51, 234, 0.3), rgba(147, 51, 234, 0.1));
  color: var(--color-emotion-fear);
}

.stat-card__icon--disgust {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.3), rgba(245, 158, 11, 0.1));
  color: var(--color-emotion-disgust);
}

.stat-card__icon--neutral {
  background: linear-gradient(135deg, rgba(107, 114, 128, 0.3), rgba(107, 114, 128, 0.1));
  color: var(--color-emotion-neutral);
}

.stat-card__content {
  flex: 1;
  min-width: 0;
}

.stat-card__label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.stat-card__value {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.stat-card__number {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--text-primary);
}

.stat-card__trend {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 600;
  margin-top: 4px;
}

.stat-card__trend--up {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}

.stat-card__trend--down {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error);
}

.stat-card__trend--neutral {
  background: rgba(107, 114, 128, 0.1);
  color: var(--text-muted);
}
</style>