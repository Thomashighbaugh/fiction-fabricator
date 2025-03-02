# /home/tlh/refactored_gui_fict_fab/llm/llm_client.py
import json
from typing import Optional

import aiohttp

from utils.config import config
from utils.logger import logger
from openai import AsyncOpenAI  # Import OpenAI


class OpenAILLMClient:
    """
    Client for interacting with a local OpenAI compatible instance using aiohttp.
    """

    def __init__(self, base_url: str = None):
        """
        Initializes the OpenAI client.
        """
        self.base_url = base_url or config.get_openai_base_url()
        self.client = AsyncOpenAI(
            base_url=self.base_url, api_key="placeholder"
        )  # Initialize OpenAI client
        logger.debug(
            "OpenAILLMClient initialized with base_url: %s", self.base_url
        )  # Lazy formatting

    async def list_models(self) -> Optional[list[str]]:
        """OpenAI does not support listing models via localhost."""
        return None

    async def generate_text(self, model_name: str, prompt: str) -> Optional[str]:
        """
        Asynchronously generates text using the OpenAI API.
        """
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
                logger.info(
                    "Text generated successfully using model '%s'", model_name
                )  # Lazy formatting
                return generated_text
            else:
                logger.error("No response from OpenAI API")
                return None

        except Exception as e:  # General exception to handle OpenAI and other errors
            logger.error("OpenAI text generation failed: %s", e)  # Lazy formatting
            return None