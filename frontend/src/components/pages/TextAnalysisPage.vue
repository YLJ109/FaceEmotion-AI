<template>
  <div class="text-analysis-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>📊 文本情绪分析</h1>
      <p>分析数据表中的文本数据，识别情绪类型并生成分析报告</p>
    </div>

    <!-- 功能选项卡 -->
    <div class="tabs-container">
      <button 
        v-for="tab in tabs" 
        :key="tab.key"
        class="tab-btn"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- 单条文本分析 -->
    <div v-if="activeTab === 'single'" class="analysis-section">
      <div class="input-card">
        <h3>📝 输入文本</h3>
        <textarea
          v-model="inputText"
          class="text-input"
          placeholder="请输入要分析的文本内容..."
          rows="4"
          maxlength="500"
        ></textarea>
        <div class="input-footer">
          <span class="char-count">{{ inputText.length }}/500</span>
          <button class="analyze-btn" @click="analyzeSingleText" :disabled="!inputText.trim()">
            🚀 分析情绪
          </button>
        </div>
      </div>

      <!-- 分析结果 -->
      <div v-if="singleResult" class="result-card">
        <div class="result-header">
          <span class="result-title">🎯 分析结果</span>
          <span 
            class="emotion-badge"
            :class="singleResult.emotion_level"
          >
            {{ singleResult.emotion_label }}
          </span>
        </div>
        
        <div class="result-content">
          <div class="stat-grid">
            <div class="stat-item">
              <span class="stat-label">情感分数</span>
              <span class="stat-value" :class="getScoreClass(singleResult.sentiment_score)">
                {{ singleResult.sentiment_score }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">积极词汇</span>
              <span class="stat-value positive">{{ singleResult.positive_count }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">消极词汇</span>
              <span class="stat-value negative">{{ singleResult.negative_count }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">警告词汇</span>
              <span class="stat-value warning">{{ singleResult.warning_count }}</span>
            </div>
          </div>

          <div class="analysis-summary">
            <h4>📊 分析摘要</h4>
            <p>{{ singleResult.analysis_summary }}</p>
          </div>

          <div class="recommendation-box" v-if="singleResult.recommendation">
            <h4>💡 情绪建议</h4>
            <p>{{ singleResult.recommendation }}</p>
          </div>

          <!-- 识别的关键词 -->
          <div v-if="singleResult.positive_words.length > 0" class="keywords-section">
            <h4>🌟 积极关键词</h4>
            <div class="keywords-list">
              <span v-for="word in singleResult.positive_words" :key="word" class="keyword positive">
                {{ word }}
              </span>
            </div>
          </div>

          <div v-if="singleResult.negative_words.length > 0" class="keywords-section">
            <h4>😔 消极关键词</h4>
            <div class="keywords-list">
              <span v-for="word in singleResult.negative_words" :key="word" class="keyword negative">
                {{ word }}
              </span>
            </div>
          </div>

          <div v-if="singleResult.warning_words.length > 0" class="keywords-section warning">
            <h4>⚠️ 警告关键词</h4>
            <div class="keywords-list">
              <span v-for="word in singleResult.warning_words" :key="word" class="keyword warning">
                {{ word }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 批量文本分析 -->
    <div v-if="activeTab === 'batch'" class="analysis-section">
      <div class="input-card">
        <h3>📋 批量输入文本</h3>
        <p class="hint-text">每行输入一条文本，系统将批量分析情绪</p>
        <textarea
          v-model="batchInput"
          class="text-input"
          placeholder="第一条文本&#10;第二条文本&#10;第三条文本&#10;..."
          rows="6"
          maxlength="2000"
        ></textarea>
        <div class="input-footer">
          <span class="char-count">{{ batchInput.length }}/2000</span>
          <button class="analyze-btn" @click="analyzeBatchText" :disabled="!batchInput.trim()">
            🚀 批量分析
          </button>
        </div>
      </div>

      <!-- 批量分析结果 -->
      <div v-if="batchResults.length > 0" class="batch-results">
        <div class="summary-card">
          <h3>📈 整体统计</h3>
          <div class="summary-grid">
            <div class="summary-item">
              <span class="summary-label">总记录数</span>
              <span class="summary-value">{{ batchSummary.total_records }}</span>
            </div>
            <div class="summary-item positive">
              <span class="summary-label">积极</span>
              <span class="summary-value">{{ batchSummary.positive_count }} ({{ batchSummary.positive_ratio }}%)</span>
            </div>
            <div class="summary-item neutral">
              <span class="summary-label">中性</span>
              <span class="summary-value">{{ batchSummary.neutral_count }} ({{ batchSummary.neutral_ratio }}%)</span>
            </div>
            <div class="summary-item negative">
              <span class="summary-label">消极</span>
              <span class="summary-value">{{ batchSummary.negative_count }} ({{ batchSummary.negative_ratio }}%)</span>
            </div>
            <div class="summary-item warning">
              <span class="summary-label">警告</span>
              <span class="summary-value">{{ batchSummary.warning_count }} ({{ batchSummary.warning_ratio }}%)</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">平均情感分数</span>
              <span class="summary-value" :class="getScoreClass(batchSummary.average_sentiment_score)">
                {{ batchSummary.average_sentiment_score }}
              </span>
            </div>
          </div>
        </div>

        <!-- 结果表格 -->
        <div class="results-table-container">
          <table class="results-table">
            <thead>
              <tr>
                <th>序号</th>
                <th>文本内容</th>
                <th>情绪类型</th>
                <th>情感分数</th>
                <th>积极词</th>
                <th>消极词</th>
                <th>警告词</th>
                <th>分析摘要</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="result in batchResults" :key="result.row_index">
                <td>{{ result.row_index + 1 }}</td>
                <td class="text-cell">{{ result.text }}</td>
                <td>
                  <span class="emotion-tag" :class="result.emotion_level">
                    {{ result.emotion_label }}
                  </span>
                </td>
                <td :class="getScoreClass(result.sentiment_score)">
                  {{ result.sentiment_score }}
                </td>
                <td>{{ result.positive_count }}</td>
                <td>{{ result.negative_count }}</td>
                <td>{{ result.warning_count }}</td>
                <td class="summary-cell">{{ result.analysis_summary }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 历史反馈分析 -->
    <div v-if="activeTab === 'feedback'" class="analysis-section">
      <div class="action-bar">
        <button class="refresh-btn" @click="analyzeFeedbackRecords">
          🔄 刷新数据
        </button>
      </div>

      <div v-if="feedbackResults.length > 0" class="batch-results">
        <div class="summary-card">
          <h3>📊 用户反馈情绪分析</h3>
          <div class="summary-grid">
            <div class="summary-item">
              <span class="summary-label">总记录数</span>
              <span class="summary-value">{{ feedbackSummary.total_records }}</span>
            </div>
            <div class="summary-item positive">
              <span class="summary-label">积极</span>
              <span class="summary-value">{{ feedbackSummary.positive_count }} ({{ feedbackSummary.positive_ratio }}%)</span>
            </div>
            <div class="summary-item neutral">
              <span class="summary-label">中性</span>
              <span class="summary-value">{{ feedbackSummary.neutral_count }} ({{ feedbackSummary.neutral_ratio }}%)</span>
            </div>
            <div class="summary-item negative">
              <span class="summary-label">消极</span>
              <span class="summary-value">{{ feedbackSummary.negative_count }} ({{ feedbackSummary.negative_ratio }}%)</span>
            </div>
            <div class="summary-item warning">
              <span class="summary-label">警告</span>
              <span class="summary-value">{{ feedbackSummary.warning_count }} ({{ feedbackSummary.warning_ratio }}%)</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">平均情感分数</span>
              <span class="summary-value" :class="getScoreClass(feedbackSummary.average_sentiment_score)">
                {{ feedbackSummary.average_sentiment_score }}
              </span>
            </div>
          </div>
        </div>

        <!-- 结果表格 -->
        <div class="results-table-container">
          <table class="results-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>时间</th>
                <th>预测情绪</th>
                <th>正确情绪</th>
                <th>文本内容</th>
                <th>情绪类型</th>
                <th>情感分数</th>
                <th>建议</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="result in feedbackResults" :key="result.record_id">
                <td>{{ result.record_id }}</td>
                <td>{{ formatTimestamp(result.timestamp) }}</td>
                <td>{{ result.predicted_emotion || '-' }}</td>
                <td>{{ result.correct_emotion || '-' }}</td>
                <td class="text-cell">{{ result.text }}</td>
                <td>
                  <span class="emotion-tag" :class="result.emotion_level">
                    {{ result.emotion_label }}
                  </span>
                </td>
                <td :class="getScoreClass(result.sentiment_score)">
                  {{ result.sentiment_score }}
                </td>
                <td class="summary-cell">{{ result.recommendation }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-else class="empty-state">
        <span class="empty-icon">📭</span>
        <p>暂无反馈数据</p>
        <button class="refresh-btn" @click="analyzeFeedbackRecords">
          🔄 点击加载数据
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const tabs = [
  { key: 'single', label: '单条分析' },
  { key: 'batch', label: '批量分析' },
  { key: 'feedback', label: '历史反馈分析' }
]

const activeTab = ref('single')
const inputText = ref('')
const batchInput = ref('')
const singleResult = ref(null)
const batchResults = ref([])
const batchSummary = reactive({
  total_records: 0,
  positive_count: 0,
  negative_count: 0,
  neutral_count: 0,
  warning_count: 0,
  average_sentiment_score: 0,
  positive_ratio: 0,
  negative_ratio: 0,
  neutral_ratio: 0,
  warning_ratio: 0
})
const feedbackResults = ref([])
const feedbackSummary = reactive({
  total_records: 0,
  positive_count: 0,
  negative_count: 0,
  neutral_count: 0,
  warning_count: 0,
  average_sentiment_score: 0,
  positive_ratio: 0,
  negative_ratio: 0,
  neutral_ratio: 0,
  warning_ratio: 0
})

async function analyzeSingleText() {
  try {
    const response = await fetch('/api/text-analysis/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: inputText.value })
    })
    const data = await response.json()
    if (data.status === 'success') {
      singleResult.value = data.data
    }
  } catch (error) {
    console.error('分析失败:', error)
  }
}

async function analyzeBatchText() {
  const texts = batchInput.value.split('\n').filter(t => t.trim())
  try {
    const response = await fetch('/api/text-analysis/analyze-batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ texts })
    })
    const data = await response.json()
    if (data.status === 'success') {
      batchResults.value = data.data
      Object.assign(batchSummary, data.summary)
    }
  } catch (error) {
    console.error('批量分析失败:', error)
  }
}

async function analyzeFeedbackRecords() {
  try {
    const response = await fetch('/api/text-analysis/analyze-feedback?limit=100')
    const data = await response.json()
    if (data.status === 'success') {
      feedbackResults.value = data.data
      Object.assign(feedbackSummary, data.summary)
    }
  } catch (error) {
    console.error('获取反馈数据失败:', error)
  }
}

function getScoreClass(score) {
  if (score > 30) return 'positive'
  if (score < -30) return 'negative'
  return 'neutral'
}

function formatTimestamp(timestamp) {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
}

// 初始化加载反馈数据
analyzeFeedbackRecords()
</script>

<style scoped>
.text-analysis-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.page-header p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.tabs-container {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.tab-btn {
  padding: 10px 20px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.tab-btn.active {
  background: rgba(139, 92, 246, 0.1);
  border-color: rgba(139, 92, 246, 0.3);
  color: #8B5CF6;
}

.analysis-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.input-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
}

.input-card h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.hint-text {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0 0 12px 0;
}

.text-input {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-hover);
  color: var(--text-primary);
  font-size: 14px;
  resize: vertical;
  box-sizing: border-box;
  transition: border-color 0.2s ease;
}

.text-input:focus {
  outline: none;
  border-color: rgba(139, 92, 246, 0.5);
}

.text-input::placeholder {
  color: var(--text-placeholder);
}

.input-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
}

.char-count {
  font-size: 12px;
  color: var(--text-secondary);
}

.analyze-btn, .refresh-btn {
  padding: 8px 20px;
  background: linear-gradient(135deg, #8B5CF6, #6366F1);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.analyze-btn:hover:not(:disabled), .refresh-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}

.analyze-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.refresh-btn {
  background: var(--bg-hover);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.refresh-btn:hover {
  background: var(--bg-tertiary);
  box-shadow: none;
}

.result-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: rgba(139, 92, 246, 0.05);
  border-bottom: 1px solid var(--border-color);
}

.result-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.emotion-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.emotion-badge.positive {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
}

.emotion-badge.neutral {
  background: rgba(107, 114, 128, 0.1);
  color: #6B7280;
}

.emotion-badge.negative {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

.emotion-badge.warning {
  background: rgba(245, 158, 11, 0.1);
  color: #F59E0B;
}

.result-content {
  padding: 20px;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.stat-item {
  background: var(--bg-hover);
  border-radius: 8px;
  padding: 12px;
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.stat-value.positive {
  color: #10B981;
}

.stat-value.negative {
  color: #EF4444;
}

.stat-value.warning {
  color: #F59E0B;
}

.analysis-summary, .recommendation-box {
  margin-bottom: 20px;
}

.analysis-summary h4, .recommendation-box h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 0 0 8px 0;
}

.analysis-summary p {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.6;
  margin: 0;
}

.recommendation-box {
  padding: 16px;
  background: rgba(139, 92, 246, 0.08);
  border-radius: 8px;
  border-left: 3px solid #8B5CF6;
}

.recommendation-box p {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.6;
  margin: 0;
}

.keywords-section {
  margin-bottom: 16px;
}

.keywords-section h4 {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 0 0 8px 0;
}

.keywords-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.keyword {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
}

.keyword.positive {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
}

.keyword.negative {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

.keyword.warning {
  background: rgba(245, 158, 11, 0.1);
  color: #F59E0B;
}

.batch-results {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.summary-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
}

.summary-card h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
}

.summary-item {
  text-align: center;
}

.summary-label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.summary-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.summary-item.positive .summary-value {
  color: #10B981;
}

.summary-item.neutral .summary-value {
  color: #6B7280;
}

.summary-item.negative .summary-value {
  color: #EF4444;
}

.summary-item.warning .summary-value {
  color: #F59E0B;
}

.results-table-container {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  max-height: 500px;
  overflow-y: auto;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
}

.results-table th,
.results-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
  font-size: 13px;
}

.results-table th {
  background: var(--bg-hover);
  font-weight: 600;
  color: var(--text-secondary);
  position: sticky;
  top: 0;
  z-index: 1;
}

.results-table tbody tr:hover {
  background: var(--bg-hover);
}

.text-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.summary-cell {
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.emotion-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.emotion-tag.positive {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
}

.emotion-tag.neutral {
  background: rgba(107, 114, 128, 0.1);
  color: #6B7280;
}

.emotion-tag.negative {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

.emotion-tag.warning {
  background: rgba(245, 158, 11, 0.1);
  color: #F59E0B;
}

.action-bar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 16px 0;
}
</style>