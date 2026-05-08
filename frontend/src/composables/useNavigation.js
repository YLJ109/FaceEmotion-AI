/**
 * 导航组合式函数
 * 封装侧边栏导航逻辑和菜单配置
 */
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

/**
 * 导航菜单配置
 */
const NAVIGATION_CONFIG = {
    // 数据模式分组
    data: [
        { key: 'analytics', label: '数据看板', enLabel: 'Analytics', icon: 'DataAnalysis', path: '/analytics' },
        { key: 'adaptive-learning', label: 'AI学习监控', enLabel: 'AI Learning', icon: 'Cpu', path: '/adaptive-learning' }
    ],

    // 检测模式分组
    detection: [
        { key: 'realtime', label: '实时检测', enLabel: 'Real-time', icon: 'VideoCamera', path: '/realtime' },
        { key: 'image', label: '图片检测', enLabel: 'Image', icon: 'Picture', path: '/image' },
        { key: 'batch', label: '图片批量检测', enLabel: 'Batch', icon: 'Files', path: '/batch', badge: '3并发' },
        { key: 'video', label: '视频检测', enLabel: 'Video', icon: 'VideoPlay', path: '/video', badge: 'Beta' },
        { key: 'batch-video', label: '批量视频检测', enLabel: 'Batch Video', icon: 'Film', path: '/batch-video', badge: '3并发' }
    ],

    // 记录模式分组
    record: [
        { key: 'history', label: '历史档案', enLabel: 'History', icon: 'Clock', path: '/history' },
        { key: 'feedback-history', label: '反馈历史', enLabel: 'Feedback', icon: 'DocumentChecked', path: '/feedback-history' }
    ],

    // 管理分组
    manage: [
        { key: 'theme', label: '主题切换', enLabel: 'Theme', icon: 'Brush', path: '/theme' },
        { key: 'settings', label: '系统设置', enLabel: 'Settings', icon: 'Setting', path: '/settings' }
    ]
}

/**
 * 使用导航
 * @returns {Object} 导航相关的响应式数据和方法
 */
export function useNavigation() {
    const router = useRouter()
    const route = useRoute()

    /**
     * 当前激活的菜单项 (基于路由)
     */
    const activeMenu = computed(() => {
        return route.name?.toLowerCase() || 'realtime'
    })

    /**
     * 导航到指定页面
     * @param {string} menuKey - 菜单键名
     */
    const navigateTo = (menuKey) => {
        const path = getPathByMenuKey(menuKey)
        if (path) {
            router.push(path)
        }
    }

    /**
     * 根据菜单键名获取路由路径
     * @param {string} menuKey - 菜单键名
     * @returns {string|null} 路由路径
     */
    const getPathByMenuKey = (menuKey) => {
        for (const group of Object.values(NAVIGATION_CONFIG)) {
            const item = group.find(i => i.key === menuKey)
            if (item) return item.path
        }
        return null
    }

    /**
     * 检查菜单项是否激活
     * @param {string} menuKey - 菜单键名
     * @returns {boolean} 是否激活
     */
    const isActive = (menuKey) => {
        return activeMenu.value === menuKey
    }

    /**
     * 获取所有导航菜单 (按分组)
     */
    const navigationMenus = computed(() => {
        return NAVIGATION_CONFIG
    })

    /**
     * 获取主题描述
     * @param {string} themeKey - 主题键名
     * @returns {string} 主题描述
     */
    const getThemeDesc = (themeKey) => {
        const descriptions = {
            sunny: '阳光活力橙',
            rainy: '雨天忧郁蓝',
            fire: '火焰激情红',
            galaxy: '银河神秘紫',
            mist: '迷雾朦胧灰',
            forest: '森林自然绿',
            zen: '禅意平和白',
            overwatch: '守望先锋暗紫',
            cyberpunk: '赛博朋克霓虹',
            minimal: '极简纯净黑白'
        }
        return descriptions[themeKey] || ''
    }

    /**
     * 获取当前激活菜单的标签
     * @returns {string} 当前激活菜单项的标签
     */
    const getActiveMenuLabel = computed(() => {
        for (const group of Object.values(NAVIGATION_CONFIG)) {
            const item = group.find(i => i.key === activeMenu.value)
            if (item) return item.label
        }
        return ''
    })

    /**
     * 获取当前激活菜单的英文标签
     * @returns {string} 当前激活菜单项的英文标签
     */
    const getActiveMenuEnLabel = computed(() => {
        for (const group of Object.values(NAVIGATION_CONFIG)) {
            const item = group.find(i => i.key === activeMenu.value)
            if (item) return item.enLabel
        }
        return ''
    })

    return {
        activeMenu,
        navigateTo,
        isActive,
        navigationMenus,
        getThemeDesc,
        getActiveMenuLabel,
        getActiveMenuEnLabel
    }
}
