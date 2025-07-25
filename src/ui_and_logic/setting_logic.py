import os
import json
import platform
import subprocess
from pathlib import Path

# from settings.minimize_to_tray import MinimizeToTray as MTT
from settings.autostart_manager import AutoStartManager as ASM
from settings.get_all_path import GetAllPath as GAP
from logger import FileLogger

file_name = "setting_logic.py"
class SettingsManager:
    class_name = "SettingsManager"

    """管理应用程序设置的类"""
    DEFAULT_SETTINGS = {
        "autostart": False,
        "minimize_to_tray": False,
        # "autostart_minimize": False,
        
        "is_capture_codeforces": False,
        "is_capture_nowcoder": False,
        "is_capture_atcoder": False,
        
        "desktop_notify": False,
        "is_notify_codeforces": False,
        "is_notify_nowcoder": False,
        "is_notify_atcoder": False,
        
    }

    def __init__(self, main_window=None, config_file=None):
        self.main_window = main_window
        self.logger = FileLogger()

        self.config_file = GAP().get_settings_path()
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.load_settings()


    def load_settings(self):
        """从配置文件加载设置"""
        try:
            if not self.config_file.exists():
                self.save_settings()  # 保存默认配置
        
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
        # ui_instance.minimize_to_tray_var.set(self.get_setting("minimize_to_tray"))
        ui_instance.autostart_minimize_var.set(self.get_setting("autostart_minimize"))
        
        ui_instance.capturing_codeforces_var.set(self.get_setting("is_capture_codeforces"))
        ui_instance.capturing_nowcoder_var.set(self.get_setting("is_capture_nowcoder"))
        ui_instance.capturing_atcoder_var.set(self.get_setting("is_capture_atcoder"))
        
        ui_instance.desktop_notify_var.set(self.get_setting("desktop_notify"))
        ui_instance.notify_codeforces_var.set(self.get_setting("is_notify_codeforces"))
        ui_instance.notify_nowcoder_var.set(self.get_setting("is_notify_nowcoder"))
        ui_instance.notify_atcoder_var.set(self.get_setting("is_notify_atcoder"))
        

    def handle_save(self, ui_instance):
        """处理保存按钮点击事件"""
        settings_data = {
            "autostart": ui_instance.autostart_var.get(),
            # "minimize_to_tray": ui_instance.minimize_to_tray_var.get(),
            "autostart_minimize": ui_instance.autostart_minimize_var.get(),
            
            "is_capture_codeforces": ui_instance.capturing_codeforces_var.get(),
            "is_capture_nowcoder": ui_instance.capturing_nowcoder_var.get(),
            "is_capture_atcoder": ui_instance.capturing_atcoder_var.get(),
            
            "desktop_notify": ui_instance.desktop_notify_var.get(),
            "is_notify_codeforces": ui_instance.notify_codeforces_var.get(),
            "is_notify_nowcoder": ui_instance.notify_nowcoder_var.get(),
            "is_notify_atcoder": ui_instance.notify_atcoder_var.get(),
        }
        
        self.update_settings(**settings_data)
        if self.save_settings():
            if self.apply_system_settings():
                return True
        return False


    def apply_system_settings(self):
        asm = ASM()
        try:
            self.logger.info(f"[{file_name}][{self.class_name}] 正在应用系统设置...")

            autostart = self.settings.get("autostart", False)
            autostart_minimized = self.settings.get("autostart_minimize", False)
            # minimize_to_tray = self.settings.get("minimize_to_tray", False)
            desktop_notify = self.settings.get("desktop_notify", False)

            # 合并开机启动逻辑
            try:
                self.logger.info(f"[{file_name}][{self.class_name}] 正在设置开机自启动和静默启动...")
                asm.apply(autostart, autostart_minimized)
                self.logger.info(f"[{file_name}][{self.class_name}] 开机启动设置完成")
            except Exception as e:
                self.logger.error(f"[{file_name}][{self.class_name}] 开机启动设置失败: {e}")
                return False

            # # 最小化托盘逻辑
            # if self.main_window:
            #     if minimize_to_tray:
            #         self.logger.info(f"[{file_name}][{self.class_name}] 启用最小化托盘...")
            #     else:
            #         self.logger.info(f"[{file_name}][{self.class_name}] 禁用最小化托盘...")
            # else:
            #     self.logger.warning(f"[{file_name}][{self.class_name}] 主窗口未设置，跳过最小化托盘设置")

            # 桌面通知
            if desktop_notify:
                self.logger.info(f"[{file_name}][{self.class_name}] 启用桌面通知...")
            else:
                self.logger.info(f"[{file_name}][{self.class_name}] 禁用桌面通知...")

            self.logger.info(f"[{file_name}][{self.class_name}] 成功保存设置")
            return True

        except Exception as e:
            self.logger.error(f"[{file_name}][{self.class_name}][apply_system_settings] 保存设置失败\n错误: {e}")
            return False


    def handle_cancel(self, dialog):
        """处理取消按钮点击事件"""
        dialog.destroy()
                 
    def open_folder_in_explorer(self, path: str):
        """在操作系统的文件资源管理器中打开指定目录"""
        if not os.path.exists(path):
            self.logger.warning(f"[{file_name}][{self.class_name}][open_folder_in_explorer] 路径不存在: {path}")
            return
        
        system = platform.system()
        try:
            if system == "Windows":
                os.startfile(path)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", path])
            else:  # Linux
                subprocess.run(["xdg-open", path])
        except Exception as e:
            self.logger.error(f"[{file_name}][{self.class_name}][open_folder_in_explorer] 打开文件夹失败: {e}")

if __name__ == "__main__":
    pass
