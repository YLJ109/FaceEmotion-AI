import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from PIL import Image
import json
import matplotlib.pyplot as plt
import numpy as np
import random
from datetime import datetime
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix
from tqdm import tqdm
from collections import Counter

# 表情类别定义
EMOTION_CLASSES = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
NUM_CLASSES = len(EMOTION_CLASSES)

# 训练参数优化
IMG_SIZE = 128
BATCH_SIZE = 128
NUM_EPOCHS = 100
LEARNING_RATE = 0.0002
WEIGHT_DECAY = 1e-4
LABEL_SMOOTHING = 0.0
DROPOUT_RATE = 0.2
SEED = 42

# 断点续训配置
RESUME_TRAINING = True
RESUME_FROM_EPOCH = 0

# 路径配置
TRAIN_MODEL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(TRAIN_MODEL_DIR, 'models')
LOG_DIR = os.path.join(TRAIN_MODEL_DIR, 'log')
VISUALIZATION_DIR = os.path.join(TRAIN_MODEL_DIR, 'visualization')
DATASET_DIR = os.path.join(TRAIN_MODEL_DIR, 'dataset')

def setup_gpu():
    if not torch.cuda.is_available():
        print('WARNING: CUDA not available, using CPU')
        return torch.device('cpu'), False
    device = torch.device('cuda')
    torch.backends.cudnn.benchmark = True
    torch.backends.cudnn.deterministic = False
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    gpu_name = torch.cuda.get_device_name(0)
    gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f'GPU: {gpu_name}')
    print(f'GPU Memory: {gpu_mem:.1f} GB')
    print(f'CUDA Version: {torch.version.cuda}')
    return device, True

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

class EmotionDataset(Dataset):
    def __init__(self, root_dir, split='train', transform=None):
        self.root_dir = os.path.join(root_dir, split)
        self.transform = transform
        self.samples = []
        self.class_to_idx = {cls: idx for idx, cls in enumerate(EMOTION_CLASSES)}
        for class_name in EMOTION_CLASSES:
            class_dir = os.path.join(self.root_dir, class_name)
            if not os.path.exists(class_dir):
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
        return image, label

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

class IdentityAugment:
    def __call__(self, batch_x, batch_y):
        return batch_x, batch_y, batch_y, 1.0

class MixUp:
    def __init__(self, alpha=0.4):
        self.alpha = alpha

    def __call__(self, batch_x, batch_y):
        if self.alpha > 0:
            lam = np.random.beta(self.alpha, self.alpha)
        else:
            lam = 1
        batch_size = batch_x.size(0)
        index = torch.randperm(batch_size).to(batch_x.device)
        mixed_x = lam * batch_x + (1 - lam) * batch_x[index]
        y_a, y_b = batch_y, batch_y[index]
        return mixed_x, y_a, y_b, lam

class CutMix:
    def __init__(self, alpha=1.0):
        self.alpha = alpha

    def __call__(self, batch_x, batch_y):
        lam = np.random.beta(self.alpha, self.alpha)
        batch_size = batch_x.size(0)
        index = torch.randperm(batch_size).to(batch_x.device)
        bbx1, bby1, bbx2, bby2 = self._rand_bbox(batch_x.size(), lam)
        batch_x[:, :, bbx1:bbx2, bby1:bby2] = batch_x[index, :, bbx1:bbx2, bby1:bby2]
        lam = 1 - ((bbx2 - bbx1) * (bby2 - bby1) / (batch_x.size()[-1] * batch_x.size()[-2]))
        y_a, y_b = batch_y, batch_y[index]
        return batch_x, y_a, y_b, lam

    def _rand_bbox(self, size, lam):
        W = size[2]
        H = size[3]
        cut_rat = np.sqrt(1. - lam)
        cut_w = int(W * cut_rat)
        cut_h = int(H * cut_rat)
        cx = np.random.randint(W)
        cy = np.random.randint(H)
        bbx1 = np.clip(cx - cut_w // 2, 0, W)
        bby1 = np.clip(cy - cut_h // 2, 0, H)
        bbx2 = np.clip(cx + cut_w // 2, 0, W)
        bby2 = np.clip(cy + cut_h // 2, 0, H)
        return bbx1, bby1, bbx2, bby2

class CutMixMixUp:
    def __init__(self, cutmix_prob=0.5, mixup_alpha=0.4, cutmix_alpha=1.0):
        self.cutmix_prob = cutmix_prob
        self.mixup = MixUp(alpha=mixup_alpha)
        self.cutmix = CutMix(alpha=cutmix_alpha)

    def __call__(self, batch_x, batch_y):
        if np.random.random() < self.cutmix_prob:
            return self.cutmix(batch_x, batch_y)
        else:
            return self.mixup(batch_x, batch_y)

def train_epoch(model, dataloader, criterion, optimizer, device, scaler, use_amp, augment):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    progress_bar = tqdm(dataloader, desc='Training', leave=False)
    for images, labels in progress_bar:
        images, labels = images.to(device, non_blocking=True), labels.to(device, non_blocking=True)
        images, labels_a, labels_b, lam = augment(images, labels)

        optimizer.zero_grad(set_to_none=True)
        if use_amp:
            with torch.amp.autocast('cuda'):
                outputs = model(images)
                loss = lam * criterion(outputs, labels_a) + (1 - lam) * criterion(outputs, labels_b)
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            scaler.step(optimizer)
            scaler.update()
        else:
            outputs = model(images)
            loss = lam * criterion(outputs, labels_a) + (1 - lam) * criterion(outputs, labels_b)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

        running_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += (lam * predicted.eq(labels_a).sum().item() + (1 - lam) * predicted.eq(labels_b).sum().item())

        progress_bar.set_postfix({
            'loss': f'{running_loss / total:.4f}',
            'acc': f'{100.0 * correct / total:.2f}%'
        })

    epoch_loss = running_loss / total
    epoch_acc = 100.0 * correct / total
    return epoch_loss, epoch_acc

def validate(model, dataloader, criterion, device, use_amp):
    model.eval()
    running_loss = 0.0
    all_preds = []
    all_labels = []
    progress_bar = tqdm(dataloader, desc='Validating', leave=False)
    with torch.no_grad():
        for images, labels in progress_bar:
            images, labels = images.to(device, non_blocking=True), labels.to(device, non_blocking=True)
            if use_amp:
                with torch.amp.autocast('cuda'):
                    outputs = model(images)
                    loss = criterion(outputs, labels)
            else:
                outputs = model(images)
                loss = criterion(outputs, labels)

            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    epoch_loss = running_loss / len(all_labels)
    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    accuracy = 100.0 * np.mean(all_preds == all_labels)

    precision, recall, f1, _ = precision_recall_fscore_support(
        all_labels, all_preds, average='weighted', zero_division=0
    )
    precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
        all_labels, all_preds, average='macro', zero_division=0
    )
    class_precision, class_recall, class_f1, _ = precision_recall_fscore_support(
        all_labels, all_preds, average=None, zero_division=0
    )

    metrics = {
        'accuracy': accuracy,
        'precision_weighted': precision * 100,
        'recall_weighted': recall * 100,
        'f1_weighted': f1 * 100,
        'precision_macro': precision_macro * 100,
        'recall_macro': recall_macro * 100,
        'f1_macro': f1_macro * 100,
        'class_precision': class_precision * 100,
        'class_recall': class_recall * 100,
        'class_f1': class_f1 * 100,
        'all_preds': all_preds,
        'all_labels': all_labels
    }
    return epoch_loss, metrics

def plot_training_history(history, save_path):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes[0, 0].plot(history['train_loss'], label='Train Loss', marker='o', markersize=3)
    axes[0, 0].plot(history['val_loss'], label='Val Loss', marker='s', markersize=3)
    axes[0, 0].set_title('Loss per Epoch')
    axes[0, 0].set_xlabel('Epoch')
    axes[0, 0].set_ylabel('Loss')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].plot(history['train_acc'], label='Train Acc', marker='o', markersize=3)
    axes[0, 1].plot(history['val_acc'], label='Val Acc', marker='s', markersize=3)
    axes[0, 1].set_title('Accuracy per Epoch')
    axes[0, 1].set_xlabel('Epoch')
    axes[0, 1].set_ylabel('Accuracy (%)')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    axes[1, 0].plot(history['train_f1'], label='Train F1', marker='o', markersize=3)
    axes[1, 0].plot(history['val_f1'], label='Val F1', marker='s', markersize=3)
    axes[1, 0].set_title('F1 Score per Epoch')
    axes[1, 0].set_xlabel('Epoch')
    axes[1, 0].set_ylabel('F1 Score (%)')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].plot(history['learning_rate'], label='Learning Rate', color='purple', marker='d', markersize=3)
    axes[1, 1].set_title('Learning Rate Schedule')
    axes[1, 1].set_xlabel('Epoch')
    axes[1, 1].set_ylabel('Learning Rate')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].set_yscale('log')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Training plot saved to {save_path}')

def plot_confusion_matrix(cm, save_path):
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)
    ax.set(xticks=np.arange(cm.shape[1]),
           yticks=np.arange(cm.shape[0]),
           xticklabels=EMOTION_CLASSES,
           yticklabels=EMOTION_CLASSES,
           title='Confusion Matrix',
           ylabel='True label',
           xlabel='Predicted label')

    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    fmt = '.2f'
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], fmt), ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black")
    fig.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Confusion matrix saved to {save_path}')

def log_message(message, log_file):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f'[{timestamp}] {message}'
    print(log_line)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_line + '\n')

def main():
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(VISUALIZATION_DIR, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(LOG_DIR, f'train_{timestamp}.log')

    set_seed(SEED)
    device, use_gpu = setup_gpu()
    use_amp = use_gpu

    log_message(f'Device: {device}', log_file)
    log_message(f'Model: EfficientNet-B2 (Optimized for Grayscale via RGB 3-Channel)', log_file)
    log_message(f'Mixed Precision (AMP): {use_amp}', log_file)
    log_message(f'Image Size: {IMG_SIZE}x{IMG_SIZE}', log_file)

    train_transform = transforms.Compose([
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(10),
        transforms.RandomAffine(degrees=0, translate=(0.05, 0.05), scale=(0.95, 1.05)),
        transforms.RandomApply([transforms.GaussianBlur(3)], p=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    train_dataset = EmotionDataset(DATASET_DIR, split='train', transform=train_transform)
    val_dataset = EmotionDataset(DATASET_DIR, split='val', transform=val_transform)

    log_message(f'Train samples: {len(train_dataset)}', log_file)
    log_message(f'Validation samples: {len(val_dataset)}', log_file)

    train_labels = [sample[1] for sample in train_dataset.samples]
    class_counts = Counter(train_labels)
    total_samples = len(train_labels)
    class_weights = []
    for i in range(NUM_CLASSES):
        count = class_counts.get(i, 1)
        class_weights.append(total_samples / (NUM_CLASSES * count))
    class_weights = torch.tensor(class_weights, dtype=torch.float).to(device)
    log_message(f'Class Weights: {class_weights.cpu().numpy()}', log_file)

    num_workers = min(4, os.cpu_count() // 2) if use_gpu else 0
    persistent_workers = use_gpu

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True,
                              num_workers=num_workers, pin_memory=use_gpu, persistent_workers=persistent_workers)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE * 2, shuffle=False,
                            num_workers=num_workers, pin_memory=use_gpu, persistent_workers=persistent_workers)

    model = EmotionEfficientNet(num_classes=NUM_CLASSES, dropout_rate=DROPOUT_RATE).to(device)

    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    log_message(f'Total parameters: {total_params:,}', log_file)
    log_message(f'Trainable parameters: {trainable_params:,}', log_file)

    criterion = nn.CrossEntropyLoss(weight=class_weights, label_smoothing=LABEL_SMOOTHING)

    base_lr = LEARNING_RATE
    classifier_lr = LEARNING_RATE * 3
    optimizer = optim.AdamW([
        {'params': model.backbone.features.parameters(), 'lr': base_lr},
        {'params': model.backbone.classifier.parameters(), 'lr': classifier_lr}
    ], weight_decay=WEIGHT_DECAY)

    scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer, T_0=10, T_mult=2, eta_min=1e-6)
    scaler = torch.amp.GradScaler('cuda') if use_amp else None

    augment = IdentityAugment()
    log_message('Using Identity Augmentation (No MixUp/CutMix) for higher confidence.', log_file)

    # ============ 修复：断点续训逻辑（增加架构兼容性检测 + 修复best_val_f1被重置的Bug） ============
    start_epoch = RESUME_FROM_EPOCH
    best_val_f1 = 0.0
    best_model_path = os.path.join(MODELS_DIR, 'best_model.pth')

    if RESUME_TRAINING and os.path.exists(best_model_path):
        checkpoint = torch.load(best_model_path, weights_only=False)
        try:
            # 尝试严格加载模型权重
            model.load_state_dict(checkpoint['model_state_dict'], strict=True)
            
            # 尝试加载优化器状态
            if 'optimizer_state_dict' in checkpoint:
                try:
                    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
                    log_message('Optimizer state restored', log_file)
                except Exception:
                    log_message('Optimizer state incompatible, using fresh optimizer', log_file)
            
            # 恢复训练轮次
            if 'epoch' in checkpoint:
                start_epoch = checkpoint['epoch'] + 1
                log_message(f'Resuming training from epoch {start_epoch}', log_file)
            
            # 恢复最佳指标
            if 'val_metrics' in checkpoint and 'f1_weighted' in checkpoint['val_metrics']:
                best_val_f1 = checkpoint['val_metrics']['f1_weighted']
                log_message(f'Restored best validation F1: {best_val_f1:.2f}%', log_file)
                
            log_message('Checkpoint loaded successfully', log_file)
            
        except RuntimeError as e:
            # 如果报错架构不匹配，自动备份旧模型并从头训练
            log_message(f'Checkpoint architecture mismatch! Training from scratch.', log_file)
            log_message(f'Error detail: {str(e)[:200]}', log_file)
            start_epoch = 0
            best_val_f1 = 0.0
            backup_path = best_model_path + '.arch_mismatch_backup'
            if not os.path.exists(backup_path):
                os.rename(best_model_path, backup_path)
                log_message(f'Old checkpoint backed up to: {backup_path}', log_file)
            else:
                os.remove(best_model_path)
                log_message('Old checkpoint removed.', log_file)
    else:
        log_message('Starting training from scratch', log_file)
    # ==========================================================================================

    history = {
        'train_loss': [], 'val_loss': [],
        'train_acc': [], 'val_acc': [],
        'train_f1': [], 'val_f1': [],
        'learning_rate': []
    }

    # 修复：原代码在这里有 best_val_f1 = 0.0，导致上面恢复的best_val_f1被覆盖重置，现已删除
    
    patience_counter = 0
    early_stop_patience = 20

    log_message('Starting training...', log_file)
    for epoch in range(start_epoch, NUM_EPOCHS):
        log_message(f'Epoch {epoch + 1}/{NUM_EPOCHS}', log_file)
        log_message('-' * 50, log_file)

        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device, scaler, use_amp, augment)
        val_loss, val_metrics = validate(model, val_loader, criterion, device, use_amp)
        scheduler.step()

        current_lrs = [param_group['lr'] for param_group in optimizer.param_groups]

        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['train_acc'].append(train_acc)
        history['val_acc'].append(val_metrics['accuracy'])
        history['train_f1'].append(val_metrics['f1_weighted'])
        history['val_f1'].append(val_metrics['f1_weighted'])
        history['learning_rate'].append(current_lrs[0])

        log_message(f'Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%', log_file)
        log_message(f'Val Loss: {val_loss:.4f} | Val Acc: {val_metrics["accuracy"]:.2f}%', log_file)
        log_message(f'Val Precision (weighted): {val_metrics["precision_weighted"]:.2f}%', log_file)
        log_message(f'Val Recall (weighted): {val_metrics["recall_weighted"]:.2f}%', log_file)
        log_message(f'Val F1 (weighted): {val_metrics["f1_weighted"]:.2f}%', log_file)
        log_message(f'Val F1 (macro): {val_metrics["f1_macro"]:.2f}%', log_file)

        log_message('Class Metrics:', log_file)
        for i, cls in enumerate(EMOTION_CLASSES):
            log_message(f'  {cls:10s}: P={val_metrics["class_precision"][i]:5.2f}%  R={val_metrics["class_recall"][i]:5.2f}%  F1={val_metrics["class_f1"][i]:5.2f}%', log_file)

        if val_metrics['f1_weighted'] > best_val_f1:
            best_val_f1 = val_metrics['f1_weighted']
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_metrics': val_metrics,
                'emotion_classes': EMOTION_CLASSES,
                'img_size': IMG_SIZE
            }, best_model_path)
            log_message(f'Best model saved! Val F1: {val_metrics["f1_weighted"]:.2f}%', log_file)
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= early_stop_patience:
                log_message(f'Early stopping triggered after {epoch + 1} epochs', log_file)
                break

        log_message(f'Backbone LR: {current_lrs[0]:.6f} | Classifier LR: {current_lrs[1]:.6f}', log_file)
        log_message(f'Patience: {patience_counter}/{early_stop_patience}', log_file)

        if use_gpu and (epoch + 1) % 5 == 0:
            mem_allocated = torch.cuda.memory_allocated() / 1024**3
            mem_reserved = torch.cuda.memory_reserved() / 1024**3
            log_message(f'GPU Memory: {mem_allocated:.2f}GB / {mem_reserved:.2f}GB', log_file)
        log_message('', log_file)

    plot_training_history(history, os.path.join(VISUALIZATION_DIR, 'training_history.png'))

    if os.path.exists(best_model_path):
        checkpoint = torch.load(best_model_path, weights_only=False)
        if 'all_preds' in checkpoint.get('val_metrics', {}):
            cm = confusion_matrix(checkpoint['val_metrics']['all_labels'], checkpoint['val_metrics']['all_preds'], labels=list(range(NUM_CLASSES)))
        else:
            model.load_state_dict(checkpoint['model_state_dict'])
            _, best_metrics = validate(model, val_loader, criterion, device, use_amp)
            cm = confusion_matrix(best_metrics['all_labels'], best_metrics['all_preds'], labels=list(range(NUM_CLASSES)))
        cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100
        plot_confusion_matrix(cm_normalized, os.path.join(VISUALIZATION_DIR, 'confusion_matrix.png'))
        log_message('Confusion matrix saved.', log_file)

    torch.save({
        'model_state_dict': model.state_dict(),
        'emotion_classes': EMOTION_CLASSES,
        'img_size': IMG_SIZE
    }, os.path.join(MODELS_DIR, 'final_model.pth'))

    with open(os.path.join(LOG_DIR, 'training_history.json'), 'w') as f:
        json.dump(history, f, indent=2)

    log_message('=' * 50, log_file)
    log_message('Training completed!', log_file)
    log_message(f'Best validation F1 (weighted): {best_val_f1:.2f}%', log_file)
    log_message(f'Models saved to: {MODELS_DIR}', log_file)
    log_message('=' * 50, log_file)

if __name__ == '__main__':
    main()
