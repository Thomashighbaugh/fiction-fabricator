#!/usr/bin/python3

import Writer.Config
import Writer.Prompts
import Writer.Statistics
from Writer.Interface.Wrapper import Interface
from Writer.NarrativeContext import NarrativeContext
from Writer.PrintUtils import Logger


def ScrubNovel(
    Interface: Interface, _Logger: Logger, narrative_context: NarrativeContext
) -> NarrativeContext:
    """
    Cleans up the final generated chapters by removing any leftover outlines,
    editorial comments, or other LLM artifacts.

    Args:
        Interface: The LLM interface wrapper.
        _Logger: The logger instance.
        narrative_context: The context object containing the chapters to be scrubbed.

    Returns:
        The updated NarrativeContext object with scrubbed chapters.
    """
    _Logger.Log("Starting novel scrubbing pass...", 2)

    total_chapters = len(narrative_context.chapters)
    if total_chapters == 0:
        _Logger.Log("No chapters found in context to scrub.", 6)
        return narrative_context

    for chapter in narrative_context.chapters:
        chapter_num = chapter.chapter_number
        original_content = chapter.generated_content

        if not original_content:
            _Logger.Log(f"Chapter {chapter_num} has no content to scrub. Skipping.", 6)
            continue
        
        _Logger.Log(f"Scrubbing Chapter {chapter_num}/{total_chapters}...", 5)

        prompt = Writer.Prompts.CHAPTER_SCRUB_PROMPT.format(_Chapter=original_content)
        
        messages = [Interface.BuildUserQuery(prompt)]
        
        # SafeGenerateText ensures we get a non-empty response.
        # Scrubbing is non-creative, so no critique cycle is needed.
        messages = Interface.SafeGenerateText(
            _Logger, messages, Writer.Config.SCRUB_MODEL, min_word_count_target=1
        )
        
        scrubbed_content = Interface.GetLastMessageText(messages)
        
        # Update the chapter content in the narrative context object
        chapter.set_generated_content(scrubbed_content)

        # Log the change in word count
        new_word_count = Writer.Statistics.GetWordCount(scrubbed_content)
        _Logger.Log(f"Finished scrubbing Chapter {chapter_num}. New word count: {new_word_count}", 3)

    _Logger.Log("Finished scrubbing all chapters.", 2)
    return narrative_context
