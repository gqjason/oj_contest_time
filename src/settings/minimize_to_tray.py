import pystray
from PIL import Image
import threading
from logger import FileLogger
import tkinter as tk

from .get_all_path import GetAllPath as GAP

file_name = "minimize_to_tray.py"
class MinimizeToTray:
    class_name = "MinimizeToTray"

    def __init__(self, window: tk.Tk):
        self.window = window
        self.tray_icon = None
        self.logger = FileLogger()

    def on_show(self):
        self.window.after(0, self.window.deiconify)

    def on_quit(self, icon):
        self.logger.info(f"[{file_name}][{self.class_name}] 退出程序")
        icon.stop()
        self.window.after(0, self.window.destroy)

    def on_close(self):
        """关闭窗口时最小化到托盘"""
        self.window.withdraw()
        if not self.tray_icon:
            self.create_tray_icon()

    def create_tray_icon(self):
        if self.tray_icon is None:
            icon_path = GAP().get_resource_path("resources/icons/app.ico")
            image = Image.open(icon_path)
            menu = pystray.Menu(
                pystray.MenuItem("显示", self.on_show),
                pystray.MenuItem("退出", self.on_quit)
            )
            self.tray_icon = pystray.Icon("App", image, "应用正在后台运行", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def remove_tray_icon(self):
        if self.tray_icon:
            self.tray_icon.stop()  # 停止托盘图标事件循环
            self.tray_icon = None
            self.logger.info(f"[{file_name}][{self.class_name}] 托盘图标已关闭")
    
    def enable_running(self):
        self.logger.info(f"[{file_name}][{self.class_name}][enable_running] 启用最小化托盘")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def disable_running(self):
        self.logger.info(f"[{file_name}][{self.class_name}][disable_running] 禁用最小化托盘")
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)
