# File: Writer/Scrubber.py
# Purpose: Cleans up final generated novel text by removing author notes, outline remnants, etc.

"""
Novel Text Scrubber Module.

This module provides functionality to perform a final "scrubbing" pass
on the generated chapters of a novel. The goal is to remove any
non-narrative elements that might have been inadvertently included by the LLMs
during the creative generation process. This includes:
- Leftover outline markers or headings.
- Author notes or editorial comments (e.g., "[TODO: Describe sunset]").
- Any other meta-text not intended for the final reader.

The scrubbing process uses an LLM with a specific prompt to identify and
remove these elements, leaving only the clean, publishable story text.
"""

import Writer.Config as Config
import Writer.Prompts as Prompts
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger
from Writer.Statistics import get_word_count
from typing import List, Optional

# Heuristic: 1 word is approx 1.5 tokens in English, but can vary.
WORD_TO_TOKEN_RATIO = 1.5


def scrub_novel_chapters(
    interface: Interface, logger: Logger, chapters_to_scrub: List[str]
) -> List[str]:
    """
    Scrubs a list of chapter texts to remove non-narrative elements.

    Args:
        interface (Interface): The LLM interaction wrapper.
        logger (Logger): The logging instance.
        chapters_to_scrub (List[str]): A list of strings, where each string is
                                       the text of a chapter.

    Returns:
        List[str]: A list of scrubbed chapter texts. If scrubbing fails for a chapter,
                   the original chapter text might be returned for that entry.
    """
    if not chapters_to_scrub:
        logger.Log("No chapters provided for scrubbing. Returning empty list.", 1)
        return []

    total_chapters = len(chapters_to_scrub)
    logger.Log(
        f"Starting novel scrubbing process for {total_chapters} chapter(s)...", 2
    )

    scrubbed_chapters_list: List[str] = []

    for i, chapter_text_to_scrub in enumerate(chapters_to_scrub):
        chapter_num = i + 1
        original_word_count = get_word_count(chapter_text_to_scrub)
        logger.Log(
            f"Scrubbing Chapter {chapter_num}/{total_chapters} (Original word count: {original_word_count})...",
            3,
        )

        if not chapter_text_to_scrub or not chapter_text_to_scrub.strip():
            logger.Log(
                f"Chapter {chapter_num} is empty. Skipping scrubbing for this chapter.",
                5,
            )
            scrubbed_chapters_list.append(
                chapter_text_to_scrub
            )
            continue

        try:
            prompt_template = Prompts.CHAPTER_SCRUB_PROMPT
            formatted_prompt = prompt_template.format(_Chapter=chapter_text_to_scrub)
        except KeyError as e:
            error_msg = f"Formatting error in CHAPTER_SCRUB_PROMPT for Chapter {chapter_num}: Missing key {e}"
            logger.Log(error_msg, 7)
            scrubbed_chapters_list.append(
                f"// Scrubbing Error for Chapter {chapter_num}: {error_msg} //\n{chapter_text_to_scrub}"
            )
            continue
        except Exception as e:
            error_msg = f"Unexpected error formatting scrub prompt for Chapter {chapter_num}: {e}"
            logger.Log(error_msg, 7)
            scrubbed_chapters_list.append(
                f"// Scrubbing Error for Chapter {chapter_num}: {error_msg} //\n{chapter_text_to_scrub}"
            )
            continue

        messages = [
            interface.build_system_query(
                "You are an AI text cleaning utility. Your sole task is to remove non-narrative elements like author notes, outline markers, and comments from the provided text, leaving only the pure story content. Do not add, remove, or change the story's narrative itself."
            ),
            interface.build_user_query(formatted_prompt),
        ]

        try:
            MIN_WORDS_AFTER_SCRUB = max(10, int(original_word_count * 0.5))
            # The output should be slightly smaller than the input. Set max_tokens to be the same as input tokens as a safe upper bound.
            MAX_TOKENS_FOR_SCRUB = int(original_word_count * WORD_TO_TOKEN_RATIO)

            response_messages = interface.safe_generate_text(
                logger,
                messages,
                Config.SCRUB_MODEL,
                min_word_count=MIN_WORDS_AFTER_SCRUB,
                max_tokens=MAX_TOKENS_FOR_SCRUB,
            )

            scrubbed_chapter_text: str = interface.get_last_message_text(
                response_messages
            )

            if not scrubbed_chapter_text or "Error:" in scrubbed_chapter_text:
                log_msg = f"LLM failed to scrub Chapter {chapter_num} or returned an error. Using original text for this chapter."
                logger.Log(log_msg, 6)
                scrubbed_chapters_list.append(
                    chapter_text_to_scrub
                )
            else:
                scrubbed_word_count = get_word_count(scrubbed_chapter_text)
                words_removed = original_word_count - scrubbed_word_count
                logger.Log(
                    f"Chapter {chapter_num} scrubbing complete. New word count: {scrubbed_word_count} (Removed approx. {words_removed} words).",
                    4,
                )
                scrubbed_chapters_list.append(scrubbed_chapter_text)

        except Exception as e:
            error_msg_runtime = f"An unexpected critical error occurred during scrubbing of Chapter {chapter_num}: {e}"
            logger.Log(error_msg_runtime, 7)
            scrubbed_chapters_list.append(
                f"// Scrubbing Runtime Error for Chapter {chapter_num}: {error_msg_runtime} //\n{chapter_text_to_scrub}"
            )

    logger.Log(
        f"Novel scrubbing process complete for all {total_chapters} chapter(s).", 2
    )
    return scrubbed_chapters_list