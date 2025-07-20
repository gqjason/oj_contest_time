import json
import sys
import os
import logging
import platform
import datetime
import random
from pathlib import Path

from setting.autostarting import AutoStartOption as ASO
from setting.minimize_to_tray import MinimizeToTray as MTT
from setting.autostart_minimize import AutoStartMinimize as ASM
from information.capture import CaptureAllInformation as CAI
from logger import FileLogger

file_name = "setting_logic.py"

class SettingsManager:
    class_name = "SettingsManager"

    """管理应用程序设置的类"""
    DEFAULT_SETTINGS = {
        "autostart": False,
        "minimize_to_tray": False,
        "autostart_minimize": False,
        "desktop_notify": False,
        "notify_receiver_email": "",
        "theme": "light",
        "language": "zh_CN"
    }

    @staticmethod
    def get_base_path():
        """获取项目根路径（支持 PyInstaller 打包和未打包运行）"""
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent
        else:
            return Path(__file__).resolve().parent.parent

    def __init__(self, main_window=None, config_file=None):
        """
        初始化设置管理器
        参数:
            main_window: 主窗口对象
            config_file: 设置文件路径（可选）
        """
        self.main_window = main_window
        base_path = self.get_base_path()
        self.config_file = Path(config_file) if config_file else base_path / "configs" / "settings.json"
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.logger = FileLogger()
        self.load_settings()

    def load_settings(self):
        """从配置文件加载设置"""
        try:
            if not self.config_file.exists():
                self.save_settings()  # 保存默认配置
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    for key, value in self.DEFAULT_SETTINGS.items():
                        self.settings[key] = loaded_settings.get(key, value)
        except Exception as e:
            self.logger.error(
                f"[{file_name}][{self.class_name}][load_settings] 加载设置失败: {e}")

    def save_settings(self):
        """保存当前设置到配置文件"""
        try:
            config_dir = self.config_file.parent
            if not config_dir.exists():
                config_dir.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)

            self.logger.info(f"[{file_name}][{self.class_name}] 正在保存设置")
            return True
        except Exception as e:
            self.logger.error(
                f"[{file_name}][{self.class_name}][save_settings] 保存设置失败: {e}")
            return False

    def get_setting(self, key):
        """获取指定设置项的值"""
        return self.settings.get(key, self.DEFAULT_SETTINGS.get(key))

    def update_setting(self, key, value):
        """更新单个设置项"""
        if key in self.DEFAULT_SETTINGS:
            self.settings[key] = value
            return True
        return False

    def update_settings(self, **kwargs):
        """批量更新设置"""
        for key, value in kwargs.items():
            if key in self.DEFAULT_SETTINGS:
                self.settings[key] = value

    def apply_settings(self, ui_instance):
        """将设置应用到UI界面"""
        ui_instance.autostart_var.set(self.get_setting("autostart"))
        ui_instance.minimize_to_tray_var.set(self.get_setting("minimize_to_tray"))
        ui_instance.autostart_minimize_var.set(self.get_setting("autostart_minimize"))
        ui_instance.desktop_notify_var.set(self.get_setting("desktop_notify"))

    def handle_save(self, ui_instance):
        """处理保存按钮点击事件"""
        settings_data = {
            "autostart": ui_instance.autostart_var.get(),
            "minimize_to_tray": ui_instance.minimize_to_tray_var.get(),
            "autostart_minimize": ui_instance.autostart_minimize_var.get(),
            "desktop_notify": ui_instance.desktop_notify_var.get(),
        }
        self.update_settings(**settings_data)
        if self.save_settings():
            if self.apply_system_settings():
                return True
        return False

    def apply_system_settings(self):
        """将设置应用到操作系统"""
        try:
            self.logger.info(f"[{file_name}][{self.class_name}] 正在应用系统设置...")

            as_enable = self.settings["autostart"]
            asm_enable = self.settings["autostart_minimize"]

            aso = ASO()
            if as_enable and not asm_enable:
                self.logger.info(f"[{file_name}][{self.class_name}] 正在配置开机自启动...")
                aso.configure_autostart(enable=True)
                self.logger.info(f"[{file_name}][{self.class_name}] 已经配置开机自启动...")
            else:
                self.logger.info(f"[{file_name}][{self.class_name}] 正在禁用开机自启动...")
                aso.configure_autostart(enable=False)
                self.logger.info(f"[{file_name}][{self.class_name}] 已经禁用开机自启动...")

            if self.main_window:
                mtt = MTT(self.main_window)
                if self.settings["minimize_to_tray"]:
                    self.logger.info(f"[{file_name}][{self.class_name}] 正在开启最小化到后台运行...")
                    mtt.enable_running()
                    self.logger.info(f"[{file_name}][{self.class_name}] 已经开启最小化到后台运行...")
                else:
                    self.logger.info(f"[{file_name}][{self.class_name}] 正在关闭最小化到后台运行...")
                    mtt.disable_running()
                    self.logger.info(f"[{file_name}][{self.class_name}] 已经关闭最小化到后台运行...")
            else:
                self.logger.warning(f"[{file_name}][{self.class_name}] 主窗口未设置，跳过最小化托盘设置")

            try:
                asm = ASM(as_enable, asm_enable)
                asm.enable_autostart_minimize()
                self.logger.info(f"[{file_name}][{self.class_name}] 开启静默启动成功")
            except Exception as e:
                self.logger.error(f"[{file_name}][{self.class_name}] 关闭静默启动失败\n错误: {e}")
                return False

            if self.settings["desktop_notify"]:
                self.logger.info(f"[{file_name}][{self.class_name}] 启用桌面通知...")
                self.switch_system_notification(True)
            else:
                self.logger.info(f"[{file_name}][{self.class_name}] 禁用桌面通知...")

            self.logger.info(f"[{file_name}][{self.class_name}] 成功保存设置")

        except Exception as e:
            self.logger.error(
                f"[{file_name}][{self.class_name}][apply_system_settings] 保存设置失败\n错误: {e}")
            return False

        return True

    def handle_cancel(self, dialog):
        """处理取消按钮点击事件"""
        dialog.destroy()

    def switch_system_notification(self, enable):
        if enable:
            try:
                # 调用系统通知逻辑（待实现）
                pass
            except Exception as e:
                self.logger.error(f"发送通知失败: {e}")

if __name__ == "__main__":
    pass
