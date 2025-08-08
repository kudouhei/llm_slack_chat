import re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from typing import Callable, Tuple, Optional
from .logger_config import get_logger


class SlackHandler:
    """Class responsible for Slack-related processing"""

    def __init__(self, bot_token: str, app_token: str):
        self.logger = get_logger("slack_handler")
        self.logger.info("Slack handler initialization started")

        self.app = App(token=bot_token)
        self.app_token = app_token
        self._setup_handlers()

        self.logger.info("Slack handler initialization completed")
    
    def _setup_handlers(self):
        """Set up event handlers"""
        self.logger.info("Slack event handler setup started")

        @self.app.event("app_mention")
        def handle_mention(event, say):
            if hasattr(self, "_mention_callback"):
                self._mention_callback(event, say)

        @self.app.event("message")
        def handle_message(event, say):
            if hasattr(self, "_message_callback"):
                self._message_callback(event, say)

        self.logger.info("Slack event handler setup completed")
    
    def set_mention_callback(self, callback: Callable):
        """Set the mention processing callback"""
        self.logger.info("Mention callback setting")
        self._mention_callback = callback

    def set_message_callback(self, callback: Callable):
        """Set the message processing callback"""
        self.logger.info("Message callback setting")
        self._message_callback = callback

    @staticmethod
    def clean_mention_text(text: str) -> str:
        """Remove the mention part and get the clean text"""
        logger = get_logger("slack_handler.util")
        original_length = len(text)
        clean_text = re.sub(r"<@[A-Z0-9]+>", "", text).strip()
        logger.debug(
            f"Mention text cleaning - Original length: {original_length}, Cleaned length: {len(clean_text)}"
        )
        return clean_text

    @staticmethod
    def parse_command_and_message(
        text: str,
    ) -> Tuple[str, str, Optional[str], Optional[str]]:
        """Parse command, message, system prompt, and model name"""
        logger = get_logger("slack_handler.util")
        clean_text = SlackHandler.clean_mention_text(text)

        # Extract system prompt
        system_prompt = None
        system_pattern = r'system:"([^"]*)"'
        system_match = re.search(system_pattern, clean_text)
        if system_match:
            system_prompt = system_match.group(1)
            # Remove system prompt part
            clean_text = re.sub(system_pattern, "", clean_text).strip()
            logger.debug(f"System prompt extraction: {system_prompt}")

        # Extract model name
        model_name = None
        model_pattern = r'model:"([^"]*)"'
        model_match = re.search(model_pattern, clean_text)
        if model_match:
            model_name = model_match.group(1)
            # Remove model name part
            clean_text = re.sub(model_pattern, "", clean_text).strip()
            logger.debug(f"Model name extraction: {model_name}")

        # Parse command (check longer commands first)
        if clean_text.startswith("/ollama"):
            command, message = "ollama", clean_text[len("/ollama") :].strip()
        elif clean_text.startswith("/clear"):
            command, message = "clear", ""
        elif clean_text.startswith("/help"):
            command, message = "help", ""
        else:
            command, message = "ollama", clean_text

        logger.debug(
            f"Command parsing - Command: {command}, Message length: {len(message)}, System prompt presence: {system_prompt is not None}, Model name presence: {model_name is not None}"
        )
        return command, message, system_prompt, model_name

    @staticmethod
    def get_thread_id(event: dict) -> str:
        """Get thread ID (use message ts if no thread)"""
        logger = get_logger("slack_handler.util")
        thread_id = event.get("thread_ts") or event["ts"]
        logger.debug(f"Thread ID retrieval: {thread_id}")
        return thread_id

    def start(self):
        """Start Slack app (Socket Mode)"""
        self.logger.info("Slack Socket Mode startup started")
        try:
            handler = SocketModeHandler(self.app, self.app_token)
            self.logger.info("Socket Mode handler creation successful")
            handler.start()
        except Exception as e:
            self.logger.exception(f"Socket Mode startup failed: {str(e)}")
            raise
