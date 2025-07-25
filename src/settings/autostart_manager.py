# setting/autostart_manager.py
import os
import sys
import platform
import winreg
import getpass
import subprocess
from logger import FileLogger
from settings.get_all_path import GetAllPath as GAP
file_name = "autostart_manager.py"
class AutoStartManager:
    class_name = "AutoStartManager"
    def __init__(self):
        self.logger = FileLogger()
        self.app_name = "CaptureOJContestTime"
        self.key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        self.exe_path = GAP().get_current_exe_path()
        self.vbs_path = GAP().get_scripts_path()
        self.vbs_file_path = os.path.join(self.vbs_path, f"{self.app_name}_silent_launcher.vbs")
        self.task_name = f"startup_{self.app_name}"
        self.task_path = f'wscript.exe \\"{self.vbs_file_path}"'
    
    def apply(self, autostart: bool, minimized: bool):
        system = platform.system()
        self.logger.info(f"[AutoStartManager] 系统平台: {system}")
        try:
            if not autostart:
                self.disable_autostart()
                self.logger.info("[AutoStartManager] 已禁用开机启动")
                return

            self.logger.info(f"[{file_name}][{self.class_name}] exe_path: {self.exe_path}")

            self.enable_autostart(minimized)

        except Exception as e:
            self.logger.error(f"[AutoStartManager] 设置失败: {e}")

    def enable_autostart(self, minimized):
        self.create_vbs_regedit_script()  # 创建 VBScript 脚本
        self.logger.info(f"[AutoStartManager] VBScript 文件已创建: {self.vbs_file_path}")
        
        if minimized:
            self.register_task_scheduler()  # 注册任务计划程序
            self.logger.info(f"[AutoStartManager] 任务计划程序已注册: {self.task_name}")
        
    def disable_autostart(self):
        self.remove_vbs_regedit_script()  # 删除 VBScript 脚本
        self.logger.info(f"[AutoStartManager] VBScript 文件已删除: {self.vbs_file_path}")
        self.cancel_task_scheduler()  # 取消任务计划程序
        self.logger.info(f"[AutoStartManager] 任务计划程序已取消: {self.task_name}")
    
    def create_vbs_regedit_script(self):

        os.makedirs(self.vbs_path, exist_ok=True) # 确保目录存在
        # 最终传递给WshShell.Run的字符串
        run_command_quoted = f'"{self.exe_path} --silent"' # 确保整个命令字符串被双引号包裹
        vbs_content = f"""
        Set WshShell = WScript.CreateObject("WScript.Shell")
        WshShell.Run "{run_command_quoted}", 0, False
        """
        # 移除VBS内容中的空行和多余空格，使其更紧凑
        vbs_content = "\n".join(
            [line.strip() for line in vbs_content.splitlines() if line.strip()]
        )
        try:
            # 写入 VBScript 文件
            with open(self.vbs_file_path, "w") as f:
                f.write(vbs_content)
            self.logger.info(f"[{file_name}][{self.class_name}] VBScript file created at: {self.vbs_file_path}")

            # 写入注册表
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key_root = winreg.HKEY_CURRENT_USER
            key = winreg.OpenKey(key_root, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, f'wscript.exe "{self.vbs_file_path}"')
            winreg.CloseKey(key)

            self.logger.info(f"[{file_name}][{self.class_name}] Successfully set '{self.app_name}' to autostart silently via VBScript.")
            self.logger.info(f"[{file_name}][{self.class_name}] Registry entry: {key_root}\\{key_path}\\{self.app_name} = wscript.exe \"{self.vbs_file_path}\"")
            return True

        except PermissionError:
            self.logger.warning(f"[{file_name}][{self.class_name}][create_vbs_regedit_script] Permission denied: You need administrator privileges to write to HKEY_LOCAL_MACHINE.")
            return False
        except Exception as e:
            self.logger.error(f"[{file_name}][{self.class_name}][create_vbs_regedit_script] An error occurred: {e}")
            return False

    def remove_vbs_regedit_script(self):
        try:
            # 尝试删除 VBScript 文件
            if os.path.exists(self.vbs_file_path):
                os.remove(self.vbs_file_path)
                self.logger.info(f"Removed VBScript file: {self.vbs_file_path}")
            else:
                self.logger.info(f"VBScript file not found: {self.vbs_file_path}")

            # 尝试从注册表删除
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key_root = winreg.HKEY_CURRENT_USER

            try:
                key = winreg.OpenKey(key_root, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, self.app_name)
                winreg.CloseKey(key)
                self.logger.info(f"Successfully removed '{self.app_name}' from autostart.")
                return True
            
            except FileNotFoundError: # 如果注册表键不存在
                self.logger.warning(f"Registry entry for '{self.app_name}' not found.")
                return True # 视为成功，因为它已经不在了
            except PermissionError:
                self.logger.error("Permission denied: You need administrator privileges to remove from HKEY_LOCAL_MACHINE.")
                return False

        except Exception as e:
            self.logger.error(f"An error occurred during removal: {e}")
            return False
        
    def register_task_scheduler(self):
        cmd = [
            "schtasks",
            "/Create",
            "/SC", "ONSTART",
            "/DELAY", "0000:05",  # 延迟5秒启动
            "/TN", self.task_name,
            "/TR", self.task_path,
            "/RL", "HIGHEST",           # 最高权限运行
            "/F",                       # 强制覆盖已有任务
            "/RU", getpass.getuser(),   # 当前用户
            
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            self.logger.info(f"[{file_name}][{self.class_name}] 任务 [startup_{self.app_name}] 创建成功。")
        else:
            self.logger.error(f"[{file_name}][{self.class_name}][create_task_scheduler] 创建任务失败：{result.stderr}")

    def cancel_task_scheduler(self):
        
        # 查询任务是否存在
        query_cmd = [
            "schtasks",
            "/Query",
            "/TN", self.task_name
        ]
        query_result = subprocess.run(query_cmd, capture_output=True, text=True)

        if query_result.returncode != 0:
            self.logger.warning(f"[{file_name}][{self.class_name}] 任务 [startup_{self.app_name}] 不存在，跳过取消。")
            return
        cmd = [
            "schtasks",
            "/Delete",
            "/TN", self.task_name,
            "/F"  # 强制删除
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            self.logger.info(f"[{file_name}][{self.class_name}] 任务 [startup_{self.app_name}] 取消成功。")
        else:
            self.logger.error(f"[{file_name}][{self.class_name}][cancel_task_scheduler] 取消任务失败：{result.stderr}")