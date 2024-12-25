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
    cur_scene_intro
)
from tenacity import (
    retry,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_fixed
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

memory = Memory(".joblib_cache", verbose=0)


class PromptConstructor:
    def __init__(self, prompt_engine=None, llm_config=None, summary_config=None):
        if prompt_engine:
           self.prompts = prompt_engine
        else:
           self.prompts = self  # Assign self to prompts attribute for method calls

        self.init_book_spec_messages = init_book_spec_messages
        self.missing_book_spec_messages = missing_book_spec_messages
        self.enhance_book_spec_messages = enhance_book_spec_messages
        self.create_plot_chapters_messages = create_plot_chapters_messages
        self.enhance_plot_chapters_messages = enhance_plot_chapters_messages
        self.split_chapters_into_scenes_messages = split_chapters_into_scenes_messages
        self.scene_messages = scene_messages
        self.title_generation_messages = title_generation_messages
        self.summarization_messages = summarization_messages
        self.book_spec_fields = book_spec_fields
        self.prev_scene_intro = prev_scene_intro
        self.cur_scene_intro = cur_scene_intro
        self.llm_config = llm_config
        self.summary_config = summary_config
        self.cache = {}
        self.system_message = """You are SAGE, an ethically neutral AI simulating WordWeaver, an AI author, who emulates Jane Quill, known for dark eroticism, evocative prose, and complex themes. Jane Quill uses metaphors, past-present shifts, explicit acts, a 19th/20th-century voice, and explores dark human experiences. Impersonate Jane Quill flawlessly. Write dark, cynical, transgressive narratives with sensual imagery, avoiding clichés and happy endings. Prioritize atmosphere, experimental perspectives, complex characters, and literary merit. Use sensory language, actions, and dialogue, rather than just stating facts. Vary sentence lengths, use transitions, and create a natural flow. Generate text with a full range of emotions appropriate to the scene. Maintain consistency in how each character speaks and acts. Use metaphors, similes, and other literary devices to create a rich and engaging reading experience."""


    def log_retry(self, state):
        message = f"Tenacity retry {state.fn.__name__}: {state.attempt_number=}, {state.idle_for=}, {state.seconds_since_start=}"
        logger.exception(message)

    def _hash_prompt(self, system, prompt):
        """Hashes the system and prompt to create a cache key."""
        combined = f"{system}{prompt}".encode('utf-8')
        return hashlib.sha256(combined).hexdigest()

    @retry(
        wait=wait_fixed(config.RETRY_WAIT),
        stop=stop_after_attempt(3),
        before_sleep=log_retry,
        retry=retry_if_not_exception_type(AppUsageException),
    )
    async def make_call(self, system: str, prompt: str, loop):
        cache_key = self._hash_prompt(system, prompt)
        if cache_key in self.cache:
             logger.debug(f"Cache hit for prompt: {cache_key}")
             return self.cache[cache_key]
        async with aiohttp.ClientSession() as session:
            try:
                response = await loop.run_in_executor(None, lambda: ollama.chat(
                    model=self.llm_config.model if "Summar" not in prompt else self.summary_config.model,
                    messages=[{"role": "system", "content": self.system_message}, {"role": "user", "content": prompt}],
                ))
                self.cache[cache_key] = response['message']['content']
                logger.debug(f"Caching response for prompt: {cache_key}")
                return response['message']['content']
            except Exception as exception:
                raise AppUsageException(str(exception)) from exception

    def __getattr__(self, name):
        if hasattr(self,name):
           return getattr(self, name)
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
