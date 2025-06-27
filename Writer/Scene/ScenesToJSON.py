#!/usr/bin/python3

import Writer.Config
import Writer.Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger

def ScenesToJSON(
    Interface: Interface, _Logger: Logger, _SceneOutlineMD: str
) -> list:
    """
    Converts a markdown-formatted, scene-by-scene outline into a structured
    JSON list of strings. Each string in the list represents one scene's outline.

    This is a non-creative, structural conversion task.

    Args:
        Interface: The LLM interface wrapper.
        _Logger: The logger instance.
        _SceneOutlineMD: A string containing the full markdown of the scene-by-scene outline.

    Returns:
        A list of strings, where each string is the outline for a single scene.
        Returns an empty list if the conversion fails.
    """
    _Logger.Log("Converting scene outline markdown to JSON list...", 4)

    # Prepare the prompt for the LLM
    prompt = Writer.Prompts.SCENES_TO_JSON.format(_Scenes=_SceneOutlineMD)
    messages = [Interface.BuildUserQuery(prompt)]

    # Use SafeGenerateJSON to ensure a valid JSON list is returned.
    # The prompt specifically requests a list of strings, so we don't need
    # to check for specific attributes, just that the result is a list.
    _, response_json = Interface.SafeGenerateJSON(
        _Logger,
        messages,
        Writer.Config.CHECKER_MODEL, # Use a fast, reliable model for this conversion
    )

    # Validate that the response is a list
    if isinstance(response_json, list):
        _Logger.Log(f"Successfully converted markdown to a list of {len(response_json)} scenes.", 5)
        return response_json
    else:
        _Logger.Log(f"Conversion failed: LLM did not return a valid JSON list. Response: {response_json}", 7)
        return []
