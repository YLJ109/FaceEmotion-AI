/**
 * Axios HTTP 客户端配置
 * 统一管理请求拦截、响应拦截、错误处理
 */
import axios from 'axios'
import { API_BASE_URL } from './config'
import { ElMessage } from 'element-plus'

// 创建 Axios 实例
const http = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000, // 30秒超时
    headers: {
        'Content-Type': 'application/json'
    }
})

// ==================== 请求拦截器 ====================
http.interceptors.request.use(
    config => {
        // 可以在这里添加 token、请求日志等
        // const token = localStorage.getItem('token')
        // if (token) {
        //   config.headers.Authorization = `Bearer ${token}`
        // }

        // 开发环境打印请求信息
        if (import.meta.env.DEV) {
            console.log(`📤 [API Request] ${config.method?.toUpperCase()} ${config.url}`)
        }

        return config
    },
    error => {
        console.error('❌ [Request Error]', error)
        return Promise.reject(error)
    }
)

// ==================== 响应拦截器 ====================
http.interceptors.response.use(
    response => {
        // 开发环境打印响应信息
        if (import.meta.env.DEV) {
            console.log(`📥 [API Response] ${response.status} ${response.config.url}`)
        }

        // 直接返回 data，简化调用
        return response.data
    },
    error => {
        // 统一错误处理
        const message = getErrorMessage(error)

        // 显示错误提示（可配置是否显示）
        if (error.config?.showError !== false) {
            ElMessage.error(message)
        }

        console.error(`❌ [API Error] ${message}`, error)

        return Promise.reject(error)
    }
)

/**
 * 获取友好的错误提示信息
 * @param {Error} error - Axios 错误对象
 * @returns {string}
 */
function getErrorMessage(error) {
    if (!error.response) {
        // 网络错误或超时
        if (error.code === 'ECONNABORTED') {
            return '请求超时，请检查网络连接'
        }
        return '网络连接失败，请检查后端服务是否启动'
    }

    const { status, data } = error.response

    switch (status) {
        case 400:
            return data.detail || '请求参数错误'
        case 401:
            return '未授权，请重新登录'
        case 403:
            return '禁止访问'
        case 404:
            return '请求的资源不存在'
        case 500:
            return '服务器内部错误'
        case 502:
            return '网关错误，后端服务可能未启动'
        case 503:
            return '服务不可用'
        default:
            return data.detail || `请求失败 (${status})`
    }
}

export default http
