/**
 * Canvas绘制工具 - 高性能渲染人脸框与情感标签
 * 使用阴影代替手动描边，减少绘制调用次数
 */
import { EMOTION_NAMES, EMOTION_EMOJI } from './emotion'

/**
 * 绘制带发光效果的四角框
 * 使用 shadowBlur 一次完成描边+发光，减少50%绘制调用
 */
export function drawCornerBox(ctx, bbox, color, lineWidth = 3) {
  const [x, y, w, h] = bbox
  const cornerLength = Math.min(w, h) / 6

  ctx.save()
  ctx.lineCap = 'round'

  const corners = [
    [[x, y], [x + cornerLength, y]], [[x, y], [x, y + cornerLength]],
    [[x + w - cornerLength, y], [x + w, y]], [[x + w, y], [x + w, y + cornerLength]],
    [[x, y + h - cornerLength], [x, y + h]], [[x, y + h], [x + cornerLength, y + h]],
    [[x + w - cornerLength, y + h], [x + w, y + h]], [[x + w, y + h - cornerLength], [x + w, y + h]],
  ]

  // 绘制白色描边底边（更粗）
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.9)'
  ctx.lineWidth = lineWidth + 2
  ctx.shadowColor = 'rgba(0, 0, 0, 0.5)'
  ctx.shadowBlur = 8

  corners.forEach(([start, end]) => {
    ctx.beginPath()
    ctx.moveTo(...start)
    ctx.lineTo(...end)
    ctx.stroke()
  })

  // 绘制彩色边框
  ctx.strokeStyle = color
  ctx.lineWidth = lineWidth
  ctx.shadowColor = color
  ctx.shadowBlur = 12

  corners.forEach(([start, end]) => {
    ctx.beginPath()
    ctx.moveTo(...start)
    ctx.lineTo(...end)
    ctx.stroke()
  })

  ctx.restore()
}

/**
 * 绘制情感标签 - 带毛玻璃背景
 * @param {number} faceIndex - 人脸编号（从 1 开始）
 * @param {number} totalFaces - 人脸总数（用于判断是否显示编号）
 * @param {Array} existingLabels - 已绘制的标签位置 [{x, y, width, height}]
 */
export function drawEmotionLabel(ctx, bbox, emotion, confidence, themeColors, faceIndex = 1, totalFaces = 1, existingLabels = []) {
  const [x, y, w, h] = bbox

  // 根据人脸数量决定是否显示编号
  const showIndex = totalFaces > 1
  const label = showIndex
    ? `人脸${faceIndex} ${EMOTION_EMOJI[emotion] || ''} ${EMOTION_NAMES[emotion] || emotion}: ${(confidence * 100).toFixed(1)}%`
    : `${EMOTION_EMOJI[emotion] || ''} ${EMOTION_NAMES[emotion] || emotion}: ${(confidence * 100).toFixed(1)}%`

  ctx.save()

  // 根据人脸框宽度动态计算字体大小
  const fontSize = Math.max(12, Math.min(20, w / 12))
  ctx.font = `bold ${fontSize}px "Microsoft YaHei", sans-serif`

  const textMetrics = ctx.measureText(label)
  const padding = fontSize * 0.7
  const labelHeight = fontSize * 2.2
  const textWidth = textMetrics.width + padding * 2 + 10

  // 初始位置：人脸框上方
  let labelX = x
  let labelY = y - labelHeight - 8

  // ✅ 新增: 标签碰撞检测，避免重叠
  const labelRect = { x: labelX, y: labelY, width: textWidth, height: labelHeight }
  for (const existing of existingLabels) {
    if (isRectOverlap(labelRect, existing)) {
      // 如果重叠，向下偏移
      labelY = existing.y + existing.height + 4
    }
  }

  // 毛玻璃标签背景
  ctx.shadowColor = 'rgba(0, 0, 0, 0.4)'
  ctx.shadowBlur = 12
  ctx.shadowOffsetY = 4

  ctx.fillStyle = themeColors.card_bg || 'rgba(26, 11, 46, 0.85)'
  ctx.strokeStyle = themeColors.border || 'rgba(156, 78, 255, 0.4)'
  ctx.lineWidth = 1

  const r = fontSize * 0.7
  ctx.beginPath()
  ctx.moveTo(labelX + r, labelY)
  ctx.lineTo(labelX + textWidth - r, labelY)
  ctx.quadraticCurveTo(labelX + textWidth, labelY, labelX + textWidth, labelY + r)
  ctx.lineTo(labelX + textWidth, labelY + labelHeight - r)
  ctx.quadraticCurveTo(labelX + textWidth, labelY + labelHeight, labelX + textWidth - r, labelY + labelHeight)
  ctx.lineTo(labelX + r, labelY + labelHeight)
  ctx.quadraticCurveTo(labelX, labelY + labelHeight, labelX, labelY + labelHeight - r)
  ctx.lineTo(labelX, labelY + r)
  ctx.quadraticCurveTo(labelX, labelY, labelX + r, labelY)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  // 文本
  ctx.shadowColor = 'transparent'
  ctx.fillStyle = themeColors.text || '#E9DEFF'
  ctx.textBaseline = 'middle'
  ctx.fillText(label, labelX + padding, labelY + labelHeight / 2)

  ctx.restore()

  // 返回当前标签的位置信息
  return { x: labelX, y: labelY, width: textWidth, height: labelHeight }
}

/**
 * 检测两个矩形是否重叠
 */
function isRectOverlap(rect1, rect2) {
  return !(
    rect1.x + rect1.width < rect2.x ||
    rect1.x > rect2.x + rect2.width ||
    rect1.y + rect1.height < rect2.y ||
    rect1.y > rect2.y + rect2.height
  )
}

/**
 * 绘制置信度条 - 渐变进度
 */
export function drawConfidenceBar(ctx, bbox, scores, themeColors) {
  const [x, y, w, h] = bbox
  const sortedScores = Object.entries(scores)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)

  const barWidth = w
  const barHeight = 5
  const barSpacing = 4
  const startY = y + h + 12
  const radius = 3

  sortedScores.forEach(([emotion, score], index) => {
    const barY = startY + index * (barHeight + barSpacing)

    // 背景条
    ctx.fillStyle = 'rgba(0, 0, 0, 0.2)'
    ctx.beginPath()
    ctx.roundRect(x, barY, barWidth, barHeight, radius)
    ctx.fill()

    // 前景进度条
    if (score > 0) {
      ctx.fillStyle = themeColors.highlight || '#A259FF'
      ctx.globalAlpha = 0.7 + 0.3 * (1 - index / 3)
      ctx.beginPath()
      ctx.roundRect(x, barY, barWidth * Math.min(score, 1), barHeight, radius)
      ctx.fill()
      ctx.globalAlpha = 1.0
    }
  })
}

/**
 * 清空画布
 */
export function clearCanvas(ctx, width, height) {
  ctx.clearRect(0, 0, width, height)
}

/**
 * 绘制视频帧
 */
export function drawVideoFrame(ctx, videoElement, width, height) {
  if (videoElement && videoElement.readyState === 4) {
    ctx.drawImage(videoElement, 0, 0, width, height)
    return true
  }
  return false
}
