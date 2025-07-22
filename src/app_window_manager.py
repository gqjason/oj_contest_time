# app/app_window_manager.py
import tkinter as tk
import sys
import json
import os

from ui_and_logic.main_logic import AppLogic
from ui_and_logic.main_ui import AppUI
from setting.minimize_to_tray import MinimizeToTray
from logger import FileLogger

class AppWindowManager:
    def __init__(self, lock, lock_file_path):
        self.logger = FileLogger()
        self.root = tk.Tk()
        self.app_logic = AppLogic()
        self.app_ui = AppUI(self.root, self.app_logic)
        self.settings = self.load_settings()

        # 将锁传给托盘管理
        self.tray_manager = MinimizeToTray(self.root, lock, lock_file_path)

    def load_settings(self):
        cfg = os.path.join(os.path.dirname(__file__), "..", "config", "settings.json")
        try:
            with open(cfg, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"[AppWindowManager] 加载设置失败: {e}")
            return {}

    def run(self):
        # 无论何时都拦截关闭到托盘
        self.tray_manager.enable()

        # 程序一启动就隐藏并显示托盘
        self.root.withdraw()
        self.tray_manager.hide_to_tray()

        self.root.mainloop()
