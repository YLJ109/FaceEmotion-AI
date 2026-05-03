<template>
  <div class="analytics-dashboard">
    <!-- 页面头部 -->
    <div class="dashboard-header">
      <div class="header-left">
        <h2 class="header-title">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
            stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 20V10" />
            <path d="M12 20V4" />
            <path d="M6 20v-6" />
          </svg>
          数据看板
        </h2>
        <span class="header-subtitle">基于历史检测数据的统计分析</span>
      </div>
      <div class="header-right">
        <button @click="refresh" class="refresh-btn" title="刷新数据">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
            stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 2v6h-6M3 12a9 9 0 0 1 15-6.7L21 8M3 22v-6h6M21 12a9 9 0 0 1-15 6.7L3 16" />
          </svg>
        </button>
      </div>
    </div>



    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card" v-for="(stat, idx) in statCards" :key="stat.label">
        <div class="stat-card-inner">
          <div class="stat-icon-wrap" :style="{ background: stat.bg }">
            <svg v-if="idx === 0" width="20" height="20" viewBox="0 0 24 24" fill="none" :stroke="stat.color"
              stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 20V10" />
              <path d="M18 20V4" />
              <path d="M6 20v-6" />
            </svg>
            <svg v-else-if="idx === 1" width="20" height="20" viewBox="0 0 24 24" fill="none" :stroke="stat.color"
              stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="2" y="3" width="20" height="14" rx="2" />
              <path d="M8 21h8" />
              <path d="M12 17v4" />
            </svg>
            <svg v-else-if="idx === 2" width="20" height="20" viewBox="0 0 24 24" fill="none" :stroke="stat.color"
              stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="4" width="18" height="18" rx="2" />
              <path d="M16 2v4M8 2v4M3 10h18" />
            </svg>
            <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" :stroke="stat.color" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10" />
              <polyline points="12 6 12 12 16 14" />
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-label">{{ stat.label }}</span>
            <span class="stat-value">{{ stat.value }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区 -->
    <div class="charts-grid">
      <!-- ✅ 新增: 情绪趋势折线图 -->
      <div class="chart-card">
        <div class="chart-card-header">
          <h3>情绪变化趋势</h3>
          <span class="chart-hint">近7天情绪分布</span>
        </div>
        <div class="chart-body">
          <div v-if="emotionTrend.length" class="trend-line-chart">
            <!-- 图例 -->
            <div class="trend-legend">
              <div v-for="(emotion, idx) in topEmotions" :key="idx" class="legend-item">
                <span class="legend-dot" :style="{ background: getEmotionColor(emotion.key) }"></span>
                <span class="legend-label">{{ emotion.name }}</span>
              </div>
            </div>

            <!-- 折线图容器 -->
            <div class="line-chart-area">
              <svg class="trend-svg" :viewBox="`0 0 ${svgWidth} ${svgHeight}`" preserveAspectRatio="xMidYMid meet">
                <defs>
                  <!-- 渐变定义 -->
                  <linearGradient v-for="(emotion, idx) in topEmotions" :key="'grad-' + idx" :id="'gradient-' + idx"
                    x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" :stop-color="getEmotionColor(emotion.key)" stop-opacity="0.3" />
                    <stop offset="100%" :stop-color="getEmotionColor(emotion.key)" stop-opacity="0" />
                  </linearGradient>

                  <!-- 网格线渐变 -->
                  <linearGradient id="grid-gradient" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stop-color="rgba(255,255,255,0.1)" />
                    <stop offset="100%" stop-color="rgba(255,255,255,0.02)" />
                  </linearGradient>
                </defs>

                <!-- 网格线 -->
                <g class="grid-lines">
                  <line v-for="(tick, idx) in yTicks" :key="'grid-' + idx" :x1="paddingLeft" :y1="getYPosition(tick)"
                    :x2="svgWidth - paddingRight" :y2="getYPosition(tick)" stroke="rgba(255, 255, 255, 0.05)"
                    stroke-width="1" />
                </g>

                <!-- Y轴刻度标签 -->
                <g class="y-axis-labels">
                  <text v-for="(tick, idx) in yTicks" :key="'ytick-' + idx" :x="paddingLeft - 12"
                    :y="getYPosition(tick)" text-anchor="end" dominant-baseline="middle" class="axis-text">
                    {{ tick }}
                  </text>
                </g>

                <!-- 填充区域 -->
                <path v-for="(emotion, idx) in topEmotions" :key="'area-' + idx" :d="getAreaPath(emotion.key, idx)"
                  :fill="'url(#gradient-' + idx + ')'" class="area-path" />

                <!-- 折线 -->
                <path v-for="(emotion, idx) in topEmotions" :key="'line-' + idx" :d="getLinePath(emotion.key, idx)"
                  :stroke="getEmotionColor(emotion.key)" class="line-path" />

                <!-- 数据点 -->
                <template v-for="(emotion, idx) in topEmotions" :key="'points-' + idx">
                  <circle v-for="(point, pidx) in getPoints(emotion.key, idx)" :key="'point-' + idx + '-' + pidx"
                    :cx="point.x" :cy="point.y" r="3" :fill="getEmotionColor(emotion.key)" class="data-point" />
                </template>

                <!-- X轴刻度标签 -->
                <g class="x-axis-labels">
                  <text v-for="(day, idx) in emotionTrend" :key="'xlabel-' + idx" :x="getXPosition(idx)"
                    :y="svgHeight - 8" text-anchor="middle" dominant-baseline="middle" class="axis-text">
                    {{ day.date }}
                  </text>
                </g>
              </svg>
            </div>
          </div>
          <div v-else class="empty-state">
            <p>暂无趋势数据</p>
          </div>
        </div>
      </div>

      <!-- 情绪分布柱状图 -->
      <div class="chart-card">
        <div class="chart-card-header">
          <h3>情绪分布统计</h3>
          <span class="chart-hint">各情绪占比</span>
        </div>
        <div class="chart-body">
          <div v-if="Object.keys(emotionDist).length" class="emotion-chart-list">
            <div v-for="([emotionName, count], ei) in sortedEmotions" :key="ei" class="echart-item">
              <div class="echart-left">
                <!-- ✅ 使用合并后的情绪名称作为键,查找对应的颜色和图标 -->
                <span class="echart-dot" :style="{ background: getEmotionColorByChineseName(emotionName) }"></span>
                <span class="echart-name">{{ emotionName }}</span>
              </div>
              <div class="echart-bar-wrap">
                <div class="echart-bar-track">
                  <div class="echart-bar-fill" :style="{
                    width: (count / maxEmotionCount) * 100 + '%',
                    background: `linear-gradient(90deg, ${getEmotionColorByChineseName(emotionName)}, ${getEmotionColorByChineseName(emotionName)}aa)`
                  }"></div>
                </div>
              </div>
              <span class="echart-count">{{ count }}次</span>
            </div>
          </div>
          <div v-else class="empty-state">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)"
              stroke-width="1.5" opacity="0.3">
              <circle cx="12" cy="12" r="10" />
              <path d="M8 14s1.5 2 4 2 4-2 4-2" />
              <line x1="9" y1="9" x2="9.01" y2="9" />
              <line x1="15" y1="9" x2="15.01" y2="9" />
            </svg>
            <p>暂无情绪数据</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getEmotionName, getEmotionColor } from '@/utils/emotion'

const stats = ref({})
const emotionDist = ref({})
// ✅ 新增: 情绪趋势数据
const emotionTrend = ref([])

// 统计卡片数据
const statCards = computed(() => {
  const s = stats.value
  return [
    { label: '总检测次数', value: s.total_records || 0, color: '#A259FF', bg: 'rgba(162,89,255,0.12)' },
    { label: '情绪种类', value: sortedEmotions.value.length, color: '#0ABDE3', bg: 'rgba(10,189,227,0.12)' },  // ✅ 使用合并后的情绪种类数量
    { label: '主导情绪', value: dominantEmotion.value, color: '#F99E1A', bg: 'rgba(249,158,26,0.12)' },
  ]
})

// 主导情绪
const dominantEmotion = computed(() => {
  const entries = Object.entries(emotionDist.value)
  if (!entries.length) return '-'
  const sorted = entries.sort((a, b) => b[1] - a[1])
  return getEmotionName(sorted[0][0])
})

// 排序后的情绪数据（合并相同中文名的情绪）
const sortedEmotions = computed(() => {
  const entries = Object.entries(emotionDist.value)

  // ✅ 合并相同中文名的情绪（如 disgust 和 disgusted 都映射到“厌恶”）
  const mergedEmotions = {}
  entries.forEach(([emotionKey, count]) => {
    const emotionName = getEmotionName(emotionKey)
    mergedEmotions[emotionName] = (mergedEmotions[emotionName] || 0) + count
  })

  // 转换为数组并排序
  return Object.entries(mergedEmotions).sort((a, b) => b[1] - a[1])
})

const maxEmotionCount = computed(() => {
  return Math.max(...Object.values(emotionDist.value), 1)
})

// ✅ 新增: 趋势图最大计数
const maxTrendCount = computed(() => {
  if (!emotionTrend.value.length) return 1
  let max = 0
  emotionTrend.value.forEach(day => {
    Object.values(day.emotions).forEach(count => {
      if (count > max) max = count
    })
  })
  return max || 1
})

// SVG 图表配置
const svgWidth = 700  // 减小宽度，适应并排布局
const svgHeight = 260  // 减小高度，适应并排布局
const paddingLeft = 50  // 左边距
const paddingRight = 20  // 右边距
const paddingTop = 10  // 顶部间距
const paddingBottom = 35  // 底部间距，容纳X轴标签
const chartWidth = svgWidth - paddingLeft - paddingRight
const chartHeight = svgHeight - paddingTop - paddingBottom
const chartTop = paddingTop

// 获取 Y 轴位置
const getYPosition = (value) => {
  if (!yTicks.value.length) return paddingTop
  const maxVal = Math.max(...yTicks.value)
  if (maxVal === 0) return paddingTop + chartHeight
  return paddingTop + chartHeight - (value / maxVal) * chartHeight
}

// 获取 X 轴位置
const getXPosition = (index) => {
  if (!emotionTrend.value.length) return paddingLeft
  if (emotionTrend.value.length === 1) return paddingLeft + chartWidth / 2
  return paddingLeft + (index / (emotionTrend.value.length - 1)) * chartWidth
}

// 获取前7种情绪作为图例（显示更多情绪类型）
const topEmotions = computed(() => {
  if (!emotionTrend.value.length) return []
  const allEmotions = {}
  emotionTrend.value.forEach(day => {
    Object.entries(day.emotions).forEach(([emotion, count]) => {
      allEmotions[emotion] = (allEmotions[emotion] || 0) + count
    })
  })
  // 返回情绪键和中文名称的对象
  return Object.entries(allEmotions)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 7)  // ✅ 从3种增加到7种
    .map(([emotion]) => ({
      key: emotion,              // 英文键
      name: getEmotionName(emotion)  // 中文名称
    }))
})

// Y轴刻度
const yTicks = computed(() => {
  const max = maxTrendCount.value
  const steps = 5
  const step = Math.ceil(max / steps)
  return Array.from({ length: steps + 1 }, (_, i) => i * step)
})

// 获取数据点坐标
const getPoints = (emotion, emotionIdx) => {
  return emotionTrend.value.map((day, dayIdx) => {
    const x = getXPosition(dayIdx)
    const y = getYPosition(day.emotions[emotion] || 0)
    return { x, y }
  })
}

// 生成折线路径
const getLinePath = (emotion, emotionIdx) => {
  const points = getPoints(emotion, emotionIdx)
  return points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
}

// 生成填充区域路径
const getAreaPath = (emotion, emotionIdx) => {
  const points = getPoints(emotion, emotionIdx)
  const bottomY = svgHeight - paddingBottom
  const linePath = getLinePath(emotion, emotionIdx)
  return `${linePath} L ${points[points.length - 1].x} ${bottomY} L ${points[0].x} ${bottomY} Z`
}

// ✅ 根据中文情绪名称获取颜色（用于合并后的情绪显示）
const getEmotionColorByChineseName = (chineseName) => {
  // 中文名称到英文键的映射
  const chineseToEnglish = {
    '开心': 'happy',
    '悲伤': 'sad',
    '愤怒': 'angry',
    '惊讶': 'surprise',
    '恐惧': 'fear',
    '厌恶': 'disgust',
    '平静': 'neutral'
  }
  const englishKey = chineseToEnglish[chineseName]
  return englishKey ? getEmotionColor(englishKey) : '#999'
}

// 从历史记录 API 获取数据
async function fetchData() {
  try {
    const baseUrl = localStorage.getItem('api_base') || 'http://localhost:8000'

    // 获取统计信息
    const statsRes = await fetch(`${baseUrl}/api/history/stats`)
    if (statsRes.ok) {
      const statsData = await statsRes.json()
      stats.value = {
        total_records: statsData.total_records || 0,
        stats: statsData.stats || {}
      }
    }

    // 获取所有历史记录来计算分布
    const historyRes = await fetch(`${baseUrl}/api/history?limit=1000&offset=0`)
    if (historyRes.ok) {
      const historyData = await historyRes.json()
      const records = historyData.data || []

      // 计算情绪分布
      const emotions = {}

      records.forEach(record => {
        // 统计情绪
        if (record.dominant_emotion) {
          emotions[record.dominant_emotion] = (emotions[record.dominant_emotion] || 0) + 1
        }
      })

      emotionDist.value = emotions
    }

    // ✅ 新增: 获取情绪趋势数据
    try {
      const baseUrl = localStorage.getItem('api_base') || 'http://localhost:8000'
      const trendRes = await fetch(`${baseUrl}/api/analytics/emotion_trend?days=7`)
      if (trendRes.ok) {
        const trendData = await trendRes.json()
        // 后端返回格式: { daily_emotion_trend: { '2026-05-01': { happy: 10, ... }, ... } }
        // 前端需要格式: [ { date: '05-01', emotions: { happy: 10, ... } }, ... ]
        const rawTrend = trendData.daily_emotion_trend || {}
        emotionTrend.value = Object.entries(rawTrend)
          .sort(([a], [b]) => a.localeCompare(b))  // 按日期排序
          .map(([date, emotions]) => ({
            date: date.slice(5),  // '2026-05-01' -> '05-01'
            emotions
          }))
          .slice(-7)  // 只取最近7天
        console.log('情绪趋势数据:', emotionTrend.value)
      }
    } catch (e) {
      console.warn('获取情绪趋势失败，使用模拟数据:', e)
      // 降级：使用模拟数据
      emotionTrend.value = generateMockTrend()
    }
  } catch (e) {
    console.error('获取分析数据失败:', e)
  }
}

// ✅ 新增: 生成模拟趋势数据(当API不可用时)
function generateMockTrend() {
  const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  const emotions = ['happy', 'sad', 'angry', 'surprise', 'neutral']
  return days.map(day => ({
    date: day,
    emotions: {
      happy: Math.floor(Math.random() * 50) + 20,
      sad: Math.floor(Math.random() * 30) + 10,
      angry: Math.floor(Math.random() * 20) + 5,
      surprise: Math.floor(Math.random() * 15) + 5,
      neutral: Math.floor(Math.random() * 40) + 15
    }
  }))
}

const refresh = () => fetchData()

onMounted(fetchData)
</script>

<style scoped>
.analytics-dashboard {
  padding: 0;
  height: 100%;
  overflow-y: auto;
  /* 允许数据看板内部滚动 */
  overflow-x: hidden;
  /* 禁止横向滚动 */
  display: flex;
  flex-direction: column;
  gap: 12px;
  /* 减小间距 */
}

/* ===== 头部 ===== */
.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.header-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text);
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.header-subtitle {
  font-size: 15px;
  color: var(--text-secondary);
  opacity: 0.6;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.period-group .el-radio-button__inner {
  font-size: 16px !important;
  padding: 6px 14px !important;
}

.refresh-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  outline: none;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-secondary);
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.refresh-btn:hover {
  background: rgba(255, 255, 255, 0.12);
  color: var(--text);
  border-color: var(--primary);
  transform: rotate(180deg);
}

.refresh-btn:active {
  transform: scale(0.92) rotate(180deg);
}

/* ===== 洞察条 ===== */
.insights-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  flex-shrink: 0;
}

.insight-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 20px;
  font-size: 16px;
  font-weight: 500;
  background: color-mix(in srgb, var(--card-bg) 80%, transparent);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border);
  color: var(--text);
  line-height: 1.4;
}

.chip-highlight {
  border-color: rgba(255, 217, 61, 0.35);
  background: color-mix(in srgb, var(--card-bg) 70%, rgba(255, 217, 61, 0.08));
}

.chip-emotion {
  border-color: rgba(162, 89, 255, 0.35);
  background: color-mix(in srgb, var(--card-bg) 70%, rgba(162, 89, 255, 0.08));
}

.chip-info {
  border-color: rgba(10, 189, 227, 0.35);
  background: color-mix(in srgb, var(--card-bg) 70%, rgba(10, 189, 227, 0.08));
}

.chip-icon {
  display: flex;
  flex-shrink: 0;
}

.chip-text {
  line-height: 1.4;
  color: var(--text);
}

/* ===== 统计卡片 ===== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  /* 从4列改为3列 */
  gap: 10px;
  /* 减小间距 */
  flex-shrink: 0;
}

.stat-card {
  background: var(--card-bg);
  backdrop-filter: blur(16px);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  transition: all 0.3s ease;
  overflow: hidden;
}

.stat-card:hover {
  border-color: color-mix(in srgb, var(--border) 60%, var(--primary));
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.stat-card-inner {
  padding: 12px;
  /* 减小内边距 */
  display: flex;
  align-items: center;
  gap: 12px;
  /* 减小间距 */
}

.stat-icon-wrap {
  width: 38px;
  /* 减小图标容器 */
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 13px;
  /* 减小字体 */
  color: var(--text-secondary);
  font-weight: 500;
  opacity: 0.7;
  margin-bottom: 2px;
}

.stat-value {
  font-size: 22px;
  /* 减小数字大小 */
  font-weight: 800;
  color: var(--text);
  line-height: 1.1;
}

.stat-trend {
  font-size: 15px;
  font-weight: 700;
  flex-shrink: 0;
}

/* ===== 图表区 ===== */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  /* 减小间距 */
  padding-bottom: 16px;
  /* 减小底部间距 */
  flex: 1;
}

.chart-card {
  background: var(--card-bg);
  backdrop-filter: blur(16px);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  overflow: hidden;
  transition: all 0.3s ease;
}

.chart-card:hover {
  border-color: color-mix(in srgb, var(--border) 60%, var(--primary));
  box-shadow: var(--shadow-lg);
}

.chart-card.full-width {
  grid-column: 1 / -1;
}

.chart-card:not(.full-width) {
  min-height: 280px;
  /* 设置最小高度，确保有足够空间 */
  max-height: 340px;
  /* 限制最大高度，防止溢出 */
  display: flex;
  flex-direction: column;
}

.chart-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px 0;
  /* 减小内边距 */
}

.chart-card-header h3 {
  font-size: 16px;
  /* 减小标题大小 */
  font-weight: 700;
  color: var(--text);
  margin: 0;
}

.chart-hint {
  font-size: 12px;
  /* 减小提示文字 */
  color: var(--text-secondary);
  opacity: 0.5;
  font-weight: 500;
}

.chart-body {
  padding: 10px 14px 14px;
  /* 减小内边距 */
  flex: 1;
  overflow-y: auto;
  /* 内容过多时允许滚动 */
  overflow-x: hidden;
  /* 禁止横向滚动 */
}

/* 优化滚动条样式 */
.chart-body::-webkit-scrollbar {
  width: 6px;
}

.chart-body::-webkit-scrollbar-track {
  background: transparent;
}

.chart-body::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 3px;
}

.chart-body::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.25);
}

/* ✅ 新增: 情绪趋势折线图样式 */
.trend-line-chart {
  height: 260px;
  /* 减小高度，适应并排布局 */
  display: flex;
  flex-direction: column;
}

/* 图例 */
.trend-legend {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  justify-content: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.legend-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

/* 图表区域 */
.line-chart-area {
  flex: 1;
  position: relative;
  overflow: hidden;
  /* 防止溢出 */
  padding: 0 4px;
  /* 左右留出空间 */
}

.trend-svg {
  width: 100%;
  height: 100%;
  display: block;
  /* 防止底部空隙 */
  box-sizing: border-box;
  /* 包含 padding */
}

.line-path {
  fill: none;
  stroke-width: 2.5;
  stroke-linecap: round;
  stroke-linejoin: round;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.area-path {
  opacity: 0.6;
}

.data-point {
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.5));
  transition: r 0.2s ease;
}

.data-point:hover {
  r: 5;
}

.axis-text {
  font-size: 11px;
  fill: var(--text-secondary);
  opacity: 0.6;
}

/* ===== 水平柱状图 ===== */
.horizontal-bars {
  display: flex;
  flex-direction: column;
  gap: 8px;
  /* 减小间距 */
}

.hbar-row {
  display: grid;
  grid-template-columns: 90px 1fr 36px;
  align-items: center;
  gap: 10px;
}

.hbar-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  /* 减小字体 */
  color: var(--text-secondary);
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hbar-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.hbar-track-wrap {
  overflow: hidden;
}

.hbar-track {
  height: 14px;
  /* 减小高度 */
  background: color-mix(in srgb, var(--text) 6%, transparent);
  border-radius: 7px;
  overflow: hidden;
}

.hbar-fill {
  height: 100%;
  border-radius: 8px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.hbar-shine {
  position: absolute;
  top: 0;
  left: 0;
  width: 30%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.15), transparent);
  animation: shimmer 2s ease-in-out infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }

  100% {
    transform: translateX(400%);
  }
}

.hbar-value {
  font-size: 15px;
  /* 减小字体 */
  font-weight: 700;
  color: var(--text);
  text-align: right;
}

/* ===== 情绪图表 ===== */
.emotion-chart-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  /* 减小间距 */
}

.echart-item {
  display: grid;
  grid-template-columns: 70px 1fr 45px;
  /* 减小列宽 */
  align-items: center;
  gap: 8px;
  /* 减小间距 */
}

.echart-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.echart-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.echart-name {
  font-size: 14px;
  /* 减小字体 */
  font-weight: 600;
  color: var(--text);
}

.echart-bar-wrap {
  overflow: hidden;
}

.echart-bar-track {
  height: 10px;
  /* 减小高度 */
  background: color-mix(in srgb, var(--text) 6%, transparent);
  border-radius: 5px;
  overflow: hidden;
}

.echart-bar-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.echart-count {
  font-size: 14px;
  /* 减小字体 */
  font-weight: 700;
  color: var(--text-secondary);
  text-align: right;
}

/* ===== 空状态 ===== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  /* 减小间距 */
  padding: 16px;
  /* 减小内边距 */
  color: var(--text-secondary);
  font-size: 15px;
  /* 减小字体 */
}

/* ===== 响应式 ===== */
@media (max-width: 900px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    /* 从4列改为2列 */
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .stats-grid {
    grid-template-columns: 1fr;
    /* 从2列改为1列 */
  }

  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
