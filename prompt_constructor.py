# prompt_constructor.py
from prompts import (
    init_book_spec_messages,
    missing_book_spec_messages,
    enhance_book_spec_messages,
    create_plot_chapters_messages,
    enhance_plot_chapters_messages,
    split_chapters_into_scenes_messages,
    scene_messages,
    title_generation_messages,
    summarization_messages,
    book_spec_fields,
    prev_scene_intro,
    cur_scene_intro,
    create_chapters_messages,
)
from tenacity import (
    retry,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_fixed,
    wait_exponential,
    retry_if_exception_type,
)
from classes import AppUsageException
from joblib import Memory
import config
from loguru import logger
from datetime import datetime
from omegaconf import DictConfig
import ollama
import asyncio
import aiohttp
import hashlib
import json


class PromptConstructor:
    def __init__(self, prompt_engine=None, llm_config=None, summary_config=None):
        if prompt_engine:
            self.init_book_spec_messages = prompt_engine["init_book_spec_messages"]
            self.missing_book_spec_messages = prompt_engine[
                "missing_book_spec_messages"
            ]
            self.enhance_book_spec_messages = prompt_engine[
                "enhance_book_spec_messages"
            ]
            self.create_plot_chapters_messages = prompt_engine[
                "create_plot_chapters_messages"
            ]
            self.enhance_plot_chapters_messages = prompt_engine[
                "enhance_plot_chapters_messages"
            ]
            self.split_chapters_into_scenes_messages = prompt_engine[
                "split_chapters_into_scenes_messages"
            ]
            self.scene_messages = prompt_engine["scene_messages"]
            self.title_generation_messages = prompt_engine["title_generation_messages"]
            self.summarization_messages = prompt_engine["summarization_messages"]
            self.book_spec_fields = prompt_engine["book_spec_fields"]
            self.prev_scene_intro = prompt_engine["prev_scene_intro"]
            self.cur_scene_intro = prompt_engine["cur_scene_intro"]
            self.create_chapters_messages = prompt_engine["create_chapters_messages"]
        self.llm_config = llm_config
        self.summary_config = summary_config

    def generate_prompt_parts(self, messages):
        for message in messages:
            yield message["content"]

    @retry(
        wait=wait_exponential(
            multiplier=1, min=config.RETRY_WAIT, max=config.RETRY_WAIT * 4
        ),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(AppUsageException),
    )
    async def make_call(self, prompt, system_message):
        """Makes a call to the language model."""
        try:
            response = await self._query_ollama(
                prompt=prompt, system_message=system_message
            )
            return response
        except Exception as e:
            logger.error(f"Error during make_call: {e}")
            raise AppUsageException(f"Error during make_call: {e}") from e

    async def _query_ollama(self, prompt, system_message):
        """Queries the ollama model and returns the response."""
        try:
            async with aiohttp.ClientSession() as session:
                url = "http://localhost:11434/api/chat"
                payload = {
                    "model": (
                        self.llm_config.model if self.llm_config else config.MODEL_NAME
                    ),
                    "messages": [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt},
                    ],
                    "stream": False,
                }
                async with session.post(
                    url, json=payload, timeout=config.TIMEOUT
                ) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        logger.error(f"Ollama API Error: {resp.status}, {text}")
                        raise AppUsageException(
                            f"Ollama API Error: {resp.status}, {text}"
                        )

                    # Handle streaming and non-streaming responses
                    if resp.content_type == "application/x-ndjson":
                        all_content = ""
                        async for line in resp.content:
                            if line:
                                try:
                                    line = line.decode("utf-8").rstrip("\n")
                                    if not line:
                                        continue
                                    part = json.loads(line)
                                    all_content += part.get("message", {}).get(
                                        "content", ""
                                    )
                                except json.JSONDecodeError as e:
                                    logger.error(f"Error decoding JSON: {e}")
                        return all_content
                    elif resp.content_type == "application/json":
                        response_data = await resp.json()
                        if (
                            "message" in response_data
                            and "content" in response_data["message"]
                        ):
                            return response_data["message"]["content"]
                        else:
                            logger.error(f"Unexpected response format: {response_data}")
                            raise AppUsageException(
                                f"Unexpected response format: {response_data}"
                            )
                    else:
                        text = await resp.text()
                        logger.error(f"Unexpected content type: {resp.content_type}")
                        raise AppUsageException(
                            f"Unexpected content type: {resp.content_type}, {text}"
                        )

        except Exception as e:
            logger.error(f"Error during _query_ollama: {e}")
            raise AppUsageException(f"Error during _query_ollama: {e}") from e
