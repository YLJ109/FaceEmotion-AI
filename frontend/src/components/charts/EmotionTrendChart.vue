<template>
  <div class="emotion-trend-chart" ref="chartRef"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { getEmotionName, getEmotionColor } from '@/utils/emotion'
import { useThemeStore } from '@/stores/theme'

const props = defineProps({
  emotionCounts: {
    type: Object,
    default: () => ({})
  }
})

const chartRef = ref(null)
const themeStore = useThemeStore()
let chartInstance = null

// 7种情绪列表（与项目一致）
const EMOTION_KEYS = ['happy', 'sad', 'angry', 'surprise', 'fear', 'disgust', 'neutral']

// ✅ 动态获取当前主题的 CSS 变量值
function getThemeColors() {
  const root = document.documentElement
  return {
    primary: getComputedStyle(root).getPropertyValue('--primary').trim(),
    primaryLight: getComputedStyle(root).getPropertyValue('--primary-light').trim(),
    text: getComputedStyle(root).getPropertyValue('--text').trim(),
    textSecondary: getComputedStyle(root).getPropertyValue('--text-secondary').trim(),
    border: getComputedStyle(root).getPropertyValue('--border').trim(),
    cardBg: getComputedStyle(root).getPropertyValue('--card-bg').trim()
  }
}

// ✅ 将十六进制颜色转换为 RGBA
function hexToRgba(hex, alpha = 1) {
  if (hex.startsWith('rgba')) {
    return hex.replace(/\)$/, `, ${alpha})`)
  }
  const clean = hex.replace('#', '')
  const r = parseInt(clean.substring(0, 2), 16)
  const g = parseInt(clean.substring(2, 4), 16)
  const b = parseInt(clean.substring(4, 6), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return

  // ✅ 修复: 确保 DOM 容器有正确的宽高后再初始化
  const { width, height } = chartRef.value.getBoundingClientRect()
  if (width === 0 || height === 0) {
    // 延迟初始化，等待 DOM 渲染完成
    setTimeout(() => {
      initChart()
    }, 100)
    return
  }

  chartInstance = echarts.init(chartRef.value, null, {
    renderer: 'canvas'
  })

  updateChart()
}

// 更新图表
const updateChart = () => {
  if (!chartInstance) return

  // ✅ 获取当前主题颜色（与数据看板一致）
  const colors = getThemeColors()
  const primaryColor = colors.primary
  const textColor = colors.text
  const textSecondaryColor = colors.textSecondary
  const borderColor = colors.border
  const cardBgColor = colors.cardBg

  const option = {
    backgroundColor: 'transparent',
    animationDuration: 1500,
    animationEasing: 'cubicOut',
    tooltip: {
      trigger: 'axis',
      // ✅ 使用主题变量，与数据看板一致
      backgroundColor: hexToRgba(cardBgColor, 0.92),
      borderColor: hexToRgba(primaryColor, 0.5),
      borderWidth: 1.5,
      textStyle: { color: textColor, fontSize: 13 },
      padding: [10, 14],
      borderRadius: 8,
      shadowBlur: 10,
      shadowColor: 'rgba(0, 0, 0, 0.3)',
      axisPointer: {
        type: 'cross',
        lineStyle: { color: hexToRgba(primaryColor, 0.4) },
        crossStyle: { color: hexToRgba(primaryColor, 0.4) }
      },
      formatter: (params) => {
        const emotion = EMOTION_KEYS[params[0].dataIndex]
        const emotionName = getEmotionName(emotion)
        const value = params[0].value
        const color = getEmotionColor(emotion)
        return `<div style="display: flex; align-items: center; gap: 8px;">
          <span style="color: ${color}; font-size: 14px;">●</span>
          <span style="flex: 1; font-weight: bold; color: ${textColor};">${emotionName}</span>
          <span style="font-weight: bold; color: ${color};">${value} 次</span>
        </div>`
      }
    },
    // ✅ 移除: legend，因为柱状图不需要显示图例
    // legend: {
    //   data: EMOTION_KEYS.map(key => getEmotionName(key)),
    //   top: 0,
    //   textStyle: { color: hexToRgba(textColor, 0.7), fontSize: 12 },
    //   icon: 'circle',
    //   itemWidth: 10,
    //   itemHeight: 10
    // },
    grid: {
      left: 55,
      right: 20,
      top: 15,
      bottom: 35
    },
    xAxis: {
      type: 'category',
      data: EMOTION_KEYS.map(key => getEmotionName(key)),
      axisLabel: {
        color: hexToRgba(textColor, 0.6),
        fontSize: 12
      },
      axisLine: {
        lineStyle: {
          color: hexToRgba(primaryColor, 0.2)
        }
      },
      axisTick: {
        show: false
      }
    },
    yAxis: {
      type: 'value',
      min: 0,  // ✅ 修复: 确保Y轴从0开始
      max: 1,  // ✅ 修复: 设置默认最大值，避免0值不显示
      axisLabel: {
        color: hexToRgba(textColor, 0.6),
        fontSize: 12
      },
      axisLine: {
        lineStyle: {
          color: hexToRgba(primaryColor, 0.2)
        }
      },
      splitLine: {
        lineStyle: {
          color: hexToRgba(primaryColor, 0.08)
        }
      },
      axisTick: {
        show: false
      }
    },
    series: [{
      name: '检测次数',
      type: 'bar',
      data: EMOTION_KEYS.map((key, index) => {
        const value = props.emotionCounts[key] || 0
        // ✅ 调试: 打印数据
        if (index === 0) {
          console.debug('📊 情绪图表数据:', EMOTION_KEYS.map(k => `${getEmotionName(k)}:${props.emotionCounts[k] || 0}`))
        }
        return value
      }),
      barWidth: '50%',
      itemStyle: {
        color: (params) => {
          const emotion = EMOTION_KEYS[params.dataIndex]
          return getEmotionColor(emotion)
        },
        borderRadius: [4, 4, 0, 0],
        shadowBlur: 4,
        shadowColor: 'rgba(0, 0, 0, 0.2)'
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 8,
          shadowColor: 'rgba(0, 0, 0, 0.3)'
        }
      },
      animationDuration: 500,
      animationEasing: 'cubicOut'
    }]
  }

  chartInstance.setOption(option, true)
}

// 监听主题变化
watch(() => themeStore.currentTheme, () => {
  if (chartInstance) {
    updateChart()
  }
})

// 监听数据变化
watch(() => props.emotionCounts, () => {
  if (chartInstance) {
    updateChart()
  }
}, { deep: true })

// 响应窗口大小变化
const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
  window.removeEventListener('resize', handleResize)
})

// 暴露方法供父组件调用
defineExpose({
  resize: handleResize
})
</script>

<style scoped>
.emotion-trend-chart {
  width: 100%;
  height: 220px;
  border-radius: 8px;
  background: transparent;
}
</style>
