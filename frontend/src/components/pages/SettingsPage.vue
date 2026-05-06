<template>
    <div class="page settings-page">
        <div class="settings-container">
            <div class="page-header">
                <h2><el-icon>
                        <Setting />
                    </el-icon> 系统设置</h2>
                <p>配置系统参数，优化使用体验</p>
            </div>
            <div class="settings-form-panel">
                <!-- 选项卡导航 -->
                <div class="settings-tabs">
                    <div v-for="tab in settingsTabs" :key="tab.key" class="tab-item"
                        :class="{ active: activeTab === tab.key }" @click="activeTab = tab.key">
                        <el-icon>
                            <component :is="tab.icon" />
                        </el-icon>
                        <span>{{ tab.label }}</span>
                    </div>
                </div>

                <!-- 选项卡内容 -->
                <div class="settings-tab-content">
                    <!-- ✅ 新增: 性能优化 -->
                    <div v-show="activeTab === 'performance'" class="tab-panel">
                        <el-form label-position="top" size="large">
                            <!-- 性能模式选择器 -->
                            <el-form-item label="性能模式">
                                <el-select v-model="settingsConfig.performance_mode" style="width:100%"
                                    @change="handlePerformanceModeChange" class="compact-select">
                                    <el-option label="🚀 超高 (Ultra) - GPU加速 + 高分辨率 + 无跳帧" value="ultra" />
                                    <el-option label="⚡ 高 (High) - GPU加速 + 标准分辨率 + 适度跳帧" value="high" />
                                    <el-option label="💻 中 (Medium) - CPU推理 + 低分辨率 + 较大跳帧" value="medium" />
                                    <el-option label="🐢 低 (Low) - 轻量CPU + 最低分辨率 + 最大跳帧" value="low" />
                                </el-select>
                                <div class="mode-description">
                                    <div v-if="settingsConfig.performance_mode === 'ultra'">
                                        <p><strong>适用场景：</strong>高端 NVIDIA GPU (RTX 3060+ / RTX 40系列)</p>
                                        <p><strong>性能表现：</strong>30-60 FPS，最佳画质和响应速度</p>
                                        <p><strong>硬件要求：</strong>GPU 显存 ≥ 4GB，推荐 8GB+</p>
                                    </div>
                                    <div v-else-if="settingsConfig.performance_mode === 'high'">
                                        <p><strong>适用场景：</strong>中端 GPU (GTX 1060+ / RTX 20系列) 或入门级独显</p>
                                        <p><strong>性能表现：</strong>15-30 FPS，平衡性能和画质</p>
                                        <p><strong>硬件要求：</strong>GPU 显存 ≥ 2GB</p>
                                    </div>
                                    <div v-else-if="settingsConfig.performance_mode === 'medium'">
                                        <p><strong>适用场景：</strong>无 GPU 或中端 CPU (Intel i5+ / AMD Ryzen 5+)</p>
                                        <p><strong>性能表现：</strong>8-15 FPS，CPU 推理，稳定运行</p>
                                        <p><strong>硬件要求：</strong>CPU 4核心以上，内存 ≥ 4GB</p>
                                    </div>
                                    <div v-else>
                                        <p><strong>适用场景：</strong>老旧硬件或低功耗设备 (Intel i3 / 集成显卡)</p>
                                        <p><strong>性能表现：</strong>5-8 FPS，确保流畅运行</p>
                                        <p><strong>硬件要求：</strong>任意 CPU，内存 ≥ 2GB</p>
                                    </div>
                                </div>
                            </el-form-item>

                            <!-- 硬件信息展示 -->
                            <el-form-item label="当前硬件状态">
                                <div class="hardware-info">
                                    <div class="info-item">
                                        <el-icon>
                                            <Monitor />
                                        </el-icon>
                                        <span>GPU: {{ hardwareInfo.gpu || '未检测到' }}</span>
                                    </div>
                                    <div class="info-item">
                                        <el-icon>
                                            <Cpu />
                                        </el-icon>
                                        <span>CPU: {{ hardwareInfo.cpu || '未知' }}</span>
                                    </div>
                                    <div class="info-item">
                                        <el-icon>
                                            <Setting />
                                        </el-icon>
                                        <span>推荐模式: {{ hardwareInfo.recommendedMode || '检测中...' }}</span>
                                    </div>
                                </div>
                            </el-form-item>
                        </el-form>
                    </div>

                    <!-- AI 模型配置 -->
                    <div v-show="activeTab === 'ai'" class="tab-panel">
                        <el-form label-position="top" size="large">

                            <el-form-item label="推理设备">
                                <el-radio-group v-model="settingsConfig.use_gpu" size="large"
                                    @change="handleConfigChange" class="compact-radio-group">
                                    <el-radio-button :value="true" class="compact-radio">
                                        <el-icon>
                                            <Monitor />
                                        </el-icon> GPU 加速
                                    </el-radio-button>
                                    <el-radio-button :value="false" class="compact-radio">
                                        <el-icon>
                                            <Cpu />
                                        </el-icon> CPU 推理
                                    </el-radio-button>
                                </el-radio-group>
                            </el-form-item>

                            <el-form-item label="人脸检测模型">
                                <el-radio-group v-model="settingsConfig.use_onnx_face_detector" size="large"
                                    @change="handleConfigChange" class="compact-radio-group">
                                    <el-radio-button :value="false" class="compact-radio">Caffe SSD
                                        (更准确)</el-radio-button>
                                    <el-radio-button :value="true" class="compact-radio">ONNX RFB (更快)</el-radio-button>
                                </el-radio-group>
                            </el-form-item>

                            <el-form-item label="情绪识别模型">
                                <el-select v-model="settingsConfig.emotion_model" style="width:100%"
                                    @change="handleConfigChange" class="compact-select">
                                    <el-option label="ONNX 优化版 (推荐)" value="./models/emotion_model.onnx" />
                                    <el-option label="PyTorch 原版" value="./models/pytorch_final_3060.pth" />
                                </el-select>
                            </el-form-item>

                            <el-form-item label="置信度阈值">
                                <div class="slider-group">
                                    <el-slider v-model="settingsConfig.confidence_threshold" :min="0.3" :max="0.9"
                                        :step="0.05" :format-tooltip="val => (val * 100).toFixed(0) + '%'"
                                        @change="handleConfigChange" />
                                    <span class="slider-hint">当前阈值: {{ (settingsConfig.confidence_threshold *
                                        100).toFixed(0) }}%</span>
                                </div>
                            </el-form-item>
                        </el-form>
                    </div>

                    <!-- 检测参数 -->
                    <div v-show="activeTab === 'detection'" class="tab-panel">
                        <el-form label-position="top" size="large">
                            <el-form-item label="摄像头分辨率">
                                <el-select v-model="settingsConfig.resolution" style="width:100%"
                                    @change="handleConfigChange" class="compact-select">
                                    <el-option label="320×240 (流畅)" value="320x240" />
                                    <el-option label="640×480 (清晰)" value="640x480" />
                                    <el-option label="1280×720 (高清)" value="1280x720" />
                                </el-select>
                            </el-form-item>

                            <el-form-item label="检测频率">
                                <div class="slider-group">
                                    <el-slider v-model="settingsConfig.detect_every_n_frames" :min="1" :max="5"
                                        :step="1" show-stops @change="handleConfigChange" />
                                    <span class="slider-hint">每 {{ settingsConfig.detect_every_n_frames }} 帧检测一次</span>
                                </div>
                            </el-form-item>
                        </el-form>
                    </div>

                    <!-- 界面设置 -->
                    <div v-show="activeTab === 'ui'" class="tab-panel">
                        <el-form label-position="top" size="large">
                            <el-form-item label="主题模式">
                                <el-radio-group v-model="settingsConfig.theme_mode" size="large"
                                    @change="handleConfigChange" class="compact-radio-group">
                                    <el-radio-button value="auto" class="compact-radio">自动切换（根据情绪）</el-radio-button>
                                    <el-radio-button value="manual" class="compact-radio">手动选择</el-radio-button>
                                </el-radio-group>
                            </el-form-item>
                        </el-form>
                    </div>

                    <!-- AI 音乐配置 -->
                    <div v-show="activeTab === 'music'" class="tab-panel">
                        <el-form label-position="top" size="large">
                            <el-form-item label="基础音量">
                                <div class="slider-group">
                                    <el-slider v-model="settingsConfig.music_volume" :min="0" :max="100" :step="1"
                                        :format-tooltip="val => val + '%'" @change="handleConfigChange" />
                                    <span class="slider-hint">当前音量: {{ settingsConfig.music_volume }}%</span>
                                </div>
                            </el-form-item>

                            <el-form-item label="情绪敏感度">
                                <div class="slider-group">
                                    <el-slider v-model="settingsConfig.emotion_sensitivity" :min="0" :max="100"
                                        :step="1" :format-tooltip="val => val + '%'" @change="handleConfigChange" />
                                    <span class="slider-hint">当前敏感度: {{ settingsConfig.emotion_sensitivity }}%</span>
                                </div>
                            </el-form-item>

                            <el-form-item label="节奏平滑度">
                                <div class="slider-group">
                                    <el-slider v-model="settingsConfig.rhythm_smoothness" :min="0" :max="100" :step="1"
                                        :format-tooltip="val => val + '%'" @change="handleConfigChange" />
                                    <span class="slider-hint">当前平滑度: {{ settingsConfig.rhythm_smoothness }}%</span>
                                </div>
                            </el-form-item>

                            <el-form-item label="音色风格">
                                <el-select v-model="settingsConfig.timbre_style" style="width:100%"
                                    @change="handleConfigChange" class="compact-select">
                                    <el-option label="柔和正弦波 (Sine)" value="sine" />
                                    <el-option label="明亮三角波 (Triangle)" value="triangle" />
                                    <el-option label="温暖锯齿波 (Sawtooth)" value="sawtooth" />
                                    <el-option label="复古方波 (Square)" value="square" />
                                </el-select>
                            </el-form-item>
                        </el-form>
                    </div>

                    <!-- 操作按钮 -->
                    <div class="settings-actions">
                        <!-- ✅ 性能优化选项卡专属按钮 -->
                        <el-button v-if="activeTab === 'performance'" type="primary" round
                            @click="detectAndRecommendMode" :loading="detecting" size="large">
                            <el-icon>
                                <Odometer />
                            </el-icon>
                            {{ detecting ? '检测中...' : ' 智能推荐最佳模式' }}
                        </el-button>
                        <el-button type="primary" plain round @click="resetConfig" size="large">
                            恢复默认
                        </el-button>
                        <el-button type="primary" round @click="saveConfig(false)" :loading="saving" size="large">
                            {{ saving ? '保存中...' : '保存设置' }}
                        </el-button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { ElMessage } from 'element-plus'
import { Setting, Cpu, Monitor, VideoCamera, Brush, Odometer, Headset } from '@element-plus/icons-vue'
import { API } from '@/api/config'
import generativeAudio from '@/utils/generativeAudio'

const themeStore = useThemeStore()

// 系统设置选项卡状态
const activeTab = ref('ai') // 默认显示 AI 模型配置
const settingsTabs = [
    { key: 'performance', label: '性能优化', icon: 'Odometer' },
    { key: 'ai', label: 'AI 模型配置', icon: 'Cpu' },
    { key: 'detection', label: '检测参数', icon: 'VideoCamera' },
    { key: 'ui', label: '界面设置', icon: 'Brush' },
    { key: 'music', label: 'AI 音乐配置', icon: 'Headset' }
]

// 系统设置配置(与后端同步)
const settingsConfig = reactive({
    // ✅ 新增: 性能模式
    performance_mode: 'high',

    // AI 模型配置
    use_gpu: true,
    use_onnx_face_detector: false,
    emotion_model: './models/emotion_model.onnx',
    confidence_threshold: 0.6,

    // 检测参数
    resolution: '640x480',
    detect_every_n_frames: 2,

    // 界面设置
    theme_mode: 'auto',

    // AI 音乐配置
    music_volume: 70,
    emotion_sensitivity: 50,
    rhythm_smoothness: 50,
    timbre_style: 'sine'
})

const saving = ref(false)
const detecting = ref(false)
const originalConfig = ref(null)

// 硬件信息
const hardwareInfo = reactive({
    gpu: null,
    cpu: null,
    recommendedMode: null
})

// 从后端加载配置
const loadConfig = async () => {
    try {
        const response = await fetch(`${API.baseUrl}/api/config`)
        if (!response.ok) throw new Error('获取配置失败')
        const data = await response.json()

        // 同步后端配置到前端
        const backendConfig = data.config
        settingsConfig.performance_mode = backendConfig.performance_mode ?? 'high'
        settingsConfig.use_gpu = backendConfig.use_gpu ?? true
        settingsConfig.use_onnx_face_detector = backendConfig.use_onnx_face_detector ?? false
        settingsConfig.emotion_model = backendConfig.emotion_model ?? './models/emotion_model.onnx'
        settingsConfig.confidence_threshold = backendConfig.confidence_threshold ?? 0.6
        settingsConfig.detect_every_n_frames = backendConfig.detect_every_n_frames ?? 2
        settingsConfig.theme_mode = backendConfig.theme_mode ?? 'auto'
        // AI 音乐配置
        settingsConfig.music_volume = backendConfig.music_volume ?? 70
        settingsConfig.emotion_sensitivity = backendConfig.emotion_sensitivity ?? 50
        settingsConfig.rhythm_smoothness = backendConfig.rhythm_smoothness ?? 50
        settingsConfig.timbre_style = backendConfig.timbre_style ?? 'sine'

        // 保存原始配置用于重置
        originalConfig.value = { ...settingsConfig }

        console.log('✅ 配置加载成功:', settingsConfig)
    } catch (error) {
        console.error('❌ 加载配置失败:', error)
        ElMessage.error('加载配置失败，使用默认值')
    }
}

// 配置变更时自动保存
let saveTimer = null
const handleConfigChange = () => {
    // 防抖保存（500ms 后自动保存）
    clearTimeout(saveTimer)
    saveTimer = setTimeout(() => {
        saveConfig(true) // silent = true
    }, 500)
}

// ✅ 新增: 智能检测并推荐性能模式
const detectAndRecommendMode = async () => {
    detecting.value = true
    try {
        // 调用后端 API 检测硬件并推荐模式
        const response = await fetch(`${API.baseUrl}/api/performance/recommend`)
        if (!response.ok) throw new Error('检测失败')
        const data = await response.json()

        // 更新硬件信息
        hardwareInfo.gpu = data.gpu || '未检测到'
        hardwareInfo.cpu = data.cpu || '未知'
        hardwareInfo.recommendedMode = data.recommended_mode || 'high'

        // 自动应用推荐模式
        settingsConfig.performance_mode = hardwareInfo.recommendedMode

        // 保存配置（静默模式，避免提示重叠）
        await saveConfig(true)

        ElMessage({
            message: `✅ 已自动推荐并应用 ${hardwareInfo.recommendedMode.toUpperCase()} 模式`,
            type: 'success',
            duration: 3000
        })
    } catch (error) {
        console.error('❌ 智能检测失败:', error)
        ElMessage.error('检测失败，请手动选择模式')
    } finally {
        detecting.value = false
    }
}

// ✅ 修改: 性能模式切换处理
const handlePerformanceModeChange = async () => {
    console.log(`🚀 切换性能模式: ${settingsConfig.performance_mode}`)

    // 立即保存配置（静默模式，避免提示重叠）
    await saveConfig(true)

    // 提示用户重启检测以生效
    ElMessage({
        message: '✅ 性能模式已更新，请重启实时检测以生效',
        type: 'success',
        duration: 3000
    })
}

// 保存设置（支持静默模式）
const saveConfig = async (silent = false) => {
    saving.value = true
    try {
        // 1. 同步到后端
        const payload = {
            performance_mode: settingsConfig.performance_mode,
            use_gpu: settingsConfig.use_gpu,
            use_onnx_face_detector: settingsConfig.use_onnx_face_detector,
            emotion_model: settingsConfig.emotion_model,
            confidence_threshold: settingsConfig.confidence_threshold,
            detect_every_n_frames: settingsConfig.detect_every_n_frames,
            theme_mode: settingsConfig.theme_mode,
            // AI 音乐配置
            music_volume: settingsConfig.music_volume,
            emotion_sensitivity: settingsConfig.emotion_sensitivity,
            rhythm_smoothness: settingsConfig.rhythm_smoothness,
            timbre_style: settingsConfig.timbre_style
        }

        const response = await fetch(`${API.baseUrl}/api/config`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })

        if (!response.ok) throw new Error('保存配置失败')

        // 2. 保存到本地
        localStorage.setItem('app_config', JSON.stringify(settingsConfig))

        // 3. 同步主题模式到 themeStore
        themeStore.themeMode = settingsConfig.theme_mode

        if (!silent) {
            ElMessage.success('设置已保存到后端并持久化')
        }
    } catch (error) {
        console.error('❌ 保存配置失败:', error)
        if (!silent) {
            ElMessage.error('保存失败: ' + error.message)
        }
    } finally {
        saving.value = false
    }
}

// 恢复默认配置
const resetConfig = async () => {
    try {
        // 重置为后端默认值
        settingsConfig.performance_mode = 'high'
        settingsConfig.use_gpu = true
        settingsConfig.use_onnx_face_detector = false
        settingsConfig.emotion_model = './models/emotion_model.onnx'
        settingsConfig.confidence_threshold = 0.6
        settingsConfig.detect_every_n_frames = 2
        settingsConfig.theme_mode = 'auto'
        settingsConfig.resolution = '640x480'
        // AI 音乐配置
        settingsConfig.music_volume = 70
        settingsConfig.emotion_sensitivity = 50
        settingsConfig.rhythm_smoothness = 50
        settingsConfig.timbre_style = 'sine'

        // 同步保存到后端
        await saveConfig(true)

        ElMessage.success('已恢复默认配置')
    } catch (error) {
        ElMessage.error('恢复配置失败')
    }
}

// 组件挂载时加载配置
onMounted(() => {
    loadConfig()
})

// ✅ 新增: 监听音乐配置变化并同步到音频引擎
watch(
    () => ({
        music_volume: settingsConfig.music_volume,
        emotion_sensitivity: settingsConfig.emotion_sensitivity,
        rhythm_smoothness: settingsConfig.rhythm_smoothness,
        timbre_style: settingsConfig.timbre_style
    }),
    (newConfig) => {
        // 同步到音频引擎
        if (generativeAudio.isInitialized) {
            generativeAudio.updateConfig(newConfig);
            console.log('🎵 音乐配置已同步到音频引擎:', newConfig);
        }
    },
    { deep: true }
)
</script>

<style scoped>
/* ✅ 性能模式描述样式 */
.mode-description {
    margin-top: 12px;
    padding: 10px 12px;
    background: linear-gradient(135deg, rgba(113, 57, 255, 0.08), rgba(156, 78, 255, 0.05));
    border-left: 3px solid var(--primary);
    border-radius: 6px;
    width: 100%;
}

.mode-description p {
    margin: 4px 0;
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.5;
}

.mode-description strong {
    color: var(--primary);
    font-weight: 600;
}

/* ✅ 新增: 硬件信息展示样式 */
.hardware-info {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 16px;
    width: 100%;
    padding: 16px;
    background: linear-gradient(135deg, rgba(113, 57, 255, 0.05), rgba(156, 78, 255, 0.03));
    border-radius: 8px;
    border: 1px solid rgba(113, 57, 255, 0.15);
}

.hardware-info .info-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 6px;
    font-size: 13px;
    color: var(--text-secondary);
    min-width: 0;
    width: 100%;
}

.hardware-info .info-item .el-icon {
    font-size: 16px;
    color: var(--primary);
    flex-shrink: 0;
}

.hardware-info .info-item span {
    white-space: normal;
    word-break: break-word;
    line-height: 1.4;
    flex: 1;
}

/* 响应式适配：小屏幕时恢复垂直排列 */
@media (max-width: 768px) {
    .hardware-info {
        grid-template-columns: 1fr;
    }
}
</style>
