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

# import re # Currently unused, but could be for future more complex parsing
import datetime  # Currently unused


def parse_llm_scene_outlines_response(
    interface: Interface,
    logger: Logger,
    llm_response_text: str,
    model_to_use_for_correction: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Parses an LLM's text response, expecting it to contain a list of scene outlines.
    Primarily attempts to parse as JSON. If that fails, it can optionally try
    LLM-based correction.

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
    if cleaned_response_text.startswith("```json"):
        cleaned_response_text = cleaned_response_text[7:]
    if cleaned_response_text.endswith("```"):
        cleaned_response_text = cleaned_response_text[:-3]
    cleaned_response_text = cleaned_response_text.strip()

    try:
        if not cleaned_response_text:
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
                    "Parsed JSON list items seem valid dicts but might be missing typical scene keys.",
                    5,  # Warning, not critical failure if it's list of dicts
                )
            logger.Log(
                f"Successfully parsed {len(scene_outlines_list)} scene outlines from JSON.",
                4,
            )
            return scene_outlines_list
        else:
            error_message = f"Parsed JSON is not a list of dictionaries. Type: {type(scene_outlines_list)}"
            logger.Log(error_message, 6)
            raise ValueError(error_message)  # Fall through to LLM correction

    except (json.JSONDecodeError, ValueError) as e:
        logger.Log(
            f"Initial JSON parse failed for scene outlines: {e}. "
            f"LLM response snippet: '{llm_response_text[:250]}...'",  # Increased snippet length
            6,
        )

        # Attempt 2: LLM-based correction
        logger.Log(
            f"Attempting LLM-based correction for malformed scene outline JSON "
            f"using model: {model_to_use_for_correction}",
            5,
        )

        # More specific correction prompt
        correction_prompt_text = (
            "The following text was intended to be a valid JSON list of objects. "
            "Each object in the list represents a 'scene outline' and should have keys like "
            "'scene_number_in_chapter', 'scene_title', 'setting_description', "
            "'characters_present', 'character_goals_moods', 'key_events_actions' (list of strings), "
            "'dialogue_points' (list of strings), 'pacing_note', 'tone', "
            "'purpose_in_chapter', and 'transition_out_hook'.\n"
            "The current text is malformed or not in the correct structure. "
            "Common errors include Python-style string concatenation (e.g., 'text' + 'more text') "
            "within JSON string values, or unescaped special characters.\n"
            "Please correct it and provide ONLY the valid JSON list of scene outline objects. "
            "Do not include any explanatory text before or after the JSON.\n\n"
            f"Original Text:\n```\n{llm_response_text}\n```\n\n"
            "Corrected JSON Output:"
        )

        correction_messages: List[Dict[str, Any]] = [
            interface.build_system_query(
                "You are an expert AI assistant that specializes in correcting malformed JSON data "
                "to adhere to a specific schema, in this case, a list of scene outline objects. "
                "Ensure all string values within the JSON are simple, valid JSON strings, "
                "and lists of strings are correctly formatted."
            ),
            interface.build_user_query(correction_prompt_text),
        ]

        try:
            # safe_generate_json will try to get a valid JSON structure.
            # We don't specify required_attribs here as the goal is to get *any* valid JSON list of dicts first.
            # The prompt guides the structure.
            _response_msgs, parsed_corrected_json = interface.safe_generate_json(
                logger,
                correction_messages,
                model_to_use_for_correction,
                required_attribs=[],  # No specific required attributes for the correction, just valid JSON list of dicts.
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
                    f"LLM correction did not yield a valid list of scene outline dictionaries. "
                    f"Type received: {type(parsed_corrected_json)}. "
                    f"Corrected JSON snippet: {str(parsed_corrected_json)[:200]}",
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
            log_snippet = str(scene_outlines_list)[:200]
            logger.Log(
                f"TypeError converting scene outlines list to JSON string: {e}. "
                f"List snippet: {log_snippet}",
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
        """Mock logger for testing SceneParser."""

        def Log(self, item: str, level: int, stream: bool = False):
            print(f"LOG L{level}: {item}")

        def save_langchain_interaction(self, label: str, messages: list):
            print(f"LANGCHAIN_SAVE: {label}")

    class MockInterface:
        """Mock interface for testing SceneParser."""

        def __init__(self):
            self.json_correction_attempt = 0

        def build_system_query(self, q: str) -> Dict[str, str]:
            return {"role": "system", "content": q}

        def build_user_query(self, q: str) -> Dict[str, str]:
            return {"role": "user", "content": q}

        def build_assistant_query(self, q: str) -> Dict[str, str]:
            return {"role": "assistant", "content": q}

        def get_last_message_text(self, msgs: List[Dict[str, Any]]) -> str:
            return msgs[-1]["content"] if msgs else ""

        def safe_generate_json(
            self,
            l: MockLogger,  # pylint: disable=unused-argument
            m: List[Dict[str, Any]],
            mo: str,
            required_attribs: List[str],  # pylint: disable=unused-argument
        ) -> tuple[list[Any], Any]:
            self.json_correction_attempt += 1
            l.Log(
                f"Mock LLM JSON Correction Call ({self.json_correction_attempt}) to {mo}.",
                0,
            )
            # Simulate LLM correcting the malformed JSON (e.g. python string concat)
            corrected_data = [
                {
                    "scene_title": "Corrected Scene 1",
                    "key_events_actions": ["Event A"],
                    "dialogue_points": ["This is a corrected simple string."],
                },
                {
                    "scene_title": "Corrected Scene 2",
                    "key_events_actions": ["Event B"],
                    "dialogue_points": ["Another corrected string."],
                },
            ]
            return (
                [*m, {"role": "assistant", "content": json.dumps(corrected_data)}],
                corrected_data,
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

    # Test 2: JSON with Python-style string concatenation (should trigger LLM correction)
    malformed_dialogue_json = """
    [
      {
        "scene_title": "Problematic Dialogue",
        "dialogue_points": ["'This is part one.' + ' This is part two.'"]
      }
    ]
    """
    mock_interface_instance.json_correction_attempt = 0
    parsed_malformed_dialogue = parse_llm_scene_outlines_response(
        mock_interface_instance,
        mock_logger_instance,
        malformed_dialogue_json,
        "mock_correction_model",
    )
    print(
        f"Parsed malformed dialogue JSON (after mock correction): "
        f"{json.dumps(parsed_malformed_dialogue, indent=2)}\n"
    )
    assert len(parsed_malformed_dialogue) == 2  # Mock returns 2 corrected scenes
    assert parsed_malformed_dialogue[0]["scene_title"] == "Corrected Scene 1"
    assert parsed_malformed_dialogue[0]["dialogue_points"] == [
        "This is a corrected simple string."
    ]

    print("--- Testing convert_scene_outlines_to_json_string ---")
    sample_outlines_list = [
        {"scene_title": "Scene Alpha", "order": 1},
        {"scene_title": "Scene Beta", "order": 2},
    ]
    json_string = convert_scene_outlines_to_json_string(
        sample_outlines_list, mock_logger_instance
    )
    print(f"Converted list to JSON string:\n{json_string}\n")
    assert '"Scene Alpha"' in json_string
