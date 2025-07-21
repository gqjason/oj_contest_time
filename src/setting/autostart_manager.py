import os
import sys
import platform
import winreg
import plistlib
from logger import FileLogger

class AutoStartManager:
    def __init__(self):
        self.logger = FileLogger()
        self.app_name = "CaptureOJContestTime"
        self.key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

    def apply(self, autostart: bool, minimized: bool):
        system = platform.system()
        self.logger.info(f"[AutoStartManager] 系统平台: {system}")
        try:
            if not autostart:
                self._disable_autostart(system)
                self.logger.info("[AutoStartManager] 已禁用开机启动")
                return

            exe_path = f'"{sys.executable}" {"--minimized" if minimized else ""}'.strip()

            if system == "Windows":
                self._set_windows_autostart(exe_path)
            elif system == "Darwin":
                self._set_macos_autostart(exe_path)
            elif system == "Linux":
                self._set_linux_autostart(exe_path)
            else:
                self.logger.error(f"[AutoStartManager] 不支持的平台: {system}")
        except Exception as e:
            self.logger.error(f"[AutoStartManager] 设置失败: {e}")

    def _set_windows_autostart(self, exe_path):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.key_path, 0, winreg.KEY_SET_VALUE)
        except FileNotFoundError:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.key_path)
        with key:
            winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, exe_path)
        self.logger.info(f"[AutoStartManager][_set_windows_autostart] Windows注册表启动项设置为: {exe_path}")

    def _disable_autostart(self, system):
        if system == "Windows":
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.key_path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, self.app_name)
                self.logger.info("[AutoStartManager] 已移除 Windows 启动项")
            except FileNotFoundError:
                pass

        elif system == "Darwin":
            plist_path = os.path.expanduser(f"~/Library/LaunchAgents/com.{self.app_name}.plist")
            if os.path.exists(plist_path):
                os.remove(plist_path)
                self.logger.info("[AutoStartManager] 已移除 macOS 启动项")

        elif system == "Linux":
            desktop_path = os.path.expanduser(f"~/.config/autostart/{self.app_name}.desktop")
            if os.path.exists(desktop_path):
                os.remove(desktop_path)
                self.logger.info("[AutoStartManager] 已移除 Linux 启动项")

    def _set_macos_autostart(self, exe_path):
        label = f"com.{self.app_name}"
        plist_path = os.path.expanduser(f"~/Library/LaunchAgents/{label}.plist")
        plist = {
            "Label": label,
            "ProgramArguments": exe_path.split(),
            "RunAtLoad": True,
            "KeepAlive": False
        }
        os.makedirs(os.path.dirname(plist_path), exist_ok=True)
        with open(plist_path, "wb") as f:
            plistlib.dump(plist, f)
        self.logger.info(f"[AutoStartManager] macOS 启动项写入成功: {plist_path}")

    def _set_linux_autostart(self, exe_path):
        desktop_path = os.path.expanduser(f"~/.config/autostart/{self.app_name}.desktop")
        content = f"""[Desktop Entry]
Type=Application
Exec={exe_path}
Hidden=false
X-GNOME-Autostart-enabled=true
Name={self.app_name}
"""
        os.makedirs(os.path.dirname(desktop_path), exist_ok=True)
        with open(desktop_path, "w") as f:
            f.write(content)
        self.logger.info(f"[AutoStartManager] Linux 启动项写入成功: {desktop_path}")
