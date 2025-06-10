# File: Writer/NovelEditor.py
# Purpose: Performs an optional global editing pass on the assembled novel for consistency and flow.

"""
Global Novel Editing Module.

This module provides functionality for an optional, high-level editing pass
over the entire assembled novel (all generated chapters). Its purpose is to:
- Enhance inter-chapter consistency in plot, characterization, and tone.
- Smooth out transitions between chapters.
- Identify and potentially refine areas where foreshadowing could be
  strengthened or payoffs made more impactful, based on the complete narrative.
- Improve overall pacing across the entire story arc.

This pass is distinct from the per-chapter or per-scene revisions. It assumes
individual chapters are already reasonably well-written and focuses on their
integration into the larger work.
"""

import Writer.Config as Config
import Writer.Prompts as Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger
from Writer.Statistics import get_word_count
from typing import List, Dict, Any, Optional

# Heuristic: 1 word is approx 1.5 tokens in English, but can vary.
WORD_TO_TOKEN_RATIO = 1.5


def edit_novel_globally(
    interface: Interface,
    logger: Logger,
    assembled_chapters: List[str],
    overall_story_outline: str,
) -> List[str]:
    """
    Performs a global editing pass on a list of assembled chapter texts.
    Each chapter is reviewed by an LLM in the context of preceding chapters
    and the overall story outline to improve global narrative cohesion.

    Args:
        interface (Interface): The LLM interaction wrapper.
        logger (Logger): The logging instance.
        assembled_chapters (List[str]): A list of strings, where each string is
                                        the text of an assembled and potentially
                                        individually revised chapter.
        overall_story_outline (str): The original high-level, chapter-by-chapter
                                     plot outline for the entire story.

    Returns:
        List[str]: A list of globally edited chapter texts. If editing fails for
                   a chapter, the pre-edit version of that chapter might be returned.
    """
    if not assembled_chapters:
        logger.Log(
            "No chapters provided for global novel editing. Returning empty list.", 1
        )
        return []

    if not overall_story_outline or not overall_story_outline.strip():
        logger.Log(
            "Overall story outline is empty. Global editing context is limited.", 6
        )
        overall_story_outline = "Overall story outline not provided for full context."

    total_chapters = len(assembled_chapters)
    logger.Log(
        f"Starting global novel editing pass for {total_chapters} chapter(s)...", 2
    )

    globally_edited_chapters: List[str] = list(assembled_chapters)

    novel_text_so_far_for_context = ""

    for chapter_idx, current_chapter_text in enumerate(globally_edited_chapters):
        chapter_num = chapter_idx + 1
        original_word_count = get_word_count(current_chapter_text)
        logger.Log(
            f"Performing global edit review on Chapter {chapter_num}/{total_chapters} (Word count: {original_word_count})...",
            3,
        )

        if not current_chapter_text or not current_chapter_text.strip():
            logger.Log(
                f"Chapter {chapter_num} is empty. Skipping global edit for this chapter.",
                5,
            )
            novel_text_so_far_for_context += f"\n\n## Chapter {chapter_num} (Empty)\n\n"
            continue

        try:
            prompt_template = Prompts.GLOBAL_NOVEL_CHAPTER_EDIT_PROMPT
            text_before_current_chapter = novel_text_so_far_for_context

            formatted_prompt = prompt_template.format(
                ChapterNum=chapter_num,
                _OverallStoryOutline=overall_story_outline,
                _NovelTextSoFar=(
                    text_before_current_chapter
                    if text_before_current_chapter
                    else "This is the first chapter of the novel."
                ),
                _ChapterTextToEdit=current_chapter_text,
            )
        except KeyError as e:
            error_msg = f"Formatting error in GLOBAL_NOVEL_CHAPTER_EDIT_PROMPT for Chapter {chapter_num}: Missing key {e}"
            logger.Log(error_msg, 7)
            novel_text_so_far_for_context += (
                f"\n\n## Chapter {chapter_num}\n\n{current_chapter_text}\n\n"
            )
            continue
        except Exception as e:
            error_msg = f"Unexpected error formatting global edit prompt for Chapter {chapter_num}: {e}"
            logger.Log(error_msg, 7)
            novel_text_so_far_for_context += (
                f"\n\n## Chapter {chapter_num}\n\n{current_chapter_text}\n\n"
            )
            continue

        messages: List[Dict[str, Any]] = [
            interface.build_system_query(
                Prompts.DEFAULT_SYSTEM_PROMPT
            ),
            interface.build_user_query(formatted_prompt),
        ]

        try:
            MIN_WORDS_AFTER_GLOBAL_EDIT = max(50, int(original_word_count * 0.75))
            MAX_TOKENS_FOR_GLOBAL_EDIT = int(original_word_count * WORD_TO_TOKEN_RATIO * 1.15)
            
            response_messages = interface.safe_generate_text(
                logger,
                messages,
                Config.CHAPTER_REVISION_WRITER_MODEL,
                min_word_count=MIN_WORDS_AFTER_GLOBAL_EDIT,
                max_tokens=MAX_TOKENS_FOR_GLOBAL_EDIT,
            )

            updated_chapter_text: str = interface.get_last_message_text(
                response_messages
            )

            if not updated_chapter_text or "Error:" in updated_chapter_text:
                logger.Log(
                    f"LLM failed global edit for Chapter {chapter_num} or returned an error. Keeping pre-edit version.",
                    6,
                )
                novel_text_so_far_for_context += (
                    f"\n\n## Chapter {chapter_num}\n\n{current_chapter_text}\n\n"
                )
            else:
                globally_edited_chapters[chapter_idx] = updated_chapter_text
                edited_word_count = get_word_count(updated_chapter_text)
                logger.Log(
                    f"Global edit review for Chapter {chapter_num} complete. New word count: {edited_word_count}.",
                    4,
                )
                novel_text_so_far_for_context += (
                    f"\n\n## Chapter {chapter_num}\n\n{updated_chapter_text}\n\n"
                )

        except Exception as e:
            error_msg_runtime = f"An unexpected critical error during global editing of Chapter {chapter_num}: {e}"
            logger.Log(error_msg_runtime, 7)
            novel_text_so_far_for_context += (
                f"\n\n## Chapter {chapter_num}\n\n{current_chapter_text}\n\n"
            )

    logger.Log(
        f"Global novel editing pass complete for all {total_chapters} chapter(s).", 2
    )
    return globally_edited_chapters