#!/usr/bin/env python3
"""
训练日志可视化脚本
从训练日志中提取指标并生成可视化图表
"""

import os
import re
import json
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from datetime import datetime

# 中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def parse_log_file(log_path):
    """
    解析训练日志文件，提取训练指标
    
    Args:
        log_path: 日志文件路径
        
    Returns:
        dict: 包含所有提取的指标
    """
    data = {
        'epochs': [],
        'train_loss': [],
        'train_acc': [],
        'val_loss': [],
        'val_acc': [],
        'val_f1_weighted': [],
        'val_f1_macro': [],
        'val_precision': [],
        'val_recall': [],
        'lr_backbone': [],
        'lr_classifier': [],
        'patience': [],
        'gpu_memory': [],
        'class_metrics': {}
    }
    
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # 提取训练参数
    device_match = re.search(r'Device:\s*(.+)', content)
    model_match = re.search(r'Model:\s*(.+)', content)
    image_size_match = re.search(r'Image Size:\s*(.+)', content)
    train_samples_match = re.search(r'Train samples:\s*(\d+)', content)
    val_samples_match = re.search(r'Validation samples:\s*(\d+)', content)
    
    data['device'] = device_match.group(1) if device_match else 'Unknown'
    data['model'] = model_match.group(1) if model_match else 'Unknown'
    data['image_size'] = image_size_match.group(1) if image_size_match else 'Unknown'
    data['train_samples'] = int(train_samples_match.group(1)) if train_samples_match else 0
    data['val_samples'] = int(val_samples_match.group(1)) if val_samples_match else 0
    
    # 提取每个epoch的数据 - 使用逐行解析方法
    lines = content.split('\n')
    current_epoch = None
    current_section_lines = []
    
    for line in lines:
        # 检查是否是新的epoch开始
        epoch_match = re.search(r'\[.*?\]\s*Epoch\s+(\d+)/\d+', line)
        if epoch_match:
            # 处理上一个epoch的数据
            if current_epoch is not None and current_section_lines:
                process_epoch_section(data, current_epoch, current_section_lines)
            # 开始新的epoch
            current_epoch = int(epoch_match.group(1))
            current_section_lines = [line]
        elif current_epoch is not None:
            current_section_lines.append(line)
    
    # 处理最后一个epoch
    if current_epoch is not None and current_section_lines:
        process_epoch_section(data, current_epoch, current_section_lines)
    
    return data

def process_epoch_section(data, epoch_num, section_lines):
    """处理单个epoch的数据"""
    section = '\n'.join(section_lines)
    
    # 提取训练损失和准确率
    train_loss_match = re.search(r'Train Loss:\s*([\d.]+)', section)
    train_acc_match = re.search(r'Train Acc:\s*([\d.]+)%', section)
    
    # 提取验证指标
    val_loss_match = re.search(r'Val Loss:\s*([\d.]+)', section)
    val_acc_match = re.search(r'Val Acc:\s*([\d.]+)%', section)
    val_precision_match = re.search(r'Val Precision.*?\:\s*([\d.]+)%', section)
    val_recall_match = re.search(r'Val Recall.*?\:\s*([\d.]+)%', section)
    val_f1_weighted_match = re.search(r'Val F1 \(weighted\):\s*([\d.]+)%', section)
    val_f1_macro_match = re.search(r'Val F1 \(macro\):\s*([\d.]+)%', section)
    
    # 提取学习率
    lr_backbone_match = re.search(r'Backbone LR:\s*([\d.e-]+)', section)
    lr_classifier_match = re.search(r'Classifier LR:\s*([\d.e-]+)', section)
    
    # 提取patience
    patience_match = re.search(r'Patience:\s*(\d+)/\d+', section)
    
    # 提取GPU内存
    gpu_memory_match = re.search(r'GPU Memory:\s*([\d.]+)GB', section)
    
    # 提取类别指标
    class_metrics_section = re.search(r'Class Metrics:(.*?)(?=\[|Best model|Backbone LR|$)', section, re.DOTALL)
    class_metrics = {}
    if class_metrics_section:
        class_lines = class_metrics_section.group(1).strip().split('\n')
        for line in class_lines:
            class_match = re.search(r'(\w+)\s*:\s*P=([\d.]+)%\s*R=([\d.]+)%\s*F1=([\d.]+)%', line)
            if class_match:
                class_name = class_match.group(1).strip()
                class_metrics[class_name] = {
                    'precision': float(class_match.group(2)),
                    'recall': float(class_match.group(3)),
                    'f1': float(class_match.group(4))
                }
    
    # 添加到数据列表
    data['epochs'].append(epoch_num)
    data['train_loss'].append(float(train_loss_match.group(1)) if train_loss_match else None)
    data['train_acc'].append(float(train_acc_match.group(1)) if train_acc_match else None)
    data['val_loss'].append(float(val_loss_match.group(1)) if val_loss_match else None)
    data['val_acc'].append(float(val_acc_match.group(1)) if val_acc_match else None)
    data['val_precision'].append(float(val_precision_match.group(1)) if val_precision_match else None)
    data['val_recall'].append(float(val_recall_match.group(1)) if val_recall_match else None)
    data['val_f1_weighted'].append(float(val_f1_weighted_match.group(1)) if val_f1_weighted_match else None)
    data['val_f1_macro'].append(float(val_f1_macro_match.group(1)) if val_f1_macro_match else None)
    data['lr_backbone'].append(float(lr_backbone_match.group(1)) if lr_backbone_match else None)
    data['lr_classifier'].append(float(lr_classifier_match.group(1)) if lr_classifier_match else None)
    data['patience'].append(int(patience_match.group(1)) if patience_match else None)
    data['gpu_memory'].append(float(gpu_memory_match.group(1)) if gpu_memory_match else None)
    data['class_metrics'][epoch_num] = class_metrics

def plot_loss_curves(data_list, labels, save_path):
    """
    绘制损失曲线对比图
    
    Args:
        data_list: 多个日志数据列表
        labels: 每个数据的标签
        save_path: 保存路径
    """
    plt.figure(figsize=(12, 6))
    
    for data, label in zip(data_list, labels):
        epochs = data['epochs']
        train_loss = data['train_loss']
        val_loss = data['val_loss']
        
        plt.plot(epochs, train_loss, label=f'{label} - 训练损失', linestyle='-', marker='o', markersize=3)
        plt.plot(epochs, val_loss, label=f'{label} - 验证损失', linestyle='--', marker='s', markersize=3)
    
    plt.xlabel('Epoch')
    plt.ylabel('损失')
    plt.title('训练损失与验证损失曲线')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, 'loss_curves.png'), dpi=150, bbox_inches='tight')
    plt.close()

def plot_accuracy_curves(data_list, labels, save_path):
    """
    绘制准确率曲线对比图
    
    Args:
        data_list: 多个日志数据列表
        labels: 每个数据的标签
        save_path: 保存路径
    """
    plt.figure(figsize=(12, 6))
    
    for data, label in zip(data_list, labels):
        epochs = data['epochs']
        train_acc = data['train_acc']
        val_acc = data['val_acc']
        
        plt.plot(epochs, train_acc, label=f'{label} - 训练准确率', linestyle='-', marker='o', markersize=3)
        plt.plot(epochs, val_acc, label=f'{label} - 验证准确率', linestyle='--', marker='s', markersize=3)
    
    plt.xlabel('Epoch')
    plt.ylabel('准确率 (%)')
    plt.title('训练准确率与验证准确率曲线')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, 'accuracy_curves.png'), dpi=150, bbox_inches='tight')
    plt.close()

def plot_f1_curves(data_list, labels, save_path):
    """
    绘制F1曲线对比图
    
    Args:
        data_list: 多个日志数据列表
        labels: 每个数据的标签
        save_path: 保存路径
    """
    plt.figure(figsize=(12, 6))
    
    for data, label in zip(data_list, labels):
        epochs = data['epochs']
        val_f1_weighted = data['val_f1_weighted']
        val_f1_macro = data['val_f1_macro']
        
        plt.plot(epochs, val_f1_weighted, label=f'{label} - Weighted F1', linestyle='-', marker='o', markersize=3)
        plt.plot(epochs, val_f1_macro, label=f'{label} - Macro F1', linestyle='--', marker='s', markersize=3)
    
    plt.xlabel('Epoch')
    plt.ylabel('F1 Score (%)')
    plt.title('验证集F1分数曲线')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, 'f1_curves.png'), dpi=150, bbox_inches='tight')
    plt.close()

def plot_lr_curves(data_list, labels, save_path):
    """
    绘制学习率变化曲线
    
    Args:
        data_list: 多个日志数据列表
        labels: 每个数据的标签
        save_path: 保存路径
    """
    plt.figure(figsize=(12, 6))
    
    for data, label in zip(data_list, labels):
        epochs = data['epochs']
        lr_backbone = data['lr_backbone']
        lr_classifier = data['lr_classifier']
        
        plt.plot(epochs, lr_backbone, label=f'{label} - Backbone LR', linestyle='-', marker='o', markersize=3)
        plt.plot(epochs, lr_classifier, label=f'{label} - Classifier LR', linestyle='--', marker='s', markersize=3)
    
    plt.xlabel('Epoch')
    plt.ylabel('学习率')
    plt.title('学习率变化曲线')
    plt.yscale('log')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, 'lr_curves.png'), dpi=150, bbox_inches='tight')
    plt.close()

def plot_class_metrics(data, save_path):
    """
    绘制类别级别的指标对比图
    
    Args:
        data: 日志数据
        save_path: 保存路径
    """
    emotions = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
    emotion_names = {'angry': '愤怒', 'disgust': '厌恶', 'fear': '恐惧', 
                     'happy': '开心', 'neutral': '平静', 'sad': '悲伤', 'surprise': '惊讶'}
    
    # 获取最后一个epoch的类别指标
    if not data['class_metrics']:
        print("  - 警告: 没有类别指标数据，跳过类别指标图")
        return
    
    last_epoch = max(data['class_metrics'].keys())
    last_metrics = data['class_metrics'][last_epoch]
    
    # 检查是否有完整的类别数据
    if not all(e in last_metrics for e in emotions):
        print("  - 警告: 类别指标数据不完整，跳过类别指标图")
        return
    
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
    
    # 准确率
    precision = [last_metrics[e]['precision'] for e in emotions]
    ax1.bar(range(len(emotions)), precision, color='skyblue')
    ax1.set_xticks(range(len(emotions)))
    ax1.set_xticklabels([emotion_names[e] for e in emotions], rotation=45)
    ax1.set_ylabel('准确率 (%)')
    ax1.set_title('各情绪类别准确率')
    ax1.grid(True, alpha=0.3)
    
    # 召回率
    recall = [last_metrics[e]['recall'] for e in emotions]
    ax2.bar(range(len(emotions)), recall, color='lightgreen')
    ax2.set_xticks(range(len(emotions)))
    ax2.set_xticklabels([emotion_names[e] for e in emotions], rotation=45)
    ax2.set_ylabel('召回率 (%)')
    ax2.set_title('各情绪类别召回率')
    ax2.grid(True, alpha=0.3)
    
    # F1分数
    f1 = [last_metrics[e]['f1'] for e in emotions]
    ax3.bar(range(len(emotions)), f1, color='salmon')
    ax3.set_xticks(range(len(emotions)))
    ax3.set_xticklabels([emotion_names[e] for e in emotions], rotation=45)
    ax3.set_ylabel('F1分数 (%)')
    ax3.set_title('各情绪类别F1分数')
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, 'class_metrics.png'), dpi=150, bbox_inches='tight')
    plt.close()

def generate_summary_report(data_list, labels, save_path):
    """
    生成训练总结报告
    
    Args:
        data_list: 多个日志数据列表
        labels: 每个数据的标签
        save_path: 保存路径
    """
    report = "# 训练日志可视化报告\n\n"
    report += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for data, label in zip(data_list, labels):
        report += f"## {label}\n\n"
        report += f"- **设备**: {data['device']}\n"
        report += f"- **模型**: {data['model']}\n"
        report += f"- **图像尺寸**: {data['image_size']}\n"
        report += f"- **训练样本**: {data['train_samples']}\n"
        report += f"- **验证样本**: {data['val_samples']}\n"
        report += f"- **训练轮数**: {len(data['epochs'])}\n\n"
        
        # 过滤掉None值
        valid_f1_weighted = [x for x in data['val_f1_weighted'] if x is not None]
        valid_f1_macro = [x for x in data['val_f1_macro'] if x is not None]
        valid_val_acc = [x for x in data['val_acc'] if x is not None]
        valid_val_loss = [x for x in data['val_loss'] if x is not None]
        
        # 最佳指标
        if valid_f1_weighted:
            best_f1_idx = data['val_f1_weighted'].index(max(valid_f1_weighted))
            best_epoch = data['epochs'][best_f1_idx]
            report += "### 最佳指标\n\n"
            report += f"- **最佳Epoch**: {best_epoch}\n"
            report += f"- **最佳Val F1 (Weighted)**: {max(valid_f1_weighted):.2f}%\n"
            report += f"- **最佳Val F1 (Macro)**: {max(valid_f1_macro):.2f}%\n" if valid_f1_macro else ""
            report += f"- **最佳Val Acc**: {max(valid_val_acc):.2f}%\n" if valid_val_acc else ""
            report += f"- **最佳Val Loss**: {min(valid_val_loss):.4f}\n\n" if valid_val_loss else ""
        
        # 最终指标
        report += "### 最终指标\n\n"
        report += f"- **最终Train Loss**: {data['train_loss'][-1]:.4f}\n" if data['train_loss'][-1] is not None else ""
        report += f"- **最终Train Acc**: {data['train_acc'][-1]:.2f}%\n" if data['train_acc'][-1] is not None else ""
        report += f"- **最终Val Loss**: {data['val_loss'][-1]:.4f}\n" if data['val_loss'][-1] is not None else ""
        report += f"- **最终Val Acc**: {data['val_acc'][-1]:.2f}%\n" if data['val_acc'][-1] is not None else ""
        report += f"- **最终Val F1 (Weighted)**: {data['val_f1_weighted'][-1]:.2f}%\n" if data['val_f1_weighted'][-1] is not None else ""
        report += f"- **最终Val F1 (Macro)**: {data['val_f1_macro'][-1]:.2f}%\n\n" if data['val_f1_macro'][-1] is not None else ""
    
    with open(os.path.join(save_path, 'summary_report.md'), 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 保存JSON数据
    summary_data = []
    for data, label in zip(data_list, labels):
        valid_f1_w = [x for x in data['val_f1_weighted'] if x is not None]
        valid_f1_m = [x for x in data['val_f1_macro'] if x is not None]
        valid_acc = [x for x in data['val_acc'] if x is not None]
        
        summary_data.append({
            'label': label,
            'device': data['device'],
            'model': data['model'],
            'epochs': len(data['epochs']),
            'best_f1_weighted': max(valid_f1_w) if valid_f1_w else None,
            'best_f1_macro': max(valid_f1_m) if valid_f1_m else None,
            'best_acc': max(valid_acc) if valid_acc else None,
            'final_f1_weighted': data['val_f1_weighted'][-1] if data['val_f1_weighted'] and data['val_f1_weighted'][-1] is not None else None,
            'final_acc': data['val_acc'][-1] if data['val_acc'] and data['val_acc'][-1] is not None else None
        })
    
    with open(os.path.join(save_path, 'summary_data.json'), 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)

def main():
    # 日志文件路径
    log_dir = r'd:\front-back\FaceEmotion-AI\train_model\log'
    log_files = [
        'train_20260508_203832.log',
        'train_20260508_220502.log'
    ]
    
    # 输出目录
    output_dir = r'd:\front-back\FaceEmotion-AI\train_model\visualization'
    os.makedirs(output_dir, exist_ok=True)
    
    # 解析日志文件
    data_list = []
    labels = []
    
    for log_file in log_files:
        log_path = os.path.join(log_dir, log_file)
        if os.path.exists(log_path):
            print(f"正在解析: {log_file}")
            data = parse_log_file(log_path)
            data_list.append(data)
            # 提取日期时间作为标签
            date_time = log_file.replace('train_', '').replace('.log', '')
            labels.append(f"训练 {date_time}")
            print(f"  - Epochs: {len(data['epochs'])}")
            # 过滤掉None值
            valid_f1 = [x for x in data['val_f1_weighted'] if x is not None]
            print(f"  - Best F1: {max(valid_f1):.2f}%" if valid_f1 else "  - Best F1: N/A")
            
            # 打印前几个和后几个训练损失值来验证
            if data['train_loss']:
                print(f"  - Train Loss (前3个): {data['train_loss'][:3]}")
                print(f"  - Train Loss (后3个): {data['train_loss'][-3:]}")
        else:
            print(f"警告: 文件不存在 - {log_path}")
    
    if not data_list:
        print("没有找到有效的日志文件")
        return
    
    # 生成可视化图表
    print("\n正在生成可视化图表...")
    
    # 损失曲线
    plot_loss_curves(data_list, labels, output_dir)
    print("  - loss_curves.png")
    
    # 准确率曲线
    plot_accuracy_curves(data_list, labels, output_dir)
    print("  - accuracy_curves.png")
    
    # F1曲线
    plot_f1_curves(data_list, labels, output_dir)
    print("  - f1_curves.png")
    
    # 学习率曲线
    plot_lr_curves(data_list, labels, output_dir)
    print("  - lr_curves.png")
    
    # 类别指标
    plot_class_metrics(data_list[0], output_dir)  # 使用第一个日志的类别指标
    print("  - class_metrics.png")
    
    # 生成报告
    generate_summary_report(data_list, labels, output_dir)
    print("  - summary_report.md")
    print("  - summary_data.json")
    
    print(f"\n所有图表已保存到: {output_dir}")

if __name__ == '__main__':
    main()
