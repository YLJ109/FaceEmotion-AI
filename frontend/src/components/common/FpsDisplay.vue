"""UI/UX 辅助组件 - FPS显示、情绪标签等"""
<template>
    <div class="fps-indicator" v-if="fps > 0">
        <span class="fps-dot"></span>
        <span class="fps-value">{{ fps.toFixed(1) }}</span>
        <span class="fps-unit">FPS</span>
    </div>
</template>

<script setup>
defineProps({
    fps: { type: Number, default: 0 }
})
</script>

<style scoped>
.fps-indicator {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(8px);
    padding: 4px 12px;
    border-radius: 8px;
    font-family: 'Consolas', monospace;
    border: 1px solid rgba(0, 217, 255, 0.2);
}

.fps-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #00D9FF;
    animation: pulse 1s ease-in-out infinite;
}

.fps-value {
    font-size: 14px;
    font-weight: 700;
    color: #00D9FF;
}

.fps-unit {
    font-size: 11px;
    color: rgba(0, 217, 255, 0.6);
    font-weight: 600;
}

@keyframes pulse {

    0%,
    100% {
        opacity: 1;
        box-shadow: 0 0 4px #00D9FF;
    }

    50% {
        opacity: 0.3;
        box-shadow: none;
    }
}
</style>
