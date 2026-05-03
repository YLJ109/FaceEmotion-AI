#  AI 情感检测系统

> 基于深度学习的多模态实时情感识别平台，支持人脸检测、情绪分析、语音情绪识别和 AI 音乐生成

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-orange.svg)](LICENSE)

---

## 📑 目录

- [项目简介](#-项目简介)
- [核心功能](#-核心功能)
- [技术栈](#-技术栈)
- [系统架构](#-系统架构)
- [快速开始](#-快速开始)
- [详细配置](#-详细配置)
- [API 文档](#-api-文档)
- [前端组件](#-前端组件)
- [数据库设计](#-数据库设计)
- [性能优化](#-性能优化)
- [常见问题](#-常见问题)
- [开发规范](#-开发规范)
- [部署指南](#-部署指南)
- [贡献指南](#-贡献指南)
- [许可证](#-许可证)

---

## 📖 项目简介

**AI 情感检测系统**是一个基于深度学习的全栈情感识别平台，集成了：

- **人脸检测与情绪识别**：使用 Caffe SSD + ONNX 模型，支持 GPU 加速
- **语音情绪分析**：通过 AudioWorklet 实时采集音频，分析声学特征
- **多模态融合**：结合视觉和语音情绪，提供更准确的情感判断
- **AI 音乐生成**：根据情绪状态实时生成对应的背景音乐
- **实时流媒体**：WebSocket 实现毫秒级数据传输
- **历史记录与统计**：完整的检测记录和数据分析看板

### 应用场景

-  **实时情感监控**：视频会议、在线教育、远程医疗
- 📊 **情绪数据分析**：用户行为研究、市场调研、心理学实验
- 🎵 **个性化音乐推荐**：根据情绪状态播放对应音乐
- 🎮 **游戏交互**：情感驱动的游戏体验

---

##  核心功能

### 1. 实时人脸检测

| 功能 | 说明 |
|------|------|
| 多模型支持 | Caffe SSD（高精度）+ ONNX RFB（高速度） |
| GPU 加速 | CUDA + TensorRT 支持 |
| 实时渲染 | Canvas 绘制检测框和情绪标签 |
| 多人脸识别 | 支持同时检测多张人脸 |
| 自适应阈值 | 动态调整置信度阈值 |

### 2. 情绪分类

| 情绪类型 | Emoji | 说明 |
|----------|-------|------|
| 😊 Happy | 快乐 | 高兴、愉悦 |
|  Sad | 悲伤 | 难过、沮丧 |
| 😠 Angry | 愤怒 | 生气、恼怒 |
| 😨 Fear | 恐惧 | 害怕、担心 |
|  Surprise | 惊讶 | 惊奇、意外 |
| 🤢 Disgust | 厌恶 | 反感、讨厌 |
| 😐 Neutral | 中性 | 平静、无表情 |

### 3. 语音情绪分析

- **AudioWorklet 采集**：低延迟音频流处理
- **声学特征提取**：
  - 音高（Pitch）
  - 能量（Energy）
  - 语速（Speaking Rate）
  - 有声/无声检测（VAD）
- **情绪分类**：基于音频特征的情绪识别
- **多模态融合**：结合视觉和语音情绪

### 4. AI 音乐生成

- **情绪驱动**：根据情绪状态选择音乐风格
- **实时生成**：基于 Web Audio API 合成音乐
- **交叉淡入淡出**：平滑过渡不同情绪的音乐
- **多音轨混合**：旋律、和声、节奏层独立控制

### 5. 检测模式

| 模式 | 说明 |
|------|------|
| 实时检测 | 摄像头实时视频流分析 |
| 图片检测 | 单张图片情绪识别 |
| 批量检测 | 多张图片批量处理 |
| 视频检测 | 视频文件关键帧分析 |

### 6. 数据管理

- **历史记录**：保存所有检测记录
- **数据统计**：情绪分布、趋势分析
- **数据导出**：CSV/JSON 格式导出
- **类型筛选**：按检测类型过滤记录

---

## 🛠 技术栈

### 后端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 主要开发语言 |
| FastAPI | 0.100+ | Web 框架 |
| Uvicorn | 0.23+ | ASGI 服务器 |
| OpenCV | 4.8+ | 图像处理 |
| ONNX Runtime | 1.15+ | 模型推理 |
| SQLite | 3.x | 数据库 |
| WebSocket | - | 实时通信 |

### 前端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue.js | 3.x | 前端框架 |
| Vite | 4.x | 构建工具 |
| Element Plus | 2.x | UI 组件库 |
| Chart.js | 4.x | 数据可视化 |
| Web Audio API | - | 音频处理 |
| Canvas API | - | 视频渲染 |

### 模型与技术

| 模型 | 格式 | 用途 |
|------|------|------|
| Caffe SSD | .caffemodel | 人脸检测（高精度） |
| ONNX RFB | .onnx | 人脸检测（高速度） |
| Emotion Classifier | .onnx | 情绪分类 |
| TensorRT | - | GPU 加速 |
| FP16 | - | 半精度推理 |

---

## 🏗 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端 (Vue.js)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ 实时检测 │  │ 图片检测 │  │ 批量检测 │  │ 视频检测 │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │             │             │           │
│  ┌────┴─────────────┴─────────────┴─────────────┴─────┐   │
│  │              WebSocket 实时通信                      │   │
│  └─────────────────────┬───────────────────────────────┘   │
│       ┌────────────────┴────────────────┐                  │
│       │    AudioWorklet (音频采集)       │                  │
│       └────────────────┬────────────────┘                  │
────────────────────────┼──────────────────────────────────┘
                         │ WebSocket / HTTP
┌────────────────────────┼──────────────────────────────────┐
│                        后端 (FastAPI)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ 人脸检测 │  │ 情绪分类 │  │ 语音分析 │  │ 音乐生成 │   │
│  │  模块    │  │  模块    │  │  模块    │  │  模块    │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │             │             │           │
│  ┌────┴─────────────┴─────────────┴─────────────┴─────┐   │
│  │           ONNX Runtime (GPU 加速)                    │   │
│  └─────────────────────┬───────────────────────────────┘   │
│                         │                                  │
│  ┌─────────────────────┴───────────────────────────────┐   │
│  │              SQLite 数据库                            │   │
│  │  • 检测历史记录                                      │   │
│  │  • 用户反馈                                          │   │
│  │  • 统计数据                                          │   │
│  └─────────────────────────────────────────────────────┘   │
─────────────────────────────────────────────────────────────┘
```

### 目录结构

```
FaceEmotion-AI/
├── backend/                    # 后端服务
│   ├── api/                    # API 路由
│   │   ├── detection.py        # 检测接口
│   │   ├── history.py          # 历史记录接口
│   │   ├── websocket.py        # WebSocket 处理
│   │   └── analytics.py        # 数据分析接口
│   ├── models/                 # AI 模型
│   │   ├── detector.py         # 人脸检测器
│   │   ├── emotion_classifier_onnx.py  # 情绪分类器
│   │   ├── face_detector_onnx.py       # ONNX 人脸检测
│   │   └── *.caffemodel        # Caffe 模型文件
│   ├── multimodal/             # 多模态模块
│   │   └── voice_analyzer.py   # 语音分析器
│   ├── music/                  # 音乐生成
│   │   └── music_generator.py  # 音乐生成器
│   ├── adaptation/             # 自适应学习
│   │   └── active_learner.py   # 主动学习
│   ├── optimizer/              # 性能优化
│   │   └── dynamic_inference.py # 动态推理
│   ├── analytics/              # 数据分析
│   │   └── user_analytics.py   # 用户分析
│   ├── database.py             # 数据库管理
│   ├── config.py               # 配置文件
│   ├── constants.py            # 常量定义
│   ├── app.py                  # 应用入口
│   └── requirements.txt        # Python 依赖
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── api/                # API 配置
│   │   │   ├── config.js       # API 地址
│   │   │   ── websocket.js    # WebSocket 客户端
│   │   ├── components/         # Vue 组件
│   │   │   ├── detection/      # 检测组件
│   │   │   │   ├── RealtimeDetector.vue   # 实时检测
│   │   │   │   ├── ImageDetector.vue      # 图片检测
│   │   │   │   ├── BatchDetector.vue      # 批量检测
│   │   │   │   └── VideoDetector.vue      # 视频检测
│   │   │   ├── HistoryViewer.vue          # 历史记录
│   │   │   ├── AnalyticsDashboard.vue     # 数据看板
│   │   │   ├── EmotionSVG.vue             # 情绪图标
│   │   │   └── FpsDisplay.vue             # FPS 显示
│   │   ├── utils/              # 工具函数
│   │   │   ├── emotion.js      # 情绪工具
│   │   │   ├── canvas.js       # Canvas 工具
│   │   │   ├── audioCapture.js # 音频采集
│   │   │   ├── audioEngine.js  # 音频引擎
│   │   │   └── analytics.js    # 分析工具
│   │   ├── stores/             # 状态管理
│   │   │   └── theme.js        # 主题状态
│   │   ├── themes/             # 主题配置
│   │   │   └── index.js        # 主题定义
│   │   ├── styles/             # 样式文件
│   │   │   └── element-overwatch.css  # Element Plus 主题
│   │   ├── App.vue             # 根组件
│   │   ── main.js             # 入口文件
│   ├── public/                 # 静态资源
│   ├── index.html              # HTML 模板
│   ├── vite.config.js          # Vite 配置
│   └── package.json            # 前端依赖
│
├── .env.example                # 环境变量示例
├── docker-compose.yml          # Docker 配置
└── README.md                   # 项目文档
```

---

## 🚀 快速开始

### 环境要求

- **Python**: 3.10 或更高版本
- **Node.js**: 18.x 或更高版本
- **GPU** (可选): NVIDIA GPU with CUDA 支持
- **操作系统**: Windows / Linux / macOS

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/yourusername/FaceEmotion-AI.git
cd FaceEmotion-AI
```

#### 2. 后端安装

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 下载模型文件
# 将模型文件放置在 backend/models/ 目录：
# - res10_300x300_ssd_iter_140000_fp16.caffemodel
# - deploy.prototxt
# - emotion_model.onnx
# - version-RFB-320.onnx (可选)
```

#### 3. 前端安装

```bash
cd ../frontend

# 安装依赖
npm install
```

#### 4. 配置环境变量

```bash
# 复制环境变量示例文件
cd backend
cp .env.example .env

# 编辑 .env 文件，配置你的参数
```

**.env 配置示例**：

```bash
# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=true

# 模型配置
FACE_DETECTOR_MODEL=./models/res10_300x300_ssd_iter_140000_fp16.caffemodel
USE_ONNX_FACE_DETECTOR=false
EMOTION_MODEL_PATH=./models/emotion_model.onnx
CONFIDENCE_THRESHOLD=0.6

# GPU 配置
USE_GPU=true
GPU_DEVICE=0
TENSORRT_CACHE=true
USE_FP16=true

# 数据库配置
DATABASE_PATH=./data/emotion.db

# 其他配置
MAX_FACES=10
FRAME_SKIP=2
```

#### 5. 启动服务

**启动后端**：

```bash
cd backend
python app.py
```

后端服务将在 `http://localhost:8000` 启动。

**启动前端**：

```bash
cd frontend
npm run dev
```

前端服务将在 `http://localhost:5173` 启动。

#### 6. 访问应用

打开浏览器访问 `http://localhost:5173`

---

## ️ 详细配置

### 后端配置

#### 模型选择

在 `backend/config.py` 中可以配置使用的模型：

```python
# 使用 Caffe SSD（高精度，推荐）
'face_detector_model': './models/res10_300x300_ssd_iter_140000_fp16.caffemodel',
'use_onnx_face_detector': False,

# 使用 ONNX RFB（高速度）
# 'face_detector_model': './models/version-RFB-320.onnx',
# 'use_onnx_face_detector': True,
```

#### GPU 加速

启用 GPU 加速以获得最佳性能：

```python
'use_gpu': True,
'gpu_device': 0,  # GPU 设备 ID
'tensorrt_cache': True,  # 使用 TensorRT 缓存
'use_fp16': True,  # 使用半精度推理
```

#### 性能调优

```python
# 置信度阈值（过滤低置信度的检测结果）
'confidence_threshold': 0.6,

# 最大检测人脸数
'max_faces': 10,

# 跳帧数（每 N 帧检测一次）
'frame_skip': 2,
```

### 前端配置

#### API 地址配置

在 `frontend/src/api/config.js` 中配置：

```javascript
export const API = {
  baseURL: 'http://localhost:8000/api',
  wsURL: 'ws://localhost:8000/ws/stream',
  // ... 其他 API 端点
}
```

#### 主题配置

在 `frontend/src/themes/index.js` 中自定义主题：

```javascript
export const themes = {
  overwatch: {
    name: 'Overwatch',
    primary: '#7139FF',
    // ... 主题颜色
  },
  // ... 其他主题
}
```

---

## 📡 API 文档

### REST API

#### 1. 单张图片检测

```
POST /api/detect/image
Content-Type: multipart/form-data

文件: file (图片文件)

响应:
{
  "status": "success",
  "faces": [
    {
      "bbox": [x, y, width, height],
      "emotion": "happy",
      "confidence": 0.95,
      "emotions": {
        "happy": 0.95,
        "sad": 0.02,
        ...
      }
    }
  ]
}
```

#### 2. 批量图片检测

```
POST /api/detect/batch
Content-Type: multipart/form-data

文件: files (多张图片)

响应:
{
  "status": "success",
  "results": [
    {
      "filename": "image1.jpg",
      "faces": [...]
    },
    ...
  ]
}
```

#### 3. 视频检测

```
POST /api/detect/video
Content-Type: multipart/form-data

文件: file (视频文件)

响应:
{
  "status": "success",
  "video_info": {
    "duration": 10.5,
    "fps": 30.0,
    "total_frames": 315,
    "key_frames_count": 10
  },
  "key_frames": [
    {
      "frame": 0,
      "timestamp": 0.0,
      "faces": [...]
    },
    ...
  ]
}
```

#### 4. 获取历史记录

```
GET /api/history?limit=20&offset=0&type=all

响应:
{
  "data": [...],
  "total": 100,
  "type_counts": {
    "realtime": 50,
    "image": 20,
    "batch": 10,
    "video": 20
  }
}
```

### WebSocket API

#### 实时视频流

```javascript
// 连接 WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/stream')

// 发送视频帧
ws.send(videoFrameBlob)

// 接收检测结果
ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  console.log('检测结果:', data)
  // data.faces: 人脸数据
  // data.voice_scores: 语音情绪分数
  // data.is_fused: 是否多模态融合
}
```

**数据格式**：

```json
{
  "faces": [
    {
      "bbox": [x, y, width, height],
      "emotion": "happy",
      "confidence": 0.95,
      "emotions": { ... }
    }
  ],
  "voice_scores": {
    "angry": 0.0,
    "disgust": 0.0,
    "fear": 0.0,
    "happy": 0.8,
    "neutral": 0.2,
    "sad": 0.0,
    "surprise": 0.0
  },
  "is_fused": true,
  "fps": 30.5
}
```

---

## 🧩 前端组件

### 检测组件

#### RealtimeDetector.vue

实时摄像头检测组件，核心功能：

- 摄像头画面采集
- WebSocket 实时通信
- Canvas 检测框绘制
- 情绪标签显示
- 语音情绪分析
- 多模态融合指示

**关键配置**：

```vue
<RealtimeDetector
  :show-voice-analysis="true"
  :show-fps="true"
  :ema-alpha="0.3"
/>
```

#### ImageDetector.vue

单张图片检测组件：

- 图片上传
- 人脸检测
- 情绪分类
- 结果展示

#### BatchDetector.vue

批量图片检测组件：

- 多文件上传
- 进度显示
- 批量处理
- 结果汇总

#### VideoDetector.vue

视频文件检测组件：

- 视频上传
- 关键帧提取
- 帧间插值
- 时间轴显示
- 结果导出

### 其他组件

#### HistoryViewer.vue

历史记录查看器：

- 分页显示
- 类型筛选
- 详情查看
- 数据导出

#### AnalyticsDashboard.vue

数据分析看板：

- 情绪分布图表
- 趋势分析
- 统计卡片
- 时间筛选

---

## 💾 数据库设计

### 检测历史记录表 (detection_history)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| timestamp | DATETIME | 检测时间 |
| detection_type | TEXT | 检测类型 (realtime/image/batch/video) |
| source | TEXT | 来源 |
| image_path | TEXT | 图片路径 |
| image_type | TEXT | 图片类型 |
| thumbnail | TEXT | 缩略图 (Base64) |
| results | TEXT | 检测结果 (JSON) |
| detected_faces | TEXT | 检测到的人脸 (JSON) |
| dominant_emotion | TEXT | 主导情绪 |
| confidence | FLOAT | 置信度 |

### 用户反馈表 (user_feedback)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| timestamp | DATETIME | 反馈时间 |
| emotion | TEXT | 原始情绪 |
| predicted_emotion | TEXT | 预测情绪 |
| correct_emotion | TEXT | 正确情绪 |
| feedback_type | TEXT | 反馈类型 |
| notes | TEXT | 备注 |

### 分析统计表 (analytics)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| timestamp | DATETIME | 统计时间 |
| metric_type | TEXT | 指标类型 |
| metric_value | FLOAT | 指标值 |
| metadata | TEXT | 元数据 (JSON) |

---

## ⚡ 性能优化

### 已实施的优化

#### 1. GPU 加速

- **CUDA**: 使用 NVIDIA GPU 加速模型推理
- **TensorRT**: 模型优化和缓存
- **FP16**: 半精度推理，速度提升 2 倍

#### 2. 模型优化

- **Caffe SSD**: 高精度人脸检测（准确率 >99%）
- **ONNX Runtime**: 跨平台推理引擎
- **模型缓存**: 避免重复加载

#### 3. 前端优化

- **Canvas 渲染**: 高效的视频帧绘制
- **帧率控制**: 可配置的跳帧策略
- **WebSocket 优化**: 二进制数据传输
- **EMA 平滑**: 情绪过渡更流畅

#### 4. 数据库优化

- **索引优化**: 查询性能提升
- **分页查询**: 避免大量数据传输
- **JSON 压缩**: 减少存储空间

### 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| 人脸检测 FPS | 30-60 | GPU 加速 |
| 情绪分类延迟 | <50ms | ONNX 推理 |
| WebSocket 延迟 | <100ms | 实时传输 |
| 模型加载时间 | <2s | 缓存优化 |
| 数据库查询 | <10ms | 索引优化 |

---

## ❓ 常见问题

### 1. 人脸检测不准确

**问题**：检测框不准确或出现多个框

**解决方案**：
- 提高置信度阈值：修改 `config.py` 中的 `confidence_threshold`
- 调整 NMS 阈值：在 `face_detector_onnx.py` 中修改
- 使用 Caffe SSD 模型：准确率更高

### 2. GPU 未启用

**问题**：系统使用 CPU 而非 GPU

**解决方案**：
- 检查 CUDA 是否正确安装
- 确认 `USE_GPU=true` 在 `.env` 中
- 检查 GPU 设备 ID 是否正确

### 3. WebSocket 连接失败

**问题**：前端无法连接 WebSocket

**解决方案**：
- 检查后端服务是否启动
- 确认防火墙未阻止 8000 端口
- 检查 `API.wsURL` 配置是否正确

### 4. 语音情绪分析不工作

**问题**：语音情绪分数全为 0

**解决方案**：
- 检查麦克风权限
- 确认 AudioWorklet 加载成功
- 检查音频采样率（应为 16000Hz）

### 5. 历史记录数据显示为空

**问题**：视频检测记录的关键字段为空

**解决方案**：
- 确保后端版本 >= v3.0.0
- 检查数据库迁移是否完成
- 重新进行视频检测（旧数据可能不兼容）

---

## 📝 开发规范

### 代码规范

#### Python (后端)

- 遵循 PEP 8 规范
- 使用类型注解
- 添加文档字符串
- 日志记录使用 logger

```python
def detect_faces(frame: np.ndarray, threshold: float = 0.6) -> List[Dict]:
    """检测人脸
    
    Args:
        frame: 输入图像
        threshold: 置信度阈值
        
    Returns:
        人脸列表
    """
    pass
```

#### JavaScript (前端)

- 使用 Vue 3 Composition API
- 组件命名使用 PascalCase
- 变量命名使用 camelCase
- 添加必要的注释

```javascript
// ✅ 好的命名
const dominantEmotion = ref('neutral')
const calculateAverage = (values) => { ... }

// ❌ 不好的命名
const a = ref('')
const func1 = (x) => { ... }
```

### Git 提交规范

使用语义化提交信息：

```
feat: 添加语音情绪分析功能
fix: 修复人脸检测框闪烁问题
docs: 更新 API 文档
style: 优化 UI 样式
refactor: 重构数据库模块
test: 添加单元测试
chore: 更新依赖版本
```

### 分支管理

- `main`: 主分支，稳定版本
- `develop`: 开发分支
- `feature/xxx`: 功能分支
- `hotfix/xxx`: 紧急修复分支

---

## 🚢 部署指南

### Docker 部署

#### 1. 构建镜像

```bash
docker-compose build
```

#### 2. 启动服务

```bash
docker-compose up -d
```

#### 3. 查看日志

```bash
docker-compose logs -f
```

#### 4. 停止服务

```bash
docker-compose down
```

### 生产环境部署

#### 后端部署 (使用 Gunicorn)

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动服务
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### 前端部署 (使用 Nginx)

1. 构建前端：

```bash
npm run build
```

2. Nginx 配置：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /var/www/face-emotion-ai/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 贡献步骤

1. **Fork 项目**
2. **创建功能分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'feat: Add AmazingFeature'`)
4. **推送到分支** (`git push origin feature/AmazingFeature`)
5. **创建 Pull Request**

### 贡献要求

- 代码符合项目规范
- 添加必要的测试
- 更新相关文档
- 通过 CI/CD 检查

---

##  许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- **OpenCV**: 图像处理库
- **ONNX**: 模型格式和运行时
- **FastAPI**: 高性能 Web 框架
- **Vue.js**: 渐进式 JavaScript 框架
- **Element Plus**: Vue 3 UI 组件库


---

## 📊 项目统计

![GitHub stars](https://img.shields.io/github/stars/YLJ109/FaceEmotion-AI?style=social)
![GitHub forks](https://img.shields.io/github/forks/YLJ109/FaceEmotion-AI?style=social)
![GitHub issues](https://img.shields.io/github/issues/YLJ109/FaceEmotion-AI)
![GitHub pull requests](https://img.shields.io/github/issues-pr/YLJ109/FaceEmotion-AI)

---

**Made with ❤️ by Your Team**
