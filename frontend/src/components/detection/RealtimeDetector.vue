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
                <div class="panel-controls">
                    <el-tooltip content="情感识别" placement="top">
                        <el-button :icon="MagicStick" :type="isEmotionDetectionOn ? 'primary' : 'default'"
                            @click="toggleEmotionDetection" circle size="small" />
                    </el-tooltip>
                    <el-tooltip content="麦克风输入" placement="top">
                        <el-button :icon="Microphone" :class="['mic-button', { 'mic-active': isMicOn }]"
                            @click="toggleMicrophone" circle size="small" />
                    </el-tooltip>
                    <el-tooltip content="反馈识别结果" placement="top" v-if="currentEmotion">
                        <el-button :icon="Edit" @click="showFeedback = true" circle size="small" />
                    </el-tooltip>
                </div>
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

                <!-- ✅ 修改: 移除 hasVoiceData 条件，避免闪烁 -->
                <div v-if="isMicOn" class="voice-indicator">
                    <span class="voice-icon"></span>
                    <span class="voice-text">{{ isFused ? '多模态融合' : '仅视觉检测' }}</span>
                    <span class="voice-badge">{{ isFused ? '语音+视觉' : '仅视觉' }}</span>

                    <!-- ✅ 新增: 音频活动指示器 -->
                    <div class="audio-activity-bar">
                        <div class="audio-activity-fill" :style="{ width: `${audioActivityLevel * 100}%` }"></div>
                    </div>
                </div>

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

                <!-- ✅ 修改: 移除 hasVoiceData 条件，避免闪烁 -->
                <div v-if="isMicOn" class="voice-emotion-section">
                    <div class="voice-emotion-title">
                        <span class="voice-icon-small">🎤</span>
                        <span>语音情绪分析</span>
                    </div>
                    <div class="confidence-bars voice-bars">
                        <!-- ✅ 修改: 按照 emotionList 顺序显示，保持与上方一致 -->
                        <div v-for="emotion in emotionList" :key="emotion" class="confidence-bar-item voice-bar-item">
                            <span class="bar-label">
                                <EmotionSVG :emotion="emotion" size="small" :animated="false" />
                                {{ getEmotionName(emotion) }}
                            </span>
                            <div class="bar-track">
                                <div class="bar-fill voice-fill" :style="{
                                    width: `${(voiceScores[emotion] || 0) * 100}%`,
                                    background: getEmotionColor(emotion),
                                    boxShadow: `0 0 8px ${getEmotionColor(emotion)}`
                                }"></div>
                            </div>
                            <span class="bar-value">{{ ((voiceScores[emotion] || 0) * 100).toFixed(0) }}%</span>
                        </div>
                    </div>
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

        <!-- ✅ 新增: 情绪反馈对话框 -->
        <EmotionFeedback v-model:visible="showFeedback" :predicted-emotion="currentEmotion"
            :predicted-confidence="currentConfidence" @submitted="handleFeedbackSubmitted" />
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, reactive, computed } from 'vue'
import { VideoCamera, VideoPlay, MagicStick, Microphone, Edit } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useThemeStore } from '@/stores/theme'
import { getEmotionName, getEmotionColor, getEmotionEmoji } from '@/utils/emotion'
import { drawCornerBox, drawEmotionLabel } from '@/utils/canvas'
import wsManager from '@/api/websocket'
import EmotionSVG from '@/components/common/EmotionSVG.vue'
import { logFeatureUsage } from '@/utils/analytics'
import httpMonitor from '@/utils/httpMonitor'
import AudioCapture from '@/utils/audioCapture'
import { API } from '@/api/config'
import PerformanceMonitor from '@/components/monitor/PerformanceMonitor.vue'
import EmotionFeedback from '@/components/feedback/EmotionFeedback.vue'

const themeStore = useThemeStore()
const videoElement = ref(null)
const canvasElement = ref(null)
const videoContainer = ref(null)
const isCameraOn = ref(false)
const isEmotionDetectionOn = ref(true)
const currentEmotion = ref(null)
const currentConfidence = ref(0)
const showFeedback = ref(false)  // ✅ 新增: 反馈对话框显示状态
// const hasVoiceData = ref(false)  // ✅ 已移除: 未使用的变量
const isFused = ref(false)  // ✅ 新增: 标记是否是多模态融合结果
const emotionScores = ref({})
const voiceScores = ref({})  // ✅ 新增: 语音情绪分数
const visionScores = ref({})  // ✅ 新增: 视觉情绪分数（融合前）

// ✅ 修复: 暴露 voiceScores 为响应式变量
const exposedVoiceScores = computed(() => voiceScores.value)
const currentFaces = ref([])
const fps = ref(0)
// ✅ 新增: 麦克风控制
const isMicOn = ref(false)
const audioActivityLevel = ref(0)  // ✅ 新增: 音频活动级别 (0-1)
let lastAudioSendTime = 0  // ✅ 新增: 上次发送音频的时间
const audioCapture = new AudioCapture({
    sampleRate: 16000,
    compressionEnabled: false,  // 禁用音频压缩，直接发送原始PCM16数据
    bufferSize: 16000,  // ✅ 优化: 1 秒缓冲（16kHz * 1.0 = 16000 样本），提高识别准确率
    onAudioData: (pcmData) => {
        // ✅ 修复: 通过 WebSocket 发送批量音频数据
        if (wsManager.isConnected && pcmData.byteLength > 0) {
            try {
                // 添加类型标识，避免与视频帧混淆
                // 格式: [type(1B)] + [audio_data]
                const typeByte = new Uint8Array([0x02]) // 0x01=video, 0x02=audio
                const combined = new Uint8Array(typeByte.length + pcmData.byteLength)
                combined.set(typeByte, 0)
                combined.set(new Uint8Array(pcmData), typeByte.length)
                wsManager.sendBinary(combined.buffer)

                // ✅ 优化: 更新音频活动指示器（使用平滑算法）
                const int16View = new Int16Array(pcmData)
                const volume = int16View.reduce((sum, val) => sum + Math.abs(val), 0) / int16View.length
                // 使用 EMA 平滑，避免跳动
                audioActivityLevel.value = audioActivityLevel.value * 0.7 + Math.min(1, volume / 5000) * 0.3
                lastAudioSendTime = performance.now()
            } catch (error) {
                console.error(' 发送批量音频数据失败:', error)
            }
        }
    }
})
// ✅ 修复: 情绪列表（7种情绪，calm 合并到 neutral）
const emotionList = ['happy', 'sad', 'angry', 'surprised', 'fearful', 'disgust', 'neutral']

// ✅ 新增: 情绪分数排序计算属性（从高到低）
const sortedEmotionScores = computed(() => {
    return Object.entries(emotionScores.value)
        .map(([emotion, score]) => ({ emotion, score }))
        .sort((a, b) => b.score - a.score)  // 降序排序
})
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

    // ✅ 新增: 音频活动指示器衰减定时器（每100ms衰减一次）
    const audioActivityInterval = setInterval(() => {
        if (isMicOn.value && audioActivityLevel.value > 0) {
            // 如果超过 500ms 没有新的音频数据，快速衰减
            if (performance.now() - lastAudioSendTime > 500) {
                audioActivityLevel.value *= 0.7  // 快速衰减
                if (audioActivityLevel.value < 0.01) {
                    audioActivityLevel.value = 0
                }
            } else {
                audioActivityLevel.value *= 0.95  // 慢速衰减
            }
        }
    }, 100)

    // 组件卸载时清除定时器
    onUnmounted(() => {
        clearInterval(httpMonitorInterval)
        clearInterval(audioActivityInterval)
    })
})

onUnmounted(() => {
    stopCamera()
    // ✅ 优化: 清理 Canvas 防止内存泄漏
    cleanupCanvas()

    // ✅ 新增: 清理防抖定时器
    if (saveHistoryDebounceTimer) {
        clearTimeout(saveHistoryDebounceTimer)
        saveHistoryDebounceTimer = null
    }
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

// ✅ 新增: 动态分辨率调整
const adjustResolution = () => {
    const avgFps = fps.value
    let newResolution = currentResolution

    if (avgFps < 10 && currentResolution !== SEND_RESOLUTIONS.low) {
        newResolution = SEND_RESOLUTIONS.low
        console.log('📉 检测到FPS过低,降低分辨率以提升性能')
    } else if (avgFps >= 10 && avgFps <= 20 && currentResolution !== SEND_RESOLUTIONS.medium) {
        newResolution = SEND_RESOLUTIONS.medium
        console.log('⚖️ FPS适中,使用标准分辨率')
    } else if (avgFps > 20 && currentResolution !== SEND_RESOLUTIONS.high) {
        newResolution = SEND_RESOLUTIONS.high
        console.log('📈 FPS良好,提高分辨率以提升精度')
    }

    if (newResolution !== currentResolution) {
        currentResolution = newResolution
        // 重新初始化sendCanvas
        sendCanvas = null
        initSendCanvas()
    }
}

// ✅ 新增: 麦克风控制
const toggleMicrophone = async () => {
    if (isMicOn.value) {
        audioCapture.stop()
        isMicOn.value = false
        ElMessage({
            message: '🎤 麦克风已关闭',
            type: 'info',
            duration: 2000
        })
    } else {
        // ✅ 优化: 先检查WebSocket连接状态
        if (!wsManager.isConnected) {
            ElMessage.warning('⚠️ WebSocket未连接，无法使用麦克风功能')
            return
        }

        // ✅ 优化: 异步启动，避免阻塞检测
        try {
            const success = await audioCapture.start()
            if (success) {
                isMicOn.value = true
                ElMessage({
                    message: '✅ 麦克风已开启 | 多模态语音情绪融合分析中...',
                    type: 'success',
                    duration: 3000,
                    showClose: true
                })
            } else {
                ElMessage.error('❌ 无法访问麦克风，请检查权限设置')
            }
        } catch (error) {
            console.error('麦克风启动失败:', error)
            ElMessage.error('❌ 麦克风启动失败，请重试')
        }
    }
}

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

// ✅ 新增: 防抖保存历史记录（避免频繁调用）
let saveHistoryDebounceTimer = null
const SAVE_HISTORY_INTERVAL = 5000  // 每 5 秒保存一次

const handleWsMessage = (data) => {
    if (data.type !== 'result') return

    // ✅ 已移除: hasVoiceData.value = data.has_voice_data || false （未使用）

    updateInferenceFps()  // 统计 AI 推理帧率

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

    // 接收语音情绪分数（无论是否检测到人脸都更新）
    if (data.voice_scores) {
        voiceScores.value = data.voice_scores
    }

    // 过滤掉低置信度的缓存结果（置信度 < 0.6 视为无效）
    const validFaces = data.faces?.filter(face => face.confidence >= 0.6 && !face._cached) || []

    if (validFaces.length) {
        const rawScores = validFaces[0].scores

        // ✅ 新增: 接收视觉情绪分数（融合前）
        if (validFaces[0].vision_scores) {
            visionScores.value = validFaces[0].vision_scores
        }

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

        // ✅ 新增: 检查是否是多模态融合结果
        isFused.value = validFaces[0].is_fused || false

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

        // ✅ 新增: 自动保存历史记录（防抖：每 5 秒保存一次）
        if (!_analyticsLogged) {
            _analyticsLogged = true
            logFeatureUsage('实时检测', { emotion: smoothedEmotion })
        }

        // 触发防抖保存
        if (saveHistoryDebounceTimer) {
            clearTimeout(saveHistoryDebounceTimer)
        }
        saveHistoryDebounceTimer = setTimeout(() => {
            saveRealtimeToHistory(smoothedEmotion, smoothedConf, validFaces)
        }, SAVE_HISTORY_INTERVAL)
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

// ✅ 新增: 处理反馈提交成功
const handleFeedbackSubmitted = () => {
    // 反馈提交后，可以在这里添加一些额外逻辑
    // 比如记录反馈统计、显示学习进度等
    console.log('✅ 用户反馈已提交，系统将自动学习优化')
}

// ✅ 新增: 保存实时检测历史记录
const saveRealtimeToHistory = async (emotion, confidence, faces) => {
    try {
        const canvas = canvasElement.value
        if (!canvas) {
            console.warn('⚠️ Canvas 元素未找到，无法保存历史记录')
            return
        }

        // 截取当前 Canvas 帧作为缩略图（压缩到 320x240）
        const thumbnailCanvas = document.createElement('canvas')
        const thumbCtx = thumbnailCanvas.getContext('2d')
        thumbnailCanvas.width = 320
        thumbnailCanvas.height = 240

        // 保持宽高比
        const scale = Math.min(320 / canvas.width, 240 / canvas.height)
        const scaledWidth = canvas.width * scale
        const scaledHeight = canvas.height * scale
        const offsetX = (320 - scaledWidth) / 2
        const offsetY = (240 - scaledHeight) / 2

        thumbCtx.fillStyle = '#000'  // 黑色背景
        thumbCtx.fillRect(0, 0, 320, 240)
        thumbCtx.drawImage(canvas, offsetX, offsetY, scaledWidth, scaledHeight)

        // 转换为 JPEG 格式（质量 0.7）
        const thumbnail = thumbnailCanvas.toDataURL('image/jpeg', 0.7)

        // 构建保存数据
        const historyData = {
            detection_type: 'realtime',
            results: [{
                emotion: emotion,
                confidence: confidence,
                bbox: faces[0]?.bbox || [0, 0, 0, 0]
            }],
            source: '摄像头实时检测',
            image_path: '',
            image_type: 'realtime',
            thumbnail: thumbnail,
            dominant_emotion: emotion,
            confidence: confidence,
            detected_faces: faces.map(face => ({
                bbox: face.bbox,
                emotion: face.emotion,
                confidence: face.confidence,
                scores: face.scores
            }))
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
            console.warn('⚠️ 保存历史记录失败:', response.statusText)
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
    /* font-weight: 600; */
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
    /* font-weight: 600; */
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
    /* ✅ 修复: 移除 overflow-y，让内部元素管理滚动 */
    overflow-y: visible;
    display: flex;
    flex-direction: column;
    /* ✅ 优化: 减小最小高度，避免内容少时出现大片空白 */
    min-height: 350px;
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
    overflow-y: auto;
    animation: fadeIn 0.3s ease;
    /* ✅ 优化: 动态最大高度，根据视口调整 */
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
    /* font-weight: 600; */
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
    /* font-weight: 600; */
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
    /* ✅ 优化: 减小最大高度，更紧凑 */
    max-height: 250px;
    overflow-y: auto;
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
    /* font-weight: 600; */
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

.no-detection {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 10px;
    color: var(--text-secondary);
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

/* 麦克风按钮样式 */
.mic-button {
    background: rgba(13, 6, 27, 0.5) !important;
    border: 1px solid rgba(156, 78, 255, 0.2) !important;
    color: var(--text) !important;
    transition: all 0.3s ease !important;
}

/* 修改所有圆形按钮的圆角 */
:deep(.el-button.is-circle) {
    border-radius: 25% !important;
}

.mic-button:hover {
    background: rgba(113, 57, 255, 0.15) !important;
    border-color: var(--primary) !important;
    color: var(--primary-light) !important;
    transform: translateY(-1px);
}

.mic-button.mic-active {
    background: linear-gradient(135deg, var(--primary), #9B59B6) !important;
    border: none !important;
    color: var(--text) !important;
    box-shadow: 0 0 12px rgba(113, 57, 255, 0.6), 0 0 20px rgba(113, 57, 255, 0.3) !important;
    animation: micPulse 2s ease-in-out infinite;
}

.mic-button.mic-active:hover {
    box-shadow: 0 0 16px rgba(113, 57, 255, 0.8), 0 0 24px rgba(113, 57, 255, 0.4) !important;
}

@keyframes micPulse {

    0%,
    100% {
        box-shadow: 0 0 12px rgba(113, 57, 255, 0.6), 0 0 20px rgba(113, 57, 255, 0.3);
    }

    50% {
        box-shadow: 0 0 16px rgba(113, 57, 255, 0.8), 0 0 28px rgba(113, 57, 255, 0.4);
    }
}
</style>
