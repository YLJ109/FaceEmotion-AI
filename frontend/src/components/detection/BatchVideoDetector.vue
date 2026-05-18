<template>
    <div class="batch-video-detector">
        <div class="detector-layout">
            <!-- 左侧：视频上传和播放 -->
            <div class="left-panel">
                <el-card class="glass-card">
                    <template #header>
                        <div class="card-header">
                            <span class="card-icon">🎥</span>
                            <h3>批量视频检测 <span class="badge">并发3个</span></h3>
                        </div>
                    </template>

                    <!-- 上传区域（未选择文件时显示） -->
                    <el-upload v-if="fileList.length === 0 && !selectedVideoUrl" class="upload-area" drag multiple
                        :auto-upload="false" :on-change="handleFilesChange" :file-list="fileList" accept="video/*">
                        <el-icon class="el-icon--upload" :size="48">
                            <UploadFilled />
                        </el-icon>
                        <div class="el-upload__text">
                            拖拽多个视频到此处或 <em>点击上传</em>
                        </div>
                        <template #tip>
                            <div class="el-upload__tip">支持 MP4、AVI、MOV 格式</div>
                        </template>
                    </el-upload>

                    <!-- 视频选择区域（已选择文件但未播放时） -->
                    <div v-if="fileList.length > 0 && !selectedVideoUrl" class="video-selection-section">
                        <div class="selection-header">
                            <span class="file-count">已选择 {{ fileList.length }} 个视频</span>
                            <button class="clear-btn" @click="clearAll">
                                <el-icon>
                                    <Delete />
                                </el-icon>
                                清空
                            </button>
                        </div>
                        <div class="video-list">
                            <div v-for="(file, index) in fileList" :key="index" class="video-list-item"
                                @click="previewVideo(file)">
                                <div class="video-icon">🎬</div>
                                <div class="video-info">
                                    <div class="video-name">{{ file.name }}</div>
                                    <div class="video-hint">点击预览</div>
                                </div>
                            </div>
                        </div>
                        <div class="action-bar">
                            <el-button type="primary" @click="startBatchDetection" :loading="detecting" round
                                size="large">
                                <el-icon style="margin-right:6px">
                                    <VideoPlay />
                                </el-icon>
                                {{ results.length > 0 ? '重新检测' : '开始检测' }} ({{ fileList.length }} 个)
                            </el-button>
                            <el-button type="primary" @click="clearAll" round size="large">清空列表</el-button>
                        </div>
                    </div>

                    <!-- 视频播放区域 -->
                    <div v-if="selectedVideoUrl" class="video-section">
                        <div class="video-container glass-card-inner">
                            <div class="video-wrapper">
                                <video ref="videoRef" :src="selectedVideoUrl" controls @loadedmetadata="onVideoLoaded"
                                    @timeupdate="onVideoTimeUpdate" @play="onVideoPlay" @pause="onVideoPause"
                                    @seeking="onVideoSeeking" @seeked="onVideoSeeked"></video>
                                <canvas ref="videoCanvasRef" class="video-canvas-overlay"></canvas>
                            </div>
                        </div>
                        <div class="control-panel">
                            <el-button type="primary" @click="startBatchDetection" :loading="detecting" round
                                size="large" :disabled="detecting">
                                <el-icon style="margin-right:6px">
                                    <VideoPlay />
                                </el-icon>
                                {{ detecting ? '检测中...' : '开始检测' }}
                            </el-button>
                            <el-button type="primary" @click="backToSelection" round size="large">返回列表</el-button>
                        </div>
                        <div v-if="detecting" class="floating-progress">
                            <div class="floating-progress-card">
                                <el-progress :percentage="progress" :status="progress === 100 ? 'success' : undefined"
                                    :stroke-width="12" />
                                <p class="progress-status">正在处理: {{ currentIndex + 1 }} / {{ fileList.length }}</p>
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
                            <span class="card-icon"></span>
                            <h3>检测结果</h3>
                        </div>
                    </template>

                    <!-- 空状态 -->
                    <div v-if="results.length === 0" class="empty-state">
                        <div class="empty-icon"></div>
                        <p>上传并检测视频后<br />将在此处显示统计结果</p>
                    </div>

                    <!-- 检测结果内容 -->
                    <div v-else class="results-section">
                        <!-- 视频详情列表 -->
                        <div class="video-results-list">
                            <h5>视频详情 ({{ results.length }}个)</h5>
                            <div class="video-list-container">
                                <div v-for="(result, index) in results" :key="index" class="video-result-item"
                                    :class="{ 'active': selectedVideoFile?.name === result.filename }"
                                    :style="{ borderLeftColor: result.status === 'success' ? getEmotionColor(result.dominantEmotion) : 'var(--danger)' }"
                                    @click="previewResultVideo(result)">
                                    <div class="video-result-header">
                                        <span class="video-result-index">#{{ index + 1 }}</span>
                                        <span class="video-result-filename" :title="result.filename">{{ result.filename
                                            }}</span>
                                        <span :class="['result-status', result.status]">
                                            {{ result.status === 'success' ? '✓' : '✗' }}
                                        </span>
                                    </div>
                                    <div v-if="result.status === 'success'" class="video-result-details">
                                        <div class="video-result-emotion">
                                            <span class="result-emoji">{{ getEmotionEmoji(result.dominantEmotion)
                                                }}</span>
                                            <span class="result-emotion-name">{{ getEmotionName(result.dominantEmotion)
                                                }}</span>
                                            <span class="result-confidence">{{ (result.avgConfidence * 100).toFixed(1)
                                                }}%</span>
                                        </div>
                                        <div class="video-result-metrics">
                                            <span class="metric">⏱️ {{ result.video_info.duration.toFixed(1) }}s</span>
                                            <span class="metric">️ {{ result.video_info.fps.toFixed(1) }}fps</span>
                                            <span class="metric">📊 {{ result.video_info.key_frames_count }}帧</span>
                                        </div>
                                        <!-- 展开/收起按钮 -->
                                        <button class="expand-btn" @click.stop="toggleFrameDetails(index)">
                                            <el-icon>
                                                <ArrowRight v-if="!expandedFrames.includes(index)" />
                                                <ArrowDown v-else />
                                            </el-icon>
                                            <span>{{ expandedFrames.includes(index) ? '收起帧数据' : '查看帧数据' }}</span>
                                        </button>
                                        <!-- 帧数据详情面板 -->
                                        <div v-if="expandedFrames.includes(index)" class="frame-details-panel">
                                            <div class="frame-details-header">
                                                <span class="frame-count">共 {{ result.key_frames.length }} 个关键帧</span>
                                            </div>
                                            <div class="frame-list">
                                                <div v-for="(frame, frameIndex) in result.key_frames" :key="frameIndex"
                                                    class="frame-item">
                                                    <div class="frame-time">
                                                        <span class="time-label">⏰</span>
                                                        <span class="time-value">{{ formatTime(frame.timestamp)
                                                            }}</span>
                                                    </div>
                                                    <div v-if="frame.faces && frame.faces.length > 0"
                                                        class="frame-faces">
                                                        <div v-for="(face, faceIdx) in frame.faces" :key="faceIdx"
                                                            class="face-data">
                                                            <span class="face-emoji">{{ getEmotionEmoji(face.emotion)
                                                                }}</span>
                                                            <span class="face-emotion">{{ getEmotionName(face.emotion)
                                                                }}</span>
                                                            <span class="face-confidence">{{ (face.confidence *
                                                                100).toFixed(1)
                                                                }}%</span>
                                                        </div>
                                                    </div>
                                                    <div v-else class="no-face">
                                                        <span>未检测到人脸</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div v-else class="video-result-error">
                                        <span>{{ result.error }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </el-card>
            </div>
        </div>

        <!-- 性能监控面板 -->
        <PerformanceMonitor :fps="perfFps" :latency="perfLatency" :skip-rate="perfSkipRate" :gpu-memory="perfGpuMemory"
            :detect-interval="perfDetectInterval" :http-latency="perfHttpLatency" :error-rate="perfErrorRate" />
    </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { UploadFilled, Upload, Delete, VideoPlay, WarningFilled, ArrowRight, ArrowDown } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useThemeStore } from '@/stores/theme'
import { getEmotionName, getEmotionEmoji, getEmotionColor } from '@/constants/emotions'
import { drawCornerBox, drawEmotionLabel } from '@/utils/canvas'
import { detectVideo } from '@/api/modules/detection'
import { saveHistoryRecord } from '@/api/modules/history'
import { logFeatureUsage } from '@/utils/analytics'
import PerformanceMonitor from '@/components/monitor/PerformanceMonitor.vue'
import generativeAudio from '@/utils/generativeAudio'

// 组件名称,用于 keep-alive 缓存
defineOptions({
    name: 'BatchVideoDetector'
})

const themeStore = useThemeStore()
const fileList = ref([])
const detecting = ref(false)
const progress = ref(0)
const currentIndex = ref(0)
const results = ref([])
const BATCH_CONCURRENCY = 3

// 视频预览相关
const selectedVideoUrl = ref(null)
const selectedVideoFile = ref(null)
const videoRef = ref(null)
const videoCanvasRef = ref(null)
let animationFrameId = null
let isPlaying = false
let lastPlayedTimestamp = -1

// 性能监控数据
const perfFps = ref(0)
const perfLatency = ref(0)
const perfSkipRate = ref(0)
const perfGpuMemory = ref(0)
const perfDetectInterval = ref(1)
const perfHttpLatency = ref(0)
const perfErrorRate = ref(0)
const totalProcessingTime = ref(0)

// 帧数据展开状态
const expandedFrames = ref([])

const handleFilesChange = async (file, files) => {
    fileList.value = files
}

// 预览视频（点击文件列表项）
const previewVideo = (file) => {
    // 释放旧的 URL 对象，避免内存泄漏
    if (selectedVideoUrl.value) {
        URL.revokeObjectURL(selectedVideoUrl.value)
    }

    selectedVideoUrl.value = URL.createObjectURL(file.raw)
    selectedVideoFile.value = file.raw
}

// 预览结果视频（点击结果项）
const previewResultVideo = (result) => {
    if (result.status !== 'success') return

    // 释放旧的 URL 对象，避免内存泄漏
    if (selectedVideoUrl.value) {
        URL.revokeObjectURL(selectedVideoUrl.value)
    }

    // 找到对应的文件
    const file = fileList.value.find(f => f.name === result.filename)
    if (file) {
        selectedVideoUrl.value = URL.createObjectURL(file.raw)
        selectedVideoFile.value = file.raw
    }
}

// 返回选择列表
const backToSelection = () => {
    selectedVideoUrl.value = null
    selectedVideoFile.value = null
    if (videoRef.value) {
        videoRef.value.pause()
    }
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId)
        animationFrameId = null
    }
    isPlaying = false
    // ✅ 新增: 返回选择列表时自动停止音乐
    if (generativeAudio.isInitialized && generativeAudio.isPlaying) {
        generativeAudio.stop()
    }
}

const startBatchDetection = async () => {
    if (!fileList.value.length) { ElMessage.warning('请先选择视频'); return }
    detecting.value = true; progress.value = 0; currentIndex.value = 0; results.value = []

    // ✅ 新增: 在用户交互时初始化音频引擎（浏览器策略要求）
    if (!generativeAudio.isInitialized) {
        try {
            await generativeAudio.init()
            
        } catch (error) {
            console.warn('音频引擎初始化失败:', error)
        }
    }

    const startTime = performance.now()

    const total = fileList.value.length
    const queue = fileList.value.map((f, i) => ({ file: f.raw, index: i, name: f.name }))
    let completed = 0
    let errorCount = 0
    let totalLatency = 0
    let successCount = 0

    const processOne = async (item) => {
        try {
            const itemStartTime = performance.now()
            const formData = new FormData()
            formData.append('file', item.file)
            const result = await detectVideo(formData)
            const itemEndTime = performance.now()

            totalLatency += (itemEndTime - itemStartTime)

            if (result.status === 'success') {
                successCount++

                // 计算主导情绪和平均置信度
                let dominantEmotion = 'neutral'
                let totalConfidence = 0
                let faceCount = 0

                result.key_frames.forEach(frame => {
                    if (frame.faces && frame.faces.length > 0) {
                        frame.faces.forEach(face => {
                            totalConfidence += face.confidence
                            faceCount++
                        })
                        // 使用第一帧的情绪作为该视频的主导情绪
                        if (frame.faces[0]) {
                            dominantEmotion = frame.faces[0].emotion
                        }
                    }
                })

                const avgConfidence = faceCount > 0 ? totalConfidence / faceCount : 0

                // 触发音乐参数更新（使用第一个成功的视频）
                if (successCount === 1 && result.key_frames.length > 0 && result.key_frames[0].music_params) {
                    const musicParams = result.key_frames[0].music_params
                    window.dispatchEvent(new CustomEvent('music-params-updated', {
                        detail: musicParams
                    }))

                    // ✅ 修复: 只在用户没有手动关闭音乐时自动播放
                    if (generativeAudio.isInitialized && generativeAudio.isPlaying) {
                        generativeAudio.playMusic(musicParams)
                    }
                }

                return {
                    filename: item.name,
                    status: 'success',
                    video_info: result.video_info,
                    key_frames: result.key_frames,
                    dominantEmotion,
                    avgConfidence
                }
            } else {
                throw new Error('检测失败')
            }
        } catch (e) {
            console.error(`处理 ${item.name} 失败:`, e)
            errorCount++
            return {
                filename: item.name,
                status: 'error',
                error: e.message
            }
        }
    }

    const worker = async () => {
        while (queue.length > 0) {
            const item = queue.shift()
            const r = await processOne(item)
            if (r) results.value.push(r)
            completed++
            currentIndex.value = completed
            progress.value = Math.round((completed / total) * 100)
        }
    }

    const workers = Array(Math.min(BATCH_CONCURRENCY, total)).fill(null).map(() => worker())
    await Promise.all(workers)

    // 计算总体性能指标
    const endTime = performance.now()
    totalProcessingTime.value = endTime - startTime
    perfHttpLatency.value = totalLatency / completed
    perfLatency.value = perfHttpLatency.value
    perfFps.value = completed / (totalProcessingTime.value / 1000)
    perfSkipRate.value = 0
    perfGpuMemory.value = 0
    perfErrorRate.value = (errorCount / total) * 100

    logFeatureUsage('批量视频检测', { total: results.value.length })
    ElMessage.success(`批量视频检测完成！成功 ${successCount} 个，失败 ${errorCount} 个`)
    detecting.value = false

    // 保存到历史记录
    await saveBatchToHistory()
}

// 视频事件处理函数
const onVideoLoaded = () => {
    
}

// 视频时间更新时绘制检测框并切换音乐
const onVideoTimeUpdate = () => {
    if (!videoRef.value || !videoCanvasRef.value || !selectedVideoFile.value) return

    // 查找当前视频的检测结果
    const currentResult = results.value.find(r => r.filename === selectedVideoFile.value.name)
    if (!currentResult || currentResult.status !== 'success' || !currentResult.key_frames) return

    drawDetectionBoxes(currentResult.key_frames)

    // 根据当前视频时间切换情绪和音乐
    const currentTime = videoRef.value.currentTime

    // 找到当前时间对应的关键帧（允许±0.5秒误差）
    const currentFrame = currentResult.key_frames.find(frame => {
        return Math.abs(currentTime - frame.timestamp) < 0.5
    })

    if (currentFrame && currentFrame.faces?.length > 0) {
        // 检查是否切换到新的关键帧（避免频繁触发）
        if (currentFrame.timestamp !== lastPlayedTimestamp) {
            lastPlayedTimestamp = currentFrame.timestamp

            // 传递情绪数据到音乐引擎
            if (currentFrame.music_params) {
                // 触发全局事件,通知App.vue更新音乐面板状态
                window.dispatchEvent(new CustomEvent('music-params-updated', {
                    detail: currentFrame.music_params
                }))

                // ✅ 修复: 只在用户没有手动关闭音乐时自动播放
                if (generativeAudio.isInitialized && generativeAudio.isPlaying) {
                    generativeAudio.playMusic(currentFrame.music_params)
                }
            }
        }
    }
}

// 视频开始播放
const onVideoPlay = () => {
    
    isPlaying = true
    drawLoop()
}

// 视频暂停
const onVideoPause = () => {
    
    isPlaying = false
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId)
        animationFrameId = null
    }
    // ✅ 新增: 视频暂停时自动停止音乐
    if (generativeAudio.isInitialized && generativeAudio.isPlaying) {
        generativeAudio.stop()
    }
}

// 用户拖动进度条（开始）
const onVideoSeeking = () => {
    
    const currentResult = results.value.find(r => r.filename === selectedVideoFile.value.name)
    if (currentResult && currentResult.status === 'success') {
        drawDetectionBoxes(currentResult.key_frames)
    }
}

// 用户拖动进度条（结束）
const onVideoSeeked = () => {
    
    const currentResult = results.value.find(r => r.filename === selectedVideoFile.value.name)
    if (currentResult && currentResult.status === 'success') {
        drawDetectionBoxes(currentResult.key_frames)
    }
}

// 使用 requestAnimationFrame 实现流畅绘制
const drawLoop = () => {
    if (!isPlaying) return

    const currentResult = results.value.find(r => r.filename === selectedVideoFile.value.name)
    if (currentResult && currentResult.status === 'success') {
        drawDetectionBoxes(currentResult.key_frames)
    }
    animationFrameId = requestAnimationFrame(drawLoop)
}

// 绘制检测框的核心函数
const drawDetectionBoxes = (keyFrames) => {
    if (!videoRef.value || !videoCanvasRef.value || !keyFrames || keyFrames.length === 0) {
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

    for (let i = 0; i < keyFrames.length; i++) {
        if (keyFrames[i].timestamp <= currentTime) {
            prevFrame = keyFrames[i]
        }
        if (keyFrames[i].timestamp >= currentTime && !nextFrame) {
            nextFrame = keyFrames[i]
            break
        }
    }

    // 如果只有一个关键帧，使用它
    if (!prevFrame && nextFrame) prevFrame = nextFrame
    if (prevFrame && !nextFrame) nextFrame = prevFrame

    // 如果都没有，返回
    if (!prevFrame && !nextFrame) {
        return
    }

    // 计算插值比例（0-1之间）
    let t = 0
    if (prevFrame !== nextFrame) {
        t = (currentTime - prevFrame.timestamp) / (nextFrame.timestamp - prevFrame.timestamp)
        t = Math.max(0, Math.min(1, t)) // 限制在 0-1 范围内
    }

    // 插值人脸数据
    const interpolatedFaces = interpolateFaces(prevFrame, nextFrame, t)

    // 如果找到人脸，绘制检测框
    if (interpolatedFaces && interpolatedFaces.length > 0) {
        // 计算缩放比例：原始视频尺寸 -> Canvas 显示尺寸
        const scale = drawWidth / video.videoWidth

        const existingLabels = []
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
            const labelRect = drawEmotionLabel(ctx, [scaledX, scaledY, scaledW, scaledH], face.emotion, face.confidence, themeStore.currentTheme, faceIndex + 1, totalFaces, existingLabels)
            if (labelRect) existingLabels.push(labelRect)
        })
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
        interpolated.push({
            bbox: interpolatedBbox,
            emotion: prevFace.emotion,
            confidence: interpolatedConfidence,
            emotions: prevFace.emotions
        })
    }

    return interpolated
}

// 从视频中截取帧并裁剪人脸的辅助函数（批量视频使用）
const generateVideoThumbnail = async (result) => {
    return new Promise((resolve) => {
        // 找到对应的文件
        const file = fileList.value.find(f => f.name === result.filename)
        if (!file) {
            console.warn(`找不到视频文件: ${result.filename}`)
            resolve(generateFallbackThumbnail(result.dominantEmotion))
            return
        }

        // 创建临时URL
        const videoUrl = URL.createObjectURL(file.raw)

        // 取第一个关键帧的第一张人脸
        const firstFrame = result.key_frames?.[0]
        if (!firstFrame || !firstFrame.faces?.length) {
            URL.revokeObjectURL(videoUrl)
            resolve(generateFallbackThumbnail(result.dominantEmotion))
            return
        }

        const face = firstFrame.faces[0]
        

        // 创建一个临时video元素
        const tempVideo = document.createElement('video')
        tempVideo.src = videoUrl
        tempVideo.muted = true
        tempVideo.preload = 'auto'

        // 先等待元数据加载完成
        tempVideo.onloadedmetadata = () => {
            
            tempVideo.currentTime = face.videoTime || 0
        }

        tempVideo.onseeked = () => {
            
            try {
                // 创建canvas并绘制视频帧
                const canvas = document.createElement('canvas')
                const ctx = canvas.getContext('2d')

                canvas.width = tempVideo.videoWidth
                canvas.height = tempVideo.videoHeight

                ctx.drawImage(tempVideo, 0, 0)

                // 获取人脸bbox坐标
                const [x, y, w, h] = face.bbox

                // 裁剪人脸区域(添加20%的边距)
                const margin = 0.2
                const cropX = Math.max(0, x - w * margin)
                const cropY = Math.max(0, y - h * margin)
                const cropW = w * (1 + 2 * margin)
                const cropH = h * (1 + 2 * margin)

                // 创建裁剪后的canvas
                const cropCanvas = document.createElement('canvas')
                cropCanvas.width = cropW
                cropCanvas.height = cropH
                const cropCtx = cropCanvas.getContext('2d')

                cropCtx.drawImage(canvas, cropX, cropY, cropW, cropH, 0, 0, cropW, cropH)

                const thumbnail = cropCanvas.toDataURL('image/jpeg', 0.8)
                

                URL.revokeObjectURL(videoUrl)
                tempVideo.remove()
                resolve(thumbnail)
            } catch (error) {
                console.error(' 裁剪人脸失败:', error)
                URL.revokeObjectURL(videoUrl)
                tempVideo.remove()
                resolve(generateFallbackThumbnail(result.dominantEmotion))
            }
        }

        tempVideo.onerror = (e) => {
            console.error(' 加载视频帧失败:', e)
            URL.revokeObjectURL(videoUrl)
            resolve(generateFallbackThumbnail(result.dominantEmotion))
        }

        // 添加超时保护(5秒)
        setTimeout(() => {
            
            URL.revokeObjectURL(videoUrl)
            tempVideo.remove()
            resolve(generateFallbackThumbnail(result.dominantEmotion))
        }, 5000)
    })
}

// 生成降级缩略图(渐变背景+emoji)
const generateFallbackThumbnail = (emotion) => {
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
    ctx.fillText(getEmotionEmoji(emotion), 100, 75)

    return canvas.toDataURL('image/jpeg', 0.8)
}

// 批量保存到历史记录
const saveBatchToHistory = async () => {
    try {
        let successCount = 0
        let failCount = 0

        for (let i = 0; i < results.value.length; i++) {
            const result = results.value[i]

            if (result.status !== 'success') {
                failCount++
                continue
            }

            try {
                // 生成视频缩略图（从第一帧提取）
                let thumbnail = ''
                try {
                    thumbnail = await generateVideoThumbnail(result)
                } catch (thumbError) {
                    console.warn(`生成第 ${i + 1} 个视频缩略图失败:`, thumbError)
                    // 降级方案：使用情绪图标背景
                    thumbnail = generateFallbackThumbnail(result.dominantEmotion)
                }

                // 收集所有关键帧中的人脸数据
                const allDetectedFaces = []
                result.key_frames?.forEach(frame => {
                    if (frame.faces && frame.faces.length > 0) {
                        frame.faces.forEach(face => {
                            allDetectedFaces.push({
                                ...face,
                                timestamp: frame.timestamp,
                                frame_index: frame.frame_index
                            })
                        })
                    }
                })

                // ✅ 新增: 过滤空检测结果
                if (allDetectedFaces.length === 0) {
                    console.warn(`⚠️ 跳过第 ${i + 1} 个视频：未检测到人脸`)
                    failCount++
                    continue
                }

                await saveHistoryRecord({
                    detection_type: 'batch_video',
                    results: result.key_frames || [],
                    source: `批量视频检测 (${i + 1}/${results.value.length})`,
                    video_path: '',
                    video_type: 'batch_video',
                    thumbnail: thumbnail,
                    dominant_emotion: result.dominantEmotion,
                    confidence: result.avgConfidence,
                    detected_faces: allDetectedFaces
                })

                successCount++
            } catch (err) {
                console.error(` 第 ${i + 1} 个视频保存异常:`, err)
                failCount++
            }
        }

        

        if (failCount > 0) {
            ElMessage.warning(`部分记录保存失败 (${failCount}/${results.value.length})`)
        }
    } catch (error) {
        console.error('保存批量视频历史记录失败:', error)
        ElMessage.error('批量视频历史记录保存失败')
    }
}

const clearAll = () => {
    fileList.value = []; results.value = []; progress.value = 0; currentIndex.value = 0
    expandedFrames.value = []
    backToSelection()
}

// 切换帧数据展开/收起状态
const toggleFrameDetails = (index) => {
    const idx = expandedFrames.value.indexOf(index)
    if (idx > -1) {
        // 已展开，则收起
        expandedFrames.value.splice(idx, 1)
    } else {
        // 未展开，则展开
        expandedFrames.value.push(index)
    }
}

// 格式化时间为 mm:ss 格式
const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}
</script>

<style scoped>
.batch-video-detector {
    height: 100%;
    overflow: hidden;
}

.detector-layout {
    display: grid;
    grid-template-columns: 1fr 350px;
    gap: 12px;
    height: 100%;
    overflow: hidden;
}

.left-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
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
    overflow-x: hidden;
}

.left-panel .el-card__body::-webkit-scrollbar {
    width: 6px;
}

.left-panel .el-card__body::-webkit-scrollbar-thumb {
    background: rgba(146, 78, 255, 0.3);
    border-radius: 3px;
}

.left-panel .el-card__body::-webkit-scrollbar-thumb:hover {
    background: rgba(146, 78, 255, 0.5);
}

.right-panel {
    height: 100%;
    overflow: hidden;
}

.right-panel .el-card {
    height: 100%;
    display: flex;
    flex-direction: column;
}

.right-panel .el-card__body {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
}

.right-panel .el-card__body::-webkit-scrollbar {
    width: 6px;
}

.right-panel .el-card__body::-webkit-scrollbar-thumb {
    background: rgba(146, 78, 255, 0.3);
    border-radius: 3px;
}

.right-panel .el-card__body::-webkit-scrollbar-thumb:hover {
    background: rgba(146, 78, 255, 0.5);
}

.result-card {
    height: 100%;
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

.badge {
    font-size: 10px;
    padding: 2px 8px;
    border-radius: 20px;
    background: var(--gradient);
    color: var(--text);
    margin-left: 8px;
    vertical-align: middle;
}

.upload-area {
    margin-bottom: 12px;
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
    min-height: 500px;
    height: 100%;
}

:deep(.el-upload-dragger) {
    padding: 40px 16px;
}

/* 视频选择区域 */
.video-selection-section {
    margin-top: 12px;
    animation: fadeIn 0.3s ease;
}

.selection-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding: 8px 12px;
    background: color-mix(in srgb, var(--primary) 10%, transparent);
    border-radius: 8px;
}

.file-count {
    font-size: 13px;
    color: var(--text);
}

.clear-btn {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 12px;
    font-size: 12px;
    color: var(--text-secondary);
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.clear-btn:hover {
    color: var(--primary);
    background: color-mix(in srgb, var(--primary) 10%, transparent);
    border-color: color-mix(in srgb, var(--primary) 30%, transparent);
}

.clear-btn .el-icon {
    font-size: 14px;
}

.video-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-height: calc(100vh - 350px);
    overflow-y: auto;
    padding: 4px;
    margin-bottom: 12px;
}

.video-list::-webkit-scrollbar {
    width: 6px;
}

.video-list::-webkit-scrollbar-thumb {
    background: rgba(146, 78, 255, 0.3);
    border-radius: 3px;
}

.video-list::-webkit-scrollbar-thumb:hover {
    background: rgba(146, 78, 255, 0.5);
}

.video-list-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: color-mix(in srgb, var(--card-bg) 60%, transparent);
    border: 1px solid var(--border);
    border-radius: 8px;
    transition: all 0.2s ease;
    cursor: pointer;
}

.video-list-item:hover {
    border-color: color-mix(in srgb, var(--border) 60%, var(--primary));
    transform: translateX(4px);
    background: color-mix(in srgb, var(--card-bg) 80%, transparent);
}

.video-icon {
    font-size: 32px;
    flex-shrink: 0;
}

.video-info {
    flex: 1;
    min-width: 0;
}

.video-name {
    font-size: 13px;
    color: var(--text);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 4px;
}

.video-hint {
    font-size: 11px;
    color: var(--text-secondary);
}

.glass-card-inner {
    background: color-mix(in srgb, var(--card-bg) 55%, transparent);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 14px;
    transition: all 0.2s ease;
}

.glass-card-inner:hover {
    border-color: color-mix(in srgb, var(--border) 60%, var(--primary));
}

.action-bar {
    display: flex;
    gap: 8px;
    justify-content: center;
    margin: 12px 0;
}

/* 视频播放区域 */
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

.video-section video {
    width: 100%;
    max-height: calc(100vh - 350px);
    min-height: 300px;
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
    margin-bottom: 12px;
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
        inset 0 1px 0 color-mix(in srgb, var(--card-bg) 90%, transparent);
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
    text-align: center;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

/* 结果区域 */
.results-section {
    display: flex;
    flex-direction: column;
    gap: 12px;
    height: 100%;
    max-height: calc(100vh - 180px);
    overflow-y: auto;
    padding-right: 4px;
}

.results-section::-webkit-scrollbar {
    width: 6px;
}

.results-section::-webkit-scrollbar-thumb {
    background: rgba(146, 78, 255, 0.3);
    border-radius: 3px;
}

.results-section::-webkit-scrollbar-thumb:hover {
    background: rgba(146, 78, 255, 0.5);
}

/* 视频详情列表 */
.video-results-list {
    max-height: calc(100vh - 180px);
    overflow-y: auto;
}

.video-results-list::-webkit-scrollbar {
    width: 6px;
}

.video-results-list::-webkit-scrollbar-thumb {
    background: rgba(146, 78, 255, 0.3);
    border-radius: 3px;
}

.video-results-list::-webkit-scrollbar-thumb:hover {
    background: rgba(146, 78, 255, 0.5);
}

.video-results-list h5 {
    font-size: 14px;
    margin-bottom: 12px;
    color: var(--text);
    font-weight: 100;
}

.video-list-container {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.video-result-item {
    padding: 10px 12px;
    background: color-mix(in srgb, var(--card-bg) 40%, transparent);
    border-left: 3px solid var(--primary);
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.video-result-item:hover {
    background: color-mix(in srgb, var(--card-bg) 60%, transparent);
    transform: translateX(4px);
}

.video-result-item.active {
    background: color-mix(in srgb, var(--card-bg) 70%, transparent);
    border-color: var(--primary);
    box-shadow: 0 0 0 1px var(--primary);
}

.video-result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.video-result-index {
    font-size: 11px;
    color: var(--text-secondary);
    font-weight: 100;
}

.video-result-filename {
    flex: 1;
    font-size: 12px;
    color: var(--text);
    margin: 0 8px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.result-status {
    font-size: 14px;
    font-weight: 100;
}

.result-status.success {
    color: var(--success);
}

.result-status.error {
    color: var(--danger);
}

.video-result-details {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.video-result-emotion {
    display: flex;
    align-items: center;
    gap: 8px;
}

.result-emoji {
    font-size: 18px;
}

.result-emotion-name {
    font-size: 12px;
    color: var(--text);
}

.result-confidence {
    font-size: 11px;
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 100;
}

.video-result-metrics {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    color: var(--text-secondary);
}

.metric {
    font-weight: 100;
    display: flex;
    align-items: center;
    gap: 2px;
}

.video-result-error {
    font-size: 11px;
    color: var(--danger);
    padding: 4px 0;
}

/* 展开/收起按钮 */
.expand-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 8px;
    padding: 6px 12px;
    width: 100%;
    font-size: 12px;
    color: var(--text-secondary);
    background: color-mix(in srgb, var(--primary) 8%, transparent);
    border: 1px solid color-mix(in srgb, var(--primary) 20%, transparent);
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.expand-btn:hover {
    background: color-mix(in srgb, var(--primary) 15%, transparent);
    border-color: color-mix(in srgb, var(--primary) 35%, transparent);
    color: var(--primary);
}

.expand-btn .el-icon {
    font-size: 14px;
    transition: transform 0.2s ease;
}

/* 帧数据详情面板 */
.frame-details-panel {
    margin-top: 10px;
    padding: 10px;
    background: color-mix(in srgb, var(--card-bg) 30%, transparent);
    border: 1px solid color-mix(in srgb, var(--border) 60%, transparent);
    border-radius: 6px;
    animation: slideDown 0.3s ease;
}

@keyframes slideDown {
    from {
        opacity: 0;
        max-height: 0;
    }

    to {
        opacity: 1;
        max-height: 500px;
    }
}

.frame-details-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    padding-bottom: 6px;
    border-bottom: 1px solid color-mix(in srgb, var(--border) 40%, transparent);
}

.frame-count {
    font-size: 11px;
    color: var(--text-secondary);
    font-weight: 100;
}

.frame-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
    max-height: 300px;
    overflow-y: auto;
    padding-right: 4px;
}

.frame-list::-webkit-scrollbar {
    width: 4px;
}

.frame-list::-webkit-scrollbar-thumb {
    background: rgba(146, 78, 255, 0.25);
    border-radius: 2px;
}

.frame-list::-webkit-scrollbar-thumb:hover {
    background: rgba(146, 78, 255, 0.4);
}

.frame-item {
    padding: 8px 10px;
    background: color-mix(in srgb, var(--card-bg) 40%, transparent);
    border-radius: 4px;
    transition: all 0.2s ease;
}

.frame-item:hover {
    background: color-mix(in srgb, var(--card-bg) 55%, transparent);
}

.frame-time {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 6px;
}

.time-label {
    font-size: 12px;
}

.time-value {
    font-size: 12px;
    color: var(--text);
    font-family: 'Courier New', monospace;
    font-weight: 100;
}

.frame-faces {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}

.face-data {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 8px;
    background: color-mix(in srgb, var(--primary) 8%, transparent);
    border-radius: 4px;
    font-size: 11px;
}

.face-emoji {
    font-size: 14px;
}

.face-emotion {
    color: var(--text);
}

.face-confidence {
    color: var(--primary);
    font-weight: 100;
}

.no-face {
    font-size: 11px;
    color: var(--text-secondary);
    opacity: 0.6;
    font-style: italic;
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
        transform: translateY(10px);
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
