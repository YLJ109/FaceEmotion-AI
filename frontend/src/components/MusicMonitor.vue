<template>
    <div v-if="isVisible" class="music-monitor">
        <div class="monitor-header">
            <div class="monitor-title">
                <el-icon>
                    <Headset />
                </el-icon>
                <span>AI 生成式音乐</span>
            </div>
            <el-button class="close-btn" circle size="small" @click="toggleVisible">
                <el-icon>
                    <Close />
                </el-icon>
            </el-button>
        </div>

        <div class="monitor-body">
            <!-- 音乐控制按钮 -->
            <div class="control-row">
                <el-button class="music-control-btn" :type="musicOn ? 'danger' : 'success'" round @click="toggleMusic">
                    <el-icon>
                        <component :is="musicOn ? 'VideoPause' : 'VideoPlay'" />
                    </el-icon>
                    <span>{{ musicOn ? '停止音乐' : '开启音乐' }}</span>
                </el-button>
            </div>

            <!-- 音乐状态 -->
            <div class="status-row">
                <span class="status-label">状态</span>
                <span class="status-value" :class="musicOn ? 'active' : 'inactive'">
                    {{ musicOn ? '播放中' : '已停止' }}
                </span>
            </div>

            <!-- 当前情绪 -->
            <div class="metric-row">
                <div class="metric-label">
                    <el-icon class="metric-icon">
                        <User />
                    </el-icon>
                    <span>当前情绪</span>
                </div>
                <div class="metric-value">
                    {{ currentEmotion }}
                </div>
            </div>

            <!-- BPM节奏 -->
            <div class="metric-row">
                <div class="metric-label">
                    <el-icon class="metric-icon">
                        <Clock />
                    </el-icon>
                    <span>节奏 (BPM)</span>
                </div>
                <div class="metric-value">
                    {{ currentBpm }}
                </div>
            </div>

            <!-- 音量控制 -->
            <div class="volume-row">
                <div class="metric-label">
                    <el-icon class="metric-icon">
                        <VideoPlay />
                    </el-icon>
                    <span>音量</span>
                </div>
                <div class="volume-control">
                    <el-slider v-model="localVolume" :min="0" :max="100" @input="handleVolumeChange"
                        :show-tooltip="true" />
                </div>
                <div class="volume-value">
                    {{ volume }}%
                </div>
            </div>

            <!-- 音频质量 -->
            <div class="metric-row">
                <div class="metric-label">
                    <el-icon class="metric-icon">
                        <Star />
                    </el-icon>
                    <span>音频质量</span>
                </div>
                <div class="metric-value good">
                    高清
                </div>
            </div>

            <!-- 建议 -->
            <div v-if="suggestions.length > 0" class="suggestions">
                <div v-for="(tip, index) in suggestions" :key="index" class="suggestion-item">
                    <el-icon class="suggestion-icon">
                        <Warning />
                    </el-icon>
                    <span>{{ tip }}</span>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Close, Headset, User, Clock, Star, Warning, VideoPlay, VideoPause } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import generativeAudio from '@/utils/generativeAudio'
import wsManager from '@/api/websocket'

const props = defineProps({
    musicOn: { type: Boolean, default: false },
    currentEmotion: { type: String, default: 'neutral' },
    currentBpm: { type: Number, default: 100 },
    volume: { type: Number, default: 50 }
})

const emit = defineEmits(['update:music-on', 'update:volume'])

const isVisible = ref(false)
let latestMusicParams = null

// 本地音量状态
const localVolume = ref(props.volume)

// 建议
const suggestions = computed(() => {
    const tips = []

    if (!props.musicOn) {
        tips.push('点击顶部"AI音乐"按钮开启音乐')
    }

    if (props.currentBpm < 80) {
        tips.push('节奏较慢，适合放松场景')
    } else if (props.currentBpm > 140) {
        tips.push('节奏较快，适合运动场景')
    }

    return tips
})

const toggleVisible = () => {
    isVisible.value = !isVisible.value
}

// 音乐开关
const toggleMusic = async () => {
    if (!props.musicOn) {
        // 开启音乐
        try {
            await generativeAudio.init()
            if (latestMusicParams) {
                generativeAudio.playMusic(latestMusicParams)
            }
            emit('update:music-on', true)
            ElMessage.success('🎵 AI 生成式音乐已开启')
        } catch (error) {
            console.error('❌ 开启音乐失败:', error)
            ElMessage.error('开启音乐失败,请检查浏览器权限')
        }
    } else {
        // 关闭音乐
        generativeAudio.stop()
        emit('update:music-on', false)
        ElMessage.info('⏹️ 音乐已停止')
    }
}

// 音量控制
const handleVolumeChange = (value) => {
    generativeAudio.setVolume(value)
    emit('update:volume', value)
}

// 监听导航栏事件和WebSocket消息
onMounted(() => {
    const handleToggle = () => {
        toggleVisible()
    }
    window.addEventListener('toggle-music-panel', handleToggle)

    // 监听WebSocket消息
    wsManager.onMessage((data) => {
        if (data.type === 'result' && data.music_params) {
            latestMusicParams = data.music_params
        }
    })

    onUnmounted(() => {
        window.removeEventListener('toggle-music-panel', handleToggle)
    })
})
</script>

<style scoped>
.music-monitor {
    position: fixed;
    top: 60px;
    right: 24px;
    width: 280px;
    background: rgba(0, 0, 0, 0.85);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 12px;
    z-index: 9999;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    animation: slideIn 0.3s ease;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.monitor-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.monitor-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    font-weight: 700;
    color: rgba(255, 255, 255, 0.95);
}

.monitor-title .el-icon {
    font-size: 16px;
    color: #9B59B6;
}

.close-btn {
    background: rgba(255, 255, 255, 0.1) !important;
    border: none !important;
    color: rgba(255, 255, 255, 0.7) !important;
}

.close-btn:hover {
    background: rgba(255, 71, 87, 0.2) !important;
    color: #FF4757 !important;
}

.monitor-body {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

/* 控制按钮 */
.control-row {
    display: flex;
    justify-content: center;
    margin-bottom: 8px;
}

.music-control-btn {
    width: 100%;
    font-size: 14px !important;
    font-weight: 600 !important;
}

/* 音量控制 */
.volume-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 12px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
}

.volume-control {
    flex: 1;
}

.volume-value {
    font-size: 13px;
    font-weight: 700;
    color: #9B59B6;
    min-width: 40px;
    text-align: right;
    font-family: 'Consolas', 'Monaco', monospace;
}

/* 状态行 */
.status-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
}

.status-label {
    font-size: 13px;
    color: rgba(255, 255, 255, 0.7);
    font-weight: 600;
}

.status-value {
    font-size: 13px;
    font-weight: 700;
}

.status-value.active {
    color: #67C23A;
    text-shadow: 0 0 8px rgba(103, 194, 58, 0.4);
}

.status-value.inactive {
    color: #909399;
}

/* 指标行 */
.metric-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    transition: background 0.2s ease;
}

.metric-row:hover {
    background: rgba(255, 255, 255, 0.08);
}

.metric-label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: rgba(255, 255, 255, 0.7);
    font-weight: 600;
}

.metric-icon {
    font-size: 14px;
}

.metric-value {
    font-size: 14px;
    font-weight: 800;
    font-family: 'Consolas', 'Monaco', monospace;
    color: #fff;
}

.metric-value.good {
    color: #26DE81;
    text-shadow: 0 0 8px rgba(38, 222, 129, 0.4);
}

/* 建议 */
.suggestions {
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.suggestion-item {
    display: flex;
    align-items: flex-start;
    gap: 6px;
    font-size: 11px;
    color: rgba(255, 255, 255, 0.8);
    line-height: 1.4;
}

.suggestion-icon {
    font-size: 12px;
    color: #F99E1A;
    flex-shrink: 0;
    margin-top: 1px;
}
</style>
