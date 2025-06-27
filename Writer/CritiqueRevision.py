#!/usr/bin/python3

import json
import Writer.Config
import Writer.Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger


def critique_and_revise_creative_content(
    Interface: Interface,
    _Logger: Logger,
    initial_content: str,
    task_description: str,
    narrative_context_summary: str,
    initial_user_prompt: str,
    is_json: bool = False,
) -> str:
    """
    Orchestrates the critique and revision process for a piece of generated creative content.
    This process is a single pass: critique -> revise.

    1. Prompts a critique LLM to generate feedback on the initial_content.
    2. Prompts a revision LLM to revise the initial_content based on the received critique.

    Args:
        Interface: The LLM interface wrapper.
        _Logger: The logger instance.
        initial_content: The text to be critiqued and revised.
        task_description: A description of what the content was supposed to achieve.
        narrative_context_summary: A summary of the story so far to provide context.
        initial_user_prompt: The original prompt from the user, to ensure alignment.
        is_json: A flag to indicate if the content is JSON and should be handled accordingly.

    Returns:
        The revised content as a string.
    """

    # --- Step 1: Generate Critique ---
    _Logger.Log("Starting critique generation for the latest content.", 5)

    json_guidance = (
        "The content is JSON. Focus your critique on the substance, clarity, and narrative value "
        "of the data within the JSON structure, not just the format. Respond with your critique as a plain string."
    ) if is_json else "Respond with your critique as a plain string."

    critique_prompt = Writer.Prompts.CRITIQUE_CREATIVE_CONTENT_PROMPT.format(
        text_to_critique=initial_content,
        task_description=task_description,
        narrative_context_summary=narrative_context_summary,
        initial_user_prompt=initial_user_prompt,
        is_json_output=json_guidance
    )

    critique_messages = [Interface.BuildUserQuery(critique_prompt)]

    critique_model = Writer.Config.CRITIQUE_LLM if hasattr(Writer.Config, 'CRITIQUE_LLM') else Writer.Config.REVISION_MODEL

    critique_messages = Interface.SafeGenerateText(
        _Logger,
        critique_messages,
        critique_model,
        _MinWordCount=20
    )
    critique = Interface.GetLastMessageText(critique_messages)
    _Logger.Log(f"Critique received:\n---\n{critique}\n---", 4)

    # --- Step 2: Generate Revision ---
    _Logger.Log("Starting revision based on the received critique.", 5)

    json_instructions = (
        "Important: Your final output must be a single, valid JSON object, just like the original. "
        "Revise the *content* within the JSON structure based on the critique. "
        "Do not add any explanatory text, comments, or markdown outside of the JSON object itself."
    ) if is_json else (
        "Ensure your final output is only the revised text. Maintain the original's intent and narrative role, "
        "but improve it by addressing the points in the critique. Do not write a reflection on the changes."
    )

    revision_prompt = Writer.Prompts.REVISE_CREATIVE_CONTENT_BASED_ON_CRITIQUE_PROMPT.format(
        original_text=initial_content,
        critique=critique,
        task_description=task_description,
        narrative_context_summary=narrative_context_summary,
        initial_user_prompt=initial_user_prompt,
        json_instructions=json_instructions
    )

    revision_messages = [Interface.BuildUserQuery(revision_prompt)]

    revision_model = Writer.Config.CHAPTER_REVISION_WRITER_MODEL
    revision_format = "json" if is_json else None

    if is_json:
        final_messages, _ = Interface.SafeGenerateJSON(
            _Logger,
            revision_messages,
            revision_model
        )
        revised_content = Interface.GetLastMessageText(final_messages)
    else:
        min_words = max(10, int(len(initial_content.split()) * 0.75))
        final_messages = Interface.SafeGenerateText(
            _Logger,
            revision_messages,
            revision_model,
            _Format=revision_format,
            _MinWordCount=min_words
        )
        revised_content = Interface.GetLastMessageText(final_messages)

    _Logger.Log("Content revision complete.", 4)
    return revised_content
