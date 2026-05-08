<template>
    <aside class="sidebar" :class="{ collapsed: isCollapsed }">
        <!-- 主导航 -->
        <nav class="sidebar-nav">
            <!-- 数据模式分组 -->
            <div class="nav-group-label nav-group-first" v-show="!isCollapsed">数据</div>
            <el-tooltip v-for="item in navigationMenus.data" :key="item.key" :content="item.label" placement="right" :disabled="!isCollapsed">
                <div class="nav-item" :class="{ active: isActive(item.key) }" @click="navigateTo(item.key)">
                    <el-icon>
                        <component :is="item.icon" />
                    </el-icon>
                    <span class="nav-label">{{ item.label }}</span>
                    <span v-if="item.badge && !isCollapsed" class="nav-badge">{{ item.badge }}</span>
                </div>
            </el-tooltip>

            <div class="nav-group-label" v-show="!isCollapsed">检测</div>
            <el-tooltip v-for="item in navigationMenus.detection" :key="item.key" :content="item.label" placement="right" :disabled="!isCollapsed">
                <div class="nav-item" :class="{ active: isActive(item.key) }" @click="navigateTo(item.key)">
                    <el-icon>
                        <component :is="item.icon" />
                    </el-icon>
                    <span class="nav-label">{{ item.label }}</span>
                    <span v-if="item.badge && !isCollapsed" class="nav-badge">{{ item.badge }}</span>
                </div>
            </el-tooltip>

            <!-- 记录模式分组 -->
            <div class="nav-group-label" v-show="!isCollapsed">记录</div>
            <el-tooltip v-for="item in navigationMenus.record" :key="item.key" :content="item.label" placement="right" :disabled="!isCollapsed">
                <div class="nav-item" :class="{ active: isActive(item.key) }" @click="navigateTo(item.key)">
                    <el-icon>
                        <component :is="item.icon" />
                    </el-icon>
                    <span class="nav-label">{{ item.label }}</span>
                </div>
            </el-tooltip>

            <div class="nav-group-label" v-show="!isCollapsed">管理</div>
            <el-tooltip v-for="item in [...navigationMenus.manage]" :key="item.key" :content="item.label" placement="right" :disabled="!isCollapsed">
                <div class="nav-item" :class="{ active: isActive(item.key) }" @click="navigateTo(item.key)">
                    <el-icon>
                        <component :is="item.icon" />
                    </el-icon>
                    <span class="nav-label">{{ item.label }}</span>
                </div>
            </el-tooltip>
        </nav>

        <!-- 收缩/展开切换按钮 -->
        <button class="collapse-toggle" @click="toggleCollapse" :title="isCollapsed ? '展开侧边栏' : '收缩侧边栏'">
            <SvgIcon :name="isCollapsed ? 'chevron-right' : 'chevron-left'" :size="18" />
        </button>
    </aside>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useNavigation } from '@/composables/useNavigation'
import SvgIcon from '@/components/icons/SvgIcons.vue'

const { navigateTo, isActive, navigationMenus } = useNavigation()

// 侧边栏收缩状态
const isCollapsed = ref(false)

// localStorage 存储键
const STORAGE_KEY = 'sidebar_collapsed'

// 切换收缩状态
const toggleCollapse = () => {
    isCollapsed.value = !isCollapsed.value
    // 保存状态到 localStorage
    localStorage.setItem(STORAGE_KEY, JSON.stringify(isCollapsed.value))
}

// 初始化时恢复状态
onMounted(() => {
    const savedState = localStorage.getItem(STORAGE_KEY)
    if (savedState !== null) {
        isCollapsed.value = JSON.parse(savedState)
    }
})
</script>

<style scoped>
/* ===== 侧边栏 ===== */
.sidebar {
    width: 220px;
    height: 100%;
    display: flex;
    flex-direction: column;
    background: var(--card-bg);
    border-right: 2px solid var(--primary);
    overflow: hidden;
    flex-shrink: 0;
    position: relative;
    /* ✅ 平滑收缩/展开动画 */
    transition: width 0.35s cubic-bezier(0.4, 0, 0.2, 1), 
                background 0.3s ease, 
                border-color 0.3s ease;
}

/* 收缩状态 */
.sidebar.collapsed {
    width: 64px;
}

.sidebar::after {
    content: '';
    position: absolute;
    right: 0;
    top: 10%;
    height: 80%;
    width: 1px;
    background: linear-gradient(180deg, transparent, color-mix(in srgb, var(--primary) 30%, transparent), transparent);
    opacity: 0.3;
    transition: opacity 0.3s ease;
}

.sidebar.collapsed::after {
    opacity: 0.15;
}

/* ===== 导航 ===== */
.sidebar-nav {
    flex: 1;
    padding: 12px 8px;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
}

.sidebar-nav::-webkit-scrollbar {
    width: 2px;
}

.sidebar-nav::-webkit-scrollbar-thumb {
    background: rgba(113, 57, 255, 0.3);
    border-radius: 2px;
}

.nav-group-label {
    font-size: 14px;
    font-weight: 100;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 1.8px;
    padding: 12px 12px 6px;
    opacity: 0.6;
    transition: opacity 0.2s ease;
}

/* 第一个分组标题减少顶部间距 */
.nav-group-first {
    padding-top: 4px;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s ease;
    color: var(--text);
    font-size: 19px;
    font-weight: 100;
    position: relative;
    margin-bottom: 2px;
    /* ✅ 收缩状态下居中对齐 */
    justify-content: flex-start;
}

.sidebar.collapsed .nav-item {
    justify-content: center;
    gap: 0;
}

.nav-item:hover {
    background: color-mix(in srgb, var(--primary) 8%, transparent);
    color: var(--text);
}

.nav-item.active {
    background: color-mix(in srgb, var(--primary) 14%, transparent);
    color: var(--text);
}

.nav-item.active::before {
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 3px;
    height: 50%;
    background: var(--gradient);
    border-radius: 0 2px 2px 0;
    transition: opacity 0.2s ease;
}

.sidebar.collapsed .nav-item.active::before {
    opacity: 0;
}

.nav-item .el-icon {
    font-size: 20px;
    flex-shrink: 0;
    color: var(--accent);
    opacity: 0.7;
    transition: all 0.2s ease;
}

.nav-item.active .el-icon {
    opacity: 1;
    color: var(--primary-light);
}

.nav-item:hover .el-icon {
    transform: scale(1.1);
}

/* 导航标签文字 */
.nav-label {
    transition: opacity 0.2s ease, transform 0.2s ease;
    white-space: nowrap;
}

.sidebar.collapsed .nav-label {
    opacity: 0;
    transform: translateX(-10px);
    position: absolute;
    pointer-events: none;
}

.nav-badge {
    margin-left: auto;
    font-size: 10px;
    font-weight: 100;
    padding: 2px 7px;
    border-radius: 20px;
    background: color-mix(in srgb, var(--primary) 22%, transparent);
    color: var(--accent);
    letter-spacing: 0.3px;
    transition: opacity 0.2s ease;
}

/* ===== 收缩/展开切换按钮 ===== */
.collapse-toggle {
    position: absolute;
    bottom: 12px;
    left: 50%;
    transform: translateX(-50%);
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: var(--card-bg);
    border: 1px solid var(--primary);
    color: var(--text);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
    z-index: 10;
}

.collapse-toggle:hover {
    background: color-mix(in srgb, var(--primary) 12%, transparent);
    transform: translateX(-50%) scale(1.08);
    box-shadow: 0 3px 12px rgba(139, 92, 246, 0.25);
}

.collapse-toggle:active {
    transform: translateX(-50%) scale(0.96);
}

.collapse-toggle .el-icon {
    font-size: 14px;
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 响应式适配 */
@media (max-width: 768px) {
    .sidebar {
        width: 180px;
    }
    
    .sidebar.collapsed {
        width: 56px;
    }
    
    .nav-item {
        padding: 8px 10px;
        font-size: 16px;
    }
    
    .nav-item .el-icon {
        font-size: 18px;
    }
    
    .collapse-toggle {
        width: 36px;
        height: 36px;
        bottom: 12px;
    }
}

@media (max-width: 480px) {
    .sidebar {
        width: 100%;
        position: fixed;
        left: 0;
        top: 64px;
        z-index: 90;
        transform: translateX(0);
        transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .sidebar.collapsed {
        transform: translateX(-100%);
        width: 180px;
    }
}
</style>
