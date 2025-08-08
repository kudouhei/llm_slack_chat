import logging
import logging.handlers

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config import LogConfig

def setup_logging(config: "LogConfig") -> logging.Logger:
    """Setup logging configuration"""

    logger = logging.getLogger("llm_slack_chat")

    log_level = getattr(logging, config.level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Clear existing handlers
    logger.handlers.clear()

    # Create the formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)

    # create file handler
    file_handler = logging.handlers.RotatingFileHandler(
        config.file_path,
        maxBytes=config.max_size * 1024 * 1024,  # MB to bytes
        backupCount=config.backup_count,
        encoding="utf-8",
    )

    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    logger.addHandler(file_handler)

    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name"""
    return logging.getLogger(f"llm_slack_chat.{name}")
