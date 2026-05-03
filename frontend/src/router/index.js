/**
 * Vue Router 配置
 * 统一管理应用路由和页面导航
 */
import { createRouter, createWebHistory } from 'vue-router'

// 懒加载组件 - Vue Router 自动处理异步加载
const RealtimeDetector = () => import('@/components/detection/RealtimeDetector.vue')
const ImageDetector = () => import('@/components/detection/ImageDetector.vue')
const BatchDetector = () => import('@/components/detection/BatchDetector.vue')
const VideoDetector = () => import('@/components/detection/VideoDetector.vue')
const AnalyticsDashboard = () => import('@/components/analytics/AnalyticsDashboard.vue')
const HistoryViewer = () => import('@/components/HistoryViewer.vue')

// 主题页面组件 (内联在 App.vue 中,使用空组件占位)
const ThemePage = {
    template: '<div></div>'
}

const SettingsPage = {
    template: '<div></div>'
}

const routes = [
    {
        path: '/',
        redirect: '/realtime'
    },
    {
        path: '/realtime',
        name: 'Realtime',
        component: RealtimeDetector,
        meta: {
            title: '实时检测',
            icon: 'VideoCamera',
            group: 'detection'
        }
    },
    {
        path: '/image',
        name: 'Image',
        component: ImageDetector,
        meta: {
            title: '图片检测',
            icon: 'Picture',
            group: 'detection'
        }
    },
    {
        path: '/batch',
        name: 'Batch',
        component: BatchDetector,
        meta: {
            title: '批量检测',
            icon: 'Files',
            badge: '3并发',
            group: 'detection'
        }
    },
    {
        path: '/video',
        name: 'Video',
        component: VideoDetector,
        meta: {
            title: '视频检测',
            icon: 'VideoPlay',
            badge: 'Beta',
            group: 'detection'
        }
    },
    {
        path: '/analytics',
        name: 'Analytics',
        component: AnalyticsDashboard,
        meta: {
            title: '数据看板',
            icon: 'DataAnalysis',
            group: 'data'
        }
    },
    {
        path: '/history',
        name: 'History',
        component: HistoryViewer,
        meta: {
            title: '历史档案',
            icon: 'Clock',
            group: 'record'
        }
    },
    {
        path: '/theme',
        name: 'Theme',
        component: ThemePage,
        meta: {
            title: '主题切换',
            icon: 'Brush',
            group: 'manage'
        }
    },
    {
        path: '/settings',
        name: 'Settings',
        component: SettingsPage,
        meta: {
            title: '系统设置',
            icon: 'Setting',
            group: 'manage'
        }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// 路由守卫 - 上报功能使用统计
router.beforeEach((to, from, next) => {
    // 更新页面标题
    document.title = `${to.meta.title || 'AI情感检测'} - AI情感检测系统`

    // 上报功能使用 (静默失败)
    if (to.name && to.name !== from.name) {
        logFeatureUsage(to.name).catch(() => { })
    }

    next()
})

/**
 * 上报功能使用统计
 */
async function logFeatureUsage(featureName) {
    try {
        await fetch('http://localhost:8000/api/analytics/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ feature: featureName }),
        })
    } catch (e) {
        // 静默失败,不影响用户体验
    }
}

export default router
