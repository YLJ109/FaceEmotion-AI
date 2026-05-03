<template>
    <div class="history-viewer">
        <!-- 筛选器 -->
        <div class="filter-cards">
            <div class="filter-card" :class="{ active: filterType === 'all' }" @click="setFilter('all')">
                <div class="filter-card-inner">
                    <div class="filter-icon-wrap"
                        style="background: linear-gradient(135deg, rgba(113, 57, 255, 0.2), rgba(155, 89, 182, 0.2));">
                        <el-icon :size="20" color="#7139FF">
                            <DataAnalysis />
                        </el-icon>
                    </div>
                    <div class="filter-info">
                        <span class="filter-label">全部</span>
                        <span class="filter-count">{{ total }} 条</span>
                    </div>
                </div>
            </div>

            <div class="filter-card" :class="{ active: filterType === 'realtime' }" @click="setFilter('realtime')">
                <div class="filter-card-inner">
                    <div class="filter-icon-wrap"
                        style="background: linear-gradient(135deg, rgba(103, 194, 58, 0.2), rgba(103, 194, 58, 0.1));">
                        <el-icon :size="20" color="#67C23A">
                            <VideoCamera />
                        </el-icon>
                    </div>
                    <div class="filter-info">
                        <span class="filter-label">实时检测</span>
                        <span class="filter-count">{{ typeCounts.realtime }} 条</span>
                    </div>
                </div>
            </div>

            <div class="filter-card" :class="{ active: filterType === 'image' }" @click="setFilter('image')">
                <div class="filter-card-inner">
                    <div class="filter-icon-wrap"
                        style="background: linear-gradient(135deg, rgba(230, 162, 60, 0.2), rgba(230, 162, 60, 0.1));">
                        <el-icon :size="20" color="#E6A23C">
                            <Picture />
                        </el-icon>
                    </div>
                    <div class="filter-info">
                        <span class="filter-label">图片检测</span>
                        <span class="filter-count">{{ typeCounts.image }} 条</span>
                    </div>
                </div>
            </div>

            <div class="filter-card" :class="{ active: filterType === 'batch' }" @click="setFilter('batch')">
                <div class="filter-card-inner">
                    <div class="filter-icon-wrap"
                        style="background: linear-gradient(135deg, rgba(64, 158, 255, 0.2), rgba(64, 158, 255, 0.1));">
                        <el-icon :size="20" color="#409EFF">
                            <Files />
                        </el-icon>
                    </div>
                    <div class="filter-info">
                        <span class="filter-label">批量检测</span>
                        <span class="filter-count">{{ typeCounts.batch }} 条</span>
                    </div>
                </div>
            </div>

            <div class="filter-card" :class="{ active: filterType === 'video' }" @click="setFilter('video')">
                <div class="filter-card-inner">
                    <div class="filter-icon-wrap"
                        style="background: linear-gradient(135deg, rgba(245, 108, 108, 0.2), rgba(245, 108, 108, 0.1));">
                        <el-icon :size="20" color="#F56C6C">
                            <Film />
                        </el-icon>
                    </div>
                    <div class="filter-info">
                        <span class="filter-label">视频检测</span>
                        <span class="filter-count">{{ typeCounts.video }} 条</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- 空状态 -->
        <div v-if="!loading && historyList.length === 0" class="empty-state">
            <div class="empty-icon">📋</div>
            <p>暂无历史记录<br />进行检测后将自动保存</p>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
            <el-icon class="is-loading">
                <Loading />
            </el-icon>
            <p>加载中...</p>
        </div>

        <!-- 历史记录表格 -->
        <div v-if="!loading && historyList.length > 0" class="history-table-container">
            <el-table :data="historyList" style="width: 100%" :header-cell-style="headerCellStyle"
                :cell-style="cellStyle" :row-class-name="tableRowClassName" @row-click="handleRowClick"
                highlight-current-row>
                <!-- 缩略图/情绪图标列 -->
                <el-table-column label="预览" width="100" align="center">
                    <template #default="{ row }">
                        <div class="table-thumbnail">
                            <img v-if="row.thumbnail" :src="row.thumbnail" alt="缩略图" />
                            <div v-else class="thumbnail-placeholder-small">
                                <span class="placeholder-emoji-small">{{ getEmotionEmoji(row.dominant_emotion) }}</span>
                            </div>
                        </div>
                    </template>
                </el-table-column>

                <!-- 检测类型列 -->
                <el-table-column label="检测类型" width="120" align="center">
                    <template #default="{ row }">
                        <span class="type-badge">{{ getTypeLabel(row.detection_type) }}</span>
                    </template>
                </el-table-column>

                <!-- 主导情绪列 -->
                <el-table-column label="主导情绪" min-width="150" align="center">
                    <template #default="{ row }">
                        <span class="emotion-badge-table"
                            :style="{ background: getEmotionColor(row.dominant_emotion) }">
                            {{ getEmotionEmoji(row.dominant_emotion) }}
                            {{ getEmotionName(row.dominant_emotion) }}
                        </span>
                    </template>
                </el-table-column>

                <!-- 置信度列 -->
                <el-table-column label="置信度" width="120" align="center">
                    <template #default="{ row }">
                        <span class="confidence-table">{{ (row.confidence * 100).toFixed(1) }}%</span>
                    </template>
                </el-table-column>

                <!-- 人脸数量列 -->
                <el-table-column label="人脸数量" width="100" align="center">
                    <template #default="{ row }">
                        <span class="face-count-table">{{ row.detected_faces?.length || 0 }} 张</span>
                    </template>
                </el-table-column>

                <!-- 来源列 -->
                <el-table-column label="来源" min-width="120" show-overflow-tooltip>
                    <template #default="{ row }">
                        <span class="source-text">{{ row.source || '未知来源' }}</span>
                    </template>
                </el-table-column>

                <!-- 检测时间列 -->
                <el-table-column label="检测时间" width="180" align="center">
                    <template #default="{ row }">
                        <span class="time-text">{{ formatTime(row.created_at) }}</span>
                    </template>
                </el-table-column>

                <!-- 操作列 -->
                <el-table-column label="操作" width="100" align="center" fixed="right">
                    <template #default="{ row }">
                        <div class="action-buttons">
                            <el-button size="small" type="primary" link @click.stop="showDetail(row)">
                                <el-icon>
                                    <View />
                                </el-icon>
                                详情
                            </el-button>
                        </div>
                    </template>
                </el-table-column>
            </el-table>
        </div>

        <!-- 分页 -->
        <div v-if="historyList.length > 0" class="pagination-container">
            <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total"
                :page-sizes="[12, 24, 48]" layout="total, sizes, prev, pager, next" @size-change="handleSizeChange"
                @current-change="handlePageChange" />
        </div>

        <!-- 详情对话框 -->
        <el-dialog v-model="dialogVisible" title="检测详情" width="70%" :close-on-click-modal="false">
            <div v-if="selectedItem" class="detail-content">
                <div class="detail-left">
                    <div class="image-preview">
                        <img v-if="selectedItem.thumbnail" :src="selectedItem.thumbnail" alt="检测图片" />
                        <div v-else class="preview-placeholder">
                            <span class="large-emoji">{{ getEmotionEmoji(selectedItem.dominant_emotion || 'neutral')
                                }}</span>
                            <p>无预览图片</p>
                        </div>
                    </div>
                </div>
                <div class="detail-right">
                    <div class="detail-section">
                        <h4>基本信息</h4>
                        <el-descriptions :column="1" border>
                            <el-descriptions-item label="检测类型">{{ getTypeLabel(selectedItem.detection_type)
                                }}</el-descriptions-item>
                            <el-descriptions-item label="来源">{{ selectedItem.source || '未知' }}</el-descriptions-item>
                            <el-descriptions-item label="检测时间">{{ formatTime(selectedItem.created_at)
                                }}</el-descriptions-item>
                            <el-descriptions-item label="主导情绪">
                                <span class="emotion-tag"
                                    :style="{ background: getEmotionColor(selectedItem.dominant_emotion) }">
                                    {{ getEmotionEmoji(selectedItem.dominant_emotion) }}
                                    {{ getEmotionName(selectedItem.dominant_emotion) }}
                                </span>
                            </el-descriptions-item>
                            <el-descriptions-item label="置信度">{{ ((selectedItem.confidence || 0) * 100).toFixed(1)
                                }}%</el-descriptions-item>
                            <el-descriptions-item label="人脸数量">{{ selectedItem.detected_faces?.length || 0
                                }}</el-descriptions-item>
                        </el-descriptions>
                    </div>

                    <div v-if="selectedItem.detected_faces?.length > 0" class="detail-section">
                        <h4>检测到的人脸 ({{ selectedItem.detected_faces.length }})</h4>
                        <div class="faces-list">
                            <div v-for="(face, index) in selectedItem.detected_faces" :key="index"
                                class="face-detail-item">
                                <div class="face-header">
                                    <span class="face-index">人脸 {{ index + 1 }}</span>
                                    <span class="face-confidence">{{ ((face.confidence || 0) * 100).toFixed(1)
                                        }}%</span>
                                </div>
                                <el-progress
                                    :percentage="clampPercentage(parseFloat(((face.confidence || 0) * 100).toFixed(1)))"
                                    :color="getEmotionColor(face.emotion)" :stroke-width="8" />
                                <div class="face-bbox">
                                    <span>BBox: [{{ face.bbox?.join(', ') }}]</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <template #footer>
                <el-button type="primary" @click="dialogVisible = false">关闭</el-button>
                <el-button type="primary" @click="exportSingleRecord(selectedItem)">导出 JSON</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Clock, Loading, Picture, View, Download, DataAnalysis, VideoCamera, Files, Film } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getEmotionName, getEmotionColor, getEmotionEmoji } from '@/utils/emotion'
import { API } from '@/api/config'

const loading = ref(false)
const historyList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)
const dialogVisible = ref(false)
const selectedItem = ref(null)
const filterType = ref('all') // 筛选类型
const typeCounts = ref({
    realtime: 0,
    image: 0,
    batch: 0,
    video: 0
})

// 获取历史记录
const fetchHistory = async () => {
    loading.value = true
    try {
        const offset = (currentPage.value - 1) * pageSize.value
        let url = `${API.history}?limit=${pageSize.value}&offset=${offset}`

        // 添加筛选参数
        if (filterType.value !== 'all') {
            url += `&type=${filterType.value}`
        }

        const response = await fetch(url)
        if (!response.ok) throw new Error('获取历史记录失败')
        const data = await response.json()
        historyList.value = data.data || []
        total.value = data.total || 0

        // 更新各类型数量
        if (data.type_counts) {
            typeCounts.value = {
                realtime: data.type_counts.realtime || 0,
                image: data.type_counts.image || 0,
                batch: data.type_counts.batch || 0,
                video: data.type_counts.video || 0
            }
        }
    } catch (error) {
        console.error('获取历史记录错误:', error)
        ElMessage.error('获取历史记录失败')
    } finally {
        loading.value = false
    }
}

// 设置筛选类型
const setFilter = (type) => {
    filterType.value = type
    currentPage.value = 1 // 重置到第一页
    fetchHistory()
}

// 显示详情
const showDetail = (item) => {
    selectedItem.value = item
    dialogVisible.value = true
}

// 格式化时间
const formatTime = (timeStr) => {
    if (!timeStr) return '未知'
    const date = new Date(timeStr)
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    })
}

// 获取检测类型标签
const getTypeLabel = (type) => {
    const labels = {
        'image': '单张图片',
        'batch': '批量检测',
        'video': '视频检测',
        'realtime': '实时检测'
    }
    return labels[type] || type
}

// 限制百分比在 0-100 范围内
const clampPercentage = (value) => {
    const num = parseFloat(value)
    if (isNaN(num)) return 0
    return Math.max(0, Math.min(100, num))
}

// 导出单个记录
const exportSingleRecord = (item) => {
    if (!item) return
    const data = JSON.stringify(item, null, 2)
    const blob = new Blob([data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `history_${item.id}_${Date.now()}.json`
    link.click()
    URL.revokeObjectURL(url)
    ElMessage.success('✅ 已导出')
}

// 分页处理
const handlePageChange = (page) => {
    currentPage.value = page
    fetchHistory()
}

const handleSizeChange = (size) => {
    pageSize.value = size
    currentPage.value = 1
    fetchHistory()
}

// 处理行点击
const handleRowClick = (row) => {
    showDetail(row)
}

// 表格样式配置
const headerCellStyle = {
    background: 'transparent',
    color: '#ffffff',
    fontWeight: '600',
    fontSize: '13px',
    padding: '12px 0',
    borderBottom: '2px solid rgba(113, 57, 255, 0.2)',
    letterSpacing: '0.5px'
}

const cellStyle = {
    background: 'transparent',
    color: '#ffffff',
    borderBottom: '1px solid rgba(156, 78, 255, 0.1)',
    padding: '10px 0',
    fontSize: '14px'
}

const tableRowClassName = ({ rowIndex }) => {
    return rowIndex % 2 === 0 ? 'table-row-even' : 'table-row-odd'
}

onMounted(() => {
    fetchHistory()
})
</script>

<style scoped>
.history-viewer {
    height: 100%;
    overflow: hidden;
    /* padding: 20px; */
    animation: fadeIn 0.3s ease;
    display: flex;
    flex-direction: column;
}

.history-header {
    margin-bottom: 24px;
    text-align: center;
}

.history-header h2 {
    font-size: 22px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    color: #ffffff;
    margin: 0 0 8px;
}

.history-header p {
    font-size: 14px;
    color: var(--text-secondary);
    opacity: 0.7;
}

/* 筛选器卡片 */
.filter-cards {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-bottom: 20px;
    margin-top: 2px;
    flex-shrink: 0;
}

.filter-card {
    background: var(--card-bg);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    transition: all 0.3s ease;
    overflow: hidden;
    cursor: pointer;
}

.filter-card:hover {
    border-color: color-mix(in srgb, var(--border) 60%, var(--primary));
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
}

.filter-card.active {
    border-color: var(--primary);
    box-shadow: 0 0 20px rgba(113, 57, 255, 0.3);
}

.filter-card-inner {
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.filter-icon-wrap {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.filter-info {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
}

.filter-label {
    font-size: 14px;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 2px;
}

.filter-count {
    font-size: 18px;
    font-weight: 700;
    color: var(--primary-light);
    font-family: 'Consolas', 'Monaco', monospace;
}

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    gap: 16px;
    color: var(--text-secondary);
}

.empty-icon {
    font-size: 64px;
    opacity: 0.4;
}

.empty-state p {
    font-size: 15px;
    text-align: center;
    line-height: 1.8;
}

.loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 300px;
    gap: 12px;
    color: var(--text-secondary);
}

.loading-state .el-icon {
    font-size: 32px;
}

/* 表格容器 */
.history-table-container {
    flex: 1;
    overflow: hidden;
    border-radius: var(--radius-md);
    background: var(--card-bg);
    backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    box-shadow: var(--shadow-md);
}

/* 表格缩略图 */
.table-thumbnail {
    width: 50px;
    height: 38px;
    border-radius: 8px;
    overflow: hidden;
    margin: 0 auto;
    background: linear-gradient(135deg,
            color-mix(in srgb, var(--primary) 15%, transparent),
            color-mix(in srgb, var(--accent) 15%, transparent));
    border: 1px solid rgba(113, 57, 255, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
}

.table-thumbnail:hover {
    transform: scale(1.05);
    border-color: rgba(113, 57, 255, 0.4);
    box-shadow: 0 2px 8px rgba(113, 57, 255, 0.2);
}

.table-thumbnail img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.thumbnail-placeholder-small {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.placeholder-emoji-small {
    font-size: 20px;
}

/* 类型徽章 */
.type-badge {
    padding: 4px 10px;
    background: rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    color: var(--text);
    display: inline-block;
    white-space: nowrap;
    transition: all 0.2s ease;
}

.type-badge:hover {
    background: rgba(0, 0, 0, 0.6);
    border-color: rgba(255, 255, 255, 0.2);
}

/* 情绪徽章 */
.emotion-badge-table {
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    color: white;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.15);
    transition: all 0.2s ease;
}

.emotion-badge-table:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.35);
}

/* 置信度 */
.confidence-table {
    font-size: 14px;
    font-weight: 700;
    color: var(--highlight);
    font-family: 'Consolas', 'Monaco', monospace;
    letter-spacing: 0.5px;
}

/* 人脸数量 */
.face-count-table {
    font-size: 13px;
    font-weight: 600;
    color: var(--primary-light);
}

/* 来源文本 */
.source-text {
    font-size: 13px;
    color: var(--text-secondary);
    opacity: 0.8;
    max-width: 100%;
    display: inline-block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* 时间文本 */
.time-text {
    font-size: 13px;
    color: var(--text-secondary);
    font-family: 'Consolas', 'Monaco', monospace;
    opacity: 0.7;
    letter-spacing: 0.3px;
}

/* 操作按钮 */
.action-buttons {
    display: flex;
    gap: 8px;
    justify-content: center;
    align-items: center;
}

/* 操作按钮样式优化 */
.action-buttons .el-button {
    padding: 4px 10px;
    font-size: 12px;
    border-radius: 6px;
    transition: all 0.2s ease;
}

.action-buttons .el-button--primary.is-link {
    background: rgba(113, 57, 255, 0.15);
    color: var(--primary-light);
    border: 1px solid rgba(113, 57, 255, 0.3);
}

.action-buttons .el-button--primary.is-link:hover {
    background: rgba(113, 57, 255, 0.25);
    border-color: var(--primary-light);
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(113, 57, 255, 0.3);
}

.action-buttons .el-button--success.is-link {
    background: rgba(103, 194, 58, 0.15);
    color: var(--success);
    border: 1px solid rgba(103, 194, 58, 0.3);
}

.action-buttons .el-button--success.is-link:hover {
    background: rgba(103, 194, 58, 0.25);
    border-color: var(--success);
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(103, 194, 58, 0.3);
}

/* 表格行样式 */
:deep(.el-table__row) {
    cursor: pointer;
    transition: all 0.2s ease;
}

:deep(.el-table__row:hover) {
    background: rgba(113, 57, 255, 0.06) !important;
}

:deep(.table-row-even) {
    background: rgba(13, 6, 27, 0.3);
}

:deep(.table-row-odd) {
    background: rgba(13, 6, 27, 0.5);
}

:deep(.el-table__body tr.current-row > td) {
    background: rgba(113, 57, 255, 0.1) !important;
}

/* Element Plus 表格深度样式定制 */
:deep(.el-table) {
    background: transparent;
    --el-table-border-color: rgba(156, 78, 255, 0.1);
    --el-table-header-bg-color: transparent;
    --el-table-tr-bg-color: transparent;
    --el-table-expanded-cell-bg-color: transparent;
}

:deep(.el-table th.el-table__cell) {
    background: transparent !important;
    border-bottom: 2px solid rgba(113, 57, 255, 0.2) !important;
    font-weight: 600 !important;
}

:deep(.el-table td.el-table__cell) {
    border-bottom: 1px solid rgba(156, 78, 255, 0.1) !important;
    padding: 10px 16px !important;
}

:deep(.el-table__inner-wrapper::before) {
    display: none;
}

:deep(.el-button--primary.is-link) {
    color: var(--primary-light);
}

:deep(.el-button--success.is-link) {
    color: var(--success);
}

:deep(.el-button.is-link:hover) {
    opacity: 0.8;
}

.pagination-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 16px 0 12px;
    flex-shrink: 0;
    border-top: 1px solid rgba(156, 78, 255, 0.1);
    margin-top: auto;
}

/* 分页组件深色主题 */
:deep(.el-pagination) {
    --el-pagination-bg-color: transparent;
    --el-pagination-text-color: #ffffff;
    --el-pagination-button-bg-color: rgba(13, 6, 27, 0.5);
    --el-pagination-hover-color: var(--primary);
    gap: 6px;
    font-size: 13px;
}

:deep(.el-pagination > .el-pagination__total),
:deep(.el-pagination > .el-pagination__sizes),
:deep(.el-pagination > .el-pagination__prev),
:deep(.el-pagination > .el-pagination__pager),
:deep(.el-pagination > .el-pagination__next) {
    margin: 0 3px;
}

:deep(.el-pagination .el-select .el-input) {
    background: rgba(13, 6, 27, 0.5);
    border: 1px solid rgba(156, 78, 255, 0.2);
    margin: 0 3px;
    border-radius: 6px;
}

:deep(.el-pagination .el-select .el-input .el-input__inner) {
    color: #ffffff;
    background: transparent;
}

:deep(.el-pagination button),
:deep(.el-pagination .btn-prev),
:deep(.el-pagination .btn-next) {
    background: rgba(13, 6, 27, 0.5) !important;
    color: #ffffff !important;
    border: 1px solid rgba(156, 78, 255, 0.2) !important;
    margin: 0 2px;
    border-radius: 6px;
    transition: all 0.2s ease;
}

:deep(.el-pagination button:hover),
:deep(.el-pagination .btn-prev:hover),
:deep(.el-pagination .btn-next:hover) {
    color: var(--primary) !important;
    border-color: var(--primary) !important;
    background: rgba(113, 57, 255, 0.15) !important;
    transform: translateY(-1px);
}

:deep(.el-pagination button:disabled),
:deep(.el-pagination .btn-prev:disabled),
:deep(.el-pagination .btn-next:disabled) {
    background: rgba(13, 6, 27, 0.3) !important;
    color: rgba(255, 255, 255, 0.3) !important;
    border-color: rgba(156, 78, 255, 0.1) !important;
    cursor: not-allowed;
    transform: none;
}

:deep(.el-pagination .el-pager li) {
    background: rgba(13, 6, 27, 0.5) !important;
    color: #ffffff !important;
    border: 1px solid rgba(156, 78, 255, 0.2) !important;
    min-width: 32px;
    margin: 0 2px;
    border-radius: 6px;
    transition: all 0.2s ease;
}

:deep(.el-pagination .el-pager li:hover) {
    color: var(--primary) !important;
    border-color: var(--primary) !important;
    background: rgba(113, 57, 255, 0.15) !important;
    transform: translateY(-1px);
}

:deep(.el-pagination .el-pager li.is-active) {
    background: linear-gradient(135deg, var(--primary), #9B59B6) !important;
    color: #ffffff !important;
    border-color: transparent !important;
    box-shadow: 0 2px 8px rgba(113, 57, 255, 0.3);
}

:deep(.el-pagination .el-pagination__total),
:deep(.el-pagination .el-pagination__sizes) {
    color: #ffffff !important;
    margin-right: 6px;
    font-size: 13px;
}

/* 详情对话框样式 */
.detail-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    max-height: 70vh;
    overflow-y: auto;
}

.detail-left {
    display: flex;
    flex-direction: column;
}

.image-preview {
    width: 100%;
    aspect-ratio: 4/3;
    border-radius: var(--radius-md);
    overflow: hidden;
    background: color-mix(in srgb, var(--card-bg) 60%, transparent);
    border: 1px solid var(--border);
}

.image-preview img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}

.preview-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    background: linear-gradient(135deg, color-mix(in srgb, var(--primary) 15%, transparent),
            color-mix(in srgb, var(--accent) 15%, transparent));
}

.large-emoji {
    font-size: 72px;
    filter: drop-shadow(0 0 30px rgba(113, 57, 255, 0.4));
}

.preview-placeholder p {
    font-size: 14px;
    color: var(--text-secondary);
}

.detail-right {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.detail-section h4 {
    font-size: 17px;
    font-weight: 700;
    margin-bottom: 12px;
    color: var(--text);
}

/* 修复 el-descriptions 白色背景问题 */
:deep(.el-descriptions) {
    background: transparent !important;
    --el-descriptions-item-bordered-bg: rgba(13, 6, 27, 0.5) !important;
}

:deep(.el-descriptions__table) {
    background: transparent !important;
    border: none !important;
}

:deep(.el-descriptions__header) {
    margin-bottom: 12px;
}

:deep(.el-descriptions__body) {
    background: transparent !important;
}

:deep(.el-descriptions__label) {
    background: rgba(13, 6, 27, 0.5) !important;
    color: var(--text-secondary) !important;
    border: 1px solid rgba(156, 78, 255, 0.15) !important;
    font-weight: 600 !important;
    padding: 10px 12px !important;
}

:deep(.el-descriptions__content) {
    background: rgba(13, 6, 27, 0.4) !important;
    color: var(--text) !important;
    border: 1px solid rgba(156, 78, 255, 0.15) !important;
    font-weight: 500 !important;
    padding: 10px 12px !important;
    max-width: 300px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.emotion-tag {
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 700;
    color: white;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.faces-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
    max-height: 300px;
    overflow-y: auto;
}

.face-detail-item {
    padding: 12px;
    background: color-mix(in srgb, var(--card-bg) 60%, transparent);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    transition: all 0.2s ease;
}

.face-detail-item:hover {
    border-color: color-mix(in srgb, var(--primary) 30%, transparent);
}

.face-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.face-index {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-secondary);
}

.face-emotion {
    font-size: 14px;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 4px;
}

.face-bbox {
    margin-top: 8px;
    font-size: 11px;
    color: var(--text-secondary);
    font-family: 'Courier New', monospace;
    padding: 4px 8px;
    background: color-mix(in srgb, var(--card-bg) 40%, transparent);
    border-radius: 4px;
}

/* 对话框底部按钮样式 */
:deep(.el-dialog__footer) {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    padding: 12px 20px !important;
}

:deep(.el-dialog__footer .el-button) {
    padding: 6px 16px !important;
    font-size: 13px !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}

:deep(.el-dialog__footer .el-button--primary) {
    background: linear-gradient(135deg, var(--primary), #9B59B6) !important;
    border: none !important;
    color: #ffffff !important;
    box-shadow: 0 2px 8px rgba(113, 57, 255, 0.3);
}

:deep(.el-dialog__footer .el-button--primary:hover) {
    box-shadow: 0 4px 12px rgba(113, 57, 255, 0.4);
    transform: translateY(-1px);
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}

@media (max-width: 768px) {
    .filter-cards {
        grid-template-columns: repeat(2, 1fr);
    }

    .history-table-container {
        overflow-x: auto;
    }

    :deep(.el-table) {
        min-width: 800px;
    }

    .detail-content {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 600px) {
    .filter-cards {
        grid-template-columns: 1fr;
    }
}
</style>
