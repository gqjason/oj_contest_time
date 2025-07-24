import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta, timezone

from logger import FileLogger
from settings.get_all_path import GetAllPath as GAP
from information.gather_total_contest_data import CaptureAllInformation as CAI
from settings.desktop_notification import DesktopNotification as DN

file_name = "update_contest_data.py"
class UpdateContestData:
    class_name = "UpdateContestData"
    
    def __init__(self):
        self.logger = FileLogger()
        self.contest_path = GAP().get_contest_data_path()
        
        if not self.contest_path.exists():
            self.logger.warning(f"[{file_name}][{self.class_name}][__init__] 文件不存在，正在创建空文件")
            self.updating_data()  # 初始化时更新数据

    
    def updating_data(self):
        cai = CAI(command="update")
        contest_data = cai.get_upcoming_contests()  # 应返回 list[dict]
        self.save_contest_data(contest_data)

    def prepare_contest_notify(self):
        contest_data = self.read_contest_data()
        if contest_data and isinstance(contest_data, list):
            self.logger.info(f"[{file_name}][{self.class_name}][prepare_contest_notify] 读取成功，共 {len(contest_data)} 条记录")
            
            for contest in contest_data:
                # 获取时间
                start_time_str = contest['start_time']
                start_time = datetime.fromisoformat(start_time_str)
                current_time = datetime.now().astimezone()
                # 3. 统一为 UTC 时间格式
                start_time_utc = start_time.astimezone(timezone.utc)
                current_time_utc = current_time.astimezone(timezone.utc)
                                
                start_time_seconds = start_time_utc.timestamp()
                current_time_seconds = current_time_utc.timestamp()
                time_gap = abs(abs(current_time_seconds-start_time_seconds) - 3600)
                
                if time_gap <= 10.0:
                    
                    contest_platform = contest['platform']
                    contest_icon_path = "resources/icons/app.ico"
                    
                    if contest_platform == "Codeforces":
                        contest_icon_path = "resources/icons/codeforces.ico"
                    elif contest_platform == "AtCoder":
                        contest_icon_path = "resources/icons/atcoder.ico"
                    elif contest_platform == "牛客":
                        contest_icon_path = "resources/icons/nowcoder.ico"
                        
                    contest_title = "比赛还有一个小时开始"
                    contest_message = f"平台: {contest['platform']}\n"+ \
                            f"比赛标题: {contest['title']}\n" + \
                            f"比赛时间: {contest['time']}\n"
                            
                    dn = DN(icon_path=contest_icon_path)
                    dn.send(
                        title=contest_title,
                        message=contest_message,
                        timeout=5
                    )
                            
                
        else:
            self.logger.warning(f"[{file_name}][{self.class_name}][f1] 没有读取到有效比赛数据")

    def read_contest_data(self, encoding='utf-8') -> list[dict]:
        try:
            # if not self.contest_path.exists():
            #     self.logger.warning(f"[{file_name}][{self.class_name}][read_contest_data] 文件不存在，正在创建空文件")
            #     self.save_contest_data([], encoding=encoding)
            #     return []
            df = pd.read_csv(self.contest_path, encoding=encoding)
            return df.to_dict(orient="records")
        except Exception as e:
            self.logger.error(f"[{file_name}][{self.class_name}][read_contest_data] 读取失败: {e}")
            return []


    def save_contest_data(self, data: list[dict], encoding='utf-8', index=False):
        try:
            # 如果是空数据，则设置默认列名
            if not data:
                self.logger.warning(f"[{file_name}][{self.class_name}] 保存空数据，使用默认列名")
                columns = ["title", "time", "duration", "start_time", "platform", "link"]
                df = pd.DataFrame(columns=columns)
            else:
                df = pd.DataFrame(data)

            # 确保目录存在
            Path(self.contest_path.parent).mkdir(parents=True, exist_ok=True)

            # 保存 CSV
            df.to_csv(self.contest_path, encoding=encoding, index=index)
            self.logger.info(f"[{file_name}][{self.class_name}] CSV保存成功：{self.contest_path}")
        except Exception as e:
            self.logger.error(f"[{file_name}][{self.class_name}][save_contest_data] 保存失败: {e}")
