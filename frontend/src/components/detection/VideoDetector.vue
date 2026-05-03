<template>
    <div class="video-detector">
        <div class="detector-layout">
            <!-- 左侧：视频上传和播放 -->
            <div class="left-panel">
                <el-card class="glass-card">
                    <template #header>
                        <div class="card-header">
                            <span class="card-icon">🎬</span>
                            <h3>视频检测 <span class="badge">Beta</span></h3>
                        </div>
                    </template>

                    <!-- 上传区域（未选择视频时显示） -->
                    <el-upload v-if="!videoUrl" class="upload-area" drag :auto-upload="false"
                        :on-change="handleVideoChange" accept="video/*">
                        <el-icon class="el-icon--upload" :size="48">
                            <VideoPlay />
                        </el-icon>
                        <div class="el-upload__text">拖拽视频到此处或 <em>点击上传</em></div>
                        <template #tip>
                            <div class="el-upload__tip">支持 MP4、AVI、MOV 格式</div>
                        </template>
                    </el-upload>

                    <div v-if="videoUrl" class="video-section">
                        <div class="video-container glass-card-inner">
                            <div class="video-wrapper">
                                <video ref="videoRef" :src="videoUrl" controls @loadedmetadata="onVideoLoaded"
                                    @timeupdate="onVideoTimeUpdate" @play="onVideoPlay" @pause="onVideoPause"
                                    @seeking="onVideoSeeking" @seeked="onVideoSeeked"></video>
                                <canvas ref="videoCanvasRef" class="video-canvas-overlay"></canvas>
                            </div>
                        </div>
                        <div class="control-panel">
                            <el-button type="primary" @click="startDetection" :loading="processing" round size="large"
                                :icon="VideoPlay2">
                                {{ processing ? '处理中...' : '开始分析' }}
                            </el-button>
                            <el-button @click="reset" round size="large">重新选择</el-button>
                        </div>
                        <div v-if="processing" class="floating-progress">
                            <div class="floating-progress-card">
                                <el-progress :percentage="progress" :stroke-width="12" />
                                <p class="progress-status">{{ statusText.replace(/\s*\d+%/, '') }}</p>
                            </div>
                        </div>
                    </div>
                </el-card>
            </div>

            <!-- 右侧：检测结果 -->
            <div class="right-panel">
                <el-card class="glass-card result-card">
                    <template #header>
                        <div class="card-header">
                            <span class="card-icon">📊</span>
                            <h3>检测结果</h3>
                        </div>
                    </template>

                    <!-- 空状态占位符 -->
                    <div v-if="results.length === 0" class="empty-state">
                        <div class="empty-icon">📈</div>
                        <p>上传并分析视频后<br />将在此处显示统计结果</p>
                    </div>

                    <!-- 检测结果内容 -->
                    <div v-else class="results-section">
                        <el-row :gutter="12" class="stats-cards">
                            <el-col :span="12">
                                <el-card class="stat-card glass-card-inner">
                                    <div class="stat-value">{{ totalFrames }}</div>
                                    <div class="stat-label">总帧数</div>
                                </el-card>
                            </el-col>
                            <el-col :span="12">
                                <el-card class="stat-card glass-card-inner">
                                    <div class="stat-value">{{ detectedFaces }}</div>
                                    <div class="stat-label">检测到人脸</div>
                                </el-card>
                            </el-col>
                            <el-col :span="12">
                                <el-card class="stat-card glass-card-inner">
                                    <div class="stat-value">
                                        <span class="dominant-emoji-large">{{ getEmotionEmoji(dominantEmotion) || '😐'
                                            }}</span>
                                    </div>
                                    <div class="stat-label">主导情绪</div>
                                    <div class="stat-desc">{{ getEmotionName(dominantEmotion) }}</div>
                                </el-card>
                            </el-col>
                            <el-col :span="12">
                                <el-card class="stat-card glass-card-inner">
                                    <div class="stat-value">{{ avgConfidence.toFixed(1) }}%</div>
                                    <div class="stat-label">平均置信度</div>
                                </el-card>
                            </el-col>
                        </el-row>

                        <div class="emotion-distribution glass-card-inner">
                            <h5>情绪分布</h5>
                            <div v-for="item in sortedEmotionDistribution" :key="item.emotion"
                                class="distribution-item">
                                <span class="dist-emoji">{{ getEmotionEmoji(item.emotion) }}</span>
                                <span class="name">{{ getEmotionName(item.emotion) }}</span>
                                <el-progress :percentage="item.percentage" :color="getEmotionColor(item.emotion)"
                                    :stroke-width="8" :show-text="false" />
                                <span class="count">{{ item.count }}帧</span>
                            </div>
                            <div v-if="sortedEmotionDistribution.length === 0" class="empty-distribution">
                                暂无情绪数据
                            </div>
                        </div>

                        <div v-if="keyFramePreviews.length > 0" class="key-frames-section glass-card-inner">
                            <h5>关键帧预览 ({{ keyFramePreviews.length }}个时间段)</h5>
                            <div class="key-frames-grid">
                                <div v-for="(segment, index) in keyFramePreviews" :key="index" class="key-frame-item">
                                    <div class="frame-number">{{ segment.startFrame }}-{{ segment.endFrame }}</div>
                                    <div class="frame-emotion">
                                        <span class="frame-emoji">{{ getEmotionEmoji(segment.dominantEmotion) }}</span>
                                        <span class="frame-time">{{ segment.startTime.toFixed(1) }}s-{{
                                            segment.endTime.toFixed(1)
                                        }}s</span>
                                    </div>
                                    <div class="frame-count">{{ segment.count }}帧</div>
                                </div>
                            </div>
                        </div>

                        <div class="export-buttons">
                            <el-button size="small" @click="exportJSON" round>导出 JSON</el-button>
                            <el-button size="small" @click="exportCSV" round>导出 CSV</el-button>
                        </div>
                    </div>
                </el-card>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { VideoPlay as VideoPlayIcon, VideoPlay as VideoPlay2 } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useThemeStore } from '@/stores/theme'
import { getEmotionName, getEmotionColor, getEmotionEmoji } from '@/utils/emotion'
import { drawCornerBox, drawEmotionLabel } from '@/utils/canvas'
import { API } from '@/api/config'
import { logFeatureUsage } from '@/utils/analytics'

const themeStore = useThemeStore()
const videoUrl = ref(null)
const selectedFile = ref(null)
const videoRef = ref(null)
const videoCanvasRef = ref(null)
const processing = ref(false)
const progress = ref(0)
const statusText = ref('')
const results = ref([])
const totalFrames = ref(0)

// 视频播放状态
let animationFrameId = null
let isPlaying = false

const detectedFaces = computed(() => results.value.filter(r => r.faces && r.faces.length > 0).length)
const dominantEmotion = computed(() => {
    const emotions = results.value.filter(r => r.faces?.length).map(r => r.faces[0].emotion)
    if (!emotions.length) return 'neutral'
    const c = {}; emotions.forEach(e => c[e] = (c[e] || 0) + 1)
    const top = Object.keys(c).reduce((a, b) => c[a] > c[b] ? a : b)

    // ✅ 调试: 打印主导情绪值
    console.log('🎯 主导情绪:', top, '表情:', getEmotionEmoji(top))

    return top
})
const avgConfidence = computed(() => {
    const cf = results.value.filter(r => r.faces?.length).map(r => r.faces[0].confidence)
    return cf.length ? cf.reduce((a, b) => a + b, 0) / cf.length * 100 : 0
})
const emotionDistribution = computed(() => {
    const d = {}
    results.value.filter(r => r.faces?.length).forEach(r => {
        const e = r.faces[0].emotion; d[e] = (d[e] || 0) + 1
    })
    return d
})

// ✅ 修复: 排序后的情绪分布,并计算总数
const sortedEmotionDistribution = computed(() => {
    const dist = emotionDistribution.value
    const total = Object.values(dist).reduce((sum, count) => sum + count, 0)

    // 转换为数组并排序
    return Object.entries(dist)
        .map(([emotion, count]) => ({
            emotion,
            count,
            percentage: total > 0 ? (count / total) * 100 : 0
        }))
        .sort((a, b) => b.count - a.count)
})

// 关键帧预览数据（合并连续相同情绪的时间段）
const keyFramePreviews = computed(() => {
    const framesWithFaces = results.value.filter(r => r.faces && r.faces.length > 0)

    // ✅ 添加调试日志
    console.log('📊 总帧数:', results.value.length)
    console.log('📊 有脸帧数:', framesWithFaces.length)
    if (framesWithFaces.length > 0) {
        console.log('📊 第一帧:', framesWithFaces[0])
        console.log('📊 最后一帧:', framesWithFaces[framesWithFaces.length - 1])
    }

    if (framesWithFaces.length === 0) return []

    // 合并连续相同情绪的时间段
    const segments = []
    let currentSegment = {
        startFrame: framesWithFaces[0].frame,
        endFrame: framesWithFaces[0].frame,
        startTime: framesWithFaces[0].timestamp,
        endTime: framesWithFaces[0].timestamp,
        dominantEmotion: framesWithFaces[0].faces[0].emotion,
        count: 1
    }

    for (let i = 1; i < framesWithFaces.length; i++) {
        const frame = framesWithFaces[i]
        const emotion = frame.faces[0].emotion

        // ✅ 调试日志
        if (i < 5) {
            console.log(`🔍 帧 ${frame.frame}: emotion=${emotion}, timestamp=${frame.timestamp}, current=${currentSegment.dominantEmotion}`)
        }

        // 如果情绪相同，合并到当前段
        if (emotion === currentSegment.dominantEmotion) {
            currentSegment.endFrame = frame.frame
            currentSegment.endTime = frame.timestamp
            currentSegment.count++
        } else {
            // 情绪不同，保存当前段并开始新段
            segments.push({ ...currentSegment })
            currentSegment = {
                startFrame: frame.frame,
                endFrame: frame.frame,
                startTime: frame.timestamp,
                endTime: frame.timestamp,
                dominantEmotion: emotion,
                count: 1
            }
        }
    }

    // 添加最后一个段
    segments.push({ ...currentSegment })

    // ✅ 调试日志
    console.log(' 合并后的时间段:', segments)

    // 最多显示20个时间段
    return segments.slice(0, 20)
})

const handleVideoChange = (file) => {
    videoUrl.value = URL.createObjectURL(file.raw)
    selectedFile.value = file.raw
    results.value = []
}

const onVideoLoaded = () => {
    const v = videoRef.value
    if (v) totalFrames.value = Math.floor(v.duration * 30)
}

// 视频时间更新时绘制检测框
const onVideoTimeUpdate = () => {
    if (!videoRef.value || !videoCanvasRef.value || results.value.length === 0) return
    drawDetectionBoxes()
}

// 视频开始播放
const onVideoPlay = () => {
    console.log('▶️ 视频开始播放')
    isPlaying = true
    drawLoop()
}

// 视频暂停
const onVideoPause = () => {
    console.log('⏸️ 视频暂停')
    isPlaying = false
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId)
        animationFrameId = null
    }
}

// 用户拖动进度条（开始）
const onVideoSeeking = () => {
    console.log(' 开始拖动进度条')
    drawDetectionBoxes()
}

// 用户拖动进度条（结束）
const onVideoSeeked = () => {
    console.log(' 拖动进度条结束')
    drawDetectionBoxes()
}

// 使用 requestAnimationFrame 实现流畅绘制
const drawLoop = () => {
    if (!isPlaying) return

    drawDetectionBoxes()
    animationFrameId = requestAnimationFrame(drawLoop)
}

// 绘制检测框的核心函数
const drawDetectionBoxes = () => {
    if (!videoRef.value || !videoCanvasRef.value || results.value.length === 0) {
        console.log(' 跳过绘制：', {
            hasVideo: !!videoRef.value,
            hasCanvas: !!videoCanvasRef.value,
            hasResults: results.value.length > 0
        })
        return
    }

    const video = videoRef.value
    const canvas = videoCanvasRef.value
    const ctx = canvas.getContext('2d')

    // 设置 Canvas 物理尺寸与视频显示尺寸一致
    const rect = video.getBoundingClientRect()
    if (canvas.width !== rect.width || canvas.height !== rect.height) {
        canvas.width = rect.width
        canvas.height = rect.height
    }

    // 清空画布
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // 计算视频实际显示区域（考虑 object-fit: contain）
    const videoRatio = video.videoWidth / video.videoHeight
    const displayRatio = rect.width / rect.height

    let drawWidth, drawHeight, offsetX, offsetY

    if (videoRatio > displayRatio) {
        // 视频宽度占满，上下有黑边
        drawWidth = rect.width
        drawHeight = rect.width / videoRatio
        offsetX = 0
        offsetY = (rect.height - drawHeight) / 2
    } else {
        // 视频高度占满，左右有黑边
        drawHeight = rect.height
        drawWidth = rect.height * videoRatio
        offsetX = (rect.width - drawWidth) / 2
        offsetY = 0
    }

    // 找到当前时间对应的关键帧
    const currentTime = video.currentTime

    // 查找当前时间前后的两个关键帧（用于插值）
    let prevFrame = null
    let nextFrame = null

    for (let i = 0; i < results.value.length; i++) {
        if (results.value[i].timestamp <= currentTime) {
            prevFrame = results.value[i]
        }
        if (results.value[i].timestamp >= currentTime && !nextFrame) {
            nextFrame = results.value[i]
            break
        }
    }

    // 如果只有一个关键帧，使用它
    if (!prevFrame && nextFrame) prevFrame = nextFrame
    if (prevFrame && !nextFrame) nextFrame = prevFrame

    // 如果都没有，返回
    if (!prevFrame && !nextFrame) {
        console.log('⚪ 未找到关键帧')
        return
    }

    // 计算插值比例（0-1之间）
    let t = 0
    if (prevFrame !== nextFrame) {
        t = (currentTime - prevFrame.timestamp) / (nextFrame.timestamp - prevFrame.timestamp)
        t = Math.max(0, Math.min(1, t)) // 限制在 0-1 范围内
    }

    // ✅ 关闭调试日志
    // console.log(`🔍 插值计算 - 时间: ${currentTime.toFixed(2)}s, prev: ${prevFrame.timestamp.toFixed(1)}s, next: ${nextFrame.timestamp.toFixed(1)}s, t: ${t.toFixed(3)}`)

    // 插值人脸数据
    const interpolatedFaces = interpolateFaces(prevFrame, nextFrame, t)

    // 如果找到人脸，绘制检测框
    if (interpolatedFaces && interpolatedFaces.length > 0) {
        // ✅ 关闭调试日志
        // console.log(`🎨 绘制 ${interpolatedFaces.length} 个人脸检测框`)

        // 计算缩放比例：原始视频尺寸 -> Canvas 显示尺寸
        const scale = drawWidth / video.videoWidth

        interpolatedFaces.forEach((face, faceIndex) => {
            const color = getEmotionColor(face.emotion)
            const [x, y, w, h] = face.bbox

            // 转换坐标到 Canvas 坐标系
            const scaledX = x * scale + offsetX
            const scaledY = y * scale + offsetY
            const scaledW = w * scale
            const scaledH = h * scale

            // 绘制检测框和标签
            const totalFaces = interpolatedFaces.length
            drawCornerBox(ctx, [scaledX, scaledY, scaledW, scaledH], color, 4)
            drawEmotionLabel(ctx, [scaledX, scaledY, scaledW, scaledH], face.emotion, face.confidence, themeStore.currentTheme, faceIndex + 1, totalFaces)
        })
    } else {
        console.log(`⚪ 未找到人脸 - 当前时间: ${currentTime.toFixed(1)}s`)
    }
}

// 插值人脸数据（在两个关键帧之间平滑过渡）
function interpolateFaces(prevFrame, nextFrame, t) {
    if (!prevFrame || !nextFrame) return null

    // 如果两个帧相同，直接返回
    if (prevFrame === nextFrame) return prevFrame.faces || []

    const prevFaces = prevFrame.faces || []
    const nextFaces = nextFrame.faces || []

    // 简单策略：使用前一帧的人脸数量，对 bbox 进行线性插值
    // 如果人脸数量不同，使用较少的那个
    const faceCount = Math.min(prevFaces.length, nextFaces.length)
    if (faceCount === 0) return []

    const interpolated = []

    for (let i = 0; i < faceCount; i++) {
        const prevFace = prevFaces[i]
        const nextFace = nextFaces[i]

        // 对 bbox 进行线性插值
        const interpolatedBbox = [
            prevFace.bbox[0] + (nextFace.bbox[0] - prevFace.bbox[0]) * t, // x
            prevFace.bbox[1] + (nextFace.bbox[1] - prevFace.bbox[1]) * t, // y
            prevFace.bbox[2] + (nextFace.bbox[2] - prevFace.bbox[2]) * t, // w
            prevFace.bbox[3] + (nextFace.bbox[3] - prevFace.bbox[3]) * t  // h
        ]

        // 对置信度进行线性插值
        const interpolatedConfidence = prevFace.confidence + (nextFace.confidence - prevFace.confidence) * t

        // 情绪使用前帧的（因为情绪是分类，不适合插值）
        // 或者可以选择更接近的情绪
        interpolated.push({
            bbox: interpolatedBbox,
            emotion: prevFace.emotion, // 暂时使用前帧的情绪
            confidence: interpolatedConfidence,
            emotions: prevFace.emotions // 暂时使用前帧的情绪分布
        })
    }

    return interpolated
}

// TODO: 视频检测功能待后端实现完整逐帧分析
// 当前为演示原型阶段，使用真实API请求 + 模拟处理进度
const startDetection = async () => {
    if (!selectedFile.value) { ElMessage.warning('请先选择视频'); return }
    processing.value = true; progress.value = 0
    statusText.value = '正在上传...'; results.value = []

    try {
        const formData = new FormData()
        formData.append('file', selectedFile.value)
        const res = await fetch(API.detectVideo, { method: 'POST', body: formData })
        if (!res.ok) throw new Error('视频检测失败')

        const data = await res.json()
        console.log('后端返回数据:', data) // 调试信息

        if (data.status === 'success' && data.video_info) {
            // 更新视频信息
            totalFrames.value = data.video_info.total_frames || 0

            // 模拟处理进度动画
            const totalSteps = 20
            for (let step = 1; step <= totalSteps; step++) {
                await new Promise(r => setTimeout(r, 100))
                progress.value = Math.round((step / totalSteps) * 100)
                statusText.value = `正在分析视频帧... ${progress.value}%`
            }

            // 使用真实的检测结果
            results.value = data.key_frames || []

            // 立即绘制一次检测框（如果视频正在播放）
            await nextTick()
            drawDetectionBoxes()

            statusText.value = '分析完成'
            logFeatureUsage('视频检测', { frames: totalFrames.value })
            ElMessage.success(`✅ 视频分析完成！提取 ${results.value.length} 个关键帧`)

            // 保存到历史记录
            await saveToHistory(data.key_frames || [])
        } else {
            throw new Error(data.detail || data.message || '视频检测失败')
        }
    } catch (error) {
        console.error('视频检测错误:', error)
        ElMessage.error('检测失败: ' + error.message)
    } finally { processing.value = false }
}

const reset = () => {
    videoUrl.value = null; selectedFile.value = null; results.value = []
    progress.value = 0; if (videoRef.value) videoRef.value.pause()
}

const exportJSON = () => {
    const blob = new Blob([JSON.stringify(results.value, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a'); link.href = url; link.download = `video_${Date.now()}.json`; link.click()
    URL.revokeObjectURL(url); ElMessage.success('✅ 已导出JSON')
}

const exportCSV = () => {
    let csv = 'Frame,Has_Face,Emotion,Confidence\n'
    results.value.forEach(r => {
        const hasFace = r.faces && r.faces.length > 0
        const face = hasFace ? r.faces[0] : null
        csv += `${r.frame},${hasFace},${face ? face.emotion : 'N/A'},${face ? (face.confidence * 100).toFixed(1) : 0}\n`
    })
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a'); link.href = url; link.download = `video_${Date.now()}.csv`; link.click()
    URL.revokeObjectURL(url); ElMessage.success('✅ 已导出CSV')
}

// 保存视频检测到历史记录
const saveToHistory = async (keyFrames) => {
    try {
        // 计算主导情绪和平均置信度
        const facesWithEmotion = keyFrames.filter(kf => kf.faces && kf.faces.length > 0)
        const emotions = facesWithEmotion.map(kf => kf.faces[0].emotion)
        const confidences = facesWithEmotion.map(kf => kf.faces[0].confidence)

        // 统计主导情绪
        const emotionCount = {}
        emotions.forEach(e => { emotionCount[e] = (emotionCount[e] || 0) + 1 })
        const dominantEmotion = Object.keys(emotionCount).reduce((a, b) => emotionCount[a] > emotionCount[b] ? a : b, 'neutral')

        // 计算平均置信度
        const avgConfidence = confidences.length > 0
            ? confidences.reduce((sum, c) => sum + c, 0) / confidences.length
            : 0

        // 提取所有检测到的人脸数据（用于历史记录显示）
        const detectedFaces = facesWithEmotion.map(kf => kf.faces[0]).slice(0, 10)

        // 生成缩略图（使用第一个有关键帧生成简单的缩略图
        let thumbnail = null
        if (keyFrames.length > 0) {
            // 使用canvas生成简单的缩略图
            const canvas = document.createElement('canvas')
            canvas.width = 200
            canvas.height = 150
            const ctx = canvas.getContext('2d')

            // 绘制渐变背景
            const gradient = ctx.createLinearGradient(0, 0, 200, 150)
            gradient.addColorStop(0, '#1a1a2e')
            gradient.addColorStop(1, '#16213e')
            ctx.fillStyle = gradient
            ctx.fillRect(0, 0, 200, 150)

            // 绘制情绪图标
            ctx.font = '48px Arial'
            ctx.textAlign = 'center'
            ctx.textBaseline = 'middle'
            ctx.fillStyle = '#ffffff'
            ctx.fillText(getEmotionEmoji(dominantEmotion), 100, 75)

            thumbnail = canvas.toDataURL('image/jpeg', 0.8)
        }

        await fetch(API.historySave, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                detection_type: 'video',
                results: keyFrames,
                source: '视频检测',
                image_path: '',
                image_type: 'video',
                thumbnail: thumbnail,
                dominant_emotion: dominantEmotion,
                confidence: avgConfidence,
                detected_faces: detectedFaces
            })
        })
        console.log('✅ 视频历史记录已保存')
    } catch (error) {
        console.error('保存视频历史记录失败:', error)
        // 不显示错误提示，避免影响用户体验
    }
}
</script>

<style scoped>
.video-detector {
    height: 100%;
    overflow: hidden;
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

.left-panel .el-card {
    height: 100%;
    display: flex;
    flex-direction: column;
}

.left-panel .el-card__body {
    flex: 1;
    overflow-y: auto;
}

.right-panel {
    height: 100%;
    overflow-y: auto;
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

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 300px;
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
}

.card-header {
    display: flex;
    align-items: center;
    gap: 10px;
}

.card-header h3 {
    font-size: 17px;
    font-weight: 700;
    margin: 0;
}

.card-icon {
    font-size: 22px;
}

.badge {
    font-size: 10px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 20px;
    background: linear-gradient(135deg, #F99E1A, #FF6B35);
    color: white;
    margin-left: 8px;
    vertical-align: middle;
}

.upload-area {
    margin-bottom: 12px;
    min-height: 700px;
    height: 700px;
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
    min-height: 700px;
    height: 100%;
}

:deep(.el-upload-dragger) {
    padding: 40px 16px;
}

.glass-card-inner {
    background: color-mix(in srgb, var(--card-bg) 55%, transparent);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 14px;
    transition: all 0.2s ease;
}

/* ✅ 视频检测卡片内边距优化 */
.video-section :deep(.el-card__body) {
    padding: 10px !important;
}

.glass-card-inner:hover {
    border-color: color-mix(in srgb, var(--border) 60%, var(--primary));
}

.video-section {
    margin-top: 12px;
    animation: fadeIn 0.4s ease;
}

.video-container {
    padding: 4px;
    margin-bottom: 12px;
}

.video-wrapper {
    position: relative;
    width: 100%;
}

.video-container video {
    width: 100%;
    max-height: calc(100vh - 280px);
    min-height: 400px;
    border-radius: 10px;
    background: #000;
    display: block;
    position: relative;
    z-index: 1;
}

.video-canvas-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    border-radius: 10px;
    z-index: 2;
}

.control-panel {
    display: flex;
    gap: 8px;
    justify-content: center;
    /* margin-bottom: 12px; */
}

.floating-progress {
    position: fixed;
    bottom: 20%;
    left: 50%;
    transform: translateX(-50%);
    z-index: 9999;
    animation: fadeInUp 0.3s ease;
}

.floating-progress-card {
    background: color-mix(in srgb, var(--card-bg) 75%, transparent);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid color-mix(in srgb, var(--border) 80%, var(--primary));
    border-radius: 16px;
    padding: 20px 32px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4),
        0 0 0 1px rgba(113, 57, 255, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
    min-width: 480px;
    max-width: 600px;
}

.floating-progress-card :deep(.el-progress) {
    margin-bottom: 12px;
}

.floating-progress-card :deep(.el-progress-bar__outer) {
    background: color-mix(in srgb, var(--card-bg) 60%, transparent);
    border-radius: 6px;
    overflow: hidden;
}

.floating-progress-card :deep(.el-progress-bar__inner) {
    border-radius: 6px;
    box-shadow: 0 0 12px currentColor;
    transition: width 0.3s ease;
}

.progress-status {
    margin: 0;
    color: var(--text);
    font-size: 14px;
    font-weight: 600;
    text-align: center;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.results-section {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.stats-cards {
    margin-bottom: 12px;
}

.stat-card {
    text-align: center;
    border-radius: var(--radius-sm);
    border: none !important;
    background: color-mix(in srgb, var(--card-bg) 50%, transparent) !important;
}

.stat-value {
    font-size: 22px;
    font-weight: 800;
    margin-bottom: 4px;
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    display: flex;
    align-items: center;
    justify-content: center;
}

.dominant-emoji-large {
    font-size: 36px;
    line-height: 1;
    display: inline-block;
    /* ✅ 修复: 重置渐变色文本，确保 emoji 正常显示 */
    -webkit-text-fill-color: initial !important;
    background: none !important;
    -webkit-background-clip: initial !important;
    background-clip: initial !important;
    text-shadow: 0 2px 8px rgba(113, 57, 255, 0.3);
}

.stat-label {
    font-size: 12px;
    color: var(--text-secondary);
}

.stat-desc {
    font-size: 13px;
    font-weight: 600;
    margin-top: 4px;
    color: var(--text);
}

.emotion-distribution {
    margin-bottom: 12px;
    max-height: 200px;
    overflow-y: auto;
}

.emotion-distribution h5 {
    font-size: 14px;
    margin-bottom: 12px;
    color: var(--text);
    font-weight: 700;
}

.distribution-item {
    display: grid;
    grid-template-columns: 20px 65px 1fr 40px;
    align-items: center;
    gap: 6px;
    margin-bottom: 6px;
}

.dist-emoji {
    font-size: 17px;
    line-height: 1;
    text-align: center;
}

.distribution-item .name {
    font-weight: 500;
    font-size: 12px;
    color: var(--text);
}

.distribution-item .count {
    font-weight: 700;
    text-align: right;
    font-size: 12px;
    color: var(--text-secondary);
}

.empty-distribution {
    text-align: center;
    padding: 20px;
    color: var(--text-secondary);
    font-size: 14px;
    opacity: 0.6;
}

.key-frames-section {
    margin-bottom: 12px;
    max-height: calc(100vh - 500px);
    overflow-y: auto;
}

.key-frames-section h5 {
    font-size: 14px;
    margin-bottom: 12px;
    color: var(--text);
    font-weight: 700;
}

.key-frames-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
    gap: 10px;
}

.key-frame-item {
    background: color-mix(in srgb, var(--card-bg) 40%, transparent);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 8px;
    text-align: center;
    transition: all 0.2s ease;
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.key-frame-item:hover {
    border-color: color-mix(in srgb, var(--border) 60%, var(--primary));
    transform: translateY(-2px);
}

.frame-number {
    font-size: 11px;
    color: var(--text-secondary);
    font-weight: 600;
    line-height: 1.2;
}

.frame-emotion {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
}

.frame-emoji {
    font-size: 20px;
    line-height: 1;
}

.frame-time {
    font-size: 10px;
    color: var(--text-secondary);
    font-weight: 600;
    line-height: 1.2;
}

.frame-count {
    font-size: 9px;
    color: var(--text);
    font-weight: 700;
    background: color-mix(in srgb, var(--primary) 20%, transparent);
    padding: 2px 6px;
    border-radius: 10px;
    display: inline-block;
}

.export-buttons {
    display: flex;
    gap: 8px;
    justify-content: center;
    margin-top: 12px;
    flex-shrink: 0;
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
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
