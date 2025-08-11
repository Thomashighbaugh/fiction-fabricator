#!/usr/bin/python3

import Writer.Config
import Writer.CritiqueRevision
import Writer.Prompts
from Writer.Interface.Wrapper import Interface
from Writer.NarrativeContext import NarrativeContext
from Writer.PrintUtils import Logger


def ChapterOutlineToScenes(
    Interface: Interface,
    _Logger: Logger,
    _ThisChapterOutline: str,
    narrative_context: NarrativeContext,
    _ChapterNum: int,
    selected_model: str,
) -> str:
    """
    Converts a chapter outline into a more detailed outline for each scene within that chapter.
    This process involves a creative critique and revision cycle to ensure a high-quality,
    well-structured scene breakdown.

    Args:
        Interface: The LLM interface wrapper.
        _Logger: The logger instance.
        _ThisChapterOutline: The outline for the specific chapter to be broken down.
        narrative_context: The context object for the entire novel.
        _ChapterNum: The number of the chapter being processed.

    Returns:
        A string containing the detailed, scene-by-scene markdown outline for the chapter.
    """
    _Logger.Log(f"Splitting Chapter {_ChapterNum} into a scene-by-scene outline.", 2)

    # --- Step 1: Initial Generation ---
    _Logger.Log("Generating initial scene breakdown...", 5)
    initial_prompt = Writer.Prompts.CHAPTER_TO_SCENES.format(
        _ThisChapter=_ThisChapterOutline,
        _Outline=narrative_context.base_novel_outline_markdown,
        _Prompt=narrative_context.initial_prompt,
    )

    messages = [
        Interface.BuildSystemQuery(Writer.Prompts.LITERARY_STYLE_GUIDE),
        Interface.BuildUserQuery(initial_prompt),
    ]

    response_messages = Interface.SafeGenerateText(
        _Logger, messages, selected_model, min_word_count_target=100
    )
    initial_scene_breakdown = Interface.GetLastMessageText(response_messages)
    _Logger.Log("Finished initial scene breakdown generation.", 5)

    # --- Step 2: Critique and Revise ---
    _Logger.Log("Critiquing and revising scene breakdown for coherence and quality...", 3)

    task_description = f"Break down the provided chapter outline for Chapter {_ChapterNum} into a detailed, scene-by-scene plan. Each scene should have a clear purpose, setting, character list, and a summary of events, contributing to the chapter's overall arc and adhering to the novel's dark, literary style."

    context_summary = narrative_context.get_context_for_chapter_generation(_ChapterNum)
    context_summary += f"\n\nThis chapter's specific outline, which you need to expand into scenes, is:\n{_ThisChapterOutline}"

    revised_scene_breakdown = Writer.CritiqueRevision.critique_and_revise_creative_content(
        Interface,
        _Logger,
        initial_content=initial_scene_breakdown,
        task_description=task_description,
        narrative_context_summary=context_summary,
        initial_user_prompt=narrative_context.initial_prompt,
        style_guide=narrative_context.style_guide,
        selected_model=selected_model,
    )

    _Logger.Log(f"Finished splitting Chapter {_ChapterNum} into scenes.", 2)
    return revised_scene_breakdown

