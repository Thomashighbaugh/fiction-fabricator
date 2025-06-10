# File: Writer/LLMEditor.py
# Purpose: Provides LLM-based feedback and ratings for outlines and chapters.

"""
LLM-based Editing and Evaluation Module.

This module contains functions that leverage LLMs to:
- Provide constructive criticism on story outlines (`GetFeedbackOnOutline`).
- Rate the completeness or quality of outlines (`GetOutlineRating`).
- Offer editorial feedback on individual chapter texts (`GetFeedbackOnChapter`).
- Assess if a chapter meets a certain quality standard (`GetChapterRating`).

It uses prompts defined in `Writer.Prompts` and interacts with the LLM
via the `Interface` class. JSON parsing is handled for structured responses.
"""

import json
import Writer.Config as Config
import Writer.PrintUtils
import Writer.Prompts
from Writer.Interface.Wrapper import Interface
import Writer.Models as Models

# Heuristic: 1 word is approx 1.5 tokens in English, but can vary.
WORD_TO_TOKEN_RATIO = 1.5


class LLMEditorError(Exception):
    """Custom exception for errors specific to LLMEditor operations."""

    pass


def GetFeedbackOnOutline(
    interface: Interface, logger: Writer.PrintUtils.Logger, outline_text: str
) -> str:
    """
    Prompts an LLM to critique a story outline.

    Args:
        interface: The LLM interaction wrapper.
        logger: The logging instance.
        outline_text: The story outline text to be critiqued.

    Returns:
        A string containing the LLM's feedback on the outline.
    """
    logger.Log("Prompting LLM To Critique Outline", 5)

    user_prompt_text: str = Writer.Prompts.OPTIMIZED_CRITIC_OUTLINE_PROMPT.format(
        _Outline=outline_text
    )

    messages = [
        interface.build_system_query(Writer.Prompts.DEFAULT_SYSTEM_PROMPT),
        interface.build_user_query(user_prompt_text),
    ]

    # A critique should be concise, 500 words is a generous limit.
    max_tokens_for_feedback = int(500 * WORD_TO_TOKEN_RATIO)

    response_messages = interface.safe_generate_text(
        logger,
        messages,
        Config.REVISION_MODEL,
        min_word_count=70,
        max_tokens=max_tokens_for_feedback,
    )
    logger.Log("Finished Getting Outline Feedback", 5)
    return interface.get_last_message_text(response_messages)


def GetOutlineRating(
    interface: Interface, logger: Writer.PrintUtils.Logger, outline_text: str
) -> bool:
    """
    Prompts an LLM to rate the completeness of a story outline.

    Args:
        interface: The LLM interaction wrapper.
        logger: The logging instance.
        outline_text: The story outline text to be rated.

    Returns:
        A boolean indicating if the LLM deems the outline complete (True) or not (False).
        Returns False on parsing errors after multiple retries.
    """
    logger.Log("Prompting LLM To Get Outline Review JSON", 5)

    user_prompt_text: str = Writer.Prompts.OUTLINE_COMPLETE_PROMPT.format(
        _Outline=outline_text
    )

    system_prompt_text: str = (
        "You are an AI assistant that evaluates story outlines and responds strictly in JSON format "
        "as per the user's instructions."
    )

    messages = [
        interface.build_system_query(system_prompt_text),
        interface.build_user_query(user_prompt_text),
    ]

    try:
        # Expected output is a tiny JSON object.
        max_tokens_for_rating = 50

        _response_messages, parsed_json_data = interface.safe_generate_json(
            logger,
            messages,
            Config.EVAL_MODEL,
            required_attribs=["IsComplete"],
            max_tokens=max_tokens_for_rating,
            expected_response_model=Models.IsComplete,
        )

        if isinstance(parsed_json_data, dict):
            is_complete = parsed_json_data.get("IsComplete", False)
        else:
            logger.Log(
                f"LLM returned an unexpected type for outline rating: {type(parsed_json_data)}. Expected dict. Defaulting to False.",
                6,
            )
            is_complete = False

        if not isinstance(is_complete, bool):
            logger.Log(
                f"LLM returned non-boolean for IsComplete: {is_complete}. Defaulting to False.",
                6,
            )
            return False
        logger.Log(f"Editor Determined IsComplete for outline: {is_complete}", 5)
        return is_complete
    except Exception as e:
        logger.Log(
            f"Critical Error Parsing JSON for outline rating or LLM call failed: {e}", 7
        )
        return False


def GetFeedbackOnChapter(
    interface: Interface,
    logger: Writer.PrintUtils.Logger,
    chapter_text: str,
    overall_story_outline: str,
) -> str:
    """
    Prompts an LLM to critique a chapter text.

    Args:
        interface: The LLM interaction wrapper.
        logger: The logging instance.
        chapter_text: The chapter text to be critiqued.
        overall_story_outline: The overall story outline for context.

    Returns:
        A string containing the LLM's feedback on the chapter.
    """
    logger.Log("Prompting LLM To Critique Chapter", 5)

    user_prompt_text: str = Writer.Prompts.OPTIMIZED_CRITIC_CHAPTER_PROMPT.format(
        _ChapterText=chapter_text,
        _OverallStoryOutline=overall_story_outline,
    )

    messages_for_llm = [
        interface.build_system_query(Writer.Prompts.DEFAULT_SYSTEM_PROMPT),
        interface.build_user_query(user_prompt_text),
    ]

    # A critique should be concise, 500 words is a generous limit.
    max_tokens_for_feedback = int(500 * WORD_TO_TOKEN_RATIO)

    response_messages = interface.safe_generate_text(
        logger,
        messages_for_llm,
        Config.REVISION_MODEL,
        min_word_count=100,
        max_tokens=max_tokens_for_feedback,
    )
    logger.Log("Finished Getting Chapter Feedback", 5)
    return interface.get_last_message_text(response_messages)


def GetChapterRating(
    interface: Interface, logger: Writer.PrintUtils.Logger, chapter_text: str
) -> bool:
    """
    Prompts an LLM to rate the completeness/quality of a chapter.

    Args:
        interface: The LLM interaction wrapper.
        logger: The logging instance.
        chapter_text: The chapter text to be rated.

    Returns:
        A boolean indicating if the LLM deems the chapter complete/good (True) or not (False).
        Returns False on parsing errors after multiple retries.
    """
    logger.Log("Prompting LLM To Get Chapter Review JSON", 5)

    user_prompt_text: str = Writer.Prompts.CHAPTER_COMPLETE_PROMPT.format(
        _Chapter=chapter_text
    )

    system_prompt_text: str = (
        "You are an AI assistant that evaluates story chapters and responds strictly in JSON format "
        "as per the user's instructions."
    )

    messages = [
        interface.build_system_query(system_prompt_text),
        interface.build_user_query(user_prompt_text),
    ]

    try:
        # Expected output is a tiny JSON object.
        max_tokens_for_rating = 50

        _response_messages, parsed_json_data = interface.safe_generate_json(
            logger,
            messages,
            Config.EVAL_MODEL,
            required_attribs=["IsComplete"],
            max_tokens=max_tokens_for_rating,
            expected_response_model=Models.IsComplete,
        )

        if isinstance(parsed_json_data, dict):
            is_complete = parsed_json_data.get("IsComplete", False)
        else:
            logger.Log(
                f"LLM returned an unexpected type for chapter rating: {type(parsed_json_data)}. Expected dict. Defaulting to False.",
                6,
            )
            is_complete = False

        if not isinstance(is_complete, bool):
            logger.Log(
                f"LLM returned non-boolean for IsComplete: {is_complete}. Defaulting to False.",
                6,
            )
            return False
        logger.Log(f"Editor Determined IsComplete for chapter: {is_complete}", 5)
        return is_complete
    except Exception as e:
        logger.Log(
            f"Critical Error Parsing JSON for chapter rating or LLM call failed: {e}", 7
        )
        return False
