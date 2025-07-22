import os
import sys
import json
from pathlib import Path


class GetAllPath:
    
    def __init__(self) -> None:
        self.base_path = self.get_base_path()
        pass
    
    
    def get_base_path(self):
        return Path.home() / "oj_contest_time"
    
    def get_settings_path(self):
        config_path = self.base_path / "configs"/ "settings.json"
        return config_path
    
    def get_logs_path(self):
        logs_path = self.base_path / "logs"
        return logs_path