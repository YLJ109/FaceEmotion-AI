/**
 * Web Worker 检测服务
 * 封装 Web Worker 通信，提供简洁的检测 API
 */
import logger from '@/utils/logger'

class WorkerDetectionService {
    constructor() {
        this.worker = null
        this.pendingCallbacks = new Map()
        this.callbackId = 0
        this.isInitialized = false
        this.workerPath = '/src/workers/detection.worker.js'
    }

    /**
     * 初始化 Worker
     */
    async initialize() {
        if (this.isInitialized && this.worker) {
            return
        }

        return new Promise((resolve, reject) => {
            try {
                // 创建 Web Worker
                this.worker = new Worker(new URL(this.workerPath, import.meta.url))

                // 设置消息处理器
                this.worker.onmessage = (e) => {
                    const { type, id, data, error } = e.data

                    if (type === 'result' && this.pendingCallbacks.has(id)) {
                        const callback = this.pendingCallbacks.get(id)
                        this.pendingCallbacks.delete(id)
                        callback(null, data)
                    } else if (type === 'error' && this.pendingCallbacks.has(id)) {
                        const callback = this.pendingCallbacks.get(id)
                        this.pendingCallbacks.delete(id)
                        callback(new Error(error))
                    }
                }

                this.worker.onerror = (error) => {
                    logger.error('Worker error:', error)
                    this.pendingCallbacks.forEach((callback) => {
                        callback(error)
                    })
                    this.pendingCallbacks.clear()
                }

                // 验证 Worker 是否正常工作
                const pingId = this._generateId()
                this.pendingCallbacks.set(pingId, (err) => {
                    if (err) {
                        reject(err)
                    } else {
                        this.isInitialized = true
                        logger.info('[WorkerDetection] Web Worker 初始化完成')
                        resolve()
                    }
                })

                this.worker.postMessage({ type: 'ping', id: pingId })

            } catch (error) {
                logger.error('Worker 创建失败:', error)
                reject(error)
            }
        })
    }

    /**
     * 检测图像中的人脸
     * @param {ImageData} imageData - 图像数据
     * @param {number} width - 图像宽度
     * @param {number} height - 图像高度
     * @returns {Promise<Object>} 检测结果
     */
    async detect(imageData, width, height) {
        if (!this.isInitialized) {
            await this.initialize()
        }

        return new Promise((resolve, reject) => {
            const id = this._generateId()

            this.pendingCallbacks.set(id, (error, data) => {
                if (error) {
                    reject(error)
                } else {
                    resolve(data)
                }
            })

            // 发送检测请求
            this.worker.postMessage({
                type: 'detect',
                id,
                data: {
                    imageData,
                    width,
                    height
                }
            }, [imageData.data.buffer]) // 传输缓冲区所有权，避免复制
        })
    }

    /**
     * 销毁 Worker
     */
    destroy() {
        if (this.worker) {
            this.worker.terminate()
            this.worker = null
        }
        this.isInitialized = false
        this.pendingCallbacks.clear()
        logger.info('[WorkerDetection] Web Worker 已销毁')
    }

    /**
     * 生成唯一回调 ID
     */
    _generateId() {
        return ++this.callbackId
    }

    /**
     * 检查是否支持 Web Worker
     */
    static isSupported() {
        return typeof Worker !== 'undefined'
    }
}

// 创建单例
export const workerDetectionService = new WorkerDetectionService()
export default workerDetectionService