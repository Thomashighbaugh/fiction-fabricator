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
import Writer.Prompts as Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger
from typing import List, Dict, Any, Optional, Union
import re
import Writer.Models as Models


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
    # Clean common markdown artifacts around JSON
    if cleaned_response_text.startswith("```json"):
        cleaned_response_text = cleaned_response_text[7:]
    if cleaned_response_text.endswith("```"):
        cleaned_response_text = cleaned_response_text[:-3]
    cleaned_response_text = cleaned_response_text.strip()

    parsed_json_data: Union[Dict[str, Any], List[Any]] = {}
    try:
        if not cleaned_response_text:
            raise json.JSONDecodeError("Cleaned response text is empty.", "", 0)

        parsed_json_data = json.loads(cleaned_response_text)

        # Expecting a list of scene dictionaries.
        # If the LLM returned a dictionary with a "scenes" key (as per Models.SceneOutlinesList),
        # extract the list from there. Otherwise, assume it's a direct list.
        if (
            isinstance(parsed_json_data, dict)
            and "scenes" in parsed_json_data
            and isinstance(parsed_json_data["scenes"], list)
        ):
            scene_outlines_list = parsed_json_data["scenes"]
            logger.Log("Parsed JSON is a dict with 'scenes' key; extracting list.", 4)
        elif isinstance(parsed_json_data, list):
            scene_outlines_list = parsed_json_data
            logger.Log("Parsed JSON is a direct list of scenes.", 4)
        else:
            logger.Log(
                f"Parsed JSON is neither a list nor a dict with a 'scenes' key: {type(parsed_json_data)}. Expected list of dicts.",
                6,
            )
            raise ValueError(
                "Parsed JSON not in expected list-of-dictionaries format for scene outlines."
            )

        if scene_outlines_list and not all(
            isinstance(item, dict)
            and ("scene_title" in item or "key_events_actions" in item)
            for item in scene_outlines_list
        ):
            logger.Log(
                "Parsed JSON list items do not appear to be scene outlines (missing common keys or not dicts).",
                5,
            )
            raise ValueError(
                "Parsed list items are not valid scene outline dictionaries."
            )

        logger.Log(
            f"Successfully parsed {len(scene_outlines_list)} scene outlines from direct JSON.",
            4,
        )
        return scene_outlines_list

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

        correction_prompt_user_text = Prompts.JSON_PARSE_ERROR.format(
            _OriginalText=llm_response_text, _Error=str(e)
        )

        correction_messages: List[Dict[str, Any]] = [
            interface.build_system_query(
                Prompts.DEFAULT_SYSTEM_PROMPT
                + "\nAdditionally, you are an expert in JSON formatting. Your task is to fix malformed JSON."
            ),
            interface.build_user_query(correction_prompt_user_text),
        ]

        try:
            # Use Models.SceneOutlinesList for correction to ensure the output is a valid Pydantic structure
            _response_msgs, parsed_corrected_json_data = interface.safe_generate_json(
                logger,
                correction_messages,
                model_to_use_for_correction,
                required_attribs=[],
                expected_response_model=Models.SceneOutlinesList,
            )

            # Extract the list from the Pydantic model's output (which is a dict with 'scenes' key)
            if (
                isinstance(parsed_corrected_json_data, dict)
                and "scenes" in parsed_corrected_json_data
                and isinstance(parsed_corrected_json_data["scenes"], list)
            ):
                corrected_scene_list = parsed_corrected_json_data["scenes"]
                logger.Log(
                    f"Successfully parsed {len(corrected_scene_list)} scene outlines after LLM correction (via Pydantic model).",
                    4,
                )
                return corrected_scene_list
            else:
                logger.Log(
                    f"LLM correction did not yield a valid list of scene outline dictionaries. Type: {type(parsed_corrected_json_data)}",
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
