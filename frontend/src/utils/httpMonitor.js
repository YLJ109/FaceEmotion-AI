/**
 * HTTP性能监控工具
 * - 追踪所有HTTP请求的延迟和错误率
 * - 提供实时统计数据
 */

class HttpMonitor {
    constructor() {
        this.requestTimes = []
        this.errorCount = 0
        this.totalRequests = 0
        this.windowSize = 100  // 统计窗口大小
    }

    /**
     * 包装fetch调用,自动记录性能数据
     */
    async monitoredFetch(url, options = {}) {
        const startTime = performance.now()
        this.totalRequests++

        try {
            const response = await fetch(url, options)
            const endTime = performance.now()
            const latency = endTime - startTime

            // 记录延迟
            this.recordLatency(latency)

            // 检查是否为错误响应
            if (!response.ok) {
                this.recordError()
            }

            return response
        } catch (error) {
            const endTime = performance.now()
            const latency = endTime - startTime
            this.recordLatency(latency)
            this.recordError()
            throw error
        }
    }

    /**
     * 记录延迟
     */
    recordLatency(latency) {
        this.requestTimes.push(latency)

        // 保持窗口大小
        if (this.requestTimes.length > this.windowSize) {
            this.requestTimes.shift()
        }
    }

    /**
     * 记录错误
     */
    recordError() {
        this.errorCount++
    }

    /**
     * 获取平均HTTP延迟
     */
    getAverageLatency() {
        if (this.requestTimes.length === 0) return 0

        const sum = this.requestTimes.reduce((a, b) => a + b, 0)
        return sum / this.requestTimes.length
    }

    /**
     * 获取错误率(%)
     */
    getErrorRate() {
        if (this.totalRequests === 0) return 0

        return (this.errorCount / this.totalRequests) * 100
    }

    /**
     * 重置统计数据
     */
    reset() {
        this.requestTimes = []
        this.errorCount = 0
        this.totalRequests = 0
    }

    /**
     * 获取完整统计信息
     */
    getStats() {
        return {
            averageLatency: this.getAverageLatency(),
            errorRate: this.getErrorRate(),
            totalRequests: this.totalRequests,
            recentLatencies: [...this.requestTimes]
        }
    }
}

// ✅ 导出单例
export const httpMonitor = new HttpMonitor()
export default httpMonitor
