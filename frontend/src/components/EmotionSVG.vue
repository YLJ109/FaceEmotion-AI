<template>
    <svg :class="['emotion-svg', size, { 'is-animated': animated }]" :width="svgSize" :height="svgSize"
        viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
        <!-- 😊 开心 -->
        <g v-if="emotion === 'happy'" class="emotion-group">
            <circle cx="50" cy="50" r="45" fill="url(#happy-gradient)" stroke="#FFD700" stroke-width="3" />
            <path d="M30 42 Q35 38 40 42" stroke="#333" stroke-width="2.5" stroke-linecap="round" fill="none" />
            <path d="M60 42 Q65 38 70 42" stroke="#333" stroke-width="2.5" stroke-linecap="round" fill="none" />
            <path d="M30 60 Q50 75 70 60" stroke="#333" stroke-width="2.5" stroke-linecap="round" fill="none" />
            <circle cx="25" cy="55" r="5" fill="#FFB6C1" opacity="0.6" />
            <circle cx="75" cy="55" r="5" fill="#FFB6C1" opacity="0.6" />
        </g>

        <!-- 😄 享受/enjoy - 更夸张的开心表情 -->
        <g v-else-if="emotion === 'enjoy'" class="emotion-group">
            <circle cx="50" cy="50" r="45" fill="url(#enjoy-gradient)" stroke="#26DE81" stroke-width="3" />
            <!-- 眯眼笑 -->
            <path d="M28 40 Q35 35 42 40" stroke="#333" stroke-width="2.5" stroke-linecap="round" fill="none" />
            <path d="M58 40 Q65 35 72 40" stroke="#333" stroke-width="2.5" stroke-linecap="round" fill="none" />
            <!-- 大笑 -->
            <path d="M25 58 Q50 80 75 58" stroke="#333" stroke-width="2.5" stroke-linecap="round" fill="#FF6B6B"
                opacity="0.8" />
            <!-- 舌头 -->
            <ellipse cx="50" cy="68" rx="8" ry="6" fill="#FF6B6B" />
            <!-- 红晕 -->
            <circle cx="22" cy="52" r="6" fill="#FFB6C1" opacity="0.7" />
            <circle cx="78" cy="52" r="6" fill="#FFB6C1" opacity="0.7" />
        </g>

        <!-- 😢 悲伤 -->
        <g v-else-if="emotion === 'sad'" class="emotion-group">
            <circle cx="50" cy="50" r="45" fill="url(#sad-gradient)" stroke="#87CEEB" stroke-width="3" />
            <path d="M30 48 Q35 44 40 48" stroke="#333" stroke-width="2.5" stroke-linecap="round" fill="none" />
            <path d="M60 48 Q65 44 70 48" stroke="#333" stroke-width="2.5" stroke-linecap="round" fill="none" />
            <path d="M35 68 Q50 60 65 68" stroke="#333" stroke-width="2.5" stroke-linecap="round" fill="none" />
            <path d="M42 58 Q42 65 40 70" stroke="#4682B4" stroke-width="2" stroke-linecap="round" fill="none">
                <animate attributeName="opacity" values="1;0.5;1" dur="2s" repeatCount="indefinite" />
            </path>
        </g>

        <!-- 😠 愤怒 -->
        <g v-else-if="emotion === 'angry'" class="emotion-group">
            <circle cx="50" cy="50" r="45" fill="url(#angry-gradient)" stroke="#FF4500" stroke-width="3" />
            <path d="M28 40 L42 46" stroke="#333" stroke-width="2.5" stroke-linecap="round" />
            <path d="M72 40 L58 46" stroke="#333" stroke-width="2.5" stroke-linecap="round" />
            <circle cx="35" cy="50" r="4" fill="#333" />
            <circle cx="65" cy="50" r="4" fill="#333" />
            <path d="M35 68 Q50 62 65 68" stroke="#333" stroke-width="2.5" stroke-linecap="round" fill="none" />
            <path d="M20 30 L25 35 M75 30 L80 35" stroke="#FF4500" stroke-width="2" stroke-linecap="round">
                <animate attributeName="opacity" values="1;0.3;1" dur="1s" repeatCount="indefinite" />
            </path>
        </g>

        <!-- 😲 惊讶 -->
        <g v-else-if="emotion === 'surprise'" class="emotion-group">
            <circle cx="50" cy="50" r="45" fill="url(#surprise-gradient)" stroke="#DDA0DD" stroke-width="3" />
            <circle cx="35" cy="45" r="6" fill="#333" />
            <circle cx="65" cy="45" r="6" fill="#333" />
            <circle cx="35" cy="45" r="2.5" fill="white" />
            <circle cx="65" cy="45" r="2.5" fill="white" />
            <ellipse cx="50" cy="68" rx="10" ry="12" fill="#333" />
        </g>

        <!-- 😨 恐惧 -->
        <g v-else-if="emotion === 'fear'" class="emotion-group">
            <circle cx="50" cy="50" r="45" fill="url(#fear-gradient)" stroke="#9370DB" stroke-width="3" />
            <circle cx="35" cy="45" r="7" fill="#333" />
            <circle cx="65" cy="45" r="7" fill="#333" />
            <circle cx="35" cy="45" r="2.5" fill="white" />
            <circle cx="65" cy="45" r="2.5" fill="white" />
            <ellipse cx="50" cy="70" rx="8" ry="10" fill="#333" />
            <path d="M25 30 Q30 25 35 30" stroke="#9370DB" stroke-width="2" fill="none" opacity="0.6">
                <animate attributeName="d" values="M25 30 Q30 25 35 30;M25 30 Q30 28 35 30;M25 30 Q30 25 35 30"
                    dur="1.5s" repeatCount="indefinite" />
            </path>
        </g>

        <!-- 🤢 厌恶 -->
        <g v-else-if="emotion === 'disgust'" class="emotion-group">
            <circle cx="50" cy="50" r="45" fill="url(#disgust-gradient)" stroke="#32CD32" stroke-width="3" />
            <path d="M30 45 Q35 42 40 45" stroke="#333" stroke-width="2.5" stroke-linecap="round" fill="none" />
            <path d="M60 45 Q65 42 70 45" stroke="#333" stroke-width="2.5" stroke-linecap="round" fill="none" />
            <path d="M35 65 Q50 58 65 65" stroke="#333" stroke-width="2.5" stroke-linecap="round" fill="none" />
            <path d="M25 55 L30 60 M70 60 L75 55" stroke="#32CD32" stroke-width="2" stroke-linecap="round"
                opacity="0.6" />
        </g>

        <!-- 😐 平静 -->
        <g v-else class="emotion-group">
            <circle cx="50" cy="50" r="45" fill="url(#neutral-gradient)" stroke="#D3D3D3" stroke-width="3" />
            <circle cx="35" cy="45" r="4.5" fill="#333" />
            <circle cx="65" cy="45" r="4.5" fill="#333" />
            <line x1="35" y1="65" x2="65" y2="65" stroke="#333" stroke-width="2.5" stroke-linecap="round" />
        </g>

        <defs>
            <radialGradient id="happy-gradient" cx="50%" cy="50%">
                <stop offset="0%" stop-color="#FFE066" />
                <stop offset="100%" stop-color="#FFD700" />
            </radialGradient>
            <radialGradient id="enjoy-gradient" cx="50%" cy="50%">
                <stop offset="0%" stop-color="#90EE90" />
                <stop offset="100%" stop-color="#26DE81" />
            </radialGradient>
            <radialGradient id="sad-gradient" cx="50%" cy="50%">
                <stop offset="0%" stop-color="#B0E0E6" />
                <stop offset="100%" stop-color="#87CEEB" />
            </radialGradient>
            <radialGradient id="angry-gradient" cx="50%" cy="50%">
                <stop offset="0%" stop-color="#FF6B6B" />
                <stop offset="100%" stop-color="#FF4500" />
            </radialGradient>
            <radialGradient id="surprise-gradient" cx="50%" cy="50%">
                <stop offset="0%" stop-color="#E6E6FA" />
                <stop offset="100%" stop-color="#DDA0DD" />
            </radialGradient>
            <radialGradient id="fear-gradient" cx="50%" cy="50%">
                <stop offset="0%" stop-color="#D8BFD8" />
                <stop offset="100%" stop-color="#9370DB" />
            </radialGradient>
            <radialGradient id="disgust-gradient" cx="50%" cy="50%">
                <stop offset="0%" stop-color="#90EE90" />
                <stop offset="100%" stop-color="#32CD32" />
            </radialGradient>
            <radialGradient id="neutral-gradient" cx="50%" cy="50%">
                <stop offset="0%" stop-color="#F5F5F5" />
                <stop offset="100%" stop-color="#D3D3D3" />
            </radialGradient>
        </defs>
    </svg>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
    emotion: { type: String, default: 'neutral' },
    size: {
        type: String, default: 'medium',
        validator: (v) => ['small', 'medium', 'large', 'xlarge'].includes(v)
    },
    animated: { type: Boolean, default: true }
})

const svgSize = computed(() => ({
    small: 36, medium: 72, large: 108, xlarge: 140
}[props.size] || 72))
</script>

<style scoped>
.emotion-svg {
    display: inline-block;
    transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    /* filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.25)); */
    vertical-align: middle;
}

.emotion-svg:hover {
    transform: scale(1.15);
}

.emotion-svg.small {
    /* filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2)); */
}

.emotion-svg.large,
.emotion-svg.xlarge {
    /* filter: drop-shadow(0 8px 20px rgba(0, 0, 0, 0.35)); */
}

.emotion-group {
    animation: float 3s ease-in-out infinite;
}

.emotion-group .is-animated {
    animation: none;
}

@keyframes float {

    0%,
    100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-3px);
    }
}
</style>
