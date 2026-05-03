/**
 * AI 生成式音乐引擎 V3.0 — 防爆音 + 音量归一化 + 柔和音色
 *
 * 【架构】
 * 1. 背景垫音 (pad)：持续低频振荡器
 * 2. 节奏序列 (arpeggio)：基于 BPM 的 setTimeout 调度
 * 3. 和弦层 (chord)：每 2 拍叠加一个和弦
 *
 * 【关键优化】
 * - 防爆音：所有音量变化使用 setTargetAtTime 平滑过渡
 * - 音量归一化：根据情绪补偿系数动态调整
 * - 柔和音色：优化波形和滤波器参数
 */

const midiToFreq = (midi) => 440 * Math.pow(2, (midi - 69) / 12)

// 优化：更柔和的波形和节奏模式（移除刺耳的方波，愤怒情绪改用锯齿波但降低音量）
const EMOTION_SYNTH = {
  happy: { wave: 'sine', padNote: 48, arpNote: 55, filter: 0.7, lfo: 1.2, rhythm: [0.5, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.5] },
  sad: { wave: 'triangle', padNote: 45, arpNote: 40, filter: 0.4, lfo: 0.4, rhythm: [1.0, 0.75, 0.5, 1.0, 0.5, 1.0, 0.5, 0.75] },
  angry: { wave: 'sawtooth', padNote: 43, arpNote: 50, filter: 0.6, lfo: 1.8, rhythm: [0.25, 0.25, 0.5, 0.25, 0.25, 0.5, 0.25, 0.25] },
  surprise: { wave: 'sine', padNote: 50, arpNote: 57, filter: 0.65, lfo: 1.5, rhythm: [0.5, 0.25, 0.125, 0.125, 0.5, 0.25, 0.125, 0.125] },
  fear: { wave: 'triangle', padNote: 44, arpNote: 42, filter: 0.45, lfo: 1.0, rhythm: [0.5, 0.5, 1.0, 0.5, 0.5, 1.0, 0.5, 0.5] },
  disgust: { wave: 'triangle', padNote: 46, arpNote: 41, filter: 0.5, lfo: 0.8, rhythm: [0.5, 0.25, 0.5, 0.75, 0.5, 0.25, 0.25, 0.5] },
  neutral: { wave: 'sine', padNote: 48, arpNote: 43, filter: 0.5, lfo: 0.5, rhythm: [0.5, 0.5, 0.5, 0.5, 1.0, 0.5, 0.5, 0.5] },
}

class AudioEngine {
  constructor() {
    this.ctx = null
    this.masterGain = null
    this.masterFilter = null
    this.padOsc = null
    this.padGain = null
    this.lfo = null
    this.lfoGain = null
    this.isPlaying = false
    this.currentEmotion = 'neutral'
    this._arpTimer = null
    this._arpBeat = 0
    this._pendingStop = false   // 防止半停状态
    this._transitionTime = 0.12 // 过渡时长 (秒) - 缩短以避免延迟感
    this._lastEmotion = null    // 跟踪上次情绪用于防抖

    this.state = {
      isPlaying: false,
      currentEmotion: 'neutral',
      bpm: 80,
      volume: 0.5,
    }
    // 创建可观察副本供 Vue 响应式使用
    this._vueReactiveState = null
  }

  init() {
    if (this.ctx) return true
    try {
      this.ctx = new (window.AudioContext || window.webkitAudioContext)()

      // 主增益（初始为0，防止爆音）
      this.masterGain = this.ctx.createGain()
      this.masterGain.gain.value = 0
      this.masterGain.connect(this.ctx.destination)

      // 低通滤波器（更柔和的参数）
      this.masterFilter = this.ctx.createBiquadFilter()
      this.masterFilter.type = 'lowpass'
      this.masterFilter.frequency.value = 400  // 降低初始截止频率
      this.masterFilter.Q.value = 0.7  // 降低共振
      this.masterFilter.connect(this.masterGain)

      // 背景垫音
      this.padOsc = this.ctx.createOscillator()
      this.padOsc.type = 'sine'
      this.padOsc.frequency.value = 130
      this.padGain = this.ctx.createGain()
      this.padGain.gain.value = 0
      this.padOsc.connect(this.padGain)
      this.padGain.connect(this.masterFilter)
      this.padOsc.start()

      // LFO 颤音（降低强度）
      this.lfo = this.ctx.createOscillator()
      this.lfo.type = 'sine'
      this.lfo.frequency.value = 0.5
      this.lfoGain = this.ctx.createGain()
      this.lfoGain.gain.value = 50  // 降低LFO强度
      this.lfo.connect(this.lfoGain)
      this.lfoGain.connect(this.masterFilter.frequency)
      this.lfo.start()

      return true
    } catch (e) {
      console.error('AudioEngine init failed:', e)
      return false
    }
  }

  start(params) {
    if (!this.init()) return false
    this._pendingStop = false
    this._currentParams = params
    this._lastBpm = params.bpm || 80
    this._currentVolume = 0

    // 淡入：避免启动时爆音
    const now = this.ctx.currentTime
    this.masterGain.gain.setValueAtTime(0, now)
    this.masterGain.gain.linearRampToValueAtTime(0.3, now + 0.3)

    this.applyParams(params)
    this.isPlaying = true
    this.state.isPlaying = true
    this._startArpeggio(params)
    this.resume()
    return true
  }

  stop() {
    this._pendingStop = true
    this.isPlaying = false
    this.state.isPlaying = false

    if (this._arpTimer) {
      clearTimeout(this._arpTimer)
      this._arpTimer = null
    }

    if (this.ctx && this.masterGain) {
      // 淡出：避免停止时爆音
      const now = this.ctx.currentTime
      this.masterGain.gain.setTargetAtTime(0, now, 0.08)
    }
    if (this.padGain) {
      this.padGain.gain.setTargetAtTime(0, this.ctx.currentTime, 0.08)
    }
  }

  /** 平滑过渡参数 — 使用 setTargetAtTime 自动缓动 */
  applyParams(params) {
    if (!params || !params.dominant || !this.ctx || this._pendingStop) return

    const emotion = params.dominant
    const synth = EMOTION_SYNTH[emotion] || EMOTION_SYNTH.neutral
    const intensity = params.intensity || 0.5

    // 防抖：如果情绪未变且参数变化小于阈值，跳过更新
    if (this._lastEmotion === emotion && this._currentParams) {
      const bpmDiff = Math.abs((this._currentParams.bpm || 80) - (params.bpm || 80))
      const volDiff = Math.abs((this._currentParams.volume || 0.5) - (params.volume || 0.5))
      if (bpmDiff < 3 && volDiff < 0.05) return
    }

    this._currentParams = params
    this._lastEmotion = emotion
    this.currentEmotion = emotion
    this.state.currentEmotion = emotion
    this.state.bpm = params.bpm || 80

    const now = this.ctx.currentTime
    const t = this._transitionTime

    // 垫音波形 + 频率 + 音量（setTargetAtTime 自动缓动）
    this.padOsc.type = synth.wave
    this.padOsc.frequency.setTargetAtTime(midiToFreq(synth.padNote - 12), now, t)

    // 优化：降低垫音基础音量，避免掩盖琶音
    const padVolume = 0.04 + intensity * 0.08
    this.padGain.gain.setTargetAtTime(padVolume, now, t)

    // 滤波器截止频率（限制上限避免刺耳）
    const cutoff = 200 + synth.filter * 2500
    this.masterFilter.frequency.setTargetAtTime(cutoff, now, t)
    this.masterFilter.Q.setTargetAtTime(0.7, now, t) // 保持适度共振

    // LFO 速率（限制范围）
    const lfoFreq = synth.lfo * (0.6 + intensity * 0.6)
    this.lfo.frequency.setTargetAtTime(lfoFreq, now, t)
    this.lfoGain.gain.setTargetAtTime(60, now, t) // 降低 LFO 深度

    // 主音量（归一化 + 情绪补偿）
    const baseVol = 0.15
    const volCompensation = this._getVolumeCompensation(emotion)
    const vol = baseVol * (0.6 + params.volume * 0.4) * volCompensation
    const clampedVol = Math.max(0.08, Math.min(0.45, vol))
    this.masterGain.gain.setTargetAtTime(clampedVol, now, t)
  }

  updateParams(params) {
    // 只在节拍边界或情绪变化时才触发过渡，避免高频更新
    if (!this._lastEmotion || this._lastEmotion !== params.dominant) {
      this._lastEmotion = params.dominant
      this.applyParams(params)
    }
  }

  /** 获取情绪音量补偿系数 */
  _getVolumeCompensation(emotion) {
    // 预设补偿值（与后端保持一致）
    const compensations = {
      happy: 1.0,
      sad: 1.3,
      angry: 0.85,
      surprise: 1.05,
      fear: 1.2,
      disgust: 0.9,
      neutral: 1.0,
    }
    return compensations[emotion] || 1.0
  }

  setVolume(vol) {
    if (this.masterGain && this.ctx) {
      // 平滑过渡音量（提高音量范围让用户能听到）
      const targetVol = 0.1 + vol * 0.5  // 0.1 - 0.6 范围
      this.masterGain.gain.setTargetAtTime(targetVol, this.ctx.currentTime, 0.1)
    }
    this.state.volume = vol
  }

  async resume() {
    if (this.ctx && this.ctx.state === 'suspended') {
      try { await this.ctx.resume() } catch (e) { /* 浏览器限制，用户手势后自动恢复 */ }
    }
  }

  destroy() {
    this.stop()
    if (this.padOsc) { try { this.padOsc.stop() } catch (e) { } }
    if (this.lfo) { try { this.lfo.stop() } catch (e) { } }
    if (this.ctx) { this.ctx.close(); this.ctx = null }
  }

  // ── 节拍调度 ──

  _startArpeggio(params) {
    this._arpCount = 0
    this._arpBeat = 0
    this._scheduleNextArp(params)
  }

  _scheduleNextArp(params) {
    if (!this.isPlaying || !this.ctx || this._pendingStop) return

    const emotion = params.dominant || 'neutral'
    const synth = EMOTION_SYNTH[emotion] || EMOTION_SYNTH.neutral
    const bpm = params.bpm || 80
    const intensity = params.intensity || 0.5
    const beatDuration = 60.0 / bpm
    const rhythmPattern = synth.rhythm

    // 前瞻调度 8 个音 (提高节拍准确性)
    let offset = 0
    const now = this.ctx.currentTime

    for (let i = 0; i < 8; i++) {
      const beatIdx = this._arpBeat % rhythmPattern.length
      const dur = rhythmPattern[beatIdx] * beatDuration

      this._playArpNote(
        synth.arpNote + Math.floor((this._arpBeat % 16) / 4) * 2,  // 降低音程跨度
        now + offset,
        dur * 0.7,  // 缩短音符时长，更干净
        intensity * (0.1 + 0.2 * (1 - (this._arpBeat % 16) / 16)),  // 降低音量
        synth.wave
      )

      offset += dur
      this._arpBeat++
    }

    const nextDelay = Math.max(20, offset * 1000 - 30) // 提前 30ms 调度下一批
    this._arpTimer = setTimeout(() => {
      if (this.isPlaying && !this._pendingStop) {
        this._scheduleNextArp(this._currentParams || params)
      }
    }, nextDelay)
  }

  _playArpNote(baseNote, startTime, duration, velocity, waveType) {
    if (!this.ctx || duration < 0.01) return

    const osc = this.ctx.createOscillator()
    const gain = this.ctx.createGain()
    const filter = this.ctx.createBiquadFilter() // 为每个音符添加独立滤波器

    osc.type = waveType
    osc.frequency.value = midiToFreq(baseNote)

    // 优化：更柔和的 ADSR 包络（延长 Attack/Release 避免爆音）
    const attack = 0.01
    const decay = 0.02
    const release = Math.min(0.02, duration * 0.3) // 根据音符长度动态调整释音
    const peakVel = velocity * 0.12 // 降低峰值音量
    const sustainVel = peakVel * 0.75

    gain.gain.setValueAtTime(0, startTime)
    gain.gain.linearRampToValueAtTime(peakVel, startTime + attack)
    gain.gain.linearRampToValueAtTime(sustainVel, startTime + attack + decay)
    gain.gain.setValueAtTime(sustainVel, startTime + duration - release)
    gain.gain.linearRampToValueAtTime(0, startTime + duration)

    // 滤波器使音色更柔和
    filter.type = 'lowpass'
    filter.frequency.value = 1200
    filter.Q.value = 0.5

    osc.connect(filter)
    filter.connect(gain)
    gain.connect(this.masterFilter)
    osc.start(startTime)
    osc.stop(startTime + duration + 0.02)
  }
}

export const audioEngine = new AudioEngine()
// 导出 state 引用供 Vue 响应式使用
export const audioState = audioEngine.state
export default audioEngine
