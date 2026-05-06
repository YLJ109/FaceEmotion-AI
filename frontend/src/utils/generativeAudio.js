/**
 * AI 生成式音频引擎 - 使用 Web Audio API 实时合成音乐
 * 
 * 核心特性:
 * 1. ADSR 包络控制 - 杜绝炸麦与爆音
 * 2. 全局增益平滑过渡 - 消除音量忽大忽小
 * 3. 交叉淡入淡出(Cross-fade) - 丝滑的情绪切换
 * 4. 低通滤波器 - 柔化音色,减少刺耳高频
 * 5. 内存管理 - 避免振荡器泄漏
 */

class GenerativeAudioEngine {
    constructor() {
        this.audioContext = null;
        this.masterGain = null;
        this.filterNode = null;
        this.reverbNode = null;

        // 当前播放的音符调度器
        this.currentOscillators = [];
        this.currentGainNodes = [];
        this.scheduledNotes = [];

        // 状态管理
        this.isPlaying = false;
        this.isInitialized = false;
        this.isSuspended = false;

        // 平滑过渡参数
        this.targetVolume = 0.7;  // ✅ 提高: 从0.5提升到0.7，基础音量更大
        this.currentVolume = 0.7;  // ✅ 提高: 从0.5提升到0.7
        this.volumeSmoothFactor = 0.05; // 音量平滑系数(越小越平滑)

        // 交叉淡入淡出
        this.crossfadeDuration = 0.5; // 跨情绪淡入淡出时长(秒)
        this.oldOscillators = [];
        this.oldGainNodes = [];
        this.isCrossfading = false;

        // 音乐参数
        this.currentParams = null;
        this.noteIndex = 0;
        this.chordIndex = 0;
        this.nextNoteTime = 0;

        // ✅ 新增: 用户可配置的音乐参数
        this.config = {
            musicVolume: 70,           // 基础音量 (0-100)
            emotionSensitivity: 50,    // 情绪敏感度 (0-100)
            rhythmSmoothness: 50,      // 节奏平滑度 (0-100)
            timbreStyle: 'sine'        // 音色风格
        };

        // 定时器
        this.schedulerTimer = null;
        this.lookahead = 0.1; // 提前调度时间(秒)
        this.scheduleInterval = 25; // 调度间隔(毫秒)

        // 错误处理
        this.errorCount = 0;
        this.maxErrors = 5;
    }

    /**
     * 初始化音频上下文
     * 必须在用户交互后调用(浏览器策略要求)
     */
    async init() {
        if (this.isInitialized) return;

        try {
            // 创建音频上下文
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            this.audioContext = new AudioContext();

            // 检查是否被挂起
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
            }

            // 创建主增益节点(全局音量控制)
            this.masterGain = this.audioContext.createGain();
            this.masterGain.gain.value = this.currentVolume;

            // ✅ 新增: 创建音量调节节点(用户控制)
            this.volumeControl = this.audioContext.createGain();
            this.volumeControl.gain.value = 1.2; // ✅ 提高: 从1.0提升到1.2，增加20%增益

            // 创建低通滤波器(柔化音色)
            this.filterNode = this.audioContext.createBiquadFilter();
            this.filterNode.type = 'lowpass';
            this.filterNode.frequency.value = 2000;
            this.filterNode.Q.value = 1.0;

            // 创建简单的混响效果(使用延迟线模拟)
            this.reverbNode = this.audioContext.createConvolver();
            this._createSimpleReverb();

            // 连接音频链: Oscillator -> Gain -> VolumeControl -> Filter -> Reverb -> Master -> Destination
            this.filterNode.connect(this.volumeControl);
            this.volumeControl.connect(this.reverbNode);
            this.reverbNode.connect(this.masterGain);
            this.masterGain.connect(this.audioContext.destination);

            this.isInitialized = true;
            this.isSuspended = false;
            this.errorCount = 0;

            console.log('✅ 音频引擎初始化成功');
        } catch (error) {
            console.error('❌ 音频引擎初始化失败:', error);
            this.errorCount++;
            if (this.errorCount >= this.maxErrors) {
                console.warn('⚠️ 音频引擎初始化失败次数过多,已禁用');
                this.isInitialized = false;
            }
        }
    }

    /**
     * 创建简单混响(使用指数衰减噪声)
     */
    _createSimpleReverb() {
        const sampleRate = this.audioContext.sampleRate;
        const length = sampleRate * 2; // 2秒混响
        const impulse = this.audioContext.createBuffer(2, length, sampleRate);

        for (let channel = 0; channel < 2; channel++) {
            const channelData = impulse.getChannelData(channel);
            for (let i = 0; i < length; i++) {
                // 指数衰减噪声
                channelData[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / length, 3);
            }
        }

        this.reverbNode.buffer = impulse;
    }

    /**
     * ✅ 新增: 更新音乐配置参数
     * @param {Object} config - 音乐配置对象
     */
    updateConfig(config) {
        if (!config) return;

        if (config.music_volume !== undefined) {
            this.config.musicVolume = Math.max(0, Math.min(100, config.music_volume));
        }
        if (config.emotion_sensitivity !== undefined) {
            this.config.emotionSensitivity = Math.max(0, Math.min(100, config.emotion_sensitivity));
        }
        if (config.rhythm_smoothness !== undefined) {
            this.config.rhythmSmoothness = Math.max(0, Math.min(100, config.rhythm_smoothness));
        }
        if (config.timbre_style !== undefined) {
            this.config.timbreStyle = config.timbre_style;
        }

        // 立即应用音量变化
        this.setVolume(this.config.musicVolume);

        console.log('🎵 音乐配置已更新:', this.config);
    }

    /**
     * 播放音乐(根据参数动态生成)
     * @param {Object} params - 音乐参数
     * @param {number} params.bpm - 节拍每分钟
     * @param {number} params.root_note - 根音(MIDI编号)
     * @param {Array} params.melody - 旋律音符序列(MIDI编号数组)
     * @param {string} params.waveform - 波形类型 ('sine'|'square'|'sawtooth'|'triangle')
     * @param {number} params.filter_cutoff - 滤波器截止频率(Hz)
     * @param {number} params.reverb_mix - 混响混合比(0.0-1.0)
     * @param {number} params.volume - 音量(0.0-1.0)
     */
    playMusic(params) {
        if (!this.isInitialized) {
            console.warn('⚠️ 音频引擎未初始化,请先调用 init()');
            return;
        }

        // 恢复被挂起的音频上下文
        if (this.audioContext.state === 'suspended') {
            this.audioContext.resume().then(() => {
                this.isSuspended = false;
                console.log('🔄 音频上下文已恢复');
            });
        }

        // 检测情绪变化,触发交叉淡入淡出
        const emotionChanged = this.currentParams &&
            this.currentParams.emotion !== params.emotion;

        if (emotionChanged && this.isPlaying) {
            this._startCrossfade(params);
        } else {
            // ✅ 修改: 应用用户配置的音色风格
            const adjustedParams = {
                ...params,
                waveform: this.config.timbreStyle || params.waveform
            };
            this._updateParams(adjustedParams);
            this._startScheduler();
        }
    }

    /**
     * 更新音乐参数(不重启播放)
     */
    _updateParams(params) {
        const oldBpm = this.currentParams?.bpm || params.bpm;
        const newBpm = params.bpm || 100;

        this.currentParams = params;
        this.targetVolume = params.volume || 0.5;

        // ✅ 新增: 根据节奏平滑度实现BPM平滑过渡
        const smoothnessFactor = this.config.rhythmSmoothness / 100; // 0-1
        const bpmTransitionTime = 0.5 + (1 - smoothnessFactor) * 2.0; // 0.5-2.5秒

        if (oldBpm !== newBpm && this.isPlaying) {
            console.log(`🎵 BPM平滑过渡: ${oldBpm} → ${newBpm} (${bpmTransitionTime.toFixed(1)}s)`);

            // 使用渐变方式过渡BPM，避免突兀的节奏变化
            this._smoothBpmTransition(oldBpm, newBpm, bpmTransitionTime);
        }

        // 平滑更新滤波器截止频率
        if (this.filterNode) {
            const targetCutoff = params.filter_cutoff || 2000;
            this.filterNode.frequency.setTargetAtTime(
                targetCutoff,
                this.audioContext.currentTime,
                0.1
            );
        }

        // 平滑更新混响混合比
        if (this.reverbNode) {
            // 混响通过湿/干比控制,这里简化为直接调整增益
            // 实际项目中可以使用 GainNode 实现更精细的控制
        }
    }

    /**
     * ✅ 新增: BPM平滑过渡算法
     * @param {number} oldBpm - 旧BPM
     * @param {number} newBpm - 新BPM
     * @param {number} transitionTime - 过渡时间(秒)
     */
    _smoothBpmTransition(oldBpm, newBpm, transitionTime) {
        const startTime = this.audioContext.currentTime;
        const endTime = startTime + transitionTime;
        const steps = Math.ceil(transitionTime * 10); // 每秒10步

        // 使用缓动函数实现更自然的过渡
        const easeInOutCubic = (t) => {
            return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
        };

        // 预计算过渡期间的BPM变化
        this._bpmTransition = {
            startTime,
            endTime,
            oldBpm,
            newBpm,
            transitionTime,
            getBpmAtTime: (time) => {
                if (time <= startTime) return oldBpm;
                if (time >= endTime) return newBpm;

                const progress = (time - startTime) / transitionTime;
                const easedProgress = easeInOutCubic(progress);
                return oldBpm + (newBpm - oldBpm) * easedProgress;
            }
        };

        // 过渡完成后清除
        setTimeout(() => {
            this._bpmTransition = null;
        }, transitionTime * 1000 + 100);
    }

    /**
     * 启动音符调度器
     */
    _startScheduler() {
        if (this.schedulerTimer) return; // 已在运行

        this.isPlaying = true;
        this.noteIndex = 0;
        this.chordIndex = 0;
        this.nextNoteTime = this.audioContext.currentTime + 0.1;

        this.schedulerTimer = setInterval(() => {
            this._scheduler();
        }, this.scheduleInterval);

        console.log(`🎵 开始播放: ${this.currentParams.emotion}, BPM=${this.currentParams.bpm}`);
        // ✅ 关闭调试日志
        // console.log(`🎵 开始播放: ${this.currentParams.emotion}, BPM=${this.currentParams.bpm}`);
    }

    /**
     * 停止调度器
     */
    _stopScheduler() {
        if (this.schedulerTimer) {
            clearInterval(this.schedulerTimer);
            this.schedulerTimer = null;
        }
    }

    /**
     * 音符调度器(提前调度以避免卡顿)
     */
    _scheduler() {
        if (!this.isPlaying || !this.currentParams) return;

        const currentTime = this.audioContext.currentTime;

        // ✅ 修改: 使用平滑BPM过渡（如果正在过渡中）
        let currentBpm = this.currentParams.bpm;
        if (this._bpmTransition) {
            currentBpm = this._bpmTransition.getBpmAtTime(currentTime);
        }

        const noteDuration = 60 / currentBpm; // 每个音符时长(秒)

        // 提前调度未来 lookahead 时间内的音符
        while (this.nextNoteTime < currentTime + this.lookahead) {
            this._scheduleNote(this.nextNoteTime, noteDuration);
            this.nextNoteTime += noteDuration;
        }
    }

    /**
     * 调度单个音符
     * @param {number} startTime - 音符开始时间(音频上下文时间)
     * @param {number} duration - 音符持续时间(秒)
     */
    _scheduleNote(startTime, duration) {
        if (!this.currentParams || !this.currentParams.melody) return;

        const melody = this.currentParams.melody;
        if (melody.length === 0) return;

        // 获取当前音符(MIDI编号)
        const midiNote = melody[this.noteIndex % melody.length];
        const frequency = this._midiToFreq(midiNote);

        // ✅ 修改: 使用用户配置的音色风格
        const waveform = this.currentParams.waveform || this.config.timbreStyle || 'sine';

        // 创建振荡器
        const oscillator = this.audioContext.createOscillator();
        oscillator.type = waveform;
        oscillator.frequency.value = frequency;

        // 创建增益节点(ADSR 包络)
        const gainNode = this.audioContext.createGain();

        // ✅ 修改: 根据情绪敏感度调整音量变化幅度
        const sensitivityFactor = this.config.emotionSensitivity / 100; // 0-1
        const baseVolume = this.targetVolume * 0.5;
        const peakVolume = baseVolume * (0.5 + sensitivityFactor * 0.5); // 敏感度越高,音量变化越大

        // ADSR 包络参数
        const attackTime = 0.05;  // 起音时间(秒)
        const decayTime = 0.1;    // 衰减时间(秒)
        const sustainLevel = 0.8; // 延音电平
        const releaseTime = 0.15; // 释音时间(秒)

        // 应用 ADSR 包络
        gainNode.gain.setValueAtTime(0, startTime);
        gainNode.gain.linearRampToValueAtTime(
            peakVolume,  // ✅ 使用敏感度调整后的峰值音量
            startTime + attackTime
        );
        gainNode.gain.exponentialRampToValueAtTime(
            peakVolume * sustainLevel,
            startTime + attackTime + decayTime
        );
        gainNode.gain.setValueAtTime(
            peakVolume * sustainLevel,
            startTime + duration - releaseTime
        );
        gainNode.gain.exponentialRampToValueAtTime(
            0.001,
            startTime + duration
        );

        // 连接音频链
        oscillator.connect(gainNode);
        gainNode.connect(this.filterNode);

        // 启动和停止振荡器
        oscillator.start(startTime);
        oscillator.stop(startTime + duration + 0.1); // 额外留0.1秒确保释音完成

        // 记录振荡器和增益节点(用于清理)
        this.currentOscillators.push(oscillator);
        this.currentGainNodes.push(gainNode);

        // 清理已完成的振荡器(防止内存泄漏)
        this._cleanupFinishedOscillators(startTime + duration);

        // 移动到下一个音符
        this.noteIndex++;
    }

    /**
     * 清理已完成的振荡器
     * @param {number} currentTime - 当前音频时间
     */
    _cleanupFinishedOscillators(currentTime) {
        // 保留最近 2 秒内的振荡器(确保释音完成)
        const maxAge = 2.0;

        // 这里简化处理:每调度 100 个音符清理一次
        if (this.currentOscillators.length > 100) {
            this.currentOscillators.slice(0, 50).forEach(osc => {
                try {
                    osc.disconnect();
                } catch (e) {
                    // 忽略断开连接错误
                }
            });
            this.currentOscillators = this.currentOscillators.slice(50);
            this.currentGainNodes = this.currentGainNodes.slice(50);
        }
    }

    /**
     * 启动交叉淡入淡出(情绪切换时)
     * @param {Object} newParams - 新情绪的音乐参数
     */
    _startCrossfade(newParams) {
        if (this.isCrossfading) return;

        this.isCrossfading = true;

        // 保存旧振荡器用于淡出
        this.oldOscillators = [...this.currentOscillators];
        this.oldGainNodes = [...this.currentGainNodes];

        // 清空当前列表(新音符将使用新参数)
        this.currentOscillators = [];
        this.currentGainNodes = [];

        // ✅ 修改: 应用用户配置的音色风格和节奏平滑度
        const adjustedParams = {
            ...newParams,
            waveform: this.config.timbreStyle || newParams.waveform
        };
        this._updateParams(adjustedParams);

        // ✅ 新增: 根据节奏平滑度调整交叉淡入淡出时长
        const smoothnessFactor = this.config.rhythmSmoothness / 100;
        const crossfadeDuration = 0.3 + (1 - smoothnessFactor) * 0.7; // 0.3-1.0秒

        // 淡出旧音符
        const fadeOutTime = this.audioContext.currentTime;
        this.oldGainNodes.forEach(gainNode => {
            try {
                gainNode.gain.cancelScheduledValues(fadeOutTime);
                gainNode.gain.setValueAtTime(gainNode.gain.value, fadeOutTime);
                gainNode.gain.exponentialRampToValueAtTime(
                    0.001,
                    fadeOutTime + crossfadeDuration
                );
            } catch (e) {
                console.warn('⚠️ 淡出旧音符失败:', e);
            }
        });

        // 清理旧振荡器
        setTimeout(() => {
            this.oldOscillators.forEach(osc => {
                try {
                    osc.stop();
                    osc.disconnect();
                } catch (e) {
                    // 忽略错误
                }
            });
            this.oldOscillators = [];
            this.oldGainNodes = [];
            this.isCrossfading = false;
        }, crossfadeDuration * 1000 + 100);
    }

    /**
     * 平滑更新全局音量
     */
    _smoothVolumeUpdate() {
        if (!this.masterGain) return;

        // 指数平滑
        const diff = this.targetVolume - this.currentVolume;
        if (Math.abs(diff) > 0.001) {
            this.currentVolume += diff * this.volumeSmoothFactor;
            this.masterGain.gain.setTargetAtTime(
                this.currentVolume,
                this.audioContext.currentTime,
                0.05
            );
        }
    }

    /**
     * 停止播放
     */
    stop() {
        this.isPlaying = false;
        this._stopScheduler();

        // 停止所有振荡器
        this.currentOscillators.forEach(osc => {
            try {
                osc.stop();
                osc.disconnect();
            } catch (e) {
                // 忽略错误
            }
        });
        this.currentOscillators = [];
        this.currentGainNodes = [];

        console.log('⏹️ 音乐已停止');
    }

    /**
     * ✅ 新增: 设置音量(0-100)
     * @param {number} volume - 音量百分比(0-100)
     */
    setVolume(volume) {
        if (!this.isInitialized || !this.volumeControl) {
            console.warn('⚠️ 音频引擎未初始化');
            return;
        }

        // 限制音量范围
        const clampedVolume = Math.max(0, Math.min(100, volume));

        // 转换为增益值(0-1)
        const gainValue = clampedVolume / 100;

        // 平滑过渡到目标音量
        const currentTime = this.audioContext.currentTime;
        this.volumeControl.gain.setTargetAtTime(gainValue, currentTime, 0.1);

        console.log(`🔊 音量已设置为: ${clampedVolume}%`);
    }

    /**
     * ✅ 新增: 获取当前音量
     * @returns {number} 音量百分比(0-100)
     */
    getVolume() {
        if (!this.volumeControl) return 50;
        return Math.round(this.volumeControl.gain.value * 100);
    }

    /**
     * ✅ 新增: 静音/取消静音
     */
    toggleMute() {
        if (!this.volumeControl) return;

        const currentGain = this.volumeControl.gain.value;
        if (currentGain > 0) {
            // 保存当前音量并静音
            this._savedVolume = currentGain;
            this.setVolume(0);
        } else {
            // 恢复音量
            if (this._savedVolume !== undefined) {
                this.setVolume(Math.round(this._savedVolume * 100));
            } else {
                this.setVolume(50);
            }
        }
    }

    /**
     * 销毁音频引擎(释放资源)
     */
    destroy() {
        this.stop();

        if (this.audioContext) {
            this.audioContext.close().then(() => {
                console.log('🗑️ 音频引擎已销毁');
            });
        }

        this.isInitialized = false;
        this.currentParams = null;
    }

    /**
     * MIDI 音符转频率
     * @param {number} midiNote - MIDI 音符编号(C4=60)
     * @returns {number} 频率(Hz)
     */
    _midiToFreq(midiNote) {
        return 440 * Math.pow(2, (midiNote - 69) / 12);
    }

    /**
     * 获取引擎状态
     */
    getState() {
        return {
            isInitialized: this.isInitialized,
            isPlaying: this.isPlaying,
            isSuspended: this.isSuspended,
            currentEmotion: this.currentParams?.emotion || 'none',
            currentVolume: this.currentVolume,
            oscillatorCount: this.currentOscillators.length,
            config: this.config // ✅ 新增: 返回当前配置
        };
    }
}

// 导出单例
export default new GenerativeAudioEngine();
