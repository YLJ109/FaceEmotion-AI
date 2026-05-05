# 🎭 FaceEmotion-AI

> **智能面部情绪识别与多模态分析平台**  
> 基于深度学习的实时情绪检测系统，支持人脸情绪识别、语音情感分析、AI 音乐生成与自适应学习

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue.js-3.x-brightgreen.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 项目简介

FaceEmotion-AI 是一个全栈 AI 情绪识别系统，结合了计算机视觉、深度学习和前端可视化技术。系统能够实时检测和分析面部情绪，并提供智能化的情绪反馈与音乐推荐。

###  核心功能

- 🎯 **实时情绪检测**：基于摄像头的实时面部情绪识别，支持多张人脸同时检测
- 🖼️ **图片/视频批量处理**：支持上传图片或视频进行批量情绪分析
- 🎵 **AI 音乐生成**：根据检测到的情绪自动生成匹配的背景音乐
-  **自适应学习**：系统能够通过用户反馈不断优化识别准确率
-  **数据分析看板**：可视化的情绪趋势分析与用户行为统计
- 🎨 **多主题切换**：支持深色/浅色主题，Overwatch/禅意等多种 UI 风格
-  **响应式设计**：完美适配桌面端和移动端

### 🚀 技术亮点

- **高性能推理**：ONNX Runtime + GPU 加速，实时检测 FPS > 30
- **模型与代码分离**：创新的架构设计，模型文件独立管理
- **智能帧率控制**：动态调整检测频率，平衡性能与精度
- **WebSocket 实时通信**：低延迟的数据传输与状态同步
- **Docker 容器化**：一键部署，跨平台兼容

---

## 🛠️ 技术栈

### 前端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| [Vue 3](https://vuejs.org/) | 3.x | 核心框架（Composition API） |
| [Vite](https://vitejs.dev/) | 5.x | 构建工具与开发服务器 |
| [Element Plus](https://element-plus.org/) | 2.x | UI 组件库 |
| [Pinia](https://pinia.vuejs.org/) | 2.x | 状态管理 |
| [Axios](https://axios-http.com/) | 1.x | HTTP 客户端 |
| [ECharts](https://echarts.apache.org/) | 5.x | 数据可视化图表 |
| [Web Audio API](https://developer.mozilla.org/) | 原生 | 音频采集与处理 |

### 后端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| [FastAPI](https://fastapi.tiangolo.com/) | 0.100+ | Web 框架 |
| [Uvicorn](https://www.uvicorn.org/) | 0.23+ | ASGI 服务器 |
| [OpenCV](https://opencv.org/) | 4.x | 图像处理与人脸检测 |
| [ONNX Runtime](https://onnxruntime.ai/) | 1.x | 模型推理引擎 |
| [PyTorch](https://pytorch.org/) | 2.x | 深度学习框架 |
| [SQLAlchemy](https://www.sqlalchemy.org/) | 2.x | ORM 数据库管理 |
| [WebSockets](https://websockets.readthedocs.io/) | 11.x | 实时通信 |

### AI 模型

| 模型 | 类型 | 用途 | 大小 |
|------|------|------|------|
| `pytorch_final_3060.pth` | PyTorch | 情绪分类主模型 | 26.5 MB |
| `emotion_model.onnx` | ONNX | 情绪分类（推理优化） | 8.7 MB |
| `res10_300x300_ssd_iter_140000_fp16.caffemodel` | Caffe | 人脸检测（高精度） | 5.2 MB |
| `version-RFB-320.onnx` | ONNX | 人脸检测（快速） | 1.2 MB |
| `wav2vec2` | Transformer | 语音情感识别 | 645 MB |

---

## 📁 项目结构

```
FaceEmotion-AI/
├──  models/                          # 🎯 AI 模型文件（新架构）
│   ├── 📁 weights/                     # 模型权重文件
│   │   ├── pytorch_final_3060.pth
│   │   ├── emotion_model.onnx
│   │   ├── version-RFB-320.onnx
│   │   └── res10_300x300_ssd_iter_140000_fp16.caffemodel
│   ├──  configs/                     # 模型配置文件
│   │   ├── deploy.prototxt
│   │   └── haarcascade_frontalface_default.xml
│   └── 📁 docs/                        # 模型文档
│       └── MODEL_MIGRATION_GUIDE.md
│
├── 📁 backend/                         # 🔧 后端服务
│   ├── 📁 api/                         # API 路由层
│   │   ├── __init__.py
│   │   ├── detection.py                # 检测接口
│   │   ├── history.py                  # 历史记录接口
│   │   └── analytics.py                # 数据分析接口
│   ├── 📁 models/                      # Python 模型代码
│   │   ├── detector.py                 # 人脸检测器
│   │   ├── emotion_classifier.py       # 情绪分类器
│   │   ├── emotion_classifier_onnx.py  # ONNX 分类器
│   │   └── face_detector_onnx.py       # ONNX 人脸检测
│   ├──  adaptation/                  # 自适应学习模块
│   │   ├── active_learner.py
│   │   └── enhanced_learner.py
│   ├──  analytics/                   # 数据分析模块
│   │   └── user_analytics.py
│   ├── 📁 multimodal/                  # 多模态分析
│   │   └── voice_analyzer.py
│   ├── 📁 music/                       # AI 音乐生成
│   │   ── music_generator.py
│   ├── 📁 optimizer/                   # 性能优化器
│   │   └── dynamic_inference.py
│   ├── 📁 data/                        # 数据目录
│   │   ├── emotion.db                  # 主数据库
│   │   ├── face_emotion.db             # 人脸数据库
│   │   ├── screenshots/                # 截图缓存
│   │   └── uploads/                    # 上传文件
│   ├── 📁 scripts/                     # 工具脚本
│   │   └── convert_to_onnx.py          # 模型转换
│   ├── app.py                          # 🚀 应用入口
│   ├── config.py                       # 配置管理器
│   ├── config.json                     # 配置文件
│   ├── constants.py                    # 常量定义
│   ├── database.py                     # 数据库管理
│   ├── requirements.txt                # Python 依赖
│   └── Dockerfile                      # Docker 配置
│
├── 📁 frontend/                        # 🎨 前端应用
│   ├── 📁 src/
│   │   ├── 📁 api/                     # API 客户端层
│   │   │   ├── http.js                 # Axios 封装
│   │   │   ├── websocket.js            # WebSocket 客户端
│   │   │   └── modules/                # 业务 API 模块
│   │   │       ├── detection.js
│   │   │       ├── history.js
│   │   │       ├── analytics.js
│   │   │       └── system.js
│   │   ├── 📁 components/              # Vue 组件
│   │   │   ├── 📁 common/              # 通用组件
│   │   │   │   ├── EmotionSVG.vue
│   │   │   │   ├── FpsDisplay.vue
│   │   │   │   └── ThemeSelector.vue
│   │   │   ├── 📁 detection/           # 检测组件
│   │   │   │   ├── RealtimeDetector.vue
│   │   │   │   ├── ImageDetector.vue
│   │   │   │   ├── VideoDetector.vue
│   │   │   │   └── BatchDetector.vue
│   │   │   ├── 📁 layout/              # 布局组件
│   │   │   │   ├── AppHeader.vue
│   │   │   │   └── AppSidebar.vue
│   │   │   ├── 📁 analytics/           # 分析组件
│   │   │   │   └── AnalyticsDashboard.vue
│   │   │   └── 📁 feedback/            # 反馈组件
│   │   │       ├── EmotionFeedback.vue
│   │   │       └── HistoryViewer.vue
│   │   ├── 📁 stores/                  # Pinia 状态管理
│   │   │   ├── theme.js
│   │   │   ├── audio.js
│   │   │   └── analytics.js
│   │   ├── 📁 utils/                   # 工具函数
│   │   │   ├── emotion.js
│   │   │   ├── audioCapture.js
│   │   │   ├── canvas.js
│   │   │   └── analytics.js
│   │   ├── 📁 styles/                  # 样式文件
│   │   │   ├── global.css
│   │   │   ├── element-overwatch.css
│   │   │   └── components.css
│   │   ├── 📁 themes/                  # 主题配置
│   │   │   └── index.js
│   │   ├── App.vue                     # 根组件
│   │   └── main.js                     # 入口文件
│   ├── 📁 public/                      # 静态资源
│   ├── 📁 data/                        # 前端数据缓存
│   ├── index.html                      # HTML 入口
│   ├── vite.config.js                  # Vite 配置
│   ├── package.json                    # Node 依赖
│   ├── nginx.conf                      # Nginx 配置
│   └── Dockerfile                      # Docker 配置
│
├── 📁 wav2vac2/                        # 🎤 语音模型（可选）
│   ├── model.safetensors
│   ├── config.json
│   └── preprocessor_config.json
│
├── .gitignore                          # Git 忽略规则
├── docker-compose.yml                  # Docker Compose 配置
└── README.md                           # 项目文档
```

### 📌 架构说明

#### 模型与代码分离架构

本项目采用**模型文件与代码分离**的创新架构：

- **`models/weights/`**：存放所有模型权重文件（`.pth`, `.onnx`, `.caffemodel`）
- **`models/configs/`**：存放模型配置文件（`.prototxt`, `.xml`）
- **`backend/models/`**：仅保留 Python 模型代码，不含权重文件

**优势**：
- ✅ Git 仓库体积小（不追踪大文件）
- ✅ 模型文件独立管理，便于版本控制
- ✅ 支持多环境模型切换（开发/生产）
- ✅ 便于模型更新与热替换

---

## 🚀 环境准备

### 系统要求

| 组件 | 最低要求 | 推荐配置 |
|------|---------|---------|
| **操作系统** | Windows 10+ / macOS / Linux | Windows 11 / Ubuntu 22.04 |
| **Python** | 3.10+ | 3.12 |
| **Node.js** | 18+ | 20 LTS |
| **GPU**（可选） | - | NVIDIA RTX 3060+（6GB+ 显存） |
| **内存** | 8 GB | 16 GB+ |
| **磁盘空间** | 5 GB | 10 GB+（含模型文件） |

### 1️⃣ 安装 Python 环境

#### Windows PowerShell

```powershell
# 1. 克隆项目
git clone https://github.com/your-username/FaceEmotion-AI.git
cd FaceEmotion-AI

# 2. 创建虚拟环境
python -m venv .venv

# 3. 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 4. 安装后端依赖
cd backend
pip install -r requirements.txt
```

#### macOS / Linux

```bash
# 1. 克隆项目
git clone https://github.com/your-username/FaceEmotion-AI.git
cd FaceEmotion-AI

# 2. 创建虚拟环境
python3 -m venv .venv

# 3. 激活虚拟环境
source .venv/bin/activate

# 4. 安装后端依赖
cd backend
pip install -r requirements.txt
```

### 2️⃣ 安装 Node.js 环境

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 或使用 yarn
yarn install
```

### 3️⃣ 模型文件准备

⚠️ **重要**：由于模型文件较大（约 42 MB），**不会包含在 Git 仓库中**。

#### 获取模型文件

1. **从项目维护者处下载**
   - 联系项目作者获取模型文件包
   - 或使用提供的下载链接

2. **下载后放置位置**
   ```
   models/
   ├── weights/
   │   ├── pytorch_final_3060.pth          (26.5 MB)
   │   ├── emotion_model.onnx              (8.7 MB)
   │   ├── version-RFB-320.onnx            (1.2 MB)
   │   └── res10_300x300_ssd_iter_140000_fp16.caffemodel (5.2 MB)
   └── configs/
       ├── deploy.prototxt                 (29.2 KB)
       └── haarcascade_frontalface_default.xml (908.3 KB)
   ```

3. **详细指南**
   
   查看完整迁移指南：[models/docs/MODEL_MIGRATION_GUIDE.md](models/docs/MODEL_MIGRATION_GUIDE.md)

### 4️⃣ （可选）语音模型

如需启用语音情绪识别功能，需额外下载 wav2vec2 模型：

```bash
# 模型将自动下载到 wav2vac2/ 目录
cd backend
python download_wav2vec2.py
```

⚠️ **注意**：语音模型较大（645 MB），默认不启用。

---

## ⚡ 快速启动

### 方式一：开发模式启动

#### 1. 启动后端服务

```powershell
# Windows PowerShell
cd backend
.\.venv\Scripts\python.exe app.py
```

```bash
# macOS / Linux
cd backend
source .venv/bin/activate
python app.py
```

**成功输出示例**：
```
2026-05-06 00:28:02 | INFO    | __main__ - 🚀 AI情感检测系统 V3.0.0 启动中...
2026-05-06 00:28:02 | INFO    | __main__ - ✅ GPU: NVIDIA GeForce RTX 3060 Laptop GPU (6.0 GB)
2026-05-06 00:28:02 | INFO    | __main__ - ✅ 人脸检测器加载成功
2026-05-06 00:28:02 | INFO    | __main__ - ✅ ONNX情感分类器加载成功
2026-05-06 00:28:02 | INFO    | __main__ - ✅ 数据库初始化完成
2026-05-06 00:28:02 | INFO    | uvicorn.error - Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### 2. 启动前端服务

```bash
# 打开新终端
cd frontend

# 启动开发服务器
npm run dev

# 或
yarn dev
```

**成功输出示例**：
```
VITE v5.0.0  ready in 500 ms

➜  Local:   http://localhost:5173/
➜  Network: http://192.168.1.100:5173/
➜  press h + enter to show help
```

#### 3. 访问应用

打开浏览器访问：http://localhost:5173

---

### 方式二：Docker 一键部署

#### 前置要求

- 已安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- （可选）已安装 [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/)

#### 启动命令

```bash
# 1. 构建并启动所有服务
docker-compose up --build -d

# 2. 查看服务状态
docker-compose ps

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose down
```

#### 访问地址

- **前端**：http://localhost:80
- **后端 API**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs

#### Docker 配置说明

编辑 `docker-compose.yml` 可自定义配置：

```yaml
services:
  backend:
    environment:
      - USE_GPU=true              # 启用 GPU（需 NVIDIA Container Toolkit）
      - LOG_LEVEL=info            # 日志级别
      - MAX_WORKERS=4             # 工作线程数
    volumes:
      - ./models:/app/models      # 挂载模型文件
      - ./backend/data:/app/data  # 持久化数据
```

---

## 🎯 功能特性

### 1.  实时情绪检测

- **多张人脸检测**：支持同时检测多张人脸（最多 10 张）
- **实时预览**：Canvas 绘制检测框与情绪标签
- **性能监控**：实时显示 FPS、延迟、跳帧率等指标
- **智能优化**：动态调整检测频率，保持流畅体验

**使用步骤**：
1. 选择"实时检测"模式
2. 允许摄像头权限
3. 系统自动开始检测
4. 查看实时情绪分析结果

### 2. ️ 图片检测

- **单张图片分析**：上传图片进行情绪识别
- **多张批量处理**：支持同时上传多张图片
- **检测框显示/隐藏**：可切换显示情绪标签
- **结果导出**：支持 JSON/CSV 格式导出

### 3. 🎬 视频检测

- **视频文件上传**：支持 MP4、AVI 等常见格式
- **逐帧分析**：自动提取关键帧进行情绪检测
- **时间轴展示**：情绪变化趋势可视化
- **进度条控制**：可暂停/继续/跳转

### 4.  批量检测

- **多文件上传**：支持图片和视频混合上传
- **异步处理**：后台批量处理，不阻塞 UI
- **进度追踪**：实时显示处理进度
- **统一结果**：整合所有检测结果

### 5. 📊 数据分析看板

- **情绪趋势图**：最近 7 天情绪变化趋势
- **情绪分布**：各类情绪占比饼图
- **转换矩阵**：情绪转换热力图
- **用户统计**：使用时长、检测次数等

### 6.  AI 自适应学习

- **用户反馈**：纠正错误的情绪识别结果
- **主动学习**：系统自动收集困难样本
- **模型微调**：定期使用新数据优化模型
- **场景适应**：根据使用场景自动调整

### 7. 🎵 AI 音乐生成

- **情绪匹配**：根据情绪自动生成背景音乐
- **风格多样**：支持古典、爵士、电子等多种风格
- **实时切换**：情绪变化时自动切换音乐
- **音量控制**：可调节背景音乐音量

### 8. 🎨 主题切换

- **深色/浅色模式**：支持自动/手动切换
- **多种主题**：Overwatch、禅意、赛博朋克等
- **记忆偏好**：自动保存用户主题选择
- **全局适配**：所有组件统一主题风格

---

## ⚙️ 配置说明

### 后端配置 (`backend/config.json`)

```json
{
  // 服务器配置
  "host": "0.0.0.0",                  // 监听地址
  "port": 8000,                       // 监听端口
  "debug": false,                     // 调试模式
  
  // AI 模型配置
  "use_gpu": true,                    // 启用 GPU 加速
  "model_path": "../models/weights/pytorch_final_3060.pth",  // 情绪模型路径
  "face_detector_model": "../models/weights/res10_300x300_ssd_iter_140000_fp16.caffemodel",  // 人脸检测模型
  "emotion_model": "../models/weights/emotion_model.onnx",   // ONNX 情绪模型
  "use_onnx_face_detector": false,    // 使用 ONNX 人脸检测器
  "confidence_threshold": 0.6,        // 置信度阈值（0.0-1.0）
  
  // 性能配置
  "max_workers": 4,                   // 工作线程数
  "send_width": 160,                  // 发送图像宽度
  "send_height": 120,                 // 发送图像高度
  "frame_skip_threshold": 2,          // 跳帧阈值
  "ema_alpha": 0.15,                  // EMA 平滑系数
  
  // WebSocket 配置
  "ws_max_connections": 10,           // 最大连接数
  "ws_heartbeat_interval": 30,        // 心跳间隔（秒）
  
  // 数据库配置
  "database_url": "sqlite:///./data/emotion.db",
  "db_pool_size": 5,
  "db_max_overflow": 10
}
```

### 环境变量 (`.env`)

创建 `backend/.env` 文件覆盖默认配置：

```bash
# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=info

# GPU 配置
USE_GPU=true

# 模型路径（可选，覆盖 config.json）
MODEL_PATH=../models/weights/pytorch_final_3060.pth
FACE_DETECTOR_MODEL=../models/weights/res10_300x300_ssd_iter_140000_fp16.caffemodel
EMOTION_MODEL=../models/weights/emotion_model.onnx

# 性能配置
MAX_WORKERS=4
SEND_WIDTH=160
SEND_HEIGHT=120
EMA_ALPHA=0.15

# 数据库配置
DATABASE_URL=sqlite:///./data/emotion.db
```

### 前端配置 (`frontend/.env`)

```bash
# API 地址
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws/stream

# 功能开关
VITE_ENABLE_GPU=true
VITE_ENABLE_AUDIO=false
VITE_ENABLE_ANALYTICS=true

# 性能配置
VITE_MAX_FPS=30
VITE_SEND_WIDTH=160
VITE_SEND_HEIGHT=120
VITE_EMA_ALPHA=0.15

# UI 配置
VITE_APP_TITLE=FaceEmotion-AI
VITE_DEFAULT_THEME=zen
```

---

## ❓ 常见问题 (FAQ)

### Q1: 启动时报错 "ONNX模型不存在"

**错误信息**：
```
RuntimeError: ONNX模型不存在: D:\front-back\FaceEmotion-AI\backend\models\emotion_model.onnx
```

**解决方案**：
1. 确认模型文件已放置在正确位置：
   ```
   models/weights/emotion_model.onnx  ✅
   ```
2. 检查 `backend/config.json` 中的路径配置：
   ```json
   "emotion_model": "../models/weights/emotion_model.onnx"
   ```
3. 确保从 `backend/` 目录启动服务（相对路径基于此）

---

### Q2: 端口 8000 已被占用

**错误信息**：
```
Error: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000)
```

**解决方案**：
```powershell
# Windows：查找占用端口的进程
netstat -ano | findstr :8000

# 终止进程（替换 PID）
taskkill /PID <PID> /F

# 或修改 config.json 中的端口
"port": 8001
```

---

### Q3: 前端无法连接后端

**现象**：前端显示 "网络连接失败"

**解决方案**：
1. 检查后端是否正常运行：
   ```bash
   curl http://localhost:8000/health
   ```
2. 确认前端配置正确：
   ```bash
   # frontend/.env
   VITE_API_URL=http://localhost:8000
   ```
3. 检查 CORS 配置：
   ```json
   // backend/config.json
   "cors_origins": ["http://localhost:5173", "http://localhost:80"]
   ```

---

### Q4: GPU 未启用，使用 CPU 推理

**现象**：日志显示 "⚠️ 人脸检测器使用 CPU"

**解决方案**：
1. 确认已安装 CUDA 版本的 PyTorch：
   ```bash
   python -c "import torch; print(torch.cuda.is_available())"
   ```
2. 检查配置：
   ```json
   "use_gpu": true
   ```
3. 安装 GPU 版本依赖：
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

---

### Q5: 依赖安装失败

**常见错误**：
```
ERROR: Could not find a version that satisfies the requirement onnxruntime-gpu
```

**解决方案**：
```bash
# 方法 1：使用 CPU 版本
pip install onnxruntime

# 方法 2：指定 Python 版本
pip install --only-binary :all: onnxruntime-gpu

# 方法 3：使用 conda
conda install -c conda-forge onnxruntime-gpu
```

---

### Q6: 摄像头无法访问

**现象**：实时检测显示黑屏

**解决方案**：
1. 检查摄像头权限：
   - Windows：设置 > 隐私 > 摄像头
   - macOS：系统偏好设置 > 安全性与隐私 > 摄像头
2. 修改摄像头索引：
   ```json
   // backend/config.json
   "camera_index": 0  // 尝试 0, 1, 2
   ```
3. 测试摄像头：
   ```python
   import cv2
   cap = cv2.VideoCapture(0)
   print(cap.isOpened())
   ```

---

### Q7: Docker 部署时模型文件未加载

**现象**：容器启动时报错 "模型文件不存在"

**解决方案**：
修改 `docker-compose.yml`：
```yaml
services:
  backend:
    volumes:
      - ./models:/app/models      # ✅ 挂载模型目录
      - ./backend/data:/app/data
```

或使用 Dockerfile 复制：
```dockerfile
COPY ../models /app/models
```

---

### Q8: 数据库锁定错误

**错误信息**：
```
sqlite3.OperationalError: database is locked
```

**解决方案**：
1. 增加连接池大小：
   ```json
   "db_pool_size": 10,
   "db_max_overflow": 20
   ```
2. 清理旧进程：
   ```bash
   # Windows
   taskkill /F /IM python.exe
   
   # Linux
   pkill -f app.py
   ```
3. 删除锁定文件：
   ```bash
   rm backend/data/emotion.db-journal
   ```

---

## 🤝 贡献指南

### 代码规范

#### Python 代码

- 遵循 [PEP 8](https://peps.python.org/pep-0008/) 风格指南
- 使用类型注解（Type Hints）
- 函数和类添加文档字符串（Docstrings）
- 使用 `black` 格式化代码：
  ```bash
  black backend/
  ```

#### Vue 代码

- 使用 Composition API
- 组件命名使用 PascalCase（如 `RealtimeDetector.vue`）
- Props 和 Emits 明确声明类型
- 使用 ESLint + Prettier：
  ```bash
  npm run lint
  npm run format
  ```

### Git 工作流

```bash
# 1. Fork 项目
# 2. 创建功能分支
git checkout -b feat/your-feature-name

# 3. 提交代码
git add .
git commit -m "feat: add your feature description"

# 4. 推送分支
git push origin feat/your-feature-name

# 5. 创建 Pull Request
```

### 提交信息规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Type 类型**：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具链相关

**示例**：
```
feat(detection): add multi-face support for real-time detection

fix(api): resolve CORS error on WebSocket connection

docs(readme): update installation guide with Docker steps
```

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

```
Copyright (c) 2026 FaceEmotion-AI Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

---

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 优秀的 Python Web 框架
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [OpenCV](https://opencv.org/) - 计算机视觉库
- [ONNX Runtime](https://onnxruntime.ai/) - 跨平台推理引擎
- [Element Plus](https://element-plus.org/) - Vue 3 组件库
- [ECharts](https://echarts.apache.org/) - 数据可视化库

---

## 📬 联系方式

- **项目地址**：https://github.com/YLJ109/FaceEmotion-AI
- **问题反馈**：[GitHub Issues](https://github.com/YLJ109/FaceEmotion-AI/issues)
- **邮箱**：2869563610@qq.com

---

## ⭐ Star History

如果这个项目对你有帮助，请给它一个 Star ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=YLJ109/FaceEmotion-AI&type=Date)](https://star-history.com/#YLJ109/FaceEmotion-AI&Date)

---

**最后更新**: 2026-05-06  
**版本**: V1.9.0  
**维护者**: FaceEmotion-AI Team
