import win32event
import win32api
import winerror
import sys

def is_another_instance_running():
    mutex = win32event.CreateMutex(None, False, "OnlyOneInstanceMutex_YourAppName")  # type: ignore
    last_error = win32api.GetLastError()
    if last_error == winerror.ERROR_ALREADY_EXISTS:
        return True
    return False

if is_another_instance_running():
    print("已有程序在运行。")
    sys.exit(0)

# 启动你的主程序
from app_window_manager import AppWindowManager

def main():
    manager = AppWindowManager()
    manager.run()

if __name__ == "__main__":
    main()
