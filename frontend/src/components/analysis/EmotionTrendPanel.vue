<template>
  <div class="emotion-trend-panel" v-if="showPanel">
    <div class="panel-header">
      <h4>
        <span class="panel-icon"><el-icon><DataAnalysis /></el-icon></span>
        <span>情绪趋势分析</span>
      </h4>
      <div class="time-badge">最后3秒</div>
    </div>

    <div class="panel-content">
      <div v-if="!hasData" class="no-data">
        <el-icon :size="32"><Loading /></el-icon>
        <p>等待数据采集...</p>
      </div>

      <div v-else class="analysis-content">
        <div v-if="trendAnalysis.hasRisk" class="risk-alert" :class="`risk-${trendAnalysis.riskLevel}`">
          <el-icon class="alert-icon"><Warning /></el-icon>
          <div class="alert-content">
            <div class="alert-title">{{ trendAnalysis.riskLevelName }}</div>
            <div class="alert-message">{{ trendAnalysis.riskMessage || trendAnalysis.enhancedWarning }}</div>
          </div>
        </div>

        <div class="analysis-section">
          <div class="section-title">
            <el-icon><TrendCharts /></el-icon>
            <span>情绪波动模式</span>
          </div>
          <div class="section-content">
            <div class="info-item">
              <span class="label">波动状态:</span>
              <span class="value">{{ trendAnalysis.fluctuationPatternName }}</span>
            </div>
            <div class="info-item">
              <span class="label">数据点数:</span>
              <span class="value">{{ trendAnalysis.dataPoints }}个</span>
            </div>
            <div class="info-item">
              <span class="label">主要情绪:</span>
              <span class="value emotion-tag" :style="{ color: getEmotionColor(trendAnalysis.mainEmotion) }">
                {{ trendAnalysis.mainEmotionName }}
              </span>
            </div>
            <div class="info-item">
              <span class="label">情绪强度:</span>
              <span class="value">{{ (trendAnalysis.mainEmotionIntensity * 100).toFixed(1) }}%</span>
            </div>
            <div class="info-item">
              <span class="label">强度变化:</span>
              <span class="value">{{ trendAnalysis.intensityChangeName }}</span>
            </div>
          </div>
        </div>

        <div v-if="textAnalysis.hasText" class="analysis-section">
          <div class="section-title">
            <el-icon><Document /></el-icon>
            <span>文字内容分析</span>
          </div>
          <div class="section-content">
            <div v-if="textAnalysis.positiveCount > 0" class="info-item positive">
              <span class="label">积极情绪词:</span>
              <span class="value">{{ textAnalysis.positiveCount }}个</span>
            </div>
            <div v-if="textAnalysis.negativeCount > 0" class="info-item negative">
              <span class="label">消极情绪词:</span>
              <span class="value">{{ textAnalysis.negativeCount }}个</span>
            </div>
            <div v-if="textAnalysis.warningCount > 0" class="info-item warning">
              <span class="label">警告词:</span>
              <span class="value">{{ textAnalysis.warningCount }}个</span>
            </div>
            <div v-if="textAnalysis.keyInfo.length > 0" class="key-info-list">
              <div v-for="(info, index) in textAnalysis.keyInfo" :key="index" class="key-info-item">
                {{ info }}
              </div>
            </div>
          </div>
        </div>

        <div class="analysis-section">
          <div class="section-title">
            <el-icon><ChatLineRound /></el-icon>
            <span>综合分析意见</span>
          </div>
          <div class="section-content">
            <div class="analysis-opinion">{{ comprehensiveAnalysis.analysisOpinion }}</div>
          </div>
        </div>

        <div v-if="comprehensiveAnalysis.recommendation" class="analysis-section recommendation">
          <div class="section-title">
            <el-icon><Promotion /></el-icon>
            <span>情绪管理建议</span>
          </div>
          <div class="section-content">
            <div class="recommendation-text">{{ comprehensiveAnalysis.recommendation }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { DataAnalysis, TrendCharts, Document, ChatLineRound, Promotion, Warning, Loading } from '@element-plus/icons-vue'
import { getEmotionColor } from '@/constants/emotions'

const props = defineProps({
  showPanel: {
    type: Boolean,
    default: true
  },
  trendAnalysis: {
    type: Object,
    default: () => ({})
  },
  textAnalysis: {
    type: Object,
    default: () => ({})
  },
  comprehensiveAnalysis: {
    type: Object,
    default: () => ({})
  }
})

const hasData = computed(() => {
  return props.trendAnalysis && props.trendAnalysis.dataPoints > 0
})
</script>

<style scoped>
.emotion-trend-panel {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-top: 12px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}

.panel-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-icon {
  color: var(--primary);
}

.time-badge {
  background: var(--primary-light);
  color: var(--primary);
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.panel-content {
  min-height: 200px;
}

.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}

.no-data p {
  margin: 12px 0 0 0;
  font-size: 14px;
}

.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.risk-alert {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background: rgba(245, 158, 11, 0.1);
  border-left: 4px solid #F59E0B;
}

.risk-alert.risk-high {
  background: rgba(239, 68, 68, 0.1);
  border-left-color: #EF4444;
}

.risk-alert.risk-medium {
  background: rgba(245, 158, 11, 0.1);
  border-left-color: #F59E0B;
}

.risk-alert.risk-low {
  background: rgba(59, 130, 246, 0.1);
  border-left-color: #3B82F6;
}

.alert-icon {
  font-size: 24px;
  color: #F59E0B;
  flex-shrink: 0;
}

.risk-alert.risk-high .alert-icon {
  color: #EF4444;
}

.risk-alert.risk-low .alert-icon {
  color: #3B82F6;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 4px;
}

.alert-message {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.analysis-section {
  background: var(--card-bg);
  border-radius: 8px;
  padding: 12px;
  border: 1px solid var(--border);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 10px;
}

.section-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.info-item .label {
  color: var(--text-secondary);
}

.info-item .value {
  color: var(--text);
  font-weight: 500;
}

.info-item.positive .value {
  color: #10B981;
}

.info-item.negative .value {
  color: #EF4444;
}

.info-item.warning .value {
  color: #F59E0B;
}

.emotion-tag {
  font-weight: 600;
}

.key-info-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 8px;
}

.key-info-item {
  font-size: 12px;
  color: var(--text-secondary);
  padding: 6px 10px;
  background: var(--card-bg);
  border-radius: 4px;
  border-left: 2px solid var(--primary);
}

.analysis-opinion {
  font-size: 13px;
  color: var(--text);
  line-height: 1.6;
}

.recommendation {
  background: rgba(16, 185, 129, 0.05);
  border-color: rgba(16, 185, 129, 0.2);
}

.recommendation-text {
  font-size: 13px;
  color: var(--text);
  line-height: 1.6;
}
</style>
