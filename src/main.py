# app/main.py
import sys
import os
from filelock import FileLock, Timeout
from app_window_manager import AppWindowManager

def main():
    # 锁文件放在用户主目录下
    lock_file_path = os.path.join(os.path.expanduser("~"), ".oj_contest_time.lock")
    lock = FileLock(lock_file_path)

    try:
        # 尝试获取锁（立即超时）
        lock.acquire(timeout=0)
    except Timeout:
        print("⚠️ 程序已经在运行。")
        sys.exit(0)

    # 将 lock 对象和 path 传给 AppWindowManager，以便托盘退出时清理
    manager = AppWindowManager(lock, lock_file_path)
    manager.run()

    # 正常退出时再释放（多余，但保险）
    try:
        lock.release()
    except:
        pass
    # 删除锁文件
    try:
        os.remove(lock_file_path)
    except:
        pass

if __name__ == "__main__":
    main()
