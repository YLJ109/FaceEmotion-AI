<template>
  <nav class="mobile-navbar" :class="{ 'mobile-navbar--expanded': expanded }">
    <div class="mobile-navbar__content">
      <button
        v-for="item in navItems"
        :key="item.key"
        class="mobile-navbar__item"
        :class="{ 'mobile-navbar__item--active': activeKey === item.key }"
        @click="handleNavClick(item)"
      >
        <span class="mobile-navbar__icon">
          <component :is="item.icon" />
        </span>
        <span v-if="expanded" class="mobile-navbar__label">{{ item.label }}</span>
      </button>
    </div>
    
    <div v-if="showCenterButton" class="mobile-navbar__center">
      <button class="mobile-navbar__center-btn" @click="$emit('center-click')">
        <component :is="centerIcon" />
      </button>
    </div>
  </nav>
</template>

<script setup>import { ref } from 'vue';
import { Home, Settings, History, BarChart3, Camera } from '@element-plus/icons-vue';
defineProps({
 activeKey: {
 type: String,
 default: 'home'
 },
 showCenterButton: {
 type: Boolean,
 default: true
 }
});
const emit = defineEmits(['navigate', 'center-click']);
const expanded = ref(false);
const navItems = [
 { key: 'home', label: '首页', icon: Home },
 { key: 'history', label: '历史', icon: History },
 { key: 'stats', label: '统计', icon: BarChart3 },
 { key: 'settings', label: '设置', icon: Settings }
];
const centerIcon = Camera;
const handleNavClick = (item) => {
 emit('navigate', item.key);
};
</script>

<style scoped>
.mobile-navbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: var(--bg-card);
  border-top: 1px solid var(--border-color);
  padding: var(--spacing-sm) 0;
  padding-bottom: calc(var(--spacing-sm) + env(safe-area-inset-bottom));
  transition: all 0.3s ease;
}

.mobile-navbar__content {
  display: flex;
  justify-content: space-around;
  align-items: center;
  position: relative;
}

.mobile-navbar__item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: var(--spacing-xs) var(--spacing-sm);
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: var(--radius-md);
}

.mobile-navbar__item:hover {
  background: var(--bg-hover);
}

.mobile-navbar__item--active {
  color: var(--color-primary);
}

.mobile-navbar__icon {
  font-size: 20px;
}

.mobile-navbar__label {
  font-size: var(--text-xs);
}

.mobile-navbar__center {
  position: absolute;
  left: 50%;
  top: -20px;
  transform: translateX(-50%);
}

.mobile-navbar__center-btn {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  border: 3px solid var(--bg-card);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  cursor: pointer;
  box-shadow: var(--shadow-lg);
  transition: all 0.2s ease;
  
  &:hover {
    transform: scale(1.05);
    box-shadow: var(--shadow-xl);
  }
  
  &:active {
    transform: scale(0.95);
  }
}

@media (min-width: 768px) {
  .mobile-navbar {
    display: none;
  }
}
</style>