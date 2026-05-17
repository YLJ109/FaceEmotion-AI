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
                        <span class="filter-label">批量图片检测</span>
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

            <div class="filter-card" :class="{ active: filterType === 'batch_video' }"
                @click="setFilter('batch_video')">
                <div class="filter-card-inner">
                    <div class="filter-icon-wrap"
                        style="background: linear-gradient(135deg, rgba(230, 162, 60, 0.2), rgba(245, 108, 108, 0.2));">
                        <el-icon :size="20" color="#E6A23C">
                            <VideoPlay />
                        </el-icon>
                    </div>
                    <div class="filter-info">
                        <span class="filter-label">批量视频检测</span>
                        <span class="filter-count">{{ typeCounts.batch_video }} 条</span>
                    </div>
                </div>
            </div>


        </div>

        <!-- 空状态 -->
        <div v-if="!loading && historyList.length === 0" class="empty-state">
            <div class="empty-icon">📋</div>
            <p>暂无历史记录<br />进行检测后将自动保存</p>
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

        <!-- 历史记录表格 -->
        <div v-if="!loading && historyList.length > 0" class="history-table-container">
            <el-table :data="historyList" style="width: 100%" :header-cell-style="headerCellStyle"
                :cell-style="cellStyle" :row-class-name="tableRowClassName" @row-click="handleRowClick"
                highlight-current-row @selection-change="handleSelectionChange">
                <!-- ✅ 新增: 多选列 -->
                <el-table-column type="selection" width="55" align="center" fixed="left" />
                <!-- ✅ 新增: 序号列 -->
                <el-table-column label="ID编号" width="80" align="center">
                    <template #default="{ $index }">
                        <span class="index-number">{{ (currentPage - 1) * pageSize + $index + 1 }}</span>
                    </template>
                </el-table-column>
                <!-- 缩略图/情绪图标列 -->
                <el-table-column label="预览" width="100" align="center">
                    <template #default="{ row }">
                        <div class="table-thumbnail">
                            <!-- ✅ 修复: 所有检测类型都使用保存的缩略图 -->
                            <img v-if="row.thumbnail && row.thumbnail.length > 100" :src="row.thumbnail" alt="缩略图" />
                            <!-- 无缩略图或无效数据: 显示情绪图标 -->
                            <div v-else class="thumbnail-placeholder-small">
                                <span class="placeholder-emoji-small">{{ getEmotionEmoji(row.dominant_emotion) }}</span>
                            </div>

                            <!-- ✅ 新增: 人脸数量标记（显示在缩略图右下角） -->
                            <div v-if="row.detected_faces?.length > 0" class="face-count-badge">
                                {{ row.detected_faces.length }}
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
                <el-table-column label="操作" width="200" align="center" fixed="right">
                    <template #default="{ row }">
                        <div class="action-buttons">
                            <el-button size="small" class="detail-btn" @click="showDetail(row)">
                                <el-icon>
                                    <View />
                                </el-icon>
                                详情
                            </el-button>
                            <el-button size="small" class="delete-btn" @click="deleteRecord(row)">
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
        <div v-if="historyList.length > 0" class="pagination-container">
            <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total"
                :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" @size-change="handleSizeChange"
                @current-change="handlePageChange" />
        </div>

        <!-- 详情对话框 - 玻璃拟态风格 -->
        <el-dialog v-model="dialogVisible" :close-on-click-modal="false" width="80%" class="history-detail-dialog"
            :show-close="false">
            <div v-if="selectedItem" class="detail-content-redesign">
                <!-- 左侧: 检测详情标题 + 图片预览 + 导出按钮 + 关闭按钮 -->
                <div class="detail-left-redesign">
                    <div class="detail-title-section">
                        <h3 class="detail-main-title">检测详情</h3>
                        <p class="detail-subtitle">{{ getTypeLabel(selectedItem?.detection_type) }} · {{
                            formatTime(selectedItem?.created_at) }}</p>
                    </div>

                    <div class="image-preview-redesign">
                        <!-- ✅ 修改: 所有检测类型都使用 img 标签显示缩略图 -->
                        <img v-if="selectedItem.thumbnail && selectedItem.thumbnail.length > 100"
                            :src="selectedItem.thumbnail" alt="检测图片" class="preview-image-redesign" />
                        <!-- 无图片或无效图片时显示情绪图标 -->
                        <div v-else class="preview-placeholder-redesign">
                            <span class="large-emoji-redesign">{{ getEmotionEmoji(selectedItem.dominant_emotion ||
                                'neutral')
                            }}</span>
                            <p>无预览图片</p>
                        </div>
                    </div>

                    <!-- 操作按钮: 导出JSON + 关闭 -->
                    <div class="preview-actions-redesign">
                        <el-button @click="exportSingleRecord(selectedItem)"
                            class="action-btn-redesign export-btn-redesign">
                            <el-icon>
                                <Download />
                            </el-icon>
                            导出 JSON
                        </el-button>
                        <el-button @click="dialogVisible = false" class="action-btn-redesign close-btn-redesign">
                            <el-icon>
                                <Close />
                            </el-icon>
                            关闭
                        </el-button>
                    </div>
                </div>

                <!-- 右侧: 检测到的人脸表格 -->
                <div class="detail-right-redesign">
                    <div class="faces-table-container-redesign">
                        <h4 class="section-title-redesign">
                            <el-icon>
                                <UserFilled />
                            </el-icon>
                            检测到的人脸 ({{ selectedItem.detected_faces.length }})
                        </h4>

                        <el-table :data="selectedItem.detected_faces" class="faces-table-redesign" size="small"
                            :header-cell-style="facesTableHeaderStyle" :cell-style="facesTableCellStyle"
                            :row-class-name="facesTableRowClassName">

                            <!-- 人脸预览列 -->
                            <el-table-column label="预览" width="120" align="center">
                                <template #default="{ row, $index }">
                                    <div class="face-thumbnail-redesign">
                                        <canvas :ref="el => setFaceCanvasRef(el, $index)"
                                            class="face-mini-canvas-redesign"></canvas>
                                    </div>
                                </template>
                            </el-table-column>

                            <!-- 序号列 -->
                            <el-table-column label="#" width="60" align="center">
                                <template #default="{ $index }">
                                    <span class="face-index-redesign">{{ $index + 1 }}</span>
                                </template>
                            </el-table-column>

                            <!-- 情绪标签列 -->
                            <el-table-column label="情绪" min-width="40" align="center">
                                <template #default="{ row }">
                                    <span class="emotion-badge-small-redesign"
                                        :style="{ background: getEmotionColor(row.emotion) }">
                                        {{ getEmotionEmoji(row.emotion) }}
                                        {{ getEmotionName(row.emotion) }}
                                    </span>
                                </template>
                            </el-table-column>

                            <!-- 置信度列 -->
                            <el-table-column label="置信度" width="150" align="center">
                                <template #default="{ row }">
                                    <div class="confidence-cell-redesign">
                                        <el-progress
                                            :percentage="clampPercentage(parseFloat(((row.confidence || 0) * 100).toFixed(1)))"
                                            :color="getEmotionGradient(row.emotion)" :stroke-width="8"
                                            :show-text="true" />
                                    </div>
                                </template>
                            </el-table-column>

                            <!-- 坐标信息列 -->
                            <el-table-column label="坐标" width="180" align="center">
                                <template #default="{ row }">
                                    <span class="bbox-text-redesign">[{{row.bbox?.map(c =>
                                        Math.round(c)).join(',')}}]</span>

                                </template>
                            </el-table-column>

                            <!-- 操作列 -->
                            <el-table-column label="操作" width="100" align="center" fixed="right">
                                <template #default="{ row, $index }">
                                    <el-button @click="openFaceFeedback(row, $index)" class="face-feedback-btn-redesign"
                                        size="small" text>
                                        <el-icon>
                                            <Edit />
                                        </el-icon>
                                        反馈
                                    </el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                    </div>
                </div>
            </div>
        </el-dialog>

        <!-- ✅ 新增: 反馈对话框 -->
        <el-dialog v-model="feedbackDialogVisible" title="提交反馈" width="500px" class="feedback-dialog">
            <div class="feedback-form">
                <div class="feedback-info">
                    <span class="feedback-label">记录 ID:</span>
                    <span class="feedback-value">{{ feedbackForm.recordId }}</span>
                </div>
                <div v-if="feedbackForm.faceIndex !== null" class="feedback-info">
                    <span class="feedback-label">人脸索引:</span>
                    <span class="feedback-value">#{{ feedbackForm.faceIndex + 1 }}</span>
                </div>
                <el-form :model="feedbackForm" label-width="80px">
                    <el-form-item label="正确情绪">
                        <el-select v-model="feedbackForm.correctEmotion" placeholder="请选择正确的情绪" style="width: 100%">
                            <el-option v-for="emotion in emotionList" :key="emotion"
                                :label="getEmotionEmoji(emotion) + ' ' + getEmotionName(emotion)" :value="emotion" />
                        </el-select>
                    </el-form-item>
                    <el-form-item label="备注说明">
                        <el-input v-model="feedbackForm.comment" type="textarea" :rows="3" placeholder="可选：添加额外说明" />
                    </el-form-item>
                </el-form>
            </div>
            <template #footer>
                <el-button @click="feedbackDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="handleSubmitFeedback" :loading="feedbackSubmitting">提交反馈</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { Clock, Loading, Picture, View, Download, DataAnalysis, VideoCamera, Files, Film, Edit, InfoFilled, UserFilled, Delete, Close, VideoPlay } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getEmotionName, getEmotionColor, getEmotionEmoji, EMOTION_LIST } from '@/constants/emotions'
import { getHistoryList, deleteHistoryRecord } from '@/api/modules/history'
import { submitFeedback } from '@/api/modules/system'

// 过滤重复情绪（排除别名：surprised, fearful, calm）
const emotionList = EMOTION_LIST.filter(e => !['surprised', 'fearful', 'calm'].includes(e))

const loading = ref(false)
const historyList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const dialogVisible = ref(false)
const selectedItem = ref(null)
const filterType = ref('all') // 筛选类型
const faceCanvasRefs = ref([]) // ✅ 新增: 人脸表格中的 Canvas 引用数组
const singleFaceCanvas = ref(null) // ✅ 新增: 单张人脸 Canvas 引用
const typeCounts = ref({
    realtime: 0,
    image: 0,
    batch: 0,
    video: 0,
    batch_video: 0
})

// ✅ 新增: 批量选择
const selectedRecords = ref([])

// ✅ 新增: 反馈相关状态
const feedbackDialogVisible = ref(false)
const feedbackSubmitting = ref(false)
const feedbackForm = ref({
    recordId: null,
    faceIndex: null,
    predictedEmotion: '',  // ✅ 新增: 预测的情绪
    correctEmotion: '',
    comment: '',
    snapshot: ''  // ✅ 新增: 快照图片
})

// ✅ 新增: 人脸表格样式配置
const facesTableHeaderStyle = {
    background: 'transparent',
    color: '#ffffff',
    fontWeight: '100',
    fontSize: '12px',
    padding: '8px 0',
    borderBottom: '1px solid rgba(113, 57, 255, 0.2)'
}

const facesTableCellStyle = {
    background: 'transparent',
    color: '#ffffff',
    borderBottom: '1px solid rgba(156, 78, 255, 0.1)',
    padding: '8px 0',
    fontSize: '13px'
}

const facesTableRowClassName = ({ rowIndex }) => {
    return rowIndex % 2 === 0 ? 'face-table-row-even' : 'face-table-row-odd'
}

// 获取历史记录
const fetchHistory = async () => {
    loading.value = true
    try {
        const offset = (currentPage.value - 1) * pageSize.value
        const params = { limit: pageSize.value, offset }

        if (filterType.value !== 'all') {
            params.type = filterType.value
        }

        const data = await getHistoryList(params)
        historyList.value = data.data || []
        total.value = data.total || 0

        // 更新各类型数量
        if (data.type_counts) {
            typeCounts.value = {
                realtime: data.type_counts.realtime || 0,
                image: data.type_counts.image || 0,
                batch: data.type_counts.batch || 0,
                video: data.type_counts.video || 0,
                batch_video: data.type_counts.batch_video || 0
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

    // ✅ 优化: 如果是单张人脸,裁剪单张人脸 Canvas
    if (item.detected_faces?.length === 1) {
        nextTick(() => {
            cropSingleFaceThumbnail()
        })
    }
}

// ✅ 新增: 删除历史记录
const deleteRecord = async (item) => {
    try {
        // 确认对话框
        await ElMessageBox.confirm(
            `确定要删除这条${getTypeLabel(item.detection_type)}记录吗？此操作不可恢复。`,
            '删除记录',
            {
                confirmButtonText: '确定删除',
                cancelButtonText: '取消',
                type: 'warning',
            }
        )

        await deleteHistoryRecord(item.id)

        ElMessage.success('已成功删除记录')
            // 关闭详情对话框
            dialogVisible.value = false
            selectedItem.value = null
            fetchHistory()
        } catch (error) {
        if (error !== 'cancel') {
            console.error('删除记录失败:', error)
            ElMessage.error('删除失败: ' + error.message)
        }
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
            `确定要删除选中的 ${selectedRecords.value.length} 条历史记录吗？此操作不可恢复！`,
            '批量删除确认',
            {
                confirmButtonText: '删除',
                cancelButtonText: '取消',
                type: 'warning',
                confirmButtonClass: 'el-button--danger'
            }
        )

        const deletePromises = selectedRecords.value.map(record =>
            deleteHistoryRecord(record.id)
        )

        const results = await Promise.allSettled(deletePromises)
        const successCount = results.filter(r => r.status === 'fulfilled').length

        if (successCount > 0) {
            ElMessage.success(`成功删除 ${successCount} 条记录`)
            // 重新加载数据
            fetchHistory()
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
        'batch': '批量图片检测',
        'batch_video': '批量视频检测',
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

// ✅ 新增: 获取情绪渐变色（用于进度条）
const getEmotionGradient = (emotion) => {
    const gradients = {
        happy: ['#26DE81', '#20E3B2'],
        enjoy: ['#26DE81', '#20E3B2'],
        sad: ['#0ABDE3', '#48DBFB'],
        angry: ['#FF6348', '#FF7979'],
        surprise: ['#E056FD', '#BE2EDD'],
        surprised: ['#E056FD', '#BE2EDD'],
        fear: ['#2F3542', '#57606F'],
        fearful: ['#2F3542', '#57606F'],
        disgust: ['#FFA502', '#FFBE76'],
        disgusted: ['#FFA502', '#FFBE76'],
        neutral: ['#747D8C', '#A4B0BE'],
        calm: ['#A4B0BE', '#D1D8E0']
    }
    return gradients[emotion] || ['#747D8C', '#A4B0BE']
}

// ✅ 新增: 设置人脸 Canvas 引用
const setFaceCanvasRef = (el, index) => {
    if (el) {
        faceCanvasRefs.value[index] = el
        // 等待 DOM 更新后裁剪
        nextTick(() => {
            cropFaceThumbnail(el, index)
        })
    }
}

// ✅ 新增: 裁剪人脸缩略图
const cropFaceThumbnail = async (canvas, faceIndex) => {
    if (!selectedItem.value || !selectedItem.value.thumbnail || !selectedItem.value.detected_faces?.length) {
        return
    }

    try {
        const ctx = canvas.getContext('2d')
        if (!ctx) return

        // 加载原始缩略图
        const img = new Image()
        img.crossOrigin = 'anonymous'

        img.onload = () => {
            try {
                const face = selectedItem.value.detected_faces[faceIndex]
                const bbox = face.bbox

                if (!bbox || bbox.length < 4) return

                let [x, y, width, height] = bbox

                // ✅ 新增: 坐标验证和修正
                if (x >= img.width || y >= img.height) {
                    console.warn(`人脸 #${faceIndex + 1} 检测到旧格式坐标，尝试自适应裁剪`)
                    x = img.width * 0.3
                    y = img.height * 0.2
                    width = img.width * 0.4
                    height = img.height * 0.5
                }

                // 扩大 20% 以包含更多上下文
                const padding = 0.2
                const expandedWidth = width * (1 + padding)
                const expandedHeight = height * (1 + padding)
                const expandedX = Math.max(0, x - width * padding / 2)
                const expandedY = Math.max(0, y - height * padding / 2)

                // 确保不超出图片边界
                const finalX = Math.min(expandedX, img.width - expandedWidth)
                const finalY = Math.min(expandedY, img.height - expandedHeight)
                const finalWidth = Math.min(expandedWidth, img.width - finalX)
                const finalHeight = Math.min(expandedHeight, img.height - finalY)

                // 设置 Canvas 尺寸 (60x60)
                canvas.width = 60
                canvas.height = 60

                // 绘制裁剪后的人脸区域
                ctx.drawImage(
                    img,
                    finalX, finalY, finalWidth, finalHeight,
                    0, 0, 60, 60
                )
            } catch (error) {
                console.error('人脸裁剪失败:', error)
            }
        }

        img.onerror = () => {
            console.error('加载缩略图失败')
        }

        img.src = selectedItem.value.thumbnail
    } catch (error) {
        console.error('人脸裁剪过程出错:', error)
    }
}

// ✅ 新增: 裁剪单张人脸缩略图（用于单张人脸卡片）
const cropSingleFaceThumbnail = async () => {
    if (!selectedItem.value || !selectedItem.value.thumbnail || !selectedItem.value.detected_faces?.length) {
        return
    }

    try {
        await nextTick()

        const canvas = singleFaceCanvas.value
        if (!canvas) return

        const ctx = canvas.getContext('2d')
        if (!ctx) return

        // 加载原始缩略图
        const img = new Image()
        img.crossOrigin = 'anonymous'

        img.onload = () => {
            try {
                const face = selectedItem.value.detected_faces[0]
                const bbox = face.bbox

                if (!bbox || bbox.length < 4) return

                let [x, y, width, height] = bbox

                // ✅ 新增: 坐标验证和修正
                // 如果坐标超出缩略图范围，说明是旧数据（未转换坐标）
                // 尝试将坐标限制在缩略图范围内
                if (x >= img.width || y >= img.height) {
                    console.warn('检测到旧格式坐标，尝试自适应裁剪')
                    // 对于旧数据，直接使用缩略图中心区域
                    x = img.width * 0.3
                    y = img.height * 0.2
                    width = img.width * 0.4
                    height = img.height * 0.5
                }

                // 扩大 20% 以包含更多上下文
                const padding = 0.2
                const expandedWidth = width * (1 + padding)
                const expandedHeight = height * (1 + padding)
                const expandedX = Math.max(0, x - width * padding / 2)
                const expandedY = Math.max(0, y - height * padding / 2)

                // 确保不超出图片边界
                const finalX = Math.min(expandedX, img.width - expandedWidth)
                const finalY = Math.min(expandedY, img.height - expandedHeight)
                const finalWidth = Math.min(expandedWidth, img.width - finalX)
                const finalHeight = Math.min(expandedHeight, img.height - finalY)

                // 设置 Canvas 尺寸 (120x120)
                canvas.width = 120
                canvas.height = 120

                // 绘制裁剪后的人脸区域
                ctx.drawImage(
                    img,
                    finalX, finalY, finalWidth, finalHeight,
                    0, 0, 120, 120
                )
            } catch (error) {
                console.error('单张人脸裁剪失败:', error)
            }
        }

        img.onerror = () => {
            console.error('加载缩略图失败')
        }

        img.src = selectedItem.value.thumbnail
    } catch (error) {
        console.error('单张人脸裁剪过程出错:', error)
    }
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
    ElMessage.success('已导出')
}

// ✅ 新增: 打开记录反馈
const openFeedback = (record) => {
    feedbackForm.value = {
        recordId: record.id,
        faceIndex: null,
        predictedEmotion: record.emotion || record.dominant_emotion || '',  // ✅ 填充预测情绪
        correctEmotion: '',
        comment: '',
        snapshot: record.thumbnail || ''  // ✅ 保存快照图片
    }
    feedbackDialogVisible.value = true
}

// ✅ 新增: 打开单个人脸反馈
const openFaceFeedback = (face, index) => {
    feedbackForm.value = {
        recordId: selectedItem.value?.id,
        faceIndex: index,
        predictedEmotion: face.emotion || '',  // ✅ 填充预测情绪
        correctEmotion: '',
        comment: `人脸 #${index + 1} 的识别结果可能需要纠正`,
        snapshot: selectedItem.value?.thumbnail || ''  // ✅ 保存快照图片
    }
    feedbackDialogVisible.value = true
}

// ✅ 新增: 提交反馈
const handleSubmitFeedback = async () => {
    if (!feedbackForm.value.correctEmotion) {
        ElMessage.warning('请选择正确的情绪')
        return
    }

    feedbackSubmitting.value = true
    try {
        await submitFeedback({
            emotion: feedbackForm.value.predictedEmotion,
            predicted_emotion: feedbackForm.value.predictedEmotion,
            correct_emotion: feedbackForm.value.correctEmotion,
            feedback_type: 'incorrect',
            notes: feedbackForm.value.comment || '',
            confidence: selectedItem.value?.confidence,
            bbox: selectedItem.value?.bbox,
            snapshot: feedbackForm.value.snapshot || '',
            timestamp: Date.now()
        })

        ElMessage.success('反馈已提交，感谢您的帮助！')
        feedbackDialogVisible.value = false

        // 刷新历史记录列表
        fetchHistory()
    } catch (error) {
        console.error('提交反馈错误:', error)
        ElMessage.error(`提交失败: ${error.message}`)
    } finally {
        feedbackSubmitting.value = false
    }
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
    fontWeight: '100',
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

// ✅ 新增: 监听 selectedItem 变化，重新裁剪人脸
watch(selectedItem, (newVal) => {
    if (newVal) {
        nextTick(() => {
            // ✅ 优化: 如果是单张人脸，裁剪单张人脸 Canvas
            if (newVal.detected_faces?.length === 1) {
                cropSingleFaceThumbnail()
            }
        })
    }
})
</script>

<style scoped>
.history-viewer {
    height: 100%;
    /* overflow: hidden;  */
    /* padding: 20px; */
    animation: fadeIn 0.3s ease;
    display: flex;
    flex-direction: column;
    gap: 16px;
    /* ✅ 修复: 移除固定高度，使用 Flex 布局自适应 */
    overflow: hidden;
    /* ✅ 优化: 确保容器高度正确 */
}

.history-header {
    margin-bottom: 24px;
    text-align: center;
}

.history-header h2 {
    font-size: 22px;
    font-weight: 100;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    color: var(--text);
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
    grid-template-columns: repeat(6, 1fr);
    gap: 12px;
    margin-bottom: 16px;
    margin-top: 2px;
    flex-shrink: 0;
    /* ✅ 优化: 自适应高度，避免多余空白 */
    min-height: auto;
}

.filter-card {
    background: var(--card-bg);
    backdrop-filter: blur(16px);
    border: 1.5px solid var(--border);
    border-radius: var(--radius-lg);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
    cursor: pointer;
    position: relative;
}

.filter-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    transition: left 0.5s ease;
}

.filter-card:hover::before {
    left: 100%;
}

.filter-card:hover {
    border-color: var(--primary-light);
    box-shadow: 0 8px 32px rgba(113, 57, 255, 0.15);
    transform: translateY(-3px) scale(1.02);
}

.filter-card.active {
    border-color: var(--primary);
    box-shadow: 
        0 0 0 1px var(--primary),
        0 0 30px rgba(113, 57, 255, 0.35),
        inset 0 0 20px rgba(113, 57, 255, 0.05);
    animation: cardPulse 2s ease-in-out infinite;
}

@keyframes cardPulse {
    0%, 100% {
        box-shadow: 
            0 0 0 1px var(--primary),
            0 0 30px rgba(113, 57, 255, 0.35),
            inset 0 0 20px rgba(113, 57, 255, 0.05);
    }
    50% {
        box-shadow: 
            0 0 0 1px var(--primary),
            0 0 45px rgba(113, 57, 255, 0.5),
            inset 0 0 30px rgba(113, 57, 255, 0.08);
    }
}



.filter-card-inner {
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.filter-icon-wrap {
    width: 42px;
    height: 42px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.filter-card:hover .filter-icon-wrap {
    transform: scale(1.1) rotate(5deg);
}

.filter-card.active .filter-icon-wrap {
    animation: iconBounce 1s ease-in-out infinite;
}

@keyframes iconBounce {
    0%, 100% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.08);
    }
}

.filter-info {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.filter-label {
    font-size: 13px;
    font-weight: 500;
    color: var(--text);
    transition: color 0.3s ease;
}

.filter-card:hover .filter-label {
    color: var(--primary-light);
}

.filter-count {
    font-size: 12px;
    color: var(--text-secondary);
    font-weight: 600;
    font-family: 'Consolas', 'Monaco', monospace;
    transition: all 0.3s ease;
}

.filter-card:hover .filter-count {
    color: var(--text);
    transform: translateX(4px);
}

.filter-card.active .filter-label {
    color: var(--primary);
}

.filter-card.active .filter-count {
    color: var(--primary-light);
    animation: countPulse 1.5s ease-in-out infinite;
}

@keyframes countPulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.7;
    }
}

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    /* ✅ 优化: 减小最小高度，避免大片空白 */
    min-height: 300px;
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
    min-height: 0;
    /* ✅ 修复: 允许 flex 子元素收缩 */
    /* ✅ 优化: 动态高度，根据内容调整 */
    min-height: 300px;
    max-height: calc(100vh - 200px);
}

/* ✅ 新增: 表格容器滚动条样式 */
.history-table-container :deep(.el-table__body-wrapper)::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

.history-table-container :deep(.el-table__body-wrapper)::-webkit-scrollbar-thumb {
    background: rgba(146, 78, 255, 0.3);
    border-radius: 3px;
}

.history-table-container :deep(.el-table__body-wrapper)::-webkit-scrollbar-thumb:hover {
    background: rgba(146, 78, 255, 0.5);
}

/* ✅ 新增: 序号样式 */
.index-number {
    font-size: 13px;
    font-weight: 100;
    color: var(--text-secondary);
    font-family: 'Consolas', 'Monaco', monospace;
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
    position: relative;
    /* ✅ 新增: 用于定位人脸数量标记 */
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

/* ✅ 新增: 人脸数量标记样式 */
.face-count-badge {
    position: absolute;
    bottom: 2px;
    right: 2px;
    background: rgba(113, 57, 255, 0.9);
    color: var(--text);
    font-size: 10px;
    font-weight: 100;
    padding: 1px 4px;
    border-radius: 6px;
    min-width: 14px;
    text-align: center;
    line-height: 1.2;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

/* 类型徽章 */
.type-badge {
    padding: 4px 10px;
    background: rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(8px);
    border: 1px solid color-mix(in srgb, var(--border) 20%, transparent);
    border-radius: 6px;
    font-size: 12px;
    font-weight: 100;
    color: var(--text);
    display: inline-block;
    white-space: nowrap;
    transition: all 0.2s ease;
}

.type-badge:hover {
    background: rgba(0, 0, 0, 0.6);
    border-color: color-mix(in srgb, var(--border) 40%, transparent);
}

/* 情绪徽章 */
.emotion-badge-table {
    margin-top: 2px;
    padding: 4px 12px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 100;
    color: var(--text);
    display: inline-flex;
    align-items: center;
    gap: 4px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
    border: 1px solid color-mix(in srgb, var(--border) 30%, transparent);
    transition: all 0.2s ease;
}

.emotion-badge-table:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.35);
}

/* 置信度 */
.confidence-table {
    font-size: 14px;
    font-weight: 100;
    color: var(--highlight);
    font-family: 'Consolas', 'Monaco', monospace;
    letter-spacing: 0.5px;
}

/* 人脸数量 */
.face-count-table {
    font-size: 13px;
    font-weight: 100;
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
    margin-top: 2px;
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

/* ✅ 新增: 删除按钮样式 */
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

/* ✅ 详情按钮样式 - 玻璃拟态 */
.detail-btn {
    background: transparent !important;
    border: 1.5px solid var(--border) !important;
    color: var(--text) !important;
    backdrop-filter: blur(8px) !important;
    padding: 6px 12px !important;
}

.detail-btn:hover {
    background: color-mix(in srgb, var(--primary) 12%, transparent) !important;
    border-color: var(--primary-light) !important;
    color: var(--text) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(113, 57, 255, 0.15) !important;
}

.detail-btn:active {
    transform: translateY(0) scale(0.98) !important;
}

/* ✅ 删除按钮样式 - 玻璃拟态 */
.delete-btn {
    background: transparent !important;
    border: 1.5px solid var(--danger) !important;
    color: var(--danger) !important;
    backdrop-filter: blur(8px) !important;
    padding: 6px 12px !important;
}

.delete-btn:hover {
    background: rgba(245, 108, 108, 0.15) !important;
    border-color: var(--danger) !important;
    color: var(--danger) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(245, 108, 108, 0.2) !important;
}

.delete-btn:active {
    transform: translateY(0) scale(0.98) !important;
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

/* Element Plus 表格深度样式定制 */
:deep(.el-table) {
    background: transparent;
    --el-table-border-color: var(--border);
    --el-table-header-bg-color: transparent;
    --el-table-tr-bg-color: transparent;
    --el-table-expanded-cell-bg-color: transparent;
}

:deep(.el-table th.el-table__cell) {
    background: transparent !important;
    border-bottom: 2px solid color-mix(in srgb, var(--primary) 20%, transparent) !important;
    /* font-weight: 600 !important; */
}

:deep(.el-table td.el-table__cell) {
    border-bottom: 1px solid color-mix(in srgb, var(--border) 40%, transparent) !important;
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

/* 分页组件深色主题 */
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

/* 对话框样式 - 玻璃拟态 */
:deep(.history-detail-dialog) {
    .el-dialog {
        background: var(--card-bg) !important;
        backdrop-filter: blur(20px);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-xl);
        margin-top: 1vh !important;
        /* 向上移动弹窗,更靠近顶部 */
        max-height: 90vh !important;
    }

    .el-dialog__header {
        /* ✅ 彻底隐藏header,移除空白区域 */
        display: none !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
    }

    /* ✅ 移除body内边距,允许内容自然延伸 */
    .el-dialog__body {
        padding: 0 !important;
        overflow: visible !important;
        max-height: none !important;
    }

    .el-dialog__footer {
        border-top: 1px solid var(--border);
        padding: 16px 24px;
    }
}

/* ✅ 新增: 最小化对话框header样式 */
.dialog-header-minimal {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
}

.dialog-title-text {
    font-size: 18px;
    font-weight: 100;
    color: var(--text);
}

/* ✅ 关闭按钮样式 */
.dialog-close-btn {
    width: 32px;
    height: 32px;
    padding: 0;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
}

.dialog-close-btn:hover {
    background: rgba(255, 77, 77, 0.2);
    border-color: rgba(255, 77, 77, 0.4);
    color: #ff4d4d;
    transform: rotate(90deg);
}

.dialog-close-btn .el-icon {
    font-size: 18px;
}

.dialog-header {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.dialog-title {
    font-size: 18px;
    font-weight: 100;
    color: var(--text);
}

.dialog-subtitle {
    font-size: 13px;
    color: var(--text-secondary);
    opacity: 0.7;
}

/* 详情内容布局 */
.detail-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    max-height: 75vh;
    overflow-y: auto;
    overflow-x: hidden;
}

/* ✅ 多人脸场景: 简化为单列布局 */
.detail-content.multi-face-mode {
    grid-template-columns: 1fr;
}

/* 玻璃拟态面板 */
.glass-panel {
    background: var(--card-bg);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 20px;
    box-shadow: var(--shadow-md);
    transition: all 0.3s ease;
}

.glass-panel:hover {
    border-color: color-mix(in srgb, var(--primary) 30%, transparent);
    box-shadow: var(--shadow-lg);
}

.detail-left {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

/* ✅ 新增: 左侧区域滚动条优化 */
.detail-left::-webkit-scrollbar {
    width: 6px;
}

.detail-left::-webkit-scrollbar-thumb {
    background: rgba(146, 78, 255, 0.3);
    border-radius: 3px;
}

.detail-left::-webkit-scrollbar-thumb:hover {
    background: rgba(146, 78, 255, 0.5);
}

.detail-left::-webkit-scrollbar-track {
    background: transparent;
}

.image-preview {
    width: 100%;
    height: 280px;
    border-radius: var(--radius-md);
    overflow: hidden;
    background: color-mix(in srgb, var(--card-bg) 60%, transparent);
    border: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
    /* ✅ 修复: 使用flexbox居中显示Canvas */
    display: flex;
    align-items: center;
    justify-content: center;
}

.image-preview img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}

/* ✅ 新增: Canvas 裁剪图片样式 */
.face-crop-canvas {
    /* ✅ 修复: 不使用 100% 宽高，让Canvas保持内部尺寸 */
    display: block;
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    border-radius: var(--radius-md);
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

/* ✅ 新增: 预览操作按钮 */
.preview-actions {
    display: flex;
    gap: 12px;
}

.action-btn {
    flex: 1;
    padding: 10px 16px;
    border-radius: var(--radius-sm);
    font-size: 13px;
    font-weight: 500;
    transition: all 0.2s ease;
}

.feedback-btn {
    background: rgba(230, 162, 60, 0.15);
    border: 1px solid rgba(230, 162, 60, 0.3);
    color: var(--warning);
}

.feedback-btn:hover {
    background: rgba(230, 162, 60, 0.25);
    border-color: var(--warning);
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(230, 162, 60, 0.3);
}

.export-btn {
    background: rgba(113, 57, 255, 0.15);
    border: 1px solid rgba(113, 57, 255, 0.3);
    color: var(--primary-light);
}

.export-btn:hover {
    background: rgba(113, 57, 255, 0.25);
    border-color: var(--primary-light);
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(113, 57, 255, 0.3);
}

.detail-right {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

/* ===== 重新设计的布局样式 ===== */
/* ✅ 新增: 主内容区域 - 左右分栏布局 */
.detail-content-redesign {
    display: grid;
    grid-template-columns: 320px 1fr;
    gap: 24px;
    /* ✅ 移除max-height限制,允许内容自然延伸 */
    max-height: none !important;
    overflow: visible !important;
}

/* ✅ 左侧: 固定宽度 */
.detail-left-redesign {
    display: flex;
    flex-direction: column;
    gap: 16px;
    /* ✅ 左侧固定,不滚动 */
}

/* ✅ 标题区域 */
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

/* ✅ 图片预览区域 */
.image-preview-redesign {
    width: 100%;
    /* ✅ 自适应高度,根据图片比例 */
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

.image-preview-redesign img {
    width: 100%;
    height: auto;
    max-height: 400px;
    object-fit: contain;
}

/* ✅ 新增: 预览图片样式 */
.preview-image-redesign {
    width: 100%;
    height: auto;
    max-height: 400px;
    object-fit: contain;
    border-radius: var(--radius-md);
}

/* ✅ Canvas 裁剪图片样式 */
.face-crop-canvas-redesign {
    display: block;
    max-width: 100%;
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
    background: linear-gradient(135deg, color-mix(in srgb, var(--primary) 15%, transparent),
            color-mix(in srgb, var(--accent) 15%, transparent));
}

.large-emoji-redesign {
    font-size: 72px;
    filter: drop-shadow(0 0 30px rgba(113, 57, 255, 0.4));
}

.preview-placeholder-redesign p {
    font-size: 14px;
    color: var(--text-secondary);
}

/* ✅ 操作按钮区域 */
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

.export-btn-redesign {
    background: rgba(113, 57, 255, 0.15);
    border: 1px solid rgba(113, 57, 255, 0.3);
    color: var(--primary-light);
}

.export-btn-redesign:hover {
    background: rgba(113, 57, 255, 0.25);
    border-color: var(--primary-light);
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(113, 57, 255, 0.3);
}

/* ✅ 关闭按钮样式 */
.close-btn-redesign {
    background: rgba(255, 77, 77, 0.15);
    border: 1px solid rgba(255, 77, 77, 0.3);
    color: #ff6b6b;
}

.close-btn-redesign:hover {
    background: rgba(255, 77, 77, 0.25);
    border-color: #ff4d4d;
    color: #ff4d4d;
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(255, 77, 77, 0.3);
}

/* ✅ 右侧: 自适应宽度 */
.detail-right-redesign {
    display: flex;
    flex-direction: column;
    gap: 16px;
    /* ✅ 允许内容自然延伸 */
    min-height: 400px;
}

/* ✅ 修复: 人脸表格容器 - 限制高度并允许滚动 */
.faces-table-container-redesign {
    padding: 20px;
    background: var(--card-bg);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
    /* ✅ 修复: 设置最大高度,防止溢出对话框 */
    max-height: 60vh;
    overflow: hidden;
    display: flex;
    /* flex-direction: column; */
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

/* ✅ 修复: 表格样式 - 允许滚动 */
.faces-table-redesign {
    background: transparent !important;
    flex: 1;
    min-height: 0;
}

.faces-table-redesign :deep(.el-table) {
    /* ✅ 修复: 设置最大高度并启用滚动 */
    max-height: calc(60vh - 100px);
    overflow: hidden;
}

.faces-table-redesign :deep(.el-table__body-wrapper) {
    overflow-y: auto !important;
    overflow-x: hidden !important;
    max-height: calc(60vh - 100px) !important;
}

/* ✅ 表格滚动条样式 */
.faces-table-redesign :deep(.el-table__body-wrapper)::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

.faces-table-redesign :deep(.el-table__body-wrapper)::-webkit-scrollbar-thumb {
    background: rgba(146, 78, 255, 0.3);
    border-radius: 3px;
}

.faces-table-redesign :deep(.el-table__body-wrapper)::-webkit-scrollbar-thumb:hover {
    background: rgba(146, 78, 255, 0.5);
}

.faces-table-redesign :deep(.el-table__body-wrapper)::-webkit-scrollbar-track {
    background: transparent;
}

/* ✅ 人脸预览缩略图 */
.face-thumbnail-redesign {
    width: 60px;
    height: 60px;
    border-radius: var(--radius-sm);
    overflow: hidden;
    background: var(--card-bg);
    border: 1px solid var(--border);
}

.face-mini-canvas-redesign {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

/* ✅ 序号样式 */
.face-index-redesign {
    font-size: 14px;
    font-weight: 100;
    color: var(--primary-light);
}

/* ✅ 情绪徽章 */
.emotion-badge-small-redesign {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
    color: #fff;
}

/* ✅ 置信度单元格 */
.confidence-cell-redesign {
    width: 100%;
}

/* ✅ 坐标文本 */
.bbox-text-redesign {
    font-size: 12px;
    font-family: 'Courier New', monospace;
    color: var(--text-secondary);
}

/* ✅ 反馈按钮 */
.face-feedback-btn-redesign {
    color: var(--primary-light) !important;
}

.face-feedback-btn-redesign:hover {
    color: var(--accent) !important;
}

/* 信息卡片 */
.info-card {
    padding: 20px;
    background: var(--card-bg);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
}

/* ✅ 重构: 人脸表格容器 */
.faces-table-container {
    padding: 20px;
    background: var(--card-bg);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
}

/* ✅ 新增: 自动高度版本(多人脸场景) */
.faces-table-container.glass-panel-auto {
    max-height: none !important;
    overflow: visible !important;
}

/* ✅ 重构: 单人脸紧凑布局 */
.single-face-card.compact-layout {
    padding: 16px;
    background: var(--card-bg);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
}

/* 紧凑情绪头部 */
.compact-emotion-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
}

.compact-confidence {
    font-size: 18px;
    font-weight: 700;
    background: linear-gradient(135deg, var(--primary-light), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* 紧凑进度条 */
.compact-progress {
    margin-bottom: 16px;
}

/* 紧凑信息网格 */
.compact-info-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 16px;
}

.compact-info-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 8px 10px;
    background: rgba(113, 57, 255, 0.05);
    border: 1px solid rgba(113, 57, 255, 0.1);
    border-radius: 8px;
}

.compact-label {
    font-size: 11px;
    color: var(--text-secondary);
    font-weight: 500;
    opacity: 0.7;
}

.compact-value {
    font-size: 13px;
    color: var(--text);
    font-weight: 500;
}

.compact-value.bbox-inline {
    font-family: 'Courier New', 'Consolas', monospace;
    font-size: 11px;
    color: var(--primary-light);
}

/* 紧凑情绪分布 */
.compact-emotion-dist {
    margin-bottom: 16px;
}

.compact-section-label {
    font-size: 12px;
    color: var(--text-secondary);
    font-weight: 500;
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.compact-emotion-bars {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.compact-emotion-bar {
    display: flex;
    align-items: center;
    gap: 10px;
}

.compact-emotion-name {
    font-size: 11px;
    color: var(--text-secondary);
    min-width: 70px;
    font-weight: 500;
}

.compact-bar-progress {
    flex: 1;
}

/* 紧凑操作按钮 */
.compact-action {
    padding-top: 12px;
    border-top: 1px solid var(--border);
}

.compact-feedback-btn {
    width: 100%;
    padding: 10px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 100;
    background: linear-gradient(135deg, rgba(230, 162, 60, 0.2), rgba(230, 162, 60, 0.1));
    border: 1px solid rgba(230, 162, 60, 0.4);
    color: var(--warning);
    transition: all 0.3s ease;
}

.compact-feedback-btn:hover {
    background: linear-gradient(135deg, rgba(230, 162, 60, 0.3), rgba(230, 162, 60, 0.2));
    border-color: var(--warning);
    transform: translateY(-1px);
    box-shadow: 0 3px 10px rgba(230, 162, 60, 0.3);
}

/* 单张人脸内容布局 */
.single-face-content {
    display: grid;
    grid-template-columns: 140px 1fr;
    gap: 24px;
    align-items: start;
    margin-top: 16px;
}

/* 单张人脸预览 */
.single-face-preview {
    display: flex;
    justify-content: center;
}

.face-thumbnail-large {
    width: 160px;
    height: 160px;
    border-radius: 16px;
    overflow: hidden;
    position: relative;
    background: linear-gradient(135deg,
            color-mix(in srgb, var(--primary) 15%, transparent),
            color-mix(in srgb, var(--accent) 15%, transparent));
    border: 2px solid rgba(113, 57, 255, 0.3);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
}

.face-thumbnail-large:hover {
    transform: scale(1.05);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
}

.face-large-canvas {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

/* ✅ 新增: 情绪覆盖层 */
.emotion-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 8px;
    display: flex;
    justify-content: center;
    align-items: center;
    background: linear-gradient(to top, rgba(0, 0, 0, 0.6), transparent);
}

.overlay-emoji {
    font-size: 32px;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

/* ✅ 新增: 单张人脸详细信息 */
.single-face-info {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

/* ✅ 新增: 详细信息分区 */
.face-detail-section {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.detail-label {
    font-size: 12px;
    color: var(--text-secondary);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.detail-value-large {
    display: flex;
    align-items: center;
}

/* ✅ 新增: 置信度显示 */
.confidence-display {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.confidence-value {
    font-size: 24px;
    font-weight: 700;
    background: linear-gradient(135deg, var(--primary-light), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.detail-progress {
    width: 100%;
}

/* ✅ 新增: 坐标显示 */
.bbox-display {
    padding: 8px 12px;
    background: rgba(113, 57, 255, 0.08);
    border: 1px solid rgba(113, 57, 255, 0.2);
    border-radius: 8px;
    font-family: 'Courier New', 'Consolas', monospace;
}

.bbox-value {
    font-size: 13px;
    color: var(--primary-light);
    font-weight: 100;
    letter-spacing: 0.5px;
}

/* ✅ 新增: 情绪分布 */
.emotion-distribution {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.emotion-bar-item {
    display: flex;
    align-items: center;
    gap: 12px;
}

.emotion-name {
    font-size: 12px;
    color: var(--text-secondary);
    min-width: 80px;
    font-weight: 500;
}

.emotion-bar-progress {
    flex: 1;
}

/* 单张人脸操作按钮 */
.single-face-action {
    margin-top: 12px;
    padding-top: 16px;
    border-top: 1px solid var(--border);
}

.face-feedback-btn-large {
    width: 100%;
    padding: 12px 20px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 100;
    background: linear-gradient(135deg, rgba(230, 162, 60, 0.2), rgba(230, 162, 60, 0.1));
    border: 1px solid rgba(230, 162, 60, 0.4);
    color: var(--warning);
    transition: all 0.3s ease;
}

.face-feedback-btn-large:hover {
    background: linear-gradient(135deg, rgba(230, 162, 60, 0.3), rgba(230, 162, 60, 0.2));
    border-color: var(--warning);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(230, 162, 60, 0.4);
}

.section-title {
    font-size: 15px;
    font-weight: 100;
    margin: 0 0 16px;
    color: var(--text);
    display: flex;
    align-items: center;
    gap: 8px;
}

.section-title .el-icon {
    color: var(--primary);
}

/* 信息网格 */
.info-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}

.info-item {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.info-item.full-width {
    grid-column: 1 / -1;
}

.info-label {
    font-size: 12px;
    color: var(--text-secondary);
    opacity: 0.7;
    font-weight: 500;
}

.info-value {
    font-size: 14px;
    color: var(--text);
    font-weight: 500;
}

.info-value.highlight {
    color: var(--primary-light);
    font-weight: 100;
}

/* 大型情绪徽章 */
.emotion-badge-large {
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 15px;
    font-weight: 100;
    color: var(--text);
    display: inline-flex;
    align-items: center;
    gap: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    border: 1px solid color-mix(in srgb, var(--border) 30%, transparent);
}

.confidence-inline {
    font-size: 13px;
    opacity: 0.8;
    font-weight: 500;
}


/* ✅ 重构: 人脸表格样式 */
.faces-table {
    background: transparent !important;
    margin-top: 12px;
}

/* ✅ 新增: 表格自动高度,移除max-height限制 */
.faces-table :deep(.el-table) {
    max-height: none !important;
}

/* ✅ 优化: 表格滚动条样式 */
.faces-table :deep(.el-table__body-wrapper)::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

.faces-table :deep(.el-table__body-wrapper)::-webkit-scrollbar-thumb {
    background: rgba(146, 78, 255, 0.3);
    border-radius: 3px;
}

.faces-table :deep(.el-table__body-wrapper)::-webkit-scrollbar-thumb:hover {
    background: rgba(146, 78, 255, 0.5);
}

.faces-table :deep(.el-table__body-wrapper)::-webkit-scrollbar-track {
    background: transparent;
}

/* 人脸缩略图 */
.face-thumbnail {
    width: 50px;
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
}

.face-mini-canvas {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

/* 人脸序号 */
.face-index {
    font-size: 13px;
    font-weight: 100;
    color: var(--primary-light);
    font-family: 'Consolas', 'Monaco', monospace;
}

/* 小型情绪徽章 */
.emotion-badge-small {
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 100;
    color: var(--text);
    display: inline-flex;
    align-items: center;
    gap: 4px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
    border: 1px solid color-mix(in srgb, var(--border) 20%, transparent);
}

/* 置信度单元格 */
.confidence-cell {
    padding: 0 8px;
}

/* 坐标文本 */
.bbox-text {
    font-size: 11px;
    color: var(--text-secondary);
    font-family: 'Courier New', 'Consolas', monospace;
    letter-spacing: 0.5px;
}

/* 人脸反馈按钮 */
.face-feedback-btn {
    color: var(--warning);
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 12px;
    transition: all 0.2s ease;
}

.face-feedback-btn:hover {
    background: rgba(230, 162, 60, 0.15);
    color: var(--warning);
    transform: translateY(-1px);
}

/* 表格行样式 */
:deep(.face-table-row-even) {
    background: color-mix(in srgb, var(--card-bg) 70%, transparent);
}

:deep(.face-table-row-odd) {
    background: color-mix(in srgb, var(--card-bg) 85%, transparent);
}

:deep(.el-table__row:hover) {
    background: color-mix(in srgb, var(--primary) 8%, transparent) !important;
}

/* ✅ 新增: 反馈对话框样式 */
:deep(.feedback-dialog) {
    .el-dialog {
        background: var(--card-bg) !important;
        backdrop-filter: blur(20px);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
    }

    .el-dialog__header {
        border-bottom: 1px solid var(--border);
        padding: 16px 20px;
    }

    .el-dialog__body {
        padding: 20px;
    }
}

.feedback-form {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.feedback-info {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 14px;
    background: color-mix(in srgb, var(--primary) 10%, transparent);
    border: 1px solid color-mix(in srgb, var(--primary) 20%, transparent);
    border-radius: var(--radius-sm);
}

.feedback-label {
    font-size: 12px;
    color: var(--text-secondary);
    font-weight: 500;
}

.feedback-value {
    font-size: 13px;
    color: var(--text);
    font-weight: 100;
    font-family: 'Consolas', 'Monaco', monospace;
}

/* 表单样式 */
:deep(.el-form-item__label) {
    color: var(--text) !important;
    font-weight: 500;
}

:deep(.el-select) {
    --el-select-border-color-hover: var(--primary);
    --el-select-input-color: var(--text);
}

:deep(.el-textarea__inner) {
    background: color-mix(in srgb, var(--card-bg) 70%, transparent) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
}

:deep(.el-textarea__inner:focus) {
    border-color: var(--primary) !important;
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
    color: var(--text) !important;
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

/* ✅ 新增: 骨架屏样式 */
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
