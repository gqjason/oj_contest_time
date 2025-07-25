import tkinter as tk
import sys
import json
import os
import win32gui
import psutil

from ui_and_logic.main_logic import AppLogic
from ui_and_logic.main_ui import AppUI
from settings.minimize_to_tray import MinimizeToTray
from settings.get_all_path import GetAllPath as GAP
from settings.autostart_manager import AutoStartManager as ASM
from logger import FileLogger
from background_worker import AppBackgroundWorker as ABW

file_name = "app_window_manager.py"
class AppWindowManager:
    class_name = "AppWindowManager"
    
    def __init__(self):
        self.logger = FileLogger(log_level="DEBUG")
        self.root = tk.Tk()
        
        self.config_path =  GAP().get_settings_path()
        
        self.app_logic = AppLogic()
        self.app_ui = AppUI(self.root, self.app_logic)
        self.background_worker = ABW()
        self.tray_manager = MinimizeToTray(self.root)
        self.settings = GAP().load_settings()

    def apply_tray_behavior(self):
        """托盘逻辑统一放在 run 中处理"""
        self.tray_manager.enable_running()
        
    def is_window_running(self, window_title):
        """检查是否存在指定标题的窗口"""
        def enum_handler(hwnd, result):
            if win32gui.IsWindowVisible(hwnd):
                if window_title in win32gui.GetWindowText(hwnd):
                    result.append(hwnd)

        windows = []
        win32gui.EnumWindows(enum_handler, windows)
        self.logger.info(f"[{file_name}][{self.class_name}] 有{len(windows)}个程序窗口正在运行")
        return len(windows) > 0

    def is_tray_icon_running(self, process_name="main.exe"):
        count_process_name = 0
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == process_name:
                self.logger.info(f"[{file_name}][{self.class_name}] 进程名：{process_name} (PID={proc.pid})")
                count_process_name += 1

        self.logger.info(f"[{file_name}][{self.class_name}] 共有 {count_process_name}个进程在后台运行")
        return count_process_name

    # 如果发现已有托盘进程，则强制结束
    def kill_tray_icon_process(self, count_process_name, process_name="main.exe"):
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == process_name and count_process_name > 2:
                try:
                    proc.kill()
                    proc.wait(timeout=0.5)  # 等待结束
                    count_process_name -= 1
                    self.logger.info(f"[{file_name}][{self.class_name}] 已结束进程：{process_name} (PID={proc.pid})")
                    
                except Exception as e:
                    self.logger.error(f"[{file_name}][{self.class_name}] 无法结束进程 {proc.info['name']}：{e}")
                    
    def get_current_exe_name(self):
        return os.path.basename(sys.executable)

    def run(self):
        # 防止多开
        window_title = self.root.title()  # 获取标题字符串
        current_process_name = self.get_current_exe_name()
        count_process_name = self.is_tray_icon_running(process_name=current_process_name)
        
        if self.is_window_running(window_title):
            self.logger.warning(f"[{file_name}][{self.class_name}] 应用程序已在运行，无法启动新实例。")
            sys.exit(0)
            
        if count_process_name > 2:
            self.logger.warning(f"[{file_name}][{self.class_name}] 托盘图标已在运行，无法启动新实例。")
            self.kill_tray_icon_process(count_process_name,process_name=current_process_name)
        
        ASM().apply(self.settings.get("autostart", False), self.settings.get("autostart_minimize", False))
        self.background_worker.start()
        self.settings = GAP().load_settings()
        
        should_hide = "--hidden" in sys.argv and self.settings.get("autostart_minimize", False)
        #self.logger.debug(f"[{file_name}][{self.class_name}] 应用程序启动，隐藏状态: {should_hide}, 设置自启动最小化: {self.settings.get("autostart_minimize")}, 运行托盘: {self.settings.get("minimize_to_tray")}, should_hide: {should_hide}")
        
        self.tray_manager.create_tray_icon()  # 初始化托盘
        self.logger.info(f"[{file_name}][{self.class_name}] 已创建托盘图标")

        self.apply_tray_behavior()
        self.logger.info(f"[{file_name}][{self.class_name}] 已运行self.apply_tray_behavior()")

        
        self.tray_manager.enable_running()  # 替换原 apply_tray_behavior
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

        self.root.mainloop()
        
        self.background_worker.stop()
