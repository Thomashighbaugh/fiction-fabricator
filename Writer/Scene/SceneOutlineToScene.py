#!/usr/bin/python3

import Writer.Config
import Writer.CritiqueRevision
import Writer.Prompts
import Writer.SummarizationUtils
from Writer.Interface.Wrapper import Interface
from Writer.NarrativeContext import NarrativeContext, SceneContext
from Writer.PrintUtils import Logger

def _is_scene_complete(
    Interface: Interface,
    _Logger: Logger,
    scene_outline: str,
    full_scene_text: str,
) -> bool:
    """
    Uses an LLM to check if the generated scene text fulfills the scene's outline/goals.
    """
    _Logger.Log("Checking if scene has met its objectives...", 1)
    prompt = Writer.Prompts.IS_SCENE_COMPLETE_PROMPT.format(
        _SceneOutline=scene_outline,
        full_scene_text=full_scene_text
    )
    messages = [Interface.BuildUserQuery(prompt)]

    # This is a non-creative check, so we use a checker model and SafeGenerateJSON
    _, response_json = Interface.SafeGenerateJSON(
        _Logger, messages, Writer.Config.CHECKER_MODEL, _RequiredAttribs=["IsComplete"]
    )
    
    is_complete = response_json.get("IsComplete", False)
    if isinstance(is_complete, str):
        is_complete = is_complete.lower() == 'true'

    _Logger.Log(f"Scene completion check returned: {is_complete}", 1)
    return is_complete

def SceneOutlineToScene(
    Interface: Interface,
    _Logger: Logger,
    scene_context: SceneContext, # Receives the mutable scene context object
    narrative_context: NarrativeContext,
    _ChapterNum: int,
    _SceneNum: int,
) -> str:
    """
    Generates the full text for a single scene by building it iteratively in pieces.
    Each piece is generated, critiqued, revised, and summarized. The summary of
    the previous piece informs the generation of the next, ensuring coherence.

    Args:
        Interface: The LLM interface wrapper.
        _Logger: The logger instance.
        scene_context: The context object for the specific scene being written.
        narrative_context: The context object for the entire novel.
        _ChapterNum: The number of the current chapter.
        _SceneNum: The number of the current scene.

    Returns:
        A string containing the fully written scene text.
    """
    _Logger.Log(f"Starting iterative SceneOutlineToScene generation for C{_ChapterNum} S{_SceneNum}.", 2)
    MAX_PIECES = 7 # Safety break to prevent infinite loops

    # --- Iterative Scene Generation Loop ---
    while len(scene_context.pieces) < MAX_PIECES:
        
        # Step 1: Get summary of what's been written so far in this scene
        summary_of_previous_pieces = scene_context.get_summary_of_all_pieces()
        if not summary_of_previous_pieces:
            summary_of_previous_pieces = "This is the beginning of the scene."
        _Logger.Log(f"Context for next piece: \"{summary_of_previous_pieces}\"", 1)

        # Step 2: Generate the next piece of the scene
        _Logger.Log(f"Generating piece {len(scene_context.pieces) + 1} for C{_ChapterNum} S{_SceneNum}...", 5)
        
        # Determine the right prompt (start of scene vs. continuation)
        if not scene_context.pieces:
            # First piece: Use the main scene generation prompt
            generation_prompt = Writer.Prompts.SCENE_OUTLINE_TO_SCENE.format(
                narrative_context=narrative_context.get_context_for_scene_generation(_ChapterNum, _SceneNum),
                _SceneOutline=scene_context.initial_outline,
                style_guide=narrative_context.style_guide
            )
        else:
            # Subsequent pieces: Use the continuation prompt
            generation_prompt = Writer.Prompts.CONTINUE_SCENE_PIECE_PROMPT.format(
                summary_of_previous_pieces=summary_of_previous_pieces,
                _SceneOutline=scene_context.initial_outline,
                style_guide=narrative_context.style_guide
            )
        
        messages = [Interface.BuildSystemQuery(Writer.Prompts.LITERARY_STYLE_GUIDE), Interface.BuildUserQuery(generation_prompt)]

        # Generate the initial text for the piece
        response_messages = Interface.SafeGenerateText(
            _Logger, messages, Writer.Config.CHAPTER_STAGE1_WRITER_MODEL, min_word_count_target=250 # Aim for substantial pieces
        )
        initial_piece_text = Interface.GetLastMessageText(response_messages)

        # Step 3: Critique and Revise the generated piece
        _Logger.Log(f"Critiquing and revising piece {len(scene_context.pieces) + 1}...", 3)
        task_description = f"Write a piece of a scene for Chapter {_ChapterNum}, Scene {_SceneNum}. The writing must be compelling, adhere to a dark literary style, and seamlessly continue from the previous text."
        
        revised_piece_text = Writer.CritiqueRevision.critique_and_revise_creative_content(
            Interface,
            _Logger,
            initial_content=initial_piece_text,
            task_description=task_description,
            narrative_context_summary=narrative_context.get_context_for_scene_generation(_ChapterNum, _SceneNum),
            initial_user_prompt=narrative_context.initial_prompt,
            style_guide=narrative_context.style_guide
        )

        # Step 4: Summarize the revised piece for the next iteration's context
        piece_summary = Writer.SummarizationUtils.summarize_scene_piece(Interface, _Logger, revised_piece_text)
        
        # Step 5: Add the completed piece to the scene context
        scene_context.add_piece(revised_piece_text, piece_summary)
        _Logger.Log(f"Finished piece {len(scene_context.pieces)}. Current scene length: {len(scene_context.generated_content.split())} words.", 4)
        
        # Step 6: Check if the scene is complete
        if _is_scene_complete(Interface, _Logger, scene_context.initial_outline, scene_context.generated_content):
            _Logger.Log(f"Scene C{_ChapterNum} S{_SceneNum} is complete.", 5)
            break
    else:
        # This block executes if the while loop finishes due to MAX_PIECES being reached
        _Logger.Log(f"Scene C{_ChapterNum} S{_SceneNum} reached max pieces ({MAX_PIECES}). Forcing scene to conclude.", 6)

    final_scene_text = scene_context.generated_content
    _Logger.Log(f"Finished SceneOutlineToScene generation for C{_ChapterNum} S{_SceneNum}. Final word count: {len(final_scene_text.split())}", 2)
    return final_scene_text
