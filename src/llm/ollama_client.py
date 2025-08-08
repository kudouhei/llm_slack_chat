from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from ..utils import ErrorHandler, LoggingMixin, APIUtils
from ..config import OllamaConfig

@dataclass
class ChatMessage:
    """Chat message data class"""
    role: str
    content: str

class OllamaClient(LoggingMixin):
    """Ollama client class"""
    def __init__(self, config: OllamaConfig):
        super().__init__("ollama_client")
        self.log_initialization_start("OllamaClient", base_url=config.base_url)

        self.config = config
        self.base_url = config.base_url
        self.model = config.model
        self.timeout = config.timeout

        self.log_initialization_end("OllamaClient")
        
    @ErrorHandler.handle_sync("ollama_client", "chat processing", fallback_value="")
    def ask(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> str:
        """Ask a question to the LLM"""
        original_model = self.model
        if model_name:
            self.set_model(model_name)

        try:
            processed_messages = messages.copy()
            if system_prompt:
                # Add the system message to the beginning
                system_message = {"role": "system", "content": system_prompt}
                processed_messages.insert(0, system_message)

            # convert messages to the expected format
            chat_messages = [ChatMessage(role=msg["role"], content=msg["content"]) for msg in processed_messages]

            result = self.chat(chat_messages)

            if model_name:
                self.set_model(original_model)

            return result
        
        except Exception as e:
            if model_name:
                self.set_model(original_model)
            raise

    @ErrorHandler.handle_sync("ollama_client", "chat processing", fallback_value="")
    def chat(self, messages: List[ChatMessage], stream: bool = False) -> str:
        """Chat with the LLM"""
        self.log_operation_start("Ollama chat", model=self.model, message_count=len(messages))

        payload = self._create_chat_payload(messages, stream)
        headers = APIUtils.create_request_headers()

        self.log_api_request("Ollama", model=self.model, stream=stream)

        try:
            response = APIUtils.make_api_request(
                method="POST",
                url=f"{self.base_url}/api/chat",
                payload=payload,
                headers=headers,
                timeout=self.timeout,
                logger_name="ollama_client",
            )

            self.log_api_response("Ollama", response.status_code)

            result = APIUtils.handle_api_response(response, logger_name="ollama_client")

            if isinstance(result, dict) and "message" in result:
                content = result["message"].get("content", "")

                self.log_api_success("Ollama", response_length=len(content))
                self.log_operation_end(
                    "Ollama chat", response_length=len(content)
                )
                return content
            else:
                self.log_warning("Unexpected Ollama response format")
                return str(result)
            
        except Exception as e:
            return APIUtils.format_user_friendly_error(e, "Ollama")
        
    def _create_chat_payload(
        self, messages: List[ChatMessage], stream: bool
    ) -> Dict[str, Any]:
        """Create a chat request payload"""
        return {
            "model": self.model,
            "messages": [
                {"role": msg.role, "content": msg.content} for msg in messages
            ],
            "stream": stream,
        }
    
    def get_model(self) -> str:
        """Get the current model name"""
        return self.model

    def set_model(self, model: str) -> None:
        """Change the model"""
        self.log_debug(f"Model changed: {self.model} -> {model}")
        self.model = model
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert a message list to a prompt string (for test compatibility)"""
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
            elif role == "system":
                prompt_parts.append(f"System: {content}")
        return "\n".join(prompt_parts)