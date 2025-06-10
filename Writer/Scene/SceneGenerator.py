# File: Writer/Scene/SceneGenerator.py
# Purpose: Generates full narrative text for an individual scene based on its detailed outline.

"""
Scene Narrative Generation Module.

This module is responsible for taking a detailed scene outline (blueprint)
and relevant contextual information (overall story, previous scene/chapter summary)
to generate the full narrative text for that specific scene.

It focuses on producing high-quality, vivid prose, crafting believable dialogue,
maintaining character consistency, and ensuring the scene effectively contributes
to the chapter's arc and the overall story's pacing and themes.
"""

import Writer.Config as Config
import Writer.Prompts as Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger
from Writer.Statistics import get_word_count
from typing import Dict, Any, List, Optional
import re


def write_scene_narrative(
    interface: Interface,
    logger: Logger,
    scene_detailed_outline: Dict[str, Any],
    overall_story_outline: str,
    previous_scene_or_chapter_context_summary: str,
    chapter_number: int,
    scene_number_in_chapter: int,
    base_story_context: Optional[str],
    max_tokens: Optional[int] = None,
) -> str:
    """
    Generates the full narrative text for a single scene based on its blueprint and context.

    Args:
        interface (Interface): The LLM interaction wrapper.
        logger (Logger): The logging instance.
        scene_detailed_outline (Dict[str, Any]): The detailed blueprint for the current scene.
        overall_story_outline (str): The main outline of the entire story.
        previous_scene_or_chapter_context_summary (str): Contextual summary from the
                                                         end of the previous scene or chapter.
        chapter_number (int): The current chapter number.
        scene_number_in_chapter (int): The sequence number of this scene within the chapter.
        base_story_context (Optional[str]): Overarching story context or user instructions.
        max_tokens (Optional[int]): Maximum number of tokens the LLM should generate for this scene.

    Returns:
        str: The generated narrative text for the scene. Returns an error message string
             if generation fails.
    """
    scene_title = scene_detailed_outline.get(
        "scene_title", f"Chapter {chapter_number}, Scene {scene_number_in_chapter}"
    )
    logger.Log(
        f"Initiating narrative generation for Scene: '{scene_title}' (C{chapter_number}.S{scene_number_in_chapter})...",
        3,
    )

    if not scene_detailed_outline:
        logger.Log(
            f"Scene detailed outline for '{scene_title}' is empty or missing. Cannot generate narrative.",
            6,
        )
        return f"Scene Generation Error: Blueprint for '{scene_title}' was missing."

    try:
        prompt_template = Prompts.OPTIMIZED_SCENE_NARRATIVE_GENERATION

        key_events_list = scene_detailed_outline.get(
            "key_events_actions", ["No specific key events listed."]
        )
        key_events_str = (
            "- " + "\n- ".join(map(str, key_events_list))
            if key_events_list
            else "No specific key events listed."
        )

        dialogue_points_list = scene_detailed_outline.get(
            "dialogue_points", ["No specific dialogue points listed."]
        )
        dialogue_points_str = (
            "- " + "\n- ".join(map(str, dialogue_points_list))
            if dialogue_points_list
            else "No specific dialogue points listed."
        )

        characters_present_list = scene_detailed_outline.get("characters_present", [])
        characters_present_str = (
            ", ".join(map(str, characters_present_list))
            if characters_present_list
            else "Unknown characters"
        )

        formatted_prompt = prompt_template.format(
            _OverallStoryOutline=(
                overall_story_outline
                if overall_story_outline
                else "Overall story outline not provided."
            ),
            _PreviousSceneContextSummary=(
                previous_scene_or_chapter_context_summary
                if previous_scene_or_chapter_context_summary
                else "No immediate prior context available for this scene."
            ),
            _ChapterNumber=chapter_number,
            _SceneNumberInChapter=scene_number_in_chapter,
            _SceneTitle=scene_title,
            _SceneSettingDescription=scene_detailed_outline.get(
                "setting_description", "Setting not specified."
            ),
            _SceneCharactersPresentAndGoals=f"Characters: {characters_present_str}. Goals/Moods: {scene_detailed_outline.get('character_goals_moods', 'Not specified.')}",
            _SceneKeyEvents=key_events_str,
            _SceneDialogueHighlights=dialogue_points_str,
            _ScenePacingNote=scene_detailed_outline.get(
                "pacing_note", "Moderate pacing assumed."
            ),
            _SceneTone=scene_detailed_outline.get("tone", "Neutral tone assumed."),
            _ScenePurposeInChapter=scene_detailed_outline.get(
                "purpose_in_chapter", "Purpose not specified."
            ),
            _SceneTransitionOutHook=scene_detailed_outline.get(
                "transition_out_hook", "The scene concludes."
            ),
            _BaseStoryContext=(
                base_story_context
                if base_story_context
                else "No additional base story context provided."
            ),
            SCENE_NARRATIVE_MIN_WORDS=Config.SCENE_NARRATIVE_MIN_WORDS,
        )
    except KeyError as e:
        logger.Log(
            f"Formatting error in OPTIMIZED_SCENE_NARRATIVE_GENERATION prompt for '{scene_title}': Missing key {e}",
            7,
        )
        return f"Scene Generation Error: Prompt template key error for '{scene_title}' - {e}."
    except Exception as e:
        logger.Log(
            f"Unexpected error formatting scene narrative prompt for '{scene_title}': {e}",
            7,
        )
        return f"Scene Generation Error: Unexpected prompt formatting error for '{scene_title}' - {e}."

    messages: List[Dict[str, Any]] = [
        interface.build_system_query(Prompts.DEFAULT_SYSTEM_PROMPT),
        interface.build_user_query(formatted_prompt),
    ]

    try:
        logger.Log(
            f"Requesting LLM to write narrative text for Scene '{scene_title}' (C{chapter_number}.S{scene_number_in_chapter}).",
            4,
        )
        response_messages = interface.safe_generate_text(
            logger,
            messages,
            Config.MODEL_SCENE_NARRATIVE_GENERATOR,
            min_word_count=Config.SCENE_NARRATIVE_MIN_WORDS,
            max_tokens=max_tokens,
        )

        scene_narrative_text: str = interface.get_last_message_text(response_messages)

        if not scene_narrative_text or "Error:" in scene_narrative_text:
            logger.Log(
                f"LLM failed to generate narrative for scene '{scene_title}' or returned an error.",
                6,
            )
            return f"Scene Generation Error: LLM failed for '{scene_title}'. Response: {scene_narrative_text[:100]}..."

        generated_word_count = get_word_count(scene_narrative_text)
        logger.Log(
            f"Narrative successfully generated for Scene: '{scene_title}'. Word count: {generated_word_count}",
            4,
        )

        if generated_word_count < Config.SCENE_NARRATIVE_MIN_WORDS:
            logger.Log(
                f"Warning: Generated scene '{scene_title}' has {generated_word_count} words, less than minimum {Config.SCENE_NARRATIVE_MIN_WORDS}.",
                6,
            )

        return scene_narrative_text

    except Exception as e:
        logger.Log(
            f"An unexpected critical error occurred during scene narrative generation for '{scene_title}': {e}",
            7,
        )
        return f"Scene Generation Error: Unexpected critical error for '{scene_title}' - {e}."
