<template>
    <aside class="sidebar">
        <!-- 主导航 -->
        <nav class="sidebar-nav">
            <!-- 数据模式分组 -->
            <div class="nav-group-label nav-group-first">数据</div>
            <div class="nav-item" :class="{ active: isActive('analytics') }" @click="navigateTo('analytics')">
                <el-icon>
                    <DataAnalysis />
                </el-icon>
                <span>数据看板</span>
            </div>

            <div class="nav-group-label">检测模式</div>
            <div v-for="item in navigationMenus.detection" :key="item.key" class="nav-item"
                :class="{ active: isActive(item.key) }" @click="navigateTo(item.key)">
                <el-icon>
                    <component :is="item.icon" />
                </el-icon>
                <span>{{ item.label }}</span>
                <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
            </div>

            <!-- 记录模式分组 -->
            <div class="nav-group-label">记录</div>
            <div class="nav-item" :class="{ active: isActive('history') }" @click="navigateTo('history')">
                <el-icon>
                    <Clock />
                </el-icon>
                <span>历史档案</span>
            </div>

            <div class="nav-group-label">管理</div>
            <div v-for="item in [...navigationMenus.manage]" :key="item.key" class="nav-item"
                :class="{ active: isActive(item.key) }" @click="navigateTo(item.key)">
                <el-icon>
                    <component :is="item.icon" />
                </el-icon>
                <span>{{ item.label }}</span>
            </div>
        </nav>
    </aside>
</template>

<script setup>
import { useNavigation } from '@/composables/useNavigation'
import { DataAnalysis, Clock } from '@element-plus/icons-vue'

const { navigateTo, isActive, navigationMenus } = useNavigation()
</script>

<style scoped>
/* ===== 侧边栏 ===== */
.sidebar {
    width: 220px;
    height: 100%;
    display: flex;
    flex-direction: column;
    background: var(--card-bg);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-right: 1px solid var(--border);
    overflow: hidden;
    /* ✅ 统一过渡时间,与背景切换同步 */
    transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    flex-shrink: 0;
    position: relative;
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
    font-weight: 700;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 1.8px;
    padding: 12px 12px 6px;
    opacity: 0.6;
}

/* 第一个分组标题减少顶部间距 */
.nav-group-first {
    padding-top: 4px;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 16px;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s ease;
    color: var(--text);
    font-size: 20px;
    font-weight: 700;
    position: relative;
    margin-bottom: 2px;
}

.nav-item:hover {
    background: color-mix(in srgb, var(--primary) 8%, transparent);
    color: var(--text);
}

.nav-item.active {
    background: color-mix(in srgb, var(--primary) 14%, transparent);
    color: var(--text);
    font-weight: 600;
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
    box-shadow: 0 0 8px var(--primary);
}

.nav-item .el-icon {
    font-size: 20px;
    flex-shrink: 0;
    color: var(--accent);
    opacity: 0.7;
}

.nav-item.active .el-icon {
    opacity: 1;
    color: var(--primary-light);
}

.nav-badge {
    margin-left: auto;
    font-size: 10px;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 20px;
    background: color-mix(in srgb, var(--primary) 22%, transparent);
    color: var(--accent);
    letter-spacing: 0.3px;
}
</style>
