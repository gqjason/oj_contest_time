import tkinter as tk
import json
import os
import sys

from setting.minimize_to_tray import MinimizeToTray
from logger import FileLogger

from ui_and_logic.main_ui import AppUI
from ui_and_logic.main_logic import AppLogic

file_name = "app_window_manager.py"

class AppWindowManager:
    class_name = "AppWindowManager"

    def __init__(self):
        self.logger = FileLogger()
        self.root = tk.Tk()

        self.settings = self.load_settings()
        self.minimize_to_tray = self.settings.get("minimize_to_tray", True)

        # 初始化逻辑和UI
        self.app_logic = AppLogic()
        self.app_ui = AppUI(self.root, self.app_logic)

        # 托盘管理
        self.tray = MinimizeToTray(self.root)
        if self.minimize_to_tray:
            self.tray.enable_running()
        else:
            self.tray.disable_running()

        # 拦截关闭按钮
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_settings(self):
        try:
            with open("settings.json", "r", encoding="utf-8") as f:
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
            sys.exit()

    def run(self):
        self.root.mainloop()
