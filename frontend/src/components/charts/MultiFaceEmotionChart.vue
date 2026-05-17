<template>
  <div class="multi-face-chart" ref="chartRef">
    <div class="empty-state" v-show="isEmpty">
      <div class="empty-icon">📊</div>
      <p class="empty-text">等待数据...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import * as echarts from 'echarts'
import { getEmotionName, getEmotionEmoji, getEmotionColor } from '@/constants/emotions'
import { useThemeStore } from '@/stores/theme'

const props = defineProps({
  faceHistories: {
    type: Object,
    default: () => ({})
  }
})

const chartRef = ref(null)
const themeStore = useThemeStore()
let chartInstance = null
let isUnmounted = false

const faceIds = computed(() => Object.keys(props.faceHistories).map(Number).sort((a, b) => a - b))

const isEmpty = computed(() => {
  return faceIds.value.length === 0 || faceIds.value.every(id => {
    const history = props.faceHistories[id]
    return !history || history.length === 0
  })
})

function getThemeColors() {
  const root = document.documentElement
  return {
    primary: getComputedStyle(root).getPropertyValue('--primary').trim(),
    text: getComputedStyle(root).getPropertyValue('--text').trim(),
    textSecondary: getComputedStyle(root).getPropertyValue('--text-secondary').trim(),
    border: getComputedStyle(root).getPropertyValue('--border').trim(),
    cardBg: getComputedStyle(root).getPropertyValue('--card-bg').trim()
  }
}

function hexToRgba(hex, alpha = 1) {
  if (!hex || hex.startsWith('rgba')) {
    if (hex && hex.startsWith('rgba')) {
      return hex.replace(/[\d.]+\)$/, `${alpha})`)
    }
    return `rgba(128, 128, 128, ${alpha})`
  }
  const clean = hex.replace('#', '')
  if (clean.length < 6) return `rgba(128, 128, 128, ${alpha})`
  const r = parseInt(clean.substring(0, 2), 16)
  const g = parseInt(clean.substring(2, 4), 16)
  const b = parseInt(clean.substring(4, 6), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

const FACE_COLORS = ['#10B981', '#3B82F6', '#8B5CF6', '#F59E0B', '#EF4444', '#EC4899', '#06B6D4', '#84CC16']

function getFaceColor(faceId) {
  return FACE_COLORS[faceId % FACE_COLORS.length]
}

const initChart = () => {
  if (!chartRef.value) return
  const { width, height } = chartRef.value.getBoundingClientRect()
  if (width === 0 || height === 0) {
    setTimeout(() => initChart(), 100)
    return
  }
  chartInstance = echarts.init(chartRef.value, null, { renderer: 'canvas' })
  updateChart()
}

const updateChart = () => {
  if (!chartInstance || isUnmounted) return

  const colors = getThemeColors()
  const textColor = colors.text
  const textSecondaryColor = colors.textSecondary
  const cardBgColor = colors.cardBg
  const primaryColor = colors.primary

  const ids = faceIds.value
  if (ids.length === 0) return

  const maxLen = Math.max(...ids.map(id => (props.faceHistories[id] || []).length), 0)
  if (maxLen === 0) return

  const timeLabels = Array.from({ length: maxLen }, (_, i) => `${i + 1}s`)

  const series = ids.map(id => {
    const history = props.faceHistories[id] || []
    const latestEmotion = history.length > 0 ? history[history.length - 1].emotion : 'neutral'
    const color = getEmotionColor(latestEmotion) || getFaceColor(id)
    const faceLabel = `人脸${id + 1}`

    const data = []
    for (let i = 0; i < maxLen; i++) {
      if (i < history.length) {
        data.push(history[i].confidence)
      } else {
        data.push(null)
      }
    }

    return {
      name: faceLabel,
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 3,
      lineStyle: { width: 2, color },
      itemStyle: { color },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: hexToRgba(color, 0.25) },
          { offset: 1, color: hexToRgba(color, 0.03) }
        ])
      },
      data,
      animationDuration: 400,
      animationEasing: 'cubicOut'
    }
  })

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: hexToRgba(cardBgColor, 0.95),
      borderColor: hexToRgba(primaryColor, 0.5),
      borderWidth: 1.5,
      textStyle: { color: textColor, fontSize: 12 },
      padding: [8, 12],
      borderRadius: 8,
      shadowBlur: 10,
      shadowColor: 'rgba(0, 0, 0, 0.3)',
      formatter: (params) => {
        if (!params || params.length === 0) return ''
        let result = `<div style="font-weight:bold;margin-bottom:6px;color:${textColor}">${params[0].name}</div>`
        params.forEach(param => {
          if (param.value == null) return
          const id = ids[param.seriesIndex]
          const history = props.faceHistories[id] || []
          const idx = param.dataIndex
          const item = idx < history.length ? history[idx] : null
          const emoji = item ? getEmotionEmoji(item.emotion) : ''
          const name = item ? getEmotionName(item.emotion) : ''
          const pct = (param.value * 100).toFixed(1)
          result += `<div style="display:flex;align-items:center;gap:6px;margin:3px 0">
            <span style="color:${param.color};font-size:11px">●</span>
            <span style="color:${textSecondaryColor}">${param.seriesName}</span>
            <span>${emoji} ${name}</span>
            <span style="color:${param.color};font-weight:bold;margin-left:auto">${pct}%</span>
          </div>`
        })
        return result
      }
    },
    legend: {
      data: ids.map(id => `人脸${id + 1}`),
      bottom: 4,
      left: 'center',
      textStyle: { color: hexToRgba(textColor, 0.7), fontSize: 10 },
      icon: 'roundRect',
      itemWidth: 10,
      itemHeight: 6,
      itemGap: 12
    },
    grid: { left: 40, right: 15, top: 12, bottom: 40 },
    xAxis: {
      type: 'category',
      data: timeLabels,
      axisLabel: { color: hexToRgba(textColor, 0.5), fontSize: 10, interval: 'auto' },
      axisLine: { lineStyle: { color: hexToRgba(primaryColor, 0.15) } },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 1,
      axisLabel: {
        color: hexToRgba(textColor, 0.5),
        fontSize: 10,
        formatter: (value) => `${(value * 100).toFixed(0)}%`
      },
      axisLine: { lineStyle: { color: hexToRgba(primaryColor, 0.15) } },
      splitLine: { lineStyle: { color: hexToRgba(primaryColor, 0.06) } },
      axisTick: { show: false }
    },
    series
  }

  chartInstance.setOption(option, true)
}

watch(() => themeStore.currentTheme, () => {
  if (chartInstance && !isUnmounted) updateChart()
})

watch(() => props.faceHistories, () => {
  if (chartInstance && !isUnmounted) updateChart()
}, { deep: true })

const handleResize = () => {
  if (chartInstance) chartInstance.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  isUnmounted = true
  if (chartInstance) {
    try { chartInstance.dispose() } catch (e) { /* ignore */ }
    chartInstance = null
  }
  window.removeEventListener('resize', handleResize)
})

defineExpose({ resize: handleResize })
</script>

<style scoped>
.multi-face-chart {
  width: 100%;
  height: 280px;
  border-radius: 8px;
  background: transparent;
  position: relative;
}

.empty-state {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 36px;
  margin-bottom: 8px;
  opacity: 0.5;
}

.empty-text {
  font-size: 13px;
  margin: 0;
  opacity: 0.7;
}
</style>