import os
import shutil
import random

# 配置路径（修改为你的数据集路径）
DATASET_ROOT = r"D:\front-back\FaceEmotion-AI\train_model\dataset"
TRAIN_DIR = os.path.join(DATASET_ROOT, "train")
VAL_DIR = os.path.join(DATASET_ROOT, "val")  # 新建 val 目录
VAL_RATIO = 0.2  # 验证集比例（20%）

# 获取所有表情类别（确保与 train 目录下的类别一致）
emotion_classes = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

# 1. 删除旧的 val 目录（如果存在）
if os.path.exists(VAL_DIR):
    shutil.rmtree(VAL_DIR)
os.makedirs(VAL_DIR)

# 2. 遍历每个类别，从 train 中随机抽取文件到 val
for cls in emotion_classes:
    train_cls_dir = os.path.join(TRAIN_DIR, cls)
    val_cls_dir = os.path.join(VAL_DIR, cls)
    os.makedirs(val_cls_dir, exist_ok=True)
    
    # 获取 train 类别目录下的所有 JPG 文件
    files = []
    for img in os.listdir(train_cls_dir):
        if img.lower().endswith('.jpg'):
            files.append(os.path.join(train_cls_dir, img))
    
    if not files:
        print(f"警告: 类别 {cls} 没有有效图片，跳过划分")
        continue
    
    # 随机打乱文件列表（确保可复现）
    random.seed(42)
    random.shuffle(files)
    
    # 计算划分索引（前 80% 作为 train，后 20% 作为 val）
    split_idx = int(len(files) * (1 - VAL_RATIO))
    
    # 移动文件到 val 目录（确保与 train 独立）
    for i, file_path in enumerate(files):
        if i >= split_idx:
            dst_path = os.path.join(val_cls_dir, os.path.basename(file_path))
            shutil.move(file_path, dst_path)
            print(f"已移动: {file_path} -> {dst_path}")
    
    print(f"类别 {cls} 划分完成，train 保留 {split_idx} 张，val 移动 {len(files) - split_idx} 张")

print("数据集划分完成！train 和 val 目录已生成（完全独立）。")
