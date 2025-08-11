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


def _get_content_score(
    Interface: Interface,
    _Logger: Logger,
    content_to_score: str,
    scoring_prompt_template: str,
    # Context args
    task_description: str,
    narrative_context_summary: str,
    initial_user_prompt: str,
    style_guide: str,
    selected_model: str,
    justification: str = "No justification provided.",
) -> int:
    """
    Uses an LLM to get a numerical score for a piece of content.
    """
    _Logger.Log("Getting quality score for content...", 1)
    prompt = scoring_prompt_template.format(
        text_to_critique=content_to_score,
        task_description=task_description,
        narrative_context_summary=narrative_context_summary,
        initial_user_prompt=initial_user_prompt,
        style_guide=style_guide,
    )
    messages = [Interface.BuildUserQuery(prompt)]
    
    _, response_json = Interface.SafeGenerateJSON(
        _Logger, messages, selected_model, _RequiredAttribs=["score", "justification"]
    )
    
    score = response_json.get("score", 0)
    justification = response_json.get("justification", justification)
    
    try:
        score = int(score)
    except (ValueError, TypeError):
        _Logger.Log(f"Could not parse score as integer. Received: {score}. Defaulting to 0.", 6)
        score = 0

    _Logger.Log(f"Content score: {score}/100. Justification: {justification}", 1)
    return score


def _run_revision_cycle(
    Interface: Interface,
    _Logger: Logger,
    content_to_revise: str,
    critique_prompt_template: str,
    revision_prompt_template: str,
    scoring_prompt_template: str,
    cycle_name: str,
    # Context args
    task_description: str,
    narrative_context_summary: str,
    initial_user_prompt: str,
    style_guide: str,
    selected_model: str,
    justification: str = "No justification provided.",
) -> str:
    """
    A generic helper function to run an iterative critique-and-revision cycle.
    """
    current_content = content_to_revise
    MAX_ITERATIONS = 5
    SCORE_THRESHOLD = 95

    for i in range(MAX_ITERATIONS):
        _Logger.Log(f"Starting '{cycle_name}' revision cycle, iteration {i + 1}/{MAX_ITERATIONS}...", 3)

        # The first pass is always mandatory
        if i > 0:
            score = _get_content_score(
                Interface, _Logger, current_content, scoring_prompt_template,
                task_description, narrative_context_summary, initial_user_prompt, style_guide, selected_model,
                justification=justification
            )
            if score >= SCORE_THRESHOLD:
                _Logger.Log(f"'{cycle_name}' score ({score}) meets threshold of {SCORE_THRESHOLD}. Cycle complete.", 4)
                break
        
        # Step 1: Generate Critique
        critique_prompt = critique_prompt_template.format(
            text_to_critique=current_content,
            task_description=task_description,
            narrative_context_summary=narrative_context_summary,
            initial_user_prompt=initial_user_prompt,
            style_guide=style_guide,
        )
        critique_messages = [Interface.BuildUserQuery(critique_prompt)]
        critique_messages = Interface.SafeGenerateText(
            _Logger, critique_messages, selected_model, min_word_count_target=20
        )
        critique = Interface.GetLastMessageText(critique_messages)

        if "[ERROR:" in critique or "No issues found" in critique:
            _Logger.Log(f"'{cycle_name}' critique found no issues or failed. Skipping revision for this iteration.", 2)
            continue

        _Logger.Log(f"'{cycle_name}' critique received. Revising...", 3)

        # Step 2: Generate Revision
        revision_prompt = revision_prompt_template.format(
            original_text=current_content,
            critique=critique,
            style_guide=style_guide,
            narrative_context_summary=narrative_context_summary,
            task_description=task_description,
            initial_user_prompt=initial_user_prompt,
        )
        revision_messages = [Interface.BuildUserQuery(revision_prompt)]
        
        word_count = len(re.findall(r'\b\w+\b', current_content))
        min_words = max(100, int(word_count * 0.8))

        revision_messages = Interface.SafeGenerateText(
            _Logger, revision_messages, selected_model, min_word_count_target=min_words
        )
        revised_content = Interface.GetLastMessageText(revision_messages)

        if "[ERROR:" in revised_content or not revised_content.strip():
            _Logger.Log(f"'{cycle_name}' revision failed. Keeping previous version for this iteration.", 6)
        else:
            current_content = revised_content

    _Logger.Log(f"Finished '{cycle_name}' revision cycle.", 3)
    return current_content


def critique_and_revise_creative_content(
    Interface: Interface,
    _Logger: Logger,
    initial_content: str,
    task_description: str,
    narrative_context_summary: str,
    initial_user_prompt: str,
    style_guide: str,
    selected_model: str,
    is_json: bool = False, # is_json is no longer used in the new 3-step process for standard text
    justification: str = "No justification provided.",
) -> str:
    """
    Orchestrates the new 3-step critique and revision process.
    """
    if not initial_content or not initial_content.strip() or "[ERROR:" in initial_content:
        _Logger.Log("CritiqueRevision called with empty or invalid content. Skipping.", 6)
        return initial_content

    # --- Step 1: Style and Tone Revision ---
    style_revised_content = _run_revision_cycle(
        Interface, _Logger, initial_content,
        Writer.Prompts.STYLE_CRITIQUE_PROMPT,
        Writer.Prompts.REVISE_FOR_STYLE_PROMPT,
        Writer.Prompts.STYLE_SCORE_PROMPT,
        "Style",
        task_description, narrative_context_summary, initial_user_prompt, style_guide, selected_model,
        justification=justification
    )

    # --- Step 2: Structure and Length Revision ---
    structure_revised_content = _run_revision_cycle(
        Interface, _Logger, style_revised_content,
        Writer.Prompts.STRUCTURE_CRITIQUE_PROMPT,
        Writer.Prompts.REVISE_FOR_STRUCTURE_PROMPT,
        Writer.Prompts.STRUCTURE_SCORE_PROMPT,
        "Structure",
        task_description, narrative_context_summary, initial_user_prompt, style_guide, selected_model,
        justification=justification
    )

    # --- Step 3: Consistency Revision (Last Creative Step) ---
    consistency_revised_content = _run_revision_cycle(
        Interface, _Logger, structure_revised_content,
        Writer.Prompts.CONSISTENCY_CRITIQUE_PROMPT,
        Writer.Prompts.REVISE_FOR_CONSISTENCY_PROMPT,
        Writer.Prompts.CONSISTENCY_SCORE_PROMPT,
        "Consistency",
        task_description, narrative_context_summary, initial_user_prompt, style_guide, selected_model,
        justification=justification
    )

    # --- Step 4: Final Cleanup ---
    _Logger.Log("All revision cycles complete. Performing final cleanup.", 2)
    cleaned_content = _clean_revised_content(Interface, _Logger, consistency_revised_content)

    if "[ERROR:" in cleaned_content or not cleaned_content.strip():
        _Logger.Log("Final cleaning step failed. Returning the pre-cleaned (but fully revised) content.", 6)
        return consistency_revised_content
        
    return cleaned_content
