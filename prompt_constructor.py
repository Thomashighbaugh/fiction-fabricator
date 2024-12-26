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
