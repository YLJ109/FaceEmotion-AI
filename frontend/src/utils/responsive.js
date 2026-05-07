/**
 * 响应式工具函数
 * 提供断点检测和响应式能力
 */

export const breakpoints = {
  xs: 0,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536
}

export const breakpointNames = ['xs', 'sm', 'md', 'lg', 'xl', '2xl']

/**
 * 获取当前断点名称
 */
export function getBreakpoint() {
  const width = window.innerWidth
  
  if (width < breakpoints.sm) return 'xs'
  if (width < breakpoints.md) return 'sm'
  if (width < breakpoints.lg) return 'md'
  if (width < breakpoints.xl) return 'lg'
  if (width < breakpoints['2xl']) return 'xl'
  return '2xl'
}

/**
 * 判断是否在指定断点以下
 */
export function isBelow(breakpoint) {
  const width = window.innerWidth
  return width < breakpoints[breakpoint]
}

/**
 * 判断是否在指定断点以上
 */
export function isAbove(breakpoint) {
  const width = window.innerWidth
  return width >= breakpoints[breakpoint]
}

/**
 * 获取断点对应的列数
 */
export function getGridCols(breakpointsConfig = {}) {
  const bp = getBreakpoint()
  const config = {
    xs: 1,
    sm: 2,
    md: 2,
    lg: 3,
    xl: 4,
    ...breakpointsConfig
  }
  return config[bp]
}

/**
 * 获取容器最大宽度
 */
export function getContainerMaxWidth() {
  const bp = getBreakpoint()
  const widths = {
    xs: '100%',
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px'
  }
  return widths[bp]
}

/**
 * 创建响应式观察者
 */
export function createBreakpointObserver(callback) {
  let currentBreakpoint = getBreakpoint()
  
  const handleResize = () => {
    const newBreakpoint = getBreakpoint()
    if (newBreakpoint !== currentBreakpoint) {
      currentBreakpoint = newBreakpoint
      callback(newBreakpoint)
    }
  }
  
  window.addEventListener('resize', handleResize, { passive: true })
  
  return () => {
    window.removeEventListener('resize', handleResize)
  }
}

/**
 * Vue 组合式函数：响应式断点
 */
export function useBreakpoint() {
  if (typeof window === 'undefined') {
    return { breakpoint: 'lg' }
  }
  
  const { ref, onMounted, onUnmounted } = require('vue')
  const breakpoint = ref(getBreakpoint())
  let cleanup = null
  
  onMounted(() => {
    cleanup = createBreakpointObserver((newBp) => {
      breakpoint.value = newBp
    })
  })
  
  onUnmounted(() => {
    if (cleanup) cleanup()
  })
  
  return { breakpoint }
}

/**
 * Vue 组合式函数：响应式宽度
 */
export function useWindowWidth() {
  if (typeof window === 'undefined') {
    return { width: 1280 }
  }
  
  const { ref, onMounted, onUnmounted } = require('vue')
  const width = ref(window.innerWidth)
  
  const handleResize = () => {
    width.value = window.innerWidth
  }
  
  onMounted(() => {
    window.addEventListener('resize', handleResize, { passive: true })
  })
  
  onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
  })
  
  return { width }
}