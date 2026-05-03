"""清理所有视频检测的历史记录"""
from database import DatabaseManager
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def clean_video_history():
    """清理所有视频检测记录"""
    db = DatabaseManager('./data/emotion.db')

    try:
        # 获取当前视频检测记录数量
        count = db.get_history_count('video')
        print(f"📊 当前视频检测记录数量: {count}")

        if count > 0:
            # 删除所有视频检测记录
            deleted = db.delete_by_detection_type('video')
            print(f"✅ 成功删除 {deleted} 条视频检测记录")

            # 验证删除结果
            remaining = db.get_history_count('video')
            print(f"📊 剩余视频检测记录数量: {remaining}")
        else:
            print("️  没有视频检测记录需要清理")

    except Exception as e:
        print(f"❌ 清理失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == '__main__':
    print(" 开始清理视频检测历史记录...")
    clean_video_history()
    print("✨ 清理完成!")
