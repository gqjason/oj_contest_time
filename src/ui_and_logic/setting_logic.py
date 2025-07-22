import json
from pathlib import Path

from setting.minimize_to_tray import MinimizeToTray as MTT
from setting.autostart_manager import AutoStartManager as ASM
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

    def __init__(self, main_window=None, config_file=None):
        self.main_window = main_window
        self.logger = FileLogger()

        base_path = self.get_base_path()
        config_dir = base_path / "configs"
        config_dir.mkdir(parents=True, exist_ok=True)

        self.config_file = Path(config_file) if config_file else config_dir / "settings.json"
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.load_settings()

    @staticmethod
    def get_base_path():
        return Path.home() / "oj_contest_time"


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
        mtt = MTT(self.main_window)
        asm = ASM()
        try:
            self.logger.info(f"[{file_name}][{self.class_name}] 正在应用系统设置...")

            autostart = self.settings.get("autostart", False)
            autostart_minimized = self.settings.get("autostart_minimize", False)
            minimize_to_tray = self.settings.get("minimize_to_tray", False)
            desktop_notify = self.settings.get("desktop_notify", False)

            # 合并开机启动逻辑
            try:
                self.logger.info(f"[{file_name}][{self.class_name}] 正在设置开机自启动和静默启动...")
                asm.apply(autostart, autostart_minimized)
                self.logger.info(f"[{file_name}][{self.class_name}] 开机启动设置完成")
            except Exception as e:
                self.logger.error(f"[{file_name}][{self.class_name}] 开机启动设置失败: {e}")
                return False

            # 最小化托盘逻辑
            if self.main_window:
                if minimize_to_tray:
                    self.logger.info(f"[{file_name}][{self.class_name}] 启用最小化托盘...")
                    mtt.enable_running()
                else:
                    self.logger.info(f"[{file_name}][{self.class_name}] 禁用最小化托盘...")
                    mtt.disable_running()
            else:
                self.logger.warning(f"[{file_name}][{self.class_name}] 主窗口未设置，跳过最小化托盘设置")

            # 桌面通知
            if desktop_notify:
                self.logger.info(f"[{file_name}][{self.class_name}] 启用桌面通知...")
                self.switch_system_notification(True)
            else:
                self.logger.info(f"[{file_name}][{self.class_name}] 禁用桌面通知...")
                self.switch_system_notification(False)

            self.logger.info(f"[{file_name}][{self.class_name}] 成功保存设置")
            return True

        except Exception as e:
            self.logger.error(f"[{file_name}][{self.class_name}][apply_system_settings] 保存设置失败\n错误: {e}")
            return False


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
