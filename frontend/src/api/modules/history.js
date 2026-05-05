/**
 * 历史记录相关 API
 */
import http from '../http'

/**
 * 获取历史记录列表
 * @param {Object} params - 查询参数
 * @param {number} params.limit - 每页数量
 * @param {number} params.offset - 偏移量
 * @param {string} params.type - 检测类型筛选（可选）
 * @returns {Promise<{data: Array, total: number, type_counts: Object}>}
 */
export const getHistoryList = (params = {}) => {
    return http.get('/api/history', { params })
}

/**
 * 获取历史记录统计信息
 * @returns {Promise<{status: string, total_records: number, stats: Object}>}
 */
export const getHistoryStats = () => {
    return http.get('/api/history/stats')
}

/**
 * 保存检测结果到历史记录
 * @param {Object} record - 检测记录数据
 * @returns {Promise<Object>}
 */
export const saveHistoryRecord = (record) => {
    return http.post('/api/history/save', record)
}

/**
 * 导出单个历史记录
 * @param {number|string} id - 记录 ID
 * @returns {Promise<Blob>}
 */
export const exportHistoryRecord = (id) => {
    return http.get(`/api/history/${id}/export`, {
        responseType: 'blob'
    })
}

/**
 * 删除历史记录
 * @param {number|string} id - 记录 ID
 * @returns {Promise<Object>}
 */
export const deleteHistoryRecord = (id) => {
    return http.delete(`/api/history/${id}`)
}

/**
 * 批量删除历史记录
 * @param {Array<number|string>} ids - 记录 ID 数组
 * @returns {Promise<Object>}
 */
export const batchDeleteHistory = (ids) => {
    return http.post('/api/history/batch-delete', { ids })
}
