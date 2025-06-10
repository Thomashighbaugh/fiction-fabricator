# File: Writer/OutlineGenerator.py
# Purpose: Generates the main story outline, chapter by chapter, using story elements and LLM feedback.

"""
Overall Story Outline Generation Module.

This module orchestrates the creation of a chapter-by-chapter plot outline
for the entire story. It leverages previously generated story elements and
employs an iterative feedback loop with an LLM to refine the outline's
quality, coherence, and pacing.

The final output is a structured Markdown document detailing each chapter's
key events, character developments, and narrative purpose.
"""

import Writer.Config as Config
import Writer.Prompts as Prompts
import Writer.LLMEditor as LLMEditor
import Writer.Outline.StoryElements as StoryElements
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger
import json
from typing import Tuple, List, Dict, Any

# Heuristic: 1 word is approx 1.5 tokens in English, but can vary. Use 1.5-2 for safer estimation.
WORD_TO_TOKEN_RATIO = 1.5


def generate_outline(
    interface: Interface, logger: Logger, user_story_prompt: str
) -> Tuple[str, str, str, str]:
    """
    Generates a comprehensive, chapter-by-chapter story outline.

    The process involves:
    1. Extracting any overarching context or instructions from the user's prompt.
    2. Generating foundational story elements (genre, characters, plot synopsis, etc.).
    3. Producing an initial chapter-level outline based on the elements and prompt.
    4. Iteratively refining this outline using LLM-based feedback and quality checks.

    Args:
        interface (Interface): The LLM interaction wrapper instance.
        logger (Logger): The logging instance.
        user_story_prompt (str): The user's initial story idea or prompt.

    Returns:
        Tuple[str, str, str, str]:
            - printable_full_outline (str): A string containing the base context,
              story elements, and the final chapter-level outline, suitable for printing or saving.
            - story_elements_markdown (str): The Markdown content of the generated story elements.
            - final_chapter_level_outline (str): The refined chapter-by-chapter plot outline.
            - base_story_context (str): Extracted important context/instructions from the user prompt.
    """
    logger.Log("Starting Overall Story Outline Generation Process...", 2)

    if not user_story_prompt or not user_story_prompt.strip():
        error_msg = "User story prompt is empty. Cannot generate outline."
        logger.Log(error_msg, 7)
        return (
            error_msg,
            error_msg,
            error_msg,
            error_msg,
        )

    logger.Log("Extracting base context from user prompt...", 3)
    base_story_context = ""
    try:
        prompt_ctx_template = Prompts.GET_IMPORTANT_BASE_PROMPT_INFO
        formatted_prompt_ctx = prompt_ctx_template.format(_Prompt=user_story_prompt)
        messages_ctx = [interface.build_user_query(formatted_prompt_ctx)]

        max_tokens_for_context = int(150 * WORD_TO_TOKEN_RATIO)

        response_ctx_messages = interface.safe_generate_text(
            logger,
            messages_ctx,
            Config.EVAL_MODEL,
            min_word_count=5,
            max_tokens=max_tokens_for_context,
        )
        base_story_context = interface.get_last_message_text(response_ctx_messages)
        logger.Log(
            f"Base story context extracted (first 100 chars): '{base_story_context[:100].replace('\n', ' ')}...'",
            3,
        )
    except KeyError as e:
        logger.Log(
            f"Formatting error in GET_IMPORTANT_BASE_PROMPT_INFO prompt: Missing key {e}",
            6,
        )
        base_story_context = (
            "Warning: Could not extract base context due to prompt template error."
        )
    except Exception as e:
        logger.Log(f"Unexpected error during base context extraction: {e}", 6)
        base_story_context = f"Warning: Error extracting base context - {e}."

    logger.Log("Generating foundational story elements...", 3)
    max_tokens_for_elements = int(1000 * WORD_TO_TOKEN_RATIO)

    story_elements_markdown = StoryElements.generate_story_elements(
        interface, logger, user_story_prompt, max_tokens=max_tokens_for_elements
    )
    if "Error:" in story_elements_markdown:
        logger.Log(f"Failed to generate story elements: {story_elements_markdown}", 7)
        return (
            story_elements_markdown,
            story_elements_markdown,
            story_elements_markdown,
            base_story_context,
        )

    logger.Log("Generating initial chapter-level outline...", 3)
    current_outline = ""
    current_history_for_revision: List[Dict[str, Any]] = []
    try:
        prompt_initial_outline_template = Prompts.OPTIMIZED_OVERALL_OUTLINE_GENERATION
        formatted_prompt_initial_outline = prompt_initial_outline_template.format(
            _UserStoryPrompt=user_story_prompt,
            _StoryElementsMarkdown=story_elements_markdown,
        )
        messages_initial_outline = [
            interface.build_system_query(Prompts.DEFAULT_SYSTEM_PROMPT),
            interface.build_user_query(formatted_prompt_initial_outline),
        ]

        max_tokens_for_initial_outline = int(1500 * WORD_TO_TOKEN_RATIO)

        response_initial_outline_messages = interface.safe_generate_text(
            logger,
            messages_initial_outline,
            Config.INITIAL_OUTLINE_WRITER_MODEL,
            min_word_count=200,
            max_tokens=max_tokens_for_initial_outline,
        )
        current_outline = interface.get_last_message_text(
            response_initial_outline_messages
        )
        current_history_for_revision = response_initial_outline_messages
        logger.Log("Initial chapter-level outline generated.", 4)
    except KeyError as e:
        error_msg = f"Formatting error in OPTIMIZED_OVERALL_OUTLINE_GENERATION prompt: Missing key {e}"
        logger.Log(error_msg, 7)
        return error_msg, story_elements_markdown, error_msg, base_story_context
    except Exception as e:
        error_msg = f"Unexpected error during initial outline generation: {e}"
        logger.Log(error_msg, 7)
        return error_msg, story_elements_markdown, error_msg, base_story_context

    if not current_outline or "Error:" in current_outline:
        error_msg = (
            f"Initial outline generation failed or returned error: {current_outline}"
        )
        logger.Log(error_msg, 7)
        return error_msg, story_elements_markdown, current_outline, base_story_context

    logger.Log("Entering outline revision loop...", 3)
    iterations = 0

    while iterations < Config.OUTLINE_MAX_REVISIONS:
        iterations += 1
        logger.Log(
            f"Outline Revision Iteration {iterations}/{Config.OUTLINE_MAX_REVISIONS}", 3
        )

        try:
            feedback_on_outline = LLMEditor.GetFeedbackOnOutline(
                interface, logger, current_outline
            )
            logger.Log(
                f"Feedback received for outline (first 100 chars): '{feedback_on_outline[:100].replace('\n', ' ')}...'",
                3,
            )

            is_outline_complete = LLMEditor.GetOutlineRating(
                interface, logger, current_outline
            )
            logger.Log(f"Outline completion status: {is_outline_complete}", 3)

            if is_outline_complete and iterations >= Config.OUTLINE_MIN_REVISIONS:
                logger.Log(
                    "Outline meets quality standards and minimum revision count. Exiting revision loop.",
                    4,
                )
                break

            if iterations == Config.OUTLINE_MAX_REVISIONS:
                logger.Log(
                    f"Max outline revisions ({Config.OUTLINE_MAX_REVISIONS}) reached. Proceeding with current outline (IsComplete: {is_outline_complete}).",
                    6 if not is_outline_complete else 4,
                )
                break

            logger.Log("Revising outline based on feedback...", 3)
            current_outline, current_history_for_revision = _revise_outline_internal(
                interface,
                logger,
                current_outline,
                feedback_on_outline,
                current_history_for_revision,
            )
            if "Error:" in current_outline:
                logger.Log(f"Outline revision failed: {current_outline}", 7)
                break

            logger.Log("Outline revised successfully.", 4)

        except Exception as e:
            logger.Log(
                f"Error during outline revision loop (iteration {iterations}): {e}", 7
            )
            break

    final_chapter_level_outline = current_outline

    printable_full_outline = (
        f"# Base Story Context/Instructions:\n{base_story_context}\n\n---\n\n"
        f"# Story Elements:\n{story_elements_markdown}\n\n---\n\n"
        f"# Chapter-by-Chapter Outline:\n{final_chapter_level_outline}"
    )

    logger.Log("Overall Story Outline Generation Process Complete.", 2)
    return (
        printable_full_outline,
        story_elements_markdown,
        final_chapter_level_outline,
        base_story_context,
    )


def _revise_outline_internal(
    interface: Interface,
    logger: Logger,
    current_outline_text: str,
    feedback_text: str,
    history_messages: List[Dict[str, Any]],
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Internal helper function to revise an outline based on feedback.
    Manages the LLM call for revision.

    Args:
        interface: LLM interface.
        logger: Logger instance.
        current_outline_text: The current version of the outline.
        feedback_text: The feedback to apply.
        history_messages: The message history leading to the current outline, for context.

    Returns:
        Tuple[str, List[Dict[str, Any]]]: The revised outline text and the updated message history.
    """
    try:
        revision_prompt_template = Prompts.OUTLINE_REVISION_PROMPT
        formatted_revision_prompt = revision_prompt_template.format(
            _Outline=current_outline_text, _Feedback=feedback_text
        )
    except KeyError as e:
        error_msg = f"Formatting error in OUTLINE_REVISION_PROMPT: Missing key {e}"
        logger.Log(error_msg, 7)
        return (
            f"Error: {error_msg}",
            history_messages,
        )
    except Exception as e:
        error_msg = f"Unexpected error formatting revision prompt: {e}"
        logger.Log(error_msg, 7)
        return f"Error: {error_msg}", history_messages

    messages_for_revision = history_messages[:]
    messages_for_revision.append(interface.build_user_query(formatted_revision_prompt))

    try:
        min_words_for_revision = max(50, len(current_outline_text.split()) // 2)

        current_outline_tokens = int(
            len(current_outline_text.split()) * WORD_TO_TOKEN_RATIO
        )
        max_tokens_for_revision = min(
            int(current_outline_tokens * 1.5) + 100, int(2000 * WORD_TO_TOKEN_RATIO)
        )

        response_revised_outline_messages = interface.safe_generate_text(
            logger,
            messages_for_revision,
            Config.INITIAL_OUTLINE_WRITER_MODEL,
            min_word_count=min_words_for_revision,
            max_tokens=max_tokens_for_revision,
        )

        revised_outline_text: str = interface.get_last_message_text(
            response_revised_outline_messages
        )

        if not revised_outline_text or "Error:" in revised_outline_text:
            logger.Log(
                f"LLM failed to revise outline or returned an error: {revised_outline_text}",
                6,
            )
            return (
                current_outline_text,
                history_messages,
            )

        logger.Log(
            f"Revised outline length: {len(revised_outline_text.split())} words. Max tokens: {max_tokens_for_revision}",
            4,
        )
        return revised_outline_text, response_revised_outline_messages

    except Exception as e:
        logger.Log(
            f"An unexpected error occurred during internal outline revision call: {e}",
            7,
        )
        return (
            f"Error: Unexpected critical error during revision - {e}",
            history_messages,
        )
