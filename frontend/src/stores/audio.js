/**
 * 音频状态管理 Store
 * - 管理麦克风状态
 * - 音频采集控制
 * - 音量监控
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import AudioCapture from '@/utils/audioCapture'

export const useAudioStore = defineStore('audio', () => {
    // 状态
    const isMicOn = ref(false)
    const volumeLevel = ref(0)
    const audioCapture = new AudioCapture({
        sampleRate: 16000,
        compressionEnabled: true,  // ✅ 启用音频压缩
        onAudioData: (pcmData) => {
            // 默认处理器,可通过 setOnAudioData 覆盖
            if (_onAudioDataCallback.value && pcmData.byteLength > 0) {
                _onAudioDataCallback.value(pcmData)
            }
        }
    })

    // 内部回调
    const _onAudioDataCallback = ref(null)

    // 计算属性
    const isCapturing = computed(() => audioCapture.isCapturing)
    const hasPermission = computed(() => isMicOn.value)

    // 方法
    /**
     * 启动麦克风
     */
    async function startMicrophone() {
        try {
            const success = await audioCapture.start()
            if (success) {
                isMicOn.value = true
                console.log('🎤 麦克风已启动')

                // 开始监控音量
                _startVolumeMonitoring()

                return true
            } else {
                console.error('❌ 麦克风启动失败')
                return false
            }
        } catch (error) {
            console.error('❌ 麦克风启动异常:', error)
            return false
        }
    }

    /**
     * 停止麦克风
     */
    function stopMicrophone() {
        audioCapture.stop()
        isMicOn.value = false
        volumeLevel.value = 0
        _stopVolumeMonitoring()
        console.log('🔇 麦克风已停止')
    }

    /**
     * 切换麦克风状态
     */
    async function toggleMicrophone() {
        if (isMicOn.value) {
            stopMicrophone()
            return false
        } else {
            const success = await startMicrophone()
            return success
        }
    }

    /**
     * 设置音频数据回调
     */
    function setOnAudioData(callback) {
        _onAudioDataCallback.value = callback
    }

    /**
     * 获取当前音量等级 (0-1)
     */
    function getVolumeLevel() {
        return audioCapture.getVolumeLevel()
    }

    /**
     * 开始音量监控
     */
    let _volumeMonitorInterval = null
    function _startVolumeMonitoring() {
        _stopVolumeMonitoring()
        _volumeMonitorInterval = setInterval(() => {
            volumeLevel.value = audioCapture.getVolumeLevel()
        }, 100)
    }

    /**
     * 停止音量监控
     */
    function _stopVolumeMonitoring() {
        if (_volumeMonitorInterval) {
            clearInterval(_volumeMonitorInterval)
            _volumeMonitorInterval = null
        }
    }

    /**
     * 重置状态
     */
    function reset() {
        stopMicrophone()
        _onAudioDataCallback.value = null
    }

    return {
        // 状态
        isMicOn,
        volumeLevel,
        isCapturing,
        hasPermission,

        // 方法
        startMicrophone,
        stopMicrophone,
        toggleMicrophone,
        setOnAudioData,
        getVolumeLevel,
        reset
    }
})
