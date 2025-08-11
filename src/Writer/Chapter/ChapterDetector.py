#!/usr/bin/python3

import Writer.Config
import Writer.Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger


def LLMCountChapters(Interface: Interface, _Logger: Logger, _Summary: str, selected_model: str) -> int:
    """
    Counts the number of chapters in a given story outline using an LLM.
    This is a non-creative, JSON-focused task with a built-in retry mechanism.
    """
    prompt = Writer.Prompts.CHAPTER_COUNT_PROMPT.format(_Summary=_Summary)
    messages = [Interface.BuildUserQuery(prompt)]

    max_retries = 3
    for attempt in range(max_retries):
        _Logger.Log(f"Attempting to get chapter count (Attempt {attempt + 1}/{max_retries})...", 5)

        _, response_json = Interface.SafeGenerateJSON(
            _Logger,
            messages,
            selected_model,
            _RequiredAttribs=["TotalChapters"]
        )

        if not response_json:
             _Logger.Log("LLMCountChapters failed to get a JSON response. Retrying...", 6)
             continue

        try:
            total_chapters = int(response_json.get("TotalChapters", -1))
            # A valid chapter count should be a reasonable positive number.
            if total_chapters > 0 and total_chapters < 100:
                _Logger.Log(f"LLM detected {total_chapters} chapters.", 5)
                return total_chapters
            else:
                _Logger.Log(f"LLM returned an invalid or unreasonable chapter count: {total_chapters}. Retrying...", 7)

        except (ValueError, TypeError) as e:
            _Logger.Log(f"Could not parse 'TotalChapters'. Error: {e}. Retrying...", 7)

    _Logger.Log(f"CRITICAL: Failed to determine chapter count after {max_retries} attempts.", 7)
    return -1
