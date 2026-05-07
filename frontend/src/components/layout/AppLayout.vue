<template>
  <div class="app-layout">
    <!-- 桌面端侧边栏 -->
    <aside class="app-layout__sidebar" :class="{ 'app-layout__sidebar--collapsed': sidebarCollapsed }">
      <div class="sidebar-header">
        <div class="sidebar-logo">
          <span class="logo-icon">🎭</span>
          <span v-if="!sidebarCollapsed" class="logo-text">情感AI</span>
        </div>
        <button 
          class="sidebar-toggle" 
          @click="sidebarCollapsed = !sidebarCollapsed"
          :title="sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'"
        >
          <component :is="sidebarCollapsed ? ChevronRight : ChevronLeft" />
        </button>
      </div>
      
      <nav class="sidebar-nav">
        <button
          v-for="item in navItems"
          :key="item.key"
          class="sidebar-nav-item"
          :class="{ 'sidebar-nav-item--active': activeNav === item.key }"
          @click="handleNavClick(item)"
        >
          <component :is="item.icon" />
          <span v-if="!sidebarCollapsed" class="nav-label">{{ item.label }}</span>
          <span v-if="!sidebarCollapsed && item.badge" class="nav-badge">{{ item.badge }}</span>
        </button>
      </nav>
      
      <div class="sidebar-footer">
        <button class="sidebar-nav-item" @click="handleSettings">
          <Settings />
          <span v-if="!sidebarCollapsed" class="nav-label">设置</span>
        </button>
      </div>
    </aside>
    
    <!-- 主内容区 -->
    <main class="app-layout__main">
      <!-- 顶部导航栏 -->
      <header class="app-layout__header">
        <div class="header-left">
          <button class="header-menu-btn" @click="sidebarCollapsed = !sidebarCollapsed">
            <Menu />
          </button>
          <h1 class="header-title">{{ pageTitle }}</h1>
        </div>
        
        <div class="header-center">
          <slot name="header-center" />
        </div>
        
        <div class="header-right">
          <EmotionAnalyzer />
          <slot name="header-right" />
        </div>
      </header>
      
      <!-- 内容区域 -->
      <div class="app-layout__content">
        <slot />
      </div>
    </main>
    
    <!-- 移动端底部导航 -->
    <MobileNavbar 
      :active-key="activeNav" 
      @navigate="handleMobileNav"
      @center-click="handleMobileCenterClick"
    />
  </div>
</template>

<script setup>import { ref, computed } from 'vue';
import { Home, Search, History, BarChart3, Settings, Menu, ChevronLeft, ChevronRight } from '@element-plus/icons-vue';
import { MobileNavbar } from '@/components/ui';
import EmotionAnalyzer from '@/components/header/EmotionAnalyzer.vue';
defineProps({
 pageTitle: {
 type: String,
 default: '情感AI检测'
 },
 activeNav: {
 type: String,
 default: 'home'
 }
});
const emit = defineEmits(['navigate', 'settings']);
const sidebarCollapsed = ref(false);
const navItems = [
 { key: 'home', label: '实时检测', icon: Home },
 { key: 'history', label: '历史记录', icon: History },
 { key: 'analytics', label: '数据分析', icon: BarChart3 },
 { key: 'search', label: '搜索', icon: Search }
];
const handleNavClick = (item) => {
 emit('navigate', item.key);
};
const handleSettings = () => {
 emit('settings');
};
const handleMobileNav = (key) => {
 emit('navigate', key);
};
const handleMobileCenterClick = () => {
 emit('navigate', 'home');
};
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  background: var(--bg-primary);
}

/* 侧边栏 */
.app-layout__sidebar {
  width: 200px;
  background: var(--bg-card);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  flex-shrink: 0;
}

.app-layout__sidebar--collapsed {
  width: 64px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--text-primary);
}

.sidebar-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  background: var(--bg-hover);
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
  }
}

.sidebar-nav {
  flex: 1;
  padding: var(--spacing-sm);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sidebar-nav-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  
  &:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }
  
  &--active {
    background: rgba(139, 92, 246, 0.1);
    color: var(--color-primary);
  }
}

.nav-label {
  flex: 1;
  font-size: var(--text-sm);
}

.nav-badge {
  background: var(--color-error);
  color: white;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: var(--radius-full);
}

.sidebar-footer {
  padding: var(--spacing-sm);
  border-top: 1px solid var(--border-color);
}

/* 主内容区 */
.app-layout__main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 顶部导航栏 */
.app-layout__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.header-menu-btn {
  display: none;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  background: var(--bg-hover);
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  
  &:hover {
    color: var(--text-primary);
  }
}

.header-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--text-primary);
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

/* 内容区域 */
.app-layout__content {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-md);
}

/* 响应式适配 */
@media (max-width: 768px) {
  .app-layout__sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 200;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .app-layout__sidebar--collapsed {
    transform: translateX(0);
  }
  
  .app-layout__main {
    width: 100%;
  }
  
  .header-menu-btn {
    display: flex;
  }
  
  .app-layout__content {
    padding-bottom: calc(var(--spacing-xl) + 60px);
  }
}

@media (max-width: 640px) {
  .app-layout__header {
    padding: var(--spacing-sm);
  }
  
  .header-center {
    display: none;
  }
  
  .header-title {
    font-size: var(--text-base);
  }
}
</style>