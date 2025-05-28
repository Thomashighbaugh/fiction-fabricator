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
from Writer.Interface.Wrapper import Interface  # LLM interaction
from Writer.PrintUtils import Logger  # Logging
from typing import Optional, Dict, Any, List


def generate_previous_chapter_summary(
    interface: Interface,
    logger: Logger,
    completed_chapter_text: str,
    overall_story_outline: str,
    chapter_number_of_completed_chapter: int,
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
        ),  # Guide LLM to be a good summarizer/analyst
        interface.build_user_query(formatted_prompt),
    ]

    try:
        # MODEL_CHAPTER_CONTEXT_SUMMARIZER should be efficient but good at summarization.
        response_messages = interface.safe_generate_text(
            logger,
            messages,
            Config.MODEL_CHAPTER_CONTEXT_SUMMARIZER,
            min_word_count=50,  # A summary should be reasonably detailed but concise.
        )

        context_summary: str = interface.get_last_message_text(response_messages)

        if (
            not context_summary or "Error:" in context_summary
        ):  # Check for errors from safe_generate_text or LLM
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

    # Option 1: Non-LLM based extraction (Simpler, faster, less nuanced)
    # This could involve taking the last N sentences or looking for keywords from the scene_outline's "Transition_Out_Hook".
    # Example non-LLM approach:
    # last_sentences = " ".join(completed_scene_text.split('.')[-3:]) # very naive last few sentences
    # transition_hook_info = completed_scene_outline.get("transition_out_hook", "Scene concluded.")
    # simple_summary = f"The scene '{scene_title}' just ended. Key concluding elements: {transition_hook_info}. Last few words: \"...{last_sentences[-100:]}\"."
    # logger.Log(f"Non-LLM previous scene summary for '{scene_title}' generated.", 2)
    # return simple_summary

    # Option 2: LLM-based (More nuanced but slower and costs tokens)
    try:
        prompt_template = Prompts.OPTIMIZED_PREVIOUS_SCENE_SUMMARY_FOR_CONTEXT
        # Convert dict to string for the prompt if necessary, or format it nicely
        formatted_prompt = prompt_template.format(
            _CompletedSceneText=completed_scene_text,
            _CurrentSceneOutline=json.dumps(
                completed_scene_outline, indent=2
            ),  # Pass outline as JSON string
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
        ),  # Could be a more specialized "summarizer" persona
        interface.build_user_query(formatted_prompt),
    ]

    try:
        # Use a fast and efficient model for this very short summary. EVAL_MODEL might be suitable.
        response_messages = interface.safe_generate_text(
            logger,
            messages,
            Config.EVAL_MODEL,  # Or a specific MODEL_SCENE_CONTEXT_SUMMARIZER
            min_word_count=10,  # Expect a very short summary
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
                f"Mock LLM Call to {mo} with min_words {min_word_count} for context summary."
            )
            if "OPTIMIZED_PREVIOUS_CHAPTER_SUMMARY_FOR_CONTEXT" in m[-1]["content"]:
                return [
                    *m,
                    {
                        "role": "assistant",
                        "content": "Chapter Summary: The hero found the map and decided to go north.",
                    },
                ]
            if "OPTIMIZED_PREVIOUS_SCENE_SUMMARY_FOR_CONTEXT" in m[-1]["content"]:
                return [
                    *m,
                    {
                        "role": "assistant",
                        "content": "Scene Summary: Alice picked up the red key.",
                    },
                ]
            return [*m, {"role": "assistant", "content": "Mocked summary."}]

    mock_logger = MockLogger()
    mock_interface = MockInterface()

    Config.MODEL_CHAPTER_CONTEXT_SUMMARIZER = "mock_chapter_summarizer_model"
    Config.EVAL_MODEL = "mock_scene_summarizer_model"  # Used for scene summary
    Prompts.DEFAULT_SYSTEM_PROMPT = "You are a summarizer bot for testing."

    print("--- Testing generate_previous_chapter_summary ---")
    chapter_text = "The long day ended. Sir Reginald, weary from his travels, finally reached the Dragon's Tooth pass. He knew the journey ahead would be perilous. He unsheathed his sword, its polished surface reflecting the dim twilight. 'For the kingdom,' he muttered, and stepped into the shadows."
    overall_outline_sample = (
        "Chapter 1: Intro. Chapter 2: The Pass. Chapter 3: The Lair."
    )
    chapter_summary = generate_previous_chapter_summary(
        mock_interface, mock_logger, chapter_text, overall_outline_sample, 1
    )
    print(f"Chapter Summary Result:\n{chapter_summary}\n")

    print("--- Testing generate_previous_scene_summary ---")
    scene_text = "Alice entered the dusty room. A single red key glinted on the table. She picked it up, a sense of foreboding washing over her. The door creaked behind her."
    scene_outline_sample = {
        "scene_title": "The Red Key",
        "key_events_actions": ["Alice finds red key"],
        "transition_out_hook": "Alice feels uneasy as she holds the key.",
    }
    scene_summary = generate_previous_scene_summary(
        mock_interface, mock_logger, scene_text, scene_outline_sample
    )
    print(f"Scene Summary Result:\n{scene_summary}\n")

    print("--- Test with empty chapter text ---")
    empty_chapter_summary = generate_previous_chapter_summary(
        mock_interface, mock_logger, "", overall_outline_sample, 2
    )
    print(f"Empty Chapter Summary Result:\n{empty_chapter_summary}\n")

    print("--- Test with empty scene text ---")
    empty_scene_summary = generate_previous_scene_summary(
        mock_interface, mock_logger, "", scene_outline_sample
    )
    print(f"Empty Scene Summary Result:\n{empty_scene_summary}\n")
