<template>
    <div class="theme-selector-wrapper">
        <el-popover placement="bottom-start" :width="340" trigger="click" :show-arrow="false"
            popper-class="theme-popover-glass">
            <template #reference>
                <el-button :icon="Brush" class="theme-btn" title="切换主题">
                    <span class="btn-text">{{ themeStore.currentTheme.name }}</span>
                    <span class="btn-emoji">{{ themeStore.currentTheme.emoji }}</span>
                </el-button>
            </template>

            <div class="theme-selector">
                <div class="theme-selector-header">
                    <h4>主题选择</h4>
                    <div class="mode-switch">
                        <el-radio-group v-model="themeStore.themeMode" size="small">
                            <el-radio-button value="auto">
                                <el-icon style="margin-right:4px">
                                    <Aim />
                                </el-icon>自动
                            </el-radio-button>
                            <el-radio-button value="manual">
                                <el-icon style="margin-right:4px">
                                    <MagicStick />
                                </el-icon>手动
                            </el-radio-button>
                        </el-radio-group>
                    </div>
                </div>

                <div class="theme-section">
                    <p class="section-title">🎭 表情主题</p>
                    <div class="theme-grid">
                        <button v-for="(theme, name) in emotionThemes" :key="name" @click="selectTheme(name)"
                            class="theme-item" :class="{ active: themeStore.currentThemeName === name }"
                            :style="activeStyle(name)">
                            <div class="theme-preview" :style="{ background: theme.gradient }">
                                <span class="emoji">{{ theme.emoji }}</span>
                            </div>
                            <span class="name">{{ theme.name }}</span>
                        </button>
                    </div>
                </div>

                <div class="theme-section">
                    <p class="section-title">✨ 特殊主题</p>
                    <div class="theme-grid">
                        <button v-for="(theme, name) in specialThemes" :key="name" @click="selectTheme(name)"
                            class="theme-item" :class="{ active: themeStore.currentThemeName === name }"
                            :style="activeStyle(name)">
                            <div class="theme-preview" :style="{ background: theme.gradient }">
                                <span class="emoji">{{ theme.emoji }}</span>
                            </div>
                            <span class="name">{{ theme.name }}</span>
                        </button>
                    </div>
                </div>
            </div>
        </el-popover>
    </div>
</template>

<script setup>
import { computed } from 'vue'
import { Brush, Aim, MagicStick } from '@element-plus/icons-vue'
import { useThemeStore } from '@/stores/theme'
import { THEMES } from '@/themes'

const themeStore = useThemeStore()

const emotionThemes = computed(() => {
    const r = {}
    Object.entries(THEMES).forEach(([n, t]) => { if (t.emotion && t.emotion !== 'special') r[n] = t })
    return r
})
const specialThemes = computed(() => {
    const r = {}
    Object.entries(THEMES).forEach(([n, t]) => { if (t.emotion === 'special') r[n] = t })
    return r
})

const activeStyle = (name) => ({
    borderColor: themeStore.currentThemeName === name ? 'var(--primary)' : 'transparent',
    boxShadow: themeStore.currentThemeName === name ? '0 0 15px var(--primary)' : 'none'
})

const selectTheme = (name) => themeStore.setTheme(name)
</script>

<style scoped>
.theme-btn {
    width: 100%;
    background: color-mix(in srgb, var(--primary) 15%, transparent) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-secondary) !important;
    border-radius: 14px !important;
    padding: 14px 18px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
    transition: all 0.3s ease !important;
}

.theme-btn:hover {
    background: color-mix(in srgb, var(--primary) 25%, transparent) !important;
    border-color: var(--primary) !important;
    color: var(--text) !important;
    transform: translateY(-1px);
}

.btn-emoji {
    font-size: 19px;
}

.btn-text {
    font-size: 15px;
}

.theme-selector-header {
    text-align: center;
    margin-bottom: 16px;
}

.theme-selector-header h4 {
    font-size: 17px;
    font-weight: 100;
    margin-bottom: 12px;
    background: linear-gradient(135deg, var(--highlight), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.mode-switch {
    display: flex;
    justify-content: center;
}

.theme-section {
    margin-bottom: 14px;
}

.section-title {
    font-size: 12px;
    color: var(--text-secondary);
    margin-bottom: 8px;
    /* font-weight: 100; */
    text-transform: uppercase;
    letter-spacing: 1px;
}

.theme-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 6px;
}

.theme-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 8px 4px;
    border: 2px solid transparent;
    border-radius: 12px;
    background: transparent;
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.theme-item:hover {
    transform: translateY(-3px) scale(1.04);
    background: rgba(162, 89, 255, 0.08);
}

.theme-preview {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.emoji {
    font-size: 20px;
}

.name {
    font-size: 11px;
    /* font-weight: 100; */
    color: var(--text-secondary);
}

.theme-item.active .name {
    color: var(--text);
}
</style>
