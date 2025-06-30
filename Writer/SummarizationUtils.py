#!/usr/bin/python3

import json
import Writer.Config
import Writer.Prompts
import Writer.CritiqueRevision
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger
from Writer.NarrativeContext import NarrativeContext

def summarize_scene_and_extract_key_points(
    Interface: Interface,
    _Logger: Logger,
    scene_text: str,
    narrative_context: NarrativeContext,
    chapter_num: int,
    scene_num: int
) -> dict:
    """
    Summarizes a scene's content and extracts key points for the next scene to ensure coherence.
    This is a creative/analytical task and will undergo critique and revision.

    Returns:
        A dictionary with "summary" and "key_points_for_next_scene".
    """
    _Logger.Log(f"Generating summary for Chapter {chapter_num}, Scene {scene_num}", 4)

    # Prepare context for the summarization task
    task_description = f"You are summarizing scene {scene_num} of chapter {chapter_num}. The goal is to create a concise summary of the scene's events and to identify key plot points, character changes, or unresolved tensions that must be carried into the next scene to maintain narrative continuity."

    context_summary = narrative_context.get_full_story_summary_so_far(chapter_num)
    if chapter_ctx := narrative_context.get_chapter(chapter_num):
        if scene_num > 1:
            if prev_scene := chapter_ctx.get_scene(scene_num - 1):
                if prev_scene.summary:
                    context_summary += f"\nImmediately preceding this scene (C{chapter_num} S{scene_num-1}):\n{prev_scene.summary}"

    prompt = Writer.Prompts.SUMMARIZE_SCENE_PROMPT.format(scene_text=scene_text)
    messages = [Interface.BuildUserQuery(prompt)]

    _Logger.Log("Generating initial summary and key points...", 5)
    _, initial_summary_json = Interface.SafeGenerateJSON(
        _Logger, messages, Writer.Config.CHECKER_MODEL, _RequiredAttribs=["summary", "key_points_for_next_scene"]
    )
    initial_summary_text = json.dumps(initial_summary_json, indent=2)
    _Logger.Log("Initial summary and key points generated.", 5)

    # Critique and revise the summary for quality and coherence
    revised_summary_text = Writer.CritiqueRevision.critique_and_revise_creative_content(
        Interface,
        _Logger,
        initial_content=initial_summary_text,
        task_description=task_description,
        narrative_context_summary=context_summary,
        initial_user_prompt=narrative_context.initial_prompt,
        is_json=True
    )

    try:
        final_summary_data = json.loads(revised_summary_text)
        if "summary" not in final_summary_data or "key_points_for_next_scene" not in final_summary_data:
             _Logger.Log("Revised summary JSON is missing required keys. Falling back to initial summary.", 7)
             return initial_summary_json

        _Logger.Log(f"Successfully generated and revised summary for C{chapter_num} S{scene_num}.", 4)
        return final_summary_data
    except json.JSONDecodeError as e:
        _Logger.Log(f"Failed to parse final revised summary JSON: {e}. Falling back to initial summary.", 7)
        return initial_summary_json


def summarize_chapter(
    Interface: Interface,
    _Logger: Logger,
    chapter_text: str,
    narrative_context: NarrativeContext,
    chapter_num: int
) -> str:
    """
    Summarizes the content of a full chapter.
    This is a creative/analytical task and will undergo critique and revision.

    Returns:
        A string containing the chapter summary.
    """
    _Logger.Log(f"Generating summary for Chapter {chapter_num}", 4)

    task_description = f"You are summarizing the key events, character developments, and plot advancements of chapter {chapter_num} of a novel."
    context_summary = narrative_context.get_full_story_summary_so_far(chapter_num)

    prompt = Writer.Prompts.SUMMARIZE_CHAPTER_PROMPT.format(chapter_text=chapter_text)
    messages = [Interface.BuildUserQuery(prompt)]

    _Logger.Log("Generating initial chapter summary...", 5)
    messages = Interface.SafeGenerateText(
        _Logger, messages, Writer.Config.CHECKER_MODEL, min_word_count_target=50
    )
    initial_summary = Interface.GetLastMessageText(messages)
    _Logger.Log("Initial chapter summary generated.", 5)

    revised_summary = Writer.CritiqueRevision.critique_and_revise_creative_content(
        Interface,
        _Logger,
        initial_content=initial_summary,
        task_description=task_description,
        narrative_context_summary=context_summary,
        initial_user_prompt=narrative_context.initial_prompt,
        is_json=False
    )

    _Logger.Log(f"Successfully generated and revised summary for Chapter {chapter_num}.", 4)
    return revised_summary
