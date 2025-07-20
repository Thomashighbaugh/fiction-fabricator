#!/usr/bin/python3
# File: Writer/LLMEditor.py
# Purpose: Provides functions for LLM-based critique and quality checks.

import Writer.Config
import Writer.Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger

def GetChapterRating(Interface: Interface, _Logger: Logger, _Chapter: str) -> bool:
    """
    Uses an LLM to rate a chapter and determine if it's complete and of high quality.
    """
    _Logger.Log("Getting chapter quality rating...", 4)
    prompt = Writer.Prompts.CHAPTER_COMPLETE_PROMPT.format(_Chapter=_Chapter)
    messages = [Interface.BuildUserQuery(prompt)]
    
    _, response_json = Interface.SafeGenerateJSON(
        _Logger, messages, Writer.Config.EVAL_MODEL, _RequiredAttribs=["IsComplete"]
    )
    
    is_complete = response_json.get("IsComplete", False)
    if isinstance(is_complete, str):
        is_complete = is_complete.lower() == 'true'

    return is_complete

def GetFeedbackOnChapter(Interface: Interface, _Logger: Logger, _Chapter: str, _Outline: str) -> str:
    """
    Uses an LLM to generate constructive feedback on a given chapter.
    """
    _Logger.Log("Getting feedback on chapter...", 4)
    prompt = Writer.Prompts.CRITIC_CHAPTER_PROMPT.format(_Chapter=_Chapter)
    messages = [Interface.BuildUserQuery(prompt)]

    response_messages = Interface.SafeGenerateText(
        _Logger, messages, Writer.Config.CRITIQUE_LLM, min_word_count_target=100
    )
    
    return Interface.GetLastMessageText(response_messages)

def GetOutlineRating(Interface: Interface, _Logger: Logger, _Outline: str) -> bool:
    """
    Uses an LLM to rate an outline and determine if it's complete and well-structured.
    """
    _Logger.Log("Getting outline completeness rating...", 4)
    prompt = Writer.Prompts.OUTLINE_COMPLETE_PROMPT.format(_Outline=_Outline)
    messages = [Interface.BuildUserQuery(prompt)]
    
    _, response_json = Interface.SafeGenerateJSON(
        _Logger, messages, Writer.Config.EVAL_MODEL, _RequiredAttribs=["IsComplete"]
    )
    
    is_complete = response_json.get("IsComplete", False)
    if isinstance(is_complete, str):
        is_complete = is_complete.lower() == 'true'

    return is_complete

def GetFeedbackOnOutline(Interface: Interface, _Logger: Logger, _Outline: str) -> str:
    """
    Uses an LLM to generate constructive feedback on a given novel outline.
    """
    _Logger.Log("Getting feedback on outline...", 4)
    prompt = Writer.Prompts.CRITIC_OUTLINE_PROMPT.format(_Outline=_Outline)
    messages = [Interface.BuildUserQuery(prompt)]

    response_messages = Interface.SafeGenerateText(
        _Logger, messages, Writer.Config.CRITIQUE_LLM, min_word_count_target=100
    )

    return Interface.GetLastMessageText(response_messages)
