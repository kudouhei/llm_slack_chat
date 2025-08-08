import os
from dataclasses import dataclass
from dotenv import load_dotenv
from typing import List, Optional


load_dotenv()

@dataclass
class LogConfig:
    """Log configuration"""
    level: str = "INFO"
    file_path: str = "logs/llm_slack_chat.log"
    max_size: int = 10  # MB
    backup_count: int = 3



class Config(LoggingMixin):
    def __init__(self):
        super().__init__()
        self.log_initialization_start("Config")



    