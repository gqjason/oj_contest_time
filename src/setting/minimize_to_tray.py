import pystray
from PIL import Image
import threading
import os
import sys
from logger import FileLogger
import tkinter as tk

file_name = "minimize_to_tray.py"

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MinimizeToTray:
    class_name = "MinimizeToTray"

    def __init__(self, window: tk.Tk):
        self.window = window
        self.tray_icon = None
        self.logger = FileLogger()

    def on_show(self, icon, item):
        self.window.after(0, self.window.deiconify)

    def on_quit(self, icon, item):
        self.logger.info(f"[{file_name}][{self.class_name}] 退出程序")
        icon.stop()
        self.window.after(0, self.window.destroy)

    def on_close(self):
        """关闭窗口时最小化到托盘"""
        self.window.withdraw()
        if not self.tray_icon:
            self.create_tray_icon()

    def create_tray_icon(self):
        icon_path = get_resource_path("resources/icons/app.ico")
        image = Image.open(icon_path)
        menu = pystray.Menu(
            pystray.MenuItem("显示", self.on_show),
            pystray.MenuItem("退出", self.on_quit)
        )
        self.tray_icon = pystray.Icon("App", image, "应用正在后台运行", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def enable_running(self):
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def disable_running(self):
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)
