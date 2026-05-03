/**
 * 应用状态展示组件 - 空状态、加载中等
 */
<template>
    <div class="app-state">
        <!-- 空状态 -->
        <div v-if="type === 'empty'" class="state-wrapper">
            <div class="state-icon" :style="{ color: iconColor }">
                <el-icon :size="iconSize">
                    <component :is="icon" />
                </el-icon>
            </div>
            <h3 class="state-title">{{ title }}</h3>
            <p class="state-desc">{{ description }}</p>
            <slot />
        </div>

        <!-- 加载状态 -->
        <div v-else-if="type === 'loading'" class="state-wrapper loading">
            <el-icon :size="iconSize" class="spin-icon">
                <Loading />
            </el-icon>
            <h3 class="state-title">{{ title || '加载中...' }}</h3>
            <p v-if="description" class="state-desc">{{ description }}</p>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="type === 'error'" class="state-wrapper">
            <div class="state-icon error" :style="{ color: 'var(--error)' }">
                <el-icon :size="iconSize"><WarningFilled /></el-icon>
            </div>
            <h3 class="state-title">{{ title || '出错了' }}</h3>
            <p class="state-desc">{{ description }}</p>
            <slot />
        </div>
    </div>
</template>

<script setup>
import { Loading, WarningFilled } from '@element-plus/icons-vue'

const props = defineProps({
    type: { type: String, default: 'empty' },
    icon: { type: [String, Object], default: 'InfoFilled' },
    iconSize: { type: Number, default: 48 },
    iconColor: { type: String, default: 'var(--text-secondary)' },
    title: { type: String, default: '' },
    description: { type: String, default: '' },
})
</script>

<style scoped>
.state-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 20px;
    text-align: center;
    animation: fadeIn 0.4s ease;
}
.state-icon {
    margin-bottom: 16px;
    opacity: 0.5;
}
.state-icon.error { opacity: 0.7; }
.state-title {
    font-size: 18px;
    font-weight: 700;
    color: var(--text);
    margin: 0 0 8px;
}
.state-desc {
    font-size: 14px;
    color: var(--text-secondary);
    margin: 0;
    line-height: 1.6;
}
.spin-icon {
    animation: spin 1s linear infinite;
    color: var(--primary);
}
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>
