/**
 * 3秒窗口情绪趋势分析工具
 * 基于最后3秒的情绪数据变化特征进行综合分析
 */

import { EMOTION_NAMES, getEmotionColor } from '@/constants/emotions'

/**
 * 分析最后3秒的情绪趋势
 * @param {Array} emotionHistory - 情绪历史数据 [{ timestamp, emotions: { happy: 0.8, ... } }]
 * @param {Object} currentEmotionData - 当前情绪数据 { emotion, confidence, scores }
 * @returns {Object} - 3秒窗口分析结果
 */
export function analyze3SecondWindow(emotionHistory, currentEmotionData) {
  if (!emotionHistory || emotionHistory.length === 0) {
    return {
      hasData: false,
      analysis: '暂无情绪数据',
      fluctuationPattern: 'unknown',
      mainEmotion: null,
      mainEmotionIntensity: 0,
      intensityChange: 'stable',
      keyInfo: [],
      hasRisk: false,
      riskLevel: 'none',
      riskMessage: ''
    }
  }

  const now = Date.now()
  const threeSecondsAgo = now - 3000

  const recentData = emotionHistory.filter(item => item.timestamp >= threeSecondsAgo)

  if (recentData.length === 0) {
    return {
      hasData: true,
      dataPoints: 0,
      analysis: '数据采集时间不足3秒',
      fluctuationPattern: 'unknown',
      mainEmotion: null,
      mainEmotionIntensity: 0,
      intensityChange: 'stable',
      keyInfo: [],
      hasRisk: false,
      riskLevel: 'none',
      riskMessage: ''
    }
  }

  const result = {
    hasData: true,
    dataPoints: recentData.length,
    timeWindow: 3,
    fluctuationPattern: 'stable',
    mainEmotion: null,
    mainEmotionIntensity: 0,
    intensityChange: 'stable',
    keyInfo: [],
    hasRisk: false,
    riskLevel: 'none',
    riskMessage: '',
    emotionChanges: [],
    intensityTrends: {}
  }

  const emotionKeys = Object.keys(recentData[0].emotions || {})

  emotionKeys.forEach(emotion => {
    const scores = recentData.map(item => item.emotions[emotion] || 0)
    const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length
    const maxScore = Math.max(...scores)
    const minScore = Math.min(...scores)
    const trend = scores[scores.length - 1] - scores[0]

    result.intensityTrends[emotion] = {
      average: avgScore,
      max: maxScore,
      min: minScore,
      change: trend,
      variance: calculateVariance(scores)
    }
  })

  const sortedEmotions = emotionKeys
    .map(emotion => ({
      emotion,
      avgIntensity: result.intensityTrends[emotion].average,
      maxIntensity: result.intensityTrends[emotion].max,
      trend: result.intensityTrends[emotion].change
    }))
    .sort((a, b) => b.avgIntensity - a.avgIntensity)

  result.mainEmotion = sortedEmotions[0].emotion
  result.mainEmotionIntensity = sortedEmotions[0].avgIntensity

  const varianceValues = emotionKeys.map(e => result.intensityTrends[e].variance)
  const avgVariance = varianceValues.reduce((a, b) => a + b, 0) / varianceValues.length

  if (avgVariance < 0.01) {
    result.fluctuationPattern = 'stable'
  } else if (avgVariance < 0.05) {
    result.fluctuationPattern = 'slight_fluctuation'
  } else if (avgVariance < 0.15) {
    result.fluctuationPattern = 'moderate_fluctuation'
  } else {
    result.fluctuationPattern = 'severe_fluctuation'
  }

  const mainTrend = result.intensityTrends[result.mainEmotion].change
  if (mainTrend > 0.1) {
    result.intensityChange = 'increasing'
  } else if (mainTrend < -0.1) {
    result.intensityChange = 'decreasing'
  } else {
    result.intensityChange = 'stable'
  }

  result.emotionChanges = detectEmotionChanges(recentData)

  result.keyInfo = extractKeyInfo(result)

  const riskDetection = detectRisks(result, currentEmotionData)
  result.hasRisk = riskDetection.hasRisk
  result.riskLevel = riskDetection.level
  result.riskMessage = riskDetection.message

  result.analysis = generateAnalysisText(result)

  return result
}

function calculateVariance(scores) {
  const mean = scores.reduce((a, b) => a + b, 0) / scores.length
  const squaredDiffs = scores.map(score => Math.pow(score - mean, 2))
  return squaredDiffs.reduce((a, b) => a + b, 0) / scores.length
}

function detectEmotionChanges(recentData) {
  const changes = []
  const emotionKeys = Object.keys(recentData[0].emotions || {})

  for (let i = 1; i < recentData.length; i++) {
    const prev = recentData[i - 1].emotions
    const curr = recentData[i].emotions

    emotionKeys.forEach(emotion => {
      const prevScore = prev[emotion] || 0
      const currScore = curr[emotion] || 0
      const change = currScore - prevScore

      if (Math.abs(change) > 0.2) {
        changes.push({
          emotion,
          change,
          direction: change > 0 ? 'increase' : 'decrease',
          timeIndex: i
        })
      }
    })
  }

  return changes
}

function extractKeyInfo(result) {
  const info = []

  info.push(`数据点: ${result.dataPoints}个`)

  const patternNames = {
    stable: '情绪稳定',
    slight_fluctuation: '轻微波动',
    moderate_fluctuation: '中度波动',
    severe_fluctuation: '剧烈波动'
  }
  info.push(`波动模式: ${patternNames[result.fluctuationPattern]}`)

  if (result.mainEmotion) {
    const emotionName = EMOTION_NAMES[result.mainEmotion] || result.mainEmotion
    const intensityPercent = Math.round(result.mainEmotionIntensity * 100)
    info.push(`主要情绪: ${emotionName}(${intensityPercent}%)`)
  }

  const intensityNames = {
    increasing: '强度上升',
    decreasing: '强度下降',
    stable: '强度稳定'
  }
  info.push(`强度变化: ${intensityNames[result.intensityChange]}`)

  if (result.emotionChanges.length > 0) {
    const topChanges = result.emotionChanges.slice(0, 3)
    topChanges.forEach(change => {
      const emotionName = EMOTION_NAMES[change.emotion] || change.emotion
      const directionText = change.direction === 'increase' ? '上升' : '下降'
      const changePercent = Math.round(Math.abs(change.change) * 100)
      info.push(`${emotionName}${directionText}${changePercent}%`)
    })
  }

  return info
}

function detectRisks(result, currentEmotionData) {
  const risks = []

  if (result.fluctuationPattern === 'severe_fluctuation') {
    risks.push({
      level: 'high',
      message: '情绪有些不稳定，试着深呼吸，放松一下吧'
    })
  }

  if (result.mainEmotion && ['sad', 'angry', 'fear', 'disgust'].includes(result.mainEmotion)) {
    if (result.mainEmotionIntensity > 0.6) {
      const emotionName = EMOTION_NAMES[result.mainEmotion] || result.mainEmotion
      risks.push({
        level: 'high',
        message: `检测到${emotionName}情绪较高，保持冷静，一切都会好起来的`
      })
    } else if (result.mainEmotionIntensity > 0.4) {
      const emotionName = EMOTION_NAMES[result.mainEmotion] || result.mainEmotion
      risks.push({
        level: 'medium',
        message: `感受到${emotionName}情绪，记得照顾好自己，适当休息`
      })
    }
  }

  if (result.intensityChange === 'increasing' && result.mainEmotionIntensity > 0.5) {
    if (['sad', 'angry', 'fear', 'disgust'].includes(result.mainEmotion)) {
      risks.push({
        level: 'high',
        message: '情绪正在变化，试着做些让自己开心的事情吧'
      })
    }
  }

  if (result.emotionChanges.length > 5) {
    risks.push({
      level: 'medium',
      message: '情绪变化较多，给自己一些时间，慢慢来'
    })
  }

  if (currentEmotionData && currentEmotionData.confidence < 0.3) {
    risks.push({
      level: 'low',
      message: '请确保人脸在画面中清晰可见，以便更好地识别您的情绪'
    })
  }

  if (risks.length === 0) {
    return {
      hasRisk: false,
      level: 'none',
      message: ''
    }
  }

  const highRisks = risks.filter(r => r.level === 'high')
  const mediumRisks = risks.filter(r => r.level === 'medium')

  if (highRisks.length > 0) {
    return {
      hasRisk: true,
      level: 'high',
      message: highRisks[0].message
    }
  } else if (mediumRisks.length > 0) {
    return {
      hasRisk: true,
      level: 'medium',
      message: mediumRisks[0].message
    }
  } else {
    return {
      hasRisk: true,
      level: 'low',
      message: risks[0].message
    }
  }
}

function generateAnalysisText(result) {
  const parts = []

  const patternNames = {
    stable: '情绪稳定',
    slight_fluctuation: '情绪轻微波动',
    moderate_fluctuation: '情绪中度波动',
    severe_fluctuation: '情绪剧烈波动'
  }
  parts.push(`最后3秒内${patternNames[result.fluctuationPattern]}`)

  if (result.mainEmotion) {
    const emotionName = EMOTION_NAMES[result.mainEmotion] || result.mainEmotion
    const intensityPercent = Math.round(result.mainEmotionIntensity * 100)
    parts.push(`主要情绪为${emotionName}，平均强度${intensityPercent}%`)
  }

  const intensityNames = {
    increasing: '呈上升趋势',
    decreasing: '呈下降趋势',
    stable: '保持稳定'
  }
  parts.push(`情绪强度${intensityNames[result.intensityChange]}`)

  if (result.emotionChanges.length > 0) {
    parts.push(`检测到${result.emotionChanges.length}次显著情绪变化`)
  }

  return parts.join('，') + '。'
}

/**
 * 准备发送给后端的数据
 * @param {Object} windowAnalysis - 3秒窗口分析结果
 * @param {string} text - 用户输入的文本内容
 * @returns {Object} - 发送给后端的数据
 */
export function prepareBackendData(windowAnalysis, text = '') {
  return {
    emotion_analysis: {
      time_window: windowAnalysis.timeWindow,
      data_points: windowAnalysis.dataPoints,
      fluctuation_pattern: windowAnalysis.fluctuationPattern,
      main_emotion: windowAnalysis.mainEmotion,
      main_emotion_intensity: windowAnalysis.mainEmotionIntensity,
      intensity_change: windowAnalysis.intensityChange,
      emotion_changes: windowAnalysis.emotionChanges,
      intensity_trends: windowAnalysis.intensityTrends,
      key_info: windowAnalysis.keyInfo,
      analysis: windowAnalysis.analysis
    },
    text_content: text,
    risk_info: {
      has_risk: windowAnalysis.hasRisk,
      risk_level: windowAnalysis.riskLevel,
      risk_message: windowAnalysis.riskMessage
    },
    timestamp: Date.now()
  }
}
