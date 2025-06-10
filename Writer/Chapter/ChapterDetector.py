# File: Writer/Chapter/ChapterDetector.py
# Purpose: Detects the number of chapters from a given story outline using an LLM.

"""
Chapter Detection Module.

This module uses an LLM to analyze a story outline and determine the
total number of chapters it describes. It's designed to parse structured
outlines where chapters are explicitly mentioned (e.g., "Chapter 1:", "## Chapter Two").
"""

import Writer.Config as Config
import Writer.Prompts as Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger
import json
from typing import List, Dict, Any
import Writer.Models as Models


def llm_count_chapters(
    interface: Interface, logger: Logger, overall_story_outline: str
) -> int:
    """
    Uses an LLM to count the number of chapters in a given story outline.

    Args:
        interface (Interface): The LLM interaction wrapper instance.
        logger (Logger): The logging instance.
        overall_story_outline (str): The story outline text to analyze.

    Returns:
        int: The detected number of chapters. Returns 0 if detection fails
             or if the outline is unclear, or if the LLM returns an invalid count.
    """
    logger.Log("Attempting to detect number of chapters from outline using LLM...", 3)

    if not overall_story_outline or not overall_story_outline.strip():
        logger.Log("Overall story outline is empty. Cannot detect chapters.", 6)
        return 0

    try:
        prompt_template = Prompts.CHAPTER_COUNT_PROMPT
        formatted_prompt = prompt_template.format(_Outline=overall_story_outline)
    except KeyError as e:
        logger.Log(f"Formatting error in CHAPTER_COUNT_PROMPT: Missing key {e}", 7)
        return 0
    except Exception as e:
        logger.Log(f"Unexpected error formatting chapter count prompt: {e}", 7)
        return 0

    messages: List[Dict[str, Any]] = [
        interface.build_system_query(
            "You are an AI assistant that precisely follows formatting instructions and extracts specific information from text."
        ),
        interface.build_user_query(formatted_prompt),
    ]

    try:
        # Expected output is very small, so a tight token limit prevents wasted generation.
        max_tokens_for_count = 20

        _response_messages, parsed_json_data = interface.safe_generate_json(
            logger,
            messages,
            Config.CHECKER_MODEL,  # Use a fast model for simple checks
            required_attribs=["TotalChapters"],
            max_tokens=max_tokens_for_count,
            expected_response_model=Models.TotalChapters,
        )

        if isinstance(parsed_json_data, dict):
            total_chapters_val = parsed_json_data.get("TotalChapters")
        else:
            logger.Log(
                f"LLM returned an unexpected type for chapter count: {type(parsed_json_data)}. Expected dict.",
                6,
            )
            total_chapters_val = None

        if isinstance(total_chapters_val, int) and total_chapters_val >= 0:
            logger.Log(f"LLM detected {total_chapters_val} chapters in the outline.", 4)
            if total_chapters_val == 0 and len(overall_story_outline) > 100:
                logger.Log(
                    f"LLM reported 0 chapters, but outline has content. This might indicate an issue with the outline format or LLM interpretation.",
                    6,
                )
            return total_chapters_val
        else:
            logger.Log(
                f"LLM returned an invalid or non-integer value for TotalChapters: '{total_chapters_val}'. Defaulting to 0 chapters.",
                6,
            )
            return 0

    except Exception as e:
        logger.Log(
            f"An critical error occurred during LLM chapter count detection: {e}", 7
        )
        return 0
