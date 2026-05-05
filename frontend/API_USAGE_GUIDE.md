# API 层使用指南

## 📚 目录

- [快速开始](#快速开始)
- [HTTP 客户端](#http-客户端)
- [业务模块 API](#业务模块-api)
- [错误处理](#错误处理)
- [迁移指南](#迁移指南)

---

## 快速开始

### 导入方式

```javascript
// ✅ 推荐：从统一入口导入
import { getHistoryList, getEmotionTrend } from '@/api'

// ✅ 也可以从模块导入
import { getHistoryList } from '@/api/modules/history'
import { getEmotionTrend } from '@/api/modules/analytics'

// ✅ 直接使用 HTTP 客户端
import { http } from '@/api'
```

---

## HTTP 客户端

### 基本用法

```javascript
import { http } from '@/api'

// GET 请求
const data = await http.get('/api/history')

// POST 请求
const result = await http.post('/api/config', { key: 'value' })

// 带参数的 GET 请求
const list = await http.get('/api/history', {
  params: { limit: 10, offset: 0 }
})
```

### 特性

✅ **自动 baseURL**：无需拼接完整 URL  
✅ **自动 JSON 解析**：直接返回 `response.data`  
✅ **统一错误处理**：自动显示 Element Plus 消息提示  
✅ **请求日志**：开发环境自动打印请求/响应信息  

### 配置选项

```javascript
// 禁用错误提示（静默失败）
await http.get('/api/health', { showError: false })

// 自定义超时时间
await http.post('/api/detect/image', formData, {
  timeout: 60000, // 60秒
  headers: { 'Content-Type': 'multipart/form-data' }
})
```

---

## 业务模块 API

### 1. 历史记录 API (`modules/history.js`)

```javascript
import { 
  getHistoryList, 
  getHistoryStats, 
  saveHistoryRecord,
  exportHistoryRecord,
  deleteHistoryRecord
} from '@/api/modules/history'

// 获取历史记录列表
const { data, total, type_counts } = await getHistoryList({
  limit: 12,
  offset: 0,
  type: 'realtime' // 可选：筛选类型
})

// 获取统计信息
const stats = await getHistoryStats()
console.log(stats.total_records) // 总记录数
console.log(stats.stats) // 详细统计

// 保存检测记录
await saveHistoryRecord({
  emotion: 'happy',
  confidence: 0.95,
  detected_faces: [...]
})

// 导出记录（返回 Blob）
const blob = await exportHistoryRecord(recordId)
const url = URL.createObjectURL(blob)
// 下载文件...

// 删除记录
await deleteHistoryRecord(recordId)

// 批量删除
await batchDeleteHistory([id1, id2, id3])
```

---

### 2. 数据分析 API (`modules/analytics.js`)

```javascript
import { 
  getEmotionTrend, 
  getEmotionTransitions,
  logFeatureUsage,
  getUserAnalytics
} from '@/api/modules/analytics'

// 获取情绪趋势（最近7天）
const trendData = await getEmotionTrend({ days: 7 })

// 获取情绪转换矩阵
const transitions = await getEmotionTransitions({ limit: 1000 })

// 记录功能使用
logFeatureUsage('实时检测', {
  emotion: 'happy',
  duration: 120
})

// 获取用户行为统计
const analytics = await getUserAnalytics({
  start_date: '2026-05-01',
  end_date: '2026-05-05'
})
```

---

### 3. 检测相关 API (`modules/detection.js`)

```javascript
import { 
  detectImage, 
  detectBatch, 
  detectVideo,
  getRealtimeStreamUrl
} from '@/api/modules/detection'

// 单张图片检测
const formData = new FormData()
formData.append('file', imageFile)
const result = await detectImage(formData)

// 批量检测
const batchForm = new FormData()
files.forEach(file => {
  batchForm.append('files', file)
})
const batchResult = await detectBatch(batchForm)

// 视频检测
const videoForm = new FormData()
videoForm.append('file', videoFile)
const videoResult = await detectVideo(videoForm)

// 获取 WebSocket URL
const wsUrl = getRealtimeStreamUrl()
// ws://localhost:8000/ws/stream
```

---

### 4. 系统配置 API (`modules/system.js`)

```javascript
import { 
  getSystemConfig, 
  updateSystemConfig,
  getHealthStatus,
  getSystemStats,
  submitFeedback
} from '@/api/modules/system'

// 获取系统配置
const config = await getSystemConfig()

// 更新配置
await updateSystemConfig({
  model_path: '/path/to/model',
  confidence_threshold: 0.5
})

// 健康检查
const health = await getHealthStatus()
console.log(health.status) // 'ok'

// 获取系统统计
const stats = await getSystemStats()

// 提交反馈
await submitFeedback({
  type: 'bug',
  content: '发现一个问题...',
  contact: 'user@example.com'
})
```

---

## 错误处理

### 自动错误提示

默认情况下，API 错误会自动显示 Element Plus 消息提示：

```javascript
try {
  await getHistoryList()
} catch (error) {
  // 已自动显示错误消息
  // 可以在这里做额外处理
  console.error('额外处理:', error)
}
```

### 静默失败

如果不想显示错误提示：

```javascript
// 方式 1：在请求配置中设置
await http.get('/api/health', { showError: false })

// 方式 2：捕获错误
try {
  await getHistoryList()
} catch (error) {
  // 不会显示消息提示
}
```

### 错误类型

| 错误码 | 提示信息 | 说明 |
|--------|---------|------|
| 网络错误 | "网络连接失败，请检查后端服务是否启动" | 后端未启动或网络不通 |
| 超时 | "请求超时，请检查网络连接" | 超过 30 秒未响应 |
| 400 | "请求参数错误" | 参数格式不正确 |
| 401 | "未授权，请重新登录" | Token 失效 |
| 403 | "禁止访问" | 权限不足 |
| 404 | "请求的资源不存在" | 接口路径错误 |
| 500 | "服务器内部错误" | 后端异常 |
| 502 | "网关错误，后端服务可能未启动" | 反向代理错误 |

---

## 迁移指南

### 从 `fetch` 迁移到新的 API 层

#### 之前（使用 fetch）

```javascript
// ❌ 旧代码
import { API } from '@/api/config'

const response = await fetch(`${API.history}?limit=12&offset=0`)
if (!response.ok) throw new Error('请求失败')
const data = await response.json()
```

#### 之后（使用新 API）

```javascript
// ✅ 新代码
import { getHistoryList } from '@/api/modules/history'

const data = await getHistoryList({ limit: 12, offset: 0 })
// 自动处理错误，无需手动检查 response.ok
```

---

### 迁移步骤

1. **找到旧的 fetch 调用**
   ```bash
   grep -r "fetch(.*api/" src/
   ```

2. **确定对应的 API 模块**
   - `/api/history/*` → `modules/history.js`
   - `/api/analytics/*` → `modules/analytics.js`
   - `/api/detect/*` → `modules/detection.js`
   - `/api/config`, `/api/health` → `modules/system.js`

3. **替换为新的 API 方法**
   ```javascript
   // 之前
   const res = await fetch(`${API.baseUrl}/api/config`)
   const config = await res.json()
   
   // 之后
   import { getSystemConfig } from '@/api/modules/system'
   const config = await getSystemConfig()
   ```

4. **移除错误处理代码**
   ```javascript
   // 之前
   if (!response.ok) {
     ElMessage.error('请求失败')
     return
   }
   
   // 之后：自动处理，无需手动检查
   ```

---

## 📊 对比优势

| 特性 | fetch | 新 API 层 |
|------|-------|----------|
| 代码简洁度 | ❌ 需要手动解析 JSON | ✅ 自动解析 |
| 错误处理 | ❌ 需要手动检查 status | ✅ 自动处理 + 友好提示 |
| baseURL 管理 | ❌ 需要手动拼接 | ✅ 自动添加 |
| 请求日志 | ❌ 需要手动添加 | ✅ 开发环境自动打印 |
| TypeScript 支持 | ❌ 无类型提示 | ✅ 完整的 JSDoc 注释 |
| 拦截器 | ❌ 不支持 | ✅ 支持请求/响应拦截 |
| 取消请求 | ❌ 需要 AbortController | ✅ Axios 内置支持 |

---

## 🔧 高级用法

### 添加请求拦截器

在 `src/api/http.js` 中添加：

```javascript
http.interceptors.request.use(config => {
  // 添加 token
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  
  // 添加请求 ID（用于追踪）
  config.headers['X-Request-ID'] = generateRequestId()
  
  return config
})
```

### 自定义响应处理

```javascript
// 对于特殊接口，可以跳过自动解析
const response = await http.get('/api/export', {
  responseType: 'blob' // 返回原始 Blob
})
```

### 并行请求

```javascript
import { getHistoryList, getHistoryStats } from '@/api'

// 同时发起多个请求
const [history, stats] = await Promise.all([
  getHistoryList({ limit: 10 }),
  getHistoryStats()
])

console.log(history.data, stats.total_records)
```

---

## 📝 最佳实践

1. **优先使用模块 API**：不要直接使用 `http`，除非模块中没有对应方法
2. **统一错误处理**：依赖自动错误提示，避免重复代码
3. **合理使用静默模式**：仅在后台任务中使用 `{ showError: false }`
4. **添加 JSDoc 注释**：为新 API 方法添加完整的类型注释
5. **保持向后兼容**：保留旧的 `utils/analytics.js` 等兼容层

---

**最后更新**: 2026-05-05  
**维护者**: AI Assistant
