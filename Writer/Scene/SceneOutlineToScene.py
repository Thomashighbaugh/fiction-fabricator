#!/usr/bin/python3

import Writer.Config
import Writer.CritiqueRevision
import Writer.Prompts
from Writer.Interface.Wrapper import Interface
from Writer.NarrativeContext import NarrativeContext
from Writer.PrintUtils import Logger


def SceneOutlineToScene(
    Interface: Interface,
    _Logger: Logger,
    _ThisSceneOutline: str,
    narrative_context: NarrativeContext,
    _ChapterNum: int,
    _SceneNum: int,
) -> str:
    """
    Generates the full text for a single scene based on its detailed outline.
    This is a creative task that undergoes a critique and revision cycle.

    Args:
        Interface: The LLM interface wrapper.
        _Logger: The logger instance.
        _ThisSceneOutline: The detailed markdown outline for the specific scene to be written.
        narrative_context: The context object for the entire novel.
        _ChapterNum: The number of the current chapter.
        _SceneNum: The number of the current scene.

    Returns:
        A string containing the fully written scene text.
    """
    _Logger.Log(f"Starting SceneOutline -> Scene generation for C{_ChapterNum} S{_SceneNum}.", 2)

    # --- Step 1: Initial Generation ---
    _Logger.Log("Generating initial scene text...", 5)

    scene_context_for_prompt = narrative_context.get_context_for_scene_generation(
        _ChapterNum, _SceneNum
    )

    initial_prompt = Writer.Prompts.SCENE_OUTLINE_TO_SCENE.format(
        _SceneOutline=_ThisSceneOutline,
        narrative_context=scene_context_for_prompt,
    )

    messages = [
        Interface.BuildSystemQuery(Writer.Prompts.DEFAULT_SYSTEM_PROMPT),
        Interface.BuildUserQuery(initial_prompt),
    ]

    response_messages = Interface.SafeGenerateText(
        _Logger, messages, Writer.Config.CHAPTER_STAGE1_WRITER_MODEL, _MinWordCount=100
    )
    initial_scene_text = Interface.GetLastMessageText(response_messages)
    _Logger.Log("Finished initial scene generation.", 5)

    # --- Step 2: Critique and Revise ---
    _Logger.Log(f"Critiquing and revising C{_ChapterNum} S{_SceneNum} for quality...", 3)

    task_description = f"Write a full, compelling scene for Chapter {_ChapterNum}, Scene {_SceneNum}, based on its outline. The scene should include engaging prose, character interactions, and dialogue, and it must seamlessly connect with the preceding events."

    context_summary = scene_context_for_prompt

    revised_scene_text = Writer.CritiqueRevision.critique_and_revise_creative_content(
        Interface,
        _Logger,
        initial_content=initial_scene_text,
        task_description=task_description,
        narrative_context_summary=context_summary,
        initial_user_prompt=narrative_context.initial_prompt,
    )

    _Logger.Log(f"Finished SceneOutline -> Scene generation for C{_ChapterNum} S{_SceneNum}.", 2)
    return revised_scene_text
