import os
import sys
import json
from tkinter import ttk, messagebox
from pathlib import Path

file_name = "get_all_path.py"
class GetAllPath:
    class_name = "GetAllPath"
    
    def __init__(self) -> None:
        self.base_path = self.get_base_path()
    
    def get_base_path(self):
        return Path.home() / "oj_contest_time"
    
    def get_settings_path(self):
        config_path = self.base_path / "configs"/ "settings.json"
        return config_path
    
    def get_logs_path(self):
        logs_path = self.base_path / "logs"
        return logs_path
    
    def get_resource_path(self, relative_path):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS # type: ignore
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    def get_contest_data_path(self):
        config_path = self.base_path / "datas"/ "contest_data.csv"
        return config_path
    
    def load_settings(self):
        try:
            with open(self.get_settings_path(), "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            messagebox.showinfo(f"[{file_name}][{self.class_name}]", f"[load_settings] 无法加载设置: {e}")
            return {}