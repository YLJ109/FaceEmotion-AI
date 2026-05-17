# FaceEmotion-AI

> **智能面部情绪识别系统**
> 基于深度学习的实时情绪检测平台，支持多人脸情绪识别、AI 自适应学习与可视化数据分析

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue.js-3.5-brightgreen.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 项目简介

FaceEmotion-AI 是一个全栈 AI 情绪识别系统，结合了计算机视觉、深度学习和前端可视化技术。系统能够实时检测和分析面部情绪，提供智能化的情绪反馈、自适应学习与数据可视化分析。

### 📝 更新日志

**V3.2.0 (2026-05-18)**

- ✅ **人脸检测模型迁移**：MediaPipe FaceLandmarker → OpenCV DNN SSD，消除 MediaPipe 依赖，加载速度提升 10 倍（0.02s vs 0.2s）
- ✅ **多人脸实时追踪**：新增 FaceTracker 追踪器，支持同时检测和追踪最多 5 张人脸，基于中心点距离匹配防止 ID 跳变
- ✅ **多人脸编号显示**：多人脸时标签显示"人脸1"、"人脸2"编号，单人脸时保持简洁
- ✅ **三级性能模式**：GPU 加速 / CPU 高性能 / CPU 低性能，动态调整检测频率、分辨率和推理线程数
- ✅ **人脸框平滑优化**：浮点数平滑 + 抖动过滤（< 2px 不更新），GPU 模式平滑系数 0.55，CPU 模式 0.45，消除卡顿和抖动
- ✅ **情绪防抖机制**：EMA 平滑（alpha=0.5）+ 滞后阈值（0.15），避免情绪标签闪烁
- ✅ **代码精简**：检测服务从 200+ 行精简至 60 行，移除 12 个冗余文件
- ✅ **依赖精简**：移除 mediapipe 依赖，requirements.txt 仅保留核心依赖
- ✅ **数据库优化**：SQLite 启用 WAL 模式和 busy_timeout，提升并发性能
- ✅ **CORS 配置修复**：支持 5173/5174 双端口访问

**V3.1.0 (2026-05-08)**

- ✅ **WebSocket 稳定性修复**：修复 ping/pong 心跳检测、重连逻辑和关闭码
- ✅ **UI 体验优化**：侧边栏悬停提示、面包屑导航、SVG 图标替换
- ✅ **侧边栏功能增强**：收缩/展开动画、状态持久化

**V3.0.0 (2026-05-07)**

- ✅ **纯 ONNX 推理架构**：完全移除 PyTorch 依赖
- ✅ **AI 自适应学习**：标准版和增强版学习引擎
- ✅ **数据分析看板**：6 种可视化图表
- ✅ **多主题切换**：支持 Overwatch、禅意等主题
- ✅ **Docker 容器化部署**：一键启动

---

## 🔥 核心功能

| 功能模块 | 功能描述 | 状态 |
|---------|---------|------|
| 🎯 实时情绪检测 | 基于摄像头的实时面部情绪识别，支持多人脸同时追踪（最多5张） | ✅ |
| 🖼️ 图片检测 | 支持单张图片情绪分析，自动保存历史记录 | ✅ |
| 🎬 视频检测 | 支持视频文件逐帧分析，关键帧情绪提取与时间轴展示 | ✅ |
| 📦 批量图片检测 | 支持多张图片并发处理，统一结果展示 | ✅ |
| 🎥 批量视频检测 | 支持多个视频并发处理，关键帧情绪分析与统计报告 | ✅ |
| 🔄 AI 自适应学习 | 系统通过用户反馈不断优化识别准确率 | ✅ |
| 📊 数据分析看板 | 6种可视化图表的情绪趋势分析与用户行为统计 | ✅ |
| 🎨 多主题切换 | 支持深色/浅色主题，多种 UI 风格 | ✅ |
| 📱 响应式设计 | 完美适配桌面端和移动端 | ✅ |
| 📝 历史档案管理 | 完整的检测历史记录，支持筛选、查看与反馈 | ✅ |
| 📝 文本情绪分析 | 基于文本内容的情绪倾向分析 | ✅ |

### 📊 数据分析看板功能

- 📈 **情绪变化趋势**：折线图展示最近7天情绪变化
- 🥧 **情绪分布统计**：饼图展示各类情绪占比
- 🌹 **检测类型分布**：南丁格尔玫瑰图展示检测类型
- 📊 **置信度分布**：柱状图展示检测置信度统计
- 🔀 **情绪转换矩阵**：桑基图展示情绪转换关系
- 📉 **检测类型趋势**：面积图展示检测类型趋势

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
| [OpenCV](https://opencv.org/) | 4.13 | 图像处理与 DNN 人脸检测 |
| [ONNX Runtime](https://onnxruntime.ai/) | 1.19 | 模型推理引擎（支持 CUDA） |
| [NumPy](https://numpy.org/) | 2.0 | 数值计算 |
| [Pydantic](https://docs.pydantic.dev/) | 2.5 | 数据验证 |
| [WebSockets](https://websockets.readthedocs.io/) | 12.0 | 实时通信 |

### AI 模型

| 模型 | 类型 | 用途 | 大小 |
|------|------|------|------|
| `final_model.onnx` | ONNX (EfficientNet-B1) | 情绪分类（7种表情） | 8.7 MB |
| `res10_300x300_ssd_iter_140000_fp16.caffemodel` | Caffe (SSD) | 人脸检测 | 5.2 MB |
| `deploy.prototxt` | Prototxt | SSD 网络结构配置 | - |

**支持的7种情绪**：开心、悲伤、愤怒、惊讶、恐惧、厌恶、平静

### 性能模式

| 参数 | GPU 加速 | CPU 高性能 | CPU 低性能 |
|------|---------|-----------|-----------|
| `use_gpu` | ✅ True | ❌ False | ❌ False |
| `send_width` | 320 | 256 | 128 |
| `send_height` | 240 | 192 | 96 |
| `frame_skip_threshold` | 2 | 3 | 5 |
| `ema_alpha` | 0.25 | 0.2 | 0.15 |
| `inference_threads` | 4 | 3 | 1 |
| `quality_preset` | high | medium | low |

### 训练可视化工具

项目提供了完整的训练日志可视化工具，位于 `visualization/` 目录：

| 文件 | 描述 |
|------|------|
| `visualize_training.py` | 训练日志解析与可视化脚本 |
| `training_history.png` | 训练综合指标图表 |
| `loss_curves.png` | 损失曲线对比图 |
| `accuracy_curves.png` | 准确率曲线对比图 |
| `f1_curves.png` | F1分数曲线对比图 |
| `lr_curves.png` | 学习率变化曲线 |
| `confusion_matrix.png` | 混淆矩阵图 |
| `summary_data.json` | 训练指标汇总数据 |
| `summary_report.md` | 训练报告 |

---

## 📊 模型训练可视化

### 训练曲线

系统提供了完整的模型训练可视化分析，以下是模型训练过程中的关键指标变化：

#### 训练损失与验证损失曲线
![损失曲线](visualization/loss_curves.png)

#### 训练准确率与验证准确率曲线
![准确率曲线](visualization/accuracy_curves.png)

#### F1分数曲线
![F1曲线](visualization/f1_curves.png)

#### 学习率变化曲线
![学习率曲线](visualization/lr_curves.png)

### 训练综合图表

以下图表展示了模型训练的综合效果（包含损失、准确率、F1分数和学习率）：

![训练历史](visualization/training_history.png)

### 混淆矩阵

模型在验证集上的分类结果混淆矩阵：

![混淆矩阵](visualization/confusion_matrix.png)

### 训练指标对比

| 训练阶段 | 最佳Val F1 | 最佳Val Acc | 训练轮数 |
|---------|-----------|------------|---------|
| 第一阶段 | 96.66% | 96.65% | 100 |
| 第二阶段 | 98.51% | 98.51% | 149 |

---

## 📁 项目结构

```
FaceEmotion-AI/
├── backend/                          # 🔧 后端服务
│   ├── api/                          # API 路由层
│   │   ├── __init__.py               # 路由注册中心
│   │   ├── ai_features.py            # AI 功能接口（反馈/分析/优化器）
│   │   ├── detection.py              # 检测接口（图片/视频/批量）
│   │   ├── emotion_trend_analysis.py # 情绪趋势分析
│   │   ├── history.py                # 历史记录接口
│   │   ├── system.py                 # 系统配置接口
│   │   ├── text_analysis.py          # 文本情绪分析接口
│   │   └── websocket.py              # WebSocket 实时流（多人脸追踪）
│   ├── models/                       # 模型代码
│   │   ├── detector.py               # OpenCV DNN SSD 人脸检测器
│   │   └── emotion_classifier_onnx.py # ONNX 情绪分类器（CUDA加速）
│   ├── core/                         # 核心模块
│   │   ├── config.py                 # 配置管理器（三级性能模式）
│   │   ├── constants.py              # 常量定义
│   │   └── database.py               # 数据库管理（WAL模式）
│   ├── adaptation/                   # 自适应学习模块
│   │   ├── active_learner.py         # 自适应学习引擎
│   │   └── calibration_state.json    # 校准状态持久化
│   ├── analytics/                    # 数据分析模块
│   │   └── user_analytics.py         # 用户行为分析
│   ├── optimizer/                    # 性能优化器
│   │   └── dynamic_inference.py      # 动态推理优化
│   ├── music/                        # AI 音乐生成
│   │   └── generative_music.py       # 生成式音乐
│   ├── services/                     # 业务服务层
│   │   └── detection_service.py      # 检测服务（精简版）
│   ├── weights/                      # 模型权重文件
│   │   ├── final_model.onnx          # EfficientNet-B1 情绪模型
│   │   └── res10_300x300_ssd_iter_140000_fp16.caffemodel  # SSD 人脸模型
│   ├── configs/                      # 模型配置
│   │   └── deploy.prototxt           # SSD 网络结构配置
│   ├── tests/                        # 测试文件
│   ├── app.py                        # 🚀 应用入口
│   ├── config.json                   # 运行时配置
│   ├── requirements.txt              # Python 依赖
│   └── Dockerfile                    # Docker 配置
│
├── frontend/                         # 🎨 前端应用
│   ├── src/
│   │   ├── api/                      # API 客户端
│   │   │   ├── modules/              # API 模块（analytics/detection/history/system）
│   │   │   ├── config.js             # API 配置
│   │   │   ├── http.js               # HTTP 客户端
│   │   │   ├── index.js              # API 统一导出
│   │   │   └── websocket.js          # WebSocket 客户端
│   │   ├── components/               # Vue 组件
│   │   │   ├── detection/            # 检测组件（实时/图片/视频/批量）
│   │   │   ├── analytics/            # 分析组件（数据看板）
│   │   │   ├── analysis/             # 情绪趋势面板
│   │   │   ├── charts/               # 图表组件（折线/趋势/多人脸）
│   │   │   ├── feedback/             # 反馈组件（情绪反馈/历史/音乐监控）
│   │   │   ├── history/              # 历史记录查看器
│   │   │   ├── header/               # 情绪分析器头部
│   │   │   ├── layout/               # 布局组件（头部/侧边栏）
│   │   │   ├── monitor/              # 监控组件（自适应学习/性能）
│   │   │   ├── pages/                # 页面组件（设置/文本分析/主题）
│   │   │   ├── icons/                # SVG 图标组件
│   │   │   ├── common/               # 通用组件（图表加载/错误边界/FPS等）
│   │   │   └── ui/                   # UI 基础组件（按钮/卡片/进度/加载等）
│   │   ├── composables/              # 组合式函数
│   │   │   ├── useCamera.js          # 摄像头控制
│   │   │   ├── useCanvasRenderer.js  # Canvas 渲染器
│   │   │   ├── useDetectionStream.js # 检测流管理
│   │   │   ├── useEmotionHistory.js  # 情绪历史
│   │   │   ├── useNavigation.js      # 导航管理
│   │   │   ├── usePerformanceMonitor.js # 性能监控
│   │   │   └── useTimerScheduler.js  # 定时调度器
│   │   ├── stores/                   # Pinia 状态管理
│   │   │   ├── analytics.js          # 分析状态
│   │   │   ├── detection.js          # 检测状态
│   │   │   └── theme.js              # 主题状态
│   │   ├── router/                   # 路由配置
│   │   │   └── index.js              # 12 个页面路由
│   │   ├── styles/                   # 样式文件
│   │   │   ├── base/                 # 基础样式（动画/布局/重置）
│   │   │   ├── design-tokens/        # 设计令牌（颜色/圆角/阴影/间距/字体）
│   │   │   └── *.css                 # 全局/组件/页面样式
│   │   ├── themes/                   # 主题配置
│   │   ├── constants/                # 常量定义（检测/情绪）
│   │   ├── utils/                    # 工具函数
│   │   │   ├── canvas.js             # Canvas 绘制（赛博朋克风格）
│   │   │   ├── emotion.js            # 情绪工具（名称/颜色/图标）
│   │   │   ├── analytics.js          # 分析工具
│   │   │   ├── emotionAnalyzer.js    # 情绪分析器
│   │   │   ├── emotionTrendAnalyzer.js # 情绪趋势分析
│   │   │   ├── generativeAudio.js    # 生成式音频
│   │   │   ├── logger.js             # 日志工具
│   │   │   └── debounce.js           # 防抖工具
│   │   ├── App.vue                   # 根组件
│   │   └── main.js                   # 入口文件
│   ├── public/                       # 静态资源
│   ├── index.html                    # HTML 入口
│   ├── vite.config.js                # Vite 配置
│   ├── package.json                  # Node 依赖
│   ├── nginx.conf                    # Nginx 配置
│   └── Dockerfile                    # Docker 配置
│
├── test_image_video/                 # 测试文件目录
│   ├── image/                        # 测试图片（按情绪分类）
│   └── video/                        # 测试视频
├── visualization/                    # 训练可视化工具
│   ├── visualize_training.py         # 训练日志解析脚本
│   ├── training_history.png          # 训练综合图表
│   ├── loss_curves.png               # 损失曲线
│   ├── accuracy_curves.png           # 准确率曲线
│   ├── f1_curves.png                 # F1分数曲线
│   ├── lr_curves.png                 # 学习率曲线
│   ├── confusion_matrix.png          # 混淆矩阵
│   ├── summary_data.json             # 汇总数据
│   └── summary_report.md             # 训练报告
├── scripts/                          # 脚本工具
├── docker-compose.yml                # Docker Compose 配置
└── README.md                         # 项目文档
```

---

## 🚀 环境准备

### 系统要求

| 组件 | 最低要求 | 推荐配置 |
|------|---------|---------|
| **操作系统** | Windows 10+ / macOS / Linux | Windows 11 / Ubuntu 22.04 |
| **Python** | 3.10+ | 3.12 |
| **Node.js** | 18+ | 20 LTS |
| **内存** | 4 GB | 8 GB+ |
| **GPU** | - | NVIDIA GPU（CUDA 支持，可选） |
| **磁盘空间** | 2 GB | 5 GB+（含模型文件） |

### 安装步骤

#### 1️⃣ 安装 Python 环境

**Windows PowerShell**
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

**macOS / Linux**
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

#### 2️⃣ 安装 Node.js 环境

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
```

#### 3️⃣ 模型文件

✅ **模型文件已包含在项目中**，无需额外下载！

```
backend/weights/
├── final_model.onnx                                (8.7 MB)  - EfficientNet-B1 情绪分类
└── res10_300x300_ssd_iter_140000_fp16.caffemodel   (5.2 MB)  - SSD 人脸检测

backend/configs/
└── deploy.prototxt                                           - SSD 网络结构
```

---

## ⚡ 快速启动

### 方式一：开发模式启动

#### 1. 启动后端服务

```powershell
# Windows PowerShell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app:app --host 0.0.0.0 --port 8000
```

```bash
# macOS / Linux
cd backend
source .venv/bin/activate
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

**成功输出示例**：
```
2026-05-18 00:00:00 | INFO | app - AI情感检测系统 V3.2.0 启动中...
2026-05-18 00:00:00 | INFO | app - GPU: NVIDIA GeForce RTX 3060 Laptop GPU (6.0 GB)
2026-05-18 00:00:00 | INFO | app - 性能模式: GPU加速，最佳性能
2026-05-18 00:00:00 | INFO | app - SSD 人脸检测器加载完成 (0.02s)
2026-05-18 00:00:00 | INFO | app - ONNX 情绪识别模型加载完成 (0.48s, 7种表情)
2026-05-18 00:00:00 | INFO | app - 检测服务初始化完成
2026-05-18 00:00:00 | INFO | app - 数据库初始化完成
2026-05-18 00:00:00 | INFO | app - 系统就绪! V3.2.0
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### 2. 启动前端服务

```bash
# 打开新终端
cd frontend
npm run dev
```

**成功输出示例**：
```
VITE v8.0.10  ready in 720 ms
➜  Local:   http://localhost:5173/
```

#### 3. 访问应用

打开浏览器访问：http://localhost:5173

### 方式二：Docker 一键部署

```bash
# 构建并启动所有服务
docker-compose up --build -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

**访问地址**：
- **前端**：http://localhost:80
- **后端 API**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs

---

## 📡 API 接口文档

### 基础路径

- 后端地址：`http://localhost:8000`
- WebSocket 地址：`ws://localhost:8000/ws/stream`
- API 文档：`http://localhost:8000/docs`

### 接口列表

| 接口 | 方法 | 路径 | 描述 |
|------|------|------|------|
| 健康检查 | GET | `/health` | 检查服务状态 |
| 实时检测 | WS | `/ws/stream` | WebSocket 实时流检测（多人脸追踪） |
| 图片检测 | POST | `/api/detection/image` | 单张图片情绪检测 |
| 视频检测 | POST | `/api/detection/video` | 视频文件情绪检测 |
| 批量图片检测 | POST | `/api/detection/batch` | 多张图片批量检测 |
| 获取历史记录 | GET | `/api/history` | 获取检测历史列表 |
| 获取单条记录 | GET | `/api/history/{id}` | 获取单条检测记录 |
| 删除记录 | DELETE | `/api/history/{id}` | 删除检测记录 |
| 用户反馈 | POST | `/api/ai/feedback` | 提交情绪识别反馈 |
| 情绪趋势分析 | POST | `/api/emotion-trend/analyze` | 情绪趋势分析 |
| 文本情绪分析 | POST | `/api/text-analysis/analyze` | 文本情绪分析 |
| 系统配置 | GET | `/api/config` | 获取系统配置 |
| 更新配置 | POST | `/api/config` | 更新系统配置 |
| 行为日志 | POST | `/api/analytics/log` | 记录用户行为 |

### WebSocket 实时检测协议

**发送帧数据**：
- 二进制帧，格式：`[flag(1B)][width(2B)][height(2B)][RGBA像素数据]`

**接收检测结果**：
```json
{
  "type": "result",
  "faces": [
    {
      "bbox": [x, y, w, h],
      "emotion": "happy",
      "confidence": 0.95,
      "scores": {"happy": 0.95, "sad": 0.02, ...}
    }
  ],
  "dominant_emotion": "happy",
  "timestamp": "2026-05-18T00:00:00",
  "process_time": 0.032,
  "gpu_memory": 1024.5,
  "frame_count": 42
}
```

**控制消息**：
```json
{"type": "config_update", "config": {"performance_mode": "gpu"}}
{"type": "detection_control", "enabled": true}
```

### 请求示例

**图片检测**
```bash
curl -X POST http://localhost:8000/api/detection/image \
  -F "file=@test.jpg"
```

**获取历史记录**
```bash
curl http://localhost:8000/api/history?page=1&limit=10
```

### 响应格式

```json
{
  "success": true,
  "message": "成功",
  "data": {
    "emotions": [
      {"emotion": "happy", "confidence": 0.85},
      {"emotion": "neutral", "confidence": 0.12},
      {"emotion": "sad", "confidence": 0.03}
    ],
    "face_count": 1,
    "timestamp": "2026-05-18T12:00:00Z"
  }
}
```

---

## 🎯 使用指南

### 1. 实时情绪检测

1. 在左侧边栏选择"实时检测"
2. 点击"开始检测"按钮
3. 允许浏览器访问摄像头权限
4. 系统自动开始检测，实时显示情绪结果
5. 多人脸时自动显示编号（人脸1、人脸2...）
6. 点击"停止检测"可结束实时检测

### 2. 图片检测

1. 在左侧边栏选择"图片检测"
2. 点击上传区域或拖拽图片到上传区域
3. 系统自动分析图片中的人脸情绪
4. 检测结果会自动保存到历史记录

### 3. 视频检测

1. 在左侧边栏选择"视频检测"
2. 上传视频文件（支持 MP4、AVI 格式）
3. 系统逐帧分析视频中的情绪变化
4. 可通过时间轴查看不同时间点的情绪

### 4. 数据分析

1. 在左侧边栏选择"数据看板"
2. 查看6种可视化图表
3. 数据会随新检测结果自动更新

### 5. 历史记录

1. 在左侧边栏选择"历史档案"
2. 查看所有检测记录
3. 支持按时间、检测类型筛选
4. 可查看详细结果或删除记录

### 6. 文本情绪分析

1. 在左侧边栏选择"文本情绪分析"
2. 输入文本内容
3. 系统分析文本的情绪倾向

---

## ⚙️ 配置说明

### 后端配置 (`backend/config.json`)

```json
{
  "host": "0.0.0.0",
  "port": 8000,
  "debug": false,
  "log_level": "info",

  "performance_mode": "gpu",
  "use_gpu": true,
  "emotion_model": "weights/final_model.onnx",
  "face_detector_model": "weights/res10_300x300_ssd_iter_140000_fp16.caffemodel",
  "face_detector_proto": "configs/deploy.prototxt",
  "confidence_threshold": 0.45,
  "face_detect_confidence": 0.35,

  "max_workers": 4,
  "send_width": 320,
  "send_height": 240,
  "frame_skip_threshold": 2,
  "ema_alpha": 0.25,

  "ws_max_connections": 10,
  "ws_heartbeat_interval": 30,

  "database_url": "sqlite:///./data/emotion.db",
  "max_faces": 10,
  "enable_adaptive_calibration": false
}
```

### 性能模式配置

系统支持三种性能模式，通过 `performance_mode` 字段切换：

| 模式 | 值 | 适用场景 |
|------|------|---------|
| GPU 加速 | `"gpu"` | 有 NVIDIA GPU，追求最佳性能 |
| CPU 高性能 | `"cpu_high"` | 无 GPU，但 CPU 性能较好 |
| CPU 低性能 | `"cpu_low"` | 低配设备，优先稳定性 |

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

**解决方案**：
1. 确认模型文件存在于 `backend/weights/` 目录
2. 确认 `backend/configs/deploy.prototxt` 存在
3. 从 `backend/` 目录启动服务（相对路径基于此）

### Q2: 端口 8000 已被占用

**解决方案**：
```powershell
# Windows：查找并终止占用进程
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# 或修改 backend/config.json 中的端口
"port": 8001
```

### Q3: 前端无法连接后端

**解决方案**：
1. 检查后端是否正常运行：`curl http://localhost:8000/health`
2. 确认前端 API 配置正确
3. 检查 CORS 配置（已支持 5173/5174 端口）

### Q4: WebSocket 连接频繁断开

**解决方案**：
1. 确保网络连接稳定
2. 检查防火墙设置
3. 后端已修复 ping/pong 心跳检测机制

### Q5: 摄像头无法访问

**解决方案**：
1. 检查浏览器摄像头权限
2. 尝试更换摄像头索引（`config.json` 中 `camera_index`）
3. 测试摄像头硬件是否正常

### Q6: 数据库锁定错误

**解决方案**：
```bash
# Windows
taskkill /F /IM python.exe

# 删除锁定文件
rm backend/data/emotion.db-journal
```

### Q7: GPU 加速不生效

**解决方案**：
1. 确认已安装 CUDA 和 cuDNN
2. 安装 `onnxruntime-gpu` 替代 `onnxruntime`
3. 检查 `config.json` 中 `performance_mode` 设置为 `"gpu"`

### Q8: 人脸检测框卡顿/抖动

**解决方案**：
1. 系统已内置浮点数平滑和抖动过滤机制
2. GPU 模式下每帧检测，CPU 模式每 2 帧检测
3. 如仍有问题，可调整 `config.json` 中 `ema_alpha` 值

---

## 🤝 贡献指南

### 代码规范

**Python 代码**
- 遵循 PEP 8 风格指南
- 使用类型注解
- 使用 `black` 格式化代码

**Vue 代码**
- 使用 Composition API
- 组件命名使用 PascalCase
- 使用 ESLint + Prettier

### Git 工作流

```bash
# 1. 创建功能分支
git checkout -b feat/your-feature-name

# 2. 提交代码
git add .
git commit -m "feat: add your feature description"

# 3. 推送分支
git push origin feat/your-feature-name

# 4. 创建 Pull Request
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
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具链相关

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - Python Web 框架
- [Vue.js](https://vuejs.org/) - JavaScript 框架
- [OpenCV](https://opencv.org/) - 计算机视觉库
- [ONNX Runtime](https://onnxruntime.ai/) - 推理引擎
- [Element Plus](https://element-plus.org/) - Vue 3 组件库
- [ECharts](https://echarts.apache.org/) - 数据可视化库
