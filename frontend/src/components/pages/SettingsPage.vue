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

                    <!-- 连接配置 -->
                    <div v-show="activeTab === 'connection'" class="tab-panel">
                        <el-form label-position="top" size="large">
                            <el-form-item label="WebSocket 服务器地址">
                                <el-input v-model="settingsConfig.ws_url" placeholder="ws://localhost:8000/ws/stream"
                                    @blur="handleConfigChange" class="compact-input" />
                            </el-form-item>
                        </el-form>
                    </div>

                    <!-- 操作按钮 -->
                    <div class="settings-actions">
                        <el-button type="primary" plain round @click="resetConfig" size="large">
                            恢复默认
                        </el-button>
                        <el-button type="primary" round @click="saveConfig" :loading="saving" size="large">
                            {{ saving ? '保存中...' : '保存设置' }}
                        </el-button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { ElMessage } from 'element-plus'
import { Setting, Cpu, Monitor, VideoCamera, Connection, Brush } from '@element-plus/icons-vue'
import { API } from '@/api/config'

const themeStore = useThemeStore()

// 系统设置选项卡状态
const activeTab = ref('ai') // 默认显示 AI 模型配置
const settingsTabs = [
    { key: 'ai', label: 'AI 模型配置', icon: 'Cpu' },
    { key: 'detection', label: '检测参数', icon: 'VideoCamera' },
    { key: 'ui', label: '界面设置', icon: 'Brush' },
    { key: 'connection', label: '连接配置', icon: 'Connection' }
]

// 系统设置配置（与后端同步）
const settingsConfig = reactive({
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

    // 连接配置
    ws_url: 'ws://localhost:8000/ws/stream'
})

const saving = ref(false)
const originalConfig = ref(null)

// 从后端加载配置
const loadConfig = async () => {
    try {
        const response = await fetch(`${API.baseUrl}/api/config`)
        if (!response.ok) throw new Error('获取配置失败')
        const data = await response.json()

        // 同步后端配置到前端
        const backendConfig = data.config
        settingsConfig.use_gpu = backendConfig.use_gpu ?? true
        settingsConfig.use_onnx_face_detector = backendConfig.use_onnx_face_detector ?? false
        settingsConfig.emotion_model = backendConfig.emotion_model ?? './models/emotion_model.onnx'
        settingsConfig.confidence_threshold = backendConfig.confidence_threshold ?? 0.6
        settingsConfig.detect_every_n_frames = backendConfig.detect_every_n_frames ?? 2
        settingsConfig.theme_mode = backendConfig.theme_mode ?? 'auto'

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

// 保存设置（支持静默模式）
const saveConfig = async (silent = false) => {
    saving.value = true
    try {
        // 1. 同步到后端
        const payload = {
            use_gpu: settingsConfig.use_gpu,
            use_onnx_face_detector: settingsConfig.use_onnx_face_detector,
            emotion_model: settingsConfig.emotion_model,
            confidence_threshold: settingsConfig.confidence_threshold,
            detect_every_n_frames: settingsConfig.detect_every_n_frames,
            theme_mode: settingsConfig.theme_mode
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
            ElMessage.success('✅ 设置已保存到后端并持久化')
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
        settingsConfig.use_gpu = true
        settingsConfig.use_onnx_face_detector = false
        settingsConfig.emotion_model = './models/emotion_model.onnx'
        settingsConfig.confidence_threshold = 0.6
        settingsConfig.detect_every_n_frames = 2
        settingsConfig.theme_mode = 'auto'
        settingsConfig.ws_url = 'ws://localhost:8000/ws/stream'
        settingsConfig.resolution = '640x480'

        // 同步保存到后端
        await saveConfig(true)

        ElMessage.success('✅ 已恢复默认配置')
    } catch (error) {
        ElMessage.error('恢复配置失败')
    }
}

// 组件挂载时加载配置
onMounted(() => {
    loadConfig()
})
</script>
