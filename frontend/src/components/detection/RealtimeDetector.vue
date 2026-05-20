<template>
    <div class="realtime-page">
        <!-- 视频区域 -->
        <div class="video-section">
            <div class="video-container glass-panel" ref="videoContainer">
                <video ref="videoElement" autoplay playsinline style="display:none"></video>
                <canvas ref="canvasElement" class="video-canvas" :class="{ 'camera-switch-transition': isSwitchingCamera }"></canvas>
                <!-- 摄像头切换过渡遮罩 -->
                <div v-if="isSwitchingCamera" class="camera-transition-overlay">
                    <div class="transition-content">
                        <div class="transition-icon">
                            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="transition-spinner">
                                <path d="M21 12a9 9 0 1 1-6.219-8.56" />
                            </svg>
                        </div>
                        <span class="transition-text">切换摄像头中...</span>
                    </div>
                </div>

                <!-- 摄像头启动加载遮罩 -->
                <div v-if="isLoading" class="camera-loading-overlay">
                    <div class="loading-content">
                        <div class="loading-icon">
                            <el-icon :size="48" class="spinner"><Loading /></el-icon>
                        </div>
                        <span class="loading-text">连接中...</span>
                    </div>
                </div>

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

                    <!-- ✅ 新增: 摄像头切换下拉菜单 -->
                    <div class="ctrl-divider"></div>
                    <el-dropdown 
                        trigger="click" 
                        @command="switchCamera"
                        placement="bottom-end"
                    >
                        <div class="camera-switch-wrapper" :class="{ 'switching': isSwitchingCamera }">
                            <div class="camera-icon-wrapper">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                    stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="camera-icon">
                                    <path d="M15 10l4.553-2.276A1 1 0 0 1 21 8.618v6.764a1 1 0 0 1-1.447.894L15 14M6 18H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2m5.658 0L12 2.342a1 1 0 0 1 1.707 0L14.342 4M6 18a2 2 0 0 0 2 2h2.342a1 1 0 0 1 .707 1.293l1.314 2.626a1 1 0 0 1-.553 1.361l-2.573 1.286a11.042 11.042 0 0 1-5.516 0l-2.573-1.286a1 1 0 0 1-.553-1.361l1.314-2.626A1 1 0 0 1 6.342 20H8a2 2 0 0 0 2-2z" />
                                </svg>
                                <!-- 切换时的加载动画 -->
                                <div v-if="isSwitchingCamera" class="camera-loading">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                        stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="loading-spinner">
                                        <path d="M21 12a9 9 0 1 1-6.219-8.56" />
                                    </svg>
                                </div>
                            </div>
                            <transition name="camera-switch" mode="out-in">
                                <span :key="currentCameraIndex" class="camera-name">{{ cameras[currentCameraIndex]?.label || '摄像头' }}</span>
                            </transition>
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="camera-arrow">
                                <path d="M6 9l6 6 6-6" />
                            </svg>
                        </div>
                        <template #dropdown>
                            <el-dropdown-menu class="camera-dropdown-menu">
                                <el-dropdown-item 
                                    v-for="(camera, index) in cameras" 
                                    :key="index" 
                                    :command="index"
                                    class="camera-dropdown-item"
                                >
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                        stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="camera-item-icon">
                                        <path d="M15 10l4.553-2.276A1 1 0 0 1 21 8.618v6.764a1 1 0 0 1-1.447.894L15 14M6 18H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2m5.658 0L12 2.342a1 1 0 0 1 1.707 0L14.342 4M6 18a2 2 0 0 0 2 2h2.342a1 1 0 0 1 .707 1.293l1.314 2.626a1 1 0 0 1-.553 1.361l-2.573 1.286a11.042 11.042 0 0 1-5.516 0l-2.573-1.286a1 1 0 0 1-.553-1.361l1.314-2.626A1 1 0 0 1 6.342 20H8a2 2 0 0 0 2-2z" />
                                    </svg>
                                    <span :class="{ 'camera-item-active': index === currentCameraIndex }">
                                        <span v-if="index === currentCameraIndex" class="camera-check">✓</span>
                                        <span v-else class="camera-dot">○</span>
                                    </span>
                                    <span class="camera-item-label">{{ camera.label }}</span>
                                </el-dropdown-item>
                            </el-dropdown-menu>
                        </template>
                    </el-dropdown>

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
            <!-- 上半部分：实时分析内容 -->
            <div class="panel-upper">
                <div class="panel-header">
                    <h3>
                        <span class="panel-icon"><el-icon>
                                <DataAnalysis />
                            </el-icon></span>
                        <span>实时分析</span>
                    </h3>
                </div>

                <!-- 摄像头未启动状态 -->
                <div v-if="!isCameraOn" class="no-detection">
                    <EmotionSVG emotion="neutral" size="large" :animated="false" />
                    <p class="status-hint">请启动摄像头</p>
                    <p class="status-sub">点击左侧"启动摄像头"按钮开始检测</p>
                </div>

                <!-- 摄像头已启动 -->
                <template v-else>
                    <!-- 检测到人脸 -->
                    <div v-if="currentFaces.length > 0" class="emotion-display">
                        <!-- 多人脸标签 -->
                        <div v-if="currentFaces.length > 1" class="multi-face-badge">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                                <circle cx="9" cy="7" r="4"/>
                                <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                                <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                            </svg>
                            检测到 {{ currentFaces.length }} 张人脸
                        </div>

                        <!-- 人脸卡片列表 -->
                        <div class="face-cards-list">
                            <div v-for="(face, index) in currentFaces" :key="index" class="face-card"
                                :style="{ '--face-color': getEmotionColor(face.emotion) }">
                                <div class="face-card-number">人脸 {{ index + 1 }}</div>
                                <div class="face-card-row">
                                    <span class="face-card-emoji">{{ getEmotionEmoji(face.emotion) }}</span>
                                    <span class="face-card-emotion-name">{{ getEmotionName(face.emotion) }}</span>
                                    <div class="face-card-bar-track">
                                        <div class="face-card-bar-fill" :style="{ width: `${face.confidence * 100}%` }"></div>
                                    </div>
                                    <span class="face-card-bar-value">{{ (face.confidence * 100).toFixed(1) }}%</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 等待状态 -->
                    <div v-else class="no-detection">
                        <EmotionSVG emotion="neutral" size="large" :animated="false" />
                        <p class="status-hint">等待人脸检测...</p>
                        <p class="status-sub">将脸部对准摄像头，系统将自动分析</p>
                    </div>
                </template>
            </div>

            <!-- 下半部分：情绪趋势图表 -->
            <div class="panel-lower">
                <div class="emotion-trend-section">
                    <div class="trend-section-header">
                        <h4>
                            <span class="section-icon"><el-icon><TrendCharts /></el-icon></span>
                            <span>情绪趋势</span>
                        </h4>
                    </div>
                    <div class="trend-chart-wrapper">
                        <EmotionLineChart v-if="!isMultiFace" :emotion-history="emotionHistory" />
                        <MultiFaceEmotionChart v-else :face-histories="faceEmotionHistories" />
                    </div>
                </div>
            </div>
        </div>

        <!-- ✅ 新增: 性能监控面板（真实数据） -->
        <PerformanceMonitor 
            :camera-fps="perfFps" 
            :inference-time="perfInferenceTime" 
            :detection-latency="perfDetectionLatency" 
            :network-latency="perfNetworkLatency" 
            :is-using-gpu="isUsingGpu" 
        />

        <!-- ✅ 新增: 情绪反馈对话框（静态快照） -->
        <EmotionFeedback v-model:visible="showFeedback" :snapshot="feedbackSnapshot"
            @submitted="handleFeedbackSubmitted" />
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, onActivated, onDeactivated, reactive, computed } from 'vue'
import { VideoCamera, VideoPlay, Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useThemeStore } from '@/stores/theme'
import { useDetectionStore } from '@/stores/detection'
import { getEmotionName, getEmotionColor, getEmotionEmoji, EMOTION_KEYS } from '@/constants/emotions'
import { drawCornerBox, drawEmotionLabel } from '@/utils/canvas'
import wsManager from '@/api/websocket'
import EmotionSVG from '@/components/common/EmotionSVG.vue'
import { logFeatureUsage } from '@/utils/analytics'
import { getSystemConfig, submitFeedback } from '@/api/modules/system'
import { saveHistoryRecord } from '@/api/modules/history'
import { analyzeEmotionTrend } from '@/api/modules/analytics'
import generativeAudio from '@/utils/generativeAudio'
import PerformanceMonitor from '@/components/monitor/PerformanceMonitor.vue'
import EmotionFeedback from '@/components/feedback/EmotionFeedback.vue'
import EmotionLineChart from '@/components/charts/EmotionLineChart.vue'
import MultiFaceEmotionChart from '@/components/charts/MultiFaceEmotionChart.vue'
import EmotionTrendPanel from '@/components/analysis/EmotionTrendPanel.vue'
import { TrendCharts } from '@element-plus/icons-vue'
import logger from '@/utils/logger'
import { analyze3SecondWindow, prepareBackendData } from '@/utils/emotionTrendAnalyzer'
import { workerDetectionService } from '@/services/workerDetection'

// ✅ 新增: 组件名称,用于 keep-alive 缓存
defineOptions({
    name: 'RealtimeDetector'
})

const themeStore = useThemeStore()
const detectionStore = useDetectionStore()  // 新增：检测状态store
const videoElement = ref(null)
const canvasElement = ref(null)
const videoContainer = ref(null)
const isCameraOn = ref(false)
// ✅ 新增: 摄像头切换相关变量
const cameras = ref([])  // 可用摄像头列表
const currentCameraIndex = ref(0)  // 当前选中的摄像头索引
const isSwitchingCamera = ref(false)  // 摄像头切换中状态
const isLoading = ref(false)  // 摄像头启动加载中状态
const isEmotionDetectionOn = ref(true)
const detectionMode = ref('websocket') // 'websocket' | 'worker'
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
const emotionList = EMOTION_KEYS

// ✅ 新增: 情绪历史数据（用于趋势曲线图）
const emotionHistory = ref([])  // [{ timestamp, emotions: { happy: 0.8, ... } }]
const faceEmotionHistories = ref({})  // { 0: [{ timestamp, emotion, confidence }], 1: [...] }
const HISTORY_MAX_LENGTH = 60  // 最多保存60秒的数据
let historyTimer = null  // 定时器，每秒记录一次

// ✅ 新增: 情绪趋势分析数据
const trendAnalysis = ref({})
const textAnalysis = ref({})
const comprehensiveAnalysis = ref({})
const showTrendPanel = ref(true)
let trendAnalysisTimer = null  // 情绪趋势分析定时器

// ✅ 新增: 计算所有检测人脸的平均情绪分数（用于图表）
const getAverageScores = (faces) => {
    if (!faces || faces.length === 0) return {}
    const avgScores = {}
    const emotionKeys = EMOTION_KEYS
    emotionKeys.forEach(key => { avgScores[key] = 0 })
    let validFaceCount = 0
    faces.forEach(face => {
        if (face.scores && typeof face.scores === 'object') {
            validFaceCount++
            emotionKeys.forEach(key => {
                avgScores[key] += face.scores[key] || 0
            })
        }
    })
    if (validFaceCount > 0) {
        emotionKeys.forEach(key => {
            avgScores[key] /= validFaceCount
        })
    }
    return avgScores
}

// ✅ 新增: 启动情绪历史记录定时器
const startHistoryTimer = () => {
    if (historyTimer) return
    historyTimer = setInterval(() => {
        if (currentEmotion.value && emotionScores.value) {
            const record = {
                timestamp: Date.now(),
                emotions: { ...emotionScores.value }
            }
            emotionHistory.value.push(record)
            if (emotionHistory.value.length > HISTORY_MAX_LENGTH) {
                emotionHistory.value = emotionHistory.value.slice(-HISTORY_MAX_LENGTH)
            }
        }
        if (currentFaces.value.length > 1) {
            const newHistories = { ...faceEmotionHistories.value }
            currentFaces.value.forEach((face, index) => {
                if (!newHistories[index]) newHistories[index] = []
                newHistories[index].push({
                    timestamp: Date.now(),
                    emotion: face.emotion,
                    confidence: face.confidence
                })
                if (newHistories[index].length > HISTORY_MAX_LENGTH) {
                    newHistories[index] = newHistories[index].slice(-HISTORY_MAX_LENGTH)
                }
            })
            const activeIds = new Set(currentFaces.value.map((_, i) => i))
            Object.keys(newHistories).forEach(key => {
                if (!activeIds.has(Number(key))) {
                    delete newHistories[key]
                }
            })
            faceEmotionHistories.value = newHistories
        } else {
            faceEmotionHistories.value = {}
        }
    }, 1000)
}

// ✅ 新增: 停止情绪历史记录定时器
const stopHistoryTimer = () => {
    if (historyTimer) {
        clearInterval(historyTimer)
        historyTimer = null
    }
}

// ✅ 新增: 清空情绪历史
const clearEmotionHistory = () => {
    emotionHistory.value = []
    faceEmotionHistories.value = {}
}

// ✅ 新增: 启动情绪趋势分析定时器
const startTrendAnalysisTimer = () => {
    if (trendAnalysisTimer) return
    trendAnalysisTimer = setInterval(() => {
        if (emotionHistory.value.length >= 3) {
            performTrendAnalysis()
        }
    }, 2000)  // 每2秒分析一次
}

// ✅ 新增: 停止情绪趋势分析定时器
const stopTrendAnalysisTimer = () => {
    if (trendAnalysisTimer) {
        clearInterval(trendAnalysisTimer)
        trendAnalysisTimer = null
    }
}

// ✅ 新增: 执行情绪趋势分析
const performTrendAnalysis = async () => {
    try {
        const currentEmotionData = {
            emotion: currentEmotion.value,
            confidence: currentConfidence.value,
            scores: emotionScores.value
        }

        const windowAnalysis = analyze3SecondWindow(emotionHistory.value, currentEmotionData)

        if (windowAnalysis.hasData && windowAnalysis.dataPoints >= 3) {
            const backendData = prepareBackendData(windowAnalysis)

            const result = await analyzeEmotionTrend(backendData)

            if (result.status === 'success') {
                trendAnalysis.value = result.emotion_trend_analysis
                textAnalysis.value = result.text_analysis
                comprehensiveAnalysis.value = result.comprehensive_analysis
            }
        }
    } catch (error) {
        logger.error('情绪趋势分析失败:', error)
    }
}
const currentFaces = ref([])
const isMultiFace = computed(() => currentFaces.value.length > 1)
const fps = ref(0)
// ✅ 新增: 性能监控数据（真实数据）
const perfLatency = ref(0)
const perfSkipRate = ref(0)
const perfGpuMemory = ref(0)
const perfDetectInterval = ref(2)
// ✅ 新增: HTTP延迟和错误率
const perfHttpLatency = ref(0)
const perfErrorRate = ref(0)

// ✅ 真实帧率测量（基于渲染帧时间）
const perfFps = ref(0)
const _frameTimestamps = []
const _MAX_FRAME_HISTORY = 60

// ✅ 新增: 真实性能数据
const perfInferenceTime = ref(0)    // 模型推理时间(ms)
const perfDetectionLatency = ref(0) // 检测延迟(ms)
const perfNetworkLatency = ref(0)   // 网络延迟(Ping)(ms)
const isUsingGpu = ref(false)       // 是否使用GPU

// ✅ 真实跳帧率计算（基于实际帧计数）
let _totalFramesProcessed = 0
let _totalFramesReceived = 0

// ✅ 新增: 错误计数（用于计算错误率）
let errorCount = 0
let totalFrames = 0

// ✅ 新增: 动态分辨率策略
const SEND_RESOLUTIONS = {
    low: { width: 128, height: 96 },      // FPS < 10
    medium: { width: 160, height: 120 },  // FPS 10-20
    high: { width: 224, height: 168 }     // FPS > 20
}
let currentResolution = SEND_RESOLUTIONS.medium

// ✅ 新增: 最大检测人脸数量（从系统配置读取）
let maxDetectFaces = 10
let lastAdjustTime = 0
let lastSaveTime = 0  // ✅ 新增: 上次保存时间戳,防止重复保存
const SAVE_COOLDOWN = 2000  // ✅ 新增: 保存冷却时间(2秒)

// ✅ 新增: 性能模式配置（三级模式）
let performanceModeConfig = {
    send_width: 160,
    send_height: 120,
    frame_skip_threshold: 2,
    ema_alpha: 0.25,
    enable_realtime_charts: true,
    use_gpu: false  // ✅ 是否使用GPU
}

// ✅ 新增: 加载性能模式配置（支持三级模式）
const loadPerformanceConfig = async () => {
    try {
        const data = await getSystemConfig()
        const perfMode = data.config.performance_mode || 'cpu_high'
        
        // ✅ 新增: 获取最大检测人脸数量配置
        const maxFaces = data.config.max_faces
        if (maxFaces !== undefined && maxFaces !== null) {
            maxDetectFaces = maxFaces
        }

        // ✅ 三级模式配置（gpu/cpu_high/cpu_low）
        if (perfMode === 'gpu') {
            currentResolution = { width: 320, height: 240 }
            performanceModeConfig.frame_skip_threshold = 2
            performanceModeConfig.use_gpu = true
            performanceModeConfig.ema_alpha = 0.25
        } else if (perfMode === 'cpu_high') {
            currentResolution = { width: 256, height: 192 }
            performanceModeConfig.frame_skip_threshold = 3
            performanceModeConfig.use_gpu = false
            performanceModeConfig.ema_alpha = 0.2
        } else if (perfMode === 'cpu_low') {
            currentResolution = { width: 128, height: 96 }
            performanceModeConfig.frame_skip_threshold = 5
            performanceModeConfig.use_gpu = false
            performanceModeConfig.ema_alpha = 0.15
        }

        // ✅ 更新 GPU 状态（用于性能监控面板显示）
        isUsingGpu.value = performanceModeConfig.use_gpu === true

        // ✅ 新增: 重新初始化发送 Canvas
        if (sendCanvas) {
            sendCanvas.width = currentResolution.width
            sendCanvas.height = currentResolution.height
            
        }
    } catch (error) {
        logger.error('加载性能模式配置失败:', error)
    }
}

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

// === 情绪状态（后端已做EMA平滑，前端直接使用） ===
let _consecutiveEmpty = 0
const EMPTY_THRESHOLD = 10
let _lastGoodEmotion = null
let _lastGoodScores = {}
let _adaptiveQuality = 0.5
let _roundTripHistory = []
let _themeChangeTimer = null
let _analyticsLogged = false
let _lastFaceUpdate = 0
let _smoothedBbox = {}
let _prevBboxes = {}  // 存储上一帧的原始bbox用于IoU匹配
const BBOX_SMOOTH_ALPHA = 0.3  // ✅ 降低alpha值，增加平滑效果（0.3表示70%权重给历史值）
const BBOX_VELOCITY_DAMPING = 0.6  // 速度阻尼系数
let _lastDetectionTime = 0  // 上次检测时间戳
let _targetBbox = {}  // 目标bbox（最新检测结果）
let _renderBbox = {}  // 渲染用的插值bbox
let _nextFaceId = 0

function _computeIoU(boxA, boxB) {
  const [ax1, ay1, aw, ah] = boxA
  const [bx1, by1, bw, bh] = boxB
  const ax2 = ax1 + aw, ay2 = ay1 + ah
  const bx2 = bx1 + bw, by2 = by1 + bh
  const ix1 = Math.max(ax1, bx1), iy1 = Math.max(ay1, by1)
  const ix2 = Math.min(ax2, bx2), iy2 = Math.min(ay2, by2)
  const iw = Math.max(0, ix2 - ix1), ih = Math.max(0, iy2 - iy1)
  const inter = iw * ih
  const union = aw * ah + bw * bh - inter
  return union > 0 ? inter / union : 0
}

function _matchFacesByIoU(prevBboxes, currFaces, iouThreshold = 0.3) {
  const prevIds = Object.keys(prevBboxes).map(Number)
  if (prevIds.length === 0) {
    const matches = {}
    currFaces.forEach((_, i) => { matches[i] = _nextFaceId++ })
    return matches
  }

  const pairs = []
  currFaces.forEach((face, ci) => {
    prevIds.forEach(pid => {
      const iou = _computeIoU(prevBboxes[pid], face.bbox)
      if (iou > iouThreshold) {
        pairs.push({ iou, pid, ci })
      }
    })
  })

  pairs.sort((a, b) => b.iou - a.iou)

  const matches = {}
  const usedPrev = new Set()
  const usedCurr = new Set()

  pairs.forEach(({ pid, ci }) => {
    if (!usedPrev.has(pid) && !usedCurr.has(ci)) {
      matches[ci] = pid
      usedPrev.add(pid)
      usedCurr.add(ci)
    }
  })

  currFaces.forEach((_, ci) => {
    if (!(ci in matches)) {
      matches[ci] = _nextFaceId++
    }
  })

  return matches
}
let _fadeOutActive = false
let _fadeOutStartTime = 0
const FADE_OUT_DURATION = 500
let lastLoadedPerfMode = 'high'
let _configCheckInterval = null

const startIntervals = () => {
    stopIntervals()

    _configCheckInterval = setInterval(async () => {
        try {
            const data = await getSystemConfig()
            const currentMode = data.config.performance_mode || 'high'

            if (currentMode !== lastLoadedPerfMode) {
                
                lastLoadedPerfMode = currentMode
                await loadPerformanceConfig()
            }
        } catch (error) {
        }
    }, 30000)
}

const stopIntervals = () => {
    if (_configCheckInterval) {
        clearInterval(_configCheckInterval)
        _configCheckInterval = null
    }
}

onMounted(() => {
    wsManager.onConnect(() => {})
    wsManager.onMessage(handleWsMessage)
    wsManager.onDisconnect(() => {
        awaitingResult = false
        currentFaces.value = []
        currentEmotion.value = null
    })

    loadPerformanceConfig()
    startIntervals()
})

onUnmounted(() => {
    stopCamera()
    cleanupCanvas()
    stopIntervals()
})

// ✅ 新增: keep-alive 缓存时的生命周期
onDeactivated(() => {
    
    stopCamera()
    stopIntervals()
})

onActivated(() => {
    
    startIntervals()
})

// ✅ 新增: Canvas 清理函数
const cleanupCanvas = () => {
    if (sendCanvas) {
        sendCtx = null
        sendCanvas = null
    }
}

// === 摄像头控制 ===

// ✅ 新增: 枚举可用摄像头
const enumerateCameras = async () => {
    try {
        const devices = await navigator.mediaDevices.enumerateDevices()
        const videoDevices = devices.filter(device => device.kind === 'videoinput')
        cameras.value = videoDevices.map((device, index) => ({
            id: device.deviceId,
            label: device.label || `摄像头 ${index + 1}`,
            deviceId: device.deviceId
        }))
        
    } catch (error) {
        logger.error('枚举摄像头失败:', error)
        cameras.value = [{ id: 'default', label: '默认摄像头', deviceId: '' }]
    }
}

// ✅ 新增: 切换摄像头
const switchCamera = async (index) => {
    if (index === currentCameraIndex.value || isSwitchingCamera.value || isLoading.value) return
    
    isSwitchingCamera.value = true
    isLoading.value = true
    currentCameraIndex.value = index
    
    try {
        const camera = cameras.value[index]
        if (!camera) return

        // 停止当前流
        if (stream) {
            stream.getTracks().forEach(t => t.stop())
            stream = null
        }

        // 启动新摄像头
        const constraints = { 
            video: { 
                deviceId: camera.deviceId ? { exact: camera.deviceId } : undefined 
            } 
        }
        
        stream = await navigator.mediaDevices.getUserMedia(constraints)
        
        if (videoElement.value) {
            videoElement.value.srcObject = stream
            await videoElement.value.play()
        }
        
        ElMessage.success(`已切换到 ${camera.label}`)
    } catch (error) {
        logger.error('切换摄像头失败:', error)
        ElMessage.error('切换摄像头失败')
        // 回退到之前的摄像头
        currentCameraIndex.value = index === 0 ? 1 : 0
    } finally {
        isSwitchingCamera.value = false
        isLoading.value = false
    }
}

const startCamera = async (cameraIndex = 0) => {
    isLoading.value = true
    try {
        // ✅ 重置重连状态，确保重新连接
        wsManager.resetReconnect()
        if (!wsManager.isConnected) {
            await wsManager.connect()
        }

        // 枚举摄像头
        await enumerateCameras()
        
        if (stream) stream.getTracks().forEach(t => t.stop())
        
        // 根据索引选择摄像头
        const camera = cameras.value[cameraIndex]
        const constraints = camera && camera.deviceId 
            ? { video: { deviceId: { exact: camera.deviceId } } }
            : { video: true }
        
        stream = await navigator.mediaDevices.getUserMedia(constraints)
        currentCameraIndex.value = cameraIndex
        
        if (videoElement.value) {
            videoElement.value.srcObject = stream
            await videoElement.value.play()

            errorCount = 0
            totalFrames = 0
            perfErrorRate.value = 0

            logFeatureUsage('realtime', { action: 'start_camera' })

            startHistoryTimer()
            startTrendAnalysisTimer()

            startRendering()
            isCameraOn.value = true
        }
        ElMessage.success('摄像头已启动')
    } catch (error) {
        logger.error('摄像头启动失败:', error)
        // ✅ 优化: 细化错误类型，提供友好提示
        if (error.name === 'NotAllowedError') {
            ElMessage.error('摄像头权限被拒绝，请在浏览器设置中允许访问')
        } else if (error.name === 'NotFoundError') {
            ElMessage.error('未检测到摄像头设备，请检查连接')
        } else if (error.name === 'NotReadableError') {
            ElMessage.error('摄像头被其他应用占用，请关闭后重试')
        } else if (error.name === 'OverconstrainedError') {
            ElMessage.error('摄像头不支持 requested 分辨率')
        } else {
            ElMessage.error(`摄像头启动失败: ${error.message}`)
        }
    } finally {
        isLoading.value = false
    }
}

const stopCamera = () => {
    if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null }
    if (animationId) { cancelAnimationFrame(animationId); animationId = null }
    // ✅ 新增: 停止情绪历史记录
    stopHistoryTimer()
    // ✅ 新增: 停止情绪趋势分析
    stopTrendAnalysisTimer()
    // ✅ 新增: 断开WebSocket连接，防止继续接收消息触发音乐
    if (wsManager.isConnected) {
        wsManager.close()
    }
    isCameraOn.value = false
    fps.value = 0
    frameCountForFps = 0
    // ✅ 立即清空情绪数据，确保UI立即更新
    currentEmotion.value = null
    currentConfidence.value = 0
    emotionScores.value = {}
    currentFaces.value = []
    awaitingResult = false
    _consecutiveEmpty = 0
    _adaptiveQuality = 0.5
    _smoothedBbox = {}
    clearEmotionHistory()
    // ✅ 新增: 停止检测时自动停止音乐
    if (generativeAudio.isInitialized) {
        generativeAudio.stop()
    }
    // ✅ 修改: 不再重置情绪统计，保留历史数据供图表显示
    // emotionCounts.happy = 0
    // emotionCounts.sad = 0
    // emotionCounts.angry = 0
    // emotionCounts.surprised = 0
    // emotionCounts.fearful = 0
    // emotionCounts.disgust = 0
    // emotionCounts.neutral = 0
    // 重置主题到用户设置
    themeStore.resetTheme()
}

const toggleCamera = () => { 
    isCameraOn.value ? stopCamera() : startCamera() 
}
const toggleEmotionDetection = () => {
    isEmotionDetectionOn.value = !isEmotionDetectionOn.value
    // ✅ 修复: 切换情感识别开关时，通知后端停止/恢复检测
    try {
        wsManager.sendMessage('detection_control', {
            enabled: isEmotionDetectionOn.value
        })
    } catch (error) {
        logger.warn('发送检测控制消息失败:', error)
    }

    if (!isEmotionDetectionOn.value) {
        currentFaces.value = []
        currentEmotion.value = null
        currentConfidence.value = 0
        emotionScores.value = {}
        _smoothedBbox = {}
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
    if (!canvas || !video) {
        logger.error('[渲染] startRendering: canvas或video元素不存在')
        return
    }

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

        const currentVideoTime = video.currentTime
        if (render._lastVideoTime === currentVideoTime && currentFaces.value?.length > 0) {
            animationId = requestAnimationFrame(render)
            return
        }
        render._lastVideoTime = currentVideoTime

        const elapsed = timestamp - lastRenderTime
        if (elapsed < FRAME_INTERVAL) {
            animationId = requestAnimationFrame(render)
            return
        }
        lastRenderTime = timestamp - (elapsed % FRAME_INTERVAL)

        const vw = video.videoWidth || 640
        const vh = video.videoHeight || 480
        if (canvas.width !== vw || canvas.height !== vh) {
            canvas.width = vw
            canvas.height = vh
        }

        ctx.save()
        ctx.translate(canvas.width, 0)
        ctx.scale(-1, 1)
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
        ctx.restore()

        updateFps()

        if (currentFaces.value?.length === 0) {
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
            let currentHash = 0
            const step = 200
            for (let i = 0; i < imageData.data.length; i += step * 4) {
                currentHash = ((currentHash << 5) - currentHash) + imageData.data[i]
                currentHash |= 0
            }

            if (currentHash === lastFrameHash) {
                staticFrameCount++
                if (staticFrameCount >= MAX_STATIC_FRAMES) {
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

        // ✅ 计算人脸框插值（基于时间比例平滑过渡）
            const nowForInterpolate = performance.now()
            const timeSinceDetection = nowForInterpolate - _lastDetectionTime
            const INTERPOLATION_DURATION = 150  // 插值持续时间ms
            
            if (currentFaces.value?.length) {
                currentFaces.value.forEach((face, index) => {
                    const target = _targetBbox[index]
                    if (!target) return
                    
                    // 计算插值比例 t (0 -> 1)
                    const t = Math.min(1, timeSinceDetection / INTERPOLATION_DURATION)
                    // 使用 ease-out 缓动让动画更自然
                    const easeT = 1 - Math.pow(1 - t, 3)
                    
                    // 初始化渲染bbox
                    if (!_renderBbox[index]) {
                        _renderBbox[index] = [...target]
                    }
                    
                    // 逐帧插值到目标位置
                    const [tx, ty, tw, th] = target
                    const [rx, ry, rw, rh] = _renderBbox[index]
                    
                    _renderBbox[index][0] = rx + (tx - rx) * easeT
                    _renderBbox[index][1] = ry + (ty - ry) * easeT
                    _renderBbox[index][2] = rw + (tw - rw) * easeT
                    _renderBbox[index][3] = rh + (th - rh) * easeT
                })
            }
            
            if (isCameraOn.value && isEmotionDetectionOn.value && currentFaces.value?.length) {
                const scaleX = canvas.width / currentResolution.width
                const scaleY = canvas.height / currentResolution.height
                const totalFaces = currentFaces.value.length

                const drawnLabels = []

                currentFaces.value.forEach((face, index) => {
                    // ✅ 使用插值后的bbox进行绘制
                    const [ix, iy, iw, ih] = _renderBbox[index] || face.bbox

                    const sx = ix * scaleX, sy = iy * scaleY, sw = iw * scaleX, sh = ih * scaleY
                    const flippedBbox = [canvas.width - sx - sw, sy, sw, sh]
                    const color = getEmotionColor(face.emotion)
                    drawCornerBox(ctx, flippedBbox, color, 3)

                    const labelRect = drawEmotionLabel(ctx, flippedBbox, face.emotion, face.confidence, themeStore.currentTheme, index + 1, totalFaces, drawnLabels)
                    drawnLabels.push(labelRect)
                })
            }

        frameSkip++

        // ✅ 计算真实帧率（基于渲染帧时间）
        const now = performance.now()
        _frameTimestamps.push(now)
        if (_frameTimestamps.length > _MAX_FRAME_HISTORY) {
            _frameTimestamps.shift()
        }
        
        if (_frameTimestamps.length >= 2) {
            const elapsed = _frameTimestamps[_frameTimestamps.length - 1] - _frameTimestamps[0]
            const frameCount = _frameTimestamps.length - 1
            perfFps.value = frameCount > 0 && elapsed > 0 ? (frameCount / elapsed) * 1000 : 0
        }

        if (performance.now() - lastAdjustTime > 5000) {
            adjustResolution()
            lastAdjustTime = performance.now()
        }

        const avgRtt = _roundTripHistory.length > 0
            ? _roundTripHistory.reduce((a, b) => a + b, 0) / _roundTripHistory.length : 0

        const baseSkipThreshold = performanceModeConfig.frame_skip_threshold

        const skipThreshold = avgRtt > 200
            ? baseSkipThreshold + 1
            : avgRtt > 100
                ? baseSkipThreshold
                : Math.max(1, baseSkipThreshold - 1)

        if (isEmotionDetectionOn.value) {
            frameSkip = 0
            lastSentTime = performance.now()

            sendCtx.drawImage(video, 0, 0, currentResolution.width, currentResolution.height)
            const imageData = sendCtx.getImageData(0, 0, currentResolution.width, currentResolution.height)

            if (detectionMode.value === 'websocket' && wsManager.isConnected) {
                // WebSocket 模式
                const buf = new ArrayBuffer(6 + imageData.data.length)
                const dv = new DataView(buf)
                dv.setUint8(0, 0x02)
                dv.setUint8(1, 0x00)
                dv.setUint16(2, currentResolution.width, true)
                dv.setUint16(4, currentResolution.height, true)
                new Uint8Array(buf, 6).set(imageData.data)

                try {
                    const success = wsManager.sendBinary(buf)
                    if (success) {
                        totalFrames++
                    } else {
                        errorCount++
                    }
                } catch (error) {
                    errorCount++
                    totalFrames++
                }
            } else if (detectionMode.value === 'worker') {
                // Web Worker 模式
                detectWithWorker(imageData, currentResolution.width, currentResolution.height)
                    .then((result) => {
                        if (result) {
                            handleWorkerResult(result)
                            totalFrames++
                        } else {
                            errorCount++
                        }
                    })
                    .catch(() => {
                        errorCount++
                    })
            }
        }

        animationId = requestAnimationFrame(render)
    }
    render(performance.now())
}

// === Web Worker 检测函数 ===
const detectWithWorker = async (imageData, width, height) => {
    try {
        if (!workerDetectionService.isInitialized) {
            await workerDetectionService.initialize()
        }
        return await workerDetectionService.detect(imageData, width, height)
    } catch (error) {
        logger.error('Worker 检测失败:', error)
        return null
    }
}

// === Web Worker 结果处理 ===
const handleWorkerResult = (result) => {
    if (!result || !result.faces) return
    
    const validFaces = result.faces.filter(face => face && face.bbox && face.bbox.length === 4)
    
    if (validFaces.length) {
        const firstFace = validFaces[0]
        const rawScores = firstFace?.scores
        const rawConf = firstFace?.confidence

        if (!rawScores || typeof rawScores !== 'object' || Object.keys(rawScores).length === 0) {
            logger.warn('收到无效的 scores 数据，跳过此帧')
            return
        }

        const dominantEmotion = Object.keys(rawScores).reduce((a, b) =>
            rawScores[a] > rawScores[b] ? a : b
        )

        _lastGoodEmotion = dominantEmotion
        _lastGoodScores = { ...rawScores }
        _consecutiveEmpty = 0

        // 更新检测数据
        currentEmotion.value = dominantEmotion
        currentConfidence.value = rawConf
        emotionScores.value = getAverageScores(validFaces)
        currentFaces.value = validFaces.slice(0, maxDetectFaces)
        
        // 更新状态存储
        detectionStore.updateDetection(validFaces, dominantEmotion, rawScores)
        detectionStore.saveRealtimeState({
            faces: validFaces,
            emotion: dominantEmotion,
            timestamp: Date.now()
        })
    } else {
        _consecutiveEmpty++
        if (_consecutiveEmpty >= EMPTY_THRESHOLD) {
            currentEmotion.value = null
            currentConfidence.value = 0
            emotionScores.value = {}
            currentFaces.value = []
            _lastGoodEmotion = null
            _lastGoodScores = {}
            _consecutiveEmpty = 0
        }
    }
}

// === WebSocket 消息处理 (含 EMA + 自适应质量) ===

const handleWsMessage = (data) => {
    if (data.type !== 'result') return
    
    const processTime = data.process_time
    // ✅ 修复: 使用 lastSentTime 计算往返延迟，而不是 process_time
    // process_time 是后端处理完成的时间戳，不能直接用于计算 RTT
    const actualRtt = performance.now() - lastSentTime
    perfLatency.value = Math.max(0, actualRtt)  // 确保非负

    // ✅ 更新真实性能数据
    if (data.process_duration_ms !== undefined) {
        perfInferenceTime.value = data.process_duration_ms  // 模型推理时间
    }
    
    // ✅ 检测延迟 = 往返延迟
    perfDetectionLatency.value = Math.max(0, actualRtt)
    
    // ✅ 网络延迟(Ping) = 往返延迟的一半（近似）
    perfNetworkLatency.value = Math.max(0, actualRtt / 2)
    
    // ✅ 判断是否使用GPU（根据性能模式）
    isUsingGpu.value = performanceModeConfig.use_gpu === true

    // 计算真实处理延迟
    const rtt = Math.max(0, actualRtt)

    _roundTripHistory.push(rtt)
    if (_roundTripHistory.length > 10) _roundTripHistory.shift()

    awaitingResult = false

    // ✅ 关键修复: 信任后端结果，只过滤无效数据
    const validFaces = data.faces?.filter(face => {
        // 必须有有效的 bbox 数据
        if (!face || !face.bbox || face.bbox.length !== 4) return false
        // 缓存人脸无条件通过
        if (face._cached) return true
        // 置信度阈值降到 0.1，避免有效人脸被误过滤
        return face.confidence >= 0.1
    }) || []

    // ✅ 新增: 诊断日志
    

    if (validFaces.length) {
        const firstFace = validFaces[0]
        const rawScores = firstFace?.scores
        const rawConf = firstFace?.confidence

        if (!rawScores || typeof rawScores !== 'object' || Object.keys(rawScores).length === 0) {
            logger.warn('收到无效的 scores 数据，跳过此帧')
            return
        }

        const dominantEmotion = Object.keys(rawScores).reduce((a, b) =>
            rawScores[a] > rawScores[b] ? a : b
        )

        _lastGoodEmotion = dominantEmotion
        _lastGoodScores = { ...rawScores }
        _consecutiveEmpty = 0

        // ✅ 改进的 EMA 平滑人脸框（使用 IoU 匹配 + 速度阻尼）
        const matches = _matchFacesByIoU(_prevBboxes, validFaces)
        const currentBboxes = {}
        
        const smoothedFaces = validFaces.map((face, currIndex) => {
            const rawBbox = face.bbox
            const faceId = matches[currIndex]
            
            // 存储当前帧的原始bbox用于下一帧匹配
            currentBboxes[faceId] = [...rawBbox]
            
            if (!_smoothedBbox[faceId]) {
                // 首次检测到，直接使用原始值初始化
                _smoothedBbox[faceId] = {
                    bbox: [...rawBbox],
                    velocity: [0, 0, 0, 0]  // 记录速度用于阻尼
                }
                return { ...face, bbox: [...rawBbox] }
            }
            
            // 改进的 EMA 平滑算法：
            // 1. 计算当前帧与历史帧的差异（预测下一位置）
            // 2. 使用阻尼系数减缓速度变化
            // 3. 应用平滑后的位置
            
            const prev = _smoothedBbox[faceId]
            const newVelocity = []
            const smoothed = []
            
            for (let i = 0; i < 4; i++) {
                // 计算当前速度（当前帧 - 上一帧平滑值）
                const rawVelocity = rawBbox[i] - prev.bbox[i]
                
                // 速度阻尼：保留部分历史速度，防止突变
                newVelocity[i] = BBOX_VELOCITY_DAMPING * prev.velocity[i] + (1 - BBOX_VELOCITY_DAMPING) * rawVelocity
                
                // 改进的 EMA：结合当前值和预测值
                // smoothed = alpha * raw + (1 - alpha) * (prev + velocity)
                const predicted = prev.bbox[i] + newVelocity[i] * 0.5
                smoothed[i] = Math.round(
                    BBOX_SMOOTH_ALPHA * rawBbox[i] + 
                    (1 - BBOX_SMOOTH_ALPHA) * predicted
                )
            }
            
            // 更新平滑缓冲区
            _smoothedBbox[faceId] = {
                bbox: smoothed,
                velocity: newVelocity
            }
            
            return { ...face, bbox: smoothed }
        })
        
        // 更新上一帧的原始bbox缓存
        _prevBboxes = currentBboxes
        
        // ✅ 记录检测时间和目标bbox用于渲染插值
        _lastDetectionTime = performance.now()
        _targetBbox = {}
        smoothedFaces.forEach((face, idx) => {
            _targetBbox[idx] = [...face.bbox]
            _renderBbox[idx] = _renderBbox[idx] || [...face.bbox]
        })

        currentEmotion.value = dominantEmotion
        currentConfidence.value = rawConf
        emotionScores.value = getAverageScores(validFaces)
        // ✅ 使用系统配置的最大人脸数量限制 + 平滑后的人脸框
        currentFaces.value = smoothedFaces.slice(0, maxDetectFaces)

        detectionStore.updateDetection(validFaces, dominantEmotion, { ...rawScores })

        themeStore.updateThemeByEmotion(dominantEmotion)
    } else {
        _consecutiveEmpty++

        if (_consecutiveEmpty >= EMPTY_THRESHOLD) {
            currentEmotion.value = null
            currentConfidence.value = 0
            emotionScores.value = {}
            currentFaces.value = []

            _lastGoodEmotion = null
            _lastGoodScores = {}
            _smoothedBbox = {}
            _prevBboxes = {}  // ✅ 同时清理IoU匹配缓存
            _consecutiveEmpty = 0
        } else {
            const decayFactor = 1 - (_consecutiveEmpty / EMPTY_THRESHOLD) * 0.5
            currentConfidence.value *= decayFactor

            
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
        ElMessage.success('截图已保存')
    }
}

// ✅ 新增: 打开反馈对话框并捕获静态快照
const openFeedbackWithSnapshot = () => {
    const canvas = canvasElement.value
    if (!canvas || !currentEmotion.value) {
        ElMessage.warning('请先确保已检测到人脸')
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

        showFeedback.value = true
    } catch (error) {
        logger.error('捕获快照失败:', error)
        ElMessage.error('截图失败，请重试')
    }
}

// ✅ 新增: 手动保存到历史档案
const saveToHistoryManual = async () => {
    if (!currentEmotion.value || !currentConfidence.value || currentFaces.value.length === 0) {
        ElMessage.warning('暂无可保存的检测数据')
        return
    }

    if (isSaving.value) {
        return
    }

    try {
        isSaving.value = true

        await saveRealtimeToHistory(
            currentEmotion.value,
            currentConfidence.value,
            currentFaces.value
        )

        ElMessage.success('已保存到历史档案')
    } catch (error) {
        logger.error('手动保存失败:', error)
        ElMessage.error('保存失败，请重试')
    } finally {
        setTimeout(() => {
            isSaving.value = false
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
}

const saveRealtimeToHistory = async (emotion, confidence, faces) => {
    try {
        const now = Date.now()
        const timeSinceLastSave = now - lastSaveTime

        if (timeSinceLastSave < SAVE_COOLDOWN) {
            ElMessage.warning('请勿重复保存')
            return
        }
        lastSaveTime = now

        if (!isCameraOn.value) {
            return
        }

        if (!faces || faces.length === 0) {
            logger.warn('未检测到人脸，跳过保存历史记录')
            ElMessage.info('未检测到人脸，无法保存')
            return
        }

        const canvas = canvasElement.value
        if (!canvas) {
            logger.warn('Canvas 元素未找到，无法保存历史记录')
            return
        }

        if (canvas.width === 0 || canvas.height === 0) {
            logger.warn('Canvas 尺寸为 0，无法保存历史记录')
            return
        }

        const thumbnailCanvas = document.createElement('canvas')
        const thumbCtx = thumbnailCanvas.getContext('2d')
        thumbnailCanvas.width = 320
        thumbnailCanvas.height = 240

        let savedFaces = []

        if (faces.length > 0 && faces[0].bbox) {
            const bbox = Array.from(faces[0].bbox)
            let [x, y, w, h] = bbox

            const scaleX = canvas.width / currentResolution.width
            const scaleY = canvas.height / currentResolution.height

            const displayX = x * scaleX
            const displayY = y * scaleY
            const displayW = w * scaleX
            const displayH = h * scaleY

            const padding = 0.2
            const padX = Math.max(0, displayX - displayW * padding)
            const padY = Math.max(0, displayY - displayH * padding)
            const padW = displayW * (1 + padding * 2)
            const padH = displayH * (1 + padding * 2)

            if (padW <= 0 || padH <= 0) {
                logger.error('裁剪区域尺寸无效,使用默认完整帧')
                thumbCtx.drawImage(canvas, 0, 0, 320, 240)
                savedFaces = [{
                    ...faces[0],
                    bbox: [80, 60, 160, 120]
                }]
            } else {
                thumbCtx.drawImage(
                    canvas,
                    padX, padY, padW, padH,
                    0, 0, 320, 240
                )

                savedFaces = [{
                    ...faces[0],
                    bbox: [32, 24, 256, 192]
                }]
            }

            for (let i = 1; i < faces.length; i++) {
                if (faces[i].bbox) {
                    savedFaces.push({
                        ...faces[i],
                        bbox: [32, 24, 256, 192]
                    })
                }
            }
        } else {
            logger.error('代码逻辑错误：不应进入此分支')
            return
        }

        const thumbnail = thumbnailCanvas.toDataURL('image/jpeg', 0.8)

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

        await saveHistoryRecord(historyData)
        
    } catch (error) {
        logger.error('保存实时检测历史记录失败:', error)
    }
}
</script>

<style scoped>
.realtime-page {
    height: 100%;
    display: grid;
    grid-template-columns: 1fr 350px;
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

/* 摄像头启动加载遮罩 */
.camera-loading-overlay {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    background: color-mix(in srgb, var(--background) 85%, transparent);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    z-index: 25;
    border-radius: inherit;
}

.loading-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
}

.loading-icon .spinner {
    color: var(--primary);
    animation: loadingSpin 1s linear infinite;
}

@keyframes loadingSpin {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}

.loading-text {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-secondary);
    letter-spacing: 0.5px;
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
    max-width: 95vw;
    /* ✅ 修复: 防止控制栏溢出屏幕 */
    flex-wrap: nowrap;
    /* ✅ 修复: 保持单行布局 */
    overflow-x: auto;
    /* ✅ 修复: 允许横向滚动（小屏幕） */
    scrollbar-width: none;
    /* ✅ 修复: 隐藏滚动条 */
}

/* ✅ 新增: 隐藏 Webkit 滚动条 */
.video-controls::-webkit-scrollbar {
    display: none;
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
        width: 90px;
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

/* ✅ 修复: 模型选择器样式 - 适配圆形按钮高度 */
.model-selector {
    width: 140px;
    /* ✅ 修改: 固定宽度，不使用 min-width */
    flex-shrink: 0;
    /* ✅ 修复: 防止被压缩 */
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
    /* ✅ 优化: 参考 AnalyticsDashboard.vue 的卡片内边距风格 */
    padding: 0;
    /* ✅ 修复: 面板自身不滚动，让内部元素管理滚动 */
    overflow: hidden;
    display: flex;
    flex-direction: column;
    /* ✅ 移除: min-height，让高度完全自适应内容 */
    gap: 0;
}

/* ✅ 新增: 上半部分样式（实时分析内容） */
.panel-upper {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    padding: 14px 30px 10px;
    /* ✅ 优化: 参考 AnalyticsDashboard.vue 的 chart-card-header 内边距 */
    min-height: 0;
}

.panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    /* ✅ 修复: 移除分割线，让视觉更轻盈 */
    flex-shrink: 0;
    padding-bottom: 10px;
    /* ✅ 移除: border-bottom，避免与下半部分的分隔线重叠 */
    /* border-bottom: 1px solid var(--border); */
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
    padding: 0;
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
    font-weight: 600;
    flex-shrink: 0;
    text-shadow: 0 0 10px currentColor;
}

.emotion-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    /* margin-bottom: 16px; */
}

.emotion-confidence {
    font-size: 26px;
    font-weight: 600;
    flex-shrink: 0;
    text-shadow: 0 0 12px currentColor;
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
    margin-top: 8px;
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

/* ✅ 新增: 置信度显示模式切换 */
.confidence-mode-switch {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 12px;
    padding: 8px 12px;
    background: color-mix(in srgb, var(--text) 5%, transparent);
    border-radius: 8px;
}

.mode-label {
    font-size: 12px;
    color: var(--text-secondary);
    font-weight: 100;
}

/* ✅ 新增: 原始置信度提示 */
.raw-confidence-hint {
    font-size: 12px;
    opacity: 0.7;
    margin-left: 6px;
    color: var(--text-secondary);
    font-weight: 100;
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

    /* ✅ 新增: 移动端控制栏适配 */
    .video-controls {
        max-width: 90vw;
        /* 更窄的屏幕限制 */
        padding: 4px 8px;
        /* 减小内边距 */
        gap: 4px;
        /* 减小间距 */
    }

    /* ✅ 新增: 移动端缩小按钮尺寸 */
    .ctrl-btn {
        width: 32px;
        height: 32px;
    }

    .ctrl-btn svg {
        width: 16px;
        height: 16px;
    }

    .ctrl-stop {
        padding: 0 12px;
    }

    .btn-label {
        font-size: 11px;
    }

    /* ✅ 新增: 移动端模型选择器缩小 */
    .model-selector {
        width: 120px;
        /* 更窄的宽度 */
    }

    .model-selector :deep(.el-input__inner) {
        font-size: 11px;
    }

    /* ✅ 新增: 移动端分隔线缩小 */
    .ctrl-divider {
        height: 20px;
        margin: 0 2px;
    }
}

/* 移除: 面板控制按钮样式（已迁移到视频控制栏） */
/* .panel-controls 相关样式已删除 */

/* ✅ 新增: 情绪趋势图表区域样式 */
.panel-lower {
    flex-shrink: 0;
    border-top: 1px solid var(--border);
    padding: 10px 14px 14px;
}

.emotion-trend-section {
    width: 100%;
}

.trend-section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 12px;
}

.trend-section-header h4 {
    font-size: 15px;
    font-weight: 100;
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--text);
    margin: 0;
}

.section-icon {
    display: flex;
    color: var(--primary);
}

.trend-chart-wrapper {
    width: 100%;
}

/* ✅ 新增: 摄像头切换按钮样式 */
.camera-switch-wrapper {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 14px;
    background: var(--btn-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.2s ease;
    min-width: 120px;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
}

.camera-switch-wrapper:hover {
    background: color-mix(in srgb, var(--primary) 15%, transparent);
    border-color: var(--primary);
    color: var(--primary);
    transform: scale(1.02);
}

.camera-switch-wrapper:active {
    transform: scale(0.98);
}

/* 切换中的状态 */
.camera-switch-wrapper.switching {
    pointer-events: none;
    border-color: var(--primary);
    background: color-mix(in srgb, var(--primary) 10%, transparent);
}

/* 图标包装器 */
.camera-icon-wrapper {
    position: relative;
    width: 18px;
    height: 18px;
    flex-shrink: 0;
}

.camera-icon {
    color: var(--primary);
    transition: opacity 0.3s ease;
}

.camera-switch-wrapper.switching .camera-icon {
    opacity: 0;
}

/* 加载动画 */
.camera-loading {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    display: flex;
    align-items: center;
    justify-content: center;
}

.loading-spinner {
    animation: spin 0.6s linear infinite;
    color: var(--primary);
}

@keyframes spin {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}

.camera-name {
    flex: 1;
    font-size: 13px;
    font-weight: 100;
    text-align: left;
    min-width: 60px;
}

.camera-arrow {
    flex-shrink: 0;
    transition: transform 0.2s ease;
}

/* ✅ 摄像头名称切换动画 */
.camera-switch-enter-active,
.camera-switch-leave-active {
    transition: all 0.3s ease;
}

.camera-switch-enter-from {
    opacity: 0;
    transform: translateX(-10px) scale(0.9);
}

.camera-switch-leave-to {
    opacity: 0;
    transform: translateX(10px) scale(0.9);
}

.camera-switch-wrapper:hover .camera-arrow {
    transform: rotate(180deg);
}

/* ✅ 视频画面切换动画 */
.video-canvas {
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.video-canvas.camera-switch-transition {
    opacity: 0.5;
    transform: scale(0.98);
    filter: blur(5px);
}

/* ✅ 摄像头切换过渡遮罩 */
.camera-transition-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(10px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
    animation: overlayFadeIn 0.3s ease forwards;
}

@keyframes overlayFadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

.camera-transition-overlay .transition-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    padding: 32px 48px;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-xl);
    animation: contentScaleIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

@keyframes contentScaleIn {
    from {
        opacity: 0;
        transform: scale(0.8);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

.camera-transition-overlay .transition-icon {
    width: 64px;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: color-mix(in srgb, var(--primary) 15%, transparent);
    border-radius: 50%;
    border: 2px solid var(--primary);
}

.camera-transition-overlay .transition-spinner {
    color: var(--primary);
    animation: spin 0.8s linear infinite;
}

.camera-transition-overlay .transition-text {
    font-size: 14px;
    font-weight: 100;
    color: var(--text-secondary);
}

/* 下拉菜单项样式 */
.camera-dropdown-menu {
    background: var(--card-bg) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: var(--shadow-lg) !important;
    padding: 4px 0 !important;
    min-width: 200px !important;
    animation: dropdownFadeIn 0.25s ease;
}

@keyframes dropdownFadeIn {
    from {
        opacity: 0;
        transform: translateY(-8px) scale(0.95);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.camera-dropdown-item {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 10px 14px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    color: var(--text-secondary) !important;
    font-size: 13px !important;
}

.camera-dropdown-item:hover {
    background: color-mix(in srgb, var(--primary) 10%, transparent) !important;
    color: var(--text) !important;
}

.camera-item-icon {
    flex-shrink: 0;
    color: var(--primary);
    opacity: 0.7;
}

.camera-dropdown-item:hover .camera-item-icon {
    opacity: 1;
}

.camera-item-active {
    color: var(--success) !important;
}

.camera-check {
    color: var(--success);
    font-weight: 100;
    font-size: 14px;
    min-width: 16px;
}

.camera-dot {
    color: var(--text-secondary);
    opacity: 0.4;
    font-size: 10px;
    min-width: 16px;
}

.camera-item-label {
    flex: 1;
    font-weight: 100;
}

/* ✅ 新增: 淡入动画 */
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}

/* ✅ 新增: 多人脸标签 */
.multi-face-badge {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    background: linear-gradient(135deg, rgba(113, 57, 255, 0.15), rgba(156, 78, 255, 0.1));
    border: 1px solid rgba(113, 57, 255, 0.3);
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    color: var(--primary-light);
    flex-shrink: 0;
    animation: fadeIn 0.3s ease;
}

/* ✅ 新增: 人脸卡片列表 */
.face-cards-list {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 8px;
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding-right: 2px;
}

.face-cards-list::-webkit-scrollbar {
    width: 4px;
}

.face-cards-list::-webkit-scrollbar-thumb {
    background: rgba(146, 78, 255, 0.25);
    border-radius: 2px;
}

.face-cards-list::-webkit-scrollbar-track {
    background: transparent;
}

/* ✅ 新增: 单个人脸卡片 */
.face-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px 14px;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
}

.face-card::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 3px;
    background: var(--face-color, #7139FF);
    border-radius: 0 2px 2px 0;
}

.face-card:hover {
    border-color: var(--face-color, #7139FF);
    box-shadow: 0 2px 12px color-mix(in srgb, var(--face-color, #7139FF) 20%, transparent);
    transform: translateY(-1px);
}

.face-card-number {
    font-size: 11px;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

.face-card-row {
    display: flex;
    align-items: center;
    gap: 8px;
}

.face-card-emoji {
    font-size: 20px;
    line-height: 1;
    flex-shrink: 0;
}

.face-card-emotion-name {
    font-size: 13px;
    font-weight: 600;
    color: var(--face-color, #7139FF);
    flex-shrink: 0;
}

.face-card-bar-track {
    flex: 1;
    height: 7px;
    background: color-mix(in srgb, var(--text) 10%, transparent);
    border-radius: 4px;
    overflow: hidden;
    min-width: 40px;
}

.face-card-bar-fill {
    height: 100%;
    border-radius: 4px;
    background: var(--face-color, #7139FF);
    transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 0 8px color-mix(in srgb, var(--face-color, #7139FF) 40%, transparent);
}

.face-card-bar-value {
    font-size: 12px;
    font-weight: 700;
    color: var(--face-color, #7139FF);
    flex-shrink: 0;
    font-variant-numeric: tabular-nums;
}

/* ✅ 新增: 多人脸图表提示 */
</style>
