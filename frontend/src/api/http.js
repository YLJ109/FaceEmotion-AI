/**
 * Axios HTTP 客户端配置
 * 统一管理请求拦截、响应拦截、错误处理、重试机制
 */
import axios from 'axios'
import { API_BASE_URL } from './config'
import { ElMessage } from 'element-plus'
import logger from '@/utils/logger'

const MAX_RETRIES = 3
const RETRY_DELAY_BASE = 1000

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
}

async function retryRequest(config, retryCount = 0) {
    try {
        return await axios(config)
    } catch (error) {
        const shouldRetry = (
            retryCount < MAX_RETRIES &&
            (error.code === 'ECONNABORTED' ||
             error.code === 'ERR_NETWORK' ||
             error.response?.status >= 500 ||
             error.response?.status === 429)
        )

        if (shouldRetry) {
            const delay = RETRY_DELAY_BASE * Math.pow(2, retryCount)
            logger.warn(`请求失败，${delay}ms后重试 (${retryCount + 1}/${MAX_RETRIES}): ${config.url}`)
            await sleep(delay)
            return retryRequest(config, retryCount + 1)
        }
        throw error
    }
}

// 创建 Axios 实例
const http = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000
})

// ==================== 请求拦截器 ====================
http.interceptors.request.use(
    config => {
        // 可以在这里添加 token、请求日志等
        // const token = localStorage.getItem('token')
        // if (token) {
        //   config.headers.Authorization = `Bearer ${token}`
        // }

        // 使用统一日志工具（可通过 config.log = false 禁用）
        if (config.log !== false) {
            logger.apiRequest(config.method, config.url)
        }

        return config
    },
    error => {
        logger.error('[Request Error]', error)
        return Promise.reject(error)
    }
)

// ==================== 响应拦截器 ====================
http.interceptors.response.use(
    response => {
        // 使用统一日志工具（可通过 config.log = false 禁用）
        if (response.config.log !== false) {
            logger.apiResponse(response.status, response.config.url)
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

        logger.error(`[API Error] ${message}`, error)

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
        case 429:
            return data.detail || '请求过于频繁，请稍后重试'
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

http.retryRequest = retryRequest

export default http
