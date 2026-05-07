/**
 * 情绪趋势分析工具
 * 分析文本内容，识别情绪提示词和警告词，生成情绪趋势分析报告
 */

// 积极情绪关键词
const POSITIVE_WORDS = [
  '开心', '快乐', '高兴', '幸福', '满足', '满意', '愉悦', '兴奋',
  '喜悦', '欣慰', '温暖', '感动', '乐观', '自信', '平和', '平静',
  '放松', '舒适', '安心', '希望', '期待', '憧憬', '美好', '顺利',
  '成功', '进步', '成长', '收获', '感恩', '感谢', '爱', '喜欢',
  '微笑', '大笑', '拥抱', '加油', '努力', '坚持', '勇敢', '坚强'
]

// 消极情绪关键词
const NEGATIVE_WORDS = [
  '难过', '伤心', '悲伤', '痛苦', '失望', '沮丧', '郁闷', '烦躁',
  '焦虑', '紧张', '压力', '担心', '害怕', '恐惧', '愤怒', '生气',
  '不满', '抱怨', '委屈', '孤独', '寂寞', '无助', '迷茫', '困惑',
  '绝望', '失落', '空虚', '疲惫', '累', '厌倦', '无聊', '烦躁'
]

// 警告词（需要特别关注）
const WARNING_WORDS = [
  '自杀', '想死', '活着没意思', '太累了', '撑不住了', '放弃',
  '结束', '伤害自己', '割腕', '跳楼', '吃药', '失眠', '食欲',
  '体重', '哭泣', '崩溃', '失控', '麻木', '冷漠', '无意义'
]

// 情绪管理建议库
const ADVICE_LIBRARY = {
  positive: [
    '继续保持这份积极的心态，你的努力正在带来美好的改变！',
    '积极的情绪是最好的动力，继续保持情绪稳定！',
    '你的心态很棒，保持情绪稳定有助于身心健康！',
    '继续保持这种积极向上的状态，未来充满希望！',
    '正能量满满！保持情绪稳定，生活更美好！'
  ],
  neutral: [
    '当前情绪较为平稳，保持情绪稳定是最好的状态！',
    '情绪平和是一种智慧，继续保持情绪稳定！',
    '平淡中见真章，保持情绪稳定就是最好的生活态度！',
    '情绪稳定是心理健康的基石，继续保持！',
    '心如止水是一种境界，保持情绪稳定，从容面对！'
  ],
  negative: [
    '情绪波动是正常的，关键是学会调节，保持情绪稳定！',
    '每个人都有低谷期，给自己一些时间和空间，保持情绪稳定！',
    '困难只是暂时的，保持情绪稳定，相信一切都会好起来！',
    '请记住，你不是一个人在战斗，保持情绪稳定最重要！',
    '深呼吸，让自己平静下来，保持情绪稳定才能更好地应对！'
  ],
  warning: [
    '你的情绪状态需要特别关注，请务必保持情绪稳定！',
    '建议你及时与亲友沟通，或寻求专业帮助，保持情绪稳定！',
    '请记住，无论何时，都有人关心你，请保持情绪稳定！',
    '生命是宝贵的，每一个困难都有解决的办法，请保持情绪稳定！',
    '请给自己多一些关爱，保持情绪稳定，一切都会过去的！'
  ]
}

/**
 * 分析文本中的情绪关键词
 * @param {string} text - 用户输入的文本
 * @returns {Object} - 分析结果
 */
export function analyzeText(text) {
  if (!text || typeof text !== 'string') {
    return {
      text: '',
      positiveCount: 0,
      negativeCount: 0,
      warningCount: 0,
      positiveWords: [],
      negativeWords: [],
      warningWords: [],
      sentimentScore: 0,
      level: 'neutral',
      trend: 'stable',
      analysis: '',
      advice: ''
    }
  }

  const result = {
    text: text,
    positiveCount: 0,
    negativeCount: 0,
    warningCount: 0,
    positiveWords: [],
    negativeWords: [],
    warningWords: [],
    sentimentScore: 0,
    level: 'neutral',
    trend: 'stable',
    analysis: '',
    advice: ''
  }

  // 转换为小写进行匹配
  const lowerText = text.toLowerCase()

  // 统计积极情绪词
  POSITIVE_WORDS.forEach(word => {
    if (lowerText.includes(word.toLowerCase())) {
      result.positiveCount++
      result.positiveWords.push(word)
    }
  })

  // 统计消极情绪词
  NEGATIVE_WORDS.forEach(word => {
    if (lowerText.includes(word.toLowerCase())) {
      result.negativeCount++
      result.negativeWords.push(word)
    }
  })

  // 统计警告词
  WARNING_WORDS.forEach(word => {
    if (lowerText.includes(word.toLowerCase())) {
      result.warningCount++
      result.warningWords.push(word)
    }
  })

  // 计算情感分数
  const total = result.positiveCount + result.negativeCount
  if (total > 0) {
    result.sentimentScore = ((result.positiveCount - result.negativeCount) / total) * 100
  }

  // 确定情绪等级
  if (result.warningCount > 0) {
    result.level = 'warning'
  } else if (result.sentimentScore > 30) {
    result.level = 'positive'
  } else if (result.sentimentScore < -30) {
    result.level = 'negative'
  } else {
    result.level = 'neutral'
  }

  // 生成分析报告
  result.analysis = generateAnalysis(result)

  // 生成建议
  result.advice = generateAdvice(result)

  return result
}

/**
 * 生成情绪分析报告
 */
function generateAnalysis(result) {
  const parts = []

  if (result.warningCount > 0) {
    parts.push(`检测到 ${result.warningCount} 个需要关注的关键词`)
  }

  if (result.positiveCount > 0) {
    parts.push(`识别到 ${result.positiveCount} 个积极情绪词（${result.positiveWords.join('、')}）`)
  }

  if (result.negativeCount > 0) {
    parts.push(`识别到 ${result.negativeCount} 个消极情绪词（${result.negativeWords.join('、')}）`)
  }

  if (parts.length === 0) {
    return '文本中未明显检测到情绪相关词汇，情绪状态较为平和。'
  }

  return parts.join('；')
}

/**
 * 生成情绪管理建议
 */
function generateAdvice(result) {
  const library = ADVICE_LIBRARY[result.level] || ADVICE_LIBRARY.neutral
  const randomIndex = Math.floor(Math.random() * library.length)
  return library[randomIndex]
}

/**
 * 获取情绪等级对应的标签和颜色
 */
export function getEmotionLevelInfo(level) {
  const levelInfo = {
    positive: { label: '积极', color: '#10B981', bgColor: 'rgba(16, 185, 129, 0.1)' },
    neutral: { label: '平稳', color: '#6B7280', bgColor: 'rgba(107, 114, 128, 0.1)' },
    negative: { label: '消极', color: '#EF4444', bgColor: 'rgba(239, 68, 68, 0.1)' },
    warning: { label: '警告', color: '#F59E0B', bgColor: 'rgba(245, 158, 11, 0.1)' }
  }
  return levelInfo[level] || levelInfo.neutral
}

// 情绪名称映射
const EMOTION_NAMES = {
  happy: '开心',
  sad: '难过',
  angry: '生气',
  surprise: '惊讶',
  fear: '害怕',
  disgust: '厌恶',
  neutral: '平静'
}

// 情绪分值权重（用于计算情感分数）
const EMOTION_SCORES = {
  happy: 1,
  sad: -0.8,
  angry: -0.9,
  surprise: 0.3,
  fear: -0.7,
  disgust: -0.6,
  neutral: 0
}

/**
 * 分析实时情绪数据
 * @param {Object} data - 情绪数据对象
 * @param {string} data.text - 可选的文本输入
 * @param {string} data.currentEmotion - 当前识别的情绪
 * @param {number} data.currentConfidence - 当前情绪置信度
 * @param {Object} data.emotionScores - 各情绪的分数
 * @param {Array} data.faces - 检测到的人脸数据
 * @param {Array} data.history - 情绪历史记录
 * @returns {Object} - 分析结果
 */
export function analyzeEmotionData(data) {
  // 如果有文本输入，使用文本分析
  if (data.text && typeof data.text === 'string') {
    const textResult = analyzeText(data.text)
    return {
      ...textResult,
      emotionDistribution: {},
      hasWarning: textResult.warningCount > 0,
      warningTitle: textResult.warningCount > 0 ? '⚠️ 需要关注' : '',
      warningMessage: textResult.warningCount > 0 ? '检测到需要特别关注的内容，请及时关注情绪变化' : '',
      trendAnalysis: null
    }
  }

  const { currentEmotion, currentConfidence, emotionScores, faces, history } = data

  const result = {
    text: '',
    positiveCount: 0,
    negativeCount: 0,
    warningCount: 0,
    positiveWords: [],
    negativeWords: [],
    warningWords: [],
    sentimentScore: 0,
    level: 'neutral',
    trend: 'stable',
    analysis: '',
    advice: '',
    emotionDistribution: emotionScores || {},
    hasWarning: false,
    warningTitle: '',
    warningMessage: '',
    trendAnalysis: null
  }

  // 计算情感分数
  let totalScore = 0
  let validCount = 0
  
  if (emotionScores) {
    Object.entries(emotionScores).forEach(([emotion, score]) => {
      if (EMOTION_SCORES[emotion] !== undefined) {
        totalScore += score * EMOTION_SCORES[emotion] * 100
        validCount++
      }
    })
  }
  
  if (validCount > 0) {
    result.sentimentScore = totalScore / validCount
  }

  // 分析历史趋势
  const trendResult = analyzeTrend(history)
  result.trend = trendResult.trend
  result.trendAnalysis = trendResult.analysis

  // 检测异常情况
  const warningResult = detectWarnings({
    currentEmotion,
    currentConfidence,
    emotionScores,
    faces,
    history,
    trend: result.trend
  })
  result.hasWarning = warningResult.hasWarning
  result.warningTitle = warningResult.title
  result.warningMessage = warningResult.message
  result.warningCount = warningResult.hasWarning ? 1 : 0

  // 确定情绪等级
  if (result.hasWarning) {
    result.level = 'warning'
  } else if (result.sentimentScore > 20) {
    result.level = 'positive'
  } else if (result.sentimentScore < -20) {
    result.level = 'negative'
  } else {
    result.level = 'neutral'
  }

  // 生成分析报告
  result.analysis = generateEmotionAnalysis({
    currentEmotion,
    currentConfidence,
    emotionScores,
    faces,
    sentimentScore: result.sentimentScore,
    level: result.level
  })

  // 生成建议
  result.advice = generateAdvice(result)

  return result
}

/**
 * 分析情绪趋势
 */
function analyzeTrend(history) {
  if (!history || history.length < 3) {
    return { trend: 'stable', analysis: null }
  }

  const recentHistory = history.slice(-10)
  const emotions = recentHistory.map(entry => entry.emotion)
  const uniqueEmotions = [...new Set(emotions)]
  
  // 检测情绪波动频率
  let changeCount = 0
  for (let i = 1; i < emotions.length; i++) {
    if (emotions[i] !== emotions[i - 1]) {
      changeCount++
    }
  }

  const changeRate = changeCount / (emotions.length - 1)
  
  // 判断趋势
  let trend = 'stable'
  let analysis = ''

  if (uniqueEmotions.length === 1) {
    trend = 'stable'
    analysis = `情绪持续保持${EMOTION_NAMES[uniqueEmotions[0]] || uniqueEmotions[0]}状态，较为稳定。`
  } else if (changeRate > 0.6) {
    trend = 'fluctuating'
    analysis = `情绪波动较为频繁（${Math.round(changeRate * 100)}%变化率），建议关注情绪变化。`
  } else if (changeRate > 0.3) {
    trend = 'changing'
    analysis = `情绪有一定变化（${Math.round(changeRate * 100)}%变化率），整体保持稳定。`
  } else {
    trend = 'stable'
    analysis = `情绪相对稳定（${Math.round(changeRate * 100)}%变化率）。`
  }

  return { trend, analysis }
}

/**
 * 检测警告情况
 */
function detectWarnings({ currentEmotion, currentConfidence, emotionScores, faces, history, trend }) {
  const warnings = []

  // 检测低置信度情况
  if (currentConfidence < 0.3) {
    warnings.push('当前情绪识别置信度较低，请确保人脸在画面中清晰可见。')
  }

  // 检测消极情绪持续
  if (history && history.length >= 5) {
    const recentEmotions = history.slice(-5).map(h => h.emotion)
    const negativeCount = recentEmotions.filter(e => 
      ['sad', 'angry', 'fear', 'disgust'].includes(e)
    ).length
    
    if (negativeCount >= 4) {
      warnings.push('消极情绪已持续一段时间，建议适当休息和放松。')
    }
  }

  // 检测情绪剧烈波动
  if (trend === 'fluctuating') {
    warnings.push('情绪波动较为剧烈，建议进行深呼吸或冥想练习。')
  }

  // 检测多人脸场景
  if (faces && faces.length > 1) {
    warnings.push(`检测到${faces.length}张人脸，情绪识别可能受到影响。`)
  }

  // 检测高负面情绪分数
  if (emotionScores) {
    const negativeThreshold = 0.7
    if (emotionScores.angry && emotionScores.angry > negativeThreshold) {
      warnings.push('当前检测到较高的愤怒情绪，请保持冷静。')
    }
    if (emotionScores.fear && emotionScores.fear > negativeThreshold) {
      warnings.push('当前检测到较高的恐惧情绪，建议放松身心。')
    }
  }

  if (warnings.length > 0) {
    return {
      hasWarning: true,
      title: '⚠️ 情绪预警',
      message: warnings.join(' ')
    }
  }

  return {
    hasWarning: false,
    title: '',
    message: ''
  }
}

/**
 * 生成情绪分析报告
 */
function generateEmotionAnalysis({ currentEmotion, currentConfidence, emotionScores, faces, sentimentScore, level }) {
  const parts = []

  // 当前情绪
  if (currentEmotion) {
    const emotionName = EMOTION_NAMES[currentEmotion] || currentEmotion
    const confidencePercent = Math.round(currentConfidence * 100)
    parts.push(`当前情绪为${emotionName}（置信度: ${confidencePercent}%）`)
  }

  // 人脸数量
  if (faces && faces.length > 0) {
    parts.push(`检测到${faces.length}张人脸`)
  }

  // 情感分数
  const scoreLabel = sentimentScore >= 0 ? '积极' : '消极'
  parts.push(`情感倾向: ${scoreLabel}（分数: ${sentimentScore.toFixed(1)}）`)

  // 情绪分布详情
  if (emotionScores) {
    const sortedScores = Object.entries(emotionScores)
      .filter(([_, score]) => score > 0.1)
      .sort((a, b) => b[1] - a[1])
    
    if (sortedScores.length > 1) {
      const topEmotions = sortedScores.slice(0, 3).map(([emotion, score]) => 
        `${EMOTION_NAMES[emotion] || emotion}(${Math.round(score * 100)}%)`
      )
      parts.push(`主要情绪分布: ${topEmotions.join('、')}`)
    }
  }

  return parts.join('；')
}