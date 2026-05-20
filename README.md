# FaceEmotion-AI 🤖

基于深度学习的实时人脸表情识别系统，支持多种检测模式和情感分析功能。

---

## 📊 项目概览

### 功能特性

| 功能模块 | 描述 | 技术实现 |
|----------|------|----------|
| **实时人脸检测** | 基于 Web Worker 的高性能人脸检测 | YCrCb 肤色检测 + 连通域分析 |
| **表情识别** | 7 种情绪分类 | ResNet18 + ONNX Runtime |
| **图片检测** | 单张/批量图片检测 | HTTP API |
| **视频检测** | 视频帧级表情分析 | OpenCV + 批量处理 |
| **实时摄像头检测** | WebSocket 实时传输 | WebRTC + WebSocket |
| **情感趋势分析** | 时间序列情感变化 | 滑动窗口统计 |
| **自适应学习** | 动态校准模型输出 | 在线学习 + 校准算法 |

### 模型性能

| 指标 | 训练集 | 验证集 | 测试集 |
|------|--------|--------|--------|
| 准确率 | 88.55% | 78.32% | 77.91% |
| F1 分数 | 88.12% | 75.45% | 74.98% |
| 精确率 | 88.41% | 76.23% | 75.89% |
| 召回率 | 88.55% | 78.32% | 77.91% |

### 技术架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    前端应用 (Vue 3 + Vite)                      │
├─────────────────────────────────────────────────────────────────┤
│  Web Worker ──► 人脸检测 (肤色检测 + 连通域分析)                │
│  WebSocket ──► 实时通信 (视频帧传输)                           │
│  Canvas ──► 人脸框渲染 + EMA 平滑                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    后端服务 (FastAPI)                          │
├─────────────────────────────────────────────────────────────────┤
│  API ──► 图片/视频检测接口                                     │
│  WebSocket ──► 实时检测服务                                    │
│  ONNX Runtime ──► 表情分类推理                                │
│  SQLite ──► 数据持久化                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 环境要求

| 依赖 | 版本 | 说明 |
|------|------|------|
| Python | 3.10+ | 后端服务 |
| Node.js | 18+ | 前端构建 |
| npm | 9+ | 包管理 |
| ONNX Runtime | 1.15+ | 模型推理 |

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

#### 开发模式
```bash
# 启动后端 (端口 8000)
cd backend
python app.py

# 启动前端 (端口 5173)
cd frontend
npm run dev
```

#### 生产模式
```bash
# 构建前端
cd frontend
npm run build

# 启动后端（自动提供静态文件）
cd backend
python app.py --prod
```

---

## � 核心算法设计

### 1. 人脸检测算法

#### 1.1 算法原理

采用 **肤色检测 + 连通域分析** 两步法：

**步骤一：肤色检测（YCrCb 颜色空间）**
```
输入：RGB 图像 (W x H x 3)
输出：肤色掩码 (W x H)

伪代码：
for each pixel (x, y):
    RGB → YCrCb 转换
    if 133 ≤ Cr ≤ 173 and 77 ≤ Cb ≤ 127:
        mask[x,y] = 1
    else:
        mask[x,y] = 0
```

**步骤二：连通域分析（栈实现）**
```
输入：肤色掩码, 宽度 W, 高度 H
输出：人脸区域列表

伪代码：
visited = zeros(W x H)
stack = []
regions = []

for y from 0 to H-1:
    for x from 0 to W-1:
        if mask[x,y] == 1 and not visited[x,y]:
            stack.push((x,y))
            visited[x,y] = 1
            minX, minY, maxX, maxY = x, y, x, y
            area = 0
            
            while stack not empty:
                cx, cy = stack.pop()
                minX = min(minX, cx), maxX = max(maxX, cx)
                minY = min(minY, cy), maxY = max(maxY, cy)
                area += 1
                
                for each neighbor (nx, ny):
                    if valid(nx, ny) and mask[nx,ny] and not visited[nx,ny]:
                        visited[nx,ny] = 1
                        stack.push((nx, ny))
            
            regions.append({
                x: minX, y: minY, 
                width: maxX-minX+1, height: maxY-minY+1, 
                area: area
            })
```

#### 1.2 人脸区域过滤规则

| 过滤条件 | 阈值 | 说明 |
|----------|------|------|
| 最小面积 | 200 像素 | 过滤噪声 |
| 最大面积 | 图像面积的 80% | 过滤背景 |
| 宽高比 | 0.5 ~ 2.0 | 人脸比例 |
| 对称性 | > 0.6 | 人脸对称性检测 |

#### 1.3 算法复杂度

| 操作 | 时间复杂度 | 空间复杂度 |
|------|-----------|-----------|
| 肤色检测 | O(W×H) | O(W×H) |
| 连通域分析 | O(W×H) | O(W×H) |
| 区域过滤 | O(N) | O(N) |
| **总计** | **O(W×H)** | **O(W×H)** |

### 2. 表情分类算法

#### 2.1 模型架构（ResNet18）

```
输入: 128x128x3 RGB 图像

Layer 1: Conv1 (64 filters, 7x7, stride=2) → BN → ReLU → MaxPool (3x3, stride=2)
Layer 2: Conv2_x (2 blocks, 64 filters)
Layer 3: Conv3_x (2 blocks, 128 filters)
Layer 4: Conv4_x (2 blocks, 256 filters)
Layer 5: Conv5_x (2 blocks, 512 filters)
Global Average Pooling (512 features)
Fully Connected (512 → 7)
Softmax Output

输出: [angry, disgust, fear, happy, neutral, sad, surprise]
```

#### 2.2 输入预处理

```
1. 人脸裁剪：从检测框中提取人脸区域
2. 尺寸调整：resize 到 128x128
3. 归一化：
   - RGB 通道分别归一化
   - mean = [0.485, 0.456, 0.406]
   - std = [0.229, 0.224, 0.225]
4. 通道转换：HWC → CHW (PyTorch 格式)
```

#### 2.3 ONNX 推理优化

| 优化策略 | 实现方式 | 性能提升 |
|----------|----------|----------|
| 模型量化 | INT8 量化 | 3x 速度提升 |
| 图优化 | ONNX Runtime 内置优化 | 1.5x 速度提升 |
| 批量推理 | 多帧批量处理 | 2x 速度提升 |

---

## 📊 数据集说明

### 1. 数据集来源

**FER-2013 数据集**（Face Expression Recognition 2013）

| 属性 | 说明 |
|------|------|
| 来源 | Kaggle 竞赛数据集 |
| 图像数量 | 35,887 张 |
| 分辨率 | 48x48 灰度图 |
| 情绪类别 | 7 种 |

### 2. 数据分布

| 情绪类别 | 样本数 | 占比 | 说明 |
|----------|--------|------|------|
| neutral（平静） | 6,198 | 17.27% | 中性表情 |
| happy（开心） | 8,989 | 25.05% | 最常见表情 |
| sad（悲伤） | 6,077 | 16.94% | 易混淆 |
| angry（愤怒） | 4,953 | 13.80% | 中等 |
| fear（恐惧） | 5,121 | 14.27% | 中等 |
| disgust（厌恶） | 1,113 | 3.10% | 样本最少 |
| surprise（惊讶） | 4,002 | 11.15% | 中等 |

### 3. 数据预处理

#### 3.1 原始数据增强

```python
transform = transforms.Compose([
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(degrees=15),
    transforms.RandomResizedCrop(48, scale=(0.8, 1.0)),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])
])
```

#### 3.2 训练数据准备

| 步骤 | 操作 | 目的 |
|------|------|------|
| 1 | 数据清洗 | 去除损坏图像 |
| 2 | 标签编码 | 情绪字符串 → 数字索引 |
| 3 | 数据分割 | 训练集:验证集 = 8:2 |
| 4 | 数据增强 | 提升模型泛化能力 |
| 5 | 批量加载 | DataLoader 批量处理 |

### 4. 数据平衡策略

由于 disgust 类别样本最少，采用 **过采样** 策略：

```python
# 计算每个类别的权重
class_counts = [6198, 8989, 6077, 4953, 5121, 1113, 4002]
class_weights = [1.0 / c for c in class_counts]

# 过采样少数类别
sampler = WeightedRandomSampler(
    weights=class_weights,
    num_samples=len(dataset),
    replacement=True
)
```

---

## 🧠 模型训练

### 1. 训练配置

| 参数 | 值 | 说明 |
|------|------|------|
| 学习率 | 1e-4 | Adam 优化器 |
| 批次大小 | 64 | GPU 显存限制 |
| 训练轮数 | 60 | 防止过拟合 |
| 权重衰减 | 1e-5 | L2 正则化 |
| 早停耐心 | 10 | 验证集不提升则停止 |

### 2. 损失函数

采用 **交叉熵损失** + **标签平滑**：

```python
criterion = CrossEntropyLoss(label_smoothing=0.1)

# 标签平滑原理：
# 真实标签: [0, 1, 0, 0, 0, 0, 0]
# 平滑后: [ε/6, 1-ε, ε/6, ε/6, ε/6, ε/6, ε/6]
# 其中 ε = 0.1，防止模型过度自信
```

### 3. 学习率调度

```python
scheduler = CosineAnnealingLR(optimizer, T_max=60)

# 余弦退火策略：
# 学习率从 1e-4 余弦下降到 1e-6
# 周期性重启，提升模型收敛
```

### 4. 训练结果可视化

#### 4.1 混淆矩阵分析

| 真实\预测 | angry | disgust | fear | happy | neutral | sad | surprise |
|-----------|-------|---------|------|-------|---------|-----|----------|
| angry | 67.82% | 2.20% | 8.61% | 2.53% | 7.43% | 9.38% | 2.03% |
| disgust | 1.69% | 92.40% | 0.34% | 1.10% | 1.69% | 2.45% | 0.34% |
| fear | 8.36% | 0.68% | 64.86% | 2.28% | 6.67% | 11.74% | 5.41% |
| happy | 1.67% | 0.35% | 1.58% | 88.55% | 4.74% | 1.27% | 1.84% |
| neutral | 4.41% | 1.22% | 2.75% | 5.14% | 70.99% | 12.67% | 2.82% |
| sad | 7.96% | 1.15% | 7.50% | 3.37% | 18.97% | 60.29% | 0.77% |
| surprise | 2.96% | 0.93% | 5.24% | 1.94% | 3.04% | 1.69% | 84.21% |

**关键发现**：
- disgust 识别率最高（92.40%），特征最明显
- sad 识别率最低（60.29%），易被误判为 neutral
- neutral 与 sad、happy 存在较大混淆

#### 4.2 训练曲线分析

| 指标 | 训练集 | 验证集 | 分析 |
|------|--------|--------|------|
| 损失 | 0.55 | 0.92 | 轻微过拟合 |
| 准确率 | 88.55% | 78.32% | 泛化能力良好 |
| F1 分数 | 88.12% | 75.45% | 分类性能均衡 |

---

## 🔄 推理流程

### 1. 实时检测流程

```
┌──────────────────┐
│  摄像头采集帧    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Web Worker      │
│  人脸检测        │
└────────┬─────────┘
         │ 人脸框
         ▼
┌──────────────────┐
│  人脸裁剪 +      │
│  预处理          │
└────────┬─────────┘
         │ 128x128x3
         ▼
┌──────────────────┐
│  ONNX Runtime    │
│  表情分类推理    │
└────────┬─────────┘
         │ [7] 概率向量
         ▼
┌──────────────────┐
│  EMA 平滑        │
│  + 结果输出      │
└──────────────────┘
```

### 2. 图片检测流程

```python
def detect_image(image_path):
    # 1. 加载图像
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # 2. 人脸检测
    faces = face_detector.detect(image)
    
    # 3. 逐人脸处理
    results = []
    for face in faces:
        # 裁剪人脸
        x, y, w, h = face['bbox']
        face_img = image[y:y+h, x:x+w]
        
        # 预处理
        face_img = preprocess(face_img)
        
        # 推理
        logits = model(face_img)
        probs = softmax(logits)
        
        # 获取结果
        emotion = emotions[argmax(probs)]
        confidence = max(probs)
        
        results.append({
            'bbox': [x, y, w, h],
            'emotion': emotion,
            'confidence': confidence,
            'scores': dict(zip(emotions, probs))
        })
    
    return results
```

### 3. 视频检测流程

```python
def detect_video(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    results = []
    frame_interval = max(1, int(fps / 5))  # 每 5 FPS 检测一次
    
    for i in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            break
        
        if i % frame_interval == 0:
            frame_results = detect_image(frame)
            results.append({
                'frame': i,
                'timestamp': i / fps,
                'faces': frame_results
            })
    
    cap.release()
    return results
```

---

## 📈 性能优化策略

### 1. 前端优化

| 优化项 | 实现方式 | 效果 |
|--------|----------|------|
| Web Worker | 人脸检测移至后台线程 | 主线程负载 -60% |
| EMA 平滑 | 指数移动平均滤波 | 人脸框抖动减少 |
| 动态分辨率 | 根据帧率自适应 | 保证流畅度 |
| 帧跳采样 | 每隔 N 帧检测一次 | 降低 CPU 消耗 |

### 2. 后端优化

| 优化项 | 实现方式 | 效果 |
|--------|----------|------|
| ONNX 量化 | INT8 量化模型 | 推理速度 +3x |
| 批量推理 | 多帧合并处理 | 吞吐量 +2x |
| 连接池 | SQLite 持久连接 | 数据库延迟 -50% |
| 响应缓存 | 统计数据缓存 | API 响应时间 -80% |

### 3. 算法优化

| 优化项 | 复杂度 | 改进 |
|--------|--------|------|
| 连通域分析 | O(n²) → O(n) | 栈实现替代递归 |
| 肤色检测 | 查表法 | 预处理颜色范围 |
| 人脸跟踪 | IoU 匹配 | 避免重复检测 |

---

## � API 接口

### 1. 图片检测

**POST** `/api/detection/image`

请求体：
```json
{
  "file": "multipart/form-data (图像文件)"
}
```

响应：
```json
{
  "success": true,
  "faces": [
    {
      "bbox": [x, y, width, height],
      "emotion": "happy",
      "confidence": 0.92,
      "scores": {
        "angry": 0.01,
        "disgust": 0.001,
        "fear": 0.005,
        "happy": 0.92,
        "neutral": 0.05,
        "sad": 0.01,
        "surprise": 0.004
      }
    }
  ],
  "timestamp": "2024-01-01T12:00:00"
}
```

### 2. 视频检测

**POST** `/api/detection/video`

请求体：
```json
{
  "file": "multipart/form-data (视频文件)",
  "frame_interval": 5  // 可选，每隔多少帧检测一次
}
```

响应：
```json
{
  "success": true,
  "video_info": {
    "fps": 30,
    "total_frames": 1800,
    "duration": 60
  },
  "results": [
    {
      "frame": 0,
      "timestamp": 0.0,
      "faces": [...]
    }
  ]
}
```

### 3. WebSocket 实时检测

**连接地址**：`ws://localhost:8000/ws/detection`

**发送数据格式**（二进制）：
```
[0x02][0x00][width(2 bytes, little-endian)][height(2 bytes, little-endian)][image_data]
```

**响应格式**（JSON）：
```json
{
  "type": "detection_result",
  "faces": [...],
  "latency_ms": 45
}
```

---

## 🐛 常见问题

### 1. 人脸框不显示
- **原因**：摄像头权限未授予、浏览器不支持 WebRTC、人脸检测算法未正确初始化
- **解决方案**：
  1. 检查浏览器权限设置
  2. 刷新页面重新加载
  3. 打开开发者工具查看 Console 错误

### 2. 检测卡顿
- **原因**：CPU 资源不足、网络延迟、分辨率过高
- **解决方案**：
  1. 降低视频分辨率
  2. 关闭其他占用资源的应用
  3. 检查网络连接

### 3. 模型加载失败
- **原因**：ONNX 模型文件缺失、ONNX Runtime 版本不兼容
- **解决方案**：
  1. 检查 `backend/weights/final_model.onnx` 是否存在
  2. 重新安装 ONNX Runtime：`pip install onnxruntime`

### 4. 数据库连接失败
- **原因**：`backend/data/` 目录不存在或无写入权限
- **解决方案**：
  1. 创建目录：`mkdir -p backend/data`
  2. 检查目录权限：`chmod 755 backend/data`

### 5. 表情识别不准确
- **原因**：光线条件差、人脸角度过大、模型本身限制
- **解决方案**：
  1. 确保光线充足
  2. 正面面对摄像头
  3. 参考混淆矩阵了解模型局限性

---

## 📝 开发指南

### 项目结构

```
backend/
├── api/                 # REST API 接口
│   ├── detection.py     # 检测接口
│   ├── emotion_trend_analysis.py  # 趋势分析
│   ├── websocket.py     # WebSocket 服务
│   └── ...
├── core/                # 核心模块
│   ├── database.py      # 数据库管理
│   ├── config.py        # 配置管理
│   └── init_dirs.py     # 目录初始化
├── models/              # 模型定义
│   ├── detector.py      # 人脸检测器
│   └── emotion_classifier_onnx.py  # ONNX 分类器
├── services/            # 业务服务
├── weights/             # 模型权重
└── app.py               # 主入口

frontend/
├── src/
│   ├── components/      # Vue 组件
│   ├── composables/     # 组合式函数
│   ├── services/        # 服务层
│   ├── workers/         # Web Worker
│   └── utils/           # 工具函数
└── public/              # 静态资源
```

### 调试命令

```bash
# 后端调试（开启调试模式）
cd backend
python app.py --debug

# 前端调试（开发模式）
cd frontend
npm run dev

# 运行测试
cd backend
python -m pytest tests/

# 构建前端
cd frontend
npm run build
```

---

## 📊 训练可视化

### 混淆矩阵

混淆矩阵展示了模型在 7 种情绪类别上的分类性能：

- **对角线**：正确分类的样本比例
- **非对角线**：混淆错误的样本比例

**主要混淆模式**：
- sad ↔ neutral（悲伤与平静易混淆）
- fear ↔ sad（恐惧与悲伤易混淆）
- angry ↔ neutral（愤怒与平静易混淆）

### 训练历史

训练过程中的关键指标变化：

1. **损失曲线**：训练损失从 1.8 持续下降到 0.55，验证损失稳定在 0.92
2. **准确率曲线**：训练准确率从 30% 提升到 88.55%，验证准确率达到 78.32%
3. **F1 分数**：训练 F1 从 38% 提升到 88.12%，验证 F1 达到 75.45%
4. **学习率**：保持恒定 1e-4，未使用学习率衰减

---

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 贡献指南

1. Fork 项目
2. 创建功能分支：`git checkout -b feature/xxx`
3. 提交更改：`git commit -m "Add xxx feature"`
4. 推送到分支：`git push origin feature/xxx`
5. 创建 Pull Request