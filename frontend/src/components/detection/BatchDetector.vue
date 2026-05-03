<template>
    <div class="batch-detector">
        <div class="detector-layout">
            <!-- 左侧：上传区域 / 图片预览 -->
            <div class="left-panel">
                <el-card class="glass-card">
                    <template #header>
                        <div class="card-header">
                            <span class="card-icon">📁</span>
                            <h3>批量检测 <span class="badge">并发3张</span></h3>
                        </div>
                    </template>

                    <!-- 上传区域（未选择文件时显示） -->
                    <el-upload v-if="fileList.length === 0" class="upload-area" drag multiple :auto-upload="false"
                        :on-change="handleFilesChange" :file-list="fileList" accept="image/*">
                        <el-icon class="el-icon--upload" :size="48">
                            <UploadFilled />
                        </el-icon>
                        <div class="el-upload__text">
                            拖拽多张图片到此处或 <em>点击上传</em>
                        </div>
                        <template #tip>
                            <div class="el-upload__tip">支持 JPG、PNG 格式</div>
                        </template>
                    </el-upload>

                    <!-- 已选择文件列表（检测前显示） -->
                    <div v-if="fileList.length > 0 && results.length === 0" class="file-list-section">
                        <div class="file-list-header">
                            <span class="file-count">已选择 {{ fileList.length }} 张图片</span>
                            <button class="clear-btn" @click="clearAll">
                                <el-icon>
                                    <Delete />
                                </el-icon>
                                清空
                            </button>
                        </div>
                        <div class="file-list-grid">
                            <div v-for="(file, index) in fileList" :key="index" class="file-item">
                                <img :src="file.imageUrl" :alt="file.name" class="file-thumbnail" />
                                <div class="file-name">{{ file.name }}</div>
                            </div>
                        </div>
                    </div>

                    <!-- 检测后：图片预览（带检测框） -->
                    <div v-if="results.length > 0" class="batch-preview-section">
                        <div v-for="(result, index) in results" :key="index" class="preview-item">
                            <canvas :ref="el => canvasRefs[index] = el" class="batch-canvas"></canvas>
                            <div class="preview-overlay">
                                <span class="face-count">{{ result.faces.length }} 张人脸</span>
                            </div>
                        </div>
                    </div>

                    <div v-if="fileList.length > 0" class="action-bar">
                        <el-button type="primary" @click="startBatchDetection" :loading="detecting" round size="large">
                            <el-icon style="margin-right:6px">
                                <Upload />
                            </el-icon>
                            开始检测 ({{ fileList.length }} 张)
                        </el-button>
                        <el-button @click="clearAll" round size="large">清空列表</el-button>
                    </div>

                    <div v-if="detecting" class="floating-progress">
                        <div class="floating-progress-card">
                            <el-progress :percentage="progress" :status="progress === 100 ? 'success' : undefined"
                                :stroke-width="12" />
                            <p class="progress-status">正在处理: {{ currentIndex + 1 }} / {{ fileList.length }}</p>
                        </div>
                    </div>
                </el-card>
            </div>

            <!-- 右侧：检测结果统计 -->
            <div class="right-panel">
                <el-card class="glass-card result-card">
                    <template #header>
                        <div class="card-header">
                            <span class="card-icon">🎯</span>
                            <h3>检测结果</h3>
                        </div>
                    </template>

                    <!-- 空状态占位符 -->
                    <div v-if="results.length === 0" class="empty-state">
                        <div class="empty-icon">📊</div>
                        <p>上传并检测图片后<br />将在此处显示结果</p>
                    </div>

                    <!-- 检测结果统计 -->
                    <div v-else class="batch-results-grid">
                        <div v-for="(result, index) in results" :key="index" class="result-card-item glass-card-inner"
                            :style="{ animationDelay: `${index * 0.05}s` }">
                            <div class="result-header">
                                <span class="result-index">图片 {{ index + 1 }}</span>
                                <span class="face-count-badge">{{ result.faces.length }} 张人脸</span>
                            </div>
                            <div class="result-info">
                                <div v-if="result.faces.length > 0" class="faces-list">
                                    <div v-for="(face, faceIndex) in result.faces" :key="faceIndex" class="face-item">
                                        <div class="face-item-content">
                                            <span class="face-emoji">{{ getEmotionEmoji(face.emotion) }}</span>
                                            <span class="face-label">人脸 {{ faceIndex + 1 }}</span>
                                            <span class="face-emotion">{{ getEmotionName(face.emotion) }}</span>
                                            <span class="face-confidence">{{ (face.confidence * 100).toFixed(1)
                                            }}%</span>
                                        </div>
                                        <el-progress :percentage="face.confidence * 100"
                                            :color="getEmotionColor(face.emotion)" :stroke-width="6" :show-text="false"
                                            class="face-confidence-bar" />
                                    </div>
                                </div>
                                <div v-else class="no-face">
                                    <span class="no-face-emoji">{{ getEmotionEmoji('neutral') }}</span>
                                    未检测到人脸
                                </div>
                            </div>
                        </div>
                        <div class="export-bar">
                            <el-button size="small" @click="exportResults" round>导出 JSON</el-button>
                        </div>
                    </div>
                </el-card>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { UploadFilled, Upload, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { drawCornerBox, drawEmotionLabel } from '@/utils/canvas'
import { useThemeStore } from '@/stores/theme'
import { getEmotionName, getEmotionEmoji, getEmotionColor } from '@/utils/emotion'
import { API } from '@/api/config'
import { logFeatureUsage } from '@/utils/analytics'

const themeStore = useThemeStore()
const fileList = ref([])
const detecting = ref(false)
const progress = ref(0)
const currentIndex = ref(0)
const results = ref([])
const canvasRefs = ref([]) // 存储多个 canvas 引用
const BATCH_CONCURRENCY = 3

const handleFilesChange = async (file, files) => {
    // 为每个文件生成预览 URL
    for (const f of files) {
        if (!f.imageUrl && f.raw) {
            f.imageUrl = await readFileAsDataURL(f.raw)
        }
    }
    fileList.value = files
}

const startBatchDetection = async () => {
    if (!fileList.value.length) { ElMessage.warning('请先选择图片'); return }
    detecting.value = true; progress.value = 0; currentIndex.value = 0; results.value = []

    const total = fileList.value.length
    const queue = fileList.value.map((f, i) => ({ file: f.raw, imageUrl: f.imageUrl, index: i, name: f.name }))
    let completed = 0

    const processOne = async (item) => {
        try {
            const formData = new FormData()
            formData.append('file', item.file)
            const res = await fetch(API.detectImage, { method: 'POST', body: formData })
            const result = await res.json()

            // 使用已生成的预览 URL
            const imageUrl = item.imageUrl
            const dominantEmotion = result.faces?.[0]?.emotion || 'neutral'
            const confidence = result.faces?.[0]?.confidence || 0

            return { imageUrl, faces: result.faces || [], dominant_emotion: dominantEmotion, confidence }
        } catch (e) {
            console.error(`处理 ${item.name} 失败:`, e)
            return null
        }
    }

    const worker = async () => {
        while (queue.length > 0) {
            const item = queue.shift()
            const r = await processOne(item)
            if (r) results.value.push(r)
            completed++
            currentIndex.value = completed
            progress.value = Math.round((completed / total) * 100)
        }
    }

    const workers = Array(Math.min(BATCH_CONCURRENCY, total)).fill(null).map(() => worker())
    await Promise.all(workers)

    logFeatureUsage('批量检测', { total: results.value.length })
    ElMessage.success(`✅ 批量检测完成！共 ${results.value.length} 张图片`)
    detecting.value = false

    // 检测完成后绘制 Canvas
    await nextTick()
    results.value.forEach((result, index) => {
        drawBatchCanvas(result, index)
    })

    // 保存到历史记录（批量保存）
    await saveBatchToHistory()
}

// 绘制批量检测的 Canvas 预览
const drawBatchCanvas = (result, index) => {
    const canvas = canvasRefs.value[index]
    if (!canvas || !result.imageUrl) return

    const ctx = canvas.getContext('2d')
    const img = new Image()

    img.onload = () => {
        // 获取容器尺寸
        const container = canvas.parentElement
        const containerWidth = container.clientWidth
        const containerHeight = container.clientWidth // 正方形

        // 设置 Canvas 物理尺寸为容器大小
        canvas.width = containerWidth
        canvas.height = containerHeight

        // 计算缩放比例，确保图片完整显示不溢出
        const scaleX = containerWidth / img.width
        const scaleY = containerHeight / img.height
        const scale = Math.min(scaleX, scaleY)

        // 计算图片绘制尺寸和居中位置
        const drawWidth = img.width * scale
        const drawHeight = img.height * scale
        const offsetX = (containerWidth - drawWidth) / 2
        const offsetY = (containerHeight - drawHeight) / 2

        // 清空画布并绘制图片
        ctx.clearRect(0, 0, containerWidth, containerHeight)
        ctx.drawImage(img, offsetX, offsetY, drawWidth, drawHeight)

        // 绘制检测框和标签
        if (result.faces?.length) {
            result.faces.forEach((face, faceIndex) => {
                const color = getEmotionColor(face.emotion)

                // 缩放 bbox 坐标（格式：[x, y, width, height]）
                const scaledBbox = [
                    face.bbox[0] * scale + offsetX,  // x 坐标
                    face.bbox[1] * scale + offsetY,  // y 坐标
                    face.bbox[2] * scale,            // width
                    face.bbox[3] * scale             // height
                ]

                // 绘制检测框和标签
                const totalFaces = result.faces.length
                drawCornerBox(ctx, scaledBbox, color, 4)
                drawEmotionLabel(ctx, scaledBbox, face.emotion, face.confidence, themeStore.currentTheme, faceIndex + 1, totalFaces)
            })
        }
    }

    img.src = result.imageUrl
}

const readFileAsDataURL = (file) => new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => resolve(e.target.result)
    reader.onerror = reject
    reader.readAsDataURL(file)
})

const clearAll = () => {
    fileList.value = []; results.value = []; progress.value = 0; currentIndex.value = 0
}

const exportResults = () => {
    const data = JSON.stringify(results.value, null, 2)
    const blob = new Blob([data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url; link.download = `batch_results_${Date.now()}.json`; link.click()
    URL.revokeObjectURL(url)
    ElMessage.success('✅ 结果已导出')
}

// 批量保存到历史记录
const saveBatchToHistory = async () => {
    try {
        let successCount = 0
        let failCount = 0

        // ✅ 优化: 为每张图片单独保存一条历史记录
        for (let i = 0; i < results.value.length; i++) {
            const result = results.value[i]

            // 提取关键数据
            const dominantEmotion = result.dominant_emotion || 'neutral'
            const confidence = result.confidence || 0
            const faces = result.faces || []

            // 数据验证
            if (!result.imageUrl && faces.length === 0) {
                console.warn(`⚠️ 跳过第 ${i + 1} 张图片：无缩略图且无人脸数据`)
                failCount++
                continue
            }

            try {
                const response = await fetch(API.historySave, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        detection_type: 'batch',
                        results: faces,
                        source: `批量图片检测 (${i + 1}/${results.value.length})`,
                        image_path: '',
                        image_type: 'batch',
                        thumbnail: result.imageUrl || '',  // ✅ 确保 thumbnail 存在
                        dominant_emotion: dominantEmotion,
                        confidence: confidence,
                        detected_faces: faces  // ✅ 包含完整的人脸数据（含 bbox）
                    })
                })

                if (response.ok) {
                    successCount++
                } else {
                    console.error(`❌ 第 ${i + 1} 张图片保存失败: HTTP ${response.status}`)
                    failCount++
                }
            } catch (err) {
                console.error(` 第 ${i + 1} 张图片保存异常:`, err)
                failCount++
            }
        }

        // 输出保存结果
        console.log(`✅ 批量历史记录保存完成: 成功 ${successCount} 条, 失败 ${failCount} 条`)

        // 如果有失败，提示用户
        if (failCount > 0) {
            ElMessage.warning(`⚠️ 部分记录保存失败 (${failCount}/${results.value.length})`)
        }
    } catch (error) {
        console.error('保存批量历史记录失败:', error)
        ElMessage.error('❌ 批量历史记录保存失败')
    }
}
</script>

<style scoped>
.batch-detector {
    height: 100%;
    overflow: hidden;
}

.detector-layout {
    display: grid;
    grid-template-columns: 1fr 320px;
    gap: 12px;
    height: 100%;
}

.left-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
    /* ✅ 修复: 移除 overflow-y，让 el-card__body 管理滚动 */
    overflow-y: visible;
    padding-right: 4px;
}

.left-panel .el-card {
    height: 100%;
    display: flex;
    flex-direction: column;
}

.left-panel .el-card__body {
    flex: 1;
    overflow-y: auto;
    /* ✅ 新增: 卡片内容滚动条样式 */
}

.left-panel .el-card__body::-webkit-scrollbar {
    width: 6px;
}

.left-panel .el-card__body::-webkit-scrollbar-thumb {
    background: rgba(146, 78, 255, 0.3);
    border-radius: 3px;
}

.left-panel .el-card__body::-webkit-scrollbar-thumb:hover {
    background: rgba(146, 78, 255, 0.5);
}

.right-panel {
    height: 100%;
    /* ✅ 修复: 移除 overflow-y，让 el-card__body 管理滚动 */
    overflow-y: visible;
}

.right-panel .el-card {
    height: 100%;
    display: flex;
    flex-direction: column;
}

.right-panel .el-card__body {
    flex: 1;
    overflow-y: auto;
    /* ✅ 新增: 结果卡片滚动条样式 */
}

.right-panel .el-card__body::-webkit-scrollbar {
    width: 6px;
}

.right-panel .el-card__body::-webkit-scrollbar-thumb {
    background: rgba(146, 78, 255, 0.3);
    border-radius: 3px;
}

.right-panel .el-card__body::-webkit-scrollbar-thumb:hover {
    background: rgba(146, 78, 255, 0.5);
}

.result-card {
    height: 100%;
}

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    gap: 12px;
    color: var(--text-secondary);
}

.empty-icon {
    font-size: 48px;
    opacity: 0.5;
}

.empty-state p {
    font-size: 13px;
    text-align: center;
    line-height: 1.6;
    margin: 0;
}

.glass-card {
    border-radius: var(--radius-md);
    overflow: hidden;
}

.card-header {
    display: flex;
    align-items: center;
    gap: 10px;
}

.card-header h3 {
    font-size: 17px;
    font-weight: 100;
    margin: 0;
}

.card-icon {
    font-size: 22px;
}

.badge {
    font-size: 10px;
    /* font-weight: 600; */
    padding: 2px 8px;
    border-radius: 20px;
    background: var(--gradient);
    color: var(--text);
    margin-left: 8px;
    vertical-align: middle;
}

.upload-area {
    margin-bottom: 12px;
    /* ✅ 优化: 减小固定高度，更紧凑 */
    min-height: 500px;
    height: 500px;
    display: flex;
    flex-direction: column;
}

.upload-area :deep(.el-upload) {
    flex: 1;
    display: flex;
}

.upload-area :deep(.el-upload-dragger) {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    /* ✅ 优化: 减小最小高度，避免大片空白 */
    min-height: 500px;
    height: 100%;
}

/* 文件列表区域 */
.file-list-section {
    margin-bottom: 12px;
    animation: fadeIn 0.3s ease;
}

.file-list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    padding: 8px 12px;
    background: color-mix(in srgb, var(--primary) 10%, transparent);
    border-radius: 8px;
}

.file-count {
    font-size: 13px;
    /* font-weight: 600; */
    color: var(--text);
}

.clear-btn {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 12px;
    font-size: 12px;
    color: var(--text-secondary);
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.clear-btn:hover {
    color: var(--primary);
    background: color-mix(in srgb, var(--primary) 10%, transparent);
    border-color: color-mix(in srgb, var(--primary) 30%, transparent);
}

.clear-btn .el-icon {
    font-size: 14px;
}

.file-list-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 10px;
    /* ✅ 优化: 动态最大高度，根据视口调整 */
    max-height: calc(100vh - 350px);
    overflow-y: auto;
    padding: 4px;
}

/* ✅ 新增: 文件列表网格滚动条样式 */
.file-list-grid::-webkit-scrollbar {
    width: 6px;
}

.file-list-grid::-webkit-scrollbar-thumb {
    background: rgba(146, 78, 255, 0.3);
    border-radius: 3px;
}

.file-list-grid::-webkit-scrollbar-thumb:hover {
    background: rgba(146, 78, 255, 0.5);
}

.file-item {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 6px;
    background: color-mix(in srgb, var(--card-bg) 60%, transparent);
    border: 1px solid var(--border);
    border-radius: 8px;
    transition: all 0.2s ease;
}

.file-item:hover {
    border-color: color-mix(in srgb, var(--border) 60%, var(--primary));
    transform: translateY(-2px);
}

.file-thumbnail {
    width: 100%;
    aspect-ratio: 1;
    object-fit: cover;
    border-radius: 6px;
    background: var(--card-bg);
}

.file-name {
    font-size: 10px;
    color: var(--text-secondary);
    text-align: center;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding: 0 4px;
}

:deep(.el-upload-dragger) {
    padding: 40px 16px;
}

.glass-card-inner {
    background: color-mix(in srgb, var(--card-bg) 55%, transparent);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 14px;
    transition: all 0.2s ease;
}

.glass-card-inner:hover {
    border-color: color-mix(in srgb, var(--border) 60%, var(--primary));
}

.action-bar {
    display: flex;
    gap: 8px;
    justify-content: center;
    margin: 12px 0;
}

.floating-progress {
    position: fixed;
    bottom: 20%;
    left: 50%;
    transform: translateX(-50%);
    z-index: 9999;
    animation: fadeInUp 0.3s ease;
}

.floating-progress-card {
    background: color-mix(in srgb, var(--card-bg) 75%, transparent);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid color-mix(in srgb, var(--border) 80%, var(--primary));
    border-radius: 16px;
    padding: 20px 32px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4),
        0 0 0 1px rgba(113, 57, 255, 0.1),
        inset 0 1px 0 color-mix(in srgb, var(--card-bg) 90%, transparent);
    min-width: 480px;
    max-width: 600px;
}

.floating-progress-card :deep(.el-progress) {
    margin-bottom: 12px;
}

.floating-progress-card :deep(.el-progress-bar__outer) {
    background: color-mix(in srgb, var(--card-bg) 60%, transparent);
    border-radius: 6px;
    overflow: hidden;
}

.floating-progress-card :deep(.el-progress-bar__inner) {
    border-radius: 6px;
    box-shadow: 0 0 12px currentColor;
    transition: width 0.3s ease;
}

.progress-status {
    margin: 0;
    color: var(--text);
    font-size: 14px;
    /* font-weight: 600; */
    text-align: center;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.results-section {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

/* 批量预览区域（左侧面板显示） */
.batch-preview-section {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 12px;
    margin-top: 12px;
    max-height: calc(100vh - 250px);
    overflow-y: auto;
    padding: 4px;
}

/* ✅ 新增: 批量预览区域滚动条样式 */
.batch-preview-section::-webkit-scrollbar {
    width: 6px;
}

.batch-preview-section::-webkit-scrollbar-thumb {
    background: rgba(146, 78, 255, 0.3);
    border-radius: 3px;
}

.batch-preview-section::-webkit-scrollbar-thumb:hover {
    background: rgba(146, 78, 255, 0.5);
}

.preview-item {
    position: relative;
    background: color-mix(in srgb, var(--card-bg) 40%, transparent);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.3s ease;
}

.preview-item:hover {
    border-color: color-mix(in srgb, var(--border) 60%, var(--primary));
    transform: translateY(-2px);
    box-shadow: var(--shadow);
}

.batch-canvas {
    width: 100%;
    aspect-ratio: 1;
    display: block;
}

.preview-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 10px;
    background: linear-gradient(to top, rgba(0, 0, 0, 0.85), transparent);
    color: var(--text);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.preview-overlay .face-count {
    font-size: 13px;
    /* font-weight: 600; */
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

/* 批量结果统计网格（右侧面板显示） */
.batch-results-grid {
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-height: calc(100vh - 180px);
    overflow-y: auto;
    padding: 4px;
}

/* ✅ 新增: 批量结果网格滚动条样式 */
.batch-results-grid::-webkit-scrollbar {
    width: 6px;
}

.batch-results-grid::-webkit-scrollbar-thumb {
    background: rgba(146, 78, 255, 0.3);
    border-radius: 3px;
}

.batch-results-grid::-webkit-scrollbar-thumb:hover {
    background: rgba(146, 78, 255, 0.5);
}

.result-card-item {
    padding: 12px;
    border-radius: var(--radius-sm);
    animation: fadeInUp 0.4s ease both;
    transition: all 0.3s ease;
    flex-shrink: 0;
}

.result-card-item:hover {
    transform: translateX(4px);
    box-shadow: var(--shadow);
    border-color: color-mix(in srgb, var(--border) 60%, var(--primary));
}

.result-header {
    margin-bottom: 8px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.result-index {
    font-size: 12px;
    /* font-weight: 600; */
    color: var(--text-secondary);
}

.face-count-badge {
    font-size: 10px;
    /* font-weight: 600; */
    padding: 2px 8px;
    background: color-mix(in srgb, var(--primary) 15%, transparent);
    border: 1px solid color-mix(in srgb, var(--primary) 30%, transparent);
    border-radius: 10px;
    color: var(--primary);
}

/* 人脸列表 */
.faces-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.face-item {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 8px;
    background: color-mix(in srgb, var(--card-bg) 30%, transparent);
    border-radius: 8px;
    transition: all 0.2s ease;
}

.face-item:hover {
    background: color-mix(in srgb, var(--primary) 8%, transparent);
}

.face-item-content {
    display: grid;
    grid-template-columns: 20px 50px 1fr auto;
    align-items: center;
    gap: 6px;
}

.face-emoji {
    font-size: 17px;
    line-height: 1;
    text-align: center;
}

.face-label {
    font-size: 10px;
    /* font-weight: 600; */
    color: var(--text-secondary);
}

.face-emotion {
    font-size: 12px;
    /* font-weight: 600; */
    color: var(--text);
}

.face-confidence {
    font-size: 12px;
    font-weight: 100;
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* 置信度进度条 */
.face-confidence-bar {
    margin: 0;
}

.face-confidence-bar :deep(.el-progress-bar__outer) {
    background: color-mix(in srgb, var(--card-bg) 50%, transparent);
    border-radius: 3px;
    overflow: hidden;
}

.face-confidence-bar :deep(.el-progress-bar__inner) {
    border-radius: 3px;
    box-shadow: 0 0 8px currentColor;
    transition: width 0.6s ease;
}

.export-bar {
    display: flex;
    justify-content: center;
    flex-shrink: 0;
}

.results-grid {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.result-item {
    padding: 6px;
    border-radius: var(--radius-sm);
    animation: fadeInUp 0.4s ease both;
    transition: all 0.3s ease;
}

.result-item:hover {
    transform: translateX(4px);
    box-shadow: var(--shadow);
    border-color: color-mix(in srgb, var(--border) 60%, var(--primary));
}

.result-image {
    position: relative;
    width: 100%;
    aspect-ratio: 4/3;
    overflow: hidden;
    border-radius: 8px;
}

.result-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.result-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 8px;
    background: linear-gradient(to top, rgba(0, 0, 0, 0.8), transparent);
    color: var(--text);
}

.face-count {
    font-size: 12px;
    /* font-weight: 600; */
}

.result-info {
    padding: 10px 4px 4px;
}

.result-emotion-summary {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.dominant-emotion {
    display: flex;
    align-items: center;
    gap: 8px;
}

.dominant-emoji {
    font-size: 20px;
    line-height: 1;
    flex-shrink: 0;
}

.dominant-emotion .name {
    font-size: 13px;
    /* font-weight: 600; */
    flex: 1;
    color: var(--text);
}

.dominant-emotion .confidence {
    font-size: 14px;
    font-weight: 100;
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.no-face {
    text-align: center;
    color: var(--text-secondary);
    padding: 10px;
    font-size: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
}

.no-face-emoji {
    font-size: 18px;
    opacity: 0.4;
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@media (max-width: 1200px) {
    .detector-layout {
        grid-template-columns: 1fr;
    }

    .right-panel {
        max-height: 50vh;
    }
}
</style>
