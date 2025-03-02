# llm/llm_client.py

import asyncio
import aiohttp
import json

from utils.config import config
from utils.logger import logger


class OllamaClient:
    """
    Client for interacting with a local Ollama instance using aiohttp.
    """

    def __init__(self, base_url: str = None, timeout: float = None):
        """
        Initializes the Ollama client.

        Args:
            base_url (str): The base URL of the Ollama API.
            timeout (float, optional): Timeout for requests in seconds.
                Defaults to None (no timeout).
        """
        self.base_url = base_url or config.get_ollama_base_url()
        self.timeout = timeout  # Store the timeout
        logger.debug(
            f"OllamaClient initialized with base_url: {self.base_url}, timeout: {self.timeout}"
        )

    async def list_models(self) -> list[str] | None:
        """
        Asynchronously fetches the list of available models.
        """
        url = f"{self.base_url}/api/tags"
        try:
            # Use self.timeout here
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()
                    model_names = [model["name"] for model in data["models"]]
                    logger.info(f"Successfully fetched models: {model_names}")
                    return model_names
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching model list from Ollama: {e}")
            return None

    async def generate_text(self, model_name: str, prompt: str) -> str | None:
        """
        Asynchronously generates text.
        """
        url = f"{self.base_url}/api/generate"
        headers = {"Content-Type": "application/json"}
        data = {"model": model_name, "prompt": prompt, "stream": False}

        try:
            # Use self.timeout here
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as session:
                async with session.post(
                    url, headers=headers, data=json.dumps(data)
                ) as response:
                    response.raise_for_status()
                    response_data = await response.json()
                    generated_text = response_data.get("response")

                    if generated_text:
                        logger.info(
                            f"Text generated successfully using model '{model_name}'"
                        )
                        return generated_text
                    else:
                        logger.error(
                            f"No 'response' field found in Ollama response: {response_data}"
                        )
                        return None

        except aiohttp.ClientError as e:
            logger.error(f"Ollama text generation failed: {e}")
            return None
