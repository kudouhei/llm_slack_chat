"""
LLM client package

This package provides communication functionality with various LLM providers (Ollama, Gemini, etc.)
and tool integration functionality.
"""

from .ollama_client import OllamaClient
from .manager import LLMClientManager

__all__ = ["OllamaClient", "LLMClientManager"]
