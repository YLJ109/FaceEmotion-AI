<template>
    <div class="feedback-history-page">
        <!-- 筛选器卡片 - 参考HistoryViewer风格 -->


        <!-- 高级筛选栏 -->
        <div class="advanced-filter glass-panel">
            <div class="filter-row">
                <div class="filter-group">
                    <label>情绪类型：</label>
                    <el-select v-model="filters.emotion" placeholder="全部情绪" clearable @change="loadFeedbackHistory"
                        size="small">
                        <el-option label="全部" value="" />
                        <el-option v-for="emotion in emotionList" :key="emotion" :label="getEmotionName(emotion)"
                            :value="emotion">
                            <span class="emotion-option-emoji">{{ getEmotionEmoji(emotion) }}</span>
                            <span class="emotion-option-name">{{ getEmotionName(emotion) }}</span>
                        </el-option>
                    </el-select>
                </div>

                <div class="filter-group">
                    <label>时间范围：</label>
                    <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
                        end-placeholder="结束日期" format="YYYY-MM-DD" value-format="YYYY-MM-DD" @change="handleDateChange"
                        size="small" />
                </div>

                <div class="filter-actions">
                    <el-button @click="resetFilters" :icon="Refresh" size="small" class="reset-btn">重置</el-button>
                    <el-button type="primary" @click="loadFeedbackHistory" :icon="Search" size="small">刷新</el-button>
                    <el-button type="danger" @click="batchDelete" :icon="Delete" size="small"
                        :disabled="selectedRecords.length === 0" class="batch-btn">
                        批量删除({{ selectedRecords.length }})
                    </el-button>
                </div>
            </div>
        </div>

        <!-- 反馈记录列表 - 表格布局参考HistoryViewer -->
        <div class="records-container">
            <!-- 空状态 -->
            <div v-if="!loading && feedbackRecords.length === 0" class="empty-state">
                <div class="empty-icon">📝</div>
                <p>暂无反馈记录<br />在检测中提交反馈后将显示在这里</p>
            </div>

            <!-- 加载状态（骨架屏） -->
            <div v-if="loading" class="skeleton-container">
                <div v-for="i in 6" :key="i" class="skeleton-row">
                    <div class="skeleton-cell skeleton-avatar"></div>
                    <div class="skeleton-cell skeleton-text short"></div>
                    <div class="skeleton-cell skeleton-text medium"></div>
                    <div class="skeleton-cell skeleton-text long"></div>
                    <div class="skeleton-cell skeleton-button"></div>
                </div>
            </div>

            <!-- 反馈记录表格 -->
            <div v-if="!loading && feedbackRecords.length > 0" class="feedback-table-container">
                <el-table :data="feedbackRecords" style="width: 100%" :header-cell-style="headerCellStyle"
                    :cell-style="cellStyle" :row-class-name="tableRowClassName" @row-click="showRecordDetail"
                    highlight-current-row @selection-change="handleSelectionChange">
                    <!-- 多选列 -->
                    <el-table-column type="selection" width="55" align="center" fixed="left" />
                    <!-- 序号列 -->
                    <el-table-column label="ID编号" width="80" align="center">
                        <template #default="{ $index }">
                            <span class="index-number">{{ (currentPage - 1) * pageSize + $index + 1 }}</span>
                        </template>
                    </el-table-column>

                    <!-- 快照图片列 -->
                    <el-table-column label="快照" width="100" align="center">
                        <template #default="{ row }">
                            <div class="snapshot-thumbnail">
                                <img v-if="row.snapshot" :src="row.snapshot" alt="快照" />
                                <div v-else class="no-snapshot">
                                    <el-icon :size="24">
                                        <Picture />
                                    </el-icon>
                                </div>
                            </div>
                        </template>
                    </el-table-column>

                    <!-- 情绪对比列 -->
                    <el-table-column label="情绪对比" min-width="280" align="center">
                        <template #default="{ row }">
                            <div class="emotion-comparison-cell">
                                <div class="emotion-pair">
                                    <div class="emotion-item predicted">
                                        <span class="emotion-label-small">系统识别</span>
                                        <span class="emotion-badge-cell"
                                            :style="{ background: getEmotionColor(row.predicted_emotion) }">
                                            {{ getEmotionEmoji(row.predicted_emotion) }}
                                            {{ getEmotionName(row.predicted_emotion) }}
                                        </span>
                                        <span class="confidence-small" v-if="row.confidence">
                                            {{ (row.confidence * 100).toFixed(1) }}%
                                        </span>
                                    </div>

                                    <div class="arrow-icon-cell">→</div>

                                    <div class="emotion-item corrected">
                                        <span class="emotion-label-small">用户纠正</span>
                                        <span class="emotion-badge-cell"
                                            :style="{ background: getEmotionColor(row.correct_emotion) }">
                                            {{ getEmotionEmoji(row.correct_emotion) }}
                                            {{ getEmotionName(row.correct_emotion) }}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </template>
                    </el-table-column>

                    <!-- 备注列 -->
                    <el-table-column label="备注" min-width="150" show-overflow-tooltip>
                        <template #default="{ row }">
                            <span class="notes-text-cell">{{ row.notes || '-' }}</span>
                        </template>
                    </el-table-column>

                    <!-- 时间列 -->
                    <el-table-column label="提交时间" width="180" align="center">
                        <template #default="{ row }">
                            <span class="time-text">{{ formatTime(row.timestamp) }}</span>
                        </template>
                    </el-table-column>

                    <!-- 操作列 -->
                    <el-table-column label="操作" width="200" align="center" fixed="right">
                        <template #default="{ row }">
                            <div class="action-buttons">
                                <el-button size="small" type="primary" link @click.stop="showRecordDetail(row)">
                                    <el-icon>
                                        <View />
                                    </el-icon>
                                    详情
                                </el-button>
                                <el-button size="small" type="danger" link @click.stop="deleteRecord(row, $event)">
                                    <el-icon>
                                        <Delete />
                                    </el-icon>
                                    删除
                                </el-button>
                            </div>
                        </template>
                    </el-table-column>
                </el-table>
            </div>
        </div>

        <!-- 批量操作栏 -->
        <div v-if="selectedRecords.length > 0" class="batch-actions-bar">
            <span class="batch-info">已选择 {{ selectedRecords.length }} 条记录</span>
            <el-button type="danger" size="small" @click="batchDelete" :icon="Delete">
                批量删除
            </el-button>
            <el-button size="small" @click="clearSelection">
                取消选择
            </el-button>
        </div>

        <!-- 分页 -->
        <div class="pagination-bar" v-if="total > pageSize">
            <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total"
                :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" @current-change="handlePageChange"
                @size-change="handleSizeChange" />
        </div>

        <!-- 详情对话框 - 玻璃拟态风格参考HistoryViewer -->
        <el-dialog v-model="detailVisible" width="70%" class="feedback-detail-dialog" :show-close="false">
            <div v-if="selectedRecord" class="detail-content-redesign">
                <!-- 左侧: 快照图片 + 操作按钮 -->
                <div class="detail-left-redesign">
                    <div class="detail-title-section">
                        <h3 class="detail-main-title">反馈详情</h3>
                        <p class="detail-subtitle">记录 #{{ selectedRecord.id }} · {{
                            formatFullTime(selectedRecord.timestamp) }}</p>
                    </div>

                    <div class="snapshot-preview-redesign">
                        <img v-if="selectedRecord.snapshot" :src="selectedRecord.snapshot" alt="反馈快照"
                            class="preview-image-redesign" />
                        <div v-else class="preview-placeholder-redesign">
                            <el-icon :size="60">
                                <Picture />
                            </el-icon>
                            <p>无快照图片</p>
                        </div>
                    </div>

                    <!-- 操作按钮 -->
                    <div class="preview-actions-redesign">
                        <el-button @click="deleteFromDetail" class="action-btn-redesign delete-btn-redesign">
                            <el-icon>
                                <Delete />
                            </el-icon>
                            删除记录
                        </el-button>
                        <el-button @click="detailVisible = false" class="action-btn-redesign close-btn-redesign">
                            <el-icon>
                                <Close />
                            </el-icon>
                            关闭
                        </el-button>
                    </div>
                </div>

                <!-- 右侧: 详细信息 -->
                <div class="detail-right-redesign">
                    <div class="info-table-container-redesign">
                        <h4 class="section-title-redesign">
                            <el-icon>
                                <InfoFilled />
                            </el-icon>
                            详细信息
                        </h4>

                        <div class="info-grid-redesign">
                            <!-- 情绪对比 -->
                            <div class="info-item-redesign full-width">
                                <span class="info-label-redesign">情绪对比</span>
                                <div class="emotion-comparison-large">
                                    <div class="emotion-box predicted">
                                        <span class="box-label">系统识别</span>
                                        <div class="emotion-badge-large"
                                            :style="{ background: getEmotionColor(selectedRecord.predicted_emotion) }">
                                            {{ getEmotionEmoji(selectedRecord.predicted_emotion) }}
                                            {{ getEmotionName(selectedRecord.predicted_emotion) }}
                                        </div>
                                        <span class="confidence-large" v-if="selectedRecord.confidence">
                                            置信度: {{ (selectedRecord.confidence * 100).toFixed(1) }}%
                                        </span>
                                    </div>

                                    <div class="arrow-large">→</div>

                                    <div class="emotion-box corrected">
                                        <span class="box-label">用户纠正</span>
                                        <div class="emotion-badge-large"
                                            :style="{ background: getEmotionColor(selectedRecord.correct_emotion) }">
                                            {{ getEmotionEmoji(selectedRecord.correct_emotion) }}
                                            {{ getEmotionName(selectedRecord.correct_emotion) }}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- 人脸位置 -->
                            <div class="info-item-redesign" v-if="selectedRecord.bbox">
                                <span class="info-label-redesign">人脸位置</span>
                                <span class="info-value-redesign bbox-value">
                                    [{{selectedRecord.bbox.map(c => Math.round(c)).join(', ')}}]
                                </span>
                            </div>

                            <!-- 备注信息 -->
                            <div class="info-item-redesign full-width" v-if="selectedRecord.notes">
                                <span class="info-label-redesign">备注说明</span>
                                <p class="notes-content-redesign">{{ selectedRecord.notes }}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Search, Loading, DocumentDelete, Picture, Delete, View, Close, InfoFilled, DataAnalysis } from '@element-plus/icons-vue'
import { getEmotionName, getEmotionEmoji, getEmotionColor, EMOTION_LIST } from '@/utils/emotion'
import { API } from '@/api/config'

// ✅ 使用完整的 emotion 列表（过滤别名，避免重复）
const emotionList = EMOTION_LIST.filter(e => !['enjoy', 'surprise', 'fear', 'disgusted', 'neutral'].includes(e))

// 数据状态
const loading = ref(false)
const feedbackRecords = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

// ✅ 新增: 批量选择
const selectedRecords = ref([])

// 筛选条件
const filters = ref({
    emotion: ''
})
const dateRange = ref(null)

// 详情对话框
const detailVisible = ref(false)
const selectedRecord = ref(null)

// ✅ 新增: 表格样式配置
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

// ✅ 新增: 清除情绪筛选
const clearEmotionFilter = () => {
    filters.value.emotion = ''
    currentPage.value = 1
    loadFeedbackHistory()
}

// ✅ 新增: 设置情绪筛选
const setEmotionFilter = (emotion) => {
    filters.value.emotion = emotion
    currentPage.value = 1
    loadFeedbackHistory()
}

// 加载反馈历史
const loadFeedbackHistory = async () => {
    loading.value = true
    try {
        const params = new URLSearchParams({
            limit: pageSize.value,
            offset: (currentPage.value - 1) * pageSize.value
        })

        if (filters.value.emotion) {
            params.append('emotion', filters.value.emotion)
        }

        if (dateRange.value && dateRange.value.length === 2) {
            params.append('start_date', dateRange.value[0])
            params.append('end_date', dateRange.value[1])
        }

        const response = await fetch(`${API.feedbackHistory}?${params.toString()}`)
        const data = await response.json()

        if (data.status === 'success') {
            feedbackRecords.value = data.records
            total.value = data.total
        } else {
            ElMessage.error('加载失败')
        }
    } catch (error) {
        console.error('加载反馈历史失败:', error)
        ElMessage.error('网络错误，请稍后重试')
    } finally {
        loading.value = false
    }
}

// 处理日期变化
const handleDateChange = () => {
    currentPage.value = 1
    loadFeedbackHistory()
}

// 重置筛选
const resetFilters = () => {
    filters.value.emotion = ''
    dateRange.value = null
    currentPage.value = 1
    loadFeedbackHistory()
}

// 分页变化
const handlePageChange = (page) => {
    currentPage.value = page
    loadFeedbackHistory()
}

const handleSizeChange = (size) => {
    pageSize.value = size
    currentPage.value = 1
    loadFeedbackHistory()
}

// 显示详情
const showRecordDetail = (record) => {
    selectedRecord.value = record
    detailVisible.value = true
}

// ✅ 删除反馈记录
const deleteRecord = async (record, event) => {
    if (event) {
        event.stopPropagation()
    }

    try {
        await ElMessageBox.confirm(
            `确定要删除这条反馈记录吗？\n\n记录 ID: #${record.id}\n时间: ${formatFullTime(record.timestamp)}`,
            '确认删除',
            {
                confirmButtonText: '删除',
                cancelButtonText: '取消',
                type: 'warning',
                confirmButtonClass: 'el-button--danger'
            }
        )

        const response = await fetch(`${API.feedback}/${record.id}`, {
            method: 'DELETE'
        })

        const data = await response.json()

        if (data.status === 'success') {
            ElMessage.success('✅ 删除成功')
            const index = feedbackRecords.value.findIndex(r => r.id === record.id)
            if (index !== -1) {
                feedbackRecords.value.splice(index, 1)
                total.value -= 1
            }
            detailVisible.value = false
        } else {
            ElMessage.error('删除失败')
        }
    } catch (error) {
        if (error !== 'cancel') {
            console.error('删除反馈记录失败:', error)
            ElMessage.error('网络错误，请稍后重试')
        }
    }
}

// ✅ 从详情对话框删除
const deleteFromDetail = () => {
    if (selectedRecord.value) {
        deleteRecord(selectedRecord.value, null)
    }
}

// ✅ 新增: 处理选择变化
const handleSelectionChange = (selection) => {
    selectedRecords.value = selection
}

// ✅ 新增: 批量删除
const batchDelete = async () => {
    if (selectedRecords.value.length === 0) {
        ElMessage.warning('请先选择要删除的记录')
        return
    }

    try {
        await ElMessageBox.confirm(
            `确定要删除选中的 ${selectedRecords.value.length} 条反馈记录吗？此操作不可恢复！`,
            '批量删除确认',
            {
                confirmButtonText: '删除',
                cancelButtonText: '取消',
                type: 'warning',
                confirmButtonClass: 'el-button--danger'
            }
        )

        const deletePromises = selectedRecords.value.map(record =>
            fetch(`${API.feedback}/${record.id}`, { method: 'DELETE' })
        )

        const results = await Promise.all(deletePromises)
        const successCount = results.filter(r => r.ok).length

        if (successCount > 0) {
            ElMessage.success(`✅ 成功删除 ${successCount} 条记录`)
            // 重新加载数据
            loadFeedbackHistory()
            selectedRecords.value = []
        } else {
            ElMessage.error('删除失败')
        }
    } catch (error) {
        if (error !== 'cancel') {
            console.error('批量删除失败:', error)
            ElMessage.error('网络错误，请稍后重试')
        }
    }
}

// ✅ 新增: 清空选择
const clearSelection = () => {
    selectedRecords.value = []
}

// 格式化时间（短时间）
const formatTime = (timestamp) => {
    if (!timestamp) return '-'
    const date = new Date(timestamp)
    return date.toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    })
}

// 格式化完整时间
const formatFullTime = (timestamp) => {
    if (!timestamp) return '-'
    const date = new Date(timestamp)
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    })
}

// 组件挂载时加载数据
onMounted(() => {
    loadFeedbackHistory()
})
</script>

<style scoped>
/* ===== 主容器 ===== */
.feedback-history-page {
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 0;
    overflow: hidden;
    animation: fadeIn 0.3s ease;
}

/* ===== 筛选器卡片 - 参考HistoryViewer ===== */
.filter-cards {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-bottom: 16px;
    margin-top: 2px;
    flex-shrink: 0;
    min-height: auto;
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

.filter-emoji {
    font-size: 20px;
}

.filter-info {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
}

.filter-label {
    font-size: 14px;
    font-weight: 100;
    color: var(--text);
    margin-bottom: 2px;
}

.filter-count {
    font-size: 18px;
    font-weight: 700;
    color: var(--primary-light);
    font-family: 'Consolas', 'Monaco', monospace;
    display: none;
    /* ✅ 隐藏情绪统计数据 */
}

/* ===== 高级筛选栏 ===== */
.advanced-filter {
    padding: 16px 20px;
    flex-shrink: 0;
    background: var(--card-bg);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
}

.filter-row {
    display: flex;
    align-items: center;
    gap: 20px;
    flex-wrap: wrap;
}

.filter-group {
    display: flex;
    align-items: center;
    gap: 10px;
}

.filter-group label {
    font-size: 14px;
    color: var(--text-secondary);
    font-weight: 500;
    white-space: nowrap;
}

.filter-actions {
    margin-left: auto;
    display: flex;
    gap: 10px;
}

/* ✅ 修复: 重置按钮样式 - 适配7个主题 */
.reset-btn {
    background: transparent !important;
    border: 1.5px solid var(--border) !important;
    color: var(--text) !important;
    backdrop-filter: blur(8px) !important;
}

.reset-btn:hover {
    background: color-mix(in srgb, var(--primary) 12%, transparent) !important;
    border-color: var(--primary-light) !important;
    color: var(--text) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(113, 57, 255, 0.15) !important;
}

.reset-btn:active {
    transform: translateY(0) scale(0.98) !important;
}

/* ✅ 批量删除按钮样式 */
.batch-btn {
    background: transparent !important;
    border: 1.5px solid var(--danger) !important;
    color: var(--danger) !important;
    backdrop-filter: blur(8px) !important;
}

.batch-btn:hover:not(:disabled) {
    background: rgba(245, 108, 108, 0.15) !important;
    border-color: var(--danger) !important;
    color: var(--danger) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(245, 108, 108, 0.2) !important;
}

.batch-btn:disabled {
    opacity: 0.4 !important;
    cursor: not-allowed !important;
    transform: none !important;
}

/* ===== 记录容器 ===== */
.records-container {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    gap: 16px;
}

/* 空状态 */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    gap: 16px;
    color: var(--text-secondary);
    animation: fadeIn 0.3s ease;
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

/* ===== 骨架屏 ===== */
.skeleton-container {
    padding: 20px;
    animation: fadeIn 0.3s ease;
}

.skeleton-row {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 12px 0;
    border-bottom: 1px solid var(--border);
}

.skeleton-cell {
    background: linear-gradient(90deg,
            color-mix(in srgb, var(--card-bg) 50%, transparent) 25%,
            color-mix(in srgb, var(--card-bg) 70%, transparent) 50%,
            color-mix(in srgb, var(--card-bg) 50%, transparent) 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 4px;
}

.skeleton-avatar {
    width: 60px;
    height: 60px;
    border-radius: 8px;
    flex-shrink: 0;
}

.skeleton-text {
    height: 16px;
}

.skeleton-text.short {
    width: 100px;
}

.skeleton-text.medium {
    width: 150px;
}

.skeleton-text.long {
    width: 200px;
}

.skeleton-button {
    width: 80px;
    height: 32px;
    margin-left: auto;
}

@keyframes shimmer {
    0% {
        background-position: -200% 0;
    }

    100% {
        background-position: 200% 0;
    }
}

/* ===== 表格容器 ===== */
.feedback-table-container {
    flex: 1;
    overflow: hidden;
    border-radius: var(--radius-md);
    background: var(--card-bg);
    backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    box-shadow: var(--shadow-md);
    min-height: 0;
    min-height: 300px;
    max-height: calc(100vh - 180px);
}

/* 序号样式 */
.index-number {
    font-size: 13px;
    font-weight: 100;
    color: var(--text-secondary);
    font-family: 'Consolas', 'Monaco', monospace;
}

/* 快照缩略图 */
.snapshot-thumbnail {
    width: 70px;
    height: 50px;
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

.snapshot-thumbnail:hover {
    transform: scale(1.05);
    border-color: rgba(113, 57, 255, 0.4);
    box-shadow: 0 2px 8px rgba(113, 57, 255, 0.2);
}

.snapshot-thumbnail img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.no-snapshot {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-secondary);
    opacity: 0.5;
}

/* 情绪对比单元格 */
.emotion-comparison-cell {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 4px;
}

.emotion-pair {
    display: flex;
    align-items: center;
    gap: 16px;
}

.emotion-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
    align-items: center;
}

.emotion-label-small {
    font-size: 11px;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.emotion-badge-cell {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 100;
    color: var(--text);
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
    border: 1px solid color-mix(in srgb, var(--border) 30%, transparent);
    transition: all 0.2s ease;
    white-space: nowrap;
}

.emotion-badge-cell:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.35);
}

.confidence-small {
    font-size: 12px;
    color: var(--success);
    font-weight: 100;
    font-family: 'Consolas', 'Monaco', monospace;
}

.arrow-icon-cell {
    font-size: 24px;
    color: var(--text-secondary);
    opacity: 0.5;
    font-weight: 700;
}

/* 备注文本 */
.notes-text-cell {
    font-size: 13px;
    color: var(--text-secondary);
    opacity: 0.8;
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

.action-buttons .el-button--danger.is-link {
    background: rgba(245, 108, 108, 0.15);
    color: var(--danger);
    border: 1px solid rgba(245, 108, 108, 0.3);
}

.action-buttons .el-button--danger.is-link:hover {
    background: rgba(245, 108, 108, 0.25);
    border-color: var(--danger);
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(245, 108, 108, 0.3);
}

/* 表格行样式 */
:deep(.el-table__row) {
    cursor: pointer;
    transition: all 0.2s ease;
}

:deep(.el-table__row:hover) {
    background: color-mix(in srgb, var(--primary) 10%, transparent) !important;
}

:deep(.table-row-even) {
    background: color-mix(in srgb, var(--card-bg) 70%, transparent);
}

:deep(.table-row-odd) {
    background: color-mix(in srgb, var(--card-bg) 85%, transparent);
}

:deep(.el-table__body tr.current-row > td) {
    background: color-mix(in srgb, var(--primary) 15%, transparent) !important;
}

/* Element Plus 表格深度样式 */
:deep(.el-table) {
    background: transparent;
    --el-table-border-color: var(--border);
    --el-table-header-bg-color: transparent;
    --el-table-tr-bg-color: transparent;
}

:deep(.el-table th.el-table__cell) {
    background: transparent !important;
    border-bottom: 2px solid color-mix(in srgb, var(--primary) 20%, transparent) !important;
}

:deep(.el-table td.el-table__cell) {
    border-bottom: 1px solid color-mix(in srgb, var(--border) 40%, transparent) !important;
    padding: 10px 16px !important;
}

/* ===== 分页 ===== */
.pagination-bar {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 16px 0 12px;
    flex-shrink: 0;
    border-top: 1px solid color-mix(in srgb, var(--border) 40%, transparent);
    margin-top: auto;
}

/* ✅ 新增: 批量操作栏样式 */
.batch-actions-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 20px;
    background: var(--card-bg);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    margin-top: 12px;
    animation: slideIn 0.3s ease;
}

.batch-info {
    font-size: 14px;
    color: var(--text);
    font-weight: 500;
}

.batch-actions-bar .el-button {
    margin-left: 10px;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

:deep(.el-pagination) {
    --el-pagination-bg-color: transparent;
    --el-pagination-text-color: var(--text);
    --el-pagination-button-bg-color: color-mix(in srgb, var(--card-bg) 50%, transparent);
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
    background: color-mix(in srgb, var(--card-bg) 50%, transparent);
    border: 1px solid color-mix(in srgb, var(--border) 40%, transparent);
    margin: 0 3px;
    border-radius: 6px;
}

:deep(.el-pagination .el-select .el-input .el-input__inner) {
    color: var(--text);
    background: transparent;
}

:deep(.el-pagination button),
:deep(.el-pagination .btn-prev),
:deep(.el-pagination .btn-next) {
    background: color-mix(in srgb, var(--card-bg) 50%, transparent) !important;
    color: var(--text) !important;
    border: 1px solid color-mix(in srgb, var(--border) 40%, transparent) !important;
    margin: 0 2px;
    border-radius: 6px;
    transition: all 0.2s ease;
}

:deep(.el-pagination button:hover),
:deep(.el-pagination .btn-prev:hover),
:deep(.el-pagination .btn-next:hover) {
    color: var(--primary) !important;
    border-color: var(--primary) !important;
    background: color-mix(in srgb, var(--primary) 15%, transparent) !important;
    transform: translateY(-1px);
}

:deep(.el-pagination button:disabled),
:deep(.el-pagination .btn-prev:disabled),
:deep(.el-pagination .btn-next:disabled) {
    background: color-mix(in srgb, var(--card-bg) 30%, transparent) !important;
    color: color-mix(in srgb, var(--text) 30%, transparent) !important;
    border-color: color-mix(in srgb, var(--border) 20%, transparent) !important;
    cursor: not-allowed;
    transform: none;
}

:deep(.el-pagination .el-pager li) {
    background: color-mix(in srgb, var(--card-bg) 50%, transparent) !important;
    color: var(--text) !important;
    border: 1px solid color-mix(in srgb, var(--border) 40%, transparent) !important;
    min-width: 32px;
    margin: 0 2px;
    border-radius: 6px;
    transition: all 0.2s ease;
}

:deep(.el-pagination .el-pager li:hover) {
    color: var(--primary) !important;
    border-color: var(--primary) !important;
    background: color-mix(in srgb, var(--primary) 15%, transparent) !important;
    transform: translateY(-1px);
}

:deep(.el-pagination .el-pager li.is-active) {
    background: linear-gradient(135deg, var(--primary), #9B59B6) !important;
    color: var(--text) !important;
    border-color: transparent !important;
    box-shadow: 0 2px 8px rgba(113, 57, 255, 0.3);
}

:deep(.el-pagination .el-pagination__total),
:deep(.el-pagination .el-pagination__sizes) {
    color: var(--text) !important;
    margin-right: 6px;
    font-size: 13px;
}

/* ===== 详情对话框 - 玻璃拟态 ===== */
:deep(.feedback-detail-dialog) {
    .el-dialog {
        background: var(--card-bg) !important;
        backdrop-filter: blur(20px);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-xl);
        margin-top: 1vh !important;
        max-height: 90vh !important;
    }

    .el-dialog__header {
        display: none !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
    }

    .el-dialog__body {
        padding: 0 !important;
        overflow: visible !important;
        max-height: none !important;
    }
}

/* 详情内容布局 */
.detail-content-redesign {
    display: grid;
    grid-template-columns: 320px 1fr;
    gap: 24px;
    max-height: none !important;
    overflow: visible !important;
}

/* 左侧区域 */
.detail-left-redesign {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.detail-title-section {
    padding: 16px;
    background: var(--card-bg);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
}

.detail-main-title {
    font-size: 20px;
    font-weight: 700;
    color: var(--text);
    margin: 0 0 6px 0;
}

.detail-subtitle {
    font-size: 13px;
    color: var(--text-secondary);
    opacity: 0.7;
    margin: 0;
}

/* 快照预览 */
.snapshot-preview-redesign {
    width: 100%;
    min-height: 240px;
    max-height: 400px;
    border-radius: var(--radius-md);
    overflow: hidden;
    background: color-mix(in srgb, var(--card-bg) 60%, transparent);
    border: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
    display: flex;
    align-items: center;
    justify-content: center;
}

.preview-image-redesign {
    width: 100%;
    height: auto;
    max-height: 400px;
    object-fit: contain;
    border-radius: var(--radius-md);
}

.preview-placeholder-redesign {
    width: 100%;
    height: 100%;
    min-height: 240px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    background: linear-gradient(135deg,
            color-mix(in srgb, var(--primary) 15%, transparent),
            color-mix(in srgb, var(--accent) 15%, transparent));
}

.preview-placeholder-redesign .el-icon {
    opacity: 0.5;
}

.preview-placeholder-redesign p {
    font-size: 14px;
    color: var(--text-secondary);
}

/* 操作按钮 */
.preview-actions-redesign {
    display: flex;
    gap: 12px;
}

.action-btn-redesign {
    flex: 1;
    padding: 12px 16px;
    border-radius: var(--radius-sm);
    font-size: 14px;
    font-weight: 500;
    transition: all 0.2s ease;
}

.delete-btn-redesign {
    background: rgba(245, 108, 108, 0.15);
    border: 1px solid rgba(245, 108, 108, 0.3);
    color: #ff6b6b;
}

.delete-btn-redesign:hover {
    background: rgba(245, 108, 108, 0.25);
    border-color: #ff4d4d;
    color: #ff4d4d;
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(245, 108, 108, 0.3);
}

.close-btn-redesign {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: var(--text-secondary);
}

.close-btn-redesign:hover {
    background: rgba(255, 255, 255, 0.15);
    border-color: rgba(255, 255, 255, 0.3);
    color: var(--text);
    transform: translateY(-1px);
}

/* 右侧区域 */
.detail-right-redesign {
    display: flex;
    flex-direction: column;
    gap: 16px;
    min-height: 400px;
}

.info-table-container-redesign {
    padding: 20px;
    background: var(--card-bg);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
}

.section-title-redesign {
    font-size: 16px;
    font-weight: 100;
    color: var(--text);
    margin: 0 0 16px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

.section-title-redesign .el-icon {
    font-size: 18px;
    color: var(--primary-light);
}

/* 信息网格 */
.info-grid-redesign {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.info-item-redesign {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.info-item-redesign.full-width {
    grid-column: 1 / -1;
}

.info-label-redesign {
    font-size: 12px;
    color: var(--text-secondary);
    font-weight: 100;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.info-value-redesign {
    font-size: 14px;
    color: var(--text);
    font-weight: 500;
}

.bbox-value {
    font-family: 'Courier New', 'Consolas', monospace;
    color: var(--primary-light);
}

/* 情绪对比大视图 */
.emotion-comparison-large {
    display: flex;
    align-items: center;
    gap: 24px;
    padding: 20px;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 12px;
    border: 1px solid var(--border);
}

.emotion-box {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8px;
    align-items: center;
}

.box-label {
    font-size: 12px;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.emotion-badge-large {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 12px 20px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 100;
    color: var(--text);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    border: 1px solid color-mix(in srgb, var(--border) 30%, transparent);
    transition: all 0.2s ease;
    white-space: nowrap;
}

.emotion-badge-large:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
}

.confidence-large {
    font-size: 14px;
    color: var(--success);
    font-weight: 100;
    font-family: 'Consolas', 'Monaco', monospace;
}

.arrow-large {
    font-size: 32px;
    color: var(--text-secondary);
    opacity: 0.5;
    font-weight: 700;
}

/* 备注内容 */
.notes-content-redesign {
    font-size: 14px;
    color: var(--text);
    line-height: 1.6;
    margin: 0;
    padding: 12px;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 8px;
    border: 1px solid var(--border);
    white-space: pre-wrap;
}

/* 下拉选项样式 */
.emotion-option-emoji {
    font-size: 16px;
    line-height: 1;
    flex-shrink: 0;
}

.emotion-option-name {
    font-size: 14px;
    color: var(--text);
    font-weight: 500;
    white-space: nowrap;
}

/* 动画 */
@keyframes fadeIn {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}

/* 响应式 */
@media (max-width: 768px) {
    .filter-cards {
        grid-template-columns: repeat(2, 1fr);
    }

    .filter-row {
        flex-direction: column;
        align-items: stretch;
    }

    .filter-actions {
        margin-left: 0;
        justify-content: flex-end;
    }

    .detail-content-redesign {
        grid-template-columns: 1fr;
    }

    .emotion-comparison-large {
        flex-direction: column;
        gap: 16px;
    }

    .arrow-large {
        transform: rotate(90deg);
    }
}

@media (max-width: 600px) {
    .filter-cards {
        grid-template-columns: 1fr;
    }
}
</style>