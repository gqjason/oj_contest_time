import os
import re
import socket
from plyer import notification
from dotenv import load_dotenv

from logger import FileLogger
from get_all_path import GetAllPath as GAP

file_name = "desktop_notification.py"
class DesktopNotification:
    """
    桌面通知类，支持跨平台，自动读取环境变量配置。
    依赖 plyer 和 python-dotenv。
    """
    class_name = "DesktopNotification"
    
    def __init__(self, app_name=None, default_icon=None, icon_path = None, default_timeout=10):
        self.logger = FileLogger()

        self.app_name = app_name or os.getenv("APP_NAME", "OJ Contest Notification")
        self.icon_path = GAP().get_resource_path(icon_path) if icon_path else GAP().get_resource_path("resources/icons/app.ico")
        self.default_icon = default_icon or os.getenv("NOTIFICATION_ICON", self.icon_path)
        self.default_timeout = default_timeout

        try:
            self.hostname = socket.gethostname()
        except Exception:
            self.hostname = "Unknown"
            
        self.logger.debug(f"[{file_name}][{self.class_name}] initialize self.hostname is {self.hostname}")

    def send(self, title: str, message: str, timeout = None):
        """
        发送系统通知
        :param title: 通知标题
        :param message: 通知内容
        :param timeout: 显示时间（秒），默认读取 self.default_timeout
        """
        title = self._sanitize(title)
        message = self._sanitize(message)
        full_title = f"{title}"

        try:
            notification.notify(
                title=full_title,
                message=message,
                app_name=self.app_name,
                app_icon=self.default_icon,
                timeout=timeout or self.default_timeout
            ) # type: ignore
            return True
        except Exception as e:
            self.logger.error(f"[{file_name}][{self.class_name}] Failed to send notification: {e}")
            return False

    def _sanitize(self, text):
        """移除控制字符和危险输入，限制长度"""
        if not text:
            return ""
        text = re.sub(r"[\x00-\x1F\x7F-\x9F]", "", text)
        return text[:256]


if __name__ == '__main__':
    dnf = DesktopNotification()
    
    dnf.send("1","2")