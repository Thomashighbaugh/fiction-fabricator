# File: AIStoryWriter/Writer/LLMEditor.py
# Purpose: Handles LLM-based feedback, critique, and quality rating for outlines and chapters.

"""
LLM-Powered Editorial Module.

This module provides functions to:
1.  Generate constructive criticism (feedback) on story outlines and individual chapters
    using an LLM.
2.  Obtain a quality rating or completion status (e.g., "IsComplete": true/false)
    for outlines and chapters, also using an LLM.

The feedback and ratings are used in iterative revision loops to improve the
quality of the generated story content. Optimized prompts are crucial for
eliciting useful and actionable responses from the LLMs performing these
editorial tasks.
"""

import Writer.Config as Config
import Writer.Prompts as Prompts
from Writer.Interface.Wrapper import Interface  # LLM interaction
from Writer.PrintUtils import Logger  # Logging
import json
from typing import List, Dict, Any


def GetFeedbackOnOutline(
    interface: Interface, logger: Logger, outline_text: str
) -> str:
    """
    Generates LLM-based feedback on a given story outline.

    Args:
        interface (Interface): The LLM interaction wrapper.
        logger (Logger): The logging instance.
        outline_text (str): The story outline text to be critiqued.

    Returns:
        str: Constructive feedback from the LLM. Returns an error message string
             if feedback generation fails.
    """
    logger.Log("Requesting LLM feedback on the current story outline...", 4)

    if not outline_text or not outline_text.strip():
        logger.Log("Outline text is empty. Cannot get feedback.", 6)
        return "Feedback Error: Outline text was empty."

    try:
        prompt_template = Prompts.OPTIMIZED_CRITIC_OUTLINE_PROMPT
        formatted_prompt = prompt_template.format(_Outline=outline_text)
    except KeyError as e:
        logger.Log(
            f"Formatting error in OPTIMIZED_CRITIC_OUTLINE_PROMPT: Missing key {e}", 7
        )
        return f"Feedback Error: Prompt template key error - {e}."
    except Exception as e:
        logger.Log(f"Unexpected error formatting outline feedback prompt: {e}", 7)
        return f"Feedback Error: Unexpected prompt formatting error - {e}."

    messages: List[Dict[str, Any]] = [
        interface.build_system_query(
            Prompts.DEFAULT_SYSTEM_PROMPT
        ),  # Persona: Discerning editor
        interface.build_user_query(formatted_prompt),
    ]

    try:
        # REVISION_MODEL should be good at analytical tasks and providing constructive criticism.
        response_messages = interface.safe_generate_text(
            logger,
            messages,
            Config.REVISION_MODEL,
            min_word_count=70,  # Expect reasonably detailed feedback
        )

        feedback: str = interface.get_last_message_text(response_messages)

        if not feedback or "Error:" in feedback:
            logger.Log(
                "LLM failed to generate valid feedback for the outline or returned an error.",
                6,
            )
            return (
                f"Feedback Error: LLM failed for outline. Response: {feedback[:100]}..."
            )

        logger.Log("LLM feedback on outline received successfully.", 4)
        return feedback

    except Exception as e:
        logger.Log(
            f"An unexpected critical error occurred during outline feedback generation: {e}",
            7,
        )
        return f"Feedback Error: Unexpected critical error - {e}."


def GetOutlineRating(interface: Interface, logger: Logger, outline_text: str) -> bool:
    """
    Obtains an LLM-based quality rating (IsComplete: true/false) for a story outline.

    Args:
        interface (Interface): The LLM interaction wrapper.
        logger (Logger): The logging instance.
        outline_text (str): The story outline text to be rated.

    Returns:
        bool: True if the LLM deems the outline complete and of high quality,
              False otherwise or if rating fails.
    """
    logger.Log("Requesting LLM rating (completion check) for the story outline...", 4)

    if not outline_text or not outline_text.strip():
        logger.Log(
            "Outline text is empty. Cannot get rating. Defaulting to False (not complete).",
            6,
        )
        return False

    try:
        prompt_template = Prompts.OUTLINE_COMPLETE_PROMPT
        formatted_prompt = prompt_template.format(_Outline=outline_text)
    except KeyError as e:
        logger.Log(f"Formatting error in OUTLINE_COMPLETE_PROMPT: Missing key {e}", 7)
        return False  # Cannot proceed
    except Exception as e:
        logger.Log(f"Unexpected error formatting outline rating prompt: {e}", 7)
        return False

    messages: List[Dict[str, Any]] = [
        # System prompt can guide the LLM on its role as an evaluator
        interface.build_system_query(
            "You are an AI assistant that evaluates content quality and adherence to instructions, responding in precise JSON."
        ),
        interface.build_user_query(formatted_prompt),
    ]

    try:
        # EVAL_MODEL should be reliable for JSON output and boolean checks.
        _response_messages, parsed_json = interface.safe_generate_json(
            logger, messages, Config.EVAL_MODEL, required_attribs=["IsComplete"]
        )

        is_complete = parsed_json.get("IsComplete")

        if isinstance(is_complete, bool):
            logger.Log(
                f"LLM outline completion rating received: IsComplete = {is_complete}", 4
            )
            return is_complete
        else:
            logger.Log(
                f"LLM returned an invalid type for 'IsComplete' (Expected bool, got {type(is_complete)}). Value: '{is_complete}'. Defaulting to False.",
                6,
            )
            return False

    except Exception as e:
        # This catches failures from safe_generate_json (e.g., max retries exceeded) or other issues.
        logger.Log(
            f"An critical error occurred during outline rating: {e}. Defaulting to False.",
            7,
        )
        return False


def GetFeedbackOnChapter(
    interface: Interface, logger: Logger, chapter_text: str, overall_story_outline: str
) -> str:
    """
    Generates LLM-based feedback on a single chapter's text.

    Args:
        interface (Interface): The LLM interaction wrapper.
        logger (Logger): The logging instance.
        chapter_text (str): The text of the chapter to be critiqued.
        overall_story_outline (str): The main story outline for context.

    Returns:
        str: Constructive feedback from the LLM. Returns an error message string
             if feedback generation fails.
    """
    logger.Log(
        f"Requesting LLM feedback on chapter text (length: {len(chapter_text)} chars)...",
        4,
    )

    if not chapter_text or not chapter_text.strip():
        logger.Log("Chapter text is empty. Cannot get feedback.", 6)
        return "Feedback Error: Chapter text was empty."
    if not overall_story_outline or not overall_story_outline.strip():
        logger.Log(
            "Overall story outline is empty. Context for chapter feedback is missing.",
            6,
        )
        # Proceed but feedback might be less effective
        overall_story_outline = "Overall story outline not provided for context."

    try:
        prompt_template = Prompts.OPTIMIZED_CRITIC_CHAPTER_PROMPT
        formatted_prompt = prompt_template.format(
            _ChapterText=chapter_text,  # Corrected placeholder from _Chapter to _ChapterText
            _OverallStoryOutline=overall_story_outline,
        )
    except KeyError as e:
        logger.Log(
            f"Formatting error in OPTIMIZED_CRITIC_CHAPTER_PROMPT: Missing key {e}", 7
        )
        return f"Feedback Error: Prompt template key error - {e}."
    except Exception as e:
        logger.Log(f"Unexpected error formatting chapter feedback prompt: {e}", 7)
        return f"Feedback Error: Unexpected prompt formatting error - {e}."

    messages: List[Dict[str, Any]] = [
        interface.build_system_query(
            Prompts.DEFAULT_SYSTEM_PROMPT
        ),  # Persona: Experienced manuscript editor
        interface.build_user_query(formatted_prompt),
    ]

    try:
        response_messages = interface.safe_generate_text(
            logger,
            messages,
            Config.REVISION_MODEL,
            min_word_count=100,  # Expect detailed chapter feedback
        )

        feedback: str = interface.get_last_message_text(response_messages)

        if not feedback or "Error:" in feedback:
            logger.Log(
                "LLM failed to generate valid feedback for the chapter or returned an error.",
                6,
            )
            return (
                f"Feedback Error: LLM failed for chapter. Response: {feedback[:100]}..."
            )

        logger.Log("LLM feedback on chapter received successfully.", 4)
        return feedback

    except Exception as e:
        logger.Log(
            f"An unexpected critical error occurred during chapter feedback generation: {e}",
            7,
        )
        return f"Feedback Error: Unexpected critical error - {e}."


def GetChapterRating(interface: Interface, logger: Logger, chapter_text: str) -> bool:
    """
    Obtains an LLM-based quality rating (IsComplete: true/false) for a chapter.

    Args:
        interface (Interface): The LLM interaction wrapper.
        logger (Logger): The logging instance.
        chapter_text (str): The chapter text to be rated.

    Returns:
        bool: True if the LLM deems the chapter complete and of high quality,
              False otherwise or if rating fails.
    """
    logger.Log(
        f"Requesting LLM rating (completion check) for chapter text (length: {len(chapter_text)} chars)...",
        4,
    )

    if not chapter_text or not chapter_text.strip():
        logger.Log(
            "Chapter text is empty. Cannot get rating. Defaulting to False (not complete).",
            6,
        )
        return False

    try:
        prompt_template = Prompts.CHAPTER_COMPLETE_PROMPT
        formatted_prompt = prompt_template.format(
            _Chapter=chapter_text
        )  # Corrected placeholder
    except KeyError as e:
        logger.Log(f"Formatting error in CHAPTER_COMPLETE_PROMPT: Missing key {e}", 7)
        return False  # Cannot proceed
    except Exception as e:
        logger.Log(f"Unexpected error formatting chapter rating prompt: {e}", 7)
        return False

    messages: List[Dict[str, Any]] = [
        interface.build_system_query(
            "You are an AI assistant that evaluates content quality and adherence to instructions, responding in precise JSON."
        ),
        interface.build_user_query(formatted_prompt),
    ]

    try:
        _response_messages, parsed_json = interface.safe_generate_json(
            logger, messages, Config.EVAL_MODEL, required_attribs=["IsComplete"]
        )

        is_complete = parsed_json.get("IsComplete")

        if isinstance(is_complete, bool):
            logger.Log(
                f"LLM chapter completion rating received: IsComplete = {is_complete}", 4
            )
            return is_complete
        else:
            logger.Log(
                f"LLM returned an invalid type for 'IsComplete' (Expected bool, got {type(is_complete)}). Value: '{is_complete}'. Defaulting to False.",
                6,
            )
            return False

    except Exception as e:
        logger.Log(
            f"An critical error occurred during chapter rating: {e}. Defaulting to False.",
            7,
        )
        return False


# Example usage (typically called from OutlineGenerator.py or ChapterGenerator.py)
if __name__ == "__main__":
    # This is for testing purposes only.
    class MockLogger:
        def Log(self, item: str, level: int, stream: bool = False):
            print(f"LOG L{level}: {item}")

        def save_langchain_interaction(self, label: str, messages: list):
            print(f"LANGCHAIN_SAVE: {label}")

    class MockInterface:
        def __init__(self):
            self.rating_call_count = 0

        def build_system_query(self, q: str):
            return {"role": "system", "content": q}

        def build_user_query(self, q: str):
            return {"role": "user", "content": q}

        def get_last_message_text(self, msgs):
            return msgs[-1]["content"] if msgs else ""

        def safe_generate_text(self, l, m, mo, min_word_count):
            print(
                f"Mock LLM Call (safe_generate_text) to {mo} for feedback. Min words: {min_word_count}"
            )
            if "OPTIMIZED_CRITIC_OUTLINE_PROMPT" in m[-1]["content"]:
                return [
                    *m,
                    {
                        "role": "assistant",
                        "content": "Outline Feedback: Needs more plot twists.",
                    },
                ]
            if "OPTIMIZED_CRITIC_CHAPTER_PROMPT" in m[-1]["content"]:
                return [
                    *m,
                    {
                        "role": "assistant",
                        "content": "Chapter Feedback: Dialogue is a bit stiff.",
                    },
                ]
            return [*m, {"role": "assistant", "content": "Generic mock feedback."}]

        def safe_generate_json(self, l, m, mo, required_attribs):
            self.rating_call_count += 1
            print(
                f"Mock LLM Call (safe_generate_json) to {mo} for rating. Required: {required_attribs}"
            )
            is_complete_response = False
            if "OUTLINE_COMPLETE_PROMPT" in m[-1]["content"]:
                is_complete_response = (
                    True if self.rating_call_count > 1 else False
                )  # Simulate needs one revision
            elif "CHAPTER_COMPLETE_PROMPT" in m[-1]["content"]:
                is_complete_response = (
                    True if self.rating_call_count > 2 else False
                )  # Simulate needs two revisions

            json_content = json.dumps(
                {"IsComplete": is_complete_response, "extra_key": "value"}
            )
            return (
                [*m, {"role": "assistant", "content": json_content}],
                json.loads(json_content),
            )

    mock_logger = MockLogger()
    mock_interface = MockInterface()

    Config.REVISION_MODEL = "mock_revision_model"
    Config.EVAL_MODEL = "mock_eval_model_for_editor"
    Prompts.DEFAULT_SYSTEM_PROMPT = "System prompt for LLMEditor test."
    # Simplified prompts for testing placeholders
    Prompts.OPTIMIZED_CRITIC_OUTLINE_PROMPT = "Critique Outline: {_Outline}"
    Prompts.OUTLINE_COMPLETE_PROMPT = "Rate Outline: {_Outline}"
    Prompts.OPTIMIZED_CRITIC_CHAPTER_PROMPT = "Critique Chapter: {_ChapterText} with Outline: {_OverallStoryOutline}"  # Corrected placeholder
    Prompts.CHAPTER_COMPLETE_PROMPT = (
        "Rate Chapter: {_Chapter}"  # Corrected placeholder
    )

    print("--- Testing GetFeedbackOnOutline ---")
    outline_fb = GetFeedbackOnOutline(
        mock_interface, mock_logger, "Chapter 1: A start. Chapter 2: An end."
    )
    print(f"Outline Feedback: {outline_fb}\n")
    assert "plot twists" in outline_fb

    print("--- Testing GetOutlineRating (simulating one revision needed) ---")
    mock_interface.rating_call_count = 0  # Reset for this specific test sequence
    rating1_false = GetOutlineRating(
        mock_interface, mock_logger, "Initial Outline Draft"
    )
    print(f"Outline Rating (1st call): {rating1_false}")
    assert rating1_false == False
    rating1_true = GetOutlineRating(
        mock_interface, mock_logger, "Revised Outline Draft"
    )
    print(f"Outline Rating (2nd call): {rating1_true}")
    assert rating1_true == True

    print("\n--- Testing GetFeedbackOnChapter ---")
    chapter_fb = GetFeedbackOnChapter(
        mock_interface,
        mock_logger,
        "He said, 'Hello.' She said, 'Hi.'",
        "A short story outline.",
    )
    print(f"Chapter Feedback: {chapter_fb}\n")
    assert "Dialogue is a bit stiff" in chapter_fb

    print("--- Testing GetChapterRating (simulating two revisions needed) ---")
    mock_interface.rating_call_count = 0  # Reset for this specific test sequence
    chap_rating_false1 = GetChapterRating(
        mock_interface, mock_logger, "First chapter draft."
    )
    print(f"Chapter Rating (1st call): {chap_rating_false1}")
    assert chap_rating_false1 == False
    chap_rating_false2 = GetChapterRating(
        mock_interface, mock_logger, "Second chapter draft."
    )
    print(f"Chapter Rating (2nd call): {chap_rating_false2}")
    assert chap_rating_false2 == False
    chap_rating_true = GetChapterRating(
        mock_interface, mock_logger, "Third chapter draft."
    )
    print(f"Chapter Rating (3rd call): {chap_rating_true}")
    assert chap_rating_true == True

    print("\n--- Testing with empty inputs ---")
    empty_outline_fb = GetFeedbackOnOutline(mock_interface, mock_logger, "")
    print(f"Empty Outline Feedback: {empty_outline_fb}")
    assert "Error:" in empty_outline_fb
    empty_outline_rating = GetOutlineRating(mock_interface, mock_logger, "")
    print(f"Empty Outline Rating: {empty_outline_rating}")
    assert empty_outline_rating == False
