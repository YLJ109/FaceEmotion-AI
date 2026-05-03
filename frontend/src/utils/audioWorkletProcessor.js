/**
 * AudioWorklet 音频处理器
 * 替代已废弃的 ScriptProcessorNode，提供更低延迟和更稳定的音频采集
 */
class AudioCaptureProcessor extends AudioWorkletProcessor {
    constructor(options) {
        super()
        this.processorOptions = options.processorOptions || {}
        this.targetSampleRate = this.processorOptions.sampleRate || 16000
        this.compressionEnabled = this.processorOptions.compressionEnabled || false
        // ✅ 关闭调试日志
        // console.log('AudioWorkletProcessor 初始化:', this.processorOptions)
    }

    process(inputs, outputs, parameters) {
        const input = inputs[0]
        if (!input || input.length === 0) {
            return true
        }

        const channelData = input[0]
        if (!channelData || channelData.length === 0) {
            return true
        }

        // 下采样到目标采样率
        const downsampled = this._downsample(channelData, sampleRate, this.targetSampleRate)

        // Float32 转 PCM16
        const pcm16 = this._float32ToPcm16(downsampled)

        // 发送到主线程（使用 Transferable 对象提高性能）
        this.port.postMessage(pcm16.buffer, [pcm16.buffer])

        return true
    }

    _downsample(buffer, originalRate, targetRate) {
        if (originalRate === targetRate) {
            return buffer
        }

        const ratio = originalRate / targetRate
        const newLength = Math.floor(buffer.length / ratio)
        const result = new Float32Array(newLength)

        for (let i = 0; i < newLength; i++) {
            const index = Math.floor(i * ratio)
            result[i] = buffer[index]
        }

        return result
    }

    _float32ToPcm16(buffer) {
        const pcm16 = new Int16Array(buffer.length)
        for (let i = 0; i < buffer.length; i++) {
            const s = Math.max(-1, Math.min(1, buffer[i]))
            pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF
        }
        return pcm16
    }
}

registerProcessor('audio-capture-processor', AudioCaptureProcessor)
