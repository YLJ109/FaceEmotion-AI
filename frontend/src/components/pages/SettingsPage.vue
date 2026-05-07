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
                                <div class="mode-selector-row">
                                    <el-select v-model="settingsConfig.performance_mode"
                                        @change="handlePerformanceModeChange" class="compact-select">
                                        <el-option label="🚀 极致模式 (Ultra)" value="ultra" />
                                        <el-option label="⚡ 高性能模式 (High)" value="high" />
                                        <el-option label="🔄 平衡模式 (Medium)" value="medium" />
                                        <el-option label="🌙 节能模式 (Low)" value="low" />
                                    </el-select>
                                    <el-button type="primary" round @click="detectAndRecommendMode"
                                        :loading="detecting" size="small">
                                        <el-icon>
                                            <Odometer />
                                        </el-icon>
                                        {{ detecting ? '检测中...' : '智能推荐' }}
                                    </el-button>
                                </div>
                                <div class="mode-description">
                                    <div v-if="settingsConfig.performance_mode === 'ultra'">
                                        <div class="mode-stats">
                                            <span class="stat-item"><strong>分辨率:</strong> 256×192</span>
                                            <span class="stat-item"><strong>跳帧:</strong> 无</span>
                                            <span class="stat-item"><strong>线程:</strong> 4</span>
                                        </div>
                                        <p><strong>适用场景：</strong>高端游戏本/台式机 (Intel i7+ / AMD Ryzen 7+)</p>
                                        <p><strong>特点：</strong>极致画质，每帧检测，最低延迟，适合专业场景</p>
                                        <p><strong>硬件要求：</strong>CPU 6核心以上，内存 ≥ 8GB</p>
                                    </div>
                                    <div v-else-if="settingsConfig.performance_mode === 'high'">
                                        <div class="mode-stats">
                                            <span class="stat-item"><strong>分辨率:</strong> 192×144</span>
                                            <span class="stat-item"><strong>跳帧:</strong> 1/2</span>
                                            <span class="stat-item"><strong>线程:</strong> 3</span>
                                        </div>
                                        <p><strong>适用场景：</strong>主流笔记本/台式机 (Intel i5 / AMD Ryzen 5)</p>
                                        <p><strong>特点：</strong>高性能，平衡画质与流畅度，适合日常使用</p>
                                        <p><strong>硬件要求：</strong>CPU 4核心以上，内存 ≥ 4GB</p>
                                    </div>
                                    <div v-else-if="settingsConfig.performance_mode === 'medium'">
                                        <div class="mode-stats">
                                            <span class="stat-item"><strong>分辨率:</strong> 128×96</span>
                                            <span class="stat-item"><strong>跳帧:</strong> 1/4</span>
                                            <span class="stat-item"><strong>线程:</strong> 2</span>
                                        </div>
                                        <p><strong>适用场景：</strong>入门级设备 (Intel i3 / AMD Ryzen 3)</p>
                                        <p><strong>特点：</strong>CPU推理模式，禁用高级特性，稳定运行</p>
                                        <p><strong>硬件要求：</strong>CPU 2核心以上，内存 ≥ 4GB</p>
                                    </div>
                                    <div v-else>
                                        <div class="mode-stats">
                                            <span class="stat-item"><strong>分辨率:</strong> 80×60</span>
                                            <span class="stat-item"><strong>跳帧:</strong> 1/8</span>
                                            <span class="stat-item"><strong>线程:</strong> 1</span>
                                        </div>
                                        <p><strong>适用场景：</strong>老旧设备或低功耗笔记本</p>
                                        <p><strong>特点：</strong>节能优先，禁用实时图表，最低资源占用</p>
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
                            <!-- ✅ 修复: 移除推理设备选项（当前仅支持 CPU） -->
                            <el-alert title="当前运行模式" type="info" :closable="false" show-icon
                                style="margin-bottom: 20px;">
                                <template #default>
                                    <p style="margin: 0;">🖥️ <strong>CPU 推理模式</strong></p>
                                    <p style="margin: 4px 0 0 0; font-size: 13px; color: var(--text-secondary);">
                                        系统当前使用 ONNX Runtime + Caffe SSD 进行纯 CPU 推理，无需 GPU 加速。
                                    </p>
                                </template>
                            </el-alert>

                            <el-form-item label="置信度阈值">
                                <div class="slider-group">
                                    <el-slider v-model="settingsConfig.confidence_threshold" :min="0.3" :max="0.9"
                                        :step="0.05" :format-tooltip="val => (val * 100).toFixed(0) + '%'"
                                        @change="handleConfigChange" />
                                    <span class="slider-hint">当前阈值: {{ (settingsConfig.confidence_threshold *
                                        100).toFixed(0) }}%</span>
                                </div>
                                <p class="field-description">
                                    较低的值会检测到更多人脸但可能增加误检，较高的值更严格但可能漏检。
                                </p>
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

                            <!-- ✅ 新增: 最大人脸数量配置 -->
                            <el-form-item label="最大检测人脸数量">
                                <div class="slider-group">
                                    <el-slider v-model="settingsConfig.max_faces" :min="1" :max="10"
                                        :step="1" show-stops @change="handleConfigChange" />
                                    <span class="slider-hint">最多检测 {{ settingsConfig.max_faces }} 张人脸</span>
                                </div>
                                <p class="field-description">
                                    设置实时检测时最多识别的人脸数量。较少的数量可提高检测速度，较多的数量可支持多人场景。
                                </p>
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

    // AI 模型配置（✅ 修复: 移除已废弃的模型切换参数）
    confidence_threshold: 0.25,

    // 检测参数
    resolution: '640x480',
    detect_every_n_frames: 2,
    max_faces: 10,  // ✅ 新增: 最大检测人脸数量

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
        // ✅ 修复: 移除已废弃的模型切换参数
        settingsConfig.confidence_threshold = backendConfig.confidence_threshold ?? 0.45
        settingsConfig.detect_every_n_frames = backendConfig.detect_every_n_frames ?? 2
        settingsConfig.max_faces = backendConfig.max_faces ?? 10
        settingsConfig.theme_mode = backendConfig.theme_mode ?? 'auto'
        // AI 音乐配置
        settingsConfig.music_volume = backendConfig.music_volume ?? 70
        settingsConfig.emotion_sensitivity = backendConfig.emotion_sensitivity ?? 50
        settingsConfig.rhythm_smoothness = backendConfig.rhythm_smoothness ?? 50
        settingsConfig.timbre_style = backendConfig.timbre_style ?? 'sine'

        // 保存原始配置用于重置
        originalConfig.value = { ...settingsConfig }

        console.debug('配置加载成功')
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
    console.debug(`切换性能模式: ${settingsConfig.performance_mode}`)

    // 立即保存配置（静默模式，避免提示重叠）
    await saveConfig(true)

    // 提示用户重启检测以生效
    ElMessage({
        message: '性能模式已更新，请重启实时检测以生效',
        type: 'success',
        duration: 3000
    })
}

// 保存设置（支持静默模式）
const saveConfig = async (silent = false) => {
    saving.value = true
    try {
        // 1. 同步到后端（✅ 修复: 移除已废弃的模型切换参数）
        const payload = {
            performance_mode: settingsConfig.performance_mode,
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
        // 重置为后端默认值（✅ 修复: 移除已废弃的模型切换参数）
        settingsConfig.performance_mode = 'high'
        settingsConfig.confidence_threshold = 0.45
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
/* ✅ 模式选择器行布局 */
.mode-selector-row {
    display: flex;
    align-items: center;
    gap: 12px;
    width: 100%;
}

.mode-selector-row .compact-select {
    flex: 1;
    min-width: 0;
}

.mode-selector-row .el-button {
    flex-shrink: 0;
}

/* ✅ 性能模式描述样式 */
.mode-description {
    margin-top: 12px;
    padding: 12px 14px;
    background: linear-gradient(135deg, rgba(113, 57, 255, 0.08), rgba(156, 78, 255, 0.05));
    border-left: 3px solid var(--primary);
    border-radius: 6px;
    width: 100%;
}

.mode-description p {
    margin: 6px 0;
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.6;
}

.mode-description strong {
    color: var(--primary);
    font-weight: 600;
}

/* ✅ 模式统计信息 */
.mode-stats {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 10px;
    padding: 8px 10px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 4px;
}

.mode-stats .stat-item {
    font-size: 12px;
    color: var(--text-secondary);
    padding: 4px 8px;
    background: rgba(113, 57, 255, 0.1);
    border-radius: 4px;
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

/* ✅ 新增: 字段描述样式 */
.field-description {
    margin-top: 8px;
    font-size: 12px;
    color: var(--text-secondary);
    opacity: 0.7;
    line-height: 1.5;
}

/* 响应式适配：小屏幕时恢复垂直排列 */
@media (max-width: 768px) {
    .hardware-info {
        grid-template-columns: 1fr;
    }
}
</style>
