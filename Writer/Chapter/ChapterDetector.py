# File: Writer/Chapter/ChapterDetector.py
# Purpose: Detects the number of chapters from a given story outline using an LLM.

"""
Chapter Detection Module.

This module uses an LLM to analyze a story outline and determine the
total number of chapters it describes. It's designed to parse structured
outlines where chapters are explicitly mentioned (e.g., "Chapter 1:", "## Chapter Two").
"""

import Writer.Config as Config
import Writer.Prompts as Prompts
from Writer.Interface.Wrapper import Interface  # LLM interaction
from Writer.PrintUtils import Logger  # Logging
import json
from typing import List, Dict, Any


def llm_count_chapters(
    interface: Interface, logger: Logger, overall_story_outline: str
) -> int:
    """
    Uses an LLM to count the number of chapters in a given story outline.

    Args:
        interface (Interface): The LLM interaction wrapper instance.
        logger (Logger): The logging instance.
        overall_story_outline (str): The story outline text to analyze.

    Returns:
        int: The detected number of chapters. Returns 0 if detection fails
             or if the outline is unclear, or if the LLM returns an invalid count.
    """
    logger.Log("Attempting to detect number of chapters from outline using LLM...", 3)

    if not overall_story_outline or not overall_story_outline.strip():
        logger.Log("Overall story outline is empty. Cannot detect chapters.", 6)
        return 0

    try:
        prompt_template = Prompts.CHAPTER_COUNT_PROMPT
        formatted_prompt = prompt_template.format(_Outline=overall_story_outline)
    except KeyError as e:
        logger.Log(f"Formatting error in CHAPTER_COUNT_PROMPT: Missing key {e}", 7)
        return 0  # Cannot proceed if prompt is broken
    except Exception as e:
        logger.Log(f"Unexpected error formatting chapter count prompt: {e}", 7)
        return 0

    messages: List[Dict[str, Any]] = [
        # System prompt might not be strictly necessary for such a direct task,
        # but can help ensure the LLM focuses on instruction following.
        interface.build_system_query(
            "You are an AI assistant that precisely follows formatting instructions and extracts specific information from text."
        ),
        interface.build_user_query(formatted_prompt),
    ]

    try:
        # Use SafeGenerateJSON to ensure a valid JSON response with the "TotalChapters" field.
        # EVAL_MODEL is typically good for structured data extraction and instruction following.
        response_messages, parsed_json = interface.safe_generate_json(
            logger, messages, Config.EVAL_MODEL, required_attribs=["TotalChapters"]
        )

        total_chapters_val = parsed_json.get("TotalChapters")

        if isinstance(total_chapters_val, int) and total_chapters_val >= 0:
            logger.Log(f"LLM detected {total_chapters_val} chapters in the outline.", 4)
            if (
                total_chapters_val == 0 and len(overall_story_outline) > 100
            ):  # Arbitrary length check
                logger.Log(
                    f"LLM reported 0 chapters, but outline has content. This might indicate an issue with the outline format or LLM interpretation.",
                    6,
                )
            return total_chapters_val
        else:
            logger.Log(
                f"LLM returned an invalid or non-integer value for TotalChapters: '{total_chapters_val}'. Defaulting to 0 chapters.",
                6,
            )
            return 0

    except Exception as e:
        # This might catch errors from safe_generate_json if it fails all retries,
        # or other unexpected issues.
        logger.Log(
            f"An critical error occurred during LLM chapter count detection: {e}", 7
        )
        # Consider logging traceback for debug: import traceback; logger.Log(traceback.format_exc(), 7)
        return 0


# Example usage (typically called from Write.py)
if __name__ == "__main__":
    # This is for testing purposes only.
    class MockLogger:
        def Log(self, item: str, level: int, stream: bool = False):
            print(f"LOG L{level}: {item}")

        def save_langchain_interaction(self, label: str, messages: list):
            print(f"LANGCHAIN_SAVE: {label}")

    class MockInterface:
        def __init__(self):
            self.call_count = 0

        def build_system_query(self, q: str):
            return {"role": "system", "content": q}

        def build_user_query(self, q: str):
            return {"role": "user", "content": q}

        def get_last_message_text(self, msgs):
            return msgs[-1]["content"] if msgs else ""

        def safe_generate_json(self, l, m, mo, required_attribs):
            self.call_count += 1
            print(
                f"Mock LLM JSON Call ({self.call_count}) to {mo} for chapter count. Required: {required_attribs}"
            )
            # Simulate different LLM responses
            if "valid outline" in m[-1]["content"].lower():
                return (
                    [
                        *m,
                        {
                            "role": "assistant",
                            "content": json.dumps({"TotalChapters": 5}),
                        },
                    ],
                    {"TotalChapters": 5},
                )
            elif "empty outline" in m[-1]["content"].lower():
                return (
                    [
                        *m,
                        {
                            "role": "assistant",
                            "content": json.dumps({"TotalChapters": 0}),
                        },
                    ],
                    {"TotalChapters": 0},
                )
            elif (
                "malformed json" in m[-1]["content"].lower()
            ):  # Test SafeGenerateJSON's retry
                if self.call_count % 2 == 1:  # Fail first time
                    raise json.JSONDecodeError(
                        "Simulated bad JSON", '{"TotalChapters": "bad"', 0
                    )
                else:  # Succeed second time
                    return (
                        [
                            *m,
                            {
                                "role": "assistant",
                                "content": json.dumps({"TotalChapters": 3}),
                            },
                        ],
                        {"TotalChapters": 3},
                    )
            elif "missing key" in m[-1]["content"].lower():
                return (
                    [*m, {"role": "assistant", "content": json.dumps({"Chapters": 2})}],
                    {"Chapters": 2},
                )  # Missing "TotalChapters"
            else:  # Default for unrecognized test cases
                return (
                    [
                        *m,
                        {
                            "role": "assistant",
                            "content": json.dumps({"TotalChapters": 1}),
                        },
                    ],
                    {"TotalChapters": 1},
                )

    mock_logger = MockLogger()
    mock_interface = MockInterface()

    # Ensure Config has a value for the model
    Config.EVAL_MODEL = "mock_eval_model_for_chapter_count"
    Prompts.CHAPTER_COUNT_PROMPT = (
        "Outline: {_Outline} -> Count chapters."  # Simplified for test readability
    )

    print("--- Testing llm_count_chapters ---")

    test_outline_valid = "Chapter 1: The Start.\nChapter 2: The Middle.\nChapter 3: More.\nChapter 4: Almost.\nChapter 5: The End. This is a valid outline."
    count_valid = llm_count_chapters(mock_interface, mock_logger, test_outline_valid)
    print(f"Test with valid outline: Detected {count_valid} chapters (Expected ~5)\n")

    test_outline_empty_text = "This is an empty outline with no chapter markers."
    count_empty_text = llm_count_chapters(
        mock_interface, mock_logger, test_outline_empty_text
    )
    print(
        f"Test with outline having no chapter markers: Detected {count_empty_text} chapters (Expected 0 or 1 based on mock)\n"
    )

    test_outline_none = ""
    count_none = llm_count_chapters(mock_interface, mock_logger, test_outline_none)
    print(
        f"Test with empty string outline: Detected {count_none} chapters (Expected 0)\n"
    )

    mock_interface.call_count = 0  # Reset for this specific test
    test_outline_malformed_json = (
        "This outline will cause a malformed json response from mock initially."
    )
    count_malformed = llm_count_chapters(
        mock_interface, mock_logger, test_outline_malformed_json
    )
    print(
        f"Test with simulated malformed JSON retry: Detected {count_malformed} chapters (Expected 3 after retry)\n"
    )

    mock_interface.call_count = 0
    test_outline_missing_key = (
        "This outline will cause a missing key in JSON from mock."
    )
    # This will now raise an exception in safe_generate_json if retries fail, or return default if it can't fix it.
    # The test mock for safe_generate_json would need to be more sophisticated to simulate safe_generate_json's internal retries for missing keys.
    # For now, we expect it to fail or return 0 due to the strict `required_attribs`.
    try:
        count_missing_key = llm_count_chapters(
            mock_interface, mock_logger, test_outline_missing_key
        )
        print(
            f"Test with simulated missing key JSON: Detected {count_missing_key} chapters (Expected 0 or error)\n"
        )
    except Exception as e:
        print(
            f"Test with simulated missing key JSON resulted in error as expected: {e}\n"
        )
