/**
 * 动态分辨率调整管理器
 * 根据帧率自动调整摄像头分辨率，实现自适应性能优化
 */

import logger from '@/utils/logger'

class AdaptiveResolutionManager {
    constructor(videoElement) {
        this.videoElement = videoElement
        this.targetFps = 30
        this.minResolution = { width: 320, height: 240 }
        this.maxResolution = { width: 1280, height: 720 }
        this.currentResolution = { width: 640, height: 480 }
        
        this.fpsHistory = []
        this.adaptationInterval = null
        this.adaptationEnabled = true
        
        this.resolutionLevels = [
            { width: 320, height: 240, label: 'QVGA' },
            { width: 480, height: 360, label: 'nHD' },
            { width: 640, height: 480, label: 'VGA' },
            { width: 800, height: 600, label: 'SVGA' },
            { width: 960, height: 720, label: 'HD-' },
            { width: 1280, height: 720, label: 'HD' }
        ]
    }

    /**
     * 开始监控
     */
    start() {
        if (this.adaptationInterval) {
            clearInterval(this.adaptationInterval)
        }
        
        this.adaptationInterval = setInterval(() => {
            this._adapt()
        }, 2000)
        
        logger.info('[AdaptiveResolution] 动态分辨率管理器已启动')
    }

    /**
     * 停止监控
     */
    stop() {
        if (this.adaptationInterval) {
            clearInterval(this.adaptationInterval)
            this.adaptationInterval = null
        }
        logger.info('[AdaptiveResolution] 动态分辨率管理器已停止')
    }

    /**
     * 启用/禁用自适应
     */
    setEnabled(enabled) {
        this.adaptationEnabled = enabled
        if (enabled && !this.adaptationInterval) {
            this.start()
        } else if (!enabled) {
            this.stop()
        }
    }

    /**
     * 自适应调整
     */
    _adapt() {
        if (!this.adaptationEnabled) return
        
        const avgFps = this.fpsHistory.reduce((sum, fps) => sum + fps, 0) / (this.fpsHistory.length || 1)
        
        if (avgFps < this.targetFps * 0.8) {
            // 帧率过低，降低分辨率
            this._decreaseResolution()
        } else if (avgFps > this.targetFps * 1.1 && 
                   this._canIncreaseResolution()) {
            // 帧率充足，提高分辨率
            this._increaseResolution()
        }
        
        // 清空历史记录
        this.fpsHistory = []
    }

    /**
     * 降低分辨率
     */
    _decreaseResolution() {
        const currentIndex = this._getCurrentResolutionIndex()
        
        if (currentIndex > 0) {
            const newResolution = this.resolutionLevels[currentIndex - 1]
            this._updateResolution(newResolution.width, newResolution.height)
            logger.info(`[AdaptiveResolution] 降低分辨率: ${this.currentResolution.width}x${this.currentResolution.height}`)
        }
    }

    /**
     * 提高分辨率
     */
    _increaseResolution() {
        const currentIndex = this._getCurrentResolutionIndex()
        
        if (currentIndex < this.resolutionLevels.length - 1) {
            const newResolution = this.resolutionLevels[currentIndex + 1]
            this._updateResolution(newResolution.width, newResolution.height)
            logger.info(`[AdaptiveResolution] 提高分辨率: ${this.currentResolution.width}x${this.currentResolution.height}`)
        }
    }

    /**
     * 检查是否可以提高分辨率
     */
    _canIncreaseResolution() {
        const currentIndex = this._getCurrentResolutionIndex()
        return currentIndex < this.resolutionLevels.length - 1
    }

    /**
     * 获取当前分辨率索引
     */
    _getCurrentResolutionIndex() {
        const currentArea = this.currentResolution.width * this.currentResolution.height
        
        for (let i = this.resolutionLevels.length - 1; i >= 0; i--) {
            const levelArea = this.resolutionLevels[i].width * this.resolutionLevels[i].height
            if (currentArea >= levelArea) {
                return i
            }
        }
        
        return 0
    }

    /**
     * 更新分辨率
     */
    _updateResolution(width, height) {
        this.currentResolution = { width, height }
        
        // 更新 video 约束
        if (this.videoElement && this.videoElement.srcObject) {
            const tracks = this.videoElement.srcObject.getVideoTracks()
            tracks.forEach(track => {
                track.applyConstraints({
                    width: { ideal: width },
                    height: { ideal: height }
                }).catch(error => {
                    logger.warn('[AdaptiveResolution] 分辨率调整失败:', error)
                })
            })
        }
    }

    /**
     * 报告帧率
     */
    reportFps(fps) {
        this.fpsHistory.push(fps)
        if (this.fpsHistory.length > 30) {
            this.fpsHistory.shift()
        }
    }

    /**
     * 设置目标帧率
     */
    setTargetFps(fps) {
        this.targetFps = fps
    }

    /**
     * 获取当前分辨率
     */
    getCurrentResolution() {
        return { ...this.currentResolution }
    }

    /**
     * 获取可用分辨率列表
     */
    getAvailableResolutions() {
        return this.resolutionLevels
    }

    /**
     * 手动设置分辨率
     */
    setResolution(width, height) {
        const level = this.resolutionLevels.find(
            r => r.width === width && r.height === height
        )
        
        if (level) {
            this._updateResolution(width, height)
        } else {
            logger.warn(`[AdaptiveResolution] 不支持的分辨率: ${width}x${height}`)
        }
    }

    /**
     * 销毁
     */
    destroy() {
        this.stop()
        this.videoElement = null
    }
}

export { AdaptiveResolutionManager }
export default AdaptiveResolutionManager