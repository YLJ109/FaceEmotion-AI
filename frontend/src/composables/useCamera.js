import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { logFeatureUsage } from '@/utils/analytics'
import logger from '@/utils/logger'

export function useCamera() {
    const isCameraOn = ref(false)
    const cameras = ref([])
    const currentCameraIndex = ref(0)
    const isSwitchingCamera = ref(false)
    let stream = null

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

    const switchCamera = async (index) => {
        if (index === currentCameraIndex.value || isSwitchingCamera.value) return

        isSwitchingCamera.value = true
        currentCameraIndex.value = index

        try {
            const camera = cameras.value[index]
            if (!camera) return

            if (stream) {
                stream.getTracks().forEach(t => t.stop())
                stream = null
            }

            const constraints = {
                video: {
                    deviceId: camera.deviceId ? { exact: camera.deviceId } : undefined
                }
            }

            stream = await navigator.mediaDevices.getUserMedia(constraints)
            ElMessage.success(`已切换到 ${camera.label}`)
            return stream
        } catch (error) {
            logger.error('切换摄像头失败:', error)
            ElMessage.error('切换摄像头失败')
            currentCameraIndex.value = index === 0 ? 1 : 0
            return null
        } finally {
            isSwitchingCamera.value = false
        }
    }

    const startCamera = async (cameraIndex = 0) => {
        try {
            await enumerateCameras()

            if (stream) stream.getTracks().forEach(t => t.stop())

            const camera = cameras.value[cameraIndex]
            const constraints = camera && camera.deviceId
                ? { video: { deviceId: { exact: camera.deviceId } } }
                : { video: true }

            stream = await navigator.mediaDevices.getUserMedia(constraints)
            currentCameraIndex.value = cameraIndex

            logFeatureUsage('realtime', { action: 'start_camera' })
            isCameraOn.value = true
            return stream
        } catch (error) {
            logger.error('摄像头启动失败:', error)
            if (error.name === 'NotAllowedError') {
                ElMessage.error('摄像头权限被拒绝，请在浏览器设置中允许访问')
            } else if (error.name === 'NotFoundError') {
                ElMessage.error('未检测到摄像头设备，请检查连接')
            } else if (error.name === 'NotReadableError') {
                ElMessage.error('摄像头被其他应用占用，请关闭后重试')
            } else if (error.name === 'OverconstrainedError') {
                ElMessage.error('摄像头不支持请求的分辨率')
            } else {
                ElMessage.error(`摄像头启动失败: ${error.message}`)
            }
            return null
        }
    }

    const stopCamera = () => {
        if (stream) {
            stream.getTracks().forEach(t => t.stop())
            stream = null
        }
        isCameraOn.value = false
    }

    const toggleCamera = () => {
        return isCameraOn.value ? stopCamera() : startCamera()
    }

    const getStream = () => stream

    return {
        isCameraOn,
        cameras,
        currentCameraIndex,
        isSwitchingCamera,
        enumerateCameras,
        switchCamera,
        startCamera,
        stopCamera,
        toggleCamera,
        getStream
    }
}