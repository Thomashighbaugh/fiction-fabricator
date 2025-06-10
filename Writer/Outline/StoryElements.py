# File: Writer/Outline/StoryElements.py
# Purpose: Generates foundational story elements (genre, theme, plot, characters, etc.) using an LLM.

"""
Story Elements Generation Module.

This module is responsible for taking a user's initial story idea (prompt)
and expanding it into a comprehensive set of foundational story elements.
These elements serve as a structured basis for generating the more detailed
story outline and subsequent narrative content.

It utilizes an optimized LLM prompt to elicit rich, descriptive, and
imaginative details for various aspects of the story.
"""

import Writer.Config as Config
import Writer.Prompts as Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger
from typing import Dict, Any, List, Optional


def generate_story_elements(
    interface: Interface,
    logger: Logger,
    user_story_prompt: str,
    max_tokens: Optional[int] = None,
) -> str:
    """
    Generates detailed story elements based on the user's initial story prompt.

    Args:
        interface (Interface): The LLM interaction wrapper instance.
        logger (Logger): The logging instance.
        user_story_prompt (str): The user's initial idea or prompt for the story.
        max_tokens (Optional[int]): Maximum number of tokens the LLM should generate.

    Returns:
        str: A Markdown formatted string containing the generated story elements.
             Returns an error message string if generation fails.
    """
    logger.Log("Initiating story elements generation...", 3)

    if not user_story_prompt or not user_story_prompt.strip():
        logger.Log("User story prompt is empty. Cannot generate story elements.", 7)
        return "Error: User story prompt was empty. Cannot generate story elements."

    try:
        prompt_template = Prompts.OPTIMIZED_STORY_ELEMENTS_GENERATION
        formatted_prompt = prompt_template.format(_UserStoryPrompt=user_story_prompt)
    except KeyError as e:
        logger.Log(
            f"Formatting error in OPTIMIZED_STORY_ELEMENTS_GENERATION prompt: Missing key {e}",
            7,
        )
        return (
            f"Error: Prompt template key error - {e}. Cannot generate story elements."
        )
    except Exception as e:
        logger.Log(
            f"Unexpected error during prompt formatting for story elements: {e}", 7
        )
        return f"Error: Unexpected prompt formatting error - {e}. Cannot generate story elements."

    messages: List[Dict[str, Any]] = [
        interface.build_system_query(Prompts.DEFAULT_SYSTEM_PROMPT),
        interface.build_user_query(formatted_prompt),
    ]

    try:
        response_messages = interface.safe_generate_text(
            logger,
            messages,
            Config.MODEL_STORY_ELEMENTS_GENERATOR,
            min_word_count=250,
            max_tokens=max_tokens,
        )

        elements_markdown: str = interface.get_last_message_text(response_messages)

        if (
            not elements_markdown
            or elements_markdown.strip() == ""
            or "ERROR:" in elements_markdown
        ):
            logger.Log(
                "LLM failed to generate valid story elements or returned an error.", 6
            )
            if "ERROR:" in elements_markdown:
                return f"Error during story element generation: LLM indicated an issue - {elements_markdown}"
            return "Error: LLM returned empty or invalid story elements."

        logger.Log("Story elements generated successfully.", 4)
        return elements_markdown

    except Exception as e:
        logger.Log(
            f"An unexpected error occurred during story elements generation: {e}", 7
        )
        return f"Error: An unexpected critical error occurred: {e}. Please check logs."
