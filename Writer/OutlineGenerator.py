#!/usr/bin/python3

import Writer.Config
import Writer.LLMEditor
import Writer.PrintUtils
import Writer.Prompts
import Writer.CritiqueRevision
import Writer.Chapter.ChapterDetector
from Writer.Interface.Wrapper import Interface
from Writer.NarrativeContext import NarrativeContext
from Writer.PrintUtils import Logger


def GenerateStoryElements(
    Interface: Interface,
    _Logger: Logger,
    _OutlinePrompt: str,
    narrative_context: NarrativeContext,
) -> str:
    """Generates the core story elements using a critique and revision cycle."""

    prompt = Writer.Prompts.GENERATE_STORY_ELEMENTS_PROMPT.format(_OutlinePrompt=_OutlinePrompt)

    _Logger.Log("Generating initial Story Elements...", 4)
    messages = [Interface.BuildUserQuery(prompt)]
    messages = Interface.SafeGenerateText(
        _Logger, messages, Writer.Config.INITIAL_OUTLINE_WRITER_MODEL, _MinWordCount=150
    )
    initial_elements = Interface.GetLastMessageText(messages)
    _Logger.Log("Done generating initial Story Elements.", 4)

    _Logger.Log("Critiquing and revising Story Elements for quality...", 3)
    task_description = "Generate the core story elements (genre, theme, plot points, setting, characters) based on a user's prompt. The output should be a detailed, well-structured markdown document."
    context_summary = f"The user has provided the following high-level prompt for a new story:\n{_OutlinePrompt}"

    revised_elements = Writer.CritiqueRevision.critique_and_revise_creative_content(
        Interface,
        _Logger,
        initial_content=initial_elements,
        task_description=task_description,
        narrative_context_summary=context_summary,
        initial_user_prompt=_OutlinePrompt,
    )

    _Logger.Log("Finished revising Story Elements.", 4)
    return revised_elements


def GenerateOutline(
    Interface: Interface,
    _Logger: Logger,
    _OutlinePrompt: str,
    narrative_context: NarrativeContext,
) -> NarrativeContext:
    """
    Generates the complete story outline, including story elements and chapter breakdowns,
    and populates the provided NarrativeContext object.
    """

    # --- Step 1: Extract Important Base Context ---
    _Logger.Log("Extracting important base context from prompt...", 4)
    base_context_prompt = Writer.Prompts.GET_IMPORTANT_BASE_PROMPT_INFO.format(
        _Prompt=_OutlinePrompt
    )
    messages = [Interface.BuildUserQuery(base_context_prompt)]
    messages = Interface.SafeGenerateText(_Logger, messages, Writer.Config.INFO_MODEL)
    base_context = Interface.GetLastMessageText(messages)
    narrative_context.set_base_prompt_important_info(base_context)
    _Logger.Log("Done extracting important base context.", 4)

    # --- Step 2: Generate Story Elements ---
    story_elements = GenerateStoryElements(
        Interface, _Logger, _OutlinePrompt, narrative_context
    )
    narrative_context.set_story_elements(story_elements)

    # --- Step 3: Generate Initial Rough Outline ---
    _Logger.Log("Generating initial rough outline...", 4)
    initial_outline_prompt = Writer.Prompts.INITIAL_OUTLINE_PROMPT.format(
        StoryElements=story_elements, _OutlinePrompt=_OutlinePrompt
    )
    messages = [Interface.BuildUserQuery(initial_outline_prompt)]
    messages = Interface.SafeGenerateText(
        _Logger, messages, Writer.Config.INITIAL_OUTLINE_WRITER_MODEL, _MinWordCount=250
    )
    outline = Interface.GetLastMessageText(messages)
    _Logger.Log("Done generating initial rough outline.", 4)

    # --- Step 4: Revision Loop for the Rough Outline ---
    _Logger.Log("Entering feedback/revision loop for the rough outline...", 3)
    iterations = 0
    while True:
        iterations += 1

        is_complete = Writer.LLMEditor.GetOutlineRating(Interface, _Logger, outline)

        if iterations > Writer.Config.OUTLINE_MAX_REVISIONS:
            _Logger.Log("Max revisions reached. Exiting revision loop.", 6)
            break
        if iterations > Writer.Config.OUTLINE_MIN_REVISIONS and is_complete:
            _Logger.Log("Outline meets quality standards. Exiting revision loop.", 5)
            break

        _Logger.Log(f"Outline Revision Iteration {iterations}", 4)

        feedback = Writer.LLMEditor.GetFeedbackOnOutline(Interface, _Logger, outline)

        revision_prompt = Writer.Prompts.OUTLINE_REVISION_PROMPT.format(
            _Outline=outline, _Feedback=feedback
        )
        _Logger.Log("Revising outline based on feedback...", 2)
        revision_messages = [Interface.BuildUserQuery(revision_prompt)]
        revision_messages = Interface.SafeGenerateText(
            _Logger,
            revision_messages,
            Writer.Config.INITIAL_OUTLINE_WRITER_MODEL,
            _MinWordCount=250,
        )
        outline = Interface.GetLastMessageText(revision_messages)
        _Logger.Log("Done revising outline.", 2)

    _Logger.Log("Quality standard met. Exiting feedback/revision loop.", 4)

    # --- Step 5: Enforce Minimum Chapter Count ---
    num_chapters = Writer.Chapter.ChapterDetector.LLMCountChapters(Interface, _Logger, outline)
    if num_chapters > 0 and num_chapters < Writer.Config.MINIMUM_CHAPTERS:
        _Logger.Log(f"Outline has {num_chapters} chapters, which is less than the minimum of {Writer.Config.MINIMUM_CHAPTERS}. Expanding...", 6)
        expansion_prompt = Writer.Prompts.EXPAND_OUTLINE_TO_MIN_CHAPTERS_PROMPT.format(
            _Outline=outline, _MinChapters=Writer.Config.MINIMUM_CHAPTERS
        )
        messages = [Interface.BuildUserQuery(expansion_prompt)]
        messages = Interface.SafeGenerateText(
            _Logger, messages, Writer.Config.INITIAL_OUTLINE_WRITER_MODEL, _MinWordCount=len(outline.split()) * 1.1
        )
        outline = Interface.GetLastMessageText(messages)
        _Logger.Log("Outline expanded to meet minimum chapter count.", 5)

    narrative_context.set_base_novel_outline(outline)

    # --- Step 6: Generate Expanded Per-Chapter Outline (if enabled) ---
    if Writer.Config.EXPAND_OUTLINE:
        _Logger.Log("Starting per-chapter outline expansion...", 3)
        # Recalculate chapter count after potential expansion
        final_num_chapters = Writer.Chapter.ChapterDetector.LLMCountChapters(Interface, _Logger, outline)

        if final_num_chapters > 0 and final_num_chapters < 50:
            expanded_outlines = []
            for i in range(1, final_num_chapters + 1):
                chapter_outline = GeneratePerChapterOutline(
                    Interface, _Logger, i, outline, narrative_context
                )
                expanded_outlines.append(chapter_outline)

            full_expanded_outline = "\n\n".join(expanded_outlines)
            narrative_context.set_expanded_novel_outline(full_expanded_outline)
            _Logger.Log("Finished expanding all chapter outlines.", 3)
        else:
            _Logger.Log(f"Could not determine valid chapter count ({final_num_chapters}). Skipping expansion.", 6)

    return narrative_context


def GeneratePerChapterOutline(
    Interface: Interface,
    _Logger: Logger,
    _ChapterNum: int,
    _FullOutline: str,
    narrative_context: NarrativeContext,
) -> str:
    """
    Generates a more detailed, scene-by-scene outline for a single chapter.
    This is a creative task and uses a critique/revision cycle.
    """
    _Logger.Log(f"Generating detailed outline for Chapter {_ChapterNum}", 5)

    prompt = Writer.Prompts.CHAPTER_OUTLINE_PROMPT.format(
        _Chapter=_ChapterNum, _Outline=_FullOutline
    )
    messages = [Interface.BuildUserQuery(prompt)]
    messages = Interface.SafeGenerateText(
        _Logger, messages, Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL, _MinWordCount=50
    )
    initial_chapter_outline = Interface.GetLastMessageText(messages)

    _Logger.Log(f"Critiquing and revising outline for Chapter {_ChapterNum}...", 3)
    task_description = f"Generate a detailed, scene-by-scene outline for Chapter {_ChapterNum}, based on the main story outline. The detailed outline should break down the chapter's events, character beats, and setting for each scene."
    context_summary = narrative_context.get_full_story_summary_so_far(_ChapterNum)
    context_summary += f"\n\nMain Story Outline:\n{_FullOutline}"

    revised_chapter_outline = Writer.CritiqueRevision.critique_and_revise_creative_content(
        Interface,
        _Logger,
        initial_content=initial_chapter_outline,
        task_description=task_description,
        narrative_context_summary=context_summary,
        initial_user_prompt=narrative_context.initial_prompt,
    )

    _Logger.Log(f"Done generating detailed outline for Chapter {_ChapterNum}.", 5)
    return revised_chapter_outline
