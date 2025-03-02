#/home/tlh/refactored_gui_fict_fab/llm/prompt_manager/prompt_manager.py
import logging
from typing import Dict, Protocol, runtime_checkable

from utils.logger import logger  # Assuming you have a logger configured

from llm.prompt_manager.book_spec_prompts import BookSpecPrompts
from llm.prompt_manager.plot_outline_prompts import PlotOutlinePrompts
from llm.prompt_manager.chapter_outline_prompts import ChapterOutlinePrompts
from llm.prompt_manager.scene_outline_prompts import SceneOutlinePrompts
from llm.prompt_manager.scene_part_prompts import ScenePartPrompts



@runtime_checkable
class PromptManagerInterface(Protocol):
    """
    Defines the interface for PromptManager classes.
    """

    """
    Retrieves a specific prompt by its name.

    Args:
        prompt_name (str): The name identifier of the prompt to retrieve.

    Returns:
        str: The requested prompt text.

    Raises:
        NotImplementedError: This is an abstract method that must be implemented by subclasses.
    """

    def get_prompt(self, prompt_name: str) -> str: ...  # Abstract method


class DynamicPromptManager(PromptManagerInterface):
    """
    Manages prompts dynamically, defining them directly in code.
    """

    def __init__(self):
        """
        Initializes the DynamicPromptManager by defining prompts.
        """
        self.book_spec_prompts = BookSpecPrompts()
        self.plot_outline_prompts = PlotOutlinePrompts()
        self.chapter_outline_prompts = ChapterOutlinePrompts()
        self.scene_outline_prompts = SceneOutlinePrompts()
        self.scene_part_prompts = ScenePartPrompts()



    def get_prompt(self, prompt_name: str) -> str:
        """
        Retrieves a prompt by its name.

        Args:
            prompt_name (str): The name of the prompt to retrieve.

        Returns:
            str: The prompt text. Raises an exception if the prompt is not found.
        """
        if prompt_name.startswith("book_spec"):
            prompt_text =  getattr(self.book_spec_prompts, f"create_{prompt_name}")()
        elif prompt_name.startswith("plot_outline"):
            prompt_text = getattr(self.plot_outline_prompts, f"create_{prompt_name}")()
        elif prompt_name.startswith("chapter_outlines"):
            prompt_text =  getattr(self.chapter_outline_prompts, f"create_{prompt_name}")()
        elif prompt_name.startswith("scene_outlines"):
            prompt_text = getattr(self.scene_outline_prompts, f"create_{prompt_name}")()
        elif prompt_name.startswith("scene_part"):
            prompt_text = getattr(self.scene_part_prompts, f"create_{prompt_name}")()
        else:
            raise ValueError(f"couldnt find {prompt_name}")
        
        if prompt_text:
            logger.debug("Retrieved prompt: {prompt_name}")
            return prompt_text
        else:
            logger.warning("Prompt not found: {prompt_name}")
            raise ValueError("Prompt not found: {prompt_name}")