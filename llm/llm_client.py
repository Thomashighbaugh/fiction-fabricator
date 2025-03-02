# llm/llm_client.py

from typing import Optional


import requests  # Import the requests library

from utils.config import config
from utils.logger import logger
from openai import (
    AsyncOpenAI,
    types,
    APIError,
    APIConnectionError,
    RateLimitError,
)  # Import error types


class OpenAILLMClient:
    """
    Client for interacting with a local OpenAI compatible instance.
    """

    def __init__(self, base_url: str = None):
        """
        Initializes the OpenAI client.
        """
        self.base_url = base_url or config.get_openai_base_url()
        self.client = AsyncOpenAI(
            base_url=self.base_url, api_key="placeholder"
        )  # Initialize OpenAI client
        logger.debug("OpenAILLMClient initialized with base_url: %s", self.base_url)

    async def list_models(self) -> Optional[list[str]]:
        """
        Asynchronously fetches the list of available models from the OpenAI API.
        Falls back to requests if openai library fails.
        """
        try:
            response = await self.client.models.list()
            model_names = [
                model.id for model in response.data if isinstance(model, types.Model)
            ]  # Use types.Model
            logger.info(
                "Successfully fetched models using openai library: {model_names}"
            )
            return model_names
        except (APIError, APIConnectionError, RateLimitError) as openai_err:
            logger.warning(
                f"Error fetching models using openai library: {openai_err}. Trying requests fallback."
            )
            try:
                url = f"{self.base_url}/models"  # Standard models endpoint
                response = requests.get(url, timeout=0)
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                data = response.json()
                # Adjust key based on typical API responses; 'data' or 'models' are common
                models_data = data.get("data") or data.get("models", [])
                model_names = [
                    model["id"]
                    for model in models_data
                    if isinstance(model, dict) and "id" in model
                ]
                logger.info("Successfully fetched models using requests: {model_names}")
                return model_names
            except requests.RequestException as requests_err:
                logger.error(
                    "Error fetching models using requests fallback: {requests_err}"
                )
                return None

    async def generate_text(self, model_name: str, prompt: str) -> Optional[str]:
        """
        Asynchronously generates text using the OpenAI API.
        """
        logger.debug(
            f"Attempting to generate text with model: {model_name} to URL: {self.base_url}"
        )  # Log model and URL

        try:
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=800,
            )
            generated_text = response.choices[0].message.content

            if generated_text:
                logger.info(f"Text generated successfully using model '{model_name}'")
                return generated_text
            else:
                logger.error(
                    "No response from OpenAI API - empty content"
                )  # More specific error message for empty response
                return None

        except APIError as e:
            logger.error(f"OpenAI APIError: {e}")
            logger.error(
                f"Status code: {e.status_code}, Response: {e.response}"
            )  # Include status and response
            logger.exception(e)  # Log full exception including traceback
            return None
        except APIConnectionError as e:
            logger.error(f"OpenAI APIConnectionError: {e}")
            logger.exception(e)  # Log full exception including traceback
            return None
        except RateLimitError as e:
            logger.error(f"OpenAI RateLimitError: {e}")
            logger.exception(e)  # Log full exception including traceback
            return None
        except Exception as e:  # Catch-all for any other exceptions
            logger.error(f"General error during OpenAI text generation: {e}")
            logger.exception(e)  # Log full exception including traceback
            return None
