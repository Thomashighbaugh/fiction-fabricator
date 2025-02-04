# fiction_fabricator/src/llm/llm_client.py
import json
import requests

from  utils.config import config
from utils.logger import logger


class OllamaClient:
    """
    Client for interacting with a local Ollama instance.

    Handles communication with the Ollama API for model listing and text generation.
    """

    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Initializes the Ollama client.

        Args:
            base_url (str): The base URL of the Ollama API. Defaults to "http://localhost:11434".
        """
        self.base_url = base_url.rstrip("/")  # Remove trailing slash if present

    def list_models(self) -> list[str] | None:
        """
        Fetches the list of available models from the Ollama instance.

        Returns:
            list[str] | None: A list of model names if successful, None otherwise.
        """
        url = f"{self.base_url}/api/tags"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            models_data = response.json()
            model_names = [model["name"] for model in models_data["models"]]
            logger.info(f"Successfully fetched models: {model_names}")
            return model_names
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching model list from Ollama: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON response when listing models: {e}")
            return None

    def generate_text(self, model_name: str, prompt: str) -> str | None:
        """
        Generates text using the specified Ollama model and prompt.

        Args:
            model_name (str): The name of the Ollama model to use.
            prompt (str): The prompt for text generation.

        Returns:
            str | None: The generated text if successful, None otherwise.
        """
        url = f"{self.base_url}/api/chat"
        data = {"model": model_name, "prompt": prompt, "stream": False}  # stream: False for single response
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            response_json = response.json()
            generated_text = response_json.get("response")
            if generated_text:
                logger.info(f"Text generated successfully using model '{model_name}'")
                return generated_text
            else:
                logger.error(f"No 'response' field found in Ollama API response: {response_json}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error generating text with Ollama: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON response when generating text: {e}")
            return None