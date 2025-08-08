import os
from dataclasses import dataclass
from dotenv import load_dotenv
from typing import List, Optional

from .utils import Validator, LoggingMixin

load_dotenv()

@dataclass
class SlackConfig:
    """Slack configuration"""
    bot_token: str
    app_token: str

    def __post_init__(self):
        """Post-initialization validation"""
        Validator.validate_token_format(self.bot_token, "slack_bot_token", expected_prefix="xoxb-")
        Validator.validate_token_format(self.app_token, "slack_app_token", expected_prefix="xapp-")
    

@dataclass
class OllamaConfig:
    """Ollama configuration"""
    model: str
    base_url: str
    timeout: int

    def __post_init__(self):
        """Post-initialization validation"""
        Validator.validate_url(self.base_url, "ollama_base_url")
        Validator.require_non_empty(self.model, "ollama_model")
        self.timeout = Validator.validate_positive_integer(
            self.timeout, "ollama_timeout", min_value=1, max_value=300
        )

@dataclass
class DatabaseConfig:
    """Database related configuration"""
    db_path: str = "chat_sessions.db" 

@dataclass
class LogConfig:
    """Log configuration"""
    level: str = "INFO"
    file_path: str = "logs/llm_slack_chat.log"
    max_size: int = 10  # MB
    backup_count: int = 3


class Config(LoggingMixin):
    def __init__(self):
        super().__init__("config")
        self.log_initialization_start("Config")

        # load config from environment variables
        self.slack = self._load_slack_config()
        self.ollama = self._load_ollama_config()

        self.database = DatabaseConfig(
            db_path=os.environ.get("DATABASE_PATH", "chat_sessions.db")
        )

        self.log = LogConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            file_path=os.getenv("LOG_FILE_PATH", "logs/llm_slack_chat.log"),
            max_size=int(os.getenv("LOG_MAX_SIZE", 10)),
            backup_count=int(os.getenv("LOG_BACKUP_COUNT", 3)),
        )

        self.log_initialization_end("Config")

    def _load_slack_config(self) -> SlackConfig:
        """Load Slack configuration"""
        self.log_debug("Loading Slack configuration")

        bot_token = os.getenv("SLACK_BOT_TOKEN", "")
        app_token = os.getenv("SLACK_APP_TOKEN", "")

        Validator.validate_batch(
            [{
                    "method": Validator.require_non_empty,
                    "args": [bot_token, "SLACK_BOT_TOKEN"],
                },
                {
                    "method": Validator.require_non_empty,
                    "args": [app_token, "SLACK_APP_TOKEN"],
                },])
        
        self.log_debug("Slack configuration loaded successfully")
        return SlackConfig(bot_token=bot_token, app_token=app_token)
    
    def _load_ollama_config(self) -> OllamaConfig:
        """Load Ollama configuration"""
        self.log_debug("Loading Ollama configuration")

        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "llama3")
        timeout = int(os.getenv("OLLAMA_TIMEOUT", "30"))

        self.log_debug("Ollama configuration loaded")

        return OllamaConfig(base_url=base_url, model=model, timeout=timeout)
    
    def validate(self):
        """Validate configuration values"""
        if not self.slack.bot_token:
            raise ValueError("SLACK_BOT_TOKEN is required")

        if not self.slack.app_token:
            raise ValueError("SLACK_APP_TOKEN is required")

        if not self.ollama.base_url:
            raise ValueError("OLLAMA_BASE_URL is required")

        return True