# llm/prompt_manager/prompt_manager.py
import os
from typing import Dict

from utils.logger import logger
from llm.prompt_manager import base_prompts
from llm.prompt_manager import book_spec_prompts
from llm.prompt_manager import plot_outline_prompts
from llm.prompt_manager import chapter_outline_prompts
from llm.prompt_manager import scene_outline_prompts
from llm.prompt_manager import scene_part_prompts


class PromptManager:
    def __init__(self):
        logger.debug("PromptManager.__init__ START")  # <-- ADDED LOGGING
        self.prompts: Dict[str, str] = {}
        self._load_prompts()
        logger.debug(
            "PromptManager.__init__ END - Prompts loaded."
        )  # <-- ADDED LOGGING

    def _load_prompts(self):
        # Load base prompts
        self.prompts.update(base_prompts.base_prompts)
        logger.debug(
            f"Loaded base prompts. Count: {len(base_prompts.base_prompts)}"
        )  # <-- ADDED LOGGING

        # Load prompts from other modules
        self.prompts.update(book_spec_prompts.book_spec_prompts)
        logger.debug(
            f"Loaded book_spec_prompts. Count: {len(book_spec_prompts.book_spec_prompts)}"
        )  # <-- ADDED LOGGING
        for (
            name,
            prompt,
        ) in book_spec_prompts.book_spec_prompts.items():  # <-- ADDED LOOP LOGGING
            logger.debug(
                f"  - BookSpec Prompt: {name[:30]:30} ... content preview: {prompt[:100]!r}"
            )  # <-- ADDED LOOP LOGGING

        self.prompts.update(plot_outline_prompts.plot_outline_prompts)
        logger.debug(
            f"Loaded plot_outline_prompts. Count: {len(plot_outline_prompts.plot_outline_prompts)}"
        )  # <-- ADDED LOGGING
        for (
            name,
            prompt,
        ) in (
            plot_outline_prompts.plot_outline_prompts.items()
        ):  # <-- ADDED LOOP LOGGING
            logger.debug(
                f"  - PlotOutline Prompt: {name[:30]:30} ... content preview: {prompt[:100]!r}"
            )  # <-- ADDED LOOP LOGGING

        self.prompts.update(chapter_outline_prompts.chapter_outline_prompts)
        logger.debug(
            f"Loaded chapter_outline_prompts. Count: {len(chapter_outline_prompts.chapter_outline_prompts)}"
        )  # <-- ADDED LOGGING
        for (
            name,
            prompt,
        ) in (
            chapter_outline_prompts.chapter_outline_prompts.items()
        ):  # <-- ADDED LOOP LOGGING
            logger.debug(
                f"  - ChapterOutline Prompt: {name[:30]:30} ... content preview: {prompt[:100]!r}"
            )  # <-- ADDED LOOP LOGGING

        self.prompts.update(scene_outline_prompts.scene_outline_prompts)
        logger.debug(
            f"Loaded scene_outline_prompts. Count: {len(scene_outline_prompts.scene_outline_prompts)}"
        )  # <-- ADDED LOGGING
        for (
            name,
            prompt,
        ) in (
            scene_outline_prompts.scene_outline_prompts.items()
        ):  # <-- ADDED LOOP LOGGING
            logger.debug(
                f"  - SceneOutline Prompt: {name[:30]:30} ... content preview: {prompt[:100]!r}"
            )  # <-- ADDED LOOP LOGGING

        self.prompts.update(scene_part_prompts.scene_part_prompts)
        logger.debug(
            f"Loaded scene_part_prompts. Count: {len(scene_part_prompts.scene_part_prompts)}"
        )  # <-- ADDED LOGGING
        for (
            name,
            prompt,
        ) in scene_part_prompts.scene_part_prompts.items():  # <-- ADDED LOOP LOGGING
            logger.debug(
                f"  - ScenePart Prompt: {name[:30]:30} ... content preview: {prompt[:100]!r}"
            )  # <-- ADDED LOOP LOGGING

        logger.debug(
            f"Loaded total prompts: {list(self.prompts.keys())}"
        )  # Modified log message

    def get_prompt(self, prompt_name: str) -> str:
        prompt = self.prompts.get(prompt_name)
        if not prompt:
            logger.error(f"Prompt not found: {prompt_name}")
            raise ValueError(f"Prompt not found: {prompt_name}")
        return prompt
