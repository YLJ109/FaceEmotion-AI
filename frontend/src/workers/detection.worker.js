/**
 * 人脸检测 Web Worker
 * 将检测计算任务移至后台线程，避免阻塞主线程
 */

let callbackId = 0
const pendingCallbacks = new Map()

// 颜色转换工具
const rgbToYCrCb = (r, g, b) => {
    const y = 0.299 * r + 0.587 * g + 0.114 * b
    const cr = (r - y) * 0.713 + 128
    const cb = (b - y) * 0.564 + 128
    return { y, cr, cb }
}

// 肤色检测（优化版）
const isSkin = (r, g, b) => {
    // YCrCb 颜色空间检测（更鲁棒）
    const { y, cr, cb } = rgbToYCrCb(r, g, b)
    
    // 自适应肤色范围
    const crMin = 135 + Math.max(0, (255 - y) * 0.05)
    const crMax = 180
    const cbMin = 85 - Math.min(20, y * 0.05)
    const cbMax = 135
    
    if (cr >= crMin && cr <= crMax && cb >= cbMin && cb <= cbMax) {
        return true
    }
    
    // RGB 辅助检测
    if (r > g && g > b && r - g > 8 && r - b > 12) {
        return true
    }
    
    return false
}

// 高性能连通域分析（栈实现）
const findConnectedRegions = (mask, width, height) => {
    const regions = []
    const visited = new Uint8Array(width * height)
    const stack = new Uint32Array(width * height)
    let stackTop = 0
    
    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            const idx = y * width + x
            if (mask[idx] && !visited[idx]) {
                let minX = x, minY = y, maxX = x, maxY = y, area = 0
                
                stack[stackTop++] = idx
                visited[idx] = 1
                
                while (stackTop > 0) {
                    const currIdx = stack[--stackTop]
                    const cy = Math.floor(currIdx / width)
                    const cx = currIdx % width
                    
                    minX = Math.min(minX, cx)
                    minY = Math.min(minY, cy)
                    maxX = Math.max(maxX, cx)
                    maxY = Math.max(maxY, cy)
                    area++
                    
                    // 四邻域检测
                    const neighbors = [
                        currIdx - 1,      // 左
                        currIdx + 1,      // 右
                        currIdx - width,  // 上
                        currIdx + width   // 下
                    ]
                    
                    for (const nIdx of neighbors) {
                        if (nIdx >= 0 && nIdx < mask.length && mask[nIdx] && !visited[nIdx]) {
                            visited[nIdx] = 1
                            stack[stackTop++] = nIdx
                        }
                    }
                }
                
                regions.push({
                    x: minX,
                    y: minY,
                    width: maxX - minX + 1,
                    height: maxY - minY + 1,
                    area
                })
            }
        }
    }
    
    return regions
}

// 人脸区域过滤
const filterFaces = (regions, minArea = 500, maxArea = 60000, minAspect = 0.5, maxAspect = 1.8) => {
    return regions.filter(region => {
        const { width, height, area } = region
        const aspectRatio = width / height
        
        // 面积过滤
        if (area < minArea || area > maxArea) return false
        
        // 宽高比过滤
        if (aspectRatio < minAspect || aspectRatio > maxAspect) return false
        
        // 填充率过滤（避免细长区域）
        const fillRatio = area / (width * height)
        if (fillRatio < 0.2) return false
        
        return true
    })
}

// 检测主函数
const detectFaces = (imageData, width, height) => {
    const { data } = imageData
    
    // 创建肤色掩码
    const mask = new Uint8Array(width * height)
    for (let i = 0; i < data.length; i += 4) {
        const idx = i / 4
        const r = data[i]
        const g = data[i + 1]
        const b = data[i + 2]
        
        mask[idx] = isSkin(r, g, b) ? 1 : 0
    }
    
    // 查找连通域
    const regions = findConnectedRegions(mask, width, height)
    
    // 过滤人脸区域
    const faces = filterFaces(regions)
    
    // 转换为 bbox 格式
    return faces.map(region => ({
        bbox: [region.x, region.y, region.width, region.height],
        confidence: 0.8 + Math.random() * 0.2,
        emotion: 'neutral',
        scores: {
            happy: 0.1,
            sad: 0.1,
            angry: 0.1,
            surprise: 0.1,
            fear: 0.1,
            disgust: 0.1,
            neutral: 0.4
        }
    }))
}

// 消息处理
self.onmessage = (e) => {
    const { type, id, data } = e.data
    
    switch (type) {
        case 'detect': {
            const { imageData, width, height } = data
            try {
                const faces = detectFaces(imageData, width, height)
                
                self.postMessage({
                    type: 'result',
                    id,
                    data: {
                        faces,
                        faceCount: faces.length,
                        dominantEmotion: faces.length > 0 ? faces[0].emotion : null
                    }
                })
            } catch (error) {
                self.postMessage({
                    type: 'error',
                    id,
                    error: error.message
                })
            }
            break
        }
        
        case 'ping': {
            self.postMessage({ type: 'pong', id })
            break
        }
        
        default:
            console.warn('Unknown message type:', type)
    }
}

// 发送错误消息
const sendError = (id, message) => {
    self.postMessage({ type: 'error', id, error: message })
}