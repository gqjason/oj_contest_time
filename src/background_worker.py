# app/background_worker.py

import threading
import time
import random
from datetime import datetime, timezone

from logger import FileLogger
from information.update_contest_data import UpdateContestData as UCD
from ui_and_logic.setting_logic import SettingsManager as SM
from settings.get_all_path import GetAllPath as GAP
file_name = "background_worker.py"
class AppBackgroundWorker:
    class_name = "AppBackgroundWorker"
    
    def __init__(self):
        self._running = False
        self._thread = None
        self.logger = FileLogger(log_level="DEBUG")

    def background_run(self):
        ucd = UCD()
        ucd.updating_data() # 初始化
        def is_on_the_hour_utc():
            """检查UTC时间是否为整点"""
            now = datetime.now(timezone.utc)
            return now.minute == 0 and now.second == 0
        self.logger.info(f"[{file_name}][{self.class_name}] 后台任务启动")
        while self._running:
            try:
                # 在这里放置你的后台逻辑
                self.logger.debug(f"[{file_name}][{self.class_name}] 正在运行后台任务...")
                
                if is_on_the_hour_utc():
                    ucd.updating_data()

                time.sleep(2)
                current_settings = GAP().load_settings()
                self.logger.debug(f"[{file_name}][{self.class_name}][run] \"desktop_notify\" is {current_settings["desktop_notify"]}")
                if current_settings["desktop_notify"]:
                    ucd.prepare_contest_notify()
            except Exception as e:
                self.logger.error(f"[{file_name}][{self.class_name}][_run] 运行时异常: {e}")

        self.logger.info(f"[{file_name}][{self.class_name}] 后台任务已停止")

    def start(self):
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self.background_run, daemon=True)
            self._thread.start()
            self.logger.info(f"[{file_name}][{self.class_name}] 后台线程已启动")

    def stop(self):
        self._running = False
        self.logger.info(f"[{file_name}][{self.class_name}] 停止信号已发出")

if __name__ == "__main__":
    pass