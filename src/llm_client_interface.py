"""
llm_client_interface.py - Abstract base class for LLM client implementations.
"""
from abc import ABC, abstractmethod


class LLMClientInterface(ABC):
    """Abstract base class for LLM client implementations."""

    @abstractmethod
    def get_response(
        self, prompt: str, task_description: str, allow_stream: bool = True
    ) -> str | None:
        """
        Get a response from the LLM (synchronous).

        Args:
            prompt: The input prompt for the LLM
            task_description: Description of the task for UI feedback
            allow_stream: Whether to allow streaming responses

        Returns:
            The LLM response as a string, or None if failed
        """
        pass

    @abstractmethod
    async def get_response_async(
        self, prompt: str, task_description: str, allow_stream: bool = True
    ) -> str | None:
        """
        Get a response from the LLM (asynchronous).

        Args:
            prompt: The input prompt for the LLM
            task_description: Description of the task for UI feedback
            allow_stream: Whether to allow streaming responses

        Returns:
            The LLM response as a string, or None if failed
        """
        pass

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the client.

        Returns:
            True if initialization succeeded, False otherwise
        """
        pass
