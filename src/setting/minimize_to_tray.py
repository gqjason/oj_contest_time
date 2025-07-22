# setting/minimize_to_tray.py
import pystray
from PIL import Image
import threading
import os
from logger import FileLogger

file_name = "minimize_to_tray.py"

class MinimizeToTray:
    def __init__(self, window, lock=None, lock_file_path=None):
        self.window = window
        self.tray_icon = None
        self.logger = FileLogger()
        self.lock = lock
        self.lock_file_path = lock_file_path

    def enable(self):
        """拦截关闭，隐藏到托盘"""
        self.window.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

    def hide_to_tray(self):
        """隐藏窗口并创建托盘图标"""
        self.window.withdraw()
        self._create_tray_icon()

    def _create_tray_icon(self):
        if self.tray_icon:
            return

        def on_show(icon, item):
            self.window.after(0, self.window.deiconify)
            icon.stop()
            self.tray_icon = None

        def on_exit(icon, item):
            # 退出前释放锁并删锁文件
            if self.lock:
                try: 
                    self.lock.release()
                except: 
                    pass
                try:
                    os.remove(self.lock_file_path)
                except:
                    pass

            self.window.after(0, self.window.destroy)
            icon.stop()

        # 图标文件
        base_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_dir, "..", "resources", "icons", "app.ico")
        try:
            image = Image.open(icon_path)
        except Exception as e:
            self.logger.error(f"[{file_name}] 图标加载失败: {e}")
            image = Image.new("RGB", (64, 64), (255,255,255))

        menu = pystray.Menu(
            pystray.MenuItem("显示窗口", on_show),
            pystray.MenuItem("退出", on_exit)
        )
        self.tray_icon = pystray.Icon("tray_icon", image, "竞赛提醒工具", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
