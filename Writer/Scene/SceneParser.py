# File: Writer/Scene/SceneParser.py
# Purpose: Utilities for parsing structured scene data, primarily from LLM responses.

"""
Scene Data Parsing Utilities.

This module provides functions to parse structured scene data,
typically from LLM responses, into Python-usable formats (e.g., lists of
dictionaries). It includes error handling for malformed inputs and
can attempt LLM-based correction for invalid JSON.
"""

import json
import Writer.Config as Config
import Writer.Prompts as Prompts  # For JSON_PARSE_ERROR prompt
from Writer.Interface.Wrapper import Interface  # LLM interaction
from Writer.PrintUtils import Logger  # Logging
from typing import List, Dict, Any, Optional
import re  # For more robust markdown parsing if needed in the future
import datetime


def parse_llm_scene_outlines_response(
    interface: Interface,
    logger: Logger,
    llm_response_text: str,
    model_to_use_for_correction: Optional[
        str
    ] = None,  # Model for LLM-based JSON correction
) -> List[Dict[str, Any]]:
    """
    Parses an LLM's text response, expecting it to contain a list of scene outlines.
    Primarily attempts to parse as JSON. If that fails, it can optionally try
    LLM-based correction or more rudimentary parsing if implemented.

    Args:
        interface (Interface): The LLM interaction wrapper instance.
        logger (Logger): The logging instance.
        llm_response_text (str): The raw text response from an LLM, expected to be
                                 a JSON list of scene outline objects.
        model_to_use_for_correction (Optional[str]): The model URI to use if
                                                     LLM-based JSON correction is attempted.
                                                     Defaults to Config.EVAL_MODEL.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dictionary
                              represents a scene outline. Returns an empty list if
                              parsing fails definitively.
    """
    logger.Log("Attempting to parse LLM response for scene outlines...", 3)

    if not llm_response_text or not llm_response_text.strip():
        logger.Log("LLM response text for scene outlines is empty. Cannot parse.", 6)
        return []

    if model_to_use_for_correction is None:
        model_to_use_for_correction = Config.EVAL_MODEL

    cleaned_response_text = llm_response_text.strip()

    # Attempt 1: Direct JSON parsing (most common and preferred)
    # Clean common markdown artifacts around JSON
    if cleaned_response_text.startswith("```json"):
        cleaned_response_text = cleaned_response_text[7:]
    if cleaned_response_text.endswith("```"):
        cleaned_response_text = cleaned_response_text[:-3]
    cleaned_response_text = cleaned_response_text.strip()

    try:
        if (
            not cleaned_response_text
        ):  # Handle case where cleaning results in empty string
            raise json.JSONDecodeError("Cleaned response text is empty.", "", 0)

        scene_outlines_list = json.loads(cleaned_response_text)

        if isinstance(scene_outlines_list, list) and all(
            isinstance(item, dict) for item in scene_outlines_list
        ):
            if scene_outlines_list and not all(
                "scene_title" in item or "key_events_actions" in item
                for item in scene_outlines_list
            ):
                logger.Log(
                    "Parsed JSON list items do not appear to be scene outlines (missing common keys).",
                    5,
                )
            logger.Log(
                f"Successfully parsed {len(scene_outlines_list)} scene outlines from JSON.",
                4,
            )
            return scene_outlines_list
        else:
            logger.Log(
                f"Parsed JSON is not a list of dictionaries as expected for scene outlines. Type: {type(scene_outlines_list)}",
                6,
            )
            raise ValueError(
                "Parsed JSON not in expected list-of-dictionaries format for scene outlines."
            )

    except (json.JSONDecodeError, ValueError) as e:
        logger.Log(
            f"Initial JSON parse failed for scene outlines: {e}. LLM response snippet: '{llm_response_text[:200]}...'",
            6,
        )

        # Attempt 2: LLM-based correction if initial JSON parsing fails
        logger.Log(
            f"Attempting LLM-based correction for malformed scene outline JSON using model: {model_to_use_for_correction}",
            5,
        )

        # Check if the error message or original text indicates Python-style string concatenation
        correction_prompt_user_text = (
            f"The following text was intended to be a valid JSON list, where each item is an object "
            f"representing a scene outline (with keys like 'scene_title', 'key_events_actions', etc.). "
            f"However, it's malformed or not in the correct structure. "
            f"Please correct it and provide ONLY the valid JSON list of scene outline objects. "
            f"Original text:\n\n{llm_response_text}"
        )

        if (
            "Unterminated string starting at" in str(e)
            or "Expecting ',' delimiter" in str(e)
            or (
                cleaned_response_text
                and "+" in cleaned_response_text
                and "'" in cleaned_response_text
                and '"' in cleaned_response_text
            )
        ):
            logger.Log(
                "Detected potential Python-style string concatenation in JSON. Adding specific instructions to correction prompt.",
                5,
            )
            correction_prompt_user_text = (
                f"The following text was intended to be a valid JSON list of scene outline objects. "
                f"It appears to contain Python-style string concatenations (e.g., 'string1' + 'string2') "
                f"within JSON string values, which is invalid JSON. "
                f"Please correct these by merging such concatenated parts into single, valid JSON strings. "
                f"For example, if a value is `\"'Hello ' + name + '!'\"`, it should become `\"Hello [name]!\"` or a fully resolved string. "
                f"Also, ensure all other JSON syntax is correct (quotes, commas, braces, brackets).\n"
                f"Provide ONLY the corrected, valid JSON list of scene outline objects.\n"
                f"Original text:\n\n{llm_response_text}"
            )

        correction_messages: List[Dict[str, Any]] = [
            interface.build_system_query(
                Prompts.DEFAULT_SYSTEM_PROMPT  # "You are an expert creative writing assistant..."
                + "\nAdditionally, you are an expert in JSON formatting. "
                "Your task is to fix malformed JSON, especially issues like improper string concatenation within JSON values."
            ),
            interface.build_user_query(correction_prompt_user_text),
            interface.build_assistant_query(  # Guide the LLM
                "Understood. I will analyze the provided text, fix any malformed JSON syntax including improper string concatenations, and return only the corrected, valid JSON list of scene outline objects."
            ),
        ]

        try:
            _response_msgs, parsed_corrected_json = interface.safe_generate_json(
                logger,
                correction_messages,
                model_to_use_for_correction,
                required_attribs=[],  # No specific attribs, just want a list of dicts
            )

            if isinstance(parsed_corrected_json, list) and all(
                isinstance(item, dict) for item in parsed_corrected_json
            ):
                logger.Log(
                    f"Successfully parsed {len(parsed_corrected_json)} scene outlines after LLM correction.",
                    4,
                )
                return parsed_corrected_json
            else:
                logger.Log(
                    f"LLM correction did not yield a valid list of scene outline dictionaries. Type: {type(parsed_corrected_json)}",
                    7,
                )
                return []

        except Exception as correction_e:
            logger.Log(
                f"Critical error during LLM-based JSON correction for scene outlines: {correction_e}",
                7,
            )
            return []

    logger.Log("Failed to parse scene outlines after all attempts.", 7)
    return []


def convert_scene_outlines_to_json_string(
    scene_outlines_list: List[Dict[str, Any]],
    logger: Optional[Logger] = None,
) -> str:
    """
    Converts a list of structured scene outlines (Python list of dicts)
    into a JSON formatted string.

    Args:
        scene_outlines_list (List[Dict[str, Any]]): The list of scene outline dictionaries.
        logger (Optional[Logger]): An optional logger instance.

    Returns:
        str: A JSON formatted string. Returns an empty JSON array string "[]" on error.
    """
    try:
        return json.dumps(scene_outlines_list, indent=2, ensure_ascii=False)
    except TypeError as e:
        if logger:
            logger.Log(
                f"TypeError converting scene outlines list to JSON string: {e}. List snippet: {str(scene_outlines_list)[:200]}",
                6,
            )
        return "[]"
    except Exception as e:
        if logger:
            logger.Log(
                f"Unexpected error converting scene outlines list to JSON string: {e}",
                6,
            )
        return "[]"


# Example usage (typically called from SceneOutliner.py)
if __name__ == "__main__":
    # This is for testing purposes only.
    class MockLogger:
        def Log(self, item: str, level: int, stream: bool = False):
            print(f"LOG L{level}: {item}")

        def save_langchain_interaction(self, label: str, messages: list):
            print(f"LANGCHAIN_SAVE: {label}")

    class MockInterface:
        def __init__(self):
            self.json_correction_attempt = 0

        def build_system_query(self, q: str):
            return {"role": "system", "content": q}

        def build_user_query(self, q: str):
            return {"role": "user", "content": q}

        def build_assistant_query(self, q: str):
            return {"role": "assistant", "content": q}

        def get_last_message_text(self, msgs):
            return msgs[-1]["content"] if msgs else ""

        def safe_generate_json(self, l, m, mo, required_attribs):
            self.json_correction_attempt += 1
            print(
                f"Mock LLM JSON Correction Call ({self.json_correction_attempt}) to {mo}."
            )
            # Simulate LLM returning corrected JSON after being prompted about concatenation
            user_query_for_correction = m[-2][
                "content"
            ]  # The user query for correction
            if "Python-style string concatenations" in user_query_for_correction:
                # Find the original text snippet in the prompt
                original_text_match = re.search(
                    r"Original text:\n\n(.*?)$", user_query_for_correction, re.DOTALL
                )
                if original_text_match:
                    original_text_snippet = original_text_match.group(1)
                    # Simple mock correction: replace " + " with a space within quotes
                    # This is a very naive fix for testing the path
                    corrected_text_snippet = original_text_snippet.replace("' + '", " ")
                    corrected_text_snippet = corrected_text_snippet.replace(
                        '"', '\\"'
                    )  # escape quotes for JSON string

                    # Attempt to parse the naively corrected snippet
                    try:
                        # The mock correction should produce what the LLM *would have* produced
                        # If original_text_snippet was the malformed JSON from the log:
                        # It would look like: `[ { "dialogue_points": ["'What..' + '..self.'"] } ]`
                        # A good correction would be: `[ { "dialogue_points": ["What.. ..self."] } ]`

                        # For the test with "malformed" string literal in main:
                        if "malformed_dialogue" in original_text_snippet:
                            corrected_data = [
                                {
                                    "scene_title": "Corrected Scene 1",
                                    "key_events_actions": ["Event A"],
                                    "dialogue_points": [
                                        "This is a corrected single dialogue string."
                                    ],
                                },
                                {
                                    "scene_title": "Corrected Scene 2",
                                    "key_events_actions": ["Event B"],
                                    "dialogue_points": [
                                        "Another well-formed dialogue."
                                    ],
                                },
                            ]
                            return (
                                [
                                    *m,
                                    {
                                        "role": "assistant",
                                        "content": json.dumps(corrected_data),
                                    },
                                ],
                                corrected_data,
                            )

                    except json.JSONDecodeError:
                        pass  # Fall through if naive correction still fails

            # Fallback or default correction if specific pattern not met
            default_corrected_data = [
                {"scene_title": "Default Corrected Scene"},
            ]
            return (
                [
                    *m,
                    {
                        "role": "assistant",
                        "content": json.dumps(default_corrected_data),
                    },
                ],
                default_corrected_data,
            )

    mock_logger_instance = MockLogger()
    mock_interface_instance = MockInterface()

    Config.EVAL_MODEL = "mock_json_correction_model"
    Prompts.DEFAULT_SYSTEM_PROMPT = "You are a JSON fixer bot."

    print("--- Testing parse_llm_scene_outlines_response ---")

    # Test 1: Valid JSON string
    valid_json_text = """
    [
        {"scene_number_in_chapter": 1, "scene_title": "The Discovery", "key_events_actions": ["Hero finds map"]},
        {"scene_number_in_chapter": 2, "scene_title": "The Chase", "setting_description": "Dark alley"}
    ]
    """
    parsed_valid = parse_llm_scene_outlines_response(
        mock_interface_instance, mock_logger_instance, valid_json_text
    )
    print(f"Parsed valid JSON: {json.dumps(parsed_valid, indent=2)}\n")
    assert len(parsed_valid) == 2
    assert parsed_valid[0]["scene_title"] == "The Discovery"

    # Test 2: JSON with Python-style string concatenation (should trigger enhanced correction)
    mock_interface_instance.json_correction_attempt = 0
    malformed_concat_json_text = """
    [
        {
            "scene_title": "Scene With Concat",
            "dialogue_points": ["'This is part one'" + "' and this is part two.'"],
            "key_events_actions": ["Event X"]
        }
    ]malformed_dialogue 
    """  # Added 'malformed_dialogue' to help mock identify this test case
    parsed_concat_malformed = parse_llm_scene_outlines_response(
        mock_interface_instance,
        mock_logger_instance,
        malformed_concat_json_text,
        "mock_correction_model",
    )
    print(
        f"Parsed concat-malformed JSON (after mock correction): {json.dumps(parsed_concat_malformed, indent=2)}\n"
    )
    # The mock for safe_generate_json is designed to return a specific structure for "malformed_dialogue"
    assert (
        len(parsed_concat_malformed) == 2
    )  # Mock returns 2 scenes for this specific test case
    assert parsed_concat_malformed[0]["scene_title"] == "Corrected Scene 1"
    assert (
        "This is a corrected single dialogue string."
        in parsed_concat_malformed[0]["dialogue_points"]
    )

    # Test 3: Malformed JSON string (general error)
    mock_interface_instance.json_correction_attempt = 0
    general_malformed_json_text = """
    [
        {"scene_title": "Scene A", "key_events_actions": ["Event X"]},
        {"scene_title": "Scene B", "key_events_actions": ["Event Y"] # Missing comma here
        {"scene_title": "Scene C", "key_events_actions": ["Event Z"]}
    ]
    """
    # This won't match the "Python-style string concatenations" specific logic in the mock
    # so it will fall back to the "Default Corrected Scene"
    parsed_general_malformed = parse_llm_scene_outlines_response(
        mock_interface_instance,
        mock_logger_instance,
        general_malformed_json_text,
        "mock_correction_model",
    )
    print(
        f"Parsed general malformed JSON (after mock correction): {json.dumps(parsed_general_malformed, indent=2)}\n"
    )
    assert len(parsed_general_malformed) == 1
    assert parsed_general_malformed[0]["scene_title"] == "Default Corrected Scene"

    print("\n--- Test with the problematic log output ---")
    mock_interface_instance.json_correction_attempt = 0
    problematic_log_text = """
[
  {
    "scene_number_in_chapter":1,
    "scene_title":"Awakening",
    "setting_description":"A quiet suburban street with neatly manicured lawns and a few parked cars. A small kitchen window is open, letting in the morning sunlight.",
    "characters_present":["Johnathan"],
    "character_goals_moods":"Waking up in an unfamiliar place, feeling disoriented",
    "key_events_actions":[
      "Johnathan slowly opens his eyes to find himself in a strange bed",
      "He tries to remember how he got there but can't",
      "A sense of panic and confusion washes over him"
    ],
    "dialogue_points":[
      "'What\\'s going on?'" 
        + "Johnathan whispers to himself." 
    ],
    "pacing_note":"Tense, introspective",
    "tone":"Disoriented",
    "purpose_in_chapter":"To establish the protagonist's new reality and confusion"
  }
]malformed_dialogue"""  # Added tag to trigger specific mock correction path
    parsed_problematic = parse_llm_scene_outlines_response(
        mock_interface_instance, mock_logger_instance, problematic_log_text
    )
    print(
        f"Parsed problematic log text (after mock correction): {json.dumps(parsed_problematic, indent=2)}\n"
    )
    assert (
        len(parsed_problematic) == 2
    )  # Mock correction for "malformed_dialogue" returns 2 scenes
    assert parsed_problematic[0]["scene_title"] == "Corrected Scene 1"
    assert (
        "This is a corrected single dialogue string."
        in parsed_problematic[0]["dialogue_points"]
    )
