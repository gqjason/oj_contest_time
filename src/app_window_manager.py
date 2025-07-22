import tkinter as tk
import json
import os
import sys
from pathlib import Path
from filelock import FileLock, Timeout
import tempfile

from setting.minimize_to_tray import MinimizeToTray
from logger import FileLogger

from ui_and_logic.main_ui import AppUI
from ui_and_logic.main_logic import AppLogic

file_name = "app_window_manager.py"

LOCK_FILE = os.path.join(tempfile.gettempdir(), "oj_contest_time.lock")
lock = FileLock(LOCK_FILE, timeout=0)

try:
    lock.acquire(timeout=0)
except Timeout:
    # 已有程序在运行
    import tkinter.messagebox as messagebox
    messagebox.showwarning("程序已在运行", "检测到已有程序实例正在运行。")
    sys.exit(0)

class AppWindowManager:
    class_name = "AppWindowManager"

    def __init__(self):
        self.logger = FileLogger()
        self.root = tk.Tk()

        base_path = self.get_base_path()
        config_dir = base_path / "configs"
        self.config_file =  config_dir / "settings.json"

        self.settings = self.load_settings()
        self.minimize_to_tray = self.settings.get("minimize_to_tray")

        # 初始化逻辑和UI
        self.app_logic = AppLogic()
        self.app_ui = AppUI(self.root, self.app_logic)

        # 托盘管理
        self.tray = MinimizeToTray(self.root)
        if self.minimize_to_tray:
            self.tray.enable_running()
        else:
            self.tray.disable_running()
            
        self.logger.info(f"[{file_name}][{self.class_name}] self.minimize_to_tray 为 {self.minimize_to_tray}")

        # 拦截关闭按钮
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    @staticmethod
    def get_base_path():
        return Path.home() / "oj_contest_time"
    
    def load_settings(self):
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.logger.debug(f"[{file_name}][{self.class_name}] 文件路径为: {os.path.abspath('settings.json')}")
                return json.load(f)
        except Exception as e:
            self.logger.error(f"[{file_name}][{self.class_name}] 加载设置失败: {e}")
            return {}
    
    def on_close(self):
        if self.minimize_to_tray:
            self.logger.info(f"[{file_name}][{self.class_name}] 窗口隐藏，托盘运行")
            self.root.withdraw()
        else:
            self.logger.info(f"[{file_name}][{self.class_name}] 正常退出")
            self.tray.cleanup()
            self.root.destroy()
            sys.exit(0)  # 确保干净退出


    def run(self):
        self.root.mainloop()
