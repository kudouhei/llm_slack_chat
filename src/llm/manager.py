"""
Implementation of LLM client manager

This class manages multiple LLM providers (Ollama, Gemini) and provides
integration with MCP tools.
"""

import asyncio
from typing import List, Dict, Optional, Any, Union

from ..utils import LoggingMixin
from ..config import OllamaConfig
from ..logger_config import get_logger
from .ollama_client import OllamaClient


class LLMClientManager(LoggingMixin):
    """Class for managing multiple LLM clients"""

    def __init__(
        self,
        ollama_config: OllamaConfig,
    ):
        """Initialize LLM client manager

        Args:
            ollama_config: Ollama configuration
        """
        super().__init__("llm_manager")
        self.log_initialization_start("LLMClientManager")

        self.ollama_client = OllamaClient(ollama_config)

        self.log_initialization_end("LLMClientManager")


    def ask(
        self,
        provider: str,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> str:
        """Send a question to the specified provider"""
        self.log_debug(
            f"LLM question - provider: {provider}, message count: {len(messages)}"
        )

        if system_prompt:
            self.log_debug(f"Custom system prompt used: {system_prompt[:50]}...")

        if model_name:
            self.log_debug(f"Custom model used: {model_name}")

        try:
            if provider == "ollama":
                return self.ollama_client.ask(messages, system_prompt, model_name)
            else:
                error_msg = f"Unknown provider: {provider}"
                self.log_error(error_msg)
                return f"Unknown provider: {provider}"
        except Exception as e:
            error_msg = (
                f"Error during LLM question - provider: {provider}, error: {str(e)}"
            )
            self.log_error(error_msg, e)
            return f"Error during LLM processing: {str(e)}"

    def list_models(self) -> str:
        """Get a list of available models with Ollama"""
        self.log_debug("LLM model list retrieval")

        try:
            return self.ollama_client.list_models()
        except Exception as e:
            error_msg = f"Error during model list retrieval: {str(e)}"
            self.log_error(error_msg, e)
            return f"Error during model list retrieval: {str(e)}"

    async def close(self):
        """Clean up resources"""    
        pass
