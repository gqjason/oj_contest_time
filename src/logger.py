import os
import threading
from datetime import datetime
from tkinter import ttk, messagebox
from pathlib import Path

from settings.get_all_path import GetAllPath as GAP

class FileLogger:
    """
    多文件日志记录器，支持不同日志级别和日志分割
    
    参数:
        log_dir (str): 日志存储目录
        log_level (str): 默认日志级别 ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        max_size (int): 单个日志文件最大大小(MB)，0表示不分割
        backup_count (int): 保留的旧日志文件数量
    """
    
    # 日志级别映射
    LEVELS = {
        'DEBUG': 10,
        'INFO': 20,
        'WARNING': 30,
        'ERROR': 40,
        'CRITICAL': 50
    }

    logger_path = str(Path(__file__).parent.parent / "logs")
    
    @staticmethod
    def get_today_str():
        """获取当前日期字符串，格式为YYYY-MM-DD"""
        return datetime.now().strftime("%Y_%m_%d")
    file_name = f"{get_today_str()}"

    def __init__(self, log_level='INFO', max_size=10, backup_count=5):
        self.log_dir = GAP().get_logs_path()
        self.log_level = self.LEVELS[log_level.upper()]
        self.max_size = max_size * 1024 * 1024  # 转为字节
        self.backup_count = backup_count
        self.log_files = {}
        self.lock = threading.Lock()

        try:
            if not os.path.exists(self.log_dir):
                os.makedirs(self.log_dir)
        except PermissionError:
            # 若 Roaming 无权限，则回退
            self.log_dir = os.path.join(os.getcwd(), "oj_contest_time", "logs")
            os.makedirs(self.log_dir, exist_ok=True)
    

    def _get_log_path(self, file_name):
        """生成日志文件路径"""
        return os.path.join(self.log_dir, f"{file_name}.log")
    
    def _should_rotate(self, log_path):
        """检查是否需要分割日志"""
        if self.max_size <= 0:
            return False
            
        try:
            return os.path.exists(log_path) and os.path.getsize(log_path) >= self.max_size
        except OSError:
            return False
    
    def _rotate_log(self, log_path):
        """执行日志分割"""
        if not os.path.exists(log_path):
            return
            
        # 删除最旧的备份
        oldest = f"{log_path}.{self.backup_count}"
        if os.path.exists(oldest):
            os.remove(oldest)
        
        # 重命名现有备份
        for i in range(self.backup_count - 1, 0, -1):
            src = f"{log_path}.{i}"
            dest = f"{log_path}.{i+1}"
            if os.path.exists(src):
                os.rename(src, dest)
        
        # 重命名当前日志
        os.rename(log_path, f"{log_path}.1")
    
    def _write_log(self, level, message, log_file_name=file_name):
        """实际写入日志的底层方法"""
        log_path = self._get_log_path(log_file_name)
        
        with self.lock:
            # 检查日志分割
            if self._should_rotate(log_path):
                self._rotate_log(log_path)
            
            # 写入日志
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            log_line = f"[{timestamp}] [{level}] {message}\n"
            
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(log_line)
            except OSError as e:
                messagebox.showwarning(f"[logger.py][FileLogger][_write_log]\n内容: {message}\n无法写入日志文件: {e}")

    def log(self, level, message):
        """记录日志的通用方法
        
        参数:
            log_name (str): 日志名称/分类
            level (str): 日志级别
            message (str): 日志内容
        """
        if self.LEVELS.get(level.upper(), 0) < self.log_level:
            return
            
        self._write_log(level.upper(), message)
    
    # 快捷方法
    def debug(self, message):
        self.log('DEBUG', message)
    
    def info(self, message):
        self.log('INFO', message)
    
    def warning(self, message):
        self.log('WARNING', message)
    
    def error(self, message):
        self.log('ERROR', message)
    
    def critical(self, message):
        self.log('CRITICAL', message)
    
    def get_log_content(self, log_name, lines=100):
        """读取最近的日志内容"""
        log_path = self._get_log_path(log_name)
        if not os.path.exists(log_path):
            return "No log available"
        
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                return ''.join(f.readlines()[-lines:])
        except OSError:
            return "Error reading log"
        
        
if __name__ == "__main__":
    pass
    logger_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    lo = FileLogger()
    print(lo.logger_path,lo.log_dir)
    