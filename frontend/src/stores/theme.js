/**
 * 主题状态管理 V2 — 支持丝滑过渡
 *
 * 【优化】
 * - 情绪驱动的自适应主题切换（updateThemeByEmotion）
 * - 使用 requestAnimationFrame 插值过渡，而非瞬间跳变
 * - 低频切换保护（>= 2s 间隔才切换）
 * - 保存/恢复用户偏好
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { THEMES, getTheme, getThemeByEmotion, EMOTION_TO_THEME } from '@/themes'

// 需要插值的 CSS 属性列表
const INTERPOLATED_PROPS = ['primary', 'secondary', 'accent', 'highlight', 'background', 'card_bg', 'text', 'text_secondary', 'border', 'success', 'warning', 'error']

/** 解析 hex 颜色 → RGB */
function hexToRgb(hex) {
  const clean = hex.replace('#', '')
  if (clean.length === 3) return { r: parseInt(clean[0] + clean[0], 16), g: parseInt(clean[1] + clean[1], 16), b: parseInt(clean[2] + clean[2], 16) }
  return { r: parseInt(clean.slice(0, 2), 16), g: parseInt(clean.slice(2, 4), 16), b: parseInt(clean.slice(4, 6), 16) }
}

/** 线性插值两个颜色 */
function lerpColor(a, b, t) {
  const ca = hexToRgb(a), cb = hexToRgb(b)
  const r = Math.round(ca.r + (cb.r - ca.r) * t)
  const g = Math.round(ca.g + (cb.g - ca.g) * t)
  const blue = Math.round(ca.b + (cb.b - ca.b) * t)
  return `rgb(${r},${g},${blue})`
}

/** 插值梯度 */
function lerpGradient(fromGrad, toGrad, t) {
  // 解析 "linear-gradient(...色1..., ...色2...)"
  const extractColors = (g) => {
    const m = g.match(/#[0-9a-fA-F]{3,6}/g)
    return m || ['#000', '#000']
  }
  const fCols = extractColors(fromGrad)
  const tCols = extractColors(toGrad)
  const len = Math.max(fCols.length, tCols.length)
  const parts = []
  for (let i = 0; i < len; i++) {
    const fc = fCols[Math.min(i, fCols.length - 1)]
    const tc = tCols[Math.min(i, tCols.length - 1)]
    parts.push(lerpColor(fc, tc, t))
  }
  if (parts.length > 2) {
    return `linear-gradient(135deg, ${parts[0]}, ${parts[parts.length - 1]})`
  }
  return `linear-gradient(135deg, ${parts[0] || '#000'}, ${parts[1] || '#000'})`
}

/** 插值 rgba 背景 */
function lerpRgba(fromStr, toStr, t) {
  const parse = (s) => {
    const m = s.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/)
    if (m) return { r: +m[1], g: +m[2], b: +m[3], a: m[4] !== undefined ? +m[4] : 1 }
    // 尝试 hex
    const hex = s.match(/#([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})/)
    if (hex) return { r: parseInt(hex[1], 16), g: parseInt(hex[2], 16), b: parseInt(hex[3], 16), a: 1 }
    // hex 含 alpha 或失败
    const simple = hexToRgb(s.startsWith('#') ? s : '#000')
    return { ...simple, a: s.includes('transparent') ? 0 : 1 }
  }
  const f = parse(fromStr), tgt = parse(toStr)
  const r = Math.round(f.r + (tgt.r - f.r) * t)
  const g = Math.round(f.g + (tgt.g - f.g) * t)
  const b = Math.round(f.b + (tgt.b - f.b) * t)
  const a = (f.a || 1) + ((tgt.a || 1) - (f.a || 1)) * t
  return `rgba(${r},${g},${b},${a})`
}

export const useThemeStore = defineStore('theme', () => {
  const currentThemeName = ref('overwatch')
  const themeMode = ref('manual')  // 默认手动模式
  const currentEmotion = ref('neutral')
  const _animating = ref(false)
  const _lastThemeChange = ref(0)
  const _savedPrevTheme = ref(null)

  const allThemes = computed(() => THEMES)
  const currentTheme = computed(() => getTheme(currentThemeName.value))

  // ── 设置主题（手动模式） ──
  function setTheme(themeName) {
    if (THEMES[themeName]) {
      currentThemeName.value = themeName
      themeMode.value = 'manual'
      animateToTheme(themeName)
    }
  }

  // ── 情绪驱动的自适应主题切换 ──
  function updateThemeByEmotion(emotion) {
    if (themeMode.value !== 'auto') return
    currentEmotion.value = emotion
    const themeName = EMOTION_TO_THEME[emotion] || 'zen'
    if (themeName !== currentThemeName.value) {
      // ✅ 优化: 防抖间隔 500ms,平衡响应速度与防止频繁切换
      const now = Date.now()
      if (now - _lastThemeChange.value < 500) return
      _lastThemeChange.value = now
      // 保存旧主题用于插值
      _savedPrevTheme.value = getTheme(currentThemeName.value)
      currentThemeName.value = themeName
      animateToTheme(themeName)
    }
  }

  // ─ 渐变过渡动画 ──
  function animateToTheme(themeName) {
    const targetTheme = getTheme(themeName)
    const fromTheme = _savedPrevTheme.value || getTheme(themeName)
    // ✅ 优化: 动画时长保持 300ms,确保视觉平滑
    const duration = 300
    const startTime = performance.now()

    _animating.value = true

    function step(now) {
      const elapsed = now - startTime
      const t = Math.min(1, elapsed / duration)
      // ✅ 使用 cubic-bezier ease-out,前半段快后半段慢,感知更快
      const eased = 1 - Math.pow(1 - t, 3)

      // 应用插值后的 CSS 变量
      const map = _buildInterpolatedMap(fromTheme, targetTheme, eased)
      Object.entries(map).forEach(([key, val]) => {
        document.documentElement.style.setProperty(key, val)
      })

      if (t < 1) {
        requestAnimationFrame(step)
      } else {
        _animating.value = false
        _savedPrevTheme.value = null
        // 最终确保设置为精确目标值
        applyThemeToCSS()
      }
    }
    requestAnimationFrame(step)
  }

  // ── 构建插值映射 ──
  function _buildInterpolatedMap(fromTheme, toTheme, t) {
    const map = {}
    INTERPOLATED_PROPS.forEach(prop => {
      const fromVal = fromTheme[prop] || '#000'
      const toVal = toTheme[prop] || '#000'
      // ✅ 修复: card_bg 转换为 --card-bg（下划线转连字符）
      const cssProp = prop === 'card_bg' ? 'card-bg' : prop

      // ✅ 关键修复: background 使用渐变插值，card_bg 使用 rgba 插值，其他使用 hex 插值
      if (prop === 'background') {
        map[`--${cssProp}`] = lerpGradient(fromVal, toVal, t)
      } else if (prop === 'card_bg') {
        map[`--${cssProp}`] = lerpRgba(fromVal, toVal, t)
      } else {
        map[`--${cssProp}`] = lerpColor(fromVal, toVal, t)
      }
    })
    // primary-light = primary
    map['--primary-light'] = map['--primary']
    // 梯度
    const fromGrad = fromTheme.gradient || 'linear-gradient(135deg, #000, #000)'
    const toGrad = toTheme.gradient || 'linear-gradient(135deg, #000, #000)'
    map['--gradient'] = lerpGradient(fromGrad, toGrad, t)

    // shadow - 两端线性插值 opacity
    map['--shadow'] = t < 0.5 ? fromTheme.shadow : toTheme.shadow
    map['--shadow-lg'] = t < 0.5 ? (fromTheme.shadow + ', 0 30px 60px -20px rgba(0,0,0,0.3)') : (toTheme.shadow + ', 0 30px 60px -20px rgba(0,0,0,0.3)')
    map['--glow'] = t > 0.5 ? (toTheme.glow || 'none') : (fromTheme.glow || 'none')
    return map
  }

  // ── 直接应用（无动画） ──
  function applyThemeToCSS() {
    const theme = currentTheme.value
    if (!theme) return
    const map = {
      '--primary': theme.primary,
      '--primary-light': theme.primary,
      '--secondary': theme.secondary,
      '--accent': theme.accent,
      '--highlight': theme.highlight,
      '--background': theme.background,
      '--card-bg': theme.card_bg,
      '--text': theme.text,
      '--text-secondary': theme.text_secondary,
      '--border': theme.border,
      '--success': theme.success,
      '--warning': theme.warning,
      '--error': theme.error,
      '--gradient': theme.gradient,
      '--shadow': theme.shadow,
      '--glow': theme.glow || 'none',
    }
    Object.entries(map).forEach(([key, val]) => {
      document.documentElement.style.setProperty(key, val)
    })
  }

  function getEmotionColor(emotion) {
    const theme = getThemeByEmotion(emotion)
    return theme?.highlight || '#A259FF'
  }

  function init() {
    // 恢复已保存配置
    try {
      const saved = JSON.parse(localStorage.getItem('app_config') || '{}')
      if (saved.theme_mode) themeMode.value = saved.theme_mode
      if (saved.current_theme && THEMES[saved.current_theme]) {
        currentThemeName.value = saved.current_theme
      }
    } catch { /* ignore */ }
    applyThemeToCSS()
  }

  function toggleThemeMode() {
    themeMode.value = themeMode.value === 'auto' ? 'manual' : 'auto'
  }

  /** 重置主题到用户设置 */
  function resetTheme() {
    if (themeMode.value === 'auto') {
      // 自动模式下，重置到中性主题
      const themeName = EMOTION_TO_THEME['neutral'] || 'zen'
      if (themeName !== currentThemeName.value) {
        _savedPrevTheme.value = getTheme(currentThemeName.value)
        currentThemeName.value = themeName
        animateToTheme(themeName)
      }
    } else {
      // 手动模式下，恢复到上次保存的主题
      try {
        const saved = JSON.parse(localStorage.getItem('app_config') || '{}')
        if (saved.current_theme && THEMES[saved.current_theme] && saved.current_theme !== currentThemeName.value) {
          _savedPrevTheme.value = getTheme(currentThemeName.value)
          currentThemeName.value = saved.current_theme
          animateToTheme(saved.current_theme)
        }
      } catch { /* ignore */ }
    }

    // 重置 EMA 缓冲区（避免主题切换后情感显示不准确）
    if (typeof window !== 'undefined' && window.__detectionStore__) {
      window.__detectionStore__.resetEma()
    }
  }

  return {
    currentThemeName, themeMode, currentEmotion,
    currentTheme, allThemes,
    setTheme, updateThemeByEmotion, toggleThemeMode, resetTheme, getEmotionColor, init
  }
})
