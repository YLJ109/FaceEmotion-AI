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
                                        <el-option label="🎮 GPU 版本 (NVIDIA/CUDA)" value="gpu" />
                                        <el-option label="⚡ CPU 高性能模式" value="cpu_high" />
                                        <el-option label="🌙 CPU 低性能模式" value="cpu_low" />
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
                                    <div v-if="settingsConfig.performance_mode === 'gpu'">
                                        <div class="mode-stats">
                                            <span class="stat-item"><strong>推理设备:</strong> GPU (CUDA)</span>
                                            <span class="stat-item"><strong>分辨率:</strong> 320×240</span>
                                            <span class="stat-item"><strong>跳帧:</strong> 1/2</span>
                                        </div>
                                        <p><strong>适用场景：</strong>配备 NVIDIA GPU 的设备 (RTX 2060+)</p>
                                        <p><strong>特点：</strong>GPU 加速推理，最高性能，最低延迟</p>
                                        <p><strong>硬件要求：</strong>NVIDIA GPU + CUDA 环境，显存 ≥ 4GB</p>
                                    </div>
                                    <div v-else-if="settingsConfig.performance_mode === 'cpu_high'">
                                        <div class="mode-stats">
                                            <span class="stat-item"><strong>推理设备:</strong> CPU</span>
                                            <span class="stat-item"><strong>分辨率:</strong> 256×192</span>
                                            <span class="stat-item"><strong>跳帧:</strong> 1/3</span>
                                        </div>
                                        <p><strong>适用场景：</strong>高性能 CPU 设备 (Intel i5+ / AMD Ryzen 5+)</p>
                                        <p><strong>特点：</strong>多线程推理，平衡画质与流畅度</p>
                                        <p><strong>硬件要求：</strong>CPU 4核心以上，内存 ≥ 8GB</p>
                                    </div>
                                    <div v-else>
                                        <div class="mode-stats">
                                            <span class="stat-item"><strong>推理设备:</strong> CPU</span>
                                            <span class="stat-item"><strong>分辨率:</strong> 128×96</span>
                                            <span class="stat-item"><strong>跳帧:</strong> 1/5</span>
                                        </div>
                                        <p><strong>适用场景：</strong>低性能设备或老旧电脑</p>
                                        <p><strong>特点：</strong>节能优先，单线程推理，稳定运行</p>
                                        <p><strong>硬件要求：</strong>CPU 2核心以上，内存 ≥ 4GB</p>
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

                    <!-- 检测参数 -->
                    <div v-show="activeTab === 'detection'" class="tab-panel detection-panel">
                        <div class="detection-config">
                            <!-- 检测频率 -->
                            <div class="config-item">
                                <label class="config-label">
                                    <span class="label-icon">⚡</span>
                                    <span>检测频率</span>
                                </label>
                                <div class="config-content">
                                    <div class="slider-wrapper">
                                        <el-slider v-model="settingsConfig.detect_every_n_frames" 
                                            :min="1" :max="5" :step="1" 
                                            show-stops @change="handleConfigChange" />
                                    </div>
                                    <div class="config-hint">
                                        每 <strong>{{ settingsConfig.detect_every_n_frames }}</strong> 帧检测一次
                                    </div>
                                </div>
                            </div>

                            <!-- 最大检测人脸数量 -->
                            <div class="config-item">
                                <label class="config-label">
                                    <span class="label-icon">👥</span>
                                    <span>最大检测人脸数量</span>
                                </label>
                                <div class="config-content">
                                    <div class="slider-wrapper">
                                        <el-slider v-model="settingsConfig.max_faces" 
                                            :min="1" :max="10" :step="1" 
                                            show-stops @change="handleConfigChange" />
                                    </div>
                                    <div class="config-hint">
                                        最多检测 <strong>{{ settingsConfig.max_faces }}</strong> 张人脸
                                    </div>
                                    <p class="config-description">
                                        设置实时检测时最多识别的人脸数量。较少的数量可提高检测速度，较多的数量可支持多人场景。
                                    </p>
                                </div>
                            </div>

                            <!-- 自适应校准开关 -->
                            <div class="config-item">
                                <label class="config-label">
                                    <span class="label-icon">🧠</span>
                                    <span>自适应校准</span>
                                </label>
                                <div class="config-content">
                                    <div class="switch-wrapper">
                                        <el-switch 
                                            v-model="settingsConfig.enable_adaptive_calibration" 
                                            @change="handleConfigChange"
                                            active-text="已启用"
                                            inactive-text="已禁用"
                                            size="large"
                                        />
                                    </div>
                                    <p class="config-description">
                                        启用后，系统会根据用户反馈动态调整情绪识别的置信度，提高识别准确性。禁用后使用模型原始输出。
                                    </p>
                                </div>
                            </div>
                        </div>
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
                            <!-- ✅ 三个滑块改为一行排列 -->
                            <div class="music-sliders-row">
                                <el-form-item label="基础音量" class="slider-item">
                                    <div class="slider-group">
                                        <el-slider v-model="settingsConfig.music_volume" :min="0" :max="100" :step="1"
                                            :format-tooltip="val => val + '%'" @change="handleConfigChange" />
                                        <span class="slider-hint">当前音量: {{ settingsConfig.music_volume }}%</span>
                                    </div>
                                </el-form-item>

                                <el-form-item label="情绪敏感度" class="slider-item">
                                    <div class="slider-group">
                                        <el-slider v-model="settingsConfig.emotion_sensitivity" :min="0" :max="100"
                                            :step="1" :format-tooltip="val => val + '%'" @change="handleConfigChange" />
                                        <span class="slider-hint">当前敏感度: {{ settingsConfig.emotion_sensitivity }}%</span>
                                    </div>
                                </el-form-item>

                                <el-form-item label="节奏平滑度" class="slider-item">
                                    <div class="slider-group">
                                        <el-slider v-model="settingsConfig.rhythm_smoothness" :min="0" :max="100" :step="1"
                                            :format-tooltip="val => val + '%'" @change="handleConfigChange" />
                                        <span class="slider-hint">当前平滑度: {{ settingsConfig.rhythm_smoothness }}%</span>
                                    </div>
                                </el-form-item>
                            </div>

                            <el-form-item label="音色风格">
                                <el-select v-model="settingsConfig.timbre_style" style="width:100%"
                                    @change="handleConfigChange" class="compact-select">
                                    <el-option label="柔和正弦波 (Sine)" value="sine" />
                                    <el-option label="明亮三角波 (Triangle)" value="triangle" />
                                    <el-option label="温暖锯齿波 (Sawtooth)" value="sawtooth" />
                                    <el-option label="复古方波 (Square)" value="square" />
                                </el-select>
                            </el-form-item>

                            <el-form-item label="自动播放音乐">
                                <div class="toggle-group">
                                    <span class="toggle-label">检测完成后自动播放情绪音乐</span>
                                    <el-switch v-model="settingsConfig.auto_play_music" @change="handleConfigChange" />
                                </div>
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { ElMessage } from 'element-plus'
import { Setting, Cpu, Monitor, VideoCamera, Brush, Odometer, Headset } from '@element-plus/icons-vue'
import { getSystemConfig, updateSystemConfig, getPerformanceRecommend } from '@/api/modules/system'
import generativeAudio from '@/utils/generativeAudio'
import logger from '@/utils/logger'

const themeStore = useThemeStore()

// 系统设置选项卡状态
const activeTab = ref('performance') // 默认显示性能优化
const settingsTabs = [
    { key: 'performance', label: '性能优化', icon: 'Odometer' },
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
    enable_adaptive_calibration: false,  // ✅ 新增: 自适应校准开关

    // 界面设置
    theme_mode: 'auto',

    // AI 音乐配置
    music_volume: 70,
    emotion_sensitivity: 50,
    rhythm_smoothness: 50,
    timbre_style: 'sine',
    auto_play_music: false  // ✅ 新增: 是否在检测完成后自动播放音乐
})

const saving = ref(false)
const detecting = ref(false)
const originalConfig = ref(null)

// 硬件信息
const hardwareInfo = reactive({
    gpu: null,
    cpu: null,
    cpuCores: null,
    memory: null,
    recommendedMode: null
})

// ✅ 新增: 自动检测并分配模式
const autoDetectMode = async () => {
    try {
        const data = await getPerformanceRecommend()

        // 更新硬件信息
        hardwareInfo.gpu = data.gpu || '未检测到'
        hardwareInfo.cpu = data.cpu || '未知'
        hardwareInfo.cpuCores = data.cpu_cores || '未知'
        hardwareInfo.memory = data.memory || '未知'
        hardwareInfo.recommendedMode = data.recommended_mode || 'cpu_high'

        return hardwareInfo.recommendedMode
    } catch (error) {
        console.error('❌ 自动检测失败:', error)
        // 降级到 CPU 高性能模式
        return 'cpu_high'
    }
}

// ✅ 新增: 组件挂载时自动检测并应用推荐模式
const applyAutoMode = async () => {
    const recommendedMode = await autoDetectMode()
    settingsConfig.performance_mode = recommendedMode
    await saveConfig(true)
    
    // 显示提示
    const modeName = recommendedMode === 'gpu' ? 'GPU 版本' : 
                     recommendedMode === 'cpu_high' ? 'CPU 高性能模式' : 'CPU 低性能模式'
    ElMessage({
        message: `✅ 已自动检测并应用 ${modeName}`,
        type: 'success',
        duration: 3000
    })
}

// 从后端加载配置
const loadConfig = async () => {
    try {
        const data = await getSystemConfig()

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
        const data = await getPerformanceRecommend()

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
        logger.error('智能检测失败:', error)
        ElMessage.error('检测失败，请手动选择模式')
    } finally {
        detecting.value = false
    }
}

// ✅ 修改: 性能模式切换处理
const handlePerformanceModeChange = async () => {
    

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
        // 1. 同步到后端（✅ 修复: 添加 max_faces 参数）
        const payload = {
            performance_mode: settingsConfig.performance_mode,
            confidence_threshold: settingsConfig.confidence_threshold,
            detect_every_n_frames: settingsConfig.detect_every_n_frames,
            max_faces: settingsConfig.max_faces,  // ✅ 新增: 最大检测人脸数
            enable_adaptive_calibration: settingsConfig.enable_adaptive_calibration,  // ✅ 新增: 自适应校准开关
            theme_mode: settingsConfig.theme_mode,
            // AI 音乐配置
            music_volume: settingsConfig.music_volume,
            emotion_sensitivity: settingsConfig.emotion_sensitivity,
            rhythm_smoothness: settingsConfig.rhythm_smoothness,
            timbre_style: settingsConfig.timbre_style
        }

        await updateSystemConfig(payload)

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

// ===== 连接设置 =====
const formatServerUrl = (input) => {
  let url = input.trim()
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    url = 'http://' + url
  }
  return url.replace(/\/+$/, '')
}

const handleServerSave = () => {
  const url = formatServerUrl(serverInput.value)
  ElMessage.info('正在切换服务器地址...')
  setServerUrl(url)
}

const handleServerReset = () => {
  resetServerUrl()
}

const testConnection = async () => {
  testing.value = true
  testResult.value = null
  try {
    const url = formatServerUrl(serverInput.value || currentServerUrl.value)
    const res = await fetch(`${url}/api/health`, { signal: AbortSignal.timeout(3000) })
    if (res.ok) {
      testResult.value = { ok: true, msg: '✅ 连接成功！服务器运行正常' }
    } else {
      testResult.value = { ok: false, msg: `❌ 服务器返回 ${res.status}` }
    }
  } catch (e) {
    testResult.value = { ok: false, msg: `❌ 无法连接: ${e.message}` }
  } finally {
    testing.value = false
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

// 组件挂载时加载配置并自动检测模式
onMounted(async () => {
    await loadConfig()
    // ✅ 自动检测硬件并应用推荐模式（仅首次访问或配置为空时）
    if (!settingsConfig.performance_mode || settingsConfig.performance_mode === '') {
        await applyAutoMode()
    }
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

/* ✅ 检测参数面板全新布局样式 */
.detection-panel {
    padding: 8px 0;
}

.detection-config {
    display: flex;
    flex-direction: column;
    gap: 24px;
}

.config-item {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.config-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary);
    cursor: default;
}

.label-icon {
    font-size: 16px;
    width: 20px;
    text-align: center;
}

.config-content {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 16px;
    background: rgba(255, 255, 255, 0.02);
    border-radius: 8px;
    border: 1px solid rgba(113, 57, 255, 0.1);
}

.config-hint {
    font-size: 13px;
    color: var(--text-secondary);
    padding-left: 8px;
    
    strong {
        color: var(--primary);
        font-weight: 600;
    }
}

.config-description {
    font-size: 12px;
    color: var(--text-secondary);
    opacity: 0.7;
    line-height: 1.5;
    padding-left: 8px;
    margin: 0;
}

.slider-wrapper {
    width: 100%;
}

.slider-wrapper .el-slider {
    width: 100%;
}

.switch-wrapper {
    display: flex;
    align-items: center;
}

.resolution-select {
    width: 100%;
    max-width: 280px;
}

/* ✅ AI音乐配置滑块横向排列 */
.music-sliders-row {
    display: flex;
    gap: 24px;
    width: 100%;
}

.music-sliders-row .slider-item {
    flex: 1;
    min-width: 0;
}

.music-sliders-row .slider-item .el-form-item__label {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 8px;
}

.music-sliders-row .slider-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.music-sliders-row .slider-hint {
    font-size: 12px;
    color: var(--text-secondary);
}

/* 响应式适配 */
/* ===== 连接设置 ===== */
.server-input-row {
    display: flex;
    gap: 10px;
    width: 100%;
}

.server-input-row .el-input {
    flex: 1;
}

.server-test-row {
    display: flex;
    align-items: center;
    gap: 12px;
}

.test-pass { color: #26DE81; font-weight: 600; font-size: 13px; }
.test-fail { color: #FF4757; font-weight: 600; font-size: 13px; }

.server-input-row code,
.field-description code,
.tip-box code {
    background: rgba(162, 89, 255, 0.15);
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 12px;
    color: var(--primary);
}

.tip-box {
    padding: 12px 14px;
    background: rgba(10, 189, 227, 0.06);
    border-left: 3px solid #0ABDE3;
    border-radius: 6px;
    width: 100%;
}

.tip-box p {
    margin: 6px 0;
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.6;
}

.tip-box strong {
    color: var(--text);
    font-weight: 600;
}

@media (max-width: 768px) {
    .hardware-info {
        grid-template-columns: 1fr;
    }
    
    .config-content {
        padding: 12px;
    }
    
    .music-sliders-row {
        flex-direction: column;
        gap: 16px;
    }
    
    .server-input-row {
        flex-direction: column;
    }
}
</style>
