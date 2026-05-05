<template>
    <!-- 情绪反馈对话框 -->
    <el-dialog v-model="dialogVisible" title="情绪识别反馈" width="400px" :close-on-click-modal="false">
        <div class="feedback-content">
            <div class="feedback-info">
                <p class="predicted-label">系统识别：</p>
                <div class="predicted-emotion">
                    <EmotionSVG :emotion="predictedEmotion" size="small" :animated="false" />
                    <span class="emotion-name">{{ getEmotionName(predictedEmotion) }}</span>
                    <span class="emotion-confidence">{{ (predictedConfidence * 100).toFixed(1) }}%</span>
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
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Close } from '@element-plus/icons-vue'
import EmotionSVG from '@/components/common/EmotionSVG'
import { getEmotionName } from '@/utils/emotion'
import { API } from '@/api/config'

const props = defineProps({
    visible: Boolean,
    predictedEmotion: String,
    predictedConfidence: Number
})

const emit = defineEmits(['update:visible', 'submitted'])

const emotionList = ['happy', 'sad', 'angry', 'surprised', 'fearful', 'disgust', 'neutral']
const selectedEmotion = ref('')
const notes = ref('')

const dialogVisible = ref(false)

// 监听 visible 变化
watch(() => props.visible, (val) => {
    dialogVisible.value = val
    if (val) {
        selectedEmotion.value = ''
        notes.value = ''
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
                emotion: props.predictedEmotion,
                predicted_emotion: props.predictedEmotion,
                correct_emotion: selectedEmotion.value,
                feedback_type: 'incorrect',
                confidence: props.predictedConfidence,
                notes: notes.value
            })
        })

        if (response.ok) {
            ElMessage.success('✅ 反馈已提交，系统将自动学习优化')
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

.feedback-info {
    margin-bottom: 20px;
    padding: 15px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
}

.predicted-label {
    font-size: 14px;
    color: #888;
    margin-bottom: 10px;
}

.predicted-emotion {
    display: flex;
    align-items: center;
    gap: 10px;
}

.emotion-name {
    font-size: 16px;
    font-weight: 600;
    color: #fff;
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
    color: #ccc;
}

.emotion-option.selected span {
    color: #fff;
    font-weight: 600;
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

/* 取消按钮 - 与反馈按钮样式一致 */
:deep(.dialog-footer .el-button--default) {
    background: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    color: #fff !important;
    border-radius: 50% !important;
    width: 40px !important;
    height: 40px !important;
    padding: 0 !important;
    font-size: 16px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
}

:deep(.dialog-footer .el-button--default:hover) {
    background: rgba(255, 255, 255, 0.15) !important;
    border-color: rgba(255, 255, 255, 0.4) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
}

/* 提交按钮 */
:deep(.dialog-footer .el-button--primary) {
    background: linear-gradient(135deg, #409EFF 0%, #2563eb 100%) !important;
    border: none !important;
    color: #fff !important;
    border-radius: 20px !important;
    padding: 10px 24px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4) !important;
}

:deep(.dialog-footer .el-button--primary:hover) {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(64, 158, 255, 0.5) !important;
}
</style>
