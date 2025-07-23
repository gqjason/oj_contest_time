import tkinter as tk
import sys
import json
import os
from pathlib import Path
from filelock import FileLock, Timeout

from ui_and_logic.main_logic import AppLogic
from ui_and_logic.main_ui import AppUI
from settings.minimize_to_tray import MinimizeToTray
from logger import FileLogger
from background_worker import AppBackgroundWorker as ABW

file_name = "app_window_manager.py"
class AppWindowManager:
    class_name = "AppWindowManager"
    
    def __init__(self):
        self.logger = FileLogger()
        self.root = tk.Tk()
        
        base_path = self.get_base_path()
        config_dir = base_path / "configs"
        self.config_path =  config_dir / "settings.json"
        
        self.app_logic = AppLogic()
        self.app_ui = AppUI(self.root, self.app_logic)
        self.background_worker = ABW()
        self.tray_manager = MinimizeToTray(self.root)
        self.settings = self.load_settings()

    @staticmethod
    def get_base_path():
        return Path.home() / "oj_contest_time"
    
    def load_settings(self):
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.logger.info(f"[{file_name}][{self.class_name}] 文件路径: {self.config_path}")
                return json.load(f)
        except Exception as e:
            self.logger.error(f"[AppWindowManager] 无法加载设置: {e}")
            return {}

    def apply_tray_behavior(self):
        """托盘逻辑统一放在 run 中处理"""
        self.tray_manager.enable_running()

    def run(self):
        self.background_worker.start()
        should_hide = "--hidden" in sys.argv or self.settings.get("autostart_minimize", False)

        # 防止多开
        lock_file = os.path.join(os.path.expanduser("~"), ".your_app.lock")
        self.lock = FileLock(lock_file)
        try:
            self.lock.acquire(timeout=0.1)
        except Timeout:
            print("程序已在运行。")
            sys.exit(0)

        self.apply_tray_behavior()

        if should_hide and self.settings.get("minimize_to_tray", False):
            self.root.withdraw()
            self.tray_manager.on_close()  # 初始化托盘
        else:
            self.root.deiconify()

        self.root.mainloop()
        
        self.background_worker.stop()
