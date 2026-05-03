<template>
    <div class="page theme-page">
        <div class="theme-page-container">
            <div class="page-header">
                <h2><el-icon>
                        <Brush />
                    </el-icon> 主题切换</h2>
                <p>选择你喜欢的主题风格，系统将自动应用</p>
            </div>
            <div class="theme-grid-large">
                <div v-for="(theme, key) in themeStore.allThemes" :key="key" class="theme-card-large"
                    :class="{ active: themeStore.currentThemeName === key }" @click="themeStore.setTheme(key)"
                    :style="activeCardStyle(key)">
                    <div class="theme-preview-large" :style="{ background: theme.gradient }"></div>
                    <div class="theme-info-large">
                        <span class="theme-emoji-large">{{ theme.emoji }}</span>
                        <span class="theme-name-large">{{ theme.name }}</span>
                        <span class="theme-desc">{{ getThemeDesc(key) }}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { useThemeStore } from '@/stores/theme'
import { useNavigation } from '@/composables/useNavigation'
import { Brush } from '@element-plus/icons-vue'

const themeStore = useThemeStore()
const { getThemeDesc } = useNavigation()

// 主题卡片样式
const activeCardStyle = (key) => ({
    border: themeStore.currentThemeName === key
        ? `3px solid ${themeStore.currentTheme.primary}`
        : '3px solid transparent',
    boxShadow: themeStore.currentThemeName === key
        ? `0 0 30px ${themeStore.currentTheme.primary}40`
        : 'none'
})
</script>
