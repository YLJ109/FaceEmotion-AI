import { ref, reactive } from 'vue'
import { getSystemConfig } from '@/api/modules/system'
import logger from '@/utils/logger'

export function usePerformanceMonitor() {
    const fps = ref(0)
    const isUsingGpu = ref(false)

    const perfFps = ref(0)
    const perfInferenceTime = ref(0)
    const perfDetectionLatency = ref(0)
    const perfNetworkLatency = ref(0)
    const perfLatency = ref(0)
    const perfSkipRate = ref(0)
    const perfGpuMemory = ref(0)
    const perfHttpLatency = ref(0)
    const perfErrorRate = ref(0)

    const currentResolution = reactive({ width: 320, height: 240 })
    const performanceModeConfig = reactive({
        frame_skip_threshold: 2,
        use_gpu: false
    })

    let EMA_ALPHA = 0.25
    let lastLoadedPerfMode = null

    let frameCount = 0
    let lastFpsTime = performance.now()
    let fpsInterval = null

    const startFpsMonitor = () => {
        frameCount = 0
        lastFpsTime = performance.now()
        fpsInterval = setInterval(() => {
            const now = performance.now()
            const elapsed = (now - lastFpsTime) / 1000
            fps.value = Math.round(frameCount / elapsed)
            frameCount = 0
            lastFpsTime = now
        }, 1000)
    }

    const stopFpsMonitor = () => {
        if (fpsInterval) {
            clearInterval(fpsInterval)
            fpsInterval = null
        }
        fps.value = 0
    }

    const countFrame = () => {
        frameCount++
    }

    const loadPerformanceConfig = async () => {
        try {
            const data = await getSystemConfig()
            const perfMode = data.config.performance_mode || 'cpu_high'
            

            if (perfMode === 'gpu') {
                currentResolution.width = 320
                currentResolution.height = 240
                performanceModeConfig.frame_skip_threshold = 2
                performanceModeConfig.use_gpu = true
                EMA_ALPHA = 0.25
            } else if (perfMode === 'cpu_high') {
                currentResolution.width = 256
                currentResolution.height = 192
                performanceModeConfig.frame_skip_threshold = 3
                performanceModeConfig.use_gpu = false
                EMA_ALPHA = 0.2
            } else if (perfMode === 'cpu_low') {
                currentResolution.width = 128
                currentResolution.height = 96
                performanceModeConfig.frame_skip_threshold = 5
                performanceModeConfig.use_gpu = false
                EMA_ALPHA = 0.15
            }

            lastLoadedPerfMode = perfMode
            isUsingGpu.value = performanceModeConfig.use_gpu
        } catch (error) {
            logger.error('加载性能模式配置失败:', error)
        }
    }

    const checkConfigChange = async () => {
        try {
            const data = await getSystemConfig()
            const currentMode = data.config.performance_mode || 'cpu_high'
            if (currentMode !== lastLoadedPerfMode) {
                
                lastLoadedPerfMode = currentMode
                await loadPerformanceConfig()
            }
        } catch (error) {
        }
    }

    const getEmaAlpha = () => EMA_ALPHA

    return {
        fps,
        isUsingGpu,
        perfFps,
        perfInferenceTime,
        perfDetectionLatency,
        perfNetworkLatency,
        perfLatency,
        perfSkipRate,
        perfGpuMemory,
        perfHttpLatency,
        perfErrorRate,
        currentResolution,
        performanceModeConfig,
        startFpsMonitor,
        stopFpsMonitor,
        countFrame,
        loadPerformanceConfig,
        checkConfigChange,
        getEmaAlpha
    }
}