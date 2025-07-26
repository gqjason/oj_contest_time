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
        self.task_path = f'wscript.exe {self.vbs_file_path}'

    
    def apply(self, autostart: bool, minimized: bool):
        system = platform.system()
        self.logger.info(f"[{file_name}][{self.class_name}] 系统平台: {system}")
        try:
            if not autostart:
                self.disable_autostart()
                self.logger.info(f"[{file_name}][{self.class_name}] 已禁用开机启动")
                return

            self.logger.info(f"[{file_name}][{self.class_name}] exe_path: {self.exe_path}")

            self.enable_autostart(minimized)

        except Exception as e:
            self.logger.error(f"[{file_name}][{self.class_name}] 设置失败: {e}")

    def enable_autostart(self, minimized):
        self.register_regedit(self.exe_path)  # 注册注册表条目
        self.logger.info(f"[{file_name}][{self.class_name}] 注册表条目已注册: {self.app_name}")

        if minimized:
            self.register_regedit(self.vbs_file_path)  # 注册 VBScript 脚本
            self.logger.info(f"[{file_name}][{self.class_name}] VBScript 文件已注册: {self.vbs_file_path}")
            self.create_vbs_script()  # 创建 VBScript 脚本
            self.logger.info(f"[{file_name}][{self.class_name}] VBScript 文件已创建: {self.vbs_file_path}")
            self.register_task_scheduler()  # 注册任务计划程序
            self.logger.info(f"[{file_name}][{self.class_name}] 任务计划程序已注册: {self.task_name}")

    def disable_autostart(self):
        self.remove_regedit()  # 删除注册表条目
        self.logger.info(f"[{file_name}][{self.class_name}] 注册表条目已删除: {self.app_name}")
        self.remove_vbs_script()  # 删除 VBScript 脚本
        self.logger.info(f"[{file_name}][{self.class_name}] VBScript 文件已删除: {self.vbs_file_path}")
        self.cancel_task_scheduler()  # 取消任务计划程序
        self.logger.info(f"[{file_name}][{self.class_name}] 任务计划程序已取消: {self.task_name}")

    def register_regedit(self, register_file_path):

        try:
            # 写入注册表
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key_root = winreg.HKEY_CURRENT_USER
            reg_value = f'"{os.path.normpath(register_file_path)}" --silent'
            with winreg.OpenKey(key_root, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, reg_value)
            
            self.logger.info(f"Added registry entry: {key_root}\\{key_path}\\{self.app_name} = {reg_value}")
            return True

        except Exception as e:
            self.logger.error(f"创建注册表条目错误: {str(e)}")
            return False
        
    def remove_regedit(self):
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key_root = winreg.HKEY_CURRENT_USER

            with winreg.OpenKey(key_root, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, self.app_name)

            self.logger.info(f"删除注册表条目: {key_root}\\{key_path}\\{self.app_name} 成功。")
            return True
        
        except FileNotFoundError:
            self.logger.warning(f"未找到 '{self.app_name}' 的注册表条目。")
            return True

    def create_vbs_script(self):

        self.vbs_file_path = os.path.normpath(self.vbs_file_path)
        # 确保目录存在
        os.makedirs(os.path.dirname(self.vbs_file_path), exist_ok=True)
        
        self.exe_path = os.path.abspath(self.exe_path)
        exe_path_quoted = f'"{self.exe_path}"'
        exe_path_escaped = exe_path_quoted.replace('"', '""')
        run_command = f"{exe_path_escaped} --silent"
        window_style = 2
        # 构建VBScript内容
        vbs_content = f"""
    Set asmShell = WScript.CreateObject("WScript.Shell")
    asmShell.Run "{run_command}", {window_style}, False
        """
        vbs_content = "\n".join(
            [line.strip() for line in vbs_content.splitlines() if line.strip()]
        )
        
        try:
            # 写入 VBScript 文件前记录内容
            self.logger.debug(f"VBScript content:\n{vbs_content}")
            
            # 写入文件
            with open(self.vbs_file_path, "w") as f:
                f.write(vbs_content)
            self.logger.info(f"VBScript file created at: {self.vbs_file_path}")
            
        except Exception as e:
            self.logger.error(f"创建vbscript文件失败: {e}")

    def remove_vbs_script(self):
        try:
            # 尝试删除 VBScript 文件
            if os.path.exists(self.vbs_file_path):
                os.remove(self.vbs_file_path)
                self.logger.info(f"删除VBScript文件: {self.vbs_file_path} 成功。")
            else:
                self.logger.info(f"未找到VBScript文件: {self.vbs_file_path} ，跳过删除。")

        except Exception as e:
            self.logger.error(f"删除过程中发生错误: {e}")
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