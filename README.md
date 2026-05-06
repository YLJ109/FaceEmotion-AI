#  FaceEmotion-AI

> **智能面部情绪识别系统**  
> 基于深度学习的实时情绪检测平台，支持多模态人脸情绪识别、AI 自适应学习与可视化数据分析

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue.js-3.5-brightgreen.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 项目简介

FaceEmotion-AI 是一个全栈 AI 情绪识别系统，结合了计算机视觉、深度学习和前端可视化技术。系统能够实时检测和分析面部情绪，提供智能化的情绪反馈、自适应学习与数据可视化分析。

### 🔥 核心功能

- 🎯 **实时情绪检测**：基于摄像头的实时面部情绪识别，支持多张人脸同时检测（最多10张）
- 🖼️ **图片检测**：支持单张图片情绪分析，自动保存历史记录
- 🎬 **视频检测**：支持视频文件逐帧分析，关键帧情绪提取与时间轴展示
- 📦 **批量图片检测**：支持多张图片并发处理，统一结果展示
- 🎥 **批量视频检测**：支持多个视频并发处理，关键帧情绪分析与统计报告
- 🔄 **AI 自适应学习**：系统通过用户反馈不断优化识别准确率，支持场景自适应
- 📊 **数据分析看板**：6种可视化图表的情绪趋势分析与用户行为统计
  - 📈 情绪变化趋势（折线图）
  - 🥧 情绪分布统计（饼图）
  - 🌹 检测类型分布（南丁格尔玫瑰图）
  - 📊 置信度分布（柱状图）
  - 🔀 情绪转换矩阵（桑基图）
  - 📉 检测类型趋势（面积图）
-  **多主题切换**：支持深色/浅色主题，Overwatch/禅意等多种 UI 风格
- 📱 **响应式设计**：完美适配桌面端和移动端
- 📝 **历史档案管理**：完整的检测历史记录，支持筛选、查看与反馈

### 🚀 技术亮点

- **纯 ONNX 推理**：基于 ONNX Runtime 的高效推理引擎，无需 PyTorch 依赖
- **纯 CPU 运行**：开箱即用，无需 CUDA/GPU 环境，跨平台兼容
- **智能帧率控制**：动态调整检测频率，平衡性能与精度
- **WebSocket 实时通信**：低延迟的数据传输与状态同步
- **智能数据过滤**：自动过滤空检测结果，避免无效数据入库
- **完善的错误处理**：友好的错误提示与文件类型验证
- **Docker 容器化**：一键部署，标准化运行环境

---

## 🛠️ 技术栈

### 前端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| [Vue 3](https://vuejs.org/) | 3.5 | 核心框架（Composition API） |
| [Vite](https://vitejs.dev/) | 8.x | 构建工具与开发服务器 |
| [Element Plus](https://element-plus.org/) | 2.13 | UI 组件库 |
| [Pinia](https://pinia.vuejs.org/) | 3.0 | 状态管理 |
| [Vue Router](https://router.vuejs.org/) | 4.6 | 路由管理 |
| [Axios](https://axios-http.com/) | 1.15 | HTTP 客户端 |
| [ECharts](https://echarts.apache.org/) | 6.0 | 数据可视化图表 |

### 后端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| [FastAPI](https://fastapi.tiangolo.com/) | 0.109 | Web 框架 |
| [Uvicorn](https://www.uvicorn.org/) | 0.27 | ASGI 服务器 |
| [OpenCV](https://opencv.org/) | 4.13 | 图像处理与人脸检测 |
| [ONNX Runtime](https://onnxruntime.ai/) | 1.19 | 模型推理引擎（CPU） |
| [NumPy](https://numpy.org/) | 2.0 | 数值计算 |
| [Pydantic](https://docs.pydantic.dev/) | 2.5 | 数据验证 |
| [WebSockets](https://websockets.readthedocs.io/) | 12.0 | 实时通信 |

### AI 模型

| 模型 | 类型 | 用途 | 大小 |
|------|------|------|------|
| `emotion_model.onnx` | ONNX | 情绪分类（7种表情） | 8.7 MB |
| `res10_300x300_ssd_iter_140000_fp16.caffemodel` | Caffe | 人脸检测（高精度） | 5.2 MB |
| `version-RFB-320.onnx` | ONNX | 人脸检测（快速模式，备用） | 1.2 MB |

**说明**：
- ✅ 本项目已完全移除 PyTorch 依赖，使用纯 ONNX 推理
- ✅ 无需 CUDA/cuDNN，纯 CPU 运行，开箱即用
- ✅ 支持 7 种情绪识别：开心、悲伤、愤怒、惊讶、恐惧、厌恶、平静

---

## 📁 项目结构

```
FaceEmotion-AI/
├── backend/                          # 🔧 后端服务
│   ├── api/                          # API 路由层
│   │   ├── __init__.py               # 路由注册
│   │   ├── ai_features.py            # AI 功能接口（反馈、学习、分析）
│   │   ├── detection.py              # 检测接口（图片/视频/批量）
│   │   ├── history.py                # 历史记录接口
│   │   ├── system.py                 # 系统接口（配置、健康检查）
│   │   └── websocket.py              # WebSocket 接口（实时流）
│   ├── models/                       # Python 模型代码
│   │   ├── detector.py               # 人脸检测器（Caffe/ONNX）
│   │   └── emotion_classifier_onnx.py # ONNX 情绪分类器
│   ├── core/                         # 核心模块
│   │   ├── __init__.py
│   │   ├── config.py                 # 配置管理器
│   │   ├── constants.py              # 常量定义
│   │   └── database.py               # 数据库管理（SQLite）
│   ├── adaptation/                   # 自适应学习模块
│   │   ├── __init__.py
│   │   ├── active_learner.py         # 标准版自适应学习器
│   │   ├── enhanced_learner.py       # 增强版自适应学习器
│   │   └── calibration_state.json    # 校准状态
│   ├── analytics/                    # 数据分析模块
│   │   ├── __init__.py
│   │   ── user_analytics.py         # 用户行为分析
│   ├── optimizer/                    # 性能优化器
│   │   ├── __init__.py
│   │   └── dynamic_inference.py      # 动态推理优化
│   ├── music/                        # AI 音乐生成（已移除）
│   │   └── __init__.py
│   ├── data/                         # 数据目录
│   │   ├── emotion.db                # SQLite 主数据库
│   │   ├── screenshots/              # 截图缓存
│   │   └── uploads/                  # 上传文件临时目录
│   ├── weights/                      # 模型权重文件
│   │   ├── emotion_model.onnx        # 情绪分类模型
│   │   └── res10_300x300_ssd_iter_140000_fp16.caffemodel # 人脸检测模型
│   ├── configs/                      # 模型配置文件
│   │   └── deploy.prototxt           # Caffe 网络配置
│   ├── app.py                        # 🚀 应用入口
│   ├── config.json                   # 配置文件
│   ├── requirements.txt              # Python 依赖
│   ── Dockerfile                    # Docker 配置
│
├── frontend/                         # 🎨 前端应用
│   ├── src/
│   │   ├── api/                      # API 客户端层
│   │   │   ├── config.js             # API 配置
│   │   │   └── websocket.js          # WebSocket 客户端
│   │   ├── components/               # Vue 组件
│   │   │   ├── analytics/            # 分析组件
│   │   │   │   ── AnalyticsDashboard.vue
│   │   │   ├── common/               # 通用组件
│   │   │   ├── detection/            # 检测组件
│   │   │   │   ├── RealtimeDetector.vue      # 实时检测
│   │   │   │   ├── ImageDetector.vue         # 图片检测
│   │   │   │   ├── VideoDetector.vue         # 视频检测
│   │   │   │   ├── BatchDetector.vue         # 批量图片检测
│   │   │   │   ── BatchVideoDetector.vue    # 批量视频检测
│   │   │   ├── feedback/             # 反馈组件
│   │   │   ├── history/              # 历史组件
│   │   │   ├── layout/               # 布局组件
│   │   │   ├── monitor/              # 监控组件
│   │   │   ── pages/                # 页面组件
│   │   ├── stores/                   # Pinia 状态管理
│   │   │   └── theme.js              # 主题状态
│   │   ├── styles/                   # 样式文件
│   │   │   └── element-overwatch.css # Element Plus 主题样式
│   │   ├── themes/                   # 主题配置
│   │   │   └── index.js
│   │   ├── utils/                    # 工具函数
│   │   │   ├── analytics.js          # 数据分析工具
│   │   │   ├── audioEngine.js        # 音频引擎
│   │   │   ├── canvas.js             # Canvas 工具
│   │   │   ├── emotion.js            # 情绪处理工具
│   │   │   ├── generativeAudio.js    # 生成式音频
│   │   │   └── httpMonitor.js        # HTTP 监控
│   │   ├── App.vue                   # 根组件
│   │   ├── main.js                   # 入口文件
│   │   └── style.css                 # 全局样式
│   ├── public/                       # 静态资源
│   ├── data/                         # 前端数据缓存
│   ├── index.html                    # HTML 入口
│   ├── vite.config.js                # Vite 配置
│   ├── package.json                  # Node 依赖
│   ├── nginx.conf                    # Nginx 配置
│   └── Dockerfile                    # Docker 配置
│
├── test_image_video/                 # 测试文件目录
├── .gitignore                        # Git 忽略规则
├── docker-compose.yml                # Docker Compose 配置
└── README.md                         # 项目文档
```

### 📌 架构说明

#### 纯 ONNX 推理架构

本项目采用**纯 ONNX 推理**的轻量级架构：

- **`backend/weights/`**：存放所有模型权重文件（`.onnx`, `.caffemodel`）
- **`backend/models/`**：Python 模型代码，仅使用 ONNX Runtime 推理
- **`backend/core/`**：核心服务模块（配置、数据库、常量）
- **`backend/api/`**：RESTful API 路由层，模块化设计
- **无需 PyTorch**：所有模型已预转换为 ONNX 格式

**优势**：
- ✅ 依赖简单，无需安装 PyTorch/CUDA
- ✅ 推理速度快，ONNX Runtime 高度优化
- ✅ 跨平台兼容，Windows/macOS/Linux 均可运行
- ✅ 内存占用低，适合部署到资源受限环境
- ✅ 模块化架构，易于扩展和维护

---

## 🚀 环境准备

### 系统要求

| 组件 | 最低要求 | 推荐配置 |
|------|---------|---------|
| **操作系统** | Windows 10+ / macOS / Linux | Windows 11 / Ubuntu 22.04 |
| **Python** | 3.10+ | 3.12 |
| **Node.js** | 18+ | 20 LTS |
| **GPU** | 无需 GPU | 纯 CPU 运行 |
| **内存** | 4 GB | 8 GB+ |
| **磁盘空间** | 2 GB | 5 GB+（含模型文件） |

### 1️⃣ 安装 Python 环境

#### Windows PowerShell

```powershell
# 1. 克隆项目
git clone https://github.com/YLJ109/FaceEmotion-AI.git
cd FaceEmotion-AI

# 2. 创建虚拟环境
python -m venv backend\.venv

# 3. 激活虚拟环境
backend\.venv\Scripts\Activate.ps1

# 4. 安装后端依赖
cd backend
pip install -r requirements.txt
```

#### macOS / Linux

```bash
# 1. 克隆项目
git clone https://github.com/YLJ109/FaceEmotion-AI.git
cd FaceEmotion-AI

# 2. 创建虚拟环境
python3 -m venv backend/.venv

# 3. 激活虚拟环境
source backend/.venv/bin/activate

# 4. 安装后端依赖
cd backend
pip install -r requirements.txt
```

### 2️ 安装 Node.js 环境

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
```

### 3️ 模型文件准备

✅ **模型文件已包含在项目中**，无需额外下载！

模型文件位置：
```
backend/weights/
├── emotion_model.onnx                              (8.7 MB)
└── res10_300x300_ssd_iter_140000_fp16.caffemodel   (5.2 MB)
```

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
2026-05-07 00:00:00 | INFO | __main__ - 🚀 AI情感检测系统 V3.0.0 启动中...
2026-05-07 00:00:00 | INFO | __main__ - ✅ Caffe 人脸检测器加载完成 (1.23s, CPU)
2026-05-07 00:00:00 | INFO | __main__ - ✅ ONNX 情绪识别模型加载完成 (0.87s, CPU, 7种表情)
2026-05-07 00:00:00 | INFO | __main__ - ✅ 数据库初始化完成
2026-05-07 00:00:00 | INFO | __main__ - ✅ AI 自适应学习引擎就绪（标准版）
2026-05-07 00:00:00 | INFO | __main__ - ✅ AI用户行为分析器就绪
2026-05-07 00:00:00 | INFO | __main__ - ✅ AI推理优化引擎就绪
2026-05-07 00:00:00 | INFO | uvicorn.error - Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### 2. 启动前端服务

```bash
# 打开新终端
cd frontend

# 启动开发服务器
npm run dev
```

**成功输出示例**：
```
VITE v8.0.0  ready in 500 ms

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
      - LOG_LEVEL=info            # 日志级别
      - MAX_WORKERS=4             # 工作线程数
    volumes:
      - ./backend/weights:/app/backend/weights  # 挂载模型文件
      - ./backend/data:/app/backend/data        # 持久化数据
```

---

## 🎯 功能特性

### 1. 🎯 实时情绪检测

- **多张人脸检测**：支持同时检测多张人脸（最多 10 张）
- **实时预览**：Canvas 绘制检测框与情绪标签
- **性能监控**：实时显示 FPS、延迟、跳帧率等指标
- **智能优化**：动态调整检测频率，保持流畅体验
- **手动保存**：支持手动保存当前检测结果到历史档案

**使用步骤**：
1. 选择"实时检测"模式
2. 允许摄像头权限
3. 系统自动开始检测
4. 查看实时情绪分析结果

### 2. 🖼️ 图片检测

- **单张图片分析**：上传图片进行情绪识别
- **检测框显示/隐藏**：可切换显示情绪标签
- **自动保存历史**：检测结果自动归档
- **空结果过滤**：未检测到人脸时自动过滤，不保存无效记录

### 3. 🎬 视频检测

- **视频文件上传**：支持 MP4、AVI 等常见格式
- **逐帧分析**：自动提取关键帧进行情绪检测
- **时间轴展示**：情绪变化趋势可视化
- **进度控制**：可暂停/继续/跳转
- **音乐同步**：根据情绪变化自动调整背景音乐（基于生成式音频引擎）

### 4. 📦 批量图片检测

- **多图片并发**：支持同时上传多张图片
- **进度显示**：实时显示处理进度
- **统一结果展示**：所有检测结果集中展示
- **智能过滤**：自动跳过未检测到人脸的图片

### 5. 🎥 批量视频检测

- **多视频并发**：支持同时处理多个视频
- **关键帧提取**：自动选择代表性帧进行分析
- **情绪统计**：生成视频情绪分布报告
- **批量历史保存**：所有视频检测结果自动归档

### 6. 📊 数据分析看板

- **情绪趋势图**：最近 7 天情绪变化趋势（折线图）
- **情绪分布**：各类情绪占比统计（饼图）
- **检测类型分布**：各检测类型占比（南丁格尔玫瑰图）
- **置信度分布**：检测置信度统计（柱状图）
- **情绪转换矩阵**：情绪转换关系可视化（桑基图）
- **检测类型趋势**：各类型检测趋势（面积图）
- **实时更新**：数据随新检测结果自动刷新

### 7. 🔄 AI 自适应学习

- **用户反馈**：纠正错误的情绪识别结果
- **主动学习**：系统自动收集困难样本
- **校准矩阵**：基于历史反馈的情绪校准
- **场景适应**：根据使用场景自动调整（增强版）
- **遗忘机制**：避免过时数据影响（增强版）

### 8. 🎨 主题切换

- **深色/浅色模式**：支持自动/手动切换
- **多种主题**：Overwatch、禅意等多种 UI 风格
- **记忆偏好**：自动保存用户主题选择
- **全局适配**：所有组件统一主题风格
- **平滑过渡**：主题切换带有过渡动画

---

## ️ 配置说明

### 后端配置 (`backend/config.json`)

```json
{
  // 服务器配置
  "host": "0.0.0.0",                  // 监听地址
  "port": 8000,                       // 监听端口
  "debug": false,                     // 调试模式
  "log_level": "info",                // 日志级别
  
  // AI 模型配置
  "use_gpu": true,                    // GPU 使用开关（当前使用 CPU）
  "emotion_model": "../weights/emotion_model.onnx",   // ONNX 情绪模型
  "face_detector_model": "../weights/res10_300x300_ssd_iter_140000_fp16.caffemodel",  // 人脸检测模型
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

### 前端配置 (`frontend/vite.config.js`)

```javascript
export default {
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true
      }
    }
  }
}
```

---

## ❓ 常见问题 (FAQ)

### Q1: 启动时报错 "模型文件不存在"

**错误信息**：
```
RuntimeError: 模型文件不存在: D:\front-back\FaceEmotion-AI\backend\weights\emotion_model.onnx
```

**解决方案**：
1. 确认模型文件存在于正确位置：
   ```
   backend/weights/emotion_model.onnx  ✅
   backend/weights/res10_300x300_ssd_iter_140000_fp16.caffemodel  ✅
   ```
2. 检查 `backend/config.json` 中的路径配置是否正确
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
2. 确认前端 API 配置正确：
   ```javascript
   // frontend/src/api/config.js
   API_BASE_URL: 'http://localhost:8000'
   ```
3. 检查 CORS 配置：
   ```json
   // backend/app.py
   allow_origins: ["http://localhost:5173", "http://localhost:80"]
   ```

---

### Q4: 如何启用 GPU 加速？

**说明**：本项目默认使用 CPU 推理，如需 GPU 加速：

**解决方案**：
1. 修改 `backend/requirements.txt`：
   ```
   # 将这一行
   onnxruntime==1.19.0
   # 改为
   onnxruntime-gpu==1.19.0
   ```
2. 重新安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 确保已安装 CUDA 和 cuDNN
4. 修改 `backend/config.json`：
   ```json
   "use_gpu": true
   ```

---

### Q5: 摄像头无法访问

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

### Q6: 数据库锁定错误

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

### Q7: 检测结果保存失败

**现象**：检测完成但历史记录未保存

**解决方案**：
1. 检查是否检测到人脸（空结果会被自动过滤）
2. 查看浏览器控制台是否有错误提示
3. 检查后端日志是否有数据库写入错误
4. 确认数据库文件权限正确

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
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
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

**最后更新**: 2026-05-07  
**版本**: V3.0.0  
**维护者**: FaceEmotion-AI Team
