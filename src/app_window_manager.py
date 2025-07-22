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
    def __init__(self):
        self.logger = FileLogger()
        self.root = tk.Tk()
        self.app_logic = AppLogic()
        self.app_ui = AppUI(self.root, self.app_logic)
        self.tray_manager = MinimizeToTray(self.root)
        self.settings = self.load_settings()

    def load_settings(self):
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "settings.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"[AppWindowManager] 无法加载设置: {e}")
            return {}

    def apply_tray_setting(self):
        if self.settings.get("minimize_to_tray", False):
            self.tray_manager.enable_running()
        else:
            self.tray_manager.disable_running()

    def run(self):
        should_hide = "--hidden" in sys.argv or self.settings.get("autostart_minimize", False)
        if should_hide:
            self.root.withdraw()
            self.tray_manager.on_close()  # 👈 自动最小化到托盘
        else:
            self.apply_tray_setting()

        self.root.mainloop()
