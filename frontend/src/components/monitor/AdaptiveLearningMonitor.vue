<template>
    <div class="adaptive-learning-monitor">
        <!-- 统计卡片 -->
        <div class="stats-grid">
            <div class="stat-card" v-for="(stat, idx) in statCards" :key="stat.label">
                <div class="stat-card-inner">
                    <div class="stat-icon-wrap" :style="{ background: stat.bg }">
                        <svg v-if="idx === 0" width="20" height="20" viewBox="0 0 24 24" fill="none"
                            :stroke="stat.color" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M12 20V10" />
                            <path d="M18 20V4" />
                            <path d="M6 20v-6" />
                        </svg>
                        <svg v-else-if="idx === 1" width="20" height="20" viewBox="0 0 24 24" fill="none"
                            :stroke="stat.color" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="10" />
                            <path d="M12 16v-4M12 8h.01" />
                        </svg>
                        <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" :stroke="stat.color"
                            stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <rect x="3" y="3" width="18" height="18" rx="2" />
                            <path d="M3 9h18M9 21V9" />
                        </svg>
                    </div>
                    <div class="stat-info">
                        <span class="stat-label">{{ stat.label }}</span>
                        <span class="stat-value">{{ stat.value }}</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- 提示信息 -->
        <el-alert v-if="!stats.calibration_ready" title="AI学习系统收集中" type="info" :closable="false" show-icon>
            <template #default>
                当前校正数据较少（{{ stats.total_corrections || 0 }}条），需要至少3条反馈才能激活校准功能。请继续提交情绪纠正反馈。
            </template>
        </el-alert>
        <el-alert v-else title="AI学习系统已激活" type="success" :closable="false" show-icon>
            <template #default>
                系统正在根据历史反馈自动优化识别准确率。当前已积累 {{ stats.total_corrections }} 条校正记录。
            </template>
        </el-alert>

        <!-- 图表区 -->
        <div class="charts-grid">
            <!-- 1. 最常见纠正模式 - 柱状图 -->
            <div class="chart-card">
                <div class="chart-card-header">
                    <h3>最常见纠正模式</h3>
                    <span class="chart-hint">前5个高频错误识别</span>
                </div>
                <div ref="correctionPatternChart" class="chart-body"></div>
            </div>

            <!-- 2. 校准矩阵热力图 -->
            <div class="chart-card">
                <div class="chart-card-header">
                    <h3>校准矩阵热力图</h3>
                    <span class="chart-hint">行=预测值，列=真实值</span>
                </div>
                <div ref="calibrationMatrixChart" class="chart-body"></div>
            </div>
        </div>

        <!-- 使用说明 -->
        <div class="usage-guide">
            <div class="guide-card">
                <h3>📊 如何解读这些数据？</h3>
                <ul>
                    <li><strong>总校正次数：</strong>用户提交的情绪纠正反馈总数，越多表示学习数据越丰富</li>
                    <li><strong>校准状态：</strong>显示系统是否已开始应用校准（至少需要3条反馈）</li>
                    <li><strong>矩阵稀疏度：</strong>反映校准矩阵中有效数据的比例，越高表示学习覆盖面越广</li>
                    <li><strong>纠正模式：</strong>展示最常见的错误识别情况，帮助了解模型的薄弱环节</li>
                    <li><strong>校准矩阵：</strong>7×7网格显示每种情绪被误判为其他情绪的频率</li>
                </ul>
            </div>
            <div class="guide-card">
                <h3>💡 如何提高准确率？</h3>
                <ul>
                    <li><strong>积极提交反馈：</strong>当识别结果不正确时，点击"纠正"按钮提交正确情绪</li>
                    <li><strong>针对性纠正：</strong>重点关注经常出错的情绪类型，多次纠正可加速学习</li>
                    <li><strong>多样化反馈：</strong>在不同场景、光线条件下提交反馈，提升模型泛化能力</li>
                    <li><strong>持续观察：</strong>定期查看监控面板，观察校准矩阵的变化趋势</li>
                </ul>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { getEmotionEmoji, getEmotionName } from '@/utils/emotion'

// ✅ 动态获取当前主题的 CSS 变量值
function getThemeColors() {
    const root = document.documentElement
    return {
        primary: getComputedStyle(root).getPropertyValue('--primary').trim(),
        primaryLight: getComputedStyle(root).getPropertyValue('--primary-light').trim(),
        secondary: getComputedStyle(root).getPropertyValue('--secondary').trim(),
        accent: getComputedStyle(root).getPropertyValue('--accent').trim(),
        highlight: getComputedStyle(root).getPropertyValue('--highlight').trim(),
        text: getComputedStyle(root).getPropertyValue('--text').trim(),
        textSecondary: getComputedStyle(root).getPropertyValue('--text-secondary').trim(),
        border: getComputedStyle(root).getPropertyValue('--border').trim(),
        cardBg: getComputedStyle(root).getPropertyValue('--card-bg').trim(),
        success: getComputedStyle(root).getPropertyValue('--success').trim(),
        warning: getComputedStyle(root).getPropertyValue('--warning').trim(),
        error: getComputedStyle(root).getPropertyValue('--error').trim()
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

const loading = ref(false)
const stats = ref({
    total_corrections: 0,
    calibration_matrix: [],
    emotion_order: [],
    top_corrections: [],
    matrix_statistics: {},
    calibration_ready: false
})

// ECharts 实例引用
const correctionPatternChart = ref(null)
const calibrationMatrixChart = ref(null)

// ECharts 实例对象
let charts = {}

// 情绪顺序
const emotionOrder = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

// 统计卡片数据
const statCards = computed(() => {
    const s = stats.value
    const colors = getThemeColors()

    // 计算矩阵稀疏度百分比
    const sparsityPercent = s.matrix_statistics?.sparsity
        ? (s.matrix_statistics.sparsity * 100).toFixed(1) + '%'
        : '0%'

    // 校准状态文本
    const calibrationStatus = s.calibration_ready ? '已激活' : '收集中'

    return [
        {
            label: '总校正次数',
            value: s.total_corrections || 0,
            color: colors.accent,
            bg: hexToRgba(colors.accent, 0.12)
        },
        {
            label: '校准状态',
            value: calibrationStatus,
            color: s.calibration_ready ? colors.success : colors.warning,
            bg: hexToRgba(s.calibration_ready ? colors.success : colors.warning, 0.12)
        },
        {
            label: '矩阵稀疏度',
            value: sparsityPercent,
            color: colors.secondary,
            bg: hexToRgba(colors.secondary, 0.12)
        }
    ]
})

// 获取学习器状态
async function fetchLearnerStatus() {
    loading.value = true
    try {
        const baseUrl = localStorage.getItem('api_base') || 'http://localhost:8000'
        const response = await fetch(`${baseUrl}/api/learner/status`)

        if (response.ok) {
            const data = await response.json()
            if (data.status === 'success') {
                stats.value = data.learner || {}
                renderAllCharts()
            }
        } else {
            console.error('获取学习器状态失败:', response.statusText)
        }
    } catch (error) {
        console.error('获取学习器状态异常:', error)
    } finally {
        loading.value = false
    }
}

// 渲染所有图表
function renderAllCharts() {
    renderCorrectionPatternChart()
    renderCalibrationMatrixChart()
}

// 1. 最常见纠正模式 - 柱状图
function renderCorrectionPatternChart() {
    if (!correctionPatternChart.value) return

    const chart = echarts.init(correctionPatternChart.value)
    charts.correctionPattern = chart

    const colors = getThemeColors()
    const textColor = colors.text
    const primaryColor = colors.primary

    const corrections = stats.value.top_corrections || []

    if (corrections.length === 0) {
        // 无数据时显示提示
        const option = {
            backgroundColor: 'transparent',
            graphic: [{
                type: 'text',
                left: 'center',
                top: 'middle',
                style: {
                    text: '暂无纠正数据\n请提交情绪反馈',
                    textAlign: 'center',
                    fill: hexToRgba(textColor, 0.5),
                    fontSize: 14
                }
            }]
        }
        chart.setOption(option)
        return
    }

    const categories = corrections.map(c =>
        `${getEmotionEmoji(c.from)}${getEmotionName(c.from)}→${getEmotionEmoji(c.to)}${getEmotionName(c.to)}`
    )
    const values = corrections.map(c => c.count)

    const option = {
        backgroundColor: 'transparent',
        animationDuration: 1500,
        animationEasing: 'cubicOut',
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' },
            backgroundColor: hexToRgba(colors.cardBg, 0.92),
            borderColor: hexToRgba(primaryColor, 0.5),
            borderWidth: 1.5,
            textStyle: { color: textColor, fontSize: 13 },
            padding: [10, 14],
            borderRadius: 8,
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.3)',
            formatter: (params) => {
                const item = corrections[params[0].dataIndex]
                return `${params[0].name}<br/>频次: ${item.count.toFixed(1)}`
            }
        },
        grid: { left: 20, right: 20, top: 20, bottom: 60 },
        xAxis: {
            type: 'category',
            data: categories,
            axisLine: { lineStyle: { color: hexToRgba(primaryColor, 0.2) } },
            axisLabel: {
                color: hexToRgba(textColor, 0.7),
                fontSize: 11,
                rotate: 30,
                interval: 0
            },
            axisTick: { show: false }
        },
        yAxis: {
            type: 'value',
            axisLine: { lineStyle: { color: hexToRgba(primaryColor, 0.2) } },
            axisLabel: { color: hexToRgba(textColor, 0.6), fontSize: 12 },
            splitLine: { lineStyle: { color: hexToRgba(primaryColor, 0.08) } },
            axisTick: { show: false }
        },
        series: [{
            type: 'bar',
            data: values.map((value, idx) => ({
                value,
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: colors.accent },
                        { offset: 1, color: hexToRgba(colors.accent, 0.3) }
                    ]),
                    borderRadius: [6, 6, 0, 0],
                    shadowBlur: 8,
                    shadowColor: hexToRgba(colors.accent, 0.5)
                },
                emphasis: {
                    itemStyle: {
                        shadowBlur: 16,
                        shadowColor: hexToRgba(colors.accent, 0.7)
                    }
                }
            })),
            barWidth: '60%',
            animationType: 'scale',
            animationEasing: 'elasticOut',
            animationDelay: function (idx) {
                return idx * 100
            }
        }]
    }

    chart.setOption(option)
}

// 2. 校准矩阵热力图
function renderCalibrationMatrixChart() {
    if (!calibrationMatrixChart.value) return

    const chart = echarts.init(calibrationMatrixChart.value)
    charts.calibrationMatrix = chart

    const colors = getThemeColors()
    const textColor = colors.text
    const primaryColor = colors.primary

    const matrix = stats.value.calibration_matrix || []
    const emotions = stats.value.emotion_order || emotionOrder

    if (matrix.length === 0) {
        const option = {
            backgroundColor: 'transparent',
            graphic: [{
                type: 'text',
                left: 'center',
                top: 'middle',
                style: {
                    text: '暂无校准数据\n请提交情绪反馈',
                    textAlign: 'center',
                    fill: hexToRgba(textColor, 0.5),
                    fontSize: 14
                }
            }]
        }
        chart.setOption(option)
        return
    }

    // 准备热力图数据
    const heatmapData = []
    for (let i = 0; i < emotions.length; i++) {
        for (let j = 0; j < emotions.length; j++) {
            const value = matrix[i][j] || 0
            if (value > 0) {
                heatmapData.push([j, i, value]) // [x, y, value]
            }
        }
    }

    const option = {
        backgroundColor: 'transparent',
        animationDuration: 1500,
        animationEasing: 'cubicOut',
        tooltip: {
            position: 'top',
            backgroundColor: hexToRgba(colors.cardBg, 0.92),
            borderColor: hexToRgba(primaryColor, 0.5),
            borderWidth: 1.5,
            textStyle: { color: textColor, fontSize: 13 },
            padding: [10, 14],
            borderRadius: 8,
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.3)',
            formatter: (params) => {
                const fromEmotion = getEmotionName(emotions[params.value[1]])
                const toEmotion = getEmotionName(emotions[params.value[0]])
                return `${fromEmotion} → ${toEmotion}<br/>频次: ${params.value[2].toFixed(1)}`
            }
        },
        grid: {
            left: 80,
            right: 80,
            top: 60,
            bottom: 80
        },
        xAxis: {
            type: 'category',
            data: emotions.map(e => getEmotionEmoji(e) + '\n' + getEmotionName(e)),
            axisLine: { lineStyle: { color: hexToRgba(primaryColor, 0.2) } },
            axisLabel: {
                color: hexToRgba(textColor, 0.7),
                fontSize: 11,
                interval: 0
            },
            axisTick: { show: false },
            splitArea: { show: false }
        },
        yAxis: {
            type: 'category',
            data: emotions.map(e => getEmotionEmoji(e) + ' ' + getEmotionName(e)),
            axisLine: { lineStyle: { color: hexToRgba(primaryColor, 0.2) } },
            axisLabel: {
                color: hexToRgba(textColor, 0.7),
                fontSize: 11
            },
            axisTick: { show: false },
            splitArea: { show: false }
        },
        visualMap: {
            min: 0,
            max: Math.max(...heatmapData.map(d => d[2]), 1),
            calculable: true,
            orient: 'horizontal',
            left: 'center',
            bottom: 10,
            inRange: {
                color: [
                    hexToRgba(colors.primary, 0.1),
                    hexToRgba(colors.primary, 0.3),
                    hexToRgba(colors.primary, 0.5),
                    hexToRgba(colors.primary, 0.7),
                    colors.primary
                ]
            },
            textStyle: { color: hexToRgba(textColor, 0.7) }
        },
        series: [{
            type: 'heatmap',
            data: heatmapData,
            label: {
                show: true,
                formatter: (params) => params.value[2] > 0.5 ? params.value[2].toFixed(1) : '',
                color: textColor,
                fontSize: 10
            },
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowColor: hexToRgba(textColor, 0.3)
                }
            }
        }]
    }

    chart.setOption(option)
}

const refresh = () => fetchLearnerStatus()

// 窗口大小改变时重绘图表
function handleResize() {
    Object.values(charts).forEach(chart => chart?.resize())
}

// ✅ 监听主题变化，重新渲染图表
let themeObserver = null

onMounted(() => {
    fetchLearnerStatus()
    window.addEventListener('resize', handleResize)

    // ✅ 监听 CSS 变量变化（主题切换）
    themeObserver = new MutationObserver(() => {
        setTimeout(() => {
            renderAllCharts()
        }, 100)
    })

    themeObserver.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['style']
    })
})

onUnmounted(() => {
    Object.values(charts).forEach(chart => chart?.dispose())
    window.removeEventListener('resize', handleResize)

    if (themeObserver) {
        themeObserver.disconnect()
    }
})
</script>

<style scoped>
.adaptive-learning-monitor {
    padding: 0;
    height: 100%;
    overflow-y: auto;
    overflow-x: hidden;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

/* ===== 统计卡片 ===== */
.stats-grid {
    margin-top: 2px;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    flex-shrink: 0;
}

.stat-card {
    background: var(--card-bg);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    transition: all 0.3s ease;
    overflow: hidden;
    box-shadow: none;
}

.stat-card:hover {
    border-color: color-mix(in srgb, var(--border) 60%, var(--primary));
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
}

.stat-card-inner {
    padding: 12px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.stat-icon-wrap {
    width: 38px;
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
    color: var(--text-secondary);
    opacity: 0.7;
    margin-bottom: 2px;
}

.stat-value {
    font-size: 22px;
    color: var(--text);
    line-height: 1.1;
}

/* ===== 图表区 ===== */
.charts-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    padding-bottom: 16px;
    flex: 1;
}

.chart-card {
    background: var(--card-bg);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    overflow: hidden;
    transition: all 0.3s ease;
    box-shadow: none;
}

.chart-card:hover {
    border-color: color-mix(in srgb, var(--border) 60%, var(--primary));
    box-shadow: var(--shadow-lg);
}

.chart-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 14px 0;
}

.chart-card-header h3 {
    font-size: 16px;
    font-weight: 100;
    color: var(--text);
    margin: 0;
}

.chart-hint {
    font-size: 12px;
    color: var(--text-secondary);
    opacity: 0.5;
}

.chart-body {
    height: 350px;
    padding: 10px 14px 14px;
    background: transparent !important;
}

/* ===== 使用说明 ===== */
.usage-guide {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    padding-bottom: 16px;
    flex-shrink: 0;
}

.guide-card {
    background: var(--card-bg);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 14px;
    transition: all 0.3s ease;
}

.guide-card:hover {
    border-color: color-mix(in srgb, var(--border) 60%, var(--primary));
    box-shadow: var(--shadow-lg);
}

.guide-card h3 {
    font-size: 15px;
    font-weight: 100;
    color: var(--text);
    margin: 0 0 10px 0;
}

.guide-card ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.guide-card li {
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.8;
    padding-left: 16px;
    position: relative;
}

.guide-card li::before {
    content: '•';
    position: absolute;
    left: 0;
    color: var(--primary);
}

.guide-card li strong {
    color: var(--text);
    font-weight: 500;
}

/* ===== 响应式 ===== */
@media (max-width: 1200px) {
    .charts-grid {
        grid-template-columns: 1fr;
    }

    .usage-guide {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 900px) {
    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 600px) {
    .stats-grid {
        grid-template-columns: 1fr;
    }
}
</style>
