# FaceEmotion-AI 🤖

基于深度学习的实时人脸表情识别系统，支持多种检测模式和情感分析功能。

---

## 📊 项目概览

### 功能特性
- ✅ **实时人脸检测**：基于 Web Worker 的高性能人脸检测
- ✅ **表情识别**：支持 7 种情绪分类（愤怒、厌恶、恐惧、开心、平静、悲伤、惊讶）
- ✅ **多种检测模式**：图片检测、视频检测、实时摄像头检测
- ✅ **情感趋势分析**：实时情感变化趋势图表
- ✅ **自适应学习**：动态校准模型输出
- ✅ **音乐生成**：基于情绪的音乐推荐

### 模型性能

| 指标 | 数值 |
|------|------|
| 训练准确率 | ~88% |
| 验证准确率 | ~78% |
| F1 分数 | ~75% |
| 支持情绪类别 | 7 种 |

### 混淆矩阵分析

从训练结果可以看出：
- **disgust（厌恶）**：识别准确率最高，达到 92.40%
- **happy（开心）**：识别准确率较高，达到 88.55%
- **surprise（惊讶）**：识别准确率较高，达到 84.21%
- **neutral（平静）**：识别准确率 70.99%
- **sad（悲伤）**：识别准确率 60.29%，容易被误判为 neutral
- **fear（恐惧）**：识别准确率 64.86%
- **angry（愤怒）**：识别准确率 67.82%

---

## 🚀 快速开始

### 环境要求

- **Python**: 3.10+
- **Node.js**: 18+
- **npm**: 9+

### 安装依赖

#### 后端依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 前端依赖
```bash
cd frontend
npm install
```

### 启动服务

#### 方式一：开发模式

**1. 启动后端服务**
```bash
cd backend
python app.py
```

后端服务将在 `http://localhost:8000` 启动

**2. 启动前端开发服务器**
```bash
cd frontend
npm run dev
```

前端服务将在 `http://localhost:5173` 启动

#### 方式二：生产构建

**1. 构建前端**
```bash
cd frontend
npm run build
```

**2. 启动后端（自动提供静态文件）**
```bash
cd backend
python app.py --prod
```

---

## 📁 项目结构

```
FaceEmotion-AI/
├── backend/                 # 后端服务
│   ├── api/                 # API 接口
│   │   ├── detection.py     # 检测接口
│   │   ├── emotion_trend_analysis.py  # 趋势分析
│   │   ├── websocket.py     # WebSocket 实时通信
│   │   └── ...
│   ├── core/                # 核心模块
│   │   ├── database.py      # 数据库管理
│   │   ├── config.py        # 配置管理
│   │   └── init_dirs.py     # 目录初始化
│   ├── models/              # 模型定义
│   │   ├── detector.py      # 人脸检测器
│   │   └── emotion_classifier_onnx.py  # ONNX 情感分类器
│   ├── services/            # 业务服务
│   ├── weights/             # 模型权重
│   │   └── final_model.onnx # 预训练模型
│   ├── app.py               # 主应用入口
│   └── requirements.txt     # 依赖清单
│
├── frontend/                # 前端应用
│   ├── src/
│   │   ├── components/      # Vue 组件
│   │   ├── composables/     # 组合式函数
│   │   ├── services/        # 服务层
│   │   ├── workers/         # Web Worker
│   │   ├── utils/           # 工具函数
│   │   └── main.js          # 入口文件
│   ├── public/              # 静态资源
│   └── package.json         # 依赖配置
│
└── train_model/             # 模型训练代码
    ├── scripts/             # 训练脚本
    ├── models/              # 训练模型输出
    └── visualization/       # 训练可视化
```

---

## 🧠 训练算法说明

### 模型架构

本项目使用 **ResNet18** 作为基础模型，进行微调训练：

```
输入图像 (128x128x3)
    ↓
Conv1 → MaxPool → Conv2_x → Conv3_x → Conv4_x → Conv5_x
    ↓
Global Average Pooling
    ↓
全连接层 (7 分类)
    ↓
Softmax 输出
```

### 训练参数

| 参数 | 值 |
|------|-----|
| 学习率 | 1e-4 |
| 批次大小 | 64 |
| 训练轮数 | 60 |
| 优化器 | Adam |
| 损失函数 | CrossEntropyLoss |

### 数据增强

训练时使用以下数据增强策略：
- 随机水平翻转
- 随机裁剪
- 亮度/对比度调整
- 随机旋转 ±15°

### 数据集

使用 **FER-2013** 数据集：
- 训练集：28,709 张图像
- 验证集：3,589 张图像
- 测试集：3,589 张图像
- 7 种情绪类别

---

## 📸 训练可视化

### 训练历史

训练过程中的关键指标变化：

1. **损失曲线**：训练损失从 1.8 下降到约 0.55
2. **准确率曲线**：训练准确率从 30% 提升到约 88%
3. **F1 分数**：从 38% 提升到约 75%
4. **学习率**：保持恒定 1e-4

### 混淆矩阵解读

| 真实情绪 | 最易混淆 |
|----------|----------|
| angry | neutral |
| disgust | angry |
| fear | sad, neutral |
| happy | neutral |
| neutral | sad, happy |
| sad | neutral |
| surprise | fear |

---

## 🔧 API 接口

### 检测接口

**POST** `/api/detection/image`
- 描述：检测单张图片中的人脸和表情
- 请求体：`multipart/form-data`，包含 `file` 字段
- 返回：检测结果列表

**POST** `/api/detection/video`
- 描述：检测视频中的人脸表情
- 请求体：`multipart/form-data`，包含 `file` 字段
- 返回：视频帧检测结果

### WebSocket 实时检测

**连接地址**：`ws://localhost:8000/ws/detection`

发送数据格式：
```
[0x02][0x00][width(2 bytes)][height(2 bytes)][image_data]
```

---

## 🐛 常见问题

### 1. 人脸框不显示
- 检查摄像头权限是否已授予
- 确保浏览器支持 WebRTC
- 尝试刷新页面重新加载

### 2. 检测卡顿
- 降低视频分辨率（在设置中调整）
- 关闭其他占用资源的应用
- 确保网络连接稳定

### 3. 模型加载失败
- 检查 `backend/weights/final_model.onnx` 是否存在
- 确保 ONNX Runtime 已正确安装
- 查看后端日志获取详细错误信息

### 4. 数据库连接失败
- 确保 `backend/data/` 目录存在且有写入权限
- 检查数据库文件是否被其他进程占用

---

## 📝 日志与调试

后端日志位置：`backend/logs/`
前端控制台：按 F12 打开开发者工具

---

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！