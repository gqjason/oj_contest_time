import json
from datetime import datetime, timedelta, timezone

from .capture_nowcoder import get_nowcoder
from .capture_atcoder import get_atcoder
from .capture_codeforces import get_codeforces
from settings.get_all_path import GetAllPath as GAP
from logger import FileLogger

file_name = "capture.py"
class CaptureAllInformation:
    class_name = "CaptureAllInformation"
    
    def __init__(self, command = None):
        self.command = command
        self.config_path = GAP().get_settings_path()
        self.logger = FileLogger(log_level="DEBUG")
        self.setting = self.load_settings()
        
    def load_settings(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.logger.info(f"[{file_name}][{self.class_name}] 文件路径: {self.config_path}")
                return json.load(f)
        except Exception as e:
            self.logger.error(f"[AppWindowManager] 无法加载设置: {e}")
            return {}
    
    def get_all_website(self):
        gnc = get_nowcoder()
        gat = get_atcoder()
        gcf = get_codeforces()
        self.setting = self.load_settings()
        res = []
        
        if self.command == "display":
            res += gcf.get_cf() if self.is_capture_contest("is_capture_codeforces") else []        
            res += gnc.get_nc() if self.is_capture_contest("is_capture_nowcoder") else []
            res += gat.get_ac() if self.is_capture_contest("is_capture_atcoder") else []
            
            self.logger.debug(f"[{file_name}][{self.class_name}] 选择显示的比赛信息:\n" +
                            f"cf: {self.is_capture_contest("is_capture_codeforces")}\n" +
                            f"nk: {self.is_capture_contest("is_capture_nowcoder")}\n" +
                            f"at: {self.is_capture_contest("is_capture_atcoder")}")
                        
        elif self.command == "update":
            res += gcf.get_cf() if self.is_capture_contest("is_notify_codeforces") else []        
            res += gnc.get_nc() if self.is_capture_contest("is_notify_nowcoder") else []
            res += gat.get_ac() if self.is_capture_contest("is_notify_atcoder") else []
            
            self.logger.debug(f"[{file_name}][{self.class_name}] 选择更新比赛信息:\n" +
                            f"cf: {self.is_capture_contest("is_notify_codeforces")}\n" + 
                            f"nk: {self.is_capture_contest("is_notify_nowcoder")}\n" +
                            f"at: {self.is_capture_contest("is_notify_atcoder")}")
                    
        else:
            res += gcf.get_cf()
            res += gnc.get_nc()
            res += gat.get_ac()
        return res
    
    def is_capture_contest(self, key):
        return self.setting.get(key)
    
    def get_upcoming_contests(self):
        # 获取所有比赛
        res = self.get_all_website()
        
        # 确保所有时间都是时区感知的 UTC 时间
        for contest in res:
            if contest['start_time'].tzinfo is None:
                # 如果时间没有时区信息，假设为 UTC 并添加时区
                contest['start_time'] = contest['start_time'].replace(tzinfo=timezone.utc)
        
        # 按开始时间排序
        res.sort(key=lambda x: x['start_time'])
        return res
        
    def filter_today_competition(self, result):
        # 获取当前 UTC 时间（时区感知）
        now_utc = datetime.now().astimezone()
    
        # 计算今天 UTC 时间的开始和结束（时区感知）
        today_start_utc = now_utc.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
        today_end_utc = today_start_utc + timedelta(days=1)
        
        # 筛选今天还未开始的比赛
        upcoming_today = []
        for contest in result:
            # 确保比赛时间是时区感知的
            start_time = contest['start_time']
            #print(start_time, today_start_utc)
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=timezone.utc)
            
            # 检查比赛是否在今天
            if start_time < today_start_utc or start_time >= today_end_utc:
                continue
            
            # 检查比赛是否还未开始
            if start_time > now_utc:
                # 创建副本以避免修改原始数据
                contest_copy = contest.copy()
                contest_copy['start_time'] = start_time
                upcoming_today.append(contest_copy)
        
        return upcoming_today

    def return_today_upcoming_contest(self):
        
        upcoming_contest = self.get_upcoming_contests()
        today_contest = self.filter_today_competition(upcoming_contest)
        return today_contest
    
    def return_all_upcoming_contest(self):
        upcoming_contest = self.get_upcoming_contests()
        return upcoming_contest

    
if __name__ == '__main__':
    pass
    