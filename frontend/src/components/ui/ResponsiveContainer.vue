<template>
  <div class="responsive-container" :class="containerClasses">
    <slot />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useBreakpoint } from '@/utils/responsive'

const props = defineProps({
  maxWidth: {
    type: String,
    default: 'xl',
    validator: (value) => ['none', 'sm', 'md', 'lg', 'xl', '2xl'].includes(value)
  },
  fluid: {
    type: Boolean,
    default: false
  }
})

const { breakpoint } = useBreakpoint()

const containerClasses = computed(() => ({
  'responsive-container--fluid': props.fluid,
  [`responsive-container--max-${props.maxWidth}`]: !props.fluid,
  [`responsive-container--${breakpoint.value}`]: true
}))
</script>

<style scoped>
.responsive-container {
  width: 100%;
  margin-left: auto;
  margin-right: auto;
  padding-left: var(--spacing-md);
  padding-right: var(--spacing-md);
}

.responsive-container--fluid {
  max-width: none;
  padding-left: 0;
  padding-right: 0;
}

.responsive-container--max-none {
  max-width: none;
}

.responsive-container--max-sm {
  max-width: 640px;
}

.responsive-container--max-md {
  max-width: 768px;
}

.responsive-container--max-lg {
  max-width: 1024px;
}

.responsive-container--max-xl {
  max-width: 1280px;
}

.responsive-container--max-2xl {
  max-width: 1536px;
}

@media (max-width: 640px) {
  .responsive-container {
    padding-left: var(--spacing-sm);
    padding-right: var(--spacing-sm);
  }
}
</style>