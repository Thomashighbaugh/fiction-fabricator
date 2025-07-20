#!/usr/bin/python3

import json
import re
import Writer.Config
import Writer.Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger


def _clean_revised_content(
    Interface: Interface,
    _Logger: Logger,
    text_to_clean: str
) -> str:
    """
    Takes text from a revision process and cleans out any non-narrative artifacts.
    This is a fast, non-creative cleanup step.
    """
    if not text_to_clean or "[ERROR:" in text_to_clean:
        return text_to_clean

    _Logger.Log("Performing final cleanup on revised content...", 1)

    prompt = Writer.Prompts.CLEAN_REVISED_TEXT_PROMPT.format(text_to_clean=text_to_clean)
    messages = [Interface.BuildUserQuery(prompt)]
    min_word_target = int(len(text_to_clean.split()) * 0.7)

    response_history = Interface.SafeGenerateText(
        _Logger, messages, Writer.Config.CHECKER_MODEL, min_word_count_target=max(50, min_word_target)
    )

    return Interface.GetLastMessageText(response_history)


def critique_and_revise_creative_content(
    Interface: Interface,
    _Logger: Logger,
    initial_content: str,
    task_description: str,
    narrative_context_summary: str,
    initial_user_prompt: str,
    style_guide: str,
    is_json: bool = False,
) -> str:
    """
    Orchestrates the critique and revision process for a piece of generated creative content.
    This process is a single pass: critique -> revise -> clean.
    """
    # --- FIXED: Add robustness check for initial content ---
    if not initial_content or not initial_content.strip() or "[ERROR:" in initial_content:
        _Logger.Log("CritiqueRevision called with empty, invalid, or error-containing initial content. Skipping process.", 6)
        return initial_content

    # --- Step 1: Generate Critique ---
    _Logger.Log("Starting critique generation for the latest content.", 5)

    json_guidance = (
        "The content is JSON. Focus your critique on the substance, clarity, and narrative value of the data. Respond with your critique as a plain string."
    ) if is_json else "Respond with your critique as a plain string."

    critique_prompt = Writer.Prompts.CRITIQUE_CREATIVE_CONTENT_PROMPT.format(
        text_to_critique=initial_content,
        task_description=task_description,
        narrative_context_summary=narrative_context_summary,
        initial_user_prompt=initial_user_prompt,
        style_guide=style_guide,
        is_json_output=json_guidance
    )
    critique_messages = [Interface.BuildSystemQuery(style_guide), Interface.BuildUserQuery(critique_prompt)]
    critique_model = Writer.Config.CRITIQUE_LLM
    
    critique_messages = Interface.SafeGenerateText(
        _Logger, critique_messages, critique_model, min_word_count_target=100
    )
    critique = Interface.GetLastMessageText(critique_messages)
    _Logger.Log(f"Critique received:\n---\n{critique}\n---", 1)

    # --- FIXED: Handle critique failure gracefully ---
    if "[ERROR:" in critique or not critique.strip():
        _Logger.Log("Critique step failed or returned empty. Skipping revision and returning original content.", 6)
        return initial_content

    # --- Step 2: Generate Revision ---
    _Logger.Log("Starting revision based on the received critique.", 5)

    json_instructions = (
        "Important: Your final output must be a single, valid JSON object. Revise the *content* within the JSON structure based on the critique. Do not add any explanatory text outside of the JSON object itself."
    ) if is_json else (
        "Ensure your final output is only the revised text. Do not write a reflection on the changes."
    )

    revision_prompt = Writer.Prompts.REVISE_CREATIVE_CONTENT_BASED_ON_CRITIQUE_PROMPT.format(
        original_text=initial_content,
        critique=critique,
        task_description=task_description,
        narrative_context_summary=narrative_context_summary,
        initial_user_prompt=initial_user_prompt,
        style_guide=style_guide,
        json_instructions=json_instructions
    )
    revision_messages = [Interface.BuildSystemQuery(style_guide), Interface.BuildUserQuery(revision_prompt)]
    revision_model = Writer.Config.CHAPTER_REVISION_WRITER_MODEL

    revised_content_messy = ""
    if is_json:
        _, revised_json = Interface.SafeGenerateJSON(_Logger, revision_messages, revision_model)
        if not revised_json:
             _Logger.Log("Revision step failed to produce valid JSON. Returning original content.", 6)
             return initial_content
        revised_content_messy = json.dumps(revised_json, indent=2)
    else:
        word_count = len(re.findall(r'\b\w+\b', initial_content))
        min_words = max(100, int(word_count * 0.8))
        final_messages = Interface.SafeGenerateText(
            _Logger, revision_messages, revision_model, min_word_count_target=min_words
        )
        revised_content_messy = Interface.GetLastMessageText(final_messages)

    # --- FIXED: Handle revision failure gracefully ---
    if "[ERROR:" in revised_content_messy or not revised_content_messy.strip():
        _Logger.Log("Revision step failed or returned empty. Returning original content.", 6)
        return initial_content

    _Logger.Log("Content revision complete.", 4)

    # --- Step 3: Clean the revised content ---
    if is_json:
        return revised_content_messy
    else:
        cleaned_content = _clean_revised_content(Interface, _Logger, revised_content_messy)
        if "[ERROR:" in cleaned_content or not cleaned_content.strip():
             _Logger.Log("Final cleaning step failed. Returning the pre-cleaned (but revised) content.", 6)
             return revised_content_messy
        return cleaned_content
