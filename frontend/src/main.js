import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import router from './router'
import App from './App.vue'
import './style.css'
import './styles/element-overwatch.css'
import { useThemeStore } from './stores/theme'
import { useDetectionStore } from './stores/detection'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

const app = createApp(App)
const pinia = createPinia()

// 注册 Element Plus 图标全局可用
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}

app.use(pinia)
app.use(router)
app.use(ElementPlus, {
    locale: zhCn, // 设置中文语言包
})

// 初始化主题（在任何组件挂载之前）
const themeStore = useThemeStore()
themeStore.init()

// 暴露 detection store 到全局（供 theme store 调用）
const detectionStore = useDetectionStore()
if (typeof window !== 'undefined') {
    window.__detectionStore__ = detectionStore
}

app.mount('#app')
