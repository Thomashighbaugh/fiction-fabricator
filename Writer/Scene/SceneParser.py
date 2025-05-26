# File: AIStoryWriter/Writer/Scene/SceneParser.py
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
            # Basic validation: check for at least one common key expected in scene outlines
            if scene_outlines_list and not all(
                "scene_title" in item or "key_events_actions" in item
                for item in scene_outlines_list
            ):
                logger.Log(
                    "Parsed JSON list items do not appear to be scene outlines (missing common keys).",
                    5,
                )
                # Could still be valid JSON but not what we want. For now, accept if it's list of dicts.

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
            # Fall through to LLM correction if it's not the right structure.
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

        correction_messages: List[Dict[str, Any]] = [
            interface.build_system_query(
                Prompts.DEFAULT_SYSTEM_PROMPT
            ),  # General helpful assistant
            interface.build_user_query(
                f"The following text was intended to be a valid JSON list, where each item is an object "
                f"representing a scene outline (with keys like 'scene_title', 'key_events_actions', etc.). "
                f"However, it's malformed or not in the correct structure. "
                f"Please correct it and provide ONLY the valid JSON list of scene outline objects. "
                f"Original text:\n\n{llm_response_text}"
            ),
            # Guiding the assistant towards the expected output format
            interface.build_assistant_query(
                "Understood. I will analyze the provided text and return only the corrected, valid JSON list of scene outline objects."
            ),
        ]

        try:
            # SafeGenerateJSON will handle its own retries for getting valid JSON from the correction model
            # No specific required_attribs here, as we're just hoping for a list of dicts.
            # The initial prompt to the correction LLM already specifies the desired structure.
            _response_msgs, parsed_corrected_json = interface.safe_generate_json(
                logger,
                correction_messages,
                model_to_use_for_correction,
                required_attribs=[],
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
                return (
                    []
                )  # Fallback to empty list if correction fails to produce the right type

        except Exception as correction_e:
            logger.Log(
                f"Critical error during LLM-based JSON correction for scene outlines: {correction_e}",
                7,
            )
            return []  # Fallback

    # Future: Could add a more rudimentary regex-based parsing here as a last resort if JSON fails badly.
    # This would depend on a very consistent (but non-JSON) markdown structure from the LLM.
    # For now, rely on getting JSON or LLM-corrected JSON.

    logger.Log("Failed to parse scene outlines after all attempts.", 7)
    return []


def convert_scene_outlines_to_json_string(
    scene_outlines_list: List[Dict[str, Any]],
    logger: Optional[Logger] = None,  # Optional logger for this utility
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
            # This mock simulates the LLM correction part
            self.json_correction_attempt += 1
            print(
                f"Mock LLM JSON Correction Call ({self.json_correction_attempt}) to {mo}."
            )
            # Simulate returning a corrected JSON list after one attempt
            if (
                "malformed" in m[1]["content"]
            ):  # Assuming the user query contains 'malformed' for this test
                corrected_data = [
                    {
                        "scene_title": "Corrected Scene 1",
                        "key_events_actions": ["Event A"],
                    },
                    {
                        "scene_title": "Corrected Scene 2",
                        "key_events_actions": ["Event B"],
                    },
                ]
                return (
                    [*m, {"role": "assistant", "content": json.dumps(corrected_data)}],
                    corrected_data,
                )
            # Simulate failure if input doesn't trigger correction logic
            raise Exception(
                "Mocked safe_generate_json failed for non-correction scenario"
            )

    mock_logger = MockLogger()
    mock_interface = MockInterface()

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
        mock_interface, mock_logger, valid_json_text
    )
    print(f"Parsed valid JSON: {json.dumps(parsed_valid, indent=2)}\n")
    assert len(parsed_valid) == 2
    assert parsed_valid[0]["scene_title"] == "The Discovery"

    # Test 2: JSON with markdown backticks
    md_json_text = """
    ```json
    [
        {"scene_title": "With Backticks", "purpose_in_chapter": "To test parsing."}
    ]
    ```
    """
    parsed_md_json = parse_llm_scene_outlines_response(
        mock_interface, mock_logger, md_json_text
    )
    print(
        f"Parsed JSON with markdown backticks: {json.dumps(parsed_md_json, indent=2)}\n"
    )
    assert len(parsed_md_json) == 1
    assert parsed_md_json[0]["scene_title"] == "With Backticks"

    # Test 3: Malformed JSON string (will trigger LLM correction in the mock)
    mock_interface.json_correction_attempt = 0  # Reset counter for this specific test
    malformed_json_text = """
    [
        {"scene_title": "Scene A", "key_events_actions": ["Event X"]},
        {"scene_title": "Scene B", "key_events_actions": ["Event Y"] # Missing comma here
        {"scene_title": "Scene C", "key_events_actions": ["Event Z"]}
    ]malformed
    """  # Added 'malformed' to trigger mock's correction path
    parsed_malformed = parse_llm_scene_outlines_response(
        mock_interface, mock_logger, malformed_json_text, "mock_correction_model"
    )
    print(
        f"Parsed malformed JSON (after mock correction): {json.dumps(parsed_malformed, indent=2)}\n"
    )
    assert len(parsed_malformed) == 2  # Expecting the corrected version from mock
    assert parsed_malformed[0]["scene_title"] == "Corrected Scene 1"

    # Test 4: Not a list of dicts, but valid JSON (e.g. a single dict or a list of strings)
    not_list_of_dicts_json = """
    {"error": "This is not a list of scenes, but a single object."}
    """  # This will also trigger correction in a real scenario due to `ValueError` after initial `json.loads`
    mock_interface.json_correction_attempt = 0
    parsed_not_list = parse_llm_scene_outlines_response(
        mock_interface,
        mock_logger,
        not_list_of_dicts_json + "malformed",
        "mock_correction_model",
    )  # Add malformed to trigger mock
    print(
        f"Parsed non-list JSON (after mock correction): {json.dumps(parsed_not_list, indent=2)}\n"
    )
    assert len(parsed_not_list) == 2  # Expecting corrected version

    # Test 5: Empty string
    parsed_empty = parse_llm_scene_outlines_response(mock_interface, mock_logger, "")
    print(f"Parsed empty string: {parsed_empty}\n")
    assert parsed_empty == []

    # Test 6: Completely invalid text (not JSON at all)
    invalid_text = "This is just some plain text, not JSON at all. malformed"  # Add malformed to trigger mock
    mock_interface.json_correction_attempt = 0
    parsed_invalid = parse_llm_scene_outlines_response(
        mock_interface, mock_logger, invalid_text, "mock_correction_model"
    )
    print(
        f"Parsed invalid text (after mock correction): {json.dumps(parsed_invalid, indent=2)}\n"
    )
    assert len(parsed_invalid) == 2

    print("--- Testing convert_scene_outlines_to_json_string ---")
    sample_outlines_list = [
        {"scene_title": "Scene Alpha", "order": 1},
        {"scene_title": "Scene Beta", "order": 2},
    ]
    json_string = convert_scene_outlines_to_json_string(
        sample_outlines_list, mock_logger
    )
    print(f"Converted list to JSON string:\n{json_string}\n")
    assert '"Scene Alpha"' in json_string

    # Test with non-serializable data (pathological case, json.dumps handles some)
    try:
        non_serializable_list = [{"title": "Test", "data": datetime.datetime.now()}]
        json_string_error = convert_scene_outlines_to_json_string(
            non_serializable_list, mock_logger
        )
        print(
            f"Conversion with non-serializable (datetime): {json_string_error}"
        )  # Will likely be "[]" or raise error if json.dumps fails
        # json.dumps will raise TypeError for datetime by default. Our wrapper catches it.
        assert json_string_error == "[]"
    except Exception as e:
        print(f"Caught expected error during non-serializable test: {e}")
