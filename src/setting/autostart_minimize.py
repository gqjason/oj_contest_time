import os
import sys
import winreg as reg
import tkinter as tk

from .autostarting import AutoStartOption as ASO
from logger import FileLogger

file_name = "autostart_minimize.py"
class AutoStartMinimize:
    
    class_name = "AutoStartMinimize"
    
    def __init__(self, as_enable, asm_enable):
        
        self.as_enable = as_enable
        self.asm_enable = asm_enable
        
        self.logger = FileLogger()
        
    def enable_autostart_minimize(self):
        # 获取当前可执行文件路径
        exe_path = sys.executable
        # 注册表路径
        key = reg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "CaptureOJContestTime"
        aso = ASO()
        
        if self.asm_enable:
            
            try:
                aso._configure_windows_autostart(False)
                reg_key = reg.CreateKey(key, key_path)
                reg.SetValueEx(reg_key, app_name, 0, reg.REG_SZ, exe_path)
                reg.CloseKey(reg_key)
                self.logger.info(
                    f"[{file_name}][{self.class_name}] 成功开启静默启动")
        
            except Exception as e:
                self.logger.error(
                    f"[{file_name}][{self.class_name}][enable_autostart_minimize] 无法开启静默启动\n错误: {e}")
        
        
        elif not self.asm_enable and not self.as_enable:
            
            try:
                try:
                    reg_key = reg.OpenKey(key, key_path, 0, reg.KEY_SET_VALUE)
                    reg.DeleteValue(reg_key, app_name)
                    reg.CloseKey(reg_key)
                except FileNotFoundError:
                    pass
                
                self.logger.info(
                    f"[{file_name}][{self.class_name}] 成功关闭静默启动")
            except Exception as e:
                self.logger.error(
                    f"[{file_name}][{self.class_name}][enable_autostart_minimize] 无法关闭静默启动\n错误: {e}")

if __name__ == "__main__":
    app = AutoStartMinimize(enable=True)
    app.setup_and_run()