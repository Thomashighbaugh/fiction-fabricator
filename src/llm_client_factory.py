# -*- coding: utf-8 -*-
"""
llm_client_factory.py - Factory for creating LLM client instances based on user selection.
"""
from typing import Optional

from rich.console import Console

from src.llm_client_interface import LLMClientInterface
from src.llm_client import LLMClient
from src.openai_client import OpenAIClient
from src.anthropic_client import AnthropicClient
from src.ollama_client import OllamaClient


class LLMClientFactory:
    """Factory class for creating LLM client instances."""

    @staticmethod
    def create_client(provider: str, console: Console) -> Optional[LLMClientInterface]:
        """
        Create an LLM client instance based on the specified provider.
        
        Args:
            provider: The LLM provider name ("gemini", "openai", "anthropic", "ollama")
            console: Rich console for output
            
        Returns:
            An LLMClientInterface instance, or None if creation failed
        """
        provider = provider.lower()
        
        try:
            if provider == "gemini":
                return LLMClient(console)
            elif provider == "openai":
                return OpenAIClient(console)
            elif provider == "anthropic":
                return AnthropicClient(console)
            elif provider == "ollama":
                return OllamaClient(console)
            else:
                console.print(f"[red]Unknown LLM provider: {provider}[/red]")
                console.print("[yellow]Available providers: gemini, openai, anthropic, ollama[/yellow]")
                return None
        except Exception as e:
            console.print(f"[bold red]Failed to create {provider} client: {e}[/bold red]")
            return None

    @staticmethod
    def get_available_providers() -> list[str]:
        """Return a list of available LLM providers."""
        return ["gemini", "openai", "anthropic", "ollama"]

    @staticmethod
    def get_provider_display_names() -> dict[str, str]:
        """Return a mapping of provider keys to display names."""
        return {
            "gemini": "Google Gemini",
            "openai": "OpenAI",
            "anthropic": "Anthropic Claude",
            "ollama": "Ollama (Local)"
        }

    @staticmethod
    def get_provider_description(provider: str) -> str:
        """Get a description for the specified provider."""
        descriptions = {
            "gemini": "Google's Gemini API (default)",
            "openai": "OpenAI GPT models",
            "anthropic": "Anthropic Claude models",
            "ollama": "Local Ollama models (free, requires Ollama installation)"
        }
        return descriptions.get(provider.lower(), "Unknown provider")

    @staticmethod
    def validate_provider(provider: str) -> bool:
        """Check if a provider is valid."""
        return provider.lower() in LLMClientFactory.get_available_providers()