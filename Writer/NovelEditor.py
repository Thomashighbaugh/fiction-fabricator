#!/usr/bin/python3

import Writer.Config
import Writer.Prompts
import Writer.CritiqueRevision
import Writer.Statistics
from Writer.Interface.Wrapper import Interface
from Writer.NarrativeContext import NarrativeContext
from Writer.PrintUtils import Logger


def EditNovel(
    Interface: Interface,
    _Logger: Logger,
    narrative_context: NarrativeContext,
) -> NarrativeContext:
    """
    Performs a final, holistic editing pass on the entire novel.
    It iterates through each chapter, re-editing it with the full context of the novel so far,
    applying a critique-and-revision cycle to each edit.

    Args:
        Interface: The LLM interface wrapper.
        _Logger: The logger instance.
        narrative_context: The context object containing all chapters and story info.

    Returns:
        The updated NarrativeContext object with edited chapters.
    """
    _Logger.Log("Starting final holistic novel editing pass...", 2)

    total_chapters = len(narrative_context.chapters)
    if total_chapters == 0:
        _Logger.Log("No chapters found in narrative context to edit.", 6)
        return narrative_context

    # Create a static list of original chapter content to use as context
    original_chapters_content = {
        chap.chapter_number: chap.generated_content for chap in narrative_context.chapters
    }

    for i in range(total_chapters):
        chapter_num = i + 1
        _Logger.Log(f"--- Editing Chapter {chapter_num}/{total_chapters} ---", 3)

        chapter_to_edit_content = original_chapters_content.get(chapter_num)
        if not chapter_to_edit_content:
            _Logger.Log(f"Chapter {chapter_num} has no content to edit. Skipping.", 6)
            continue

        # --- Step 1: Initial Edit Generation ---
        _Logger.Log(f"Generating initial edit for Chapter {chapter_num}...", 5)

        # Build the context from all *other* chapters using the original, unedited content
        novel_text_context = ""
        for num, content in original_chapters_content.items():
            if num != chapter_num:
                novel_text_context += f"### Chapter {num}\n\n{content}\n\n\n"

        prompt = Writer.Prompts.CHAPTER_EDIT_PROMPT.format(
            _Outline=narrative_context.base_novel_outline_markdown,
            NovelText=novel_text_context,
            i=chapter_num,
            _Chapter=chapter_to_edit_content,
            style_guide=narrative_context.style_guide
        )

        messages = [
            Interface.BuildSystemQuery(narrative_context.style_guide),
            Interface.BuildUserQuery(prompt)
        ]

        min_words = int(len(chapter_to_edit_content.split()) * 0.9)

        messages = Interface.SafeGenerateText(
            _Logger, messages, Writer.Config.CHAPTER_REVISION_WRITER_MODEL, min_word_count_target=min_words
        )
        initial_edited_chapter = Interface.GetLastMessageText(messages)

        # --- Step 2: Critique and Revise the Edit ---
        _Logger.Log(f"Critiquing and revising the edit for Chapter {chapter_num}...", 4)

        task_description = (
            f"You are performing a final, holistic edit on Chapter {chapter_num}. "
            "Your goal is to refine the chapter to improve its pacing, prose, and consistency, "
            f"ensuring it flows perfectly with the preceding and succeeding chapters and adheres to the novel's dark, literary style."
        )

        context_summary = narrative_context.get_full_story_summary_so_far()

        revised_edited_chapter = Writer.CritiqueRevision.critique_and_revise_creative_content(
            Interface,
            _Logger,
            initial_content=initial_edited_chapter,
            task_description=task_description,
            narrative_context_summary=context_summary,
            initial_user_prompt=narrative_context.initial_prompt,
            style_guide=narrative_context.style_guide,
        )

        # Update the chapter in the narrative context object
        chapter_obj = narrative_context.get_chapter(chapter_num)
        if chapter_obj:
            chapter_obj.set_generated_content(revised_edited_chapter)

        chapter_word_count = Writer.Statistics.GetWordCount(revised_edited_chapter)
        _Logger.Log(f"New word count for edited Chapter {chapter_num}: {chapter_word_count}", 3)

        _Logger.Log(f"--- Finished editing Chapter {chapter_num} ---", 3)

    _Logger.Log("Finished final novel editing pass.", 2)
    return narrative_context
