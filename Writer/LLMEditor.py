#!/usr/bin/python3

import json
import Writer.Config
import Writer.Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger

def GetFeedbackOnOutline(Interface: Interface, _Logger: Logger, _Outline: str) -> str:
    """
    Generates a critique of a given story outline. This function is intended to be
    the 'critique' step in a larger revision process.
    """
    # Setup Initial Context History
    History = [
        Interface.BuildSystemQuery(Writer.Prompts.CRITIC_OUTLINE_INTRO),
        Interface.BuildUserQuery(Writer.Prompts.CRITIC_OUTLINE_PROMPT.format(_Outline=_Outline))
    ]

    _Logger.Log("Prompting LLM to critique outline...", 5)
    # This is a creative task, so we want a substantive response.
    History = Interface.SafeGenerateText(
        _Logger, History, Writer.Config.REVISION_MODEL, _MinWordCount=50
    )
    _Logger.Log("Finished getting outline feedback.", 5)

    return Interface.GetLastMessageText(History)


def GetOutlineRating(Interface: Interface, _Logger: Logger, _Outline: str) -> bool:
    """
    Asks an LLM to evaluate if an outline is complete and meets quality criteria.
    Returns a simple boolean. This is a non-creative check.
    """
    History = [
        Interface.BuildSystemQuery(Writer.Prompts.OUTLINE_COMPLETE_INTRO),
        Interface.BuildUserQuery(Writer.Prompts.OUTLINE_COMPLETE_PROMPT.format(_Outline=_Outline))
    ]

    _Logger.Log("Prompting LLM for outline completion rating (JSON)...", 5)
    
    # This call generates non-creative JSON. The SafeGenerateJSON function handles retries for format.
    _, ResponseJSON = Interface.SafeGenerateJSON(
        _Logger, History, Writer.Config.EVAL_MODEL, _RequiredAttribs=["IsComplete"]
    )
    
    IsComplete = ResponseJSON.get("IsComplete", False)
    _Logger.Log(f"Editor determined IsComplete: {IsComplete}", 5)
    
    # Ensure the returned value is a boolean
    if isinstance(IsComplete, bool):
        return IsComplete
    elif isinstance(IsComplete, str):
        return IsComplete.lower() == 'true'
    return False


def GetFeedbackOnChapter(Interface: Interface, _Logger: Logger, _Chapter: str, _Outline: str) -> str:
    """
    Generates a critique of a given chapter. This function is intended to be
    the 'critique' step in a larger revision process.
    """
    History = [
        Interface.BuildSystemQuery(Writer.Prompts.CRITIC_CHAPTER_INTRO),
        Interface.BuildUserQuery(Writer.Prompts.CRITIC_CHAPTER_PROMPT.format(_Chapter=_Chapter, _Outline=_Outline))
    ]

    _Logger.Log("Prompting LLM to critique chapter...", 5)
    Messages = Interface.SafeGenerateText(
        _Logger, History, Writer.Config.REVISION_MODEL, _MinWordCount=50
    )
    _Logger.Log("Finished getting chapter feedback.", 5)

    return Interface.GetLastMessageText(Messages)


def GetChapterRating(Interface: Interface, _Logger: Logger, _Chapter: str) -> bool:
    """
    Asks an LLM to evaluate if a chapter is complete and meets quality criteria.
    Returns a simple boolean. This is a non-creative check.
    """
    History = [
        Interface.BuildSystemQuery(Writer.Prompts.CHAPTER_COMPLETE_INTRO),
        Interface.BuildUserQuery(Writer.Prompts.CHAPTER_COMPLETE_PROMPT.format(_Chapter=_Chapter))
    ]

    _Logger.Log("Prompting LLM for chapter completion rating (JSON)...", 5)

    # This call generates non-creative JSON.
    _, ResponseJSON = Interface.SafeGenerateJSON(
        _Logger, History, Writer.Config.EVAL_MODEL, _RequiredAttribs=["IsComplete"]
    )

    IsComplete = ResponseJSON.get("IsComplete", False)
    _Logger.Log(f"Editor determined IsComplete: {IsComplete}", 5)

    if isinstance(IsComplete, bool):
        return IsComplete
    elif isinstance(IsComplete, str):
        return IsComplete.lower() == 'true'
    return False
