import os
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from PIL import Image
import numpy as np
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix, classification_report
import matplotlib.pyplot as plt
from tqdm import tqdm
from datetime import datetime
from collections import Counter

# ============ 配置 ============
EMOTION_CLASSES = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
NUM_CLASSES = len(EMOTION_CLASSES)
BATCH_SIZE = 128

TRAIN_MODEL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(TRAIN_MODEL_DIR, 'models')
DATASET_DIR = os.path.join(TRAIN_MODEL_DIR, 'dataset')
VISUALIZATION_DIR = os.path.join(TRAIN_MODEL_DIR, 'visualization')

MODEL_PATH = os.path.join(MODELS_DIR, 'best_model.pth')
TEST_SPLIT = 'val'  # 没有test集就改成 'val'


# ============ 模型定义（和train.py完全一致） ============
class EmotionEfficientNet(nn.Module):
    def __init__(self, num_classes=7, dropout_rate=0.2):
        super(EmotionEfficientNet, self).__init__()
        self.backbone = models.efficientnet_b2(weights='IMAGENET1K_V1')
        num_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=dropout_rate),
            nn.Linear(num_features, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_rate * 0.5),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        return self.backbone(x)


# ============ 数据集类 ============
class EmotionDataset(Dataset):
    def __init__(self, root_dir, split='test', transform=None):
        self.root_dir = os.path.join(root_dir, split)
        self.transform = transform
        self.samples = []
        self.class_to_idx = {cls: idx for idx, cls in enumerate(EMOTION_CLASSES)}
        for class_name in EMOTION_CLASSES:
            class_dir = os.path.join(self.root_dir, class_name)
            if not os.path.exists(class_dir):
                print(f"Warning: {class_dir} not found, skipping")
                continue
            for img_name in os.listdir(class_dir):
                if img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                    img_path = os.path.join(class_dir, img_name)
                    self.samples.append((img_path, self.class_to_idx[class_name]))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        image = Image.open(img_path).convert('RGB')
        if self.transform:
            image = self.transform(image)
        return image, label, img_path


# ============ 主测试函数 ============
def test_model():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}")

    # 检查模型文件
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model not found at {MODEL_PATH}")
        return

    # 加载模型
    checkpoint = torch.load(MODEL_PATH, weights_only=False)
    print(f"Loaded model from epoch: {checkpoint.get('epoch', 'unknown')}")
    if 'val_metrics' in checkpoint:
        print(f"Training best Val F1: {checkpoint['val_metrics'].get('f1_weighted', 'N/A')}")

    model = EmotionEfficientNet(num_classes=NUM_CLASSES, dropout_rate=0.2).to(device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    print("Model loaded successfully!\n")

    # 数据预处理
    test_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # 加载测试数据
    test_dataset = EmotionDataset(DATASET_DIR, split=TEST_SPLIT, transform=test_transform)
    if len(test_dataset) == 0:
        print(f"No test data found, trying validation set...")
        test_dataset = EmotionDataset(DATASET_DIR, split='val', transform=test_transform)

    if len(test_dataset) == 0:
        print("No data available for testing!")
        return

    print(f"Test samples: {len(test_dataset)}")

    # 类别分布
    test_labels_list = [sample[1] for sample in test_dataset.samples]
    class_counts = Counter(test_labels_list)
    print("Class distribution:")
    for cls_name, cls_idx in sorted(test_dataset.class_to_idx.items(), key=lambda x: x[1]):
        count = class_counts.get(cls_idx, 0)
        print(f"  {cls_name:10s}: {count}")

    # DataLoader
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False,
                             num_workers=2, pin_memory=True)

    # 推理
    all_preds = []
    all_labels = []
    all_probs = []

    print("\nRunning inference...")
    with torch.no_grad():
        for images, labels, paths in tqdm(test_loader):
            images = images.to(device, non_blocking=True)
            outputs = model(images)
            probs = torch.softmax(outputs, dim=1)
            _, predicted = outputs.max(1)

            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.numpy())
            all_probs.extend(probs.cpu().numpy())

    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    all_probs = np.array(all_probs)

    # ============ 输出结果 ============
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)

    accuracy = 100.0 * np.mean(all_preds == all_labels)
    print(f"\nOverall Accuracy: {accuracy:.2f}%")

    # 分类报告
    print("\nClassification Report:")
    print(classification_report(all_labels, all_preds, target_names=EMOTION_CLASSES, digits=4))

    # 汇总指标
    precision_w, recall_w, f1_w, _ = precision_recall_fscore_support(
        all_labels, all_preds, average='weighted', zero_division=0)
    precision_m, recall_m, f1_m, _ = precision_recall_fscore_support(
        all_labels, all_preds, average='macro', zero_division=0)

    print(f"Weighted - P: {precision_w*100:.2f}%  R: {recall_w*100:.2f}%  F1: {f1_w*100:.2f}%")
    print(f"Macro    - P: {precision_m*100:.2f}%  R: {recall_m*100:.2f}%  F1: {f1_m*100:.2f}%")

    # ============ 混淆矩阵 ============
    cm = confusion_matrix(all_labels, all_preds, labels=list(range(NUM_CLASSES)))
    cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100

    fig, axes = plt.subplots(1, 2, figsize=(20, 8))

    # 原始数量
    im1 = axes[0].imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    axes[0].set_title('Confusion Matrix (Count)', fontsize=14)
    axes[0].set_xticks(range(NUM_CLASSES))
    axes[0].set_yticks(range(NUM_CLASSES))
    axes[0].set_xticklabels(EMOTION_CLASSES, rotation=45, ha='right')
    axes[0].set_yticklabels(EMOTION_CLASSES)
    axes[0].set_ylabel('True Label')
    axes[0].set_xlabel('Predicted Label')
    fig.colorbar(im1, ax=axes[0])
    for i in range(NUM_CLASSES):
        for j in range(NUM_CLASSES):
            axes[0].text(j, i, str(cm[i, j]), ha="center", va="center",
                        color="white" if cm[i, j] > cm.max() / 2 else "black")

    # 百分比
    im2 = axes[1].imshow(cm_normalized, interpolation='nearest', cmap=plt.cm.Reds)
    axes[1].set_title('Confusion Matrix (%)', fontsize=14)
    axes[1].set_xticks(range(NUM_CLASSES))
    axes[1].set_yticks(range(NUM_CLASSES))
    axes[1].set_xticklabels(EMOTION_CLASSES, rotation=45, ha='right')
    axes[1].set_yticklabels(EMOTION_CLASSES)
    axes[1].set_ylabel('True Label')
    axes[1].set_xlabel('Predicted Label')
    fig.colorbar(im2, ax=axes[1])
    for i in range(NUM_CLASSES):
        for j in range(NUM_CLASSES):
            axes[1].text(j, i, f'{cm_normalized[i, j]:.1f}%', ha="center", va="center",
                        color="white" if cm_normalized[i, j] > 50 else "black")

    plt.tight_layout()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs(VISUALIZATION_DIR, exist_ok=True)
    cm_path = os.path.join(VISUALIZATION_DIR, f'test_confusion_matrix_{timestamp}.png')
    plt.savefig(cm_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nConfusion matrix saved to: {cm_path}")

    # ============ 误分类分析 ============
    misclassified = []
    for idx in range(len(all_labels)):
        if all_preds[idx] != all_labels[idx]:
            true_cls = EMOTION_CLASSES[all_labels[idx]]
            pred_cls = EMOTION_CLASSES[all_preds[idx]]
            confidence = all_probs[idx, all_preds[idx]]
            misclassified.append((true_cls, pred_cls, confidence))

    misclassified.sort(key=lambda x: -x[2])
    total = len(all_labels)
    print(f"\nTotal misclassified: {len(misclassified)} / {total} ({100*len(misclassified)/total:.1f}%)")
    print("\nTop 20 most confident misclassifications:")
    for i, (true_cls, pred_cls, conf) in enumerate(misclassified[:20]):
        print(f"  {i+1:2d}. True={true_cls:10s} Pred={pred_cls:10s} Conf={conf:.4f}")

    print("\n" + "=" * 60)
    print("TEST COMPLETED!")
    print("=" * 60)


if __name__ == '__main__':
    test_model()
