# File: Writer/Chapter/ChapterGenerator.py
# Purpose: Orchestrates the generation of a complete chapter by creating and assembling scenes.

"""
Chapter Generation Orchestrator.

This module manages the process of generating a full chapter. It uses a
scene-by-scene approach:
1.  It calls `SceneOutliner` to break down the chapter's plot outline into
    a list of detailed scene outlines (blueprints). This step includes retries
    if initial attempts fail.
2.  It then iterates through these scene blueprints, calling `SceneGenerator`
    to write the narrative text for each scene.
3.  Context (summaries of previous scenes/chapters) is passed along to ensure
    narrative continuity.
4.  The generated scene narratives are compiled into a single chapter text.
5.  Optionally, this assembled chapter can undergo further refinement or revision
    using LLM-based feedback to improve flow, pacing, and overall cohesion.
"""

import Writer.Config as Config
import Writer.Prompts as Prompts
import Writer.Scene.SceneOutliner as SceneOutliner
import Writer.Scene.SceneGenerator as SceneGenerator
import Writer.Chapter.ChapterContext as ChapterContext
import Writer.LLMEditor as LLMEditor
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger
from Writer.Statistics import get_word_count
from typing import List, Dict, Any, Optional, Tuple

# Heuristic: 1 word is approx 1.5 tokens in English, but can vary. Use 1.5-2 for safer estimation.
WORD_TO_TOKEN_RATIO = 1.5


def generate_chapter_by_scenes(
    interface: Interface,
    logger: Logger,
    chapter_num: int,
    total_chapters: int,
    overall_story_outline: str,
    current_chapter_plot_outline: str,
    previous_chapter_context_summary: Optional[str],
    base_story_context: Optional[str],
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Generates a complete chapter by first outlining scenes and then writing each scene.
    Includes retries for scene outline generation.

    Args:
        interface (Interface): The LLM interaction wrapper.
        logger (Logger): The logging instance.
        chapter_num (int): The current chapter number being generated.
        total_chapters (int): The total number of chapters in the story.
        overall_story_outline (str): The main outline of the entire story (chapter summaries).
        current_chapter_plot_outline (str): The specific plot outline/summary for this chapter,
                                            used as input for scene breakdown.
        previous_chapter_context_summary (Optional[str]): Contextual summary from the end
                                                          of the previous chapter. None if first chapter.
        base_story_context (Optional[str]): Overarching story context or user instructions.

    Returns:
        Tuple[str, List[Dict[str, Any]]]:
            - The full text of the generated chapter. Returns an error message string
              or placeholder if critical failures occur.
            - The list of scene outlines used to generate the chapter.
    """
    logger.Log(
        f"--- Starting Generation for Chapter {chapter_num}/{total_chapters} (Scene-by-Scene Pipeline) ---",
        2,
    )

    if not current_chapter_plot_outline or not current_chapter_plot_outline.strip():
        error_msg = (
            f"Chapter {chapter_num} plot outline is empty. Cannot generate chapter."
        )
        logger.Log(error_msg, 7)
        return f"// {error_msg} //", []

    logger.Log(
        f"Step 1: Generating detailed scene outlines for Chapter {chapter_num}.", 3
    )
    list_of_scene_outlines: List[Dict[str, Any]] = []
    scene_outline_attempts = 0

    while (
        not list_of_scene_outlines
        and scene_outline_attempts < Config.SCENE_OUTLINE_GENERATION_MAX_ATTEMPTS
    ):
        scene_outline_attempts += 1
        if scene_outline_attempts > 1:
            logger.Log(
                f"Retrying scene outline generation for Chapter {chapter_num} (Attempt {scene_outline_attempts}/{Config.SCENE_OUTLINE_GENERATION_MAX_ATTEMPTS})...",
                5,
            )

        list_of_scene_outlines = SceneOutliner.generate_detailed_scene_outlines(
            interface,
            logger,
            current_chapter_plot_outline,
            overall_story_outline,
            chapter_num,
            previous_chapter_context_summary,
            base_story_context,
        )

        if list_of_scene_outlines:
            break
        elif scene_outline_attempts < Config.SCENE_OUTLINE_GENERATION_MAX_ATTEMPTS:
            logger.Log(
                f"Scene outline generation attempt {scene_outline_attempts} for Chapter {chapter_num} yielded no scenes. Will retry if attempts remain.",
                6,
            )

    if not list_of_scene_outlines:
        error_msg = f"No scene outlines were generated for Chapter {chapter_num} after {Config.SCENE_OUTLINE_GENERATION_MAX_ATTEMPTS} attempt(s). Chapter generation aborted."
        logger.Log(error_msg, 7)
        return f"// Chapter {chapter_num} - Generation Error: {error_msg} //", []

    logger.Log(
        f"Successfully generated {len(list_of_scene_outlines)} scene outlines for Chapter {chapter_num} after {scene_outline_attempts} attempt(s).",
        3,
    )

    logger.Log(
        f"Step 2: Generating narrative for each of the {len(list_of_scene_outlines)} scenes in Chapter {chapter_num}.",
        3,
    )
    compiled_scene_texts: List[str] = []

    current_scene_context_summary = (
        previous_chapter_context_summary
        if previous_chapter_context_summary
        else f"This is the very first scene of Chapter {chapter_num}. Refer to the chapter's plot outline and overall story outline for initial context."
    )

    MAX_TOKENS_FOR_SCENE_NARRATIVE = int(
        Config.SCENE_NARRATIVE_MIN_WORDS * WORD_TO_TOKEN_RATIO * 1.5
    )

    for scene_idx, scene_outline_blueprint in enumerate(list_of_scene_outlines):
        scene_number_in_chapter = scene_idx + 1
        scene_title = scene_outline_blueprint.get(
            "scene_title", f"C{chapter_num}.S{scene_number_in_chapter}"
        )
        logger.Log(
            f"Writing narrative for Scene {scene_number_in_chapter}/{len(list_of_scene_outlines)}: '{scene_title}'...",
            4,
        )

        scene_narrative = SceneGenerator.write_scene_narrative(
            interface,
            logger,
            scene_outline_blueprint,
            overall_story_outline,
            current_scene_context_summary,
            chapter_num,
            scene_number_in_chapter,
            base_story_context,
            max_tokens=MAX_TOKENS_FOR_SCENE_NARRATIVE,
        )

        if "Error:" in scene_narrative:
            logger.Log(
                f"Error generating narrative for scene '{scene_title}': {scene_narrative}. Skipping scene.",
                6,
            )
            compiled_scene_texts.append(
                f"\n\n// Scene '{scene_title}' - Generation Error: {scene_narrative} //\n\n"
            )
            current_scene_context_summary = f"Context after failed scene '{scene_title}': An error occurred. Attempting to proceed."
        else:
            compiled_scene_texts.append(scene_narrative)
            logger.Log(
                f"Narrative for scene '{scene_title}' complete. Word count: {get_word_count(scene_narrative)}.",
                4,
            )

            if scene_idx < len(list_of_scene_outlines) - 1:
                MAX_TOKENS_FOR_SCENE_SUMMARY = int(50 * WORD_TO_TOKEN_RATIO)

                current_scene_context_summary = (
                    ChapterContext.generate_previous_scene_summary(
                        interface,
                        logger,
                        scene_narrative,
                        scene_outline_blueprint,
                        max_tokens=MAX_TOKENS_FOR_SCENE_SUMMARY,
                    )
                )
                if "Error:" in current_scene_context_summary:
                    logger.Log(
                        f"Error generating context summary after scene '{scene_title}'. Proceeding with caution.",
                        6,
                    )
                    current_scene_context_summary = (
                        f"Context after scene '{scene_title}': Summary generation failed. "
                        f"The scene involved characters: {scene_outline_blueprint.get('characters_present',[])} "
                        f"and events: {scene_outline_blueprint.get('key_events_actions',[])}."
                    )

    scene_separator = "\n\n* * *\n\n"
    full_chapter_text_from_scenes = scene_separator.join(compiled_scene_texts)
    logger.Log(
        f"Chapter {chapter_num} text assembled from {len(compiled_scene_texts)} scenes. Preliminary word count: {get_word_count(full_chapter_text_from_scenes)}.",
        3,
    )

    refined_chapter_text = full_chapter_text_from_scenes
    if not Config.CHAPTER_NO_REVISIONS and len(compiled_scene_texts) > 1:
        logger.Log(
            f"Step 3: Performing refinement pass on assembled Chapter {chapter_num}...",
            3,
        )
        try:
            refinement_prompt_text = (
                f"The following text is a draft of Chapter {chapter_num}, assembled from multiple individually-written scenes.\n"
                f"Your task is to review and refine this draft to ensure:\n"
                f"- Smooth and natural transitions between scenes.\n"
                f"- Consistent narrative voice and tone throughout the chapter.\n"
                f"- Good overall pacing and flow for the chapter as a whole.\n"
                f"- Elimination of any jarring breaks, awkward phrasing, or minor redundancies that may have arisen from scene assembly.\n\n"
                f"Do NOT significantly alter the core plot events, character actions, or dialogue of the individual scenes.\n"
                f"Focus on enhancing readability, cohesion, and the literary quality of the chapter as a unified piece.\n\n"
                f"Overall Story Outline (for context on this chapter's role):\n"
                f"<OverallStoryOutline>\n{overall_story_outline}\n</OverallStoryOutline>\n\n"
                f"Assembled Draft of Chapter {chapter_num}:\n---\n{full_chapter_text_from_scenes}\n---\n\n"
                f"Provide ONLY the refined and improved text for Chapter {chapter_num}."
            )
            refinement_messages = [
                interface.build_system_query(Prompts.DEFAULT_SYSTEM_PROMPT),
                interface.build_user_query(refinement_prompt_text),
            ]

            current_chapter_words = get_word_count(full_chapter_text_from_scenes)
            MAX_TOKENS_FOR_CHAPTER_REFINEMENT = int(
                current_chapter_words * WORD_TO_TOKEN_RATIO * 1.1
            )
            MIN_WORDS_FOR_CHAPTER_REFINEMENT = int(current_chapter_words * 0.75)

            response_refinement_messages = interface.safe_generate_text(
                logger,
                refinement_messages,
                Config.MODEL_CHAPTER_ASSEMBLY_REFINER,
                min_word_count=MIN_WORDS_FOR_CHAPTER_REFINEMENT,
                max_tokens=MAX_TOKENS_FOR_CHAPTER_REFINEMENT,
            )
            refined_chapter_text = interface.get_last_message_text(
                response_refinement_messages
            )
            logger.Log(
                f"Chapter {chapter_num} refinement pass complete. Word count: {get_word_count(refined_chapter_text)}",
                3,
            )
        except Exception as e:
            logger.Log(
                f"Error during chapter refinement pass for Chapter {chapter_num}: {e}. Using pre-refinement text.",
                6,
            )

    final_chapter_text = refined_chapter_text
    if not Config.CHAPTER_NO_REVISIONS:
        logger.Log(
            f"Step 4: Entering feedback/revision loop for Chapter {chapter_num} (post-assembly/refinement)...",
            3,
        )

        current_revision_history: List[Dict[str, Any]] = [
            interface.build_system_query(Prompts.DEFAULT_SYSTEM_PROMPT),
            interface.build_assistant_query(final_chapter_text),
        ]

        revision_iterations = 0
        while revision_iterations < Config.CHAPTER_MAX_REVISIONS:
            revision_iterations += 1
            logger.Log(
                f"Chapter {chapter_num} - Revision Iteration {revision_iterations}/{Config.CHAPTER_MAX_REVISIONS}",
                4,
            )

            try:
                feedback_on_chapter = LLMEditor.GetFeedbackOnChapter(
                    interface,
                    logger,
                    final_chapter_text,
                    overall_story_outline,
                )

                is_chapter_complete = LLMEditor.GetChapterRating(
                    interface,
                    logger,
                    final_chapter_text,
                )

                if (
                    is_chapter_complete
                    and revision_iterations >= Config.CHAPTER_MIN_REVISIONS
                ):
                    logger.Log(
                        f"Chapter {chapter_num} meets quality standards post-assembly. Exiting revision.",
                        4,
                    )
                    break

                if revision_iterations == Config.CHAPTER_MAX_REVISIONS:
                    logger.Log(
                        f"Max revisions ({Config.CHAPTER_MAX_REVISIONS}) reached for Chapter {chapter_num}. Proceeding with current version (IsComplete: {is_chapter_complete}).",
                        6 if not is_chapter_complete else 4,
                    )
                    break

                logger.Log(
                    f"Revising Chapter {chapter_num} based on feedback (IsComplete: {is_chapter_complete})...",
                    4,
                )
                chapter_revision_prompt_text = Prompts.CHAPTER_REVISION_PROMPT.format(
                    _Chapter=final_chapter_text, _Feedback=feedback_on_chapter
                )

                messages_for_this_revision = current_revision_history[:]
                messages_for_this_revision.append(
                    interface.build_user_query(chapter_revision_prompt_text)
                )

                current_chapter_words_for_rev = get_word_count(final_chapter_text)
                MIN_WORDS_FOR_CHAPTER_REVISION = int(
                    current_chapter_words_for_rev * 0.7
                )
                MAX_TOKENS_FOR_CHAPTER_REVISION = int(
                    current_chapter_words_for_rev * WORD_TO_TOKEN_RATIO * 1.2
                )

                response_revised_chapter_messages = interface.safe_generate_text(
                    logger,
                    messages_for_this_revision,
                    Config.CHAPTER_REVISION_WRITER_MODEL,
                    min_word_count=MIN_WORDS_FOR_CHAPTER_REVISION,
                    max_tokens=MAX_TOKENS_FOR_CHAPTER_REVISION,
                )

                final_chapter_text = interface.get_last_message_text(
                    response_revised_chapter_messages
                )
                current_revision_history = response_revised_chapter_messages
                logger.Log(
                    f"Chapter {chapter_num} revised. New word count: {get_word_count(final_chapter_text)}.",
                    4,
                )

            except Exception as e:
                logger.Log(
                    f"Error during Chapter {chapter_num} revision loop (iteration {revision_iterations}): {e}. Using last good version.",
                    7,
                )
                break

    logger.Log(
        f"--- Finished Generation for Chapter {chapter_num}/{total_chapters}. Final word count: {get_word_count(final_chapter_text)} ---",
        2,
    )
    return final_chapter_text, list_of_scene_outlines
