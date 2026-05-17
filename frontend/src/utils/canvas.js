/**
 * Canvas绘制工具 - 赛博朋克风格人脸框与标签
 * 霓虹发光、HUD风格、极简线条
 */
import { getEmotionName, getEmotionEmoji, getEmotionColor } from '@/constants/emotions'

function toRGBA(color, alpha = 1) {
  if (!color) return `rgba(0, 0, 0, ${alpha})`
  const hexMatch = color.match(/^#([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})$/)
  if (hexMatch) {
    return `rgba(${parseInt(hexMatch[1], 16)}, ${parseInt(hexMatch[2], 16)}, ${parseInt(hexMatch[3], 16)}, ${alpha})`
  }
  const rgbMatch = color.match(/^rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$/)
  if (rgbMatch) {
    return `rgba(${rgbMatch[1]}, ${rgbMatch[2]}, ${rgbMatch[3]}, ${alpha})`
  }
  const rgbaMatch = color.match(/^rgba\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*[\d.]+s*\)$/)
  if (rgbaMatch) {
    return `rgba(${rgbaMatch[1]}, ${rgbaMatch[2]}, ${rgbaMatch[3]}, ${alpha})`
  }
  return color
}

/**
 * 赛博朋克风格人脸框 - 极简霓虹角标
 */
export function drawCornerBox(ctx, bbox, color, lineWidth = 2) {
  const [x, y, w, h] = bbox
  const len = Math.min(w, h) * 0.18
  const gap = 4

  ctx.save()
  ctx.lineCap = 'round'

  const layers = [
    { alpha: 0.35, strokeStyle: color, lineWidth: lineWidth + 6, shadowBlur: 18 },
    { alpha: 1, strokeStyle: color, lineWidth: lineWidth, shadowBlur: 10 },
    { alpha: 0.7, strokeStyle: '#ffffff', lineWidth: 1, shadowBlur: 4 }
  ]

  for (const layer of layers) {
    ctx.globalAlpha = layer.alpha
    ctx.strokeStyle = layer.strokeStyle
    ctx.lineWidth = layer.lineWidth
    ctx.shadowColor = layer.strokeStyle
    ctx.shadowBlur = layer.shadowBlur
    drawCorners(ctx, x, y, w, h, len, gap)
  }

  ctx.restore()
}

function drawCorners(ctx, x, y, w, h, len, gap) {
  const gx = x - gap
  const gy = y - gap
  const gw = w + gap * 2
  const gh = h + gap * 2

  // 左上
  ctx.beginPath()
  ctx.moveTo(gx, gy + len)
  ctx.lineTo(gx, gy)
  ctx.lineTo(gx + len, gy)
  ctx.stroke()

  // 右上
  ctx.beginPath()
  ctx.moveTo(gx + gw - len, gy)
  ctx.lineTo(gx + gw, gy)
  ctx.lineTo(gx + gw, gy + len)
  ctx.stroke()

  // 左下
  ctx.beginPath()
  ctx.moveTo(gx, gy + gh - len)
  ctx.lineTo(gx, gy + gh)
  ctx.lineTo(gx + len, gy + gh)
  ctx.stroke()

  // 右下
  ctx.beginPath()
  ctx.moveTo(gx + gw - len, gy + gh)
  ctx.lineTo(gx + gw, gy + gh)
  ctx.lineTo(gx + gw, gy + gh - len)
  ctx.stroke()
}

/**
 * 赛博朋克风格标签 - HUD风格
 */
export function drawEmotionLabel(ctx, bbox, emotion, confidence, themeColors, faceIndex = 1, totalFaces = 1, existingLabels = []) {
  const [x, y, w, h] = bbox
  const emotionName = getEmotionName(emotion)
  const emotionEmoji = getEmotionEmoji(emotion)
  const emotionColor = getEmotionColor(emotion)
  const pct = (confidence * 100).toFixed(1)

  ctx.save()

  const fontSize = Math.max(13, Math.min(20, w / 12))
  ctx.font = `600 ${fontSize}px "Courier New", "Consolas", "Microsoft YaHei", monospace`

  const faceTag = totalFaces > 1 ? `人脸${faceIndex} ` : ''
  const label = `${faceTag}${emotionEmoji} ${emotionName}  ${pct}%`

  const metrics = ctx.measureText(label)
  const pad = fontSize * 0.6
  const lh = fontSize * 2
  const tw = metrics.width + pad * 2 + 12

  let lx = x
  let ly = y - lh - 10

  const labelRect = { x: lx, y: ly, width: tw, height: lh }
  for (const ex of existingLabels) {
    if (isRectOverlap(labelRect, ex)) {
      ly = ex.y + ex.height + 6
    }
  }

  // === 背景 ===
  ctx.fillStyle = 'rgba(0, 0, 0, 0.85)'
  ctx.shadowColor = emotionColor
  ctx.shadowBlur = 15
  ctx.beginPath()
  ctx.roundRect(lx, ly, tw, lh, 2)
  ctx.fill()

  // === 左边框霓虹条 ===
  ctx.fillStyle = emotionColor
  ctx.shadowColor = emotionColor
  ctx.shadowBlur = 10
  ctx.fillRect(lx, ly, 3, lh)

  // === 边框 ===
  ctx.strokeStyle = toRGBA(emotionColor, 0.6)
  ctx.lineWidth = 1
  ctx.shadowBlur = 8
  ctx.beginPath()
  ctx.roundRect(lx, ly, tw, lh, 2)
  ctx.stroke()

  // === 置信度条 ===
  const barX = lx + pad + 10
  const barW = tw - pad * 2 - 30
  const barY = ly + lh - 7
  const barH = 2

  ctx.fillStyle = 'rgba(255,255,255,0.1)'
  ctx.shadowBlur = 0
  ctx.fillRect(barX, barY, barW, barH)

  const barGrad = ctx.createLinearGradient(barX, barY, barX + barW, barY)
  barGrad.addColorStop(0, emotionColor)
  barGrad.addColorStop(1, toRGBA(emotionColor, 0.4))
  ctx.fillStyle = barGrad
  ctx.shadowColor = emotionColor
  ctx.shadowBlur = 6
  ctx.fillRect(barX, barY, barW * confidence, barH)

  // === 文本 ===
  ctx.shadowColor = emotionColor
  ctx.shadowBlur = 8
  ctx.fillStyle = '#ffffff'
  ctx.textBaseline = 'middle'
  ctx.fillText(label, lx + pad, ly + lh / 2)

  ctx.restore()

  return { x: lx, y: ly, width: tw, height: lh }
}

function isRectOverlap(r1, r2) {
  return !(r1.x + r1.width < r2.x || r1.x > r2.x + r2.width ||
           r1.y + r1.height < r2.y || r1.y > r2.y + r2.height)
}

/**
 * 绘制面部关键点 - 赛博朋克风格
 * @param {CanvasRenderingContext2D} ctx - canvas上下文
 * @param {Array} landmarks - 关键点数组 [{x, y}, ...]，坐标为归一化坐标(0-1)
 * @param {string} color - 点颜色
 * @param {Object} bbox - 人脸边界框 [x, y, w, h]（用于裁剪显示）
 */
export function drawFaceLandmarks(ctx, landmarks, color = '#00ffff', bbox = null) {
  if (!landmarks || landmarks.length === 0) return
  
  ctx.save()
  
  // 获取canvas尺寸
  const canvasWidth = ctx.canvas.width
  const canvasHeight = ctx.canvas.height
  
  // === 关键点发光层 ===
  ctx.fillStyle = color
  ctx.shadowColor = color
  ctx.shadowBlur = 12
  ctx.globalAlpha = 0.4
  
  landmarks.forEach(landmark => {
    // 关键点坐标是归一化的(0-1)，需要转换为绝对像素坐标
    // 由于摄像头图像是水平镜像显示的，需要进行水平翻转
    const px = (1 - landmark.x) * canvasWidth
    const py = landmark.y * canvasHeight
    
    // 如果提供了bbox，只绘制bbox内的关键点
    if (bbox) {
      const [bx, by, bw, bh] = bbox
      if (px >= bx && px <= bx + bw && py >= by && py <= by + bh) {
        ctx.beginPath()
        ctx.arc(px, py, 4, 0, Math.PI * 2)
        ctx.fill()
      }
    } else {
      ctx.beginPath()
      ctx.arc(px, py, 4, 0, Math.PI * 2)
      ctx.fill()
    }
  })
  
  // === 关键点内核层 ===
  ctx.globalAlpha = 1
  ctx.shadowBlur = 6
  
  landmarks.forEach(landmark => {
    const px = (1 - landmark.x) * canvasWidth
    const py = landmark.y * canvasHeight
    
    if (bbox) {
      const [bx, by, bw, bh] = bbox
      if (px >= bx && px <= bx + bw && py >= by && py <= by + bh) {
        ctx.beginPath()
        ctx.arc(px, py, 2, 0, Math.PI * 2)
        ctx.fill()
      }
    } else {
      ctx.beginPath()
      ctx.arc(px, py, 2, 0, Math.PI * 2)
      ctx.fill()
    }
  })
  
  // === 白色亮点 ===
  ctx.fillStyle = '#ffffff'
  ctx.shadowColor = '#ffffff'
  ctx.shadowBlur = 3
  ctx.globalAlpha = 0.8
  
  landmarks.forEach(landmark => {
    const px = (1 - landmark.x) * canvasWidth
    const py = landmark.y * canvasHeight
    
    if (bbox) {
      const [bx, by, bw, bh] = bbox
      if (px >= bx && px <= bx + bw && py >= by && py <= by + bh) {
        ctx.beginPath()
        ctx.arc(px, py, 1, 0, Math.PI * 2)
        ctx.fill()
      }
    } else {
      ctx.beginPath()
      ctx.arc(px, py, 1, 0, Math.PI * 2)
      ctx.fill()
    }
  })
  
  ctx.restore()
}

/**
 * 绘制面部关键点连接线（眼、眉、嘴轮廓）
 * @param {CanvasRenderingContext2D} ctx - canvas上下文
 * @param {Array} landmarks - 关键点数组，坐标为归一化坐标(0-1)
 * @param {string} color - 线条颜色
 * @param {Object} bbox - 人脸边界框
 */
export function drawLandmarkConnections(ctx, landmarks, color = '#00ffff', bbox = null) {
  if (!landmarks || landmarks.length < 47) return
  
  ctx.save()
  
  // 获取canvas尺寸
  const canvasWidth = ctx.canvas.width
  const canvasHeight = ctx.canvas.height
  
  const getPoint = (idx) => ({
    x: (1 - landmarks[idx].x) * canvasWidth,
    y: landmarks[idx].y * canvasHeight
  })
  
  ctx.strokeStyle = color
  ctx.lineWidth = 1.5
  ctx.shadowColor = color
  ctx.shadowBlur = 8
  ctx.globalAlpha = 0.6
  
  // 左眼轮廓 (关键点索引)
  drawPath(ctx, [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398])
  
  // 右眼轮廓
  drawPath(ctx, [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246])
  
  // 左眼眉
  drawPath(ctx, [336, 296, 334, 293, 300, 276, 283, 282, 295, 285])
  
  // 右眼眉
  drawPath(ctx, [107, 66, 105, 63, 70, 55, 65, 52, 53, 46])
  
  // 嘴巴轮廓
  drawPath(ctx, [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146])
  
  // 鼻子
  drawPath(ctx, [6, 197, 195, 5, 4, 1, 19, 94, 2, 326, 327, 328])
  
  ctx.restore()
  
  function drawPath(ctx, indices) {
    ctx.beginPath()
    const first = getPoint(indices[0])
    ctx.moveTo(first.x, first.y)
    for (let i = 1; i < indices.length; i++) {
      const point = getPoint(indices[i])
      ctx.lineTo(point.x, point.y)
    }
    ctx.closePath()
    ctx.stroke()
  }
}

/**
 * 置信度条
 */
export function drawConfidenceBar(ctx, bbox, scores, themeColors) {
  const [x, y, w, h] = bbox
  const sorted = Object.entries(scores).sort((a, b) => b[1] - a[1]).slice(0, 3)

  const bw = w * 0.75
  const bh = 3
  const gap = 5
  const sx = x + (w - bw) / 2
  const sy = y + h + 14

  sorted.forEach(([emotion, score], i) => {
    const by = sy + i * (bh + gap)
    const ec = getEmotionColor(emotion)

    ctx.fillStyle = 'rgba(0,0,0,0.35)'
    ctx.beginPath()
    ctx.roundRect(sx, by, bw, bh, 1.5)
    ctx.fill()

    if (score > 0) {
      const g = ctx.createLinearGradient(sx, by, sx + bw, by)
      g.addColorStop(0, ec)
      g.addColorStop(1, toRGBA(ec, 0.4))
      ctx.fillStyle = g
      ctx.shadowColor = ec
      ctx.shadowBlur = 6
      ctx.beginPath()
      ctx.roundRect(sx, by, bw * Math.min(score, 1), bh, 1.5)
      ctx.fill()
      ctx.shadowBlur = 0
    }
  })
}

export function clearCanvas(ctx, width, height) {
  ctx.clearRect(0, 0, width, height)
}

export function drawVideoFrame(ctx, videoElement, width, height) {
  if (videoElement && videoElement.readyState === 4) {
    ctx.drawImage(videoElement, 0, 0, width, height)
    return true
  }
  return false
}