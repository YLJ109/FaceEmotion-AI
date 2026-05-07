<template>
  <div class="responsive-grid" :style="gridStyle">
    <slot />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useBreakpoint } from '@/utils/responsive'

const props = defineProps({
  cols: {
    type: Object,
    default: () => ({
      xs: 1,
      sm: 2,
      md: 2,
      lg: 3,
      xl: 4
    })
  },
  gap: {
    type: String,
    default: 'md',
    validator: (value) => ['xs', 'sm', 'md', 'lg', 'xl'].includes(value)
  }
})

const { breakpoint } = useBreakpoint()

const gapMap = {
  xs: 'var(--spacing-xs)',
  sm: 'var(--spacing-sm)',
  md: 'var(--spacing-md)',
  lg: 'var(--spacing-lg)',
  xl: 'var(--spacing-xl)'
}

const gridStyle = computed(() => {
  const currentCols = props.cols[breakpoint.value] || props.cols.xs
  return {
    gridTemplateColumns: `repeat(${currentCols}, minmax(0, 1fr))`,
    gap: gapMap[props.gap]
  }
})
</script>

<style scoped>
.responsive-grid {
  display: grid;
  width: 100%;
}
</style>