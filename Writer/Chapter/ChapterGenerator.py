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

    # 1. Get detailed scene outlines for this chapter, with retries
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
            break  # Successfully generated outlines
        elif scene_outline_attempts < Config.SCENE_OUTLINE_GENERATION_MAX_ATTEMPTS:
            logger.Log(
                f"Scene outline generation attempt {scene_outline_attempts} for Chapter {chapter_num} yielded no scenes. Will retry if attempts remain.",
                6,
            )
        # If last attempt and still no scenes, the loop will terminate, and the error below will be triggered.

    if not list_of_scene_outlines:
        error_msg = f"No scene outlines were generated for Chapter {chapter_num} after {Config.SCENE_OUTLINE_GENERATION_MAX_ATTEMPTS} attempt(s). Chapter generation aborted."
        logger.Log(error_msg, 7)
        return f"// Chapter {chapter_num} - Generation Error: {error_msg} //", []

    logger.Log(
        f"Successfully generated {len(list_of_scene_outlines)} scene outlines for Chapter {chapter_num} after {scene_outline_attempts} attempt(s).",
        3,
    )

    # 2. Generate narrative for each scene and compile them
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

            if (
                scene_idx < len(list_of_scene_outlines) - 1
            ):  # Don't summarize after the last scene of the chapter
                current_scene_context_summary = (
                    ChapterContext.generate_previous_scene_summary(
                        interface, logger, scene_narrative, scene_outline_blueprint
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
    if (
        not Config.CHAPTER_NO_REVISIONS and len(compiled_scene_texts) > 1
    ):  # Only refine if there's more than one scene
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

            response_refinement_messages = interface.safe_generate_text(
                logger,
                refinement_messages,
                Config.MODEL_CHAPTER_ASSEMBLY_REFINER,
                min_word_count=int(
                    get_word_count(full_chapter_text_from_scenes) * 0.75
                ),
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
            interface.build_assistant_query(
                final_chapter_text
            ),  # Start history with the current version
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

                if revision_iterations >= Config.CHAPTER_MAX_REVISIONS:
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

                response_revised_chapter_messages = interface.safe_generate_text(
                    logger,
                    messages_for_this_revision,
                    Config.CHAPTER_REVISION_WRITER_MODEL,
                    min_word_count=int(get_word_count(final_chapter_text) * 0.7),
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


# Example usage (typically called from Write.py)
if __name__ == "__main__":
    # This is for testing purposes only.
    class MockLogger:
        """Mock logger for testing ChapterGenerator."""

        def Log(self, item: str, level: int, stream: bool = False):
            print(f"LOG L{level}: {item}")

        def save_langchain_interaction(self, label: str, messages: list):
            print(f"LANGCHAIN_SAVE: {label}")

    class MockInterface:
        """Mock interface for testing ChapterGenerator."""

        def build_system_query(self, q: str) -> Dict[str, str]:
            return {"role": "system", "content": q}

        def build_user_query(self, q: str) -> Dict[str, str]:
            return {"role": "user", "content": q}

        def build_assistant_query(self, q: str) -> Dict[str, str]:
            return {"role": "assistant", "content": q}

        def get_last_message_text(self, msgs: List[Dict[str, Any]]) -> str:
            return msgs[-1]["content"] if msgs else ""

        def safe_generate_text(
            self, l: MockLogger, m: List[Dict[str, Any]], mo: str, min_word_count: int
        ) -> List[Dict[str, Any]]:
            l.Log(
                f"Mock LLM Call to {mo} with min_words {min_word_count} for ChapterGenerator sub-task.",
                0,
            )
            if mo == Config.MODEL_CHAPTER_ASSEMBLY_REFINER:
                return [
                    *m,
                    {
                        "role": "assistant",
                        "content": "This is the REFINED chapter text after assembly.",
                    },
                ]
            if mo == Config.CHAPTER_REVISION_WRITER_MODEL:
                return [
                    *m,
                    {
                        "role": "assistant",
                        "content": "This is the REVISED chapter text after feedback.",
                    },
                ]
            return [
                *m,
                {
                    "role": "assistant",
                    "content": "Default mock response for chapter sub-task.",
                },
            ]

    # Mock sub-module functions
    _mock_scene_outline_attempt_count = 0

    def mock_generate_detailed_scene_outlines(
        iface: MockInterface,
        log: MockLogger,
        chap_plot: str,
        overall: str,
        chap_num: int,
        prev_sum: Optional[str],
        base_ctx: Optional[str],
    ) -> List[Dict[str, Any]]:
        global _mock_scene_outline_attempt_count
        _mock_scene_outline_attempt_count += 1
        log.Log(
            f"MOCK SceneOutliner called for Ch.{chap_num} (Attempt {_mock_scene_outline_attempt_count})",
            0,
        )
        if (
            chap_num == 1 and _mock_scene_outline_attempt_count < 2
        ):  # Simulate failure on first attempt for chapter 1
            log.Log(
                f"MOCK SceneOutliner: Simulating no scenes on attempt {_mock_scene_outline_attempt_count} for Ch.{chap_num}",
                0,
            )
            return []
        return [
            {
                "scene_number_in_chapter": 1,
                "scene_title": f"Mock Scene {chap_num}.1",
                "key_events_actions": ["Event 1.1"],
            },
            {
                "scene_number_in_chapter": 2,
                "scene_title": f"Mock Scene {chap_num}.2",
                "key_events_actions": ["Event 1.2"],
            },
        ]

    def mock_write_scene_narrative(
        iface: MockInterface,
        log: MockLogger,
        scene_outline: Dict[str, Any],
        overall: str,
        prev_ctx: str,
        chap_num: int,
        scene_num: int,
        base_ctx: Optional[str],
    ) -> str:
        log.Log(f"MOCK SceneGenerator called for {scene_outline['scene_title']}", 0)
        return f"Narrative for {scene_outline['scene_title']}. It included: {scene_outline['key_events_actions'][0]}."

    def mock_generate_previous_scene_summary(
        iface: MockInterface,
        log: MockLogger,
        scene_text: str,
        scene_outline: Dict[str, Any],
    ) -> str:
        log.Log(
            f"MOCK ChapterContext (scene summary) called for {scene_outline['scene_title']}",
            0,
        )
        return f"Summary after {scene_outline['scene_title']}: Key things happened."

    _mock_get_chapter_rating_call_count = 0

    def mock_get_feedback_on_chapter(
        iface: MockInterface, log: MockLogger, chapter_text: str, overall_outline: str
    ) -> str:
        log.Log("MOCK LLMEditor (GetFeedbackOnChapter) called.", 0)
        return "This chapter is okay, but could be more exciting."

    def mock_get_chapter_rating(
        iface: MockInterface, log: MockLogger, chapter_text: str
    ) -> bool:
        log.Log("MOCK LLMEditor (GetChapterRating) called.", 0)
        global _mock_get_chapter_rating_call_count
        _mock_get_chapter_rating_call_count += 1
        return True if _mock_get_chapter_rating_call_count > 1 else False

    # Monkey-patch the imported modules with mocks
    SceneOutliner.generate_detailed_scene_outlines = (
        mock_generate_detailed_scene_outlines
    )
    SceneGenerator.write_scene_narrative = mock_write_scene_narrative
    ChapterContext.generate_previous_scene_summary = (
        mock_generate_previous_scene_summary
    )
    LLMEditor.GetFeedbackOnChapter = mock_get_feedback_on_chapter
    LLMEditor.GetChapterRating = mock_get_chapter_rating

    mock_logger_instance = MockLogger()
    mock_interface_instance = MockInterface()

    # Setup Config for the test
    Config.MODEL_CHAPTER_ASSEMBLY_REFINER = "mock_refiner_model"
    Config.CHAPTER_REVISION_WRITER_MODEL = "mock_chapter_revision_model"
    Config.CHAPTER_NO_REVISIONS = False
    Config.CHAPTER_MIN_REVISIONS = 1
    Config.CHAPTER_MAX_REVISIONS = 1
    Config.SCENE_OUTLINE_GENERATION_MAX_ATTEMPTS = 2  # For testing retry
    Prompts.DEFAULT_SYSTEM_PROMPT = "System prompt for ChapterGenerator test."
    Prompts.CHAPTER_REVISION_PROMPT = "Revise: {_Chapter} with feedback: {_Feedback}"

    print("\n--- Testing generate_chapter_by_scenes (with scene outline retry) ---")
    _mock_get_chapter_rating_call_count = 0
    _mock_scene_outline_attempt_count = 0

    chapter_text_result, scene_outlines_result = generate_chapter_by_scenes(
        mock_interface_instance,
        mock_logger_instance,
        chapter_num=1,  # This chapter will use the retry logic in mock
        total_chapters=3,
        overall_story_outline="A three-chapter saga.",
        current_chapter_plot_outline="The hero starts their journey and faces a small test.",
        previous_chapter_context_summary=None,
        base_story_context="A fantasy world.",
    )

    print("\n--- Final Generated Chapter Text (Mocked) ---")
    print(chapter_text_result)
    print("\n--- Generated Scene Outlines (Mocked) ---")
    for idx, scene in enumerate(scene_outlines_result):
        print(f"Scene {idx+1}: {scene.get('scene_title', 'N/A')}")

    assert "Narrative for Mock Scene 1.1" in chapter_text_result
    assert "Narrative for Mock Scene 1.2" in chapter_text_result
    assert "REFINED" in chapter_text_result
    assert "REVISED" in chapter_text_result
    assert len(scene_outlines_result) == 2
    assert scene_outlines_result[0]["scene_title"] == "Mock Scene 1.1"
    assert _mock_scene_outline_attempt_count == 2  # Ensure retry happened for Ch1

    print("\n--- Testing generate_chapter_by_scenes (no retry needed) ---")
    _mock_get_chapter_rating_call_count = 0
    _mock_scene_outline_attempt_count = 0  # Reset for chapter 2
    chapter_text_result_2, scene_outlines_result_2 = generate_chapter_by_scenes(
        mock_interface_instance,
        mock_logger_instance,
        chapter_num=2,  # This chapter will succeed on first try in mock
        total_chapters=3,
        overall_story_outline="A three-chapter saga.",
        current_chapter_plot_outline="Chapter 2 plot.",
        previous_chapter_context_summary="Context from ch1.",
        base_story_context="A fantasy world.",
    )
    assert _mock_scene_outline_attempt_count == 1  # Ensure no retry for Ch2

    print("\n--- Testing generate_chapter_by_scenes (all retries fail) ---")
    _mock_get_chapter_rating_call_count = 0
    _mock_scene_outline_attempt_count = 0
    # Temporarily make mock fail all attempts for scene outlines for chapter 3
    original_scene_outliner = SceneOutliner.generate_detailed_scene_outlines

    def mock_fail_all_scene_outlines(
        iface, log, plot, overall, chap_num, prev_sum, base_ctx
    ):
        global _mock_scene_outline_attempt_count
        _mock_scene_outline_attempt_count += 1
        log.Log(
            f"MOCK SceneOutliner (FAIL ALL): Ch.{chap_num}, Attempt {_mock_scene_outline_attempt_count}",
            0,
        )
        return []

    SceneOutliner.generate_detailed_scene_outlines = mock_fail_all_scene_outlines

    Config.SCENE_OUTLINE_GENERATION_MAX_ATTEMPTS = 2  # Set for this test

    chapter_text_result_3, scene_outlines_result_3 = generate_chapter_by_scenes(
        mock_interface_instance,
        mock_logger_instance,
        chapter_num=3,
        total_chapters=3,
        overall_story_outline="A three-chapter saga.",
        current_chapter_plot_outline="Plot for chapter 3 that will fail outlining.",
        previous_chapter_context_summary="Context from ch2.",
        base_story_context="A fantasy world.",
    )
    print(f"\nResult for Chapter 3 (expected error): {chapter_text_result_3}")
    print(f"Scene outlines for Chapter 3 (expected empty): {scene_outlines_result_3}")
    assert (
        "Generation Error: No scene outlines were generated for Chapter 3 after 2 attempt(s)"
        in chapter_text_result_3
    )
    assert scene_outlines_result_3 == []
    assert (
        _mock_scene_outline_attempt_count
        == Config.SCENE_OUTLINE_GENERATION_MAX_ATTEMPTS
    )

    # Restore original mock for subsequent tests if any
    SceneOutliner.generate_detailed_scene_outlines = original_scene_outliner
