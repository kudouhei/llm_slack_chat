import asyncio
from .config import Config
from .slack_handler import SlackHandler
from .session_manager import SessionManager
from .llm_client import LLMClientManager
from .logger_config import get_logger

class ChatBot:
    """Main processing class for the chat bot"""

    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger("chat_bot")
        self.logger.info("Chat bot initialization started")

        self.slack_handler = SlackHandler(bot_token=config.slack.bot_token, app_token=config.slack.app_token)

        self.llm_manager = LLMClientManager(
            ollama_config=config.ollama,
        )

        self.session_manager = SessionManager(config.database)

        # Set callbacks for the Slack handler
        self.slack_handler.set_mention_callback(self._handle_mention)
        self.slack_handler.set_message_callback(self._handle_message)

        self.logger.info("Chat bot initialization completed")

    def _handle_mention(self, event, say):
        """Handle mention events"""
        try:
            text = event["text"]
            thread_ts = self.slack_handler.get_thread_id(event)
            user = event["user"]

            self.logger.info(f"Mention received - user: {user}, thread: {thread_ts}")

            self.logger.info(f"Received message: {text}")

            # Parse command, message, system prompt, model name
            command, user_message, system_prompt, model_name = (
                self.slack_handler.parse_command_and_message(text)
            )

            self.logger.info(
                f"Command parsing result - command: {command}, message length: {len(user_message)}, system prompt presence: {system_prompt is not None}, model name presence: {model_name is not None}"
            )

            # Execute common processing
            self._process_user_input(
                command=command,
                user_message=user_message,
                system_prompt=system_prompt,
                model_name=model_name,
                thread_ts=thread_ts,
                user=user,
                say=say,
                context="mention",
            )

        except Exception as e:
            error_msg = f"Error occurred during mention processing: {str(e)}"
            self.logger.exception(error_msg)
            try:
                say(
                    "Sorry, an error occurred during processing.",
                    thread_ts=thread_ts,
                )
            except:
                self.logger.error("Failed to send error message to Slack")

    def _handle_message(self, event, say):
        """Message processing in a thread (no mention)"""
        try:
            # Ignore messages from the bot itself
            if event.get("bot_id") or event.get("subtype"):
                return

            # Check if the message is in a thread
            if "thread_ts" not in event:
                return

            thread_ts = event["thread_ts"]
            user = event["user"]
            text = event.get("text", "")

            # Check if the bot is participating in the conversation in this thread
            if not self.session_manager.has_thread_history(thread_ts):
                self.logger.debug(f"No history, ignoring - thread: {thread_ts}")
                return

            self.logger.info(
                f"Thread message received - user: {user}, thread: {thread_ts}"
            )
            self.logger.info(f"Received message: {text}")

            # If the message is empty, skip
            if not text.strip():
                self.logger.debug(f"Empty message, ignoring - thread: {thread_ts}")
                return

            # Parse command, message, system prompt, model name
            command, user_message, system_prompt, model_name = (
                self._parse_thread_message(text)
            )

            # Execute common processing
            self._process_user_input(
                command=command,
                user_message=user_message,
                system_prompt=system_prompt,
                model_name=model_name,
                thread_ts=thread_ts,
                user=user,
                say=say,
                context="thread",
            )

        except Exception as e:
            error_msg = f"Error occurred during thread message processing: {str(e)}"
            self.logger.exception(error_msg)
            try:
                say(
                    "Sorry, an error occurred during processing.",
                    thread_ts=thread_ts,
                )
            except:
                self.logger.error("Failed to send error message to Slack")

    def _process_user_input(
        self,
        command: str,
        user_message: str,
        system_prompt: str,
        model_name: str,
        thread_ts: str,
        user: str,
        say,
        context: str,
    ):
        """Process user input"""
        try:
            self.logger.info(
                f"User input processing started - command: {command}, user: {user}, thread: {thread_ts}"
            )

            # Try to execute the command
            if self._execute_command(command, thread_ts, say, context):
                return

            # If the user message is empty, return an error
            if not user_message.strip():
                error_response = "Message is empty. Do you have anything to ask?"
                say(error_response, thread_ts=thread_ts)
                self.logger.warning(f"Received empty message - thread: {thread_ts}")
                return

            # Add the user message to the history
            self.session_manager.add_message(thread_ts, "user", user_message)

            # Get the conversation history
            history = self.session_manager.get_history(thread_ts)
            self.logger.debug(f"Conversation history retrieved - history count: {len(history)}")

            # Query the LLM
            response = self._query_llm(
                command, user_message, history, system_prompt, model_name, context
            )

            # Fallback processing if the response is empty
            if not response or not response.strip():
                response = "Sorry, I couldn't get a response from the LLM. Please try again."
                self.logger.warning(
                    f"Received empty response from LLM - thread: {thread_ts}, command: {command}"
                )

            # Add the assistant's response to the history
            self.session_manager.add_message(thread_ts, "assistant", response)

            # Record the content of the sent message (for debugging)
            response_preview = (
                response[:200] + "..." if len(response) > 200 else response
            )
            self.logger.info(f"Slack sent message: {response_preview}")

            # Send the response to Slack
            say(response, thread_ts=thread_ts)
            self.logger.info(f"Slack response sent - thread: {thread_ts}")

        except Exception as e:
            error_response = f"An error occurred: {str(e)}"
            say(error_response, thread_ts=thread_ts)
            self.logger.error(
                f"User input processing error - thread: {thread_ts}, error: {str(e)}",
                exc_info=True,
            )
    
    def _execute_command(self, command: str, thread_ts: str, say, context: str) -> bool:
        """Execute the command. Return True if the command is processed"""
        # Clear history functionality
        if command == "clear":
            self.session_manager.clear_thread_history(thread_ts)
            response = "The conversation history in this thread has been cleared."
            if response and response.strip():
                say(response, thread_ts=thread_ts)
            self.logger.info(f"History cleared - thread: {thread_ts}")
            return True

        # Help display
        if command == "help":
            response = self._get_help_message()
            if response and response.strip():
                say(response, thread_ts=thread_ts)
            self.logger.info(f"Help displayed - thread: {thread_ts}")
            return True

        return False

    def _query_llm(
        self,
        command: str,
        user_message: str,
        history: list,
        system_prompt: str,
        model_name: str,
        context: str,
    ) -> str:
        """Query the LLM"""

        provider_info = f"Provider: ollama"
        if context == "thread":
            provider_info += " (thread)"
        self.logger.info(f"LLM query started - {provider_info}")
        response = self.llm_manager.ask(
            "ollama", history, system_prompt, model_name
        )
        self.logger.info(f"LLM response received - response length: {len(response)}")

        # Check if the response is empty
        if not response or not response.strip():
            response = (
                "Sorry, I couldn't get a response from Ollama."
            )
            self.logger.warning(f"Received empty response from Ollama")

        return response

    def _parse_thread_message(self, text: str) -> tuple[str, str, str, str]:
        """Parse command, message, system prompt, model name from thread message"""
        import re

        clean_text = text.strip()

        # Extract the system prompt
        system_prompt = None
        system_pattern = r'system:"([^"]*)"'
        system_match = re.search(system_pattern, clean_text)
        if system_match:
            system_prompt = system_match.group(1)
            # Remove the system prompt part
            clean_text = re.sub(system_pattern, "", clean_text).strip()

        # Extract the model name
        model_name = None
        model_pattern = r'model:"([^"]*)"'
        model_match = re.search(model_pattern, clean_text)
        if model_match:
            model_name = model_match.group(1)
            # Remove the model name part
            clean_text = re.sub(model_pattern, "", clean_text).strip()

        # Check the command
        if clean_text.startswith("/ollama"):
            command = "ollama"
            user_message = clean_text[7:].strip()
        elif clean_text.startswith("/clear"):
            command = "clear"
            user_message = ""
        elif clean_text.startswith("/help"):
            command = "help"
            user_message = ""
        else:
            # Default is Ollama
            command = "ollama"
            user_message = clean_text

        return command, user_message, system_prompt, model_name

    def _get_help_message(self) -> str:
        """Return the help message"""
        return """**Slack LLM Chat Bot Help**

**Basic Usage:**
- `@bot Hello` - Chat with the default (Ollama)
- `@bot /ollama Hello` - Chat with Ollama

**Continuation of conversation in a thread:**
- In a thread, you can continue the conversation without `@bot`
- Example: `What can you do?`

**Commands:**
- `/clear` - Clear the conversation history
- `/help` - Display this help

**Advanced features:**
- `system:"custom prompt"` - Custom system prompt   
- `model:"model name"` - Custom model specification

**Examples:**
```
@bot system:"speak in French" hello
@bot model:"llama3" write a poem
```
"""

    def start(self):
        """Start the chat bot"""
        self.logger.info("Chat bot starting")

        # Output configuration information
        self.logger.info(
            f"Ollama settings: {self.config.ollama.base_url} ({self.config.ollama.model})"
        )
        self.logger.info(f"Database settings: {self.config.database.db_path}")

        # Start the Slack handler
        self.slack_handler.start()

    def stop(self):
        """Stop the chat bot"""
        self.logger.info("Chat bot stopping")

        # Close the LLM client
        asyncio.run(self.llm_manager.close())

        # Stop the Slack handler
        self.slack_handler.stop()

        self.logger.info("Chat bot stopped")
