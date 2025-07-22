from .capture_nowcoder import get_nowcoder
from .capture_atcoder import get_atcoder
from .capture_codeforces import get_codeforces
from datetime import datetime, timedelta, timezone

class CaptureAllInformation:
    
    def __init__(self):
        pass
    
    def get_all_website(self):
        gnc = get_nowcoder()
        gat = get_atcoder()
        gcf = get_codeforces()
        res = []
        res += gnc.get_nc()
        res += gcf.get_cf()
        res += gat.get_ac()
        
        return res
    
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
        
    def filter_today_competition(self, res):
        # 获取当前 UTC 时间（时区感知）
        now_utc = datetime.now().astimezone()
    
        # 计算今天 UTC 时间的开始和结束（时区感知）
        today_start_utc = now_utc.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
        today_end_utc = today_start_utc + timedelta(days=1)
        
        # 筛选今天还未开始的比赛
        upcoming_today = []
        for contest in res:
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
    