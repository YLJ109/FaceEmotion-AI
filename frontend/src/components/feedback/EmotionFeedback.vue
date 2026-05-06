<template>
    <!-- 情绪反馈对话框（静态快照） -->
    <el-dialog v-model="dialogVisible" title="情绪识别反馈" width="500px" :close-on-click-modal="false">
        <div class="feedback-content">
            <!-- ✅ 新增: 静态快照预览区 -->
            <div v-if="snapshot?.image" class="snapshot-section">
                <p class="snapshot-label">📸 检测时刻快照：</p>
                <div class="snapshot-container">
                    <img :src="snapshot.image" alt="检测快照" class="snapshot-image" />
                    <div class="snapshot-overlay">
                        <div class="snapshot-info">
                            <div class="info-item">
                                <span class="info-label">情绪：</span>
                                <span class="info-value">{{ getEmotionName(snapshot.emotion) }}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">置信度：</span>
                                <span class="info-value">{{ (snapshot.confidence * 100).toFixed(1) }}%</span>
                            </div>
                            <div class="info-item" v-if="snapshot.bbox">
                                <span class="info-label">人脸位置：</span>
                                <span class="info-value">({{ snapshot.bbox[0].toFixed(0) }}, {{
                                    snapshot.bbox[1].toFixed(0) }})</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">时间：</span>
                                <span class="info-value">{{ formatTimestamp(snapshot.timestamp) }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="feedback-info">
                <p class="predicted-label">系统识别：</p>
                <div class="predicted-emotion">
                    <EmotionSVG :emotion="predictedEmotionValue" size="small" :animated="false" />
                    <span class="emotion-name">{{ getEmotionName(predictedEmotionValue) }}</span>
                    <span class="emotion-confidence">{{ (predictedConfidenceValue * 100).toFixed(1) }}%</span>
                </div>
            </div>

            <div class="correction-section">
                <p class="correction-label">实际情绪是：</p>
                <div class="emotion-grid">
                    <div v-for="emotion in emotionList" :key="emotion" class="emotion-option"
                        :class="{ selected: selectedEmotion === emotion }" @click="selectedEmotion = emotion">
                        <EmotionSVG :emotion="emotion" size="small" :animated="false" />
                        <span>{{ getEmotionName(emotion) }}</span>
                    </div>
                </div>
            </div>

            <div class="notes-section">
                <p class="notes-label">备注（可选）：</p>
                <el-input v-model="notes" type="textarea" :rows="2" placeholder="描述当时的场景或表情强度..." maxlength="200"
                    show-word-limit class="notes-input" />
            </div>
        </div>

        <template #footer>
            <div class="dialog-footer">
                <el-button @click="dialogVisible = false" :icon="Close">
                    取消
                </el-button>
                <el-button type="primary" @click="submitFeedback" :disabled="!selectedEmotion">
                    提交反馈
                </el-button>
            </div>
        </template>
    </el-dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Close } from '@element-plus/icons-vue'
import EmotionSVG from '@/components/common/EmotionSVG.vue'
import { getEmotionName } from '@/utils/emotion'
import { API } from '@/api/config'

const props = defineProps({
    visible: Boolean,
    // ✅ 修改: 支持静态快照数据
    snapshot: Object,  // { image, bbox, emotion, confidence, timestamp }
    // 兼容旧的 props
    predictedEmotion: String,
    predictedConfidence: Number
})

const emit = defineEmits(['update:visible', 'submitted'])

const emotionList = ['happy', 'sad', 'angry', 'surprised', 'fearful', 'disgust', 'neutral']
const selectedEmotion = ref('')
const notes = ref('')

const dialogVisible = ref(false)

// ✅ 新增: 优先使用快照数据的计算属性
const predictedEmotionValue = computed(() => {
    return props.snapshot?.emotion || props.predictedEmotion || 'neutral'
})

const predictedConfidenceValue = computed(() => {
    return props.snapshot?.confidence || props.predictedConfidence || 0
})

// ✅ 新增: 格式化时间戳
const formatTimestamp = (timestamp) => {
    if (!timestamp) return '-'
    const date = new Date(timestamp)
    return date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    })
}

// 监听 visible 变化
watch(() => props.visible, (val) => {
    dialogVisible.value = val
    if (val) {
        selectedEmotion.value = ''
        notes.value = ''
        // ✅ 修改: 优先使用快照数据，如果没有则使用实时数据
        console.log('📊 反馈对话框打开:', {
            snapshot: props.snapshot,
            predictedEmotion: props.predictedEmotion,
            predictedConfidence: props.predictedConfidence
        })
    }
})

watch(dialogVisible, (val) => {
    emit('update:visible', val)
})

// 提交反馈
async function submitFeedback() {
    if (!selectedEmotion.value) {
        ElMessage.warning('请选择实际情绪')
        return
    }

    try {
        const response = await fetch(API.feedback, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                emotion: props.snapshot?.emotion || props.predictedEmotion,
                predicted_emotion: props.snapshot?.emotion || props.predictedEmotion,
                correct_emotion: selectedEmotion.value,
                feedback_type: 'incorrect',
                confidence: props.snapshot?.confidence || props.predictedConfidence,
                bbox: props.snapshot?.bbox,
                snapshot: props.snapshot?.image,  // ✅ 新增: 提交快照数据
                timestamp: props.snapshot?.timestamp,
                notes: notes.value
            })
        })

        if (response.ok) {
            ElMessage.success('反馈已提交，系统将自动学习优化')
            emit('submitted')
            dialogVisible.value = false
        } else {
            ElMessage.error('提交失败，请重试')
        }
    } catch (error) {
        console.error('提交反馈失败:', error)
        ElMessage.error('网络错误，请稍后重试')
    }
}
</script>

<style scoped>
.feedback-content {
    padding: 10px 0;
}

/* ✅ 新增: 静态快照预览区样式 */
.snapshot-section {
    margin-bottom: 20px;
}

.snapshot-label {
    font-size: 14px;
    color: var(--text-secondary, #888);
    margin-bottom: 10px;
    font-weight: 100;
}

.snapshot-container {
    position: relative;
    border-radius: 8px;
    overflow: hidden;
    border: 2px solid rgba(255, 255, 255, 0.1);
}

.snapshot-image {
    width: 100%;
    max-height: 300px;
    object-fit: contain;
    display: block;
    background: #000;
}

.snapshot-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(to top, rgba(0, 0, 0, 0.85), transparent);
    padding: 12px;
}

.snapshot-info {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
}

.info-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
}

.info-label {
    color: rgba(255, 255, 255, 0.7);
    font-weight: 100;
}

.info-value {
    color: var(--text);
    /* ✅ 修复: 使用主题变量 */
    font-weight: 100;
    font-family: 'Consolas', 'Monaco', monospace;
}

.feedback-info {
    margin-bottom: 20px;
    padding: 15px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
}

.predicted-label {
    font-size: 14px;
    color: var(--text-secondary);
    /* ✅ 修复: 使用主题变量 */
    margin-bottom: 10px;
}

.predicted-emotion {
    display: flex;
    align-items: center;
    gap: 10px;
}

.emotion-name {
    font-size: 16px;
    font-weight: 100;
    color: var(--text);
    /* ✅ 修复: 使用主题变量 */
}

.emotion-confidence {
    font-size: 14px;
    color: var(--success-color, #4CAF50);
    margin-left: auto;
}

.correction-section {
    margin-bottom: 20px;
}

.correction-label {
    font-size: 14px;
    color: var(--text-secondary, #888);
    margin-bottom: 12px;
}

.emotion-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
}

.emotion-option {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 12px 8px;
    background: rgba(255, 255, 255, 0.05);
    border: 2px solid transparent;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;
    gap: 6px;
}

.emotion-option:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.2);
}

.emotion-option.selected {
    background: rgba(102, 126, 234, 0.2);
    border-color: #667eea;
    box-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
}

.emotion-option span {
    font-size: 12px;
    color: var(--text-secondary);
    /* ✅ 修复: 使用主题变量 */
}

.emotion-option.selected span {
    color: var(--text);
    /* ✅ 修复: 使用主题变量 */
    font-weight: 100;
}

.notes-section {
    margin-top: 15px;
}

.notes-label {
    font-size: 14px;
    color: var(--text-secondary, #888);
    margin-bottom: 8px;
}

/* ✅ 备注输入框使用主题变量 */
:deep(.notes-input .el-textarea__inner) {
    background-color: var(--bg-input, rgba(255, 255, 255, 0.05)) !important;
    border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1)) !important;
    color: var(--text-primary, #fff) !important;
}

:deep(.notes-input .el-textarea__inner:focus) {
    border-color: var(--primary-color, #409EFF) !important;
}

:deep(.notes-input .el-input__count) {
    color: var(--text-secondary, #888) !important;
    background: transparent !important;
}

/* ✅ 底部按钮区域 */
.dialog-footer {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    padding-top: 15px;
    border-top: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
}

/* 取消按钮 - 与提交按钮样式一致 */
:deep(.dialog-footer .el-button--default) {
    background: var(--card-bg) !important;
    /* ✅ 修复: 使用主题变量 */
    border: 1px solid var(--border) !important;
    /* ✅ 修复: 使用主题变量 */
    color: var(--text) !important;
    /* ✅ 修复: 使用主题变量 */
    border-radius: 20px !important;
    padding: 10px 24px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
}

:deep(.dialog-footer .el-button--default:hover) {
    background: color-mix(in srgb, var(--primary) 12%, transparent) !important;
    /* ✅ 修复: 使用主题变量 */
    border-color: var(--primary-light) !important;
    /* ✅ 修复: 使用主题变量 */
    color: var(--text) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
}

/* 提交按钮 */
:deep(.dialog-footer .el-button--primary) {
    background: var(--gradient) !important;
    /* ✅ 修复: 使用主题变量 */
    border: none !important;
    color: var(--text) !important;
    /* ✅ 修复: 使用主题变量 */
    border-radius: 20px !important;
    padding: 10px 24px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(113, 57, 255, 0.4) !important;
    /* ✅ 修复: 使用主题色 */
}

:deep(.dialog-footer .el-button--primary:hover) {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(113, 57, 255, 0.5) !important;
    /* ✅ 修复: 使用主题色 */
}
</style>
