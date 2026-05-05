<template>
    <div class="image-detector">
        <div class="detector-layout">
            <!-- 左侧：图片和上传 -->
            <div class="left-panel">
                <el-card class="glass-card">
                    <template #header>
                        <div class="card-header">
                            <span class="card-icon">📸</span>
                            <h3>图片检测</h3>
                        </div>
                    </template>

                    <el-upload v-if="!previewUrl" class="upload-area" drag :auto-upload="false"
                        :on-change="handleFileChange" accept="image/*">
                        <el-icon class="el-icon--upload" :size="48">
                            <UploadFilled />
                        </el-icon>
                        <div class="el-upload__text">
                            拖拽图片到此处或 <em>点击上传</em>
                        </div>
                        <template #tip>
                            <div class="upload-tip">支持 JPG、PNG 格式</div>
                            <div v-if="fileName" class="file-name">
                                <el-icon>
                                    <Document />
                                </el-icon>
                                {{ fileName }}
                            </div>
                        </template>
                    </el-upload>

                    <div v-if="previewUrl" class="canvas-wrapper">
                        <div v-if="fileName" class="file-info-bar">
                            <el-icon>
                                <Document />
                            </el-icon>
                            <span>{{ fileName }}</span>
                        </div>
                        <div class="canvas-container glass-card-inner">
                            <canvas ref="canvasRef"></canvas>
                        </div>

                        <div class="action-buttons">
                            <el-button type="primary" @click="detectImage" :loading="detecting" :icon="Aim" round
                                size="large">
                                {{ detecting ? '检测中...' : '开始检测' }}
                            </el-button>
                            <el-button type="primary" @click="reset" round size="large">重新选择</el-button>
                            <el-button v-if="detectionResult" @click="toggleDetectionBoxes" round size="large"
                                :type="showDetectionBoxes ? 'warning' : 'info'">
                                {{ showDetectionBoxes ? '隐藏框' : '显示框' }}
                            </el-button>
                        </div>
                    </div>
                </el-card>
            </div>

            <!-- 右侧：检测结果 -->
            <div class="right-panel">
                <el-card class="glass-card result-card">
                    <template #header>
                        <div class="card-header">
                            <span class="card-icon">🎯</span>
                            <h3>检测结果</h3>
                        </div>
                    </template>

                    <!-- 空状态占位符 -->
                    <div v-if="!detectionResult" class="empty-state">
                        <div class="empty-icon">📊</div>
                        <p>上传并检测图片后<br />将在此处显示结果</p>
                    </div>

                    <!-- 检测结果内容 -->
                    <div v-else class="results-section">
                        <!-- 单张人脸：大图标展示 -->
                        <template v-if="detectionResult.faces?.length === 1">
                            <div class="emotion-display">
                                <div class="emotion-icon-large">
                                    <span class="emotion-emoji-large">{{
                                        getEmotionEmoji(detectionResult.faces[0].emotion || 'neutral') }}</span>
                                </div>
                                <div class="emotion-name">{{ getEmotionName(detectionResult.faces[0].emotion ||
                                    'neutral') }}</div>
                                <div class="emotion-confidence">{{ (detectionResult.faces[0].confidence *
                                    100).toFixed(1)
                                }}%
                                </div>
                                <div class="face-count">1 张人脸</div>

                                <!-- ✅ 新增: 情绪纠正按钮 -->
                                <el-popover trigger="click" placement="bottom" width="200">
                                    <template #reference>
                                        <el-button link type="warning" size="small" class="feedback-btn">
                                            <el-icon>
                                                <Edit />
                                            </el-icon>
                                            纠正
                                        </el-button>
                                    </template>
                                    <div class="feedback-popover">
                                        <p class="feedback-title">选择正确情绪:</p>
                                        <div class="emotion-options">
                                            <el-button v-for="emotion in emotionList" :key="emotion" size="small"
                                                :type="emotion === detectionResult.faces[0].emotion ? 'primary' : ''"
                                                @click="submitFeedback(emotion)" round>
                                                {{ getEmotionEmoji(emotion) }} {{ getEmotionName(emotion) }}
                                            </el-button>
                                        </div>
                                    </div>
                                </el-popover>

                                <!-- 置信度分布条 -->
                                <div class="confidence-bars">
                                    <div v-for="[emotion, score] in getMainEmotions(detectionResult.faces[0].scores)"
                                        :key="emotion" class="confidence-bar-item">
                                        <span class="bar-label">
                                            <span class="bar-emoji">{{ getEmotionEmoji(emotion) }}</span>
                                            {{ getEmotionName(emotion) }}
                                        </span>
                                        <div class="bar-track">
                                            <div class="bar-fill" :style="{
                                                width: `${score * 100}%`,
                                                background: getEmotionColor(emotion),
                                                boxShadow: `0 0 8px ${getEmotionColor(emotion)}`
                                            }"></div>
                                        </div>
                                        <span class="bar-value">{{ (score * 100).toFixed(0) }}%</span>
                                    </div>
                                </div>
                            </div>
                        </template>

                        <!-- 多张人脸：分组列表展示 -->
                        <template v-else-if="detectionResult.faces?.length > 1">
                            <div class="multi-faces-display">
                                <div class="faces-header">
                                    <div class="faces-count">{{ detectionResult.faces.length }} 张人脸</div>
                                    <div class="faces-summary">{{ getEmotionName(detectionResult.faces[0].emotion ||
                                        'neutral') }} 为主</div>
                                </div>

                                <div class="faces-list">
                                    <div v-for="(face, index) in detectionResult.faces" :key="index" class="face-item">
                                        <div class="face-item-header">
                                            <div class="face-index">人脸 {{ index + 1 }}</div>
                                            <div class="face-emotion-badge" :style="{
                                                background: getEmotionColor(face.emotion),
                                                color: 'white'
                                            }">
                                                {{ getEmotionName(face.emotion) }}
                                            </div>
                                        </div>

                                        <div class="face-item-row">
                                            <div class="emotion-emoji">
                                                {{ getEmotionEmoji(face.emotion) }}
                                            </div>
                                            <div class="face-confidence">{{ (face.confidence * 100).toFixed(1) }}%</div>
                                            <div class="face-progress-bar">
                                                <div class="face-progress-track">
                                                    <div class="face-progress-fill" :style="{
                                                        width: `${face.confidence * 100}%`,
                                                        background: getEmotionColor(face.emotion),
                                                        boxShadow: `0 0 8px ${getEmotionColor(face.emotion)}`
                                                    }"></div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </template>

                        <!-- 无人脸提示 -->
                        <div v-else class="no-face-result">
                            <EmotionSVG emotion="neutral" size="large" :animated="false" style="opacity:0.4" />
                            <p>未检测到人脸</p>
                        </div>
                    </div>
                </el-card>
            </div>
        </div>

        <!-- ✅ 新增: 性能监控面板 -->
        <PerformanceMonitor :fps="perfFps" :latency="perfLatency" :skip-rate="perfSkipRate" :gpu-memory="perfGpuMemory"
            :detect-interval="perfDetectInterval" :http-latency="perfHttpLatency" :error-rate="perfErrorRate" />
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { UploadFilled, Aim, Document, Edit } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { drawCornerBox, drawEmotionLabel } from '@/utils/canvas'
import { useThemeStore } from '@/stores/theme'
import { getEmotionName, getEmotionColor, getEmotionEmoji } from '@/utils/emotion'
import { API } from '@/api/config'
import EmotionSVG from '@/components/common/EmotionSVG.vue'
import { logFeatureUsage } from '@/utils/analytics'
import PerformanceMonitor from '@/components/monitor/PerformanceMonitor.vue'
import generativeAudio from '@/utils/generativeAudio'
import wsManager from '@/api/websocket'

// ✅ 新增: 组件名称,用于 keep-alive 缓存
defineOptions({
    name: 'ImageDetector'
})

const themeStore = useThemeStore()
const previewUrl = ref(null)
const selectedFile = ref(null)
const canvasRef = ref(null)
const detecting = ref(false)
const detectionResult = ref(null)
const showDetectionBoxes = ref(true) // 控制是否显示检测框
const fileName = ref('') // 文件名
// ✅ 新增: 情绪列表
const emotionList = ['happy', 'sad', 'angry', 'surprise', 'fear', 'disgust', 'neutral']

// ✅ 新增: 性能监控数据
const perfFps = ref(0)
const perfLatency = ref(0)
const perfSkipRate = ref(0)
const perfGpuMemory = ref(0)
const perfDetectInterval = ref(1)
const perfHttpLatency = ref(0)
const perfErrorRate = ref(0)

const handleFileChange = (file) => {
    selectedFile.value = file.raw
    fileName.value = file.name // 立即保存文件名

    const reader = new FileReader()
    reader.onload = (e) => {
        previewUrl.value = e.target.result
        detectionResult.value = null
        showDetectionBoxes.value = true // 重置显示状态

        // 立即绘制图片到 Canvas
        setTimeout(() => {
            drawImagePreview()
        }, 50) // 等待 DOM 更新
    }
    reader.readAsDataURL(file.raw)
}

// 绘制图片预览（不带检测框）
const drawImagePreview = () => {
    const canvas = canvasRef.value
    if (!canvas || !previewUrl.value) return
    const ctx = canvas.getContext('2d')
    const img = new Image()
    img.onload = () => {
        // 获取容器尺寸
        const container = canvas.parentElement
        const containerWidth = container.clientWidth - 16 // 减去 padding
        const containerHeight = container.clientHeight - 16

        // ✅ 修复: 设置 Canvas 物理尺寸为容器大小,并设置CSS样式
        canvas.width = containerWidth
        canvas.height = containerHeight
        canvas.style.width = containerWidth + 'px'
        canvas.style.height = containerHeight + 'px'

        // 计算缩放比例，确保图片完整显示不溢出
        const scaleX = containerWidth / img.width
        const scaleY = containerHeight / img.height
        const scale = Math.min(scaleX, scaleY)

        // 计算图片绘制尺寸和居中位置
        const drawWidth = img.width * scale
        const drawHeight = img.height * scale
        const offsetX = (containerWidth - drawWidth) / 2
        const offsetY = (containerHeight - drawHeight) / 2

        ctx.clearRect(0, 0, containerWidth, containerHeight)
        ctx.drawImage(img, offsetX, offsetY, drawWidth, drawHeight)
    }
    img.src = previewUrl.value
}

const detectImage = async () => {
    if (!selectedFile.value) { ElMessage.warning('请先选择图片'); return }
    detecting.value = true
    const startTime = performance.now()

    try {
        const formData = new FormData()
        formData.append('file', selectedFile.value)
        const response = await fetch(API.detectImage, { method: 'POST', body: formData })
        if (!response.ok) throw new Error('检测失败')
        const result = await response.json()

        // ✅ 新增: 计算 HTTP 延迟
        const endTime = performance.now()
        perfHttpLatency.value = endTime - startTime
        perfLatency.value = perfHttpLatency.value

        detectionResult.value = result

        // 绘制带框的结果（默认显示）
        showDetectionBoxes.value = true
        drawResults(result)

        const emotion = result.faces?.[0]?.emotion || 'neutral'
        logFeatureUsage('图片检测', { emotion, faces: result.faces?.length || 0 })
        ElMessage.success('✅ 检测完成')

        // ✅ 新增: 更新性能监控数据
        perfFps.value = 1000 / perfHttpLatency.value  // 基于HTTP延迟估算FPS
        perfSkipRate.value = 0  // 图片检测无跳帧
        perfGpuMemory.value = 0  // 图片检测不直接监控GPU

        // ✅ 新增: 传递情绪数据到音乐引擎
        if (result.faces?.length > 0 && result.music_params) {
            // 通过 WebSocket 发送情绪数据，触发全局音乐更新
            wsManager.emit('image_result', {
                type: 'result',
                music_params: result.music_params,
                emotion: emotion,
                confidence: result.faces[0].confidence || 0
            })
        }

        // 保存到历史记录
        await saveToHistory(result, previewUrl.value)
    } catch (error) {
        console.error('检测错误:', error)
        perfErrorRate.value += 1  // 记录错误
        ElMessage.error('检测失败: ' + error.message)
    } finally { detecting.value = false }
}

const drawResults = (result) => {
    const canvas = canvasRef.value
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const img = new Image()
    img.onload = () => {
        // 获取容器尺寸
        const container = canvas.parentElement
        const containerWidth = container.clientWidth - 16 // 减去 padding
        const containerHeight = container.clientHeight - 16

        // ✅ 修复: 设置 Canvas 物理尺寸为容器大小,并设置CSS样式
        canvas.width = containerWidth
        canvas.height = containerHeight
        canvas.style.width = containerWidth + 'px'
        canvas.style.height = containerHeight + 'px'

        // 计算缩放比例，确保图片完整显示不溢出
        const scaleX = containerWidth / img.width
        const scaleY = containerHeight / img.height
        const scale = Math.min(scaleX, scaleY)

        // 计算图片绘制尺寸和居中位置
        const drawWidth = img.width * scale
        const drawHeight = img.height * scale
        const offsetX = (containerWidth - drawWidth) / 2
        const offsetY = (containerHeight - drawHeight) / 2

        // 清空画布
        ctx.clearRect(0, 0, containerWidth, containerHeight)
        ctx.drawImage(img, offsetX, offsetY, drawWidth, drawHeight)

        if (result.faces?.length) {
            result.faces.forEach((face, index) => {
                const color = getEmotionColor(face.emotion)

                // ✅ 修复: 缩放 bbox 坐标（格式：[x, y, width, height]）
                // 注意：width 和 height 只缩放，不加偏移量
                const scaledBbox = [
                    face.bbox[0] * scale + offsetX,  // x 坐标
                    face.bbox[1] * scale + offsetY,  // y 坐标
                    face.bbox[2] * scale,            // width (不加偏移)
                    face.bbox[3] * scale             // height (不加偏移)
                ]

                // 只在 showDetectionBoxes 为 true 时绘制检测框
                if (showDetectionBoxes.value) {
                    const totalFaces = result.faces.length
                    drawCornerBox(ctx, scaledBbox, color, 4) // 加粗描边
                    drawEmotionLabel(ctx, scaledBbox, face.emotion, face.confidence, themeStore.currentTheme, index + 1, totalFaces)
                }
            })
        }
    }
    img.src = previewUrl.value
}

// 切换检测框显示/隐藏
const toggleDetectionBoxes = () => {
    showDetectionBoxes.value = !showDetectionBoxes.value
    if (detectionResult.value) {
        drawResults(detectionResult.value)
    }
}

// 过滤主要情绪（只显示 > 5% 的情绪）
const getMainEmotions = (scores) => {
    return Object.entries(scores)
        .filter(([_, score]) => score > 0.05) // 只显示 > 5% 的情绪
        .sort((a, b) => b[1] - a[1]) // 按分数降序
}

const reset = () => {
    previewUrl.value = null
    selectedFile.value = null
    detectionResult.value = null
    showDetectionBoxes.value = true
    fileName.value = ''
}

// 保存到历史记录
const saveToHistory = async (result, thumbnail) => {
    try {
        const dominantEmotion = result.faces?.[0]?.emotion || 'neutral'
        const confidence = result.faces?.[0]?.confidence || 0
        const faces = result.faces || []

        await fetch(API.historySave, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                detection_type: 'image',
                results: faces,
                source: '单张图片检测',
                image_path: '',
                image_type: 'single',
                thumbnail: thumbnail,
                dominant_emotion: dominantEmotion,
                confidence: confidence,
                detected_faces: faces  // ✅ 修复: 添加 detected_faces 字段
            })
        })
        console.log('✅ 历史记录已保存')
    } catch (error) {
        console.error('保存历史记录失败:', error)
    }
}

// ✅ 新增: 提交情绪纠正反馈
const submitFeedback = async (correctEmotion) => {
    try {
        const response = await fetch(API.feedback, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                emotion: detectionResult.value.faces?.[0]?.emotion,
                predicted_emotion: detectionResult.value.faces?.[0]?.emotion,
                correct_emotion: correctEmotion,
                feedback_type: 'incorrect'
            })
        })

        if (response.ok) {
            ElMessage.success('✅ 感谢反馈！系统将自动优化')
        } else {
            throw new Error('提交失败')
        }
    } catch (error) {
        console.error('反馈提交失败:', error)
        ElMessage.error('反馈提交失败')
    }
}
</script>

<style scoped>
.image-detector {
    height: 100%;
    overflow-y: auto;
    padding-right: 4px;
}

/* ✅ 新增: 图片检测器主容器滚动条样式 */
.image-detector::-webkit-scrollbar {
    width: 6px;
}

.image-detector::-webkit-scrollbar-thumb {
    background: rgba(146, 78, 255, 0.3);
    border-radius: 3px;
}

.image-detector::-webkit-scrollbar-thumb:hover {
    background: rgba(146, 78, 255, 0.5);
}

.detector-layout {
    display: grid;
    grid-template-columns: 1fr 320px;
    gap: 12px;
    height: 100%;
}

.left-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow-y: auto;
    padding-right: 4px;
}

/* ✅ 新增: 左侧面板滚动条样式 */
.left-panel::-webkit-scrollbar {
    width: 6px;
}

.left-panel::-webkit-scrollbar-thumb {
    background: rgba(146, 78, 255, 0.3);
    border-radius: 3px;
}

.left-panel::-webkit-scrollbar-thumb:hover {
    background: rgba(146, 78, 255, 0.5);
}

.left-panel .glass-card {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    gap: 12px;
    color: var(--text-secondary);
}

.empty-icon {
    font-size: 48px;
    opacity: 0.5;
}

.empty-state p {
    font-size: 13px;
    text-align: center;
    line-height: 1.6;
    margin: 0;
}

.glass-card {
    border-radius: var(--radius-md);
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.card-header {
    display: flex;
    align-items: center;
    gap: 10px;
}

.card-header h3 {
    font-size: 17px;
    font-weight: 100;
    margin: 0;
}

.card-icon {
    font-size: 22px;
}

.upload-area {
    margin-bottom: 12px;
    /* ✅ 优化: 减小固定高度，更紧凑 */
    min-height: 730px;
    height: 730px;
    display: flex;
    flex-direction: column;
}

.upload-area :deep(.el-upload) {
    flex: 1;
    display: flex;
}

.upload-area :deep(.el-upload-dragger) {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    /* ✅ 优化: 减小最小高度，避免大片空白 */
    min-height: 500px;
    height: 100%;
}

.upload-tip {
    margin-top: 8px;
    font-size: 12px;
    color: var(--text-secondary);
    opacity: 0.7;
}

:deep(.el-upload-dragger) {
    padding: 40px 16px;
}

.right-panel {
    height: 100%;
    overflow-y: auto;
}

/* ✅ 新增: 右侧面板滚动条样式 */
.right-panel::-webkit-scrollbar {
    width: 6px;
}

.right-panel::-webkit-scrollbar-thumb {
    background: rgba(146, 78, 255, 0.3);
    border-radius: 3px;
}

.right-panel::-webkit-scrollbar-thumb:hover {
    background: rgba(146, 78, 255, 0.5);
}

.right-panel .el-card {
    height: 100%;
    display: flex;
    flex-direction: column;
}

.right-panel .el-card__body {
    flex: 1;
    overflow-y: auto;
}

.result-card {
    height: 100%;
}

.canvas-wrapper {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8px;
    min-height: 0;
    overflow: hidden;
}

.file-info-bar {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 10px;
    font-size: 11px;
    color: var(--text-secondary);
    background: color-mix(in srgb, var(--primary) 8%, transparent);
    border-radius: 6px;
    flex-shrink: 0;
}

.glass-card-inner:hover {
    border-color: color-mix(in srgb, var(--border) 60%, var(--primary));
}

.glass-card-inner {
    background: color-mix(in srgb, var(--card-bg) 55%, transparent);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 8px;
    transition: all 0.2s ease;
}

.canvas-container {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 300px;
    overflow: hidden;
    padding: 8px;
    position: relative;
}

.canvas-container canvas {
    width: 100%;
    max-height: calc(100vh - 280px);
    min-height: 400px;
    border-radius: 10px;
    background: #000;
    display: block;
    position: relative;
    z-index: 1;
}

.action-buttons {
    display: flex;
    gap: 8px;
    justify-content: center;
    flex-shrink: 0;
    flex-wrap: wrap;
    padding: 0 4px;
}

.action-buttons .el-button {
    padding: 10px 20px;
    font-size: 15px;
    white-space: nowrap;
}

/* 文件名显示 */
.file-name {
    display: flex;
    align-items: center;
    gap: 6px;
    justify-content: center;
    font-size: 12px;
    color: var(--text-secondary);
    margin-top: 8px;
    padding: 6px 12px;
    background: color-mix(in srgb, var(--primary) 10%, transparent);
    border-radius: 6px;
}

.results-section {
    display: flex;
    flex-direction: column;
    gap: 0;
    flex: 1;
    overflow: hidden;
}

/* 情绪展示（参考实时检测风格） */
.emotion-display {
    padding: 16px 8px;
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    overflow-y: auto;
    animation: fadeIn 0.3s ease;
    /* ✅ 新增: 设置最大高度，超出后滚动 */
    max-height: calc(100vh - 280px);
}

/* ✅ 新增: 情绪显示区域滚动条样式 */
.emotion-display::-webkit-scrollbar {
    width: 6px;
}

.emotion-display::-webkit-scrollbar-thumb {
    background: rgba(146, 78, 255, 0.3);
    border-radius: 3px;
}

.emotion-display::-webkit-scrollbar-thumb:hover {
    background: rgba(146, 78, 255, 0.5);
}

.emotion-icon-large {
    margin-bottom: 2px;
    /* filter: drop-shadow(0 0 20px rgba(113, 57, 255, 0.25)); */
}

/* 大 Emoji 表情样式 */
.emotion-emoji-large {
    font-size: 64px;
    line-height: 1;
    display: block;
    /* filter: drop-shadow(0 0 20px rgba(113, 57, 255, 0.25)); */
}

.emotion-name {
    font-size: 20px;
    /* font-weight: 800; */
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    flex-shrink: 0;
}

.emotion-confidence {
    font-size: 24px;
    /* font-weight: 800; */
    color: var(--highlight);
    flex-shrink: 0;
    /* text-shadow: 0 0 12px rgba(226, 202, 255, 0.3); */
}

/* ✅ 新增: 反馈按钮样式 */
.feedback-btn {
    margin-top: 4px;
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 4px;
}

.feedback-popover {
    padding: 8px 0;
}

.feedback-title {
    font-size: 13px;
    /* font-weight: 100; */
    color: var(--text);
    margin: 0 0 10px 0;
    text-align: center;
}

.emotion-options {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    justify-content: center;
}

.face-count {
    font-size: 11px;
    color: var(--text-secondary);
    /* font-weight: 100; */
    flex-shrink: 0;
}

/* 置信度条 */
.confidence-bars {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 5px;
    margin-top: 10px;
    flex-shrink: 0;
}

.confidence-bar-item {
    display: grid;
    grid-template-columns: 70px 1fr 34px;
    align-items: center;
    gap: 6px;
}

.bar-label {
    font-size: 10px;
    text-align: left;
    display: flex;
    align-items: center;
    gap: 3px;
    /* font-weight: 100; */
    color: var(--text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Emoji 表情样式 */
.bar-emoji {
    font-size: 14px;
    line-height: 1;
    flex-shrink: 0;
}

.bar-track {
    height: 6px;
    background: color-mix(in srgb, var(--text) 10%, transparent);
    border-radius: 4px;
    overflow: hidden;
}

.bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.bar-value {
    font-size: 10px;
    font-weight: 100;
    text-align: right;
    color: var(--text);
}

/* 多张人脸展示 */
.multi-faces-display {
    /* padding: 12px 8px; */
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 10px;
    overflow-y: auto;
    animation: fadeIn 0.3s ease;
    /* ✅ 新增: 设置最大高度，超出后滚动 */
    max-height: calc(100vh - 280px);
}

/* ✅ 新增: 多人脸显示区域滚动条样式 */
.multi-faces-display::-webkit-scrollbar {
    width: 6px;
}

.multi-faces-display::-webkit-scrollbar-thumb {
    background: rgba(146, 78, 255, 0.3);
    border-radius: 3px;
}

.multi-faces-display::-webkit-scrollbar-thumb:hover {
    background: rgba(146, 78, 255, 0.5);
}

.faces-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 12px;
    background: color-mix(in srgb, var(--primary) 15%, transparent);
    backdrop-filter: blur(10px);
    border-radius: 10px;
    border: 1px solid var(--border);
    flex-shrink: 0;
}

.faces-count {
    font-size: 14px;
    /* font-weight: 800; */
    color: var(--primary);
}

.faces-summary {
    font-size: 11px;
    color: var(--text-secondary);
    /* font-weight: 100; */
}

.faces-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    flex: 1;
    overflow-y: auto;
    /* ✅ 新增: 设置最大高度，避免过高 */
    /* max-height: 400px; */
}

/* ✅ 新增: 人脸列表滚动条样式 */
.faces-list::-webkit-scrollbar {
    width: 6px;
}

.faces-list::-webkit-scrollbar-thumb {
    background: rgba(146, 78, 255, 0.3);
    border-radius: 3px;
}

.faces-list::-webkit-scrollbar-thumb:hover {
    background: rgba(146, 78, 255, 0.5);
}

.face-item {
    padding: 12px;
    background: color-mix(in srgb, var(--card-bg) 80%, transparent);
    backdrop-filter: blur(10px);
    border-radius: 10px;
    border: 1px solid var(--border);
    transition: all 0.2s ease;
}

.face-item:hover {
    border-color: color-mix(in srgb, var(--border) 60%, var(--primary));
    transform: translateY(-1px);
}

.face-item-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.face-index {
    font-size: 10px;
    font-weight: 100;
    color: var(--text-secondary);
}

.face-emotion-badge {
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 100;
}

.face-item-content {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
}

/* 单行横向排列 */
.face-item-row {
    display: flex;
    align-items: center;
    gap: 10px;
}

/* Emoji 表情样式 */
.emotion-emoji {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    line-height: 1;
    font-size: 24px;
    flex-shrink: 0;
    /* filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.3)); */
}

.face-confidence {
    font-size: 18px;
    /* font-weight: 800; */
    color: var(--highlight);
    /* text-shadow: 0 0 8px rgba(226, 202, 255, 0.3); */
    flex-shrink: 0;
    min-width: 60px;
}

/* 进度条 */
.face-progress-bar {
    flex: 1;
}

.face-progress-track {
    height: 6px;
    background: color-mix(in srgb, var(--text) 8%, transparent);
    border-radius: 4px;
    overflow: hidden;
}

.face-progress-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 迷你置信度条 */
.face-item-bars {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.mini-bar-item {
    display: grid;
    grid-template-columns: 55px 1fr 30px;
    align-items: center;
    gap: 5px;
}

.mini-bar-label {
    font-size: 9px;
    /* font-weight: 100; */
    color: var(--text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.mini-bar-track {
    height: 4px;
    background: color-mix(in srgb, var(--text) 8%, transparent);
    border-radius: 3px;
    overflow: hidden;
}

.mini-bar-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.3s ease;
}

.mini-bar-value {
    font-size: 9px;
    font-weight: 100;
    color: var(--text-secondary);
    text-align: right;
}

/* 无人脸提示 */
.no-face-result {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 20px;
    gap: 12px;
    color: var(--text-secondary);
}

.no-face-result p {
    font-size: 13px;
    margin: 0;
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(12px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@media (max-width: 1200px) {
    .detector-layout {
        grid-template-columns: 1fr;
    }

    .right-panel {
        max-height: 50vh;
    }
}
</style>
