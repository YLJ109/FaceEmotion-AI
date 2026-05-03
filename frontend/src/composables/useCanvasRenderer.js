/**
 * Canvas 渲染 Composable - 提取 Canvas 绘制逻辑
 * 
 * 【优化】
 * - 封装 Canvas 初始化、绘制、清理逻辑
 * - 支持人脸框、标签绘制
 * - 支持静态帧跳过优化
 */
import { ref, onUnmounted } from 'vue'
import { drawCornerBox, drawEmotionLabel } from '@/utils/canvas'
import { getEmotionColor } from '@/utils/emotion'

export function useCanvasRenderer(canvasRef) {
    const ctx = ref(null)
    const animationId = ref(null)
    const lastFrameHash = ref(0)

    // === 初始化 ===
    const initCanvas = () => {
        const canvas = canvasRef.value
        if (!canvas) return null

        ctx.value = canvas.getContext('2d')
        return ctx.value
    }

    // === 绘制人脸框和标签 ===
    const drawFaces = (faces, canvasWidth, canvasHeight, sendWidth, sendHeight, theme, totalFacesOverride = null) => {
        const canvas = canvasRef.value
        if (!canvas || !ctx.value || !faces?.length) return

        const scaleX = canvasWidth / sendWidth
        const scaleY = canvasHeight / sendHeight
        const totalFaces = totalFacesOverride !== null ? totalFacesOverride : faces.length

        faces.forEach((face, index) => {
            const [x, y, w, h] = face.bbox
            const sx = x * scaleX
            const sy = y * scaleY
            const sw = w * scaleX
            const sh = h * scaleY

            // 镜像翻转 (实时检测用)
            const flippedBbox = [canvasWidth - sx - sw, sy, sw, sh]
            const color = getEmotionColor(face.emotion)

            drawCornerBox(ctx.value, flippedBbox, color, 3)
            drawEmotionLabel(ctx.value, flippedBbox, face.emotion, face.confidence, theme, index + 1, totalFaces)
        })
    }

    // === 绘制图片检测结果 (非镜像) ===
    const drawImageResults = (faces, scale, offsetX, offsetY, theme) => {
        if (!ctx.value || !faces?.length) return

        faces.forEach((face, index) => {
            const color = getEmotionColor(face.emotion)

            // 缩放 bbox 坐标
            const scaledBbox = [
                face.bbox[0] * scale + offsetX,
                face.bbox[1] * scale + offsetY,
                face.bbox[2] * scale,
                face.bbox[3] * scale
            ]

            drawCornerBox(ctx.value, scaledBbox, color, 4)
            drawEmotionLabel(ctx.value, scaledBbox, face.emotion, face.confidence, theme, index + 1, faces.length)
        })
    }

    // === 静态帧跳过优化 ===
    const shouldSkipRender = (imageData) => {
        if (!imageData) return false

        // 计算当前帧的哈希值
        const currentHash = computeFrameHash(imageData.data)

        // 如果哈希值相同，说明画面无变化
        if (currentHash === lastFrameHash.value) {
            return true
        }

        lastFrameHash.value = currentHash
        return false
    }

    // 计算帧哈希
    const computeFrameHash = (data) => {
        let hash = 0
        // 采样部分像素点 (性能优化)
        const step = 100  // 每 100 个像素采样一次
        for (let i = 0; i < data.length; i += step * 4) {
            hash = ((hash << 5) - hash) + data[i]
            hash |= 0  // 转换为 32 位整数
        }
        return hash
    }

    // === 清空画布 ===
    const clearCanvas = () => {
        const canvas = canvasRef.value
        if (!canvas || !ctx.value) return

        ctx.value.clearRect(0, 0, canvas.width, canvas.height)
    }

    // === 停止渲染循环 ===
    const stopRender = () => {
        if (animationId.value) {
            cancelAnimationFrame(animationId.value)
            animationId.value = null
        }
    }

    // 组件卸载时清理
    onUnmounted(() => {
        stopRender()
    })

    return {
        ctx,
        animationId,
        initCanvas,
        drawFaces,
        drawImageResults,
        shouldSkipRender,
        clearCanvas,
        stopRender
    }
}
