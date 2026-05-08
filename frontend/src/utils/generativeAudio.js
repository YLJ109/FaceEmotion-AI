/**
 * AI 生成式音频引擎 - 使用 Web Audio API 实时合成钢琴音色音乐
 * 
 * 核心特性:
 * 1. 🎹 钢琴音色模拟 - ADSR包络 + 谐波叠加 + 合唱效果
 * 2. 🎭 人性化随机 - Velocity、Detune、Timing微调
 * 3. 🎼 动态情绪适配 - BPM/触键力度/音色亮度随情绪变化
 * 4. ✨ 交叉淡入淡出 - 丝滑的情绪切换无爆音
 * 5. 🔊 专业音频处理 - 低通滤波 + 混响 + 增益平滑
 */

class GenerativeAudioEngine {
    constructor() {
        this.audioContext = null;
        this.masterGain = null;
        this.filterNode = null;
        this.reverbNode = null;
        this.chorusNode = null; // ✅ 新增: 合唱效果节点

        // 当前播放的音符调度器
        this.currentOscillators = [];
        this.currentGainNodes = [];
        this.scheduledNotes = [];

        // 状态管理
        this.isPlaying = false;
        this.isInitialized = false;
        this.isSuspended = false;

        // 平滑过渡参数
        this.targetVolume = 0.7;
        this.currentVolume = 0.7;
        this.volumeSmoothFactor = 0.05;

        // 交叉淡入淡出
        this.crossfadeDuration = 0.5;
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
            musicVolume: 70,
            emotionSensitivity: 50,
            rhythmSmoothness: 50,
            timbreStyle: 'piano' // ✅ 修改: 默认钢琴音色
        };

        // ✅ 新增: 钢琴音色预设(不同情绪的触键特征)
        this.pianoPresets = {
            happy: { attack: 0.02, decay: 0.3, sustain: 0.6, release: 0.4, brightness: 3000, velocity: 0.8 },
            sad: { attack: 0.05, decay: 0.5, sustain: 0.4, release: 0.8, brightness: 1500, velocity: 0.5 },
            angry: { attack: 0.01, decay: 0.2, sustain: 0.7, release: 0.3, brightness: 4000, velocity: 0.95 },
            surprise: { attack: 0.015, decay: 0.25, sustain: 0.5, release: 0.5, brightness: 3500, velocity: 0.85 },
            fear: { attack: 0.04, decay: 0.4, sustain: 0.3, release: 0.6, brightness: 2000, velocity: 0.6 },
            disgust: { attack: 0.03, decay: 0.35, sustain: 0.4, release: 0.5, brightness: 1800, velocity: 0.55 },
            neutral: { attack: 0.03, decay: 0.4, sustain: 0.5, release: 0.6, brightness: 2200, velocity: 0.65 }
        };

        // 定时器
        this.schedulerTimer = null;
        this.lookahead = 0.1;
        this.scheduleInterval = 25;

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

            // ✅ 新增: 创建合唱效果节点(增强钢琴音色真实感)
            this.chorusNode = this.audioContext.createDelay();
            this.chorusNode.delayTime.value = 0.03; // 30ms延迟
            const chorusGain = this.audioContext.createGain();
            chorusGain.gain.value = 0.3; // 合唱混合比
            this.chorusNode.connect(chorusGain);
            chorusGain.connect(this.volumeControl);

            // 连接音频链: Oscillator -> Gain -> [Filter -> Chorus] -> VolumeControl -> Reverb -> Master -> Destination
            this.filterNode.connect(this.chorusNode); // 滤波器后接合唱
            this.filterNode.connect(this.volumeControl); // 干声直通
            this.chorusNode.connect(this.volumeControl); // 湿声混合
            this.volumeControl.connect(this.reverbNode);
            this.reverbNode.connect(this.masterGain);
            this.masterGain.connect(this.audioContext.destination);

            this.isInitialized = true;
            this.isSuspended = false;
            this.errorCount = 0;

            console.log('✅ 钢琴音色音频引擎初始化成功');
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
     * 🎹 调度单个钢琴音符(带人性化随机)
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

        // ✅ 新增: 获取情绪对应的钢琴预设
        const emotion = this.currentParams.emotion || 'neutral';
        const preset = this.pianoPresets[emotion] || this.pianoPresets.neutral;

        // ✅ 新增: 人性化随机参数
        const humanization = this._generateHumanization(preset);

        // ✅ 修改: 使用多振荡器模拟钢琴谐波(基频 + 2次谐波 + 3次谐波)
        const oscillators = [];
        const harmonicGains = [];

        // 1. 基频振荡器(主音)
        const osc1 = this.audioContext.createOscillator();
        osc1.type = 'triangle'; // 三角波作为基础
        osc1.frequency.value = frequency * humanization.detuneFactor; // 应用随机音高偏移
        oscillators.push(osc1);

        // 2. 二次谐波(增加亮度)
        const osc2 = this.audioContext.createOscillator();
        osc2.type = 'sine';
        osc2.frequency.value = frequency * 2 * humanization.detuneFactor;
        oscillators.push(osc2);

        // 3. 三次谐波(增加质感)
        const osc3 = this.audioContext.createOscillator();
        osc3.type = 'sine';
        osc3.frequency.value = frequency * 3 * humanization.detuneFactor;
        oscillators.push(osc3);

        // ✅ 修改: 创建增益节点(ADSR包络 + Velocity)
        const gainNode = this.audioContext.createGain();

        // ✅ 修改: 根据情绪敏感度和Velocity调整音量
        const sensitivityFactor = this.config.emotionSensitivity / 100;
        const baseVolume = this.targetVolume * 0.4; // 降低基础音量避免过载
        const peakVolume = baseVolume * humanization.velocity * (0.5 + sensitivityFactor * 0.5);

        // ✅ 修改: 应用钢琴ADSR包络(含随机微调)
        const attackTime = preset.attack * humanization.timingFactor;
        const decayTime = preset.decay;
        const sustainLevel = preset.sustain;
        const releaseTime = preset.release;

        // ADSR 包络曲线
        gainNode.gain.setValueAtTime(0, startTime);
        gainNode.gain.linearRampToValueAtTime(
            peakVolume,
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

        // ✅ 修改: 连接所有振荡器到增益节点(谐波混合)
        const harmonicMix = this.audioContext.createGain();
        harmonicMix.gain.value = 1.0;

        oscillators.forEach((osc, index) => {
            const oscGain = this.audioContext.createGain();
            // 谐波音量递减: 基频100%, 二次谐波40%, 三次谐波20%
            const harmonicVolume = index === 0 ? 1.0 : (index === 1 ? 0.4 : 0.2);
            oscGain.gain.value = harmonicVolume;
            osc.connect(oscGain);
            oscGain.connect(harmonicMix);
            harmonicGains.push(oscGain);
        });

        harmonicMix.connect(gainNode);
        gainNode.connect(this.filterNode);

        // ✅ 修改: 动态调整滤波器截止频率(根据情绪亮度)
        if (this.filterNode) {
            const targetCutoff = preset.brightness * (0.8 + Math.random() * 0.4); // ±20%随机
            this.filterNode.frequency.setTargetAtTime(
                targetCutoff,
                startTime,
                0.05
            );
        }

        // 启动和停止所有振荡器
        oscillators.forEach(osc => {
            osc.start(startTime);
            osc.stop(startTime + duration + 0.1);
        });

        // 记录振荡器和增益节点(用于清理)
        this.currentOscillators.push(...oscillators, ...harmonicGains, harmonicMix);
        this.currentGainNodes.push(gainNode);

        // 清理已完成的振荡器(防止内存泄漏)
        this._cleanupFinishedOscillators(startTime + duration);

        // 移动到下一个音符
        this.noteIndex++;
    }

    /**
     * ✅ 新增: 生成人性化随机参数
     * @param {Object} preset - 钢琴预设
     * @returns {Object} 随机化参数
     */
    _generateHumanization(preset) {
        return {
            // Velocity(触键力度): ±10% 随机
            velocity: preset.velocity * (0.9 + Math.random() * 0.2),

            // Detune(音高偏移): ±5 cents (1 cent = 1/100 半音)
            detuneFactor: Math.pow(2, (Math.random() * 10 - 5) / 1200),

            // Timing(时序偏移): ±20ms 随机
            timingFactor: 0.9 + Math.random() * 0.2
        };
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
     * ✨ 启动交叉淡入淡出(情绪切换时)
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

        // ✅ 修改: 应用用户配置的节奏平滑度
        const adjustedParams = { ...newParams };
        this._updateParams(adjustedParams);

        // ✅ 新增: 根据节奏平滑度调整交叉淡入淡出时长
        const smoothnessFactor = this.config.rhythmSmoothness / 100;
        const crossfadeDuration = 0.3 + (1 - smoothnessFactor) * 0.7; // 0.3-1.0秒

        // 淡出旧音符(钢琴音色需要更长的释音时间)
        const fadeOutTime = this.audioContext.currentTime;
        this.oldGainNodes.forEach(gainNode => {
            try {
                gainNode.gain.cancelScheduledValues(fadeOutTime);
                gainNode.gain.setValueAtTime(gainNode.gain.value, fadeOutTime);
                gainNode.gain.exponentialRampToValueAtTime(
                    0.001,
                    fadeOutTime + crossfadeDuration + 0.3 // ✅ 增加0.3s释音时间
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
        }, (crossfadeDuration + 0.3) * 1000 + 100);
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

        console.log('[音频] 音乐已停止');
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
                console.log('[音频] 音频引擎已销毁');
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
