<template>
  <div class="emotion-line-chart" ref="chartRef">
    <div class="empty-state" v-show="isEmpty">
      <div class="empty-icon">📊</div>
      <p class="empty-text">暂无情绪数据</p>
      <p class="empty-hint">开始检测后将显示情绪趋势</p>
    </div>
  </div>
</template>

<script setup>import { ref, onMounted, onUnmounted, watch, computed } from 'vue';
import * as echarts from 'echarts';
import { getEmotionName, getEmotionColor } from '@/constants/emotions';
import { useThemeStore } from '@/stores/theme';
const props = defineProps({
 // 时间序列数据：[{ timestamp, emotions: { happy: 0.8, sad: 0.1, ... } }]
 emotionHistory: {
 type: Array,
 default: () => []
 }
});
const chartRef = ref(null);
const themeStore = useThemeStore();
let chartInstance = null;
let isUnmounted = false; // ✅ 修复: 跟踪组件卸载状态，防止 keep-alive 缓存时的 DOM 错误
// 从统一常量导入情绪列表
import { EMOTION_KEYS } from '@/constants/emotions';

// 判断是否为空数据
const isEmpty = computed(() => props.emotionHistory.length === 0)

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

  // ✅ 确保 DOM 容器有正确的宽高后再初始化
  const { width, height } = chartRef.value.getBoundingClientRect()
  if (width === 0 || height === 0) {
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

  const colors = getThemeColors()
  const primaryColor = colors.primary
  const textColor = colors.text
  const textSecondaryColor = colors.textSecondary
  const borderColor = colors.border
  const cardBgColor = colors.cardBg

  // 构建时间轴标签（取最近30个数据点）
  const recentData = props.emotionHistory.slice(-30)
  const timeLabels = recentData.map((item, index) => {
    return `${index + 1}s`
  })

  // 构建每种情绪的数据系列
  const series = EMOTION_KEYS.map(emotion => {
    return {
      name: getEmotionName(emotion),
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 4,
      lineStyle: {
        width: 2,
        color: getEmotionColor(emotion)
      },
      itemStyle: {
        color: getEmotionColor(emotion)
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          {
            offset: 0,
            color: hexToRgba(getEmotionColor(emotion), 0.3)
          },
          {
            offset: 1,
            color: hexToRgba(getEmotionColor(emotion), 0.05)
          }
        ])
      },
      data: recentData.map(item => item.emotions[emotion] || 0),
      animationDuration: 500,
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
      textStyle: { color: textColor, fontSize: 13 },
      padding: [10, 14],
      borderRadius: 8,
      shadowBlur: 10,
      shadowColor: 'rgba(0, 0, 0, 0.3)',
      axisPointer: {
        type: 'cross',
        lineStyle: { color: hexToRgba(primaryColor, 0.4) }
      },
      formatter: (params) => {
        let result = `<div style="font-weight: bold; margin-bottom: 8px; color: ${textColor};">第 ${params[0].name}</div>`
        params.forEach(param => {
          const value = (param.value * 100).toFixed(1)
          result += `<div style="display: flex; align-items: center; gap: 8px; margin: 4px 0;">
            <span style="color: ${param.color}; font-size: 12px;">●</span>
            <span style="flex: 1; color: ${textSecondaryColor};">${param.seriesName}</span>
            <span style="color: ${param.color}; font-weight: bold;">${value}%</span>
          </div>`
        })
        return result
      }
    },
    legend: {
      data: EMOTION_KEYS.map(key => getEmotionName(key)),
      bottom: 8,
      left: 'center',
      textStyle: { 
        color: hexToRgba(textColor, 0.7), 
        fontSize: 10,
        lineHeight: 14
      },
      icon: 'circle',
      itemWidth: 6,
      itemHeight: 6,
      itemGap: 10,
      type: 'plain',
      orient: 'horizontal'
    },
    grid: {
      left: 35,
      right: 15,
      top: 15,
      bottom: 55
    },
    xAxis: {
      type: 'category',
      data: timeLabels,
      axisLabel: {
        color: hexToRgba(textColor, 0.6),
        fontSize: 11,
        interval: 'auto'
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
      min: 0,
      max: 1,
      axisLabel: {
        color: hexToRgba(textColor, 0.6),
        fontSize: 11,
        formatter: (value) => `${(value * 100).toFixed(0)}%`
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
    series: series
  }

  chartInstance.setOption(option, true)
}

// 监听主题变化
watch(() => themeStore.currentTheme, () => {
  // ✅ 修复: 组件卸载后不再更新，防止 DOM 操作错误
  if (chartInstance && !isUnmounted) {
    updateChart()
  }
})

// 监听数据变化
watch(() => props.emotionHistory, () => {
  // ✅ 修复: 组件卸载后不再更新，防止 DOM 操作错误
  if (chartInstance && !isUnmounted) {
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
  // ✅ 修复: 先标记卸载状态，阻止 watch 继续触发更新
  isUnmounted = true
  
  // ✅ 修复: 安全释放 ECharts 实例
  if (chartInstance) {
    try {
      chartInstance.dispose()
    } catch (e) {
      console.warn('ECharts dispose error:', e)
    }
    chartInstance = null
  }
  
  window.removeEventListener('resize', handleResize)
})

// 暴露方法供父组件调用
defineExpose({
  resize: handleResize
})
</script>

<style scoped>
.emotion-line-chart {
  width: 100%;
  height: 320px;
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
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.empty-text {
  font-size: 14px;
  font-weight: 500;
  margin: 0 0 6px 0;
  color: var(--text);
}

.empty-hint {
  font-size: 12px;
  margin: 0;
  opacity: 0.7;
}
</style>
