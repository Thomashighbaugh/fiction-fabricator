# llm/llm_client.py
import json 
from typing import Optional  

import aiohttp  

from utils.config import config  
from utils.logger import logger


class OllamaClient:
    """
    Client for interacting with a local Ollama instance using aiohttp.
    """

    def __init__(self, base_url: str = None):
        """
        Initializes the Ollama client.
        """
        self.base_url = base_url or config.get_ollama_base_url()
        logger.debug(
            "OllamaClient initialized with base_url: %s", self.base_url
        )  # Lazy formatting

    async def list_models(self) -> Optional[list[str]]:
        """
        Asynchronously fetches the list of available models from the Ollama API.
        """
        url = f"{self.base_url}/api/tags"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()
                    model_names = [model["name"] for model in data.get("models", [])]
                    logger.info(
                        "Successfully fetched models: %s", model_names
                    )  # Lazy formatting
                    return model_names
        except aiohttp.ClientError as e:  # Catch specific aiohttp ClientError
            logger.error(
                "Error fetching model list from Ollama: %s", e
            )  # Lazy formatting
            return None
        except json.JSONDecodeError as e:  # Catch specific json.JSONDecodeError
            logger.error(
                "Error decoding JSON response from Ollama: %s", e
            )  # Lazy formatting
            return None
        except (
            ValueError,
            TypeError,
            RuntimeError,
        ) as e:  # Catch data processing errors
            logger.error("Error processing model list data: %s", e)  # Lazy formatting
            logger.exception(e)  # Log full exception details
            return None

    async def generate_text(self, model_name: str, prompt: str) -> Optional[str]:
        """
        Asynchronously generates text using the Ollama API.
        """
        url = f"{self.base_url}/api/generate"
        headers = {"Content-Type": "application/json"}
        data = {"model": model_name, "prompt": prompt, "stream": False}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, headers=headers, data=json.dumps(data)
                ) as response:
                    response.raise_for_status()
                    response_data = await response.json()
                    generated_text = response_data.get("response")

                    if generated_text:
                        logger.info(
                            "Text generated successfully using model '%s'",
                            model_name,  # Lazy formatting
                        )
                        return generated_text
                    else:
                        logger.error(
                            "No 'response' field found in Ollama response: %s",
                            response_data,  # Lazy formatting
                        )
                        return None

        except aiohttp.ClientError as e:  # Catch specific aiohttp ClientError
            logger.error("Ollama text generation failed: %s", e)  # Lazy formatting
            return None
        except json.JSONDecodeError as e:  # Catch specific json.JSONDecodeError
            logger.error(
                "Error decoding JSON response from Ollama: %s", e
            )  # Lazy formatting
            return None
        except (
            ValueError,
            TypeError,
            RuntimeError,
        ) as e:  # Catch data processing errors
            logger.error(
                "Error processing text response data: %s", e
            )  # Lazy formatting
            logger.exception(e)  # Log full exception details
            return None
