<template>
  <div class="emotion-analyzer">
    <!-- 触发按钮 -->
    <el-tooltip content="情绪趋势分析" placement="bottom">
      <button 
        class="analyzer-trigger"
        @click="handleTriggerClick"
        :class="{ 'analyzer-trigger--active': showPanel }"
      >
        <span class="trigger-icon">💭</span>
        <span class="trigger-label">情绪分析</span>
        <span v-if="hasWarning" class="warning-badge">⚠️</span>
        <span class="trigger-arrow">{{ showPanel ? '▲' : '▼' }}</span>
      </button>
    </el-tooltip>

    <!-- 分析面板 -->
    <transition name="slide-down">
      <div v-if="showPanel" class="analyzer-panel">
        <!-- 面板头部 -->
        <div class="panel-header">
          <h3>💭 情绪分析</h3>
        </div>

        <!-- 简洁情绪提示 -->
        <div class="hint-section">
          <div class="hint-emoji">{{ getEmotionHintEmoji() }}</div>
          <div class="hint-text">{{ getPrimaryHint() }}</div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useDetectionStore } from '@/stores/detection';
import { analyzeEmotionData } from '@/utils/emotionAnalyzer';

// 外部控制
const props = defineProps({
  showPanel: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['toggle']);

// 内部状态
const internalShowPanel = ref(false);
const showPanel = computed({
  get: () => props.showPanel !== undefined ? props.showPanel : internalShowPanel.value,
  set: (val) => {
    internalShowPanel.value = val;
    emit('toggle');
  }
});

const detectionStore = useDetectionStore();
const analysisResult = ref(null);
const lastAnalysisTime = ref(0);
const emotionHistory = ref([]);
const MAX_HISTORY_LENGTH = 20;

// 是否有警告
const hasWarning = computed(() => {
  return analysisResult.value?.level === 'warning' || false;
});

// 处理触发按钮点击
const handleTriggerClick = () => {
  showPanel.value = !showPanel.value;
}

// 监听外部状态变化
watch(() => props.showPanel, (newVal) => {
  if (props.showPanel !== undefined) {
    internalShowPanel.value = newVal;
  }
});

// 获取情绪提示表情
function getEmotionHintEmoji() {
  if (!analysisResult.value) return '📊';
  const emojis = {
    positive: '😊',
    neutral: '😌',
    negative: '😔',
    warning: '⚠️'
  };
  return emojis[analysisResult.value.level] || '😐';
}

// 获取主要提示语
function getPrimaryHint() {
  if (!analysisResult.value) return '等待分析...';
  
  const level = analysisResult.value.level;
  const trend = analysisResult.value.trend;
  
  if (level === 'warning') {
    return '⚠️ 情绪波动异常，请注意调节';
  }
  
  if (level === 'negative') {
    if (trend === 'up') {
      return '情绪正在好转，请继续保持';
    }
    return '保持冷静，深呼吸';
  }
  
  if (level === 'positive') {
    if (trend === 'down') {
      return '情绪有下降趋势，注意调节';
    }
    return '情绪状态良好，请继续保持';
  }
  
  // neutral
  if (trend === 'up') {
    return '情绪正在提升，继续保持';
  }
  if (trend === 'down') {
    return '情绪有所下降，请注意调节';
  }
  return '情绪稳定，保持冷静';
}

// 更新情绪历史
function updateEmotionHistory() {
  if (!detectionStore.currentEmotion) return;
  const entry = {
    emotion: detectionStore.currentEmotion,
    confidence: detectionStore.currentConfidence,
    scores: { ...detectionStore.emotionScores },
    timestamp: Date.now()
  };
  emotionHistory.value.push(entry);
  if (emotionHistory.value.length > MAX_HISTORY_LENGTH) {
    emotionHistory.value.shift();
  }
}

// 自动分析
function performAutoAnalysis() {
  const now = Date.now();
  if (now - lastAnalysisTime.value < 2000) return;
  lastAnalysisTime.value = now;
  
  const data = {
    currentEmotion: detectionStore.currentEmotion,
    currentConfidence: detectionStore.currentConfidence,
    emotionScores: detectionStore.emotionScores,
    faces: detectionStore.currentFaces,
    history: [...emotionHistory.value]
  };
  analysisResult.value = analyzeEmotionData(data);
}

// 监听情绪变化
let emotionWatch = null;
let historyTimer = null;

onMounted(() => {
  // 定期更新历史
  historyTimer = setInterval(() => {
    updateEmotionHistory();
  }, 500);
  
  // 监听情绪变化
  emotionWatch = watch(() => detectionStore.currentEmotion, () => {
    if (showPanel.value) {
      performAutoAnalysis();
    }
  });
  
  // 初始分析
  setTimeout(() => {
    performAutoAnalysis();
  }, 1000);
});

onUnmounted(() => {
  if (historyTimer) clearInterval(historyTimer);
  if (emotionWatch) emotionWatch();
});
</script>

<style scoped>
.emotion-analyzer {
  position: relative;
}

/* 触发按钮 */
.analyzer-trigger {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 20px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;

  &:hover {
    background: rgba(139, 92, 246, 0.2);
    border-color: rgba(139, 92, 246, 0.4);
  }

  &--active {
    background: rgba(139, 92, 246, 0.2);
    border-color: rgba(139, 92, 246, 0.5);
  }
}

.trigger-icon {
  font-size: 16px;
}

.trigger-label {
  font-weight: 500;
}

.trigger-arrow {
  font-size: 12px;
  opacity: 0.7;
}

/* 分析面板 */
.analyzer-panel {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 320px;
  max-width: calc(100vw - 20px);
  padding: 20px;
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 2px solid rgba(139, 92, 246, 0.6);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(139, 92, 246, 0.3);
  z-index: 100;
}

/* 面板头部 */
.panel-header {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(139, 92, 246, 0.3);

  h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: #fff;
  }
}

/* 提示区域 */
.hint-section {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: rgba(139, 92, 246, 0.1);
  border-radius: 8px;
}

.hint-emoji {
  font-size: 48px;
}

.hint-text {
  flex: 1;
  font-size: 16px;
  color: #fff;
  line-height: 1.5;
}

/* 动画 */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>