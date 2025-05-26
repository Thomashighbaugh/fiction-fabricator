# File: AIStoryWriter/Writer/NovelEditor.py
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
from Writer.Interface.Wrapper import Interface  # LLM interaction
from Writer.PrintUtils import Logger  # Logging
from Writer.Statistics import get_word_count  # For logging word count
from typing import List, Dict, Any


def edit_novel_globally(
    interface: Interface,
    logger: Logger,
    assembled_chapters: List[str],
    overall_story_outline: str,  # The original chapter-level outline
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
        # Proceed, but edits might be less effective.
        overall_story_outline = "Overall story outline not provided for full context."

    total_chapters = len(assembled_chapters)
    logger.Log(
        f"Starting global novel editing pass for {total_chapters} chapter(s)...", 2
    )

    globally_edited_chapters: List[str] = list(assembled_chapters)  # Start with a copy

    # Accumulate text of chapters processed so far to provide context to the LLM
    # This context grows as we edit more chapters.
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
            # Add placeholder or keep empty, then add to context for next chapter
            novel_text_so_far_for_context += f"\n\n## Chapter {chapter_num} (Empty)\n\n"
            continue

        try:
            # Use the specialized prompt for global chapter editing
            prompt_template = Prompts.GLOBAL_NOVEL_CHAPTER_EDIT_PROMPT
            # Note: _NovelTextSoFar in the prompt refers to text *before* the current chapter.
            text_before_current_chapter = novel_text_so_far_for_context

            formatted_prompt = prompt_template.format(
                ChapterNum=chapter_num,
                _OverallStoryOutline=overall_story_outline,
                _NovelTextSoFar=(
                    text_before_current_chapter
                    if text_before_current_chapter
                    else "This is the first chapter."
                ),
                _ChapterTextToEdit=current_chapter_text,
            )
        except KeyError as e:
            error_msg = f"Formatting error in GLOBAL_NOVEL_CHAPTER_EDIT_PROMPT for Chapter {chapter_num}: Missing key {e}"
            logger.Log(error_msg, 7)
            # Keep original chapter text, add it to context for next iteration
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
            ),  # Expert editor persona
            interface.build_user_query(formatted_prompt),
        ]

        try:
            # The model for global editing should be strong and capable of handling large context if _NovelTextSoFar gets long.
            # Config.CHAPTER_REVISION_WRITER_MODEL or a dedicated Config.MODEL_GLOBAL_EDITOR could be used.
            # min_word_count should ensure the chapter isn't accidentally deleted.
            # Expect the LLM to make surgical changes, so output length should be similar.
            min_expected_words = max(50, int(original_word_count * 0.80))

            response_messages = interface.safe_generate_text(
                logger,
                messages,
                Config.CHAPTER_REVISION_WRITER_MODEL,  # Re-using this, could be a dedicated global editor model
                min_word_count=min_expected_words,
            )

            updated_chapter_text: str = interface.get_last_message_text(
                response_messages
            )

            if not updated_chapter_text or "Error:" in updated_chapter_text:
                logger.Log(
                    f"LLM failed global edit for Chapter {chapter_num} or returned an error. Keeping pre-edit version.",
                    6,
                )
                # Keep original, add to context for next iteration
                novel_text_so_far_for_context += (
                    f"\n\n## Chapter {chapter_num}\n\n{current_chapter_text}\n\n"
                )
            else:
                globally_edited_chapters[chapter_idx] = (
                    updated_chapter_text  # Update the list with the edited chapter
                )
                edited_word_count = get_word_count(updated_chapter_text)
                logger.Log(
                    f"Global edit review for Chapter {chapter_num} complete. New word count: {edited_word_count}.",
                    4,
                )
                # Add the *edited* version to the context for subsequent chapters
                novel_text_so_far_for_context += (
                    f"\n\n## Chapter {chapter_num}\n\n{updated_chapter_text}\n\n"
                )

        except Exception as e:
            error_msg_runtime = f"An unexpected critical error during global editing of Chapter {chapter_num}: {e}"
            logger.Log(error_msg_runtime, 7)
            # Keep original, add to context
            novel_text_so_far_for_context += (
                f"\n\n## Chapter {chapter_num}\n\n{current_chapter_text}\n\n"
            )
            # No change to globally_edited_chapters[chapter_idx] as it holds the pre-error version

    logger.Log(
        f"Global novel editing pass complete for all {total_chapters} chapter(s).", 2
    )
    return globally_edited_chapters


# Example usage (typically called from Write.py if Config.ENABLE_FINAL_EDIT_PASS is True)
if __name__ == "__main__":
    # This is for testing purposes only.
    class MockLogger:
        def Log(self, item: str, level: int, stream: bool = False):
            print(f"LOG L{level}: {item}")

        def save_langchain_interaction(self, label: str, messages: list):
            print(f"LANGCHAIN_SAVE: {label}")

    class MockInterface:
        def build_system_query(self, q: str):
            return {"role": "system", "content": q}

        def build_user_query(self, q: str):
            return {"role": "user", "content": q}

        def get_last_message_text(self, msgs):
            return msgs[-1]["content"] if msgs else ""

        def safe_generate_text(self, l, m, mo, min_word_count):
            print(
                f"Mock LLM Call (safe_generate_text) to {mo} for global novel editing. Min words: {min_word_count}"
            )
            # Simulate LLM making minor edits for global consistency
            original_chapter_text_to_edit = ""
            # Crude extraction from the complex prompt for mocking
            if "<_ChapterTextToEdit>" in m[-1]["content"]:
                original_chapter_text_to_edit = (
                    m[-1]["content"]
                    .split("<_ChapterTextToEdit>")[1]
                    .split("</_ChapterTextToEdit>")[0]
                    .strip()
                )

            edited_text = original_chapter_text_to_edit + " [Globally Edited Suffix]"
            return [*m, {"role": "assistant", "content": edited_text}]

    mock_logger = MockLogger()
    mock_interface = MockInterface()

    Config.CHAPTER_REVISION_WRITER_MODEL = (
        "mock_global_editor_model"  # Model used for this pass
    )
    Prompts.DEFAULT_SYSTEM_PROMPT = "You are a global editor bot for testing."
    # Simplified prompt for testing format call
    Prompts.GLOBAL_NOVEL_CHAPTER_EDIT_PROMPT = """
    Edit Chapter {ChapterNum}.
    Outline: {_OverallStoryOutline}
    Novel So Far: <_NovelTextSoFar>{_NovelTextSoFar}</_NovelTextSoFar>
    Chapter to Edit: <_ChapterTextToEdit>{_ChapterTextToEdit}</_ChapterTextToEdit>
    """

    print("--- Testing edit_novel_globally ---")

    sample_chapters = [
        "Chapter One: The hero, Bob, found a sword. He was happy.",
        "Chapter Two: Bob met Alice. Alice mentioned a dragon. Bob seemed interested.",  # Bob's interest is new
        "Chapter Three: Bob and Alice decided to fight the dragon. Bob was still happy.",  # Could refine Bob's unchanging happiness
    ]
    sample_outline = (
        "Outline: Bob gets sword, meets Alice, they fight dragon. Bob is always happy."
    )

    edited_chapters_result = edit_novel_globally(
        mock_interface, mock_logger, sample_chapters, sample_outline
    )

    print("\n--- Globally Edited Chapters (Mocked) ---")
    for i, chap_text in enumerate(edited_chapters_result):
        print(f"Edited Chapter {i+1}:\n---\n{chap_text}\n---\n")

    assert "[Globally Edited Suffix]" in edited_chapters_result[0]
    assert "[Globally Edited Suffix]" in edited_chapters_result[1]
    assert "[Globally Edited Suffix]" in edited_chapters_result[2]
    assert len(edited_chapters_result) == len(sample_chapters)

    print("--- Test with empty chapter list for global editing ---")
    empty_edited_list = edit_novel_globally(
        mock_interface, mock_logger, [], sample_outline
    )
    print(f"Result for empty list: {empty_edited_list}")
    assert empty_edited_list == []

    print("\n--- Test with one chapter having empty content ---")
    chapters_with_empty = [
        "Chapter One: Valid start.",
        "",  # Empty chapter
        "Chapter Three: Valid end.",
    ]
    edited_with_empty = edit_novel_globally(
        mock_interface, mock_logger, chapters_with_empty, sample_outline
    )
    print(
        f"Edited (with empty chapter):\nCh1: {edited_with_empty[0][:30]}...\nCh2: '{edited_with_empty[1]}'\nCh3: {edited_with_empty[2][:30]}..."
    )
    assert "[Globally Edited Suffix]" in edited_with_empty[0]
    assert edited_with_empty[1] == ""  # Empty chapter should remain empty
    assert "[Globally Edited Suffix]" in edited_with_empty[2]
