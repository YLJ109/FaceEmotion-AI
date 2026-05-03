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
                highlight-current-row>
                <!-- 缩略图/情绪图标列 -->
                <el-table-column label="预览" width="100" align="center">
                    <template #default="{ row }">
                        <div class="table-thumbnail">
                            <!-- ✅ 优化: 根据检测类型决定显示内容 -->
                            <!-- 视频检测: 显示情绪图标（因为视频检测保存的是情绪缩略图） -->
                            <div v-if="row.detection_type === 'video'" class="thumbnail-placeholder-small">
                                <span class="placeholder-emoji-small">{{ getEmotionEmoji(row.dominant_emotion) }}</span>
                            </div>
                            <!-- 图片/批量检测: 显示原始图片缩略图 -->
                            <img v-else-if="row.thumbnail" :src="row.thumbnail" alt="缩略图" />
                            <!-- 无缩略图: 显示情绪图标 -->
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
                        <!-- ✅ 优化: 智能裁剪显示人脸区域 -->
                        <canvas v-if="selectedItem.thumbnail && selectedItem.detected_faces?.length > 0"
                            ref="faceCropCanvas" class="face-crop-canvas"></canvas>
                        <!-- 原始缩略图（无 bbox 数据时显示） -->
                        <img v-else-if="selectedItem.thumbnail" :src="selectedItem.thumbnail" alt="检测图片" />
                        <!-- 无图片时显示情绪图标 -->
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
                                class="face-detail-card">
                                <!-- 头部：序号 + 情绪图标 + 情绪名称 + 置信度 -->
                                <div class="face-card-header">
                                    <div class="face-title-row">
                                        <span class="face-index-badge">人脸 {{ index + 1 }}</span>
                                        <span class="face-emotion-display">
                                            <span class="emotion-emoji">{{ getEmotionEmoji(face.emotion) }}</span>
                                            <span class="emotion-name">{{ getEmotionName(face.emotion) }}</span>
                                        </span>
                                    </div>
                                    <span class="face-confidence-badge"
                                        :style="{ color: getEmotionColor(face.emotion) }">
                                        {{ ((face.confidence || 0) * 100).toFixed(1) }}%
                                    </span>
                                </div>

                                <!-- 中部：置信度进度条 -->
                                <div class="face-progress-section">
                                    <el-progress
                                        :percentage="clampPercentage(parseFloat(((face.confidence || 0) * 100).toFixed(1)))"
                                        :color="getEmotionGradient(face.emotion)" :stroke-width="10"
                                        :show-text="false" />
                                </div>

                                <!-- 底部：BBox 坐标 -->
                                <div class="face-bbox-info">
                                    <span class="bbox-label">BBox:</span>
                                    <span class="bbox-coords">[{{face.bbox?.map(c => Math.round(c)).join(', ')
                                    }}]</span>
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
import { ref, onMounted, nextTick, watch } from 'vue'
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
const faceCropCanvas = ref(null) // ✅ 新增: 人脸裁剪 Canvas 引用
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

    // ✅ 新增: 打开详情时自动裁剪人脸
    nextTick(() => {
        cropAndDisplayFace()
    })
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

// ✅ 新增: 智能裁剪并显示人脸区域
const cropAndDisplayFace = async () => {
    if (!selectedItem.value || !selectedItem.value.thumbnail || !selectedItem.value.detected_faces?.length) {
        return
    }

    try {
        await nextTick() // 等待 DOM 更新

        const canvas = faceCropCanvas.value
        if (!canvas) {
            console.warn('Canvas 元素未找到')
            return
        }

        const ctx = canvas.getContext('2d')
        if (!ctx) {
            console.warn('无法获取 Canvas 上下文')
            return
        }

        // 加载原始缩略图
        const img = new Image()
        img.crossOrigin = 'anonymous' // 处理跨域问题

        img.onload = () => {
            try {
                // 获取第一张人脸的 bbox: [x, y, width, height]
                const firstFace = selectedItem.value.detected_faces[0]
                const bbox = firstFace.bbox

                if (!bbox || bbox.length < 4) {
                    console.warn('bbox 数据无效')
                    return
                }

                const [x, y, width, height] = bbox

                // 计算裁剪区域（扩大 20% 以包含更多上下文）
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

                // 设置 Canvas 尺寸（保持宽高比，最大 400x300）
                const maxWidth = 400
                const maxHeight = 300
                const aspectRatio = finalWidth / finalHeight

                let canvasWidth, canvasHeight
                if (aspectRatio > maxWidth / maxHeight) {
                    canvasWidth = maxWidth
                    canvasHeight = maxWidth / aspectRatio
                } else {
                    canvasHeight = maxHeight
                    canvasWidth = maxHeight * aspectRatio
                }

                canvas.width = canvasWidth
                canvas.height = canvasHeight

                // 绘制裁剪后的人脸区域
                ctx.drawImage(
                    img,
                    finalX, finalY, finalWidth, finalHeight, // 源图片裁剪区域
                    0, 0, canvasWidth, canvasHeight // Canvas 绘制区域
                )

                console.log('✅ 人脸裁剪成功:', { bbox, canvasSize: { width: canvasWidth, height: canvasHeight } })
            } catch (error) {
                console.error('人脸裁剪失败:', error)
                // fallback: 显示完整图片
                canvas.style.display = 'none'
            }
        }

        img.onerror = () => {
            console.error('加载缩略图失败')
            canvas.style.display = 'none'
        }

        img.src = selectedItem.value.thumbnail
    } catch (error) {
        console.error('人脸裁剪过程出错:', error)
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

// ✅ 新增: 监听 selectedItem 变化，重新裁剪人脸
watch(selectedItem, (newVal) => {
    if (newVal) {
        nextTick(() => {
            cropAndDisplayFace()
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
    grid-template-columns: repeat(5, 1fr);
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
    /* font-weight: 600; */
    color: var(--text);
    margin-bottom: 2px;
}

.filter-count {
    font-size: 18px;
    font-weight: 100;
    color: var(--primary-light);
    font-family: 'Consolas', 'Monaco', monospace;
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
    /* font-weight: 600; */
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
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 13px;
    /* font-weight: 600; */
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
    /* font-weight: 600; */
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

/* 详情对话框样式 */
.detail-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    /* ✅ 修复: 移除 max-height 和 overflow-y，让对话框自身管理滚动 */
    max-height: none;
    overflow-y: visible;
}

.detail-left {
    display: flex;
    flex-direction: column;
}

.image-preview {
    width: 100%;
    /* ✅ 优化: 减小固定高度，更紧凑 */
    height: 280px;
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

/* ✅ 新增: Canvas 裁剪图片样式 */
.face-crop-canvas {
    width: 100%;
    height: 100%;
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

.detail-right {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.detail-section h4 {
    font-size: 17px;
    font-weight: 100;
    margin-bottom: 12px;
    color: var(--text);
}

/* 修复 el-descriptions 白色背景问题 */
:deep(.el-descriptions) {
    background: transparent !important;
    --el-descriptions-item-bordered-bg: color-mix(in srgb, var(--card-bg) 85%, transparent) !important;
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
    background: color-mix(in srgb, var(--card-bg) 85%, transparent) !important;
    color: var(--text-secondary) !important;
    border: 1px solid color-mix(in srgb, var(--border) 40%, transparent) !important;
    font-weight: 600 !important;
    padding: 10px 12px !important;
}

:deep(.el-descriptions__content) {
    background: color-mix(in srgb, var(--card-bg) 70%, transparent) !important;
    color: var(--text) !important;
    border: 1px solid color-mix(in srgb, var(--border) 40%, transparent) !important;
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
    font-weight: 100;
    color: var(--text);
    display: inline-flex;
    align-items: center;
    gap: 6px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.faces-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
    /* ✅ 优化: 适当增加最大高度，支持 3-4 个人脸卡片 */
    max-height: 300px;
    overflow-y: auto;
    padding-right: 4px;
}

/* ✅ 新增: 人脸列表滚动条样式 */
.faces-list::-webkit-scrollbar {
    width: 6px;
}

.faces-list::-webkit-scrollbar-thumb {
    background: rgba(146, 78, 255, 0.3);
    border-radius: 3px;
    transition: all 0.3s ease;
}

.faces-list::-webkit-scrollbar-thumb:hover {
    background: rgba(146, 78, 255, 0.5);
}

/* ✅ 重构: 人脸卡片容器 */
.face-detail-card {
    padding: 14px;
    background: color-mix(in srgb, var(--card-bg) 70%, transparent);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    transition: all 0.25s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.face-detail-card:hover {
    border-color: color-mix(in srgb, var(--primary) 40%, transparent);
    box-shadow: 0 4px 12px rgba(146, 78, 255, 0.15);
    transform: translateY(-1px);
}

/* ✅ 新增: 卡片头部 */
.face-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.face-title-row {
    display: flex;
    align-items: center;
    gap: 10px;
    flex: 1;
}

/* 人脸序号标签 */
.face-index-badge {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-secondary);
    background: color-mix(in srgb, var(--primary) 15%, transparent);
    padding: 4px 10px;
    border-radius: 12px;
    border: 1px solid color-mix(in srgb, var(--primary) 20%, transparent);
}

/* 情绪显示 */
.face-emotion-display {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
}

.emotion-emoji {
    font-size: 18px;
    line-height: 1;
}

.emotion-name {
    color: var(--text-primary);
}

/* 置信度徽章 */
.face-confidence-badge {
    font-size: 16px;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 16px;
    background: color-mix(in srgb, currentColor 15%, transparent);
    border: 1px solid currentColor;
    line-height: 1;
    white-space: nowrap;
}

/* ✅ 新增: 进度条区域 */
.face-progress-section {
    margin-bottom: 10px;
}

/* ✅ 新增: 人脸卡片进度条渐变色支持 */
.face-detail-card .el-progress-bar__inner {
    transition: all 0.3s ease;
    box-shadow: 0 0 8px color-mix(in srgb, currentColor 30%, transparent);
}

/* ✅ 重构: BBox 信息 */
.face-bbox-info {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    color: var(--text-secondary);
    font-family: 'Courier New', 'Consolas', monospace;
    padding: 6px 10px;
    background: color-mix(in srgb, var(--card-bg) 50%, transparent);
    border-radius: var(--radius-sm);
    border: 1px solid color-mix(in srgb, var(--border) 50%, transparent);
}

.bbox-label {
    color: var(--text-tertiary);
    font-weight: 500;
}

.bbox-coords {
    color: var(--text-secondary);
    letter-spacing: 0.5px;
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
