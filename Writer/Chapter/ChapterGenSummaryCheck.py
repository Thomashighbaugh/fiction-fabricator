#!/usr/bin/python3

import json
import Writer.Config
import Writer.Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger


def LLMSummaryCheck(Interface: Interface, _Logger: Logger, _RefSummary: str, _Work: str) -> (bool, str):
    """
    Generates a summary of the work provided, compares that to the reference summary (outline),
    and asks if the work correctly followed the prompt. This is a validation step, not a creative one.
    """
    # LLM Length Check - A simple guard against empty or near-empty responses.
    if len(_Work.split()) < 100:
        _Logger.Log(
            "Previous response didn't meet the length requirement (100 words), so it likely failed to generate properly.",
            7,
        )
        return False, "The generated text was too short. Please write a full, detailed response."

    # --- Step 1: Summarize the generated work ---
    _Logger.Log("Summarizing the generated work for comparison...", 3)
    SummaryLangchain = [
        Interface.BuildSystemQuery(Writer.Prompts.SUMMARY_CHECK_INTRO),
        Interface.BuildUserQuery(Writer.Prompts.SUMMARY_CHECK_PROMPT.format(_Work=_Work))
    ]
    SummaryLangchain = Interface.SafeGenerateText(
        _Logger, SummaryLangchain, Writer.Config.CHECKER_MODEL, _MinWordCount=30
    )
    WorkSummary = Interface.GetLastMessageText(SummaryLangchain)

    # --- Step 2: Summarize the reference outline ---
    _Logger.Log("Summarizing the reference outline for comparison...", 3)
    SummaryLangchain = [
        Interface.BuildSystemQuery(Writer.Prompts.SUMMARY_OUTLINE_INTRO),
        Interface.BuildUserQuery(Writer.Prompts.SUMMARY_OUTLINE_PROMPT.format(_RefSummary=_RefSummary))
    ]
    SummaryLangchain = Interface.SafeGenerateText(
        _Logger, SummaryLangchain, Writer.Config.CHECKER_MODEL, _MinWordCount=30
    )
    OutlineSummary = Interface.GetLastMessageText(SummaryLangchain)

    # --- Step 3: Generate a JSON comparison ---
    _Logger.Log("Comparing summaries to check for outline adherence...", 3)
    ComparisonLangchain = [
        Interface.BuildSystemQuery(Writer.Prompts.SUMMARY_COMPARE_INTRO),
        Interface.BuildUserQuery(
            Writer.Prompts.SUMMARY_COMPARE_PROMPT.format(
                WorkSummary=WorkSummary, OutlineSummary=OutlineSummary
            )
        )
    ]
    
    # This is a non-creative, JSON-focused task.
    _, ResponseJSON = Interface.SafeGenerateJSON(
        _Logger,
        ComparisonLangchain,
        Writer.Config.EVAL_MODEL, # Use the EVAL_MODEL for this check
        _RequiredAttribs=["DidFollowOutline", "Suggestions"]
    )
    
    did_follow = ResponseJSON.get("DidFollowOutline", False)
    suggestions = ResponseJSON.get("Suggestions", "")

    # Ensure the output format is correct for the calling function
    if isinstance(did_follow, str):
        did_follow = did_follow.lower() == 'true'

    feedback_string = f"### Adherence Check Feedback:\n{suggestions}" if suggestions else ""
    
    _Logger.Log(f"Outline Adherence Check Result: {did_follow}", 4)

    return did_follow, feedback_string
