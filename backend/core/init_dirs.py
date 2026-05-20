"""
部署初始化脚本
在应用启动前创建所有必需的目录结构
"""
import os
from pathlib import Path


def init_directories():
    """初始化所有必需的目录"""
    # 获取 backend 目录的绝对路径
    backend_dir = Path(__file__).parent.parent

    # 定义所有必需的目录
    required_dirs = [
        backend_dir / 'data',
        backend_dir / 'data' / 'screenshots',
        backend_dir / 'data' / 'uploads',
        backend_dir / 'data' / 'thumbnails',
    ]

    # 创建所有目录
    for dir_path in required_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ 确保目录存在: {dir_path}")

    # 返回数据目录路径供其他模块使用
    return backend_dir / 'data'


if __name__ == '__main__':
    data_dir = init_directories()
    print(f"\n📁 数据目录: {data_dir}")
    print("✅ 目录初始化完成！")
