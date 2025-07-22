# minimize_to_tray.py
import pystray
from PIL import Image
import threading
import os
from logger import FileLogger

file_name = "minimize_to_tray.py"

class MinimizeToTray:
    class_name = "MinimizeToTray"

    def __init__(self, window):
        self.window = window
        self.tray_icon = None
        self.logger = FileLogger()

    def disable_running(self):
        if hasattr(self.window, "protocol"):
            self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)

    def enable_running(self):
        if hasattr(self.window, "protocol"):
            self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_tray_icon(self):
        if self.tray_icon is not None:
            return  # 已创建则不重复

        def on_tray_icon_clicked(icon, item):
            self.window.deiconify()
            icon.stop()
            self.tray_icon = None
            self.create_tray_icon()  # 重新生成托盘图标（保持在右下角）

        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        image_path = os.path.join(project_dir, "resources", "icons", "app.ico")
        try:
            image = Image.open(image_path)
        except Exception as e:
            self.logger.error(f"[MinimizeToTray] Failed to load tray icon: {e}")
            image = Image.new('RGB', (64, 64), color=(255, 255, 255)) # type: ignore

        icon = pystray.Icon(
            "minimize_to_tray",
            image,
            "竞赛提醒工具",
            menu=pystray.Menu(
                pystray.MenuItem("显示窗口", on_tray_icon_clicked),
                pystray.MenuItem("退出", lambda: self.window.destroy())
            )
        )
        threading.Thread(target=icon.run, daemon=True).start()
        self.tray_icon = icon

    def on_close(self):
        self.window.withdraw()
        self.create_tray_icon()
