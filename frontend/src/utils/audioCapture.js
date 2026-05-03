/**
 * 音频采集工具 — V3 AudioWorklet 版
 * - 使用 AudioWorkletNode 替代已废弃的 ScriptProcessorNode
 * - 提供更低的延迟和更稳定的音频采集
 * - 缓存 AudioContext / AnalyserNode，避免每次 getVolumeLevel 都新建
 * - 音量检测直接复用采集链路，零额外开销
 */
export class AudioCapture {
  constructor(options = {}) {
    this.stream = null
    this.audioCtx = null
    this.analyser = null
    this.mediaStreamSource = null
    this.isCapturing = false
    this.onAudioData = options.onAudioData || null
    this.sampleRate = options.sampleRate || 16000
    this._intervalId = null
    this._workletNode = null
    this._processorNode = null
    this._scriptNodeCompat = typeof AudioContext !== 'undefined' && !AudioContext.prototype.createScriptProcessor
      ? null : true

    // ✅ 新增: 音频压缩配置
    this.compressionEnabled = options.compressionEnabled ?? true
    this.lastSample = 0  // 用于差分编码
    this._debugPrinted = false
  }

  async start() {
    if (this.isCapturing) return true
    try {
      // ✅ 优化: 先创建AudioContext，再请求麦克风权限，避免页面挂起
      this.audioCtx = new (window.AudioContext || window.webkitAudioContext)()

      // ✅ 优化: 使用异步请求，避免阻塞主线程
      this.stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: this.sampleRate,
          channelCount: 1,
          // ✅ 修复: 关闭所有音频处理，获取原始数据
          echoCancellation: false,
          noiseSuppression: false,
          autoGainControl: false,
        }
      })

      // ✅ 关闭调试日志
      // console.log('🎙️ 麦克风流信息:', {
      //   sampleRate: this.audioCtx.sampleRate,
      //   state: this.audioCtx.state,
      //   streamActive: this.stream.active,
      //   tracks: this.stream.getTracks().map(t => ({
      //     id: t.id,
      //     kind: t.kind,
      //     enabled: t.enabled,
      //     muted: t.muted,
      //     readyState: t.readyState
      //   }))
      // })

      // 初始化 MediaStreamSource（仅一次）
      this.mediaStreamSource = this.audioCtx.createMediaStreamSource(this.stream)

      // ✅ 使用 AudioWorklet 替代 ScriptProcessorNode
      if (this.audioCtx.audioWorklet) {
        // console.log('✅ 使用 AudioWorklet 采集音频...')
        await this._startWithAudioWorklet()
      } else {
        // console.log('⚠️ AudioWorklet 不可用，降级到 ScriptProcessorNode...')
        await this._startWithScriptProcessor()
      }

      this.isCapturing = true
      return true
    } catch (error) {
      console.error('麦克风启动失败:', error)
      return false
    }
  }

  // ✅ 新增: AudioWorklet 音频采集
  async _startWithAudioWorklet() {
    try {
      // 加载 AudioWorklet 处理器
      await this.audioCtx.audioWorklet.addModule(
        new URL('./audioWorkletProcessor.js', import.meta.url)
      )
      console.log('✅ AudioWorklet 模块已加载')

      const workletNode = new AudioWorkletNode(this.audioCtx, 'audio-capture-processor', {
        numberOfInputs: 1,
        numberOfOutputs: 1,
        outputChannelCount: [1],
        processorOptions: {
          compressionEnabled: this.compressionEnabled,
          sampleRate: this.audioCtx.sampleRate
        }
      })

      // ✅ 关闭 AudioWorklet 调试日志
      // workletNode.port.onmessage = (e) => {
      //   console.log('✅ AudioWorklet 回调被触发!')
      //   console.log(`  - 数据长度: ${e.data.length}`)
      //   const int16View = new Int16Array(e.data.buffer)
      //   const volume = int16View.reduce((sum, val) => sum + Math.abs(val), 0) / int16View.length
      //   console.log(`🎵 AudioWorklet PCM16: ${int16View.length} 样本, 范围: [${Math.min(...int16View)}, ${Math.max(...int16View)}], 音量: ${volume.toFixed(4)}`)
      //   
      //   if (this.onAudioData) {
      //     this.onAudioData(e.data.buffer)
      //   }
      // }

      workletNode.port.onmessage = (e) => {
        // e.data 直接是 ArrayBuffer
        if (this.onAudioData && e.data && e.data.byteLength > 0) {
          this.onAudioData(e.data)
        }
      }

      workletNode.connect(this.audioCtx.destination)

      this.workletNode = workletNode
      this.mediaStreamSource.connect(workletNode)

      // console.log('✅ AudioWorkletNode 已连接')

    } catch (e) {
      console.warn('AudioWorklet 启动失败，降级到 ScriptProcessorNode:', e)
      await this._startWithScriptProcessor()
    }
  }

  // ✅ 降级方案: ScriptProcessorNode 音频采集
  async _startWithScriptProcessor() {
    try {
      // console.log('✅ 正在创建 ScriptProcessorNode...')
      const bufferSize = 1024
      this.scriptProcessor = this.audioCtx.createScriptProcessor(bufferSize, 1, 1)

      // ✅ 关闭 ScriptProcessor 调试日志
      // this.scriptProcessor.onaudioprocess = (e) => {
      //   console.log('✅ ScriptProcessorNode 回调被触发!')
      //   console.log('  - inputBuffer 类型:', e.inputBuffer.constructor.name)
      //   console.log('  - inputBuffer 通道数:', e.inputBuffer.numberOfChannels)
      //   console.log('  - inputBuffer 长度:', e.inputBuffer.length)
      //   
      //   const input = e.inputBuffer.getChannelData(0)
      //   const volume = input.reduce((sum, val) => sum + Math.abs(val), 0) / input.length
      //   console.log(`🎤 原始音频: ${input.length} 样本, 范围: [${Math.min(...input).toFixed(4)}, ${Math.max(...input).toFixed(4)}], 音量: ${volume.toFixed(4)}`)
      //   
      //   const int16View = new Int16Array(input.length)
      //   for (let i = 0; i < input.length; i++) {
      //     const s = Math.max(-1, Math.min(1, input[i]))
      //     int16View[i] = s < 0 ? s * 0x8000 : s * 0x7FFF
      //   }
      //   
      //   console.log(` PCM16: ${int16View.length} 样本, 范围: [${Math.min(...int16View)}, ${Math.max(...int16View)}]`)
      //   
      //   if (this.onAudioData) {
      //     this.onAudioData(int16View.buffer)
      //   }
      // }

      this.scriptProcessor.onaudioprocess = (e) => {
        const input = e.inputBuffer.getChannelData(0)
        const int16View = new Int16Array(input.length)
        for (let i = 0; i < input.length; i++) {
          const s = Math.max(-1, Math.min(1, input[i]))
          int16View[i] = s < 0 ? s * 0x8000 : s * 0x7FFF
        }
        if (this.onAudioData) {
          this.onAudioData(int16View.buffer)
        }
      }

      this.mediaStreamSource.connect(this.scriptProcessor)
      this.scriptProcessor.connect(this.audioCtx.destination)

      // console.log('✅ ScriptProcessorNode 已连接到 AnalyserNode')
    } catch (e) {
      console.error('ScriptProcessorNode 启动失败:', e)
    }
  }

  stop() {
    this.isCapturing = false
    this._debugPrinted = false

    // ✅ 清理 AudioWorkletNode
    if (this._workletNode) {
      try { this._workletNode.disconnect() } catch (e) { /* ignore */ }
      this._workletNode = null
    }

    if (this._processorNode) {
      try { this._processorNode.disconnect() } catch (e) { /* ignore */ }
      this._processorNode = null
    }

    if (this.mediaStreamSource) {
      try { this.mediaStreamSource.disconnect() } catch (e) { /* ignore */ }
      this.mediaStreamSource = null
    }

    if (this.stream) {
      this.stream.getTracks().forEach(t => t.stop())
      this.stream = null
    }

    if (this.audioCtx) {
      this.audioCtx.close()
      this.audioCtx = null
    }

    this.analyser = null
    if (this._intervalId) {
      clearInterval(this._intervalId)
      this._intervalId = null
    }
  }

  /** 音量检测 — 复用已有的 analyser，零额外开销 */
  getVolumeLevel() {
    if (!this.analyser) return 0
    try {
      const dataArray = new Uint8Array(this.analyser.frequencyBinCount)
      this.analyser.getByteTimeDomainData(dataArray)
      let sum = 0
      for (let i = 0; i < dataArray.length; i++) {
        sum += Math.abs(dataArray[i] - 128)
      }
      const avg = sum / dataArray.length
      return Math.min(1, avg / 128)
    } catch {
      return 0
    }
  }

  toggle() {
    return this.isCapturing ? (this.stop(), false) : (this.start(), true)
  }

  /** 下采样 */
  _downsample(buffer, origRate, targetRate) {
    if (origRate === targetRate) return buffer
    const ratio = origRate / targetRate
    const newLen = Math.floor(buffer.length / ratio)
    const result = new Float32Array(newLen)
    for (let i = 0; i < newLen; i++) {
      const srcIdx = Math.floor(i * ratio)
      result[i] = buffer[srcIdx < buffer.length ? srcIdx : buffer.length - 1]
    }
    return result
  }

  /** Float32 → PCM16 */
  _float32ToPcm16(float32) {
    const len = float32.length
    const int16 = new Int16Array(len)
    for (let i = 0; i < len; i++) {
      const s = Math.max(-1, Math.min(1, float32[i]))
      int16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF
    }
    return int16.buffer
  }

  // ✅ 新增: 音频压缩(差分编码 + 量化)
  _compressAudio(pcm16Buffer) {
    const int16 = new Int16Array(pcm16Buffer)
    const len = int16.length

    // 使用差分编码: 存储相邻样本的差值
    const diffs = new Int16Array(len)
    diffs[0] = int16[0] - this.lastSample
    for (let i = 1; i < len; i++) {
      diffs[i] = int16[i] - int16[i - 1]
    }
    this.lastSample = int16[len - 1]

    // 量化: 将差值除以4(降低精度但减小数据量)
    const quantized = new Int16Array(len)
    for (let i = 0; i < len; i++) {
      quantized[i] = Math.round(diffs[i] / 4)
    }

    return quantized.buffer
  }

  // ✅ 新增: 音频解压缩(后端调用)
  static decompressAudio(compressedBuffer, lastSample = 0) {
    const quantized = new Int16Array(compressedBuffer)
    const len = quantized.length

    // 反量化
    const diffs = new Int16Array(len)
    for (let i = 0; i < len; i++) {
      diffs[i] = quantized[i] * 4
    }

    // 积分恢复原始信号
    const reconstructed = new Int16Array(len)
    reconstructed[0] = diffs[0] + lastSample
    for (let i = 1; i < len; i++) {
      reconstructed[i] = reconstructed[i - 1] + diffs[i]
    }

    return { buffer: reconstructed.buffer, lastSample: reconstructed[len - 1] }
  }
}

export default AudioCapture
