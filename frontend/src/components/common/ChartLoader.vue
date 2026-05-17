<template>
  <div class="chart-loader" :class="[`chart-loader--${type}`]">
    <div class="chart-loader__inner">
      <!-- 柱状图骨架 -->
      <template v-if="type === 'bar'">
        <div class="skeleton-bars">
          <div class="skeleton-bar" v-for="i in 5" :key="i"
            :style="{ height: barHeights[i - 1] + '%', animationDelay: (i * 0.12) + 's' }">
            <div class="skeleton-bar__shimmer"></div>
          </div>
        </div>
        <div class="skeleton-axis"></div>
      </template>

      <!-- 折线图骨架 -->
      <template v-else-if="type === 'line'">
        <svg class="skeleton-line-svg" viewBox="0 0 300 160" preserveAspectRatio="none">
          <defs>
            <linearGradient id="lineGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="var(--primary)" stop-opacity="0.25" />
              <stop offset="100%" stop-color="var(--primary)" stop-opacity="0.02" />
            </linearGradient>
          </defs>
          <path class="skeleton-line-path" :d="linePath" fill="none" stroke="var(--primary)" stroke-width="2.5"
            stroke-opacity="0.5" />
          <path class="skeleton-line-fill" :d="lineFillPath" fill="url(#lineGrad)" />
          <circle v-for="(pt, i) in linePoints" :key="i" :cx="pt.x" :cy="pt.y" r="4"
            fill="var(--primary)" fill-opacity="0.4">
            <animate attributeName="r" values="4;5;4" dur="2s" repeatCount="indefinite"
              :begin="(i * 0.15) + 's'" />
          </circle>
        </svg>
        <div class="skeleton-axis"></div>
      </template>

      <!-- 饼图骨架 -->
      <template v-else-if="type === 'pie'">
        <div class="skeleton-pie">
          <svg viewBox="0 0 160 160" class="skeleton-pie__svg">
            <circle cx="80" cy="80" r="60" fill="none" stroke="var(--primary)" stroke-width="20"
              stroke-opacity="0.12" />
            <circle cx="80" cy="80" r="60" fill="none" stroke="var(--primary)" stroke-width="20"
              stroke-opacity="0.25" stroke-dasharray="94 283" stroke-dashoffset="0"
              transform="rotate(-90 80 80)">
              <animate attributeName="stroke-dashoffset" from="377" to="0" dur="2.5s"
                repeatCount="indefinite" />
            </circle>
            <circle cx="80" cy="80" r="35" fill="var(--card-bg)" stroke="var(--primary)"
              stroke-width="1" stroke-opacity="0.1" />
          </svg>
          <div class="skeleton-pie__legend">
            <div class="skeleton-legend-item" v-for="i in 4" :key="i"
              :style="{ animationDelay: (i * 0.15) + 's' }">
              <span class="skeleton-legend-dot"></span>
              <span class="skeleton-legend-line"></span>
            </div>
          </div>
        </div>
      </template>

      <!-- 桑基图骨架 -->
      <template v-else-if="type === 'sankey'">
        <div class="skeleton-sankey">
          <div class="skeleton-sankey__col" v-for="col in 2" :key="col">
            <div class="skeleton-sankey__node" v-for="i in (col === 1 ? 4 : 3)" :key="i"
              :style="{ animationDelay: ((col * 3 + i) * 0.1) + 's' }">
              <div class="skeleton-sankey__shimmer"></div>
            </div>
          </div>
          <svg class="skeleton-sankey__flows" viewBox="0 0 200 160" preserveAspectRatio="none">
            <path v-for="i in 6" :key="i" :d="sankeyFlowPaths[i - 1]"
              fill="none" stroke="var(--primary)" stroke-width="3" stroke-opacity="0.12">
              <animate attributeName="stroke-opacity" values="0.12;0.25;0.12" dur="2s"
                repeatCount="indefinite" :begin="(i * 0.2) + 's'" />
            </path>
          </svg>
        </div>
      </template>

      <!-- 面积图骨架 -->
      <template v-else-if="type === 'area'">
        <svg class="skeleton-area-svg" viewBox="0 0 300 160" preserveAspectRatio="none">
          <defs>
            <linearGradient id="areaGrad1" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="var(--accent)" stop-opacity="0.3" />
              <stop offset="100%" stop-color="var(--accent)" stop-opacity="0.02" />
            </linearGradient>
            <linearGradient id="areaGrad2" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="var(--secondary)" stop-opacity="0.25" />
              <stop offset="100%" stop-color="var(--secondary)" stop-opacity="0.02" />
            </linearGradient>
          </defs>
          <path class="skeleton-area-path" :d="areaPath1" fill="url(#areaGrad1)" stroke="var(--accent)"
            stroke-width="1.5" stroke-opacity="0.4" />
          <path class="skeleton-area-path" :d="areaPath2" fill="url(#areaGrad2)" stroke="var(--secondary)"
            stroke-width="1.5" stroke-opacity="0.4" />
        </svg>
        <div class="skeleton-axis"></div>
      </template>

      <!-- 默认脉冲骨架 -->
      <template v-else>
        <div class="skeleton-pulse">
          <div class="skeleton-pulse__ring">
            <div class="skeleton-pulse__dot"></div>
          </div>
        </div>
      </template>
    </div>
    <div class="chart-loader__label">
      <span class="chart-loader__dot-bounce" v-for="i in 3" :key="i"
        :style="{ animationDelay: (i * 0.15) + 's' }"></span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'bar',
    validator: v => ['bar', 'line', 'pie', 'sankey', 'area', 'pulse'].includes(v)
  }
})

const barHeights = [65, 42, 78, 55, 38]

const linePoints = [
  { x: 15, y: 110 }, { x: 75, y: 70 }, { x: 135, y: 95 },
  { x: 195, y: 45 }, { x: 255, y: 80 }, { x: 285, y: 55 }
]

const linePath = computed(() =>
  linePoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
)

const lineFillPath = computed(() =>
  `M ${linePoints[0].x} ${linePoints[0].y} ` +
  linePoints.slice(1).map(p => `L ${p.x} ${p.y}`).join(' ') +
  ` L ${linePoints[linePoints.length - 1].x} 160 L ${linePoints[0].x} 160 Z`
)

const areaPath1 = 'M 15 120 Q 60 80 105 95 T 195 55 T 285 70'
const areaPath2 = 'M 15 100 Q 60 110 105 75 T 195 90 T 285 50'

const sankeyFlowPaths = [
  'M 45 25 Q 120 25 155 20',
  'M 45 55 Q 120 55 155 50',
  'M 45 85 Q 120 85 155 80',
  'M 45 115 Q 120 115 155 110',
  'M 45 25 Q 120 55 155 50',
  'M 45 85 Q 120 55 155 80'
]
</script>

<style scoped>
.chart-loader {
  width: 100%;
  height: 100%;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 20px;
}

.chart-loader__inner {
  width: 100%;
  flex: 1;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  position: relative;
}

/* ===== 柱状图骨架 ===== */
.skeleton-bars {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 12px;
  width: 80%;
  height: 100%;
  padding-bottom: 24px;
}

.skeleton-bar {
  flex: 1;
  max-width: 48px;
  min-height: 20px;
  background: linear-gradient(180deg,
      var(--primary) 0%,
      color-mix(in srgb, var(--primary) 60%, transparent) 100%);
  opacity: 0.15;
  border-radius: 6px 6px 0 0;
  position: relative;
  overflow: hidden;
  animation: barPulse 2s ease-in-out infinite;
}

.skeleton-bar__shimmer {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg,
      transparent 0%,
      color-mix(in srgb, var(--primary) 30%, transparent) 40%,
      transparent 60%);
  animation: shimmer 2s ease-in-out infinite;
}

.skeleton-axis {
  position: absolute;
  bottom: 0;
  left: 10%;
  right: 10%;
  height: 1px;
  background: var(--primary);
  opacity: 0.1;
}

/* ===== 折线图骨架 ===== */
.skeleton-line-svg {
  width: 85%;
  height: 100%;
}

.skeleton-line-path {
  stroke-dasharray: 400;
  stroke-dashoffset: 400;
  animation: drawLine 2s ease-in-out infinite;
}

.skeleton-line-fill {
  opacity: 0;
  animation: fadeFill 2s ease-in-out infinite;
}

/* ===== 饼图骨架 ===== */
.skeleton-pie {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  width: 100%;
  height: 100%;
}

.skeleton-pie__svg {
  width: 140px;
  height: 140px;
  flex-shrink: 0;
}

.skeleton-pie__legend {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.skeleton-legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  animation: legendPulse 1.8s ease-in-out infinite;
}

.skeleton-legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary);
  opacity: 0.3;
}

.skeleton-legend-line {
  width: 60px;
  height: 8px;
  border-radius: 4px;
  background: var(--primary);
  opacity: 0.12;
}

/* ===== 桑基图骨架 ===== */
.skeleton-sankey {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 10%;
  position: relative;
}

.skeleton-sankey__col {
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 1;
}

.skeleton-sankey__node {
  width: 60px;
  height: 20px;
  border-radius: 4px;
  background: var(--primary);
  opacity: 0.15;
  position: relative;
  overflow: hidden;
  animation: nodePulse 2s ease-in-out infinite;
}

.skeleton-sankey__shimmer {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg,
      transparent 0%,
      color-mix(in srgb, var(--primary) 30%, transparent) 50%,
      transparent 100%);
  animation: shimmer 2s ease-in-out infinite;
}

.skeleton-sankey__flows {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

/* ===== 面积图骨架 ===== */
.skeleton-area-svg {
  width: 85%;
  height: 100%;
}

.skeleton-area-path {
  animation: areaPulse 2.5s ease-in-out infinite;
}

/* ===== 脉冲骨架 ===== */
.skeleton-pulse {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.skeleton-pulse__ring {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 3px solid var(--primary);
  border-top-color: transparent;
  opacity: 0.3;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: spin 1.2s linear infinite;
}

.skeleton-pulse__dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--primary);
  opacity: 0.5;
  animation: dotPulse 1.2s ease-in-out infinite;
}

/* ===== 加载文字 ===== */
.chart-loader__label {
  display: flex;
  align-items: center;
  gap: 4px;
  height: 16px;
}

.chart-loader__dot-bounce {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--primary);
  opacity: 0.4;
  animation: dotBounce 1.2s ease-in-out infinite;
}

/* ===== 动画关键帧 ===== */
@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

@keyframes barPulse {
  0%, 100% { opacity: 0.12; }
  50% { opacity: 0.22; }
}

@keyframes drawLine {
  0% { stroke-dashoffset: 400; }
  50% { stroke-dashoffset: 0; }
  100% { stroke-dashoffset: -400; }
}

@keyframes fadeFill {
  0%, 100% { opacity: 0; }
  50% { opacity: 1; }
}

@keyframes legendPulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

@keyframes nodePulse {
  0%, 100% { opacity: 0.1; }
  50% { opacity: 0.22; }
}

@keyframes areaPulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes dotPulse {
  0%, 100% { transform: scale(0.8); opacity: 0.3; }
  50% { transform: scale(1.2); opacity: 0.7; }
}

@keyframes dotBounce {
  0%, 80%, 100% { transform: translateY(0); opacity: 0.3; }
  40% { transform: translateY(-6px); opacity: 0.7; }
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .chart-loader {
    min-height: 160px;
    padding: 12px;
  }

  .skeleton-bars {
    gap: 8px;
  }

  .skeleton-bar {
    max-width: 36px;
  }

  .skeleton-pie__svg {
    width: 100px;
    height: 100px;
  }

  .skeleton-legend-line {
    width: 40px;
  }
}
</style>