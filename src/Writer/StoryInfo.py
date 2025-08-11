#!/usr/bin/python3

import json
import Writer.Config
import Writer.Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger


def GetStoryInfo(Interface: Interface, _Logger: Logger, _Messages: list, selected_model: str) -> dict:
    """
    Generates final story information (Title, Summary, Tags) using an LLM.
    This is a non-creative, JSON-focused task.
    """
    prompt = Writer.Prompts.STATS_PROMPT

    _Logger.Log("Prompting LLM to generate story info (JSON)...", 5)

    # We append the stats prompt to the existing message history to give the LLM
    # the full context of the generated story.
    _Messages.append(Interface.BuildUserQuery(prompt))

    # Use SafeGenerateJSON to handle the request. It will retry if the JSON is invalid.
    # We require the main keys to be present in the response.
    _, response_json = Interface.SafeGenerateJSON(
        _Logger,
        _Messages,
        selected_model,
        _RequiredAttribs=["Title", "Summary", "Tags", "OverallRating"]
    )

    _Logger.Log("Finished getting story info.", 5)
    
    # Return the validated JSON dictionary, or an empty dict if something went wrong
    # (though SafeGenerateJSON is designed to prevent that).
    return response_json if isinstance(response_json, dict) else {}
