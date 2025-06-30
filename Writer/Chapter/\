#!/usr/bin/python3

import Writer.Config
import Writer.Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger


def LLMCountChapters(Interface: Interface, _Logger: Logger, _Summary: str) -> int:
    """
    Counts the number of chapters in a given story outline using an LLM.
    This is a non-creative, JSON-focused task.
    """
    prompt = Writer.Prompts.CHAPTER_COUNT_PROMPT.format(_Summary=_Summary)

    _Logger.Log("Prompting LLM to get chapter count (JSON)...", 5)
    
    messages = [Interface.BuildUserQuery(prompt)]

    # Use SafeGenerateJSON to handle the request. It will retry if the JSON is invalid.
    # No critique-revision cycle is needed for this simple, non-creative task.
    _, response_json = Interface.SafeGenerateJSON(
        _Logger,
        messages,
        Writer.Config.EVAL_MODEL,
        _RequiredAttribs=["TotalChapters"]
    )

    try:
        total_chapters = int(response_json.get("TotalChapters", -1))
        if total_chapters > 0:
            _Logger.Log(f"LLM detected {total_chapters} chapters.", 5)
            return total_chapters
        else:
            _Logger.Log(f"LLM returned an invalid chapter count: {total_chapters}. Defaulting to -1.", 7)
            return -1
            
    except (ValueError, TypeError) as e:
        _Logger.Log(f"Critical Error: Could not parse 'TotalChapters' as an integer. Error: {e}", 7)
        return -1
