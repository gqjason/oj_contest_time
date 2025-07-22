# setting/autostart_manager.py
import os
import sys
import platform
import winreg
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

            exe_path = f'"{sys.executable}" {"--hidden" if minimized else ""}'.strip()

            if system == "Windows":
                self._set_windows_autostart(exe_path)
            else:
                self.logger.error(f"[AutoStartManager] 当前平台不支持自动启动设置: {system}")
        except Exception as e:
            self.logger.error(f"[AutoStartManager] 设置失败: {e}")

    def _set_windows_autostart(self, exe_path):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.key_path, 0, winreg.KEY_SET_VALUE)
        except FileNotFoundError:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.key_path)
        with key:
            winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, exe_path)
        self.logger.info(f"[AutoStartManager][_set_windows_autostart] 设置为: {exe_path}")

    def _disable_autostart(self, system):
        if system == "Windows":
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.key_path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, self.app_name)
                self.logger.info("[AutoStartManager] 已移除 Windows 启动项")
            except FileNotFoundError:
                pass
