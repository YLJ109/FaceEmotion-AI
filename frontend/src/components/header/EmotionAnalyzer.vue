<template>
  <div class="emotion-analyzer">
    <!-- 触发按钮 -->
    <el-tooltip content="情绪趋势分析" placement="bottom">
      <button 
        class="nav-tool-btn"
        @click="handleTriggerClick"
        :class="{ 'active': showPanel, 'warning': hasWarning }"
      >
        <span class="btn-icon">{{ currentEmotionEmoji }}</span>
        <span class="btn-label">情绪分析</span>
        <span v-if="hasWarning" class="warning-badge">⚠️</span>
        <span class="btn-arrow">{{ showPanel ? '▲' : '▼' }}</span>
      </button>
    </el-tooltip>

    <!-- 分析面板 -->
    <transition name="slide-down">
      <div v-if="showPanel" class="analyzer-panel">
        <!-- 情绪趋势提示 -->
        <div class="hint-section" :class="analysisLevel">
          <div class="hint-emoji">{{ analysisEmoji }}</div>
          <div class="hint-content">
            <div class="hint-title">{{ analysisTitle }}</div>
            <div class="hint-text">{{ analysisMessage }}</div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useDetectionStore } from '@/stores/detection';
import { useThemeStore } from '@/stores/theme';

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
const themeStore = useThemeStore();
const emotionHistory = ref([]);
const MAX_HISTORY_LENGTH = 30;
const lastAnalysisTime = ref(0);

// 七种情绪配置
const EMOTION_CONFIG = {
  happy: { name: '开心', emoji: '😊', color: '#67C23A', positive: true },
  sad: { name: '悲伤', emoji: '😢', color: '#409EFF', positive: false },
  angry: { name: '愤怒', emoji: '😠', color: '#F56C6C', positive: false },
  surprise: { name: '惊讶', emoji: '😲', color: '#E6A23C', positive: false },
  fear: { name: '恐惧', emoji: '😨', color: '#909399', positive: false },
  disgust: { name: '厌恶', emoji: '🤢', color: '#B37FEB', positive: false },
  neutral: { name: '平静', emoji: '😌', color: '#8FBC8F', positive: true }
};

// 当前情绪表情
const currentEmotionEmoji = computed(() => {
  const emotion = detectionStore.currentEmotion;
  return EMOTION_CONFIG[emotion]?.emoji || '😐';
});

// 当前情绪名称
const currentEmotionName = computed(() => {
  const emotion = detectionStore.currentEmotion;
  return EMOTION_CONFIG[emotion]?.name || '未知';
});

// 置信度百分比
const confidencePercent = computed(() => {
  return Math.round(detectionStore.currentConfidence * 100);
});

// 排序后的情绪分数
const sortedEmotions = computed(() => {
  const scores = detectionStore.emotionScores;
  return Object.entries(scores)
    .map(([key, value]) => ({
      key,
      name: EMOTION_CONFIG[key]?.name || key,
      score: Math.round(value * 100)
    }))
    .sort((a, b) => b.score - a.score);
});

// 是否有警告
const hasWarning = computed(() => {
  return analysisResult.value?.level === 'warning';
});

// 分析结果
const analysisResult = ref(null);

// 分析级别
const analysisLevel = computed(() => analysisResult.value?.level || 'neutral');

// 分析表情
const analysisEmoji = computed(() => {
  if (!analysisResult.value) return '📊';
  const emojis = {
    positive: '😊',
    neutral: '😌',
    negative: '😔',
    warning: '⚠️'
  };
  return emojis[analysisResult.value.level] || '😐';
});

// 分析标题
const analysisTitle = computed(() => {
  if (!analysisResult.value) return '分析中...';
  const titles = {
    positive: '情绪良好',
    neutral: '情绪稳定',
    negative: '情绪偏低',
    warning: '需要关注'
  };
  return titles[analysisResult.value.level] || '分析中';
});

// 分析提示信息
const analysisMessage = computed(() => {
  if (!analysisResult.value) return '正在分析您的情绪状态...';
  return analysisResult.value.message;
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

// 分析情绪趋势
function analyzeEmotionTrend() {
  const now = Date.now();
  if (now - lastAnalysisTime.value < 500) return;  // 缩短分析间隔为500ms
  lastAnalysisTime.value = now;

  const currentEmotion = detectionStore.currentEmotion;
  const confidence = detectionStore.currentConfidence;

  // 如果没有检测到情绪，显示提示
  if (!currentEmotion || confidence < 0.1) {
    analysisResult.value = { level: 'neutral', message: '请确保人脸在画面中清晰可见' };
    return;
  }

  // 获取最近的数据（每500ms一条，3秒需要6条）
  const recentData = emotionHistory.value.slice(-6);
  const primaryEmotions = recentData.map(e => e.emotion).filter(Boolean);
  
  // 统计各情绪出现次数
  const emotionCounts = {};
  primaryEmotions.forEach(e => {
    emotionCounts[e] = (emotionCounts[e] || 0) + 1;
  });

  // 找出主要情绪
  let mainEmotion = currentEmotion;
  let maxCount = 0;
  Object.entries(emotionCounts).forEach(([emotion, count]) => {
    if (count > maxCount) {
      maxCount = count;
      mainEmotion = emotion;
    }
  });

  // 分析情绪波动
  const uniqueEmotions = new Set(primaryEmotions).size;
  const isFluctuating = uniqueEmotions > 2;  // 放宽波动检测条件

  // 判断分析结果
  const config = EMOTION_CONFIG[mainEmotion];

  let level = 'neutral';
  let message = '情绪稳定，保持冷静';

  if (!config) {
    level = 'neutral';
    message = '正在识别您的情绪...';
  } else if (isFluctuating && confidence > 0.3) {
    level = 'warning';
    message = '情绪有些不稳定，试着深呼吸放松一下';
  } else if (!config.positive && confidence > 0.5) {
    level = 'warning';
    message = `检测到${config.name}情绪较高，保持冷静，一切都会好起来的`;
  } else if (!config.positive && confidence > 0.3) {
    level = 'negative';
    message = `感受到${config.name}情绪，记得照顾好自己，适当休息`;
  } else if (config.positive && confidence > 0.5) {
    level = 'positive';
    message = `当前${config.name}情绪，继续保持这份好心情！`;
  } else if (config.positive && confidence > 0.3) {
    level = 'positive';
    message = '情绪状态良好，请继续保持';
  }

  analysisResult.value = { level, message };
}

// 监听情绪变化
let emotionWatch = null;
let historyTimer = null;

onMounted(() => {
  // 定期更新历史（每500ms）
  historyTimer = setInterval(() => {
    updateEmotionHistory();
    analyzeEmotionTrend();  // 每次更新历史后立即分析
  }, 500);

  // 监听情绪变化
  emotionWatch = watch([
    () => detectionStore.currentEmotion,
    () => detectionStore.currentConfidence
  ], () => {
    analyzeEmotionTrend();
  });

  // 初始分析
  setTimeout(() => {
    analyzeEmotionTrend();
  }, 500);
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

/* 工具按钮样式 - 与AI音乐按钮保持完全一致 */
.nav-tool-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 20px;
  color: var(--text);
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  font-weight: 500;
}

.nav-tool-btn:hover {
  background: rgba(139, 92, 246, 0.2);
  border-color: rgba(139, 92, 246, 0.4);
}

.nav-tool-btn.active {
  background: rgba(139, 92, 246, 0.2);
  border-color: rgba(139, 92, 246, 0.5);
}

.nav-tool-btn .btn-icon {
  font-size: 16px;
}

.nav-tool-btn .btn-label {
  white-space: nowrap;
}

.nav-tool-btn .btn-arrow {
  font-size: 12px;
  opacity: 0.7;
}

/* 警告状态样式 */
.nav-tool-btn.warning {
  background: rgba(245, 108, 108, 0.2);
  border-color: rgba(245, 108, 108, 0.5);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(245, 108, 108, 0.4);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(245, 108, 108, 0);
  }
}

.warning-badge {
  animation: bounce 1s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-3px);
  }
}

/* 分析面板 */
.analyzer-panel {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: 360px;
  max-width: calc(100vw - 20px);
  padding: 12px;
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
      border: 1px solid 
color-mix(in srgb, var(--border) 30%, transparent);
  border-radius: 12px;
  /* box-shadow: 
    0 0 20px rgba(139, 92, 246, 0.3),
    0 4px 24px rgba(0, 0, 0, 0.3); */
  z-index: 100;
}

/* 提示区域 */
.hint-section {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
  transition: all 0.3s ease;

  &.positive {
    background: rgba(103, 194, 58, 0.15);
    border: 1px solid rgba(103, 194, 58, 0.3);
  }

  &.neutral {
    background: rgba(143, 188, 143, 0.15);
    border: 1px solid rgba(143, 188, 143, 0.3);
  }

  &.negative {
    background: rgba(64, 158, 255, 0.15);
    border: 1px solid rgba(64, 158, 255, 0.3);
  }

  &.warning {
    background: rgba(245, 108, 108, 0.15);
    border: 1px solid rgba(245, 108, 108, 0.3);
    animation: warningPulse 2s ease-in-out infinite;
  }
}

@keyframes warningPulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(245, 108, 108, 0.2);
  }
  50% {
    box-shadow: 0 0 0 4px rgba(245, 108, 108, 0);
  }
}

.hint-emoji {
  font-size: 32px;
  flex-shrink: 0;
}

.hint-content {
  flex: 1;
}

.hint-title {
  font-size: 20px;
  /* font-weight: 600; */
  color: var(--text);
  margin-bottom: 4px;
}

.hint-text {
  font-size: 15px;
  color: var(--text-secondary);
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