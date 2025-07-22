import pystray
from pystray import MenuItem as item
from PIL import Image
import threading
import os
import sys
from logger import FileLogger

file_name = "minimize_to_tray.py"

class MinimizeToTray:
    class_name = "MinimizeToTray"

    def __init__(self, window):
        self.window = window
        self.tray_icon = None
        self.icon_thread = None
        self.logger = FileLogger()

        # 图标路径
        self.icon_path = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), "resources", "icons", "app.ico")

    def enable_running(self):
        try:
            image = Image.open(self.icon_path)

            menu = (
                item('显示窗口', self.show_window),
                item('退出程序', self.exit_program)
            )
            self.tray_icon = pystray.Icon("AppTray", image, "程序正在后台运行", menu)

            self.icon_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            self.icon_thread.start()
        except Exception as e:
            self.logger.error(f"[托盘图标] 初始化失败: {e}")
            
    def disable_running(self):
        if self.tray_icon:
            self.tray_icon.stop()

    def show_window(self, icon, item):
        self.window.after(0, self.window.deiconify)

    def exit_program(self, icon, item):
        self.disable_running()
        self.window.after(0, self.window.destroy)

    def cleanup(self):
        if self.tray_icon:
            self.tray_icon.stop()
