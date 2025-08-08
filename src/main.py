#!/usr/bin/env python3
"""
LLM Slack Chat Bot - Main entry
"""

from .config import Config
from .chat_bot import ChatBot
from .logger_config import setup_logging, get_logger


def main():
    """Main function"""
    config = None
    logger = None

    try:
        # Load configuration
        config = Config()
        config.validate()

        # Initialize log settings
        setup_logging(config.log)
        logger = get_logger("main")

        logger.info("=== Slack LLM Chat Bot startup ===")
        logger.info(f"Log level: {config.log.level}")
        logger.info(f"Log file: {config.log.file_path}")

        # Initialize and start the chatbot
        bot = ChatBot(config)
        bot.start()

    except ValueError as e:
        error_msg = f"Configuration error: {e}"
        if logger:
            logger.error(error_msg)
        else:
            print(error_msg)
        print("Please set the necessary environment variables.")

    except KeyboardInterrupt:
        shutdown_msg = "Chatbot stopped."
        if logger:
            logger.info("=== Slack LLM Chat Bot shutdown ===")
            logger.info("Shutdown by user (Ctrl+C)")
        print(f"\n{shutdown_msg}")
        
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        if logger:
            logger.exception(error_msg)
        else:
            print(error_msg)


if __name__ == "__main__":
    main()
