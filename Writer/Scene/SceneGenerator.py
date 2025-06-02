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
from Writer.Interface.Wrapper import Interface  # LLM interaction
from Writer.PrintUtils import Logger  # Logging
from Writer.Statistics import get_word_count  # For logging word count
from typing import Dict, Any, List, Optional
import re  # For mock response in test block


def write_scene_narrative(
    interface: Interface,
    logger: Logger,
    scene_detailed_outline: Dict[str, Any],
    overall_story_outline: str,
    previous_scene_or_chapter_context_summary: str,
    chapter_number: int,
    scene_number_in_chapter: int,
    base_story_context: Optional[str],
) -> str:
    """
    Generates the full narrative text for a single scene based on its blueprint and context.

    Args:
        interface (Interface): The LLM interaction wrapper.
        logger (Logger): The logging instance.
        scene_detailed_outline (Dict[str, Any]): The detailed blueprint for the current scene.
            Expected keys are defined by OPTIMIZED_CHAPTER_TO_SCENES_BREAKDOWN prompt.
        overall_story_outline (str): The main outline of the entire story.
        previous_scene_or_chapter_context_summary (str): Contextual summary from the
                                                         end of the previous scene or chapter.
        chapter_number (int): The current chapter number.
        scene_number_in_chapter (int): The sequence number of this scene within the chapter.
        base_story_context (Optional[str]): Overarching story context or user instructions.

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

        # Prepare context for the prompt, ensuring all placeholders are filled
        # Convert list/dict fields from scene_detailed_outline to string representations for the prompt
        key_events_str = "\n- ".join(
            scene_detailed_outline.get(
                "key_events_actions", ["No specific key events listed."]
            )
        )
        if key_events_str and not key_events_str.startswith("\n- "):
            key_events_str = "- " + key_events_str  # Ensure list format

        dialogue_points_str = "\n- ".join(
            scene_detailed_outline.get(
                "dialogue_points", ["No specific dialogue points listed."]
            )
        )
        if dialogue_points_str and not dialogue_points_str.startswith("\n- "):
            dialogue_points_str = "- " + dialogue_points_str

        characters_present_str = ", ".join(
            scene_detailed_outline.get("characters_present", ["Unknown characters"])
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
            SCENE_NARRATIVE_MIN_WORDS=Config.SCENE_NARRATIVE_MIN_WORDS,  # Pass from Config
        )
    except KeyError as e:
        logger.Log(
            f"Formatting error in OPTIMIZED_SCENE_NARRATIVE_GENERATION prompt for '{scene_title}': Missing key {e}",
            7,
        )
        return f"Scene Generation Error: Prompt template key error for '{scene_title}' - {e}."
    except Exception as e:  # Catch any other formatting errors
        logger.Log(
            f"Unexpected error formatting scene narrative prompt for '{scene_title}': {e}",
            7,
        )
        return f"Scene Generation Error: Unexpected prompt formatting error for '{scene_title}' - {e}."

    messages: List[Dict[str, Any]] = [
        interface.build_system_query(
            Prompts.DEFAULT_SYSTEM_PROMPT
        ),  # Expert creative writer persona
        interface.build_user_query(formatted_prompt),
    ]

    try:
        # MODEL_SCENE_NARRATIVE_GENERATOR should be a strong creative writing model.
        logger.Log(
            f"Requesting LLM to write narrative text for Scene '{scene_title}' (C{chapter_number}.S{scene_number_in_chapter}).",
            4,
        )
        response_messages = interface.safe_generate_text(
            logger,
            messages,
            Config.MODEL_SCENE_NARRATIVE_GENERATOR,
            min_word_count=Config.SCENE_NARRATIVE_MIN_WORDS,
        )

        scene_narrative_text: str = interface.get_last_message_text(response_messages)

        if (
            not scene_narrative_text or "Error:" in scene_narrative_text
        ):  # Check for errors from safe_generate_text or LLM
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
        # import traceback; logger.Log(traceback.format_exc(), 7)
        return f"Scene Generation Error: Unexpected critical error for '{scene_title}' - {e}."


# Example usage (typically called from ChapterGenerator.py)
if __name__ == "__main__":
    # This is for testing purposes only.
    class MockLogger:
        def Log(self, item: str, level: int, stream: bool = False):
            print(f"LOG L{level}: {item}")

        def save_langchain_interaction(self, label: str, messages: list):
            print(f"LANGCHAIN_SAVE: {label}")

    class MockInterface:
        def build_system_query(self, q: str):
            return {"role": "system", "content": q}

        def build_user_query(self, q: str):
            return {"role": "user", "content": q}

        def get_last_message_text(self, msgs):
            return msgs[-1]["content"] if msgs else ""

        def safe_generate_text(self, l, m, mo, min_word_count):
            print(
                f"Mock LLM Call (safe_generate_text) to {mo} with min_words {min_word_count} for scene narrative."
            )
            # Simulate LLM generating scene text based on the prompt
            # Extract some info from the prompt to make the mock response slightly relevant
            user_prompt_content = m[-1]["content"]

            # Try to extract scene title dynamically for better mock response
            # This regex is specific to the format of Prompts.OPTIMIZED_SCENE_NARRATIVE_GENERATION
            title_match = None
            if (
                'Title**: "' in user_prompt_content
            ):  # Looking for "Title**: "{_SceneTitle}""
                match_simple = re.search(r"Title\*\*: \"(.*?)\"", user_prompt_content)
                if match_simple:
                    title_match = match_simple

            mock_title = (
                title_match.group(1)
                if title_match
                else "Mocked Scene Title from SceneGenerator Test"
            )

            return [
                *m,
                {
                    "role": "assistant",
                    "content": f"This is the mock narrative for scene '{mock_title}'. It describes exciting events and character interactions, fulfilling all requirements with vivid prose. The minimum word count of {min_word_count} is definitely met by this sentence and several more that follow, ensuring a complete and satisfying scene.",
                },
            ]

    mock_logger = MockLogger()
    mock_interface = MockInterface()

    # Setup necessary Config values for the test
    Config.MODEL_SCENE_NARRATIVE_GENERATOR = "mock_scene_narrative_model"
    Config.SCENE_NARRATIVE_MIN_WORDS = 50  # Lower for testing
    Prompts.DEFAULT_SYSTEM_PROMPT = "You are a scene writer bot for testing."
    # Simplified prompt for testing the format call
    Prompts.OPTIMIZED_SCENE_NARRATIVE_GENERATION = """
    Overall: {_OverallStoryOutline}
    Previous: {_PreviousSceneContextSummary}
    C.{_ChapterNumber} S.{_SceneNumberInChapter}
    **Scene Blueprint:**
    -   **Title**: "{_SceneTitle}"
    -   Setting: {_SceneSettingDescription}
    -   Chars/Goals: {_SceneCharactersPresentAndGoals}
    -   Events: {_SceneKeyEvents}
    -   Dialogue: {_SceneDialogueHighlights}
    -   Pacing: {_ScenePacingNote}
    -   Tone: {_SceneTone}
    -   Purpose: {_ScenePurposeInChapter}
    -   Transition: {_SceneTransitionOutHook}
    BaseCtx: {_BaseStoryContext}
    MinWords: {SCENE_NARRATIVE_MIN_WORDS}
    Write the scene.
    """

    print("--- Testing write_scene_narrative ---")

    sample_scene_outline = {
        "scene_title": "The Confrontation on the Clifftop",  # Made title more specific
        "setting_description": "A windswept clifftop at dawn.",
        "characters_present": ["Hero", "Villain"],
        "character_goals_moods": "Hero: To get answers. Villain: To intimidate.",
        "key_events_actions": [
            "Tense dialogue exchange.",
            "A sudden reveal.",
            "Hero makes a difficult choice.",
        ],
        "dialogue_points": [
            "Villain: 'You were always a fool.'",
            "Hero: 'I won't back down.'",
        ],
        "pacing_note": "Starts slow and tense, builds to a dramatic peak.",
        "tone": "Dramatic, suspenseful.",
        "purpose_in_chapter": "Forces the hero to confront the villain's ideology.",
        "transition_out_hook": "Hero leaves, pondering the villain's words.",
    }
    overall_story = "A hero's journey."
    prev_context = "The hero had just learned the villain's location."
    base_ctx = "The world is harsh and unforgiving."
    test_chapter_num = 5
    test_scene_num = 3

    scene_text = write_scene_narrative(
        mock_interface,
        mock_logger,
        sample_scene_outline,
        overall_story,
        prev_context,
        chapter_number=test_chapter_num,
        scene_number_in_chapter=test_scene_num,
        base_story_context=base_ctx,
    )

    print(f"\nGenerated Scene Narrative:\n{scene_text}\n")
    assert (
        sample_scene_outline["scene_title"] in scene_text
    )  # Check if mock used the title
    assert get_word_count(scene_text) >= 10  # A very basic check on mock output

    print("--- Test with missing scene outline ---")
    error_text_missing_outline = write_scene_narrative(
        mock_interface, mock_logger, {}, overall_story, prev_context, 6, 1, base_ctx
    )
    print(f"Result for missing outline: {error_text_missing_outline}\n")
    assert "Error: Blueprint" in error_text_missing_outline
