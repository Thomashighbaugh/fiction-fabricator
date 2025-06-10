# File: Writer/Chapter/ChapterContext.py
# Purpose: Generates contextual summaries of completed chapters or scenes to aid narrative flow.

"""
Chapter and Scene Context Generation Module.

This module is responsible for creating concise summaries of previously
generated content (chapters or scenes). These summaries serve as crucial
context for the LLM when it begins generating the next piece of the narrative,
helping to ensure smooth transitions, maintain plot consistency, and preserve
character development arcs.
"""
import json
import Writer.Config as Config
import Writer.Prompts as Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger
from typing import Optional, Dict, Any, List


def generate_previous_chapter_summary(
    interface: Interface,
    logger: Logger,
    completed_chapter_text: str,
    overall_story_outline: str,
    chapter_number_of_completed_chapter: int,
    max_tokens: Optional[int] = None,
) -> str:
    """
    Generates a contextual summary of a completed chapter, focusing on elements
    important for writing the next chapter.

    Args:
        interface (Interface): The LLM interaction wrapper.
        logger (Logger): The logging instance.
        completed_chapter_text (str): The full text of the chapter that was just finished.
        overall_story_outline (str): The main outline of the entire story for broader context.
        chapter_number_of_completed_chapter (int): The number of the chapter that was just completed.
        max_tokens (Optional[int]): Maximum number of tokens the LLM should generate for the summary.

    Returns:
        str: A string containing the contextual summary. Returns an error message string
             if generation fails.
    """
    logger.Log(
        f"Generating contextual summary for the end of Chapter {chapter_number_of_completed_chapter}...",
        3,
    )

    if not completed_chapter_text or not completed_chapter_text.strip():
        logger.Log(
            f"Completed chapter text for Chapter {chapter_number_of_completed_chapter} is empty. Cannot generate summary.",
            6,
        )
        return "Context Error: Previous chapter text was empty."

    try:
        prompt_template = Prompts.OPTIMIZED_PREVIOUS_CHAPTER_SUMMARY_FOR_CONTEXT
        formatted_prompt = prompt_template.format(
            _CompletedChapterText=completed_chapter_text,
            _OverallStoryOutline=overall_story_outline,
            _ChapterNumberOfCompletedChapter=chapter_number_of_completed_chapter,
        )
    except KeyError as e:
        logger.Log(
            f"Formatting error in OPTIMIZED_PREVIOUS_CHAPTER_SUMMARY_FOR_CONTEXT prompt: Missing key {e}",
            7,
        )
        return f"Context Error: Prompt template key error - {e}."
    except (ValueError, IndexError) as e:
        logger.Log(
            f"Unexpected error formatting previous chapter summary prompt: {e}", 7
        )
        return f"Context Error: Unexpected prompt formatting error - {e}."

    messages: List[Dict[str, Any]] = [
        interface.build_system_query(
            Prompts.DEFAULT_SYSTEM_PROMPT
        ),
        interface.build_user_query(formatted_prompt),
    ]

    try:
        response_messages = interface.safe_generate_text(
            logger,
            messages,
            Config.MODEL_CHAPTER_CONTEXT_SUMMARIZER,
            min_word_count=50,
            max_tokens=max_tokens,
        )

        context_summary: str = interface.get_last_message_text(response_messages)

        if (
            not context_summary or "Error:" in context_summary
        ):
            logger.Log(
                f"LLM failed to generate a valid context summary for Chapter {chapter_number_of_completed_chapter}.",
                6,
            )
            return f"Context Error: Failed to generate summary for Chapter {chapter_number_of_completed_chapter}."

        logger.Log(
            f"Contextual summary for Chapter {chapter_number_of_completed_chapter} generated successfully.",
            3,
        )
        return context_summary

    except Exception as e:
        logger.Log(
            f"An unexpected error occurred during previous chapter summary generation: {e}",
            7,
        )
        return f"Context Error: Unexpected critical error during summary generation for Chapter {chapter_number_of_completed_chapter} - {e}."


def generate_previous_scene_summary(
    interface: Interface,
    logger: Logger,
    completed_scene_text: str,
    completed_scene_outline: Dict[str, Any],
    max_tokens: Optional[int] = None,
) -> str:
    """
    Generates a very brief contextual summary of a completed scene, focusing on
    immediate takeaways for the next scene within the same chapter.

    Args:
        interface (Interface): The LLM interaction wrapper.
        logger (Logger): The logging instance.
        completed_scene_text (str): The full text of the scene that was just finished.
        completed_scene_outline (Dict[str, Any]): The detailed outline object/dictionary
                                                  for the scene that was just completed.
        max_tokens (Optional[int]): Maximum number of tokens the LLM should generate for the summary.

    Returns:
        str: A short string containing the contextual summary for the next scene.
             Returns an error message string if generation fails.
    """
    scene_title = completed_scene_outline.get("scene_title", "Untitled Scene")
    logger.Log(
        f"Generating brief context summary for end of scene: '{scene_title}'...", 2
    )

    if not completed_scene_text or not completed_scene_text.strip():
        logger.Log(
            f"Completed scene text for '{scene_title}' is empty. Cannot generate summary.",
            6,
        )
        return "Scene Context Error: Previous scene text was empty."

    try:
        prompt_template = Prompts.OPTIMIZED_PREVIOUS_SCENE_SUMMARY_FOR_CONTEXT
        formatted_prompt = prompt_template.format(
            _CompletedSceneText=completed_scene_text,
            _CurrentSceneOutline=json.dumps(
                completed_scene_outline, indent=2
            ),
        )
    except KeyError as e:
        logger.Log(
            f"Formatting error in OPTIMIZED_PREVIOUS_SCENE_SUMMARY_FOR_CONTEXT prompt: Missing key {e}",
            7,
        )
        return (
            f"Scene Context Error: Prompt template key error for '{scene_title}' - {e}."
        )
    except Exception as e:
        logger.Log(
            f"Unexpected error formatting previous scene summary prompt for '{scene_title}': {e}",
            7,
        )
        return f"Scene Context Error: Unexpected prompt formatting error for '{scene_title}' - {e}."

    messages: List[Dict[str, Any]] = [
        interface.build_system_query(
            Prompts.DEFAULT_SYSTEM_PROMPT
        ),
        interface.build_user_query(formatted_prompt),
    ]

    try:
        response_messages = interface.safe_generate_text(
            logger,
            messages,
            Config.EVAL_MODEL,
            min_word_count=10,
            max_tokens=max_tokens,
        )

        scene_context_summary: str = interface.get_last_message_text(response_messages)

        if not scene_context_summary or "Error:" in scene_context_summary:
            logger.Log(
                f"LLM failed to generate a valid brief context summary for scene '{scene_title}'.",
                6,
            )
            return (
                f"Scene Context Error: Failed to generate summary for '{scene_title}'."
            )

        logger.Log(
            f"Brief context summary for scene '{scene_title}' generated successfully.",
            2,
        )
        return scene_context_summary

    except Exception as e:
        logger.Log(
            f"An unexpected error occurred during previous scene summary generation for '{scene_title}': {e}",
            7,
        )
        return (
            f"Scene Context Error: Unexpected critical error for '{scene_title}' - {e}."
        )