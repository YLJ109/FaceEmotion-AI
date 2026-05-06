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
const HistoryViewer = () => import('@/components/history/HistoryViewer.vue')
const ThemePage = () => import('@/components/pages/ThemePage.vue')
const SettingsPage = () => import('@/components/pages/SettingsPage.vue')
const FeedbackHistory = () => import('@/components/feedback/FeedbackHistory.vue') // ✅ 新增: 反馈历史页面
const AdaptiveLearningMonitor = () => import('@/components/monitor/AdaptiveLearningMonitor.vue') // ✅ 新增: AI学习监控

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
    },
    {
        path: '/feedback-history',
        name: 'FeedbackHistory',
        component: FeedbackHistory,
        meta: {
            title: '反馈历史',
            icon: 'DocumentChecked',
            group: 'record'
        }
    },
    {
        path: '/adaptive-learning',
        name: 'AdaptiveLearning',
        component: AdaptiveLearningMonitor,
        meta: {
            title: 'AI学习监控',
            icon: 'Cpu',
            group: 'data'
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

    next()
})

export default router
