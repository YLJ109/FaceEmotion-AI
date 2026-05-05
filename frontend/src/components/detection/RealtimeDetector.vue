<template>
    <div class="realtime-page">
        <!-- 视频区域 -->
        <div class="video-section">
            <div class="video-container glass-panel" ref="videoContainer">
                <video ref="videoElement" autoplay playsinline style="display:none"></video>
                <canvas ref="canvasElement" class="video-canvas"></canvas>

                <!-- FPS显示 -->
                <div class="fps-badge" v-if="fps > 0 && isCameraOn">
                    <span class="fps-dot"></span>
                    {{ fps.toFixed(1) }} FPS
                </div>

                <!-- 摄像头状态 -->
                <div class="camera-status" v-if="isCameraOn">
                    <span class="status-dot online"></span>
                    摄像头已连接
                </div>

                <!-- 视频控制栏 -->
                <div class="video-controls" v-if="isCameraOn">
                    <button @click="takeScreenshot" class="ctrl-btn" title="截图">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                            stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path
                                d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
                            <circle cx="12" cy="13" r="4" />
                        </svg>
                    </button>
                    <button @click="stopCamera" class="ctrl-btn ctrl-stop" title="停止摄像头">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                            <rect x="6" y="6" width="12" height="12" rx="2" />
                        </svg>
                        <span class="btn-label">停止</span>
                    </button>

                    <!-- ✅ 新增: 功能按钮分隔线 -->
                    <div class="ctrl-divider"></div>

                    <!-- ✅ 新增: 情感识别按钮 -->
                    <el-tooltip content="情感识别" placement="top">
                        <button @click="toggleEmotionDetection" class="ctrl-btn ctrl-feature"
                            :class="{ 'ctrl-feature-active': isEmotionDetectionOn }" title="情感识别">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M12 2L2 7l10 5 10-5-10-5z" />
                                <path d="M2 17l10 5 10-5" />
                                <path d="M2 12l10 5 10-5" />
                            </svg>
                        </button>
                    </el-tooltip>

                    <!-- ✅ 新增: 反馈识别结果按钮（静态快照） -->
                    <el-tooltip content="反馈识别结果" placement="top" v-if="currentEmotion">
                        <button @click="openFeedbackWithSnapshot" class="ctrl-btn ctrl-feature" title="反馈识别结果">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                            </svg>
                        </button>
                    </el-tooltip>

                    <!-- ✅ 新增: 保存到历史档案按钮 -->
                    <el-tooltip content="保存到历史档案" placement="top">
                        <button @click="saveToHistoryManual" class="ctrl-btn ctrl-feature" :disabled="isSaving"
                            :class="{ 'ctrl-saving': isSaving }" title="保存到历史档案">
                            <svg v-if="!isSaving" width="18" height="18" viewBox="0 0 24 24" fill="none"
                                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
                                <polyline points="17 21 17 13 7 13 7 21" />
                                <polyline points="7 3 7 8 15 8" />
                            </svg>
                            <!-- 加载动画 -->
                            <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="saving-spinner">
                                <path d="M21 12a9 9 0 1 1-6.219-8.56" />
                            </svg>
                        </button>
                    </el-tooltip>
                </div>

                <!-- 启动摄像头按钮 -->
                <div class="camera-start-overlay" v-if="!isCameraOn">
                    <div class="overlay-content">
                        <div class="overlay-icon">
                            <el-icon :size="64">
                                <VideoCamera />
                            </el-icon>
                        </div>
                        <h3>实时人脸情感检测</h3>
                        <p>启动摄像头开始实时分析面部表情</p>
                        <el-button type="primary" :icon="VideoPlay" @click="toggleCamera" size="large" round>
                            启动摄像头
                        </el-button>
                    </div>
                </div>

            </div>
        </div>

        <!-- 情感信息面板 -->
        <div class="emotion-panel glass-panel">
            <div class="panel-header">
                <h3>
                    <span class="panel-icon"><el-icon>
                            <DataAnalysis />
                        </el-icon></span>
                    <span>实时分析</span>
                </h3>
            </div>

            <!-- 检测到人脸 -->
            <div v-if="currentEmotion" class="emotion-display">
                <!-- ✅ 移除: 大表情图标 -->
                <!-- <div class="emotion-icon-large">
                    <EmotionSVG :emotion="currentEmotion" size="xlarge" :animated="true" />
                </div> -->
                <!-- ✅ 移除: 情绪名称和置信度 -->
                <!-- <div class="emotion-name">{{ getEmotionName(currentEmotion) }}</div>
                <div class="emotion-confidence">{{ (currentConfidence * 100).toFixed(1) }}%</div> -->



                <!-- ✅ 移除: 情绪纠正按钮 -->
                <!-- <el-popover trigger="click" placement="bottom" width="200">
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
            :type="emotion === currentEmotion ? 'primary' : ''" @click="submitFeedback(emotion)" round>
            {{ getEmotionEmoji(emotion) }} {{ getEmotionName(emotion) }}
        </el-button>
    </div>
</div>
</el-popover> -->

                <!-- 置信度分布条 -->
                <div class="confidence-bars">
                    <transition-group name="emotion-sort" tag="div">
                        <div v-for="(item, index) in sortedEmotionScores" :key="item.emotion"
                            class="confidence-bar-item">
                            <span class="bar-label">
                                <EmotionSVG :emotion="item.emotion" size="small" :animated="false" />
                                {{ getEmotionName(item.emotion) }}
                            </span>
                            <div class="bar-track">
                                <div class="bar-fill" :style="{
                                    width: `${item.score * 100}%`, background: getEmotionColor(item.emotion),
                                    boxShadow: `0 0 8px ${getEmotionColor(item.emotion)}`
                                }"></div>
                            </div>
                            <span class="bar-value">{{ (item.score * 100).toFixed(0) }}%</span>
                        </div>
                    </transition-group>
                </div>


            </div>

            <!-- 等待状态 -->
            <div v-else class="no-detection">
                <EmotionSVG emotion="neutral" size="large" :animated="false" />
                <p class="status-hint">{{ isCameraOn ? '等待人脸检测...' : '请先启动摄像头' }}</p>
                <p class="status-sub">将脸部对准摄像头，系统将自动分析</p>
            </div>
        </div>

        <!-- ✅ 新增: 性能监控面板 -->
        <PerformanceMonitor :fps="fps" :latency="perfLatency" :skip-rate="perfSkipRate" :gpu-memory="perfGpuMemory"
            :detect-interval="perfDetectInterval" :http-latency="perfHttpLatency" :error-rate="perfErrorRate" />

        <!-- ✅ 新增: 情绪反馈对话框（静态快照） -->
        <EmotionFeedback v-model:visible="showFeedback" :snapshot="feedbackSnapshot"
            @submitted="handleFeedbackSubmitted" />
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, onActivated, onDeactivated, reactive, computed } from 'vue'
import { VideoCamera, VideoPlay } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useThemeStore } from '@/stores/theme'
import { getEmotionName, getEmotionColor, getEmotionEmoji } from '@/utils/emotion'
import { drawCornerBox, drawEmotionLabel } from '@/utils/canvas'
import wsManager from '@/api/websocket'
import EmotionSVG from '@/components/common/EmotionSVG.vue'
import { logFeatureUsage } from '@/utils/analytics'
import httpMonitor from '@/utils/httpMonitor'
import { API } from '@/api/config'
import PerformanceMonitor from '@/components/monitor/PerformanceMonitor.vue'
import EmotionFeedback from '@/components/feedback/EmotionFeedback.vue'

// ✅ 新增: 组件名称,用于 keep-alive 缓存
defineOptions({
    name: 'RealtimeDetector'
})

const themeStore = useThemeStore()
const videoElement = ref(null)
const canvasElement = ref(null)
const videoContainer = ref(null)
const isCameraOn = ref(false)
const isEmotionDetectionOn = ref(true)
const currentEmotion = ref(null)
const currentConfidence = ref(0)
const showFeedback = ref(false)  // ✅ 新增: 反馈对话框显示状态
const isSaving = ref(false)  // ✅ 新增: 保存状态标记
const feedbackSnapshot = ref({  // ✅ 新增: 反馈快照数据
    image: null,
    bbox: null,
    emotion: null,
    confidence: 0,
    timestamp: null
})
const emotionScores = ref({})
// ✅ 修复: 情绪列表（7种情绪，calm 合并到 neutral）
const emotionList = ['happy', 'sad', 'angry', 'surprised', 'fearful', 'disgust', 'neutral']

// ✅ 新增: 情绪分数排序计算属性（从高到低）
const sortedEmotionScores = computed(() => {
    return Object.entries(emotionScores.value)
        .map(([emotion, score]) => ({ emotion, score }))
        .sort((a, b) => b.score - a.score)  // 降序排序
})
const currentFaces = ref([])
const fps = ref(0)
// ✅ 新增: 性能监控数据
const perfLatency = ref(0)
const perfSkipRate = ref(0)
const perfGpuMemory = ref(0)
const perfDetectInterval = ref(2)
// ✅ 新增: HTTP延迟和错误率
const perfHttpLatency = ref(0)
const perfErrorRate = ref(0)

// ✅ 新增: 动态分辨率策略
const SEND_RESOLUTIONS = {
    low: { width: 128, height: 96 },      // FPS < 10
    medium: { width: 160, height: 120 },  // FPS 10-20
    high: { width: 224, height: 168 }     // FPS > 20
}
let currentResolution = SEND_RESOLUTIONS.medium
let lastAdjustTime = 0
let lastSaveTime = 0  // ✅ 新增: 上次保存时间戳,防止重复保存
const SAVE_COOLDOWN = 2000  // ✅ 新增: 保存冷却时间(2秒)

// ✅ 新增: 动态调整分辨率函数
const adjustResolution = () => {
    const currentFps = fps.value
    let newResolution = currentResolution

    if (currentFps < 10) {
        newResolution = SEND_RESOLUTIONS.low
    } else if (currentFps >= 10 && currentFps <= 20) {
        newResolution = SEND_RESOLUTIONS.medium
    } else {
        newResolution = SEND_RESOLUTIONS.high
    }

    // 只在分辨率变化时更新
    if (newResolution.width !== currentResolution.width || newResolution.height !== currentResolution.height) {
        console.log(`📊 调整分辨率: ${currentResolution.width}x${currentResolution.height} -> ${newResolution.width}x${newResolution.height}`)
        currentResolution = newResolution

        // 重新初始化发送 Canvas
        if (sendCanvas) {
            sendCanvas.width = currentResolution.width
            sendCanvas.height = currentResolution.height
        }
    }
}

let stream = null
let animationId = null
let lastFrameTime = performance.now()
let frameCountForFps = 0
let renderFps = 0  // Canvas 渲染帧率（不显示）
let inferenceFps = 0  // AI 推理帧率（显示）
let lastInferenceTime = 0
let inferenceCount = 0
let sendCanvas = null
let sendCtx = null
const SEND_WIDTH = 160
const SEND_HEIGHT = 120
let awaitingResult = false
let lastSentTime = 0
const RESULT_TIMEOUT = 5000

// === EMA 平滑(抗情绪闪烁) ===
const _emaScores = reactive({})
const EMA_ALPHA = 0.12  // ✅ 深度优化: 从0.18降到0.12,极致平滑度
let _consecutiveEmpty = 0
const EMPTY_THRESHOLD = 10  // ✅ 修复: 从3提高到10,避免频繁清除（约1-2秒容错）
let _lastGoodEmotion = null
let _lastGoodScores = {}
let _adaptiveQuality = 0.5  // retained for compatibility, no longer used for JPEG
let _roundTripHistory = []
let _themeChangeTimer = null
let _analyticsLogged = false
// 后端人脸检测间隔计数器(后端每2帧全检测,其余1帧仅分类)
let _lastFaceUpdate = 0
// ✅ 新增: 人脸框位置平滑
let _smoothedBbox = null
const BBOX_SMOOTH_ALPHA = 0.25  // ✅ 优化: 从0.3降到0.25,更平滑的坐标过渡
// ✅ 新增: 淡出效果控制
let _fadeOutActive = false
let _fadeOutStartTime = 0
const FADE_OUT_DURATION = 500  // 500ms淡出时长

onMounted(() => {
    wsManager.onConnect(() => { console.log('WebSocket 就绪') })
    wsManager.onMessage(handleWsMessage)
    wsManager.onDisconnect(() => {
        awaitingResult = false
        currentFaces.value = []
        currentEmotion.value = null
    })

    // ✅ 新增: 定时更新HTTP监控数据(每2秒)
    const httpMonitorInterval = setInterval(() => {
        const stats = httpMonitor.getStats()
        perfHttpLatency.value = stats.averageLatency
        perfErrorRate.value = stats.errorRate
    }, 2000)
})

onUnmounted(() => {
    stopCamera()
    // ✅ 优化: 清理 Canvas 防止内存泄漏
    cleanupCanvas()
})

// ✅ 新增: keep-alive 缓存时的生命周期
onDeactivated(() => {
    console.log(' 实时检测组件被缓存，停止摄像头')
    stopCamera()
})

onActivated(() => {
    console.log(' 实时检测组件被激活，恢复状态')
    // 注意: 不自动启动摄像头,由用户手动点击“启动摄像头”按钮
})

// ✅ 新增: Canvas 清理函数
const cleanupCanvas = () => {
    if (sendCanvas) {
        sendCtx = null
        sendCanvas = null
    }
}

// === 摄像头控制 ===

const startCamera = async () => {
    try {
        if (stream) stream.getTracks().forEach(t => t.stop())
        stream = await navigator.mediaDevices.getUserMedia({ video: true })
        if (videoElement.value) {
            videoElement.value.srcObject = stream
            await videoElement.value.play()
            startRendering()
            isCameraOn.value = true
        }
        ElMessage.success('✅ 摄像头已启动')
    } catch (error) {
        console.error('摄像头启动失败:', error)
        // ✅ 优化: 细化错误类型，提供友好提示
        if (error.name === 'NotAllowedError') {
            ElMessage.error('❌ 摄像头权限被拒绝，请在浏览器设置中允许访问')
        } else if (error.name === 'NotFoundError') {
            ElMessage.error('❌ 未检测到摄像头设备，请检查连接')
        } else if (error.name === 'NotReadableError') {
            ElMessage.error('❌ 摄像头被其他应用占用，请关闭后重试')
        } else if (error.name === 'OverconstrainedError') {
            ElMessage.error('❌ 摄像头不支持 requested 分辨率')
        } else {
            ElMessage.error(`❌ 摄像头启动失败: ${error.message}`)
        }
    }
}

const stopCamera = () => {
    if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null }
    if (animationId) { cancelAnimationFrame(animationId); animationId = null }
    isCameraOn.value = false
    fps.value = 0
    frameCountForFps = 0
    // ✅ 修改: 不清理情绪数据，保持右侧面板显示
    // currentEmotion.value = null
    // currentFaces.value = []
    awaitingResult = false
    _consecutiveEmpty = 0
    _adaptiveQuality = 0.5
    // 重置主题到用户设置
    themeStore.resetTheme()
}

const toggleCamera = () => { isCameraOn.value ? stopCamera() : startCamera() }
const toggleEmotionDetection = () => { isEmotionDetectionOn.value = !isEmotionDetectionOn.value }

// ✅ 新增: 提交情绪纠正反馈
const submitFeedback = async (correctEmotion) => {
    try {
        // ✅ 使用monitoredFetch追踪HTTP性能
        const response = await httpMonitor.monitoredFetch(API.feedback, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                emotion: currentEmotion.value,
                predicted_emotion: currentEmotion.value,
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

// === 渲染循环（自适应帧率 + 质量） ===

const initSendCanvas = () => {
    if (!sendCanvas) {
        sendCanvas = document.createElement('canvas')
        // ✅ 使用动态分辨率
        sendCanvas.width = currentResolution.width
        sendCanvas.height = currentResolution.height
        // 开启 willReadFrequently 优化高频 getImageData 性能
        sendCtx = sendCanvas.getContext('2d', { willReadFrequently: true })
    }
}

const updateFps = () => {
    const now = performance.now()
    frameCountForFps++
    if (now - lastFrameTime >= 1000) {
        renderFps = frameCountForFps * (1000 / (now - lastFrameTime))
        lastFrameTime = now
        frameCountForFps = 0
    }
}

const updateInferenceFps = () => {
    const now = performance.now()
    inferenceCount++
    if (now - lastInferenceTime >= 1000) {
        inferenceFps = inferenceCount * (1000 / (now - lastInferenceTime))
        fps.value = inferenceFps  // 显示真实 AI 推理帧率
        lastInferenceTime = now
        inferenceCount = 0
    }
}

const startRendering = () => {
    const canvas = canvasElement.value
    const video = videoElement.value
    if (!canvas || !video) return

    initSendCanvas()
    const ctx = canvas.getContext('2d', { willReadFrequently: true })
    let frameSkip = 0
    let lastRenderTime = 0
    const TARGET_FPS = 30  // 目标渲染帧率
    const FRAME_INTERVAL = 1000 / TARGET_FPS

    // 静态帧跳过优化
    let lastFrameHash = 0
    let staticFrameCount = 0
    const MAX_STATIC_FRAMES = 5  // 最多跳过 5 帧

    const render = (timestamp) => {
        if (!video || video.readyState !== 4) {
            animationId = requestAnimationFrame(render)
            return
        }

        // ✅ 深度优化: 检测视频帧是否真正更新(避免无效重绘)
        const currentVideoTime = video.currentTime
        if (render._lastVideoTime === currentVideoTime && !currentFaces.value?.length) {
            // 视频暂停或静止且无人脸,跳过渲染
            animationId = requestAnimationFrame(render)
            return
        }
        render._lastVideoTime = currentVideoTime

        // 帧率限制：控制渲染速度，避免绘制过快
        const elapsed = timestamp - lastRenderTime
        if (elapsed < FRAME_INTERVAL) {
            animationId = requestAnimationFrame(render)
            return
        }
        lastRenderTime = timestamp - (elapsed % FRAME_INTERVAL)

        // ✅ 优化: 只在视频尺寸变化时更新 canvas 宽高，避免频繁重布局
        const vw = video.videoWidth || 640
        const vh = video.videoHeight || 480
        if (canvas.width !== vw || canvas.height !== vh) {
            canvas.width = vw
            canvas.height = vh
        }

        // 绘制视频帧
        ctx.save()
        ctx.translate(canvas.width, 0)
        ctx.scale(-1, 1)
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
        ctx.restore()

        updateFps()

        // 静态帧跳过优化：检测画面是否变化
        if (currentFaces.value?.length === 0) {
            // 采样部分像素计算哈希
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
            let currentHash = 0
            const step = 200  // 每 200 个像素采样一次
            for (let i = 0; i < imageData.data.length; i += step * 4) {
                currentHash = ((currentHash << 5) - currentHash) + imageData.data[i]
                currentHash |= 0
            }

            if (currentHash === lastFrameHash) {
                staticFrameCount++
                if (staticFrameCount >= MAX_STATIC_FRAMES) {
                    // 画面静止，跳过渲染（降低 CPU 占用）
                    animationId = requestAnimationFrame(render)
                    return
                }
            } else {
                staticFrameCount = 0
                lastFrameHash = currentHash
            }
        } else {
            staticFrameCount = 0
            lastFrameHash = 0
        }

        // 绘制人脸框和标签(与视频帧同步)
        if (currentFaces.value?.length && currentEmotion.value) {
            // ✅ 修复: 使用实际发送到后端的图片尺寸计算缩放比例
            const scaleX = canvas.width / currentResolution.width
            const scaleY = canvas.height / currentResolution.height
            const totalFaces = currentFaces.value.length

            // ✅ 新增: 已绘制的标签位置数组（用于碰撞检测）
            const drawnLabels = []

            currentFaces.value.forEach((face, index) => {
                let [x, y, w, h] = face.bbox

                // ✅ 深度优化: 人脸框坐标平滑(减少抖动)
                if (_smoothedBbox && _smoothedBbox[index]) {
                    const [px, py, pw, ph] = _smoothedBbox[index]
                    x = px * (1 - BBOX_SMOOTH_ALPHA) + x * BBOX_SMOOTH_ALPHA
                    y = py * (1 - BBOX_SMOOTH_ALPHA) + y * BBOX_SMOOTH_ALPHA
                    w = pw * (1 - BBOX_SMOOTH_ALPHA) + w * BBOX_SMOOTH_ALPHA
                    h = ph * (1 - BBOX_SMOOTH_ALPHA) + h * BBOX_SMOOTH_ALPHA
                    _smoothedBbox[index] = [x, y, w, h]
                } else {
                    if (!_smoothedBbox) _smoothedBbox = []
                    _smoothedBbox[index] = [x, y, w, h]
                }

                const sx = x * scaleX, sy = y * scaleY, sw = w * scaleX, sh = h * scaleY
                const flippedBbox = [canvas.width - sx - sw, sy, sw, sh]
                const color = getEmotionColor(face.emotion)
                drawCornerBox(ctx, flippedBbox, color, 3)

                // ✅ 新增: 绘制情绪标签，传入已绘制标签数组避免重叠
                const labelRect = drawEmotionLabel(ctx, flippedBbox, face.emotion, face.confidence, themeStore.currentTheme, index + 1, totalFaces, drawnLabels)
                drawnLabels.push(labelRect)
            })
        } else {
            // 无人脸时重置平滑状态
            _smoothedBbox = null
        }

        // 安全超时（3秒无结果认为后端卡住，自动重试）
        if (awaitingResult && performance.now() - lastSentTime > 3000) {
            console.warn('检测超时，重置状态')
            awaitingResult = false
        }

        // 持续发送帧（不再等待后端响应）
        frameSkip++

        // ✅ 新增: 每5秒调整一次分辨率
        if (performance.now() - lastAdjustTime > 5000) {
            adjustResolution()
            lastAdjustTime = performance.now()
        }

        // 根据真实延迟自适应跳帧
        const avgRtt = _roundTripHistory.length > 0
            ? _roundTripHistory.reduce((a, b) => a + b, 0) / _roundTripHistory.length : 0

        // ✅ 优化: 动态调整跳帧阈值（更激进的策略）
        const skipThreshold = avgRtt > 250 ? 3 : avgRtt > 150 ? 2 : 1

        if (frameSkip >= skipThreshold && isEmotionDetectionOn.value) {
            frameSkip = 0
            lastSentTime = performance.now()

            // ✅ 使用动态分辨率
            sendCtx.drawImage(video, 0, 0, currentResolution.width, currentResolution.height)
            const imageData = sendCtx.getImageData(0, 0, currentResolution.width, currentResolution.height)
            // 二进制格式: [type(1B)] + [width(2B), height(2B), RGBA像素...]
            const buf = new ArrayBuffer(1 + 4 + imageData.data.length)
            const dv = new DataView(buf)
            dv.setUint8(0, 0x01) // 类型标识：0x01=video
            dv.setUint16(1, currentResolution.width, true)
            dv.setUint16(3, currentResolution.height, true)
            new Uint8Array(buf, 5).set(imageData.data)

            // 非阻塞发送
            try {
                wsManager.sendBinary(buf)
            } catch (error) {
                console.warn('发送帧失败:', error)
            }
        }

        // 调试信息：显示平均延迟
        if (avgRtt > 100 && frameSkip === 0) {
            console.log(`📊 平均延迟: ${avgRtt.toFixed(0)}ms, 跳帧: ${skipThreshold}`)
        }

        animationId = requestAnimationFrame(render)
    }
    render(performance.now())
}

// === WebSocket 消息处理 (含 EMA + 自适应质量) ===

const handleWsMessage = (data) => {
    if (data.type !== 'result') return



    // ✅ 新增: 更新性能监控数据
    const processTime = data.process_time
    // ✅ 修复: 使用 lastSentTime 计算往返延迟，而不是 process_time
    // process_time 是后端处理完成的时间戳，不能直接用于计算 RTT
    const actualRtt = performance.now() - lastSentTime
    perfLatency.value = Math.max(0, actualRtt)  // 确保非负

    if (data.gpu_memory !== undefined) {
        perfGpuMemory.value = data.gpu_memory
    }

    // 计算真实处理延迟
    const rtt = Math.max(0, actualRtt)

    _roundTripHistory.push(rtt)
    if (_roundTripHistory.length > 10) _roundTripHistory.shift()

    // ✅ 新增: 计算跳帧率
    const avgRtt = _roundTripHistory.length > 0
        ? _roundTripHistory.reduce((a, b) => a + b, 0) / _roundTripHistory.length : 0
    const skipThreshold = avgRtt > 250 ? 3 : avgRtt > 150 ? 2 : 1
    perfSkipRate.value = ((skipThreshold - 1) / skipThreshold) * 100

    awaitingResult = false

    // 过滤掉低置信度的缓存结果（置信度 < 0.6 视为无效）
    const validFaces = data.faces?.filter(face => face.confidence >= 0.6 && !face._cached) || []

    if (validFaces.length) {
        const rawScores = validFaces[0].scores



        if (Object.keys(_emaScores).length === 0) {
            Object.keys(rawScores).forEach(k => { _emaScores[k] = rawScores[k] })
            _lastGoodScores = { ...rawScores }
        } else {
            Object.entries(rawScores).forEach(([k, v]) => {
                _emaScores[k] = (_emaScores[k] !== undefined ? _emaScores[k] : 0) * (1 - EMA_ALPHA) + v * EMA_ALPHA
            })
        }

        const smoothedEmotion = Object.keys(_emaScores).reduce((a, b) =>
            _emaScores[a] > _emaScores[b] ? a : b
        )
        const smoothedConf = _emaScores[smoothedEmotion]

        _lastGoodEmotion = smoothedEmotion
        _lastGoodScores = { ..._emaScores }
        _consecutiveEmpty = 0



        if (rtt < 100) {
            // quickly restore after a slow frame
        } else if (rtt > 300) {
            // backend is loaded, skip will auto-adjust
        }

        currentEmotion.value = smoothedEmotion
        currentConfidence.value = smoothedConf
        emotionScores.value = { ..._emaScores }
        currentFaces.value = validFaces

        // ✅ 优化: 移除延迟,立即触发主题更新(防抖在 themeStore 内部处理)
        themeStore.updateThemeByEmotion(smoothedEmotion)
    } else {
        // 没有检测到有效人脸
        _consecutiveEmpty++

        // ✅ 修复: 连续无人脸时，保持缓存的人脸框（不立即清除）
        // 只有当连续超过阈值时才触发淡出
        if (_consecutiveEmpty >= EMPTY_THRESHOLD) {
            // 启动淡出效果
            if (!_fadeOutActive) {
                _fadeOutActive = true
                _fadeOutStartTime = performance.now()
            }

            // 计算淡出进度(0-1)
            const elapsed = performance.now() - _fadeOutStartTime
            const fadeProgress = Math.min(1, elapsed / FADE_OUT_DURATION)

            // 线性衰减置信度
            if (_lastGoodEmotion && currentConfidence.value > 0) {
                currentConfidence.value = Math.max(0, _lastGoodScores[_lastGoodEmotion] || 0) * (1 - fadeProgress)
            }

            // 淡出完成后彻底清除
            if (fadeProgress >= 1) {
                // ✅ 修改: 不清除情绪数据，保持右侧面板显示
                // currentEmotion.value = null
                currentConfidence.value = 0
                // emotionScores.value = {}
                // currentFaces.value = []
                // 重置EMA
                Object.keys(_emaScores).forEach(key => delete _emaScores[key])
                _lastGoodEmotion = null
                _lastGoodScores = {}
                _smoothedBbox = null  // 重置框平滑
                _fadeOutActive = false
                _consecutiveEmpty = 0  // ✅ 修复: 重置计数器
            }
        } else {
            // ✅ 修复: 在阈值内，保持显示但轻微降低置信度（不删除人脸框）
            if (_lastGoodEmotion && currentConfidence.value > 0) {
                // 更温和的衰减（从0.08降到0.03）
                currentConfidence.value = Math.max(0, currentConfidence.value - 0.03)
            }
            // 保持 currentFaces 不变，继续显示最后检测到的人脸框
        }
    }
}

const takeScreenshot = () => {
    const canvas = canvasElement.value
    if (canvas) {
        const link = document.createElement('a')
        link.download = `screenshot_${Date.now()}.png`
        link.href = canvas.toDataURL()
        link.click()
        ElMessage.success('✅ 截图已保存')
    }
}

// ✅ 新增: 打开反馈对话框并捕获静态快照
const openFeedbackWithSnapshot = () => {
    const canvas = canvasElement.value
    if (!canvas || !currentEmotion.value) {
        ElMessage.warning('⚠️ 请先确保已检测到人脸')
        return
    }

    try {
        // 1. 截取当前 Canvas 帧（包含人脸框和标签）
        const imageData = canvas.toDataURL('image/jpeg', 0.9)

        // 2. 获取当前检测数据
        const currentFace = currentFaces.value[0]

        // 3. 存储快照数据
        feedbackSnapshot.value = {
            image: imageData,
            bbox: currentFace?.bbox || null,
            emotion: currentEmotion.value,
            confidence: currentConfidence.value,
            timestamp: Date.now()
        }

        console.log('📸 静态快照已捕获:', {
            emotion: feedbackSnapshot.value.emotion,
            confidence: feedbackSnapshot.value.confidence,
            bbox: feedbackSnapshot.value.bbox,
            timestamp: new Date(feedbackSnapshot.value.timestamp).toLocaleString()
        })

        // 4. 打开反馈对话框
        showFeedback.value = true
    } catch (error) {
        console.error('❌ 捕获快照失败:', error)
        ElMessage.error('❌ 截图失败，请重试')
    }
}

// ✅ 新增: 手动保存到历史档案
const saveToHistoryManual = async () => {
    console.log(' 用户点击保存按钮')

    // 检查是否有可保存的数据
    if (!currentEmotion.value || !currentConfidence.value || currentFaces.value.length === 0) {
        ElMessage.warning('⚠️ 暂无可保存的检测数据')
        return
    }

    // 防止重复点击
    if (isSaving.value) {
        console.log('️ 正在保存中，忽略重复点击')
        return
    }

    try {
        isSaving.value = true
        console.log(' 开始手动保存历史记录...')

        await saveRealtimeToHistory(
            currentEmotion.value,
            currentConfidence.value,
            currentFaces.value
        )

        ElMessage.success('✅ 已保存到历史档案')
        console.log('✅ 手动保存成功')
    } catch (error) {
        console.error(' 手动保存失败:', error)
        ElMessage.error('❌ 保存失败，请重试')
    } finally {
        // 延迟重置状态，让用户看到加载动画
        setTimeout(() => {
            isSaving.value = false
            console.log(' 保存锁已释放')
        }, 500)
    }
}

// ✅ 新增: 处理反馈提交成功
const handleFeedbackSubmitted = () => {
    // 反馈提交后，清除快照数据
    feedbackSnapshot.value = {
        image: null,
        bbox: null,
        emotion: null,
        confidence: 0,
        timestamp: null
    }
    console.log('✅ 用户反馈已提交，系统将自动学习优化')
}

// ✅ 新增: 保存实时检测历史记录
const saveRealtimeToHistory = async (emotion, confidence, faces) => {
    try {
        // ✅ 新增: 防止重复保存(2秒冷却时间)
        const now = Date.now()
        const timeSinceLastSave = now - lastSaveTime
        console.log(`⏱️ 距离上次保存: ${timeSinceLastSave}ms`)

        if (timeSinceLastSave < SAVE_COOLDOWN) {
            console.log('ℹ️ 保存过于频繁,已跳过(冷却中)')
            ElMessage.warning('⚠️ 请勿重复保存')
            return
        }
        lastSaveTime = now
        console.log('📝 开始执行保存操作...')

        // ✅ 修复: 增加更严格的检查
        if (!isCameraOn.value) {
            console.log('ℹ️ 摄像头已关闭，跳过保存历史记录')
            return
        }

        const canvas = canvasElement.value
        if (!canvas) {
            console.warn('⚠️ Canvas 元素未找到，无法保存历史记录')
            return
        }

        // ✅ 新增: 检查 Canvas 是否有有效尺寸
        if (canvas.width === 0 || canvas.height === 0) {
            console.warn('⚠️ Canvas 尺寸为 0，无法保存历史记录')
            return
        }

        console.log(' 开始保存实时检测历史记录...', {
            emotion,
            confidence,
            canvasSize: `${canvas.width}x${canvas.height}`,
            facesCount: faces.length
        })

        // ✅ 终极修复: 不再保存全局坐标，而是直接裁剪人脸区域
        const thumbnailCanvas = document.createElement('canvas')
        const thumbCtx = thumbnailCanvas.getContext('2d')
        thumbnailCanvas.width = 320
        thumbnailCanvas.height = 240

        console.log('🖼️ 缩略图生成开始:', {
            sourceCanvasSize: `${canvas.width}x${canvas.height}`,
            facesCount: faces.length
        })

        let savedFaces = []

        if (faces.length > 0 && faces[0].bbox) {
            // ✅ 核心重构: 裁剪人脸区域并填充整个320x240
            const bbox = Array.from(faces[0].bbox)
            let [x, y, w, h] = bbox

            console.log('📍 原始人脸bbox:', bbox, '(来自发送Canvas坐标系)')

            // ✅ 关键: bbox来自发送Canvas,需转换到显示Canvas坐标
            const scaleX = canvas.width / currentResolution.width
            const scaleY = canvas.height / currentResolution.height

            const displayX = x * scaleX
            const displayY = y * scaleY
            const displayW = w * scaleX
            const displayH = h * scaleY

            console.log('✅ 转换到显示Canvas的bbox:', [displayX, displayY, displayW, displayH])

            // 添加20%边距
            const padding = 0.2
            const padX = Math.max(0, displayX - displayW * padding)
            const padY = Math.max(0, displayY - displayH * padding)
            const padW = displayW * (1 + padding * 2)
            const padH = displayH * (1 + padding * 2)

            // 验证裁剪区域有效性
            if (padW <= 0 || padH <= 0) {
                console.error('❌ 裁剪区域尺寸无效,使用默认完整帧')
                thumbCtx.drawImage(canvas, 0, 0, 320, 240)
                savedFaces = [{
                    ...faces[0],
                    bbox: [80, 60, 160, 120]
                }]
            } else {
                // ✅ 将裁剪区域直接填充到320x240(无黑边)
                thumbCtx.drawImage(
                    canvas,
                    padX, padY, padW, padH,  // 源图像裁剪区域
                    0, 0, 320, 240  // 目标区域(填满整个缩略图)
                )

                console.log('✅ 人脸区域已裁剪并填充缩略图')

                // ✅ bbox设置为缩略图中的中心区域(80%大小)
                savedFaces = [{
                    ...faces[0],
                    bbox: [32, 24, 256, 192]  // 320x240的80%中心区域
                }]

                console.log(' 保存到数据库的bbox (320x240坐标系):', savedFaces[0].bbox)
            }

            // 保存其他人脸(使用相同逻辑)
            for (let i = 1; i < faces.length; i++) {
                if (faces[i].bbox) {
                    savedFaces.push({
                        ...faces[i],
                        bbox: [32, 24, 256, 192]
                    })
                }
            }
        } else {
            // 无人脸：保存完整帧（居中缩放）
            console.log('⚠️ 未检测到人脸，保存完整帧')
            const sourceWidth = canvas.width || 640
            const sourceHeight = canvas.height || 480
            const scale = Math.min(320 / sourceWidth, 240 / sourceHeight)
            const scaledWidth = sourceWidth * scale
            const scaledHeight = sourceHeight * scale
            const offsetX = (320 - scaledWidth) / 2
            const offsetY = (240 - scaledHeight) / 2

            thumbCtx.drawImage(
                canvas,
                0, 0, sourceWidth, sourceHeight,
                offsetX, offsetY, scaledWidth, scaledHeight
            )
        }

        const thumbnail = thumbnailCanvas.toDataURL('image/jpeg', 0.8)
        console.log('📦 缩略图生成完成:', {
            dataLength: thumbnail.length,
            expectedRange: '8000-15000 bytes',
            isEmpty: thumbnail.length < 5000
        })

        // ✅ 构建保存数据（使用已转换坐标的savedFaces）
        const historyData = {
            detection_type: 'realtime',
            results: [{
                emotion: emotion,
                confidence: confidence,
                bbox: savedFaces.length > 0 ? savedFaces[0].bbox : [0, 0, 0, 0]
            }],
            source: '摄像头实时检测',
            image_path: '',
            image_type: 'realtime',
            thumbnail: thumbnail,
            dominant_emotion: emotion,
            confidence: confidence,
            detected_faces: savedFaces  // ✅ bbox已是320x240坐标系
        }

        // 调用保存接口
        const response = await fetch(API.historySave, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(historyData)
        })

        if (response.ok) {
            console.log('✅ 实时检测历史记录已保存')
        } else {
            console.warn('️ 保存历史记录失败:', response.statusText)
        }
    } catch (error) {
        console.error('❌ 保存实时检测历史记录失败:', error)
    }
}
</script>

<style scoped>
.realtime-page {
    height: 100%;
    display: grid;
    grid-template-columns: 1fr 320px;
    gap: 16px;
    padding: 0;
}

.glass-panel {
    background: var(--card-bg);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    box-shadow: var(--shadow);
    border-radius: var(--radius-md);
    transition: all 0.3s ease;
}

.glass-panel:hover {
    border-color: color-mix(in srgb, var(--border) 70%, var(--primary));
    box-shadow: var(--shadow-lg);
}

.video-section {
    display: flex;
    flex-direction: column;
    height: 100%;
    position: relative;
    min-height: 0;
}

.video-container {
    position: relative;
    width: 100%;
    height: 100%;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
}

.video-container:hover {
    border-color: color-mix(in srgb, var(--border) 70%, var(--primary));
}

.video-canvas {
    width: 100%;
    height: 100%;
    object-fit: contain;
    display: block;
}

.fps-badge,
.camera-status {
    position: absolute;
    backdrop-filter: blur(10px);
    padding: 5px 12px;
    border-radius: 8px;
    font-size: 11px;
    /* font-weight: 100; */
    z-index: 10;
    display: flex;
    align-items: center;
    gap: 6px;
    border: 1px solid color-mix(in srgb, var(--border) 15%, transparent);
}

.fps-badge {
    top: 12px;
    right: 12px;
    background: rgba(0, 0, 0, 0.55);
    color: var(--success);
    font-family: 'Consolas', 'Monaco', monospace;
}

.camera-status {
    top: 12px;
    left: 12px;
    background: rgba(0, 0, 0, 0.5);
    color: var(--text-secondary);
}

.fps-dot,
.status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    flex-shrink: 0;
}

.fps-dot {
    background: var(--success);
    box-shadow: 0 0 6px var(--success);
    animation: pulseDot 1s ease-in-out infinite;
}

.status-dot.online {
    background: var(--success);
    box-shadow: 0 0 6px var(--success);
    animation: pulseDot 2s ease-in-out infinite;
}

@keyframes pulseDot {

    0%,
    100% {
        opacity: 1;
    }

    50% {
        opacity: 0.3;
    }
}

.video-controls {
    position: absolute;
    bottom: 16px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 10;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(14px);
    padding: 6px 12px;
    border-radius: 40px;
    border: 1px solid color-mix(in srgb, var(--border) 15%, transparent);
    display: flex;
    align-items: center;
    gap: 6px;
}

.ctrl-btn {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    outline: none;
    border: none;
    background: color-mix(in srgb, var(--primary) 8%, transparent);
    color: var(--text-secondary);
    transition: all 0.2s ease;
    padding: 0;
}

.ctrl-btn:hover {
    background: color-mix(in srgb, var(--primary) 18%, transparent);
    color: var(--text);
    transform: scale(1.1);
}

.ctrl-btn:active {
    transform: scale(0.92);
}

.ctrl-stop {
    background: rgba(255, 71, 87, 0.15);
    color: #FF4757;
    width: auto;
    border-radius: 30px;
    padding: 0 16px;
    gap: 6px;
}

.ctrl-stop:hover {
    background: rgba(255, 71, 87, 0.3);
    color: #FF6B7A;
    transform: scale(1.05);
}

.btn-label {
    font-size: 12px;
    /* font-weight: 100; */
}

/* ✅ 新增: 功能按钮分隔线 */
.ctrl-divider {
    width: 1px;
    height: 24px;
    background: rgba(255, 255, 255, 0.2);
    margin: 0 4px;
}

/* ✅ 新增: 功能按钮样式 */
.ctrl-feature {
    background: color-mix(in srgb, var(--primary) 8%, transparent) !important;
    color: var(--text-secondary) !important;
}

.ctrl-feature:hover {
    background: color-mix(in srgb, var(--primary) 18%, transparent) !important;
    color: var(--text) !important;
}

/* ✅ 新增: 功能按钮激活状态 */
.ctrl-feature-active {
    background: linear-gradient(135deg, var(--primary), #9B59B6) !important;
    color: var(--text) !important;
    box-shadow: 0 0 12px rgba(113, 57, 255, 0.6), 0 0 20px rgba(113, 57, 255, 0.3) !important;
}

.ctrl-feature-active:hover {
    box-shadow: 0 0 16px rgba(113, 57, 255, 0.8), 0 0 24px rgba(113, 57, 255, 0.4) !important;
}

/* ✅ 新增: 麦克风按钮脉冲动画 */
.ctrl-feature-active.mic-active {
    animation: ctrlMicPulse 2s ease-in-out infinite;
}

@keyframes ctrlMicPulse {

    0%,
    100% {
        box-shadow: 0 0 12px rgba(113, 57, 255, 0.6), 0 0 20px rgba(113, 57, 255, 0.3);
    }

    50% {
        box-shadow: 0 0 16px rgba(113, 57, 255, 0.8), 0 0 28px rgba(113, 57, 255, 0.4);
    }
}

/* ✅ 新增: 保存按钮加载状态 */
.ctrl-saving {
    opacity: 0.7;
    cursor: not-allowed;
    pointer-events: none;
}

.saving-spinner {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
}

.camera-start-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--card-bg);
    backdrop-filter: blur(8px);
    z-index: 5;
}

.overlay-content {
    text-align: center;
    animation: fadeInUp 0.6s ease;
}

.overlay-icon {
    margin-bottom: 16px;
    color: var(--primary);
    opacity: 0.6;
}

.overlay-content h3 {
    font-size: 20px;
    font-weight: 100;
    color: var(--text);
    margin-bottom: 6px;
}

.overlay-content p {
    color: var(--text-secondary);
    font-size: 13px;
    margin-bottom: 24px;
    opacity: 0.7;
}

.emotion-panel {
    height: 100%;
    padding: 16px;
    /* ✅ 修复: 面板自身不滚动，让内部元素管理滚动 */
    overflow: hidden;
    display: flex;
    flex-direction: column;
    /* ✅ 移除: min-height，让高度完全自适应内容 */
}

.panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    /* margin-bottom: 16px; */
    flex-shrink: 0;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
}

.panel-header h3 {
    font-size: 19px;
    font-weight: 100;
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--text);
    margin: 0;
}

.panel-icon {
    display: flex;
    color: var(--primary);
}

.panel-controls {
    display: flex;
    gap: 6px;
}

.emotion-display {
    padding: 10px 10px;
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    /* ✅ 修复: 仅在内容溢出时显示滚动条，隐藏滚动条轨道 */
    overflow-y: auto;
    overflow-x: hidden;
    animation: fadeIn 0.3s ease;
    /* ✅ 优化: 使用相对高度而非视口高度，避免超出父容器 */
    min-height: 0;
    max-height: 100%;
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

/* ✅ 新增: 内容未溢出时隐藏滚动条轨道 */
.emotion-display::-webkit-scrollbar-track {
    background: transparent;
}

.emotion-icon-large {
    margin-bottom: 2px;
    filter: drop-shadow(0 0 20px rgba(113, 57, 255, 0.25));
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
    font-size: 26px;
    /* font-weight: 800; */
    color: var(--highlight);
    flex-shrink: 0;
    text-shadow: 0 0 12px rgba(226, 202, 255, 0.3);
}

/* ✅ 新增: 多模态融合指示器样式 */
.voice-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 12px;
    padding: 8px 12px;
    background: linear-gradient(135deg, rgba(113, 57, 255, 0.15), rgba(156, 78, 255, 0.1));
    border: 1px solid rgba(113, 57, 255, 0.3);
    border-radius: 8px;
    animation: voicePulse 2s ease-in-out infinite;
}

.voice-icon {
    font-size: 18px;
    animation: micBounce 1s ease-in-out infinite;
}

.voice-text {
    font-size: 13px;
    /* font-weight: 100; */
    color: var(--text);
    flex: 1;
}

.voice-badge {
    font-size: 11px;
    font-weight: 100;
    color: var(--primary-light);
    background: rgba(113, 57, 255, 0.2);
    padding: 2px 8px;
    border-radius: 12px;
    border: 1px solid rgba(113, 57, 255, 0.3);
}

/* ✅ 新增: 音频活动指示器样式 */
.audio-activity-bar {
    width: 60px;
    height: 4px;
    background: color-mix(in srgb, var(--border) 20%, transparent);
    border-radius: 2px;
    overflow: hidden;
    margin-left: 8px;
}

.audio-activity-fill {
    height: 100%;
    background: linear-gradient(90deg, #67C23A, #E6A23C, #F56C6C);
    border-radius: 2px;
    transition: width 0.1s ease-out;
    box-shadow: 0 0 8px rgba(103, 194, 58, 0.5);
}

@keyframes voicePulse {

    0%,
    100% {
        box-shadow: 0 0 8px rgba(113, 57, 255, 0.3);
    }

    50% {
        box-shadow: 0 0 16px rgba(113, 57, 255, 0.5);
    }
}

@keyframes micBounce {

    0%,
    100% {
        transform: scale(1);
    }

    50% {
        transform: scale(1.1);
    }
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

.confidence-bars {
    width: 100%;
    display: flex;
    flex-direction: column;
    /* gap: 6px; */
    margin-top: 12px;
    flex-shrink: 0;
    /* ✅ 修复: 移除 overflow-y，避免未溢出时显示滚动条 */
    overflow-y: visible;
}

/* ✅ 新增: 置信度条容器滚动条样式 */
.confidence-bars::-webkit-scrollbar {
    width: 6px;
}

.confidence-bars::-webkit-scrollbar-thumb {
    background: rgba(146, 78, 255, 0.3);
    border-radius: 3px;
}

.confidence-bars::-webkit-scrollbar-thumb:hover {
    background: rgba(146, 78, 255, 0.5);
}

/* ✅ 新增: 内容未溢出时隐藏滚动条轨道 */
.confidence-bars::-webkit-scrollbar-track {
    background: transparent;
}

/* ✅ 新增: 情绪排序丝滑动画 */
.emotion-sort-move {
    transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.emotion-sort-enter-active {
    transition: all 0.3s ease;
}

.emotion-sort-leave-active {
    transition: all 0.3s ease;
    position: absolute;
}

.emotion-sort-enter-from,
.emotion-sort-leave-to {
    opacity: 0;
    transform: translateX(30px);
}

.confidence-bar-item {
    display: grid;
    grid-template-columns: 90px minmax(100px, 1fr) 45px;
    /* ✅ 修改: 进度条列设置最小宽度 100px */
    align-items: center;
    gap: 15px;
    margin-top: 6px;
}

.voice-bar-item {
    grid-template-columns: 90px minmax(100px, 1fr) 45px;
    /* ✅ 新增: 语音情绪使用相同的列宽，确保进度条可见 */
}

.bar-label {
    font-size: 18px;
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

.bar-track {
    height: 20px;
    width: 100%;
    /* ✅ 新增: 确保进度条占满容器 */
    display: block;
    /* ✅ 新增: 确保正确显示 */
    background: color-mix(in srgb, var(--text) 10%, transparent);
    border-radius: 4px;
    overflow: hidden;
}

.bar-fill {
    height: 100%;
    display: block;
    /* ✅ 新增: 确保正确显示 */
    border-radius: 4px;
    transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.bar-value {
    font-size: 18px;
    font-weight: 100;
    text-align: right;
    color: var(--text);
}

/* ✅ 新增: 语音情绪区域样式 */
.voice-emotion-section {
    /* margin-top: 16px; */
    padding-top: 12px;
    border-top: 1px solid color-mix(in srgb, var(--border) 20%, transparent);
}

.voice-emotion-title {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 18px;
    /* ✅ 修改: 与上方标题保持一致 */
    font-weight: 100;
    /* ✅ 修改: 加粗 */
    color: var(--text);
    /* ✅ 修改: 使用主题色 */
    margin-bottom: 12px;
}

.voice-icon-small {
    font-size: 18px;
    /* ✅ 修改: 与上方一致 */
}

.voice-bars {
    opacity: 1;
    /* ✅ 修改: 不透明度恢复为1 */
}

.voice-bar-item .bar-label {
    font-size: 18px;
    /* ✅ 修改: 与上方保持一致 */
}

.voice-bar-item .bar-track {
    height: 20px;
    width: 100%;
    display: block;
    /* ✅ 修改: 与上方保持一致 */
}

.voice-bar-item .bar-fill {
    height: 100%;
    display: block;
    /* ✅ 新增: 确保进度条填充可见 */
}

.voice-bar-item .bar-value {
    font-size: 18px;
    /* ✅ 修改: 与上方保持一致 */
}

.voice-fill {
    opacity: 1;
    /* ✅ 修改: 不透明度恢复为1 */
    /* ✅ 移除: 渐变效果，与上方保持一致 */
    /* background-image: repeating-linear-gradient(...) */
}

/* 无人脸提示 */
.no-detection {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 10px;
    color: var(--text-secondary);
    /* ✅ 新增: 确保等待状态占据剩余空间 */
    min-height: 0;
}

.status-hint {
    font-size: 15px;
    font-weight: 100;
    color: var(--text);
}

.status-sub {
    font-size: 12px;
    color: var(--text-secondary);
    opacity: 0.7;
    font-weight: 100;
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
        transform: translateY(16px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@media (max-width: 768px) {
    .realtime-page {
        grid-template-columns: 1fr;
    }

    .emotion-panel {
        height: auto;
        max-height: 300px;
    }
}

/* 移除: 面板控制按钮样式（已迁移到视频控制栏） */
/* .panel-controls 相关样式已删除 */
</style>
