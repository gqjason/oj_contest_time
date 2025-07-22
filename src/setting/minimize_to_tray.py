import pystray
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
        self.logger = FileLogger()
        self.icon_path = os.path.join("resources", "icons", "app.ico")

    def enable_running(self):
        try:
            image = Image.open(self.icon_path)
            self.tray_icon = pystray.Icon("AppName", image, "AppName", menu=pystray.Menu(
                pystray.MenuItem("显示窗口", self.on_show_window),
                pystray.MenuItem("退出程序", self.on_exit_program)
            ))
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
            self.logger.info(f"[{file_name}][{self.class_name}] 启用托盘图标")
        except Exception as e:
            self.logger.error(f"[{file_name}][{self.class_name}] 启动托盘失败: {e}")

    def disable_running(self):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
            self.logger.info(f"[{file_name}][{self.class_name}] 停止托盘图标")

    def on_show_window(self, icon, item):
        if self.window:
            self.logger.info(f"[{file_name}][{self.class_name}] 还原窗口")
            self.window.after(0, self.window.deiconify)

    def on_exit_program(self, icon, item):
        self.logger.info(f"[{file_name}][{self.class_name}] 托盘退出")
        self.cleanup()
        self.window.destroy()
        sys.exit()

    def cleanup(self):
        if self.tray_icon:
            self.tray_icon.stop()
