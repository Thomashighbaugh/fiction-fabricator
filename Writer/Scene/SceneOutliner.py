# File: Writer/Scene/SceneOutliner.py
# Purpose: Generates a detailed, structured list of scene outlines for a given chapter.

"""
Scene Outliner Module.

This module takes a high-level plot outline for a specific chapter and
expands it into a detailed, structured list of scene outlines. Each scene
outline serves as a blueprint for the `SceneGenerator` module to write the
full narrative text for that scene.

The process involves:
- Formatting a request to an LLM using an optimized prompt.
- Attempting to get a direct JSON response from the LLM, leveraging Pydantic models for validation.
- If direct JSON fails, falling back to text generation and parsing with `SceneParser`.
"""
import json
import Writer.Config as Config
import Writer.Prompts as Prompts
import Writer.Scene.SceneParser as SceneParser
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger
from typing import List, Dict, Any, Optional, Union, Tuple
import Writer.Models as Models
from pydantic import ValidationError


def generate_detailed_scene_outlines(
    interface: Interface,
    logger: Logger,
    chapter_plot_outline: str,
    overall_story_outline: str,
    chapter_number: int,
    previous_chapter_context_summary: Optional[str],
    base_story_context: Optional[str],
) -> List[Dict[str, Any]]:
    """
    Generates a list of detailed scene outlines for a given chapter's plot outline.
    Prioritizes getting structured JSON directly from LLM, falls back to text parsing.

    Args:
        interface (Interface): The LLM interaction wrapper.
        logger (Logger): The logging instance.
        chapter_plot_outline (str): The specific plot outline for the current chapter.
        overall_story_outline (str): The main outline of the entire story for broader context.
        chapter_number (int): The current chapter number.
        previous_chapter_context_summary (Optional[str]): A summary of key elements from
                                                          the end of the previous chapter.
                                                          Can be None for the first chapter.
        base_story_context (Optional[str]): Overarching story context or user instructions.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dictionary represents
                              a detailed scene outline. Returns an empty list if
                              generation or parsing fails.
    """
    logger.Log(
        f"Initiating detailed scene outlining for Chapter {chapter_number}...", 3
    )

    if not chapter_plot_outline or not chapter_plot_outline.strip():
        logger.Log(
            f"Chapter {chapter_number} plot outline is empty. Cannot generate scene outlines.",
            6,
        )
        return []

    try:
        prompt_template = Prompts.OPTIMIZED_CHAPTER_TO_SCENES_BREAKDOWN
        formatted_prompt = prompt_template.format(
            _ChapterPlotOutline=chapter_plot_outline,
            _OverallStoryOutline=overall_story_outline,
            _PreviousChapterContextSummary=(
                previous_chapter_context_summary
                if previous_chapter_context_summary
                else "This is the first chapter; no specific summary from a preceding chapter is available. Rely on the overall story outline and this chapter's plot."
            ),
            _ChapterNumber=chapter_number,
            _BaseStoryContext=(
                base_story_context
                if base_story_context
                else "No additional base story context provided."
            ),
            SCENE_OUTLINE_MIN_SCENES_PER_CHAPTER=Config.SCENE_OUTLINE_MIN_SCENES_PER_CHAPTER,
        )
    except KeyError as e:
        logger.Log(
            f"Formatting error in OPTIMIZED_CHAPTER_TO_SCENES_BREAKDOWN prompt for Chapter {chapter_number}: Missing key {e}",
            7,
        )
        return []
    except Exception as e:
        logger.Log(
            f"Unexpected error formatting scene outliner prompt for Chapter {chapter_number}: {e}",
            7,
        )
        return []

    messages: List[Dict[str, Any]] = [
        interface.build_system_query(Prompts.DEFAULT_SYSTEM_PROMPT),
        interface.build_user_query(formatted_prompt),
    ]

    parsed_scene_outlines_list: List[Dict[str, Any]] = []
    parsed_json_data = (
        None  # Initialize to handle cases where safe_generate_json throws an exception
    )

    try:
        logger.Log(
            f"Attempting to generate scene outlines for Chapter {chapter_number} directly as JSON using model: {Config.MODEL_SCENE_OUTLINER} with Pydantic model {Models.SceneOutlinesList.__name__}.",
            4,
        )
        # Attempt to get structured JSON directly from the LLM using the Pydantic model
        _response_messages, parsed_json_data = interface.safe_generate_json(
            logger,
            messages,
            Config.MODEL_SCENE_OUTLINER,
            expected_response_model=Models.SceneOutlinesList,
            required_attribs=[],
        )

        # When `expected_response_model` is used, `parsed_json_data` will be the `.model_dump()` output of the Pydantic model.
        # For Models.SceneOutlinesList, this means a dict like `{"scenes": [...]}`.
        if (
            isinstance(parsed_json_data, dict)
            and "scenes" in parsed_json_data
            and isinstance(parsed_json_data["scenes"], list)
        ):
            # The actual list of scene dictionaries is under the "scenes" key.
            candidate_scene_list = parsed_json_data["scenes"]

            # Perform a basic validation on the items in the list: check if they look like scene dicts.
            if not candidate_scene_list:  # Empty list is valid if LLM decides no scenes
                parsed_scene_outlines_list = (
                    candidate_scene_list  # Could be an empty list.
                )
                logger.Log(
                    f"safe_generate_json returned an empty list of scenes for Chapter {chapter_number}.",
                    4,
                )
            elif all(
                isinstance(item, dict)
                and ("scene_title" in item or "key_events_actions" in item)
                for item in candidate_scene_list
            ):
                parsed_scene_outlines_list = candidate_scene_list
                logger.Log(
                    f"Successfully parsed {len(parsed_scene_outlines_list)} scene outlines for Chapter {chapter_number} via safe_generate_json (Pydantic).",
                    4,
                )
            else:
                logger.Log(
                    f"safe_generate_json for Chapter {chapter_number} returned a list of dicts within 'scenes', but items don't appear to be valid scene outlines. Will attempt text fallback.",
                    6,
                )

        elif isinstance(parsed_json_data, dict) and "Error" in parsed_json_data:
            logger.Log(
                f"safe_generate_json for Chapter {chapter_number} returned an error dictionary: {parsed_json_data.get('Error')}. Will attempt text fallback.",
                6,
            )
        else:  # If safe_generate_json did not return the expected Models.SceneOutlinesList structure or an error dict
            logger.Log(
                f"safe_generate_json for Chapter {chapter_number} did not return the expected Pydantic model structure (got type: {type(parsed_json_data)}). Will attempt text fallback.",
                6,
            )

    except Exception as e:
        logger.Log(
            f"Critical error during safe_generate_json for Chapter {chapter_number} scene outlining: {e}. Falling back to text generation and SceneParser.",
            6,
        )
        # Ensure parsed_scene_outlines_list remains empty to trigger fallback

    # Fallback to text generation and SceneParser if direct JSON failed or was not the expected list of dicts
    # Only fallback if parsed_scene_outlines_list is empty AND it wasn't an intentionally empty list from Pydantic.
    if not parsed_scene_outlines_list and not (
        isinstance(parsed_json_data, dict)
        and "scenes" in parsed_json_data
        and not parsed_json_data["scenes"]
    ):
        logger.Log(
            f"Falling back to text generation and SceneParser for scene outlines for Chapter {chapter_number}.",
            5,
        )
        # Estimated min words for scene outlines: (75 words/scene) * (min scenes/chapter)
        estimated_min_words_for_scene_outlines = (
            75 * Config.SCENE_OUTLINE_MIN_SCENES_PER_CHAPTER
        )

        try:
            response_messages_text_fallback = interface.safe_generate_text(
                logger,
                messages,
                Config.MODEL_SCENE_OUTLINER,
                min_word_count=estimated_min_words_for_scene_outlines,
            )

            raw_llm_scene_outlines_text: str = interface.get_last_message_text(
                response_messages_text_fallback
            )

            if (
                not raw_llm_scene_outlines_text
                or "Error:" in raw_llm_scene_outlines_text
            ):
                logger.Log(
                    f"LLM (text fallback) failed to generate scene outlines for Chapter {chapter_number} or returned an error: {raw_llm_scene_outlines_text[:100]}...",
                    6,
                )
                return []  # Critical failure at this point

            parsed_scene_outlines_list = SceneParser.parse_llm_scene_outlines_response(
                interface,
                logger,
                raw_llm_scene_outlines_text,
                Config.EVAL_MODEL,  # Use EVAL_MODEL for JSON correction by default within SceneParser
            )
            if parsed_scene_outlines_list:
                logger.Log(
                    f"Successfully parsed {len(parsed_scene_outlines_list)} scene outlines for Chapter {chapter_number} via text fallback and SceneParser.",
                    4,
                )

        except Exception as e_fallback:
            logger.Log(
                f"An unexpected error occurred during text fallback scene outlining for Chapter {chapter_number}: {e_fallback}",
                7,
            )
            return []  # Critical failure

    # Final checks and logging for the obtained list (whether from direct JSON or fallback)
    if not parsed_scene_outlines_list:
        logger.Log(
            f"Failed to generate or parse any detailed scene outlines for Chapter {chapter_number} after all attempts.",
            6,
        )
        return []

    if len(parsed_scene_outlines_list) < Config.SCENE_OUTLINE_MIN_SCENES_PER_CHAPTER:
        logger.Log(
            f"Warning: Generated only {len(parsed_scene_outlines_list)} scenes for Chapter {chapter_number}, less than minimum {Config.SCENE_OUTLINE_MIN_SCENES_PER_CHAPTER}.",
            6,
        )

    # Ensure scene_number_in_chapter is correctly set if missing or just for consistency
    # This loop is crucial because Pydantic validation might correct the incoming structure,
    # but the scene_number_in_chapter should always be sequential for downstream processes.
    for idx, scene_dict in enumerate(parsed_scene_outlines_list):
        # Pydantic model already enforces `scene_number_in_chapter: int` and `ge=1`.
        # However, if it's the *fallback* path, or if the LLM sometimes makes errors
        # even with Pydantic (e.g., if the base LLM output is extremely malformed),
        # this ensures sequential numbering.
        if "scene_number_in_chapter" not in scene_dict or scene_dict[
            "scene_number_in_chapter"
        ] != (idx + 1):
            logger.Log(
                f"Scene outline item for Ch.{chapter_number} had non-sequential or missing 'scene_number_in_chapter' (got {scene_dict.get('scene_number_in_chapter')}, expected {idx+1}). Forcing sequential number: {idx + 1}.",
                5,
            )
        scene_dict["scene_number_in_chapter"] = (
            idx + 1
        )  # Force sequential numbering regardless.

    logger.Log(
        f"Successfully generated and finalized {len(parsed_scene_outlines_list)} scene outlines for Chapter {chapter_number}.",
        4,
    )
    return parsed_scene_outlines_list
