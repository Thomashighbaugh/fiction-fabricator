# File: AIStoryWriter/Writer/Scrubber.py
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
from Writer.Interface.Wrapper import Interface # LLM interaction
from Writer.PrintUtils import Logger # Logging
from Writer.Statistics import get_word_count # For logging word count
from typing import List

def scrub_novel_chapters(
    interface: Interface, 
    logger: Logger, 
    chapters_to_scrub: List[str]
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
                   the original chapter text might be returned for that entry, or an
                   error placeholder, depending on error severity.
    """
    if not chapters_to_scrub:
        logger.Log("No chapters provided for scrubbing. Returning empty list.", 1)
        return []

    total_chapters = len(chapters_to_scrub)
    logger.Log(f"Starting novel scrubbing process for {total_chapters} chapter(s)...", 2)
    
    scrubbed_chapters_list: List[str] = []

    for i, chapter_text_to_scrub in enumerate(chapters_to_scrub):
        chapter_num = i + 1
        original_word_count = get_word_count(chapter_text_to_scrub)
        logger.Log(f"Scrubbing Chapter {chapter_num}/{total_chapters} (Original word count: {original_word_count})...", 3)

        if not chapter_text_to_scrub or not chapter_text_to_scrub.strip():
            logger.Log(f"Chapter {chapter_num} is empty. Skipping scrubbing for this chapter.", 5)
            scrubbed_chapters_list.append(chapter_text_to_scrub) # Append empty/original
            continue

        try:
            prompt_template = Prompts.CHAPTER_SCRUB_PROMPT
            formatted_prompt = prompt_template.format(_Chapter=chapter_text_to_scrub)
        except KeyError as e:
            error_msg = f"Formatting error in CHAPTER_SCRUB_PROMPT for Chapter {chapter_num}: Missing key {e}"
            logger.Log(error_msg, 7)
            scrubbed_chapters_list.append(f"// Scrubbing Error for Chapter {chapter_num}: {error_msg} //\n{chapter_text_to_scrub}")
            continue # Move to next chapter
        except Exception as e:
            error_msg = f"Unexpected error formatting scrub prompt for Chapter {chapter_num}: {e}"
            logger.Log(error_msg, 7)
            scrubbed_chapters_list.append(f"// Scrubbing Error for Chapter {chapter_num}: {error_msg} //\n{chapter_text_to_scrub}")
            continue

        messages = [
            # A system prompt can reinforce the specific task of cleaning, not creative writing.
            interface.build_system_query("You are an AI text cleaning utility. Your sole task is to remove non-narrative elements like author notes, outline markers, and comments from the provided text, leaving only the pure story content. Do not add, remove, or change the story's narrative itself."),
            interface.build_user_query(formatted_prompt)
        ]
        
        try:
            # SCRUB_MODEL should be good at precise text manipulation and following instructions.
            # min_word_count should be high enough to prevent accidental deletion of the whole chapter if LLM misbehaves,
            # but low enough to allow for significant removal of notes.
            # A heuristic: expect at least 50% of the original words to remain if it's mostly narrative.
            min_expected_words_after_scrub = max(10, int(original_word_count * 0.5))

            response_messages = interface.safe_generate_text(
                logger, 
                messages, 
                Config.SCRUB_MODEL,
                min_word_count=min_expected_words_after_scrub 
            )
            
            scrubbed_chapter_text: str = interface.get_last_message_text(response_messages)

            if not scrubbed_chapter_text or "Error:" in scrubbed_chapter_text:
                log_msg = f"LLM failed to scrub Chapter {chapter_num} or returned an error. Using original text for this chapter."
                logger.Log(log_msg, 6)
                scrubbed_chapters_list.append(chapter_text_to_scrub) # Fallback to original
            else:
                scrubbed_word_count = get_word_count(scrubbed_chapter_text)
                words_removed = original_word_count - scrubbed_word_count
                logger.Log(f"Chapter {chapter_num} scrubbing complete. New word count: {scrubbed_word_count} (Removed approx. {words_removed} words).", 4)
                scrubbed_chapters_list.append(scrubbed_chapter_text)

        except Exception as e:
            error_msg_runtime = f"An unexpected critical error occurred during scrubbing of Chapter {chapter_num}: {e}"
            logger.Log(error_msg_runtime, 7)
            scrubbed_chapters_list.append(f"// Scrubbing Runtime Error for Chapter {chapter_num}: {error_msg_runtime} //\n{chapter_text_to_scrub}")
            
    logger.Log(f"Novel scrubbing process complete for all {total_chapters} chapter(s).", 2)
    return scrubbed_chapters_list


# Example usage (typically called from Write.py)
if __name__ == "__main__":
    # This is for testing purposes only.
    class MockLogger:
        def Log(self, item: str, level: int, stream: bool = False): print(f"LOG L{level}: {item}")
        def save_langchain_interaction(self, label: str, messages: list): print(f"LANGCHAIN_SAVE: {label}")

    class MockInterface:
        def build_system_query(self, q: str): return {"role": "system", "content": q}
        def build_user_query(self, q: str): return {"role": "user", "content": q}
        def get_last_message_text(self, msgs): return msgs[-1]["content"] if msgs else ""
        
        def safe_generate_text(self, l, m, mo, min_word_count):
            print(f"Mock LLM Call (safe_generate_text) to {mo} for scrubbing. Min words: {min_word_count}")
            # Simulate LLM scrubbing the text
            original_text = ""
            for msg_part in m: # Find user message with chapter
                if msg_part["role"] == "user" and "<CHAPTER>" in msg_part["content"]:
                    # Crude extraction for mock
                    original_text = msg_part["content"].split("<CHAPTER>")[1].split("</CHAPTER>")[0]
                    break
            
            scrubbed_text = original_text
            scrubbed_text = scrubbed_text.replace("[TODO: Add more detail here]", "")
            scrubbed_text = scrubbed_text.replace("## Scene 1: The Beginning", "")
            scrubbed_text = scrubbed_text.replace("<!-- Author note: make this scarier -->", "")
            scrubbed_text = "\n".join([line for line in scrubbed_text.splitlines() if line.strip()]) # Remove empty lines
            
            return [*m, {"role": "assistant", "content": scrubbed_text if scrubbed_text else "Mock scrubbed to empty."}]

    mock_logger = MockLogger()
    mock_interface = MockInterface()
    
    Config.SCRUB_MODEL = "mock_scrub_model"
    Prompts.CHAPTER_SCRUB_PROMPT = "Scrub this chapter:\n<CHAPTER>\n{_Chapter}\n</CHAPTER>" # Simplified

    print("--- Testing scrub_novel_chapters ---")
    
    chapters_with_notes = [
        "## Chapter 1: The Start\n\n<!-- Author note: Check continuity -->Once upon a time, in a land far away. [TODO: Describe the land]. The hero felt brave.",
        "The adventure continued. They found a cave. ## Scene 2: Cave Exploration. It was dark. [Remember to add a monster!]",
        "Chapter 3\nJust clean story text here. No notes to remove.",
        "" # Empty chapter
    ]
    
    scrubbed = scrub_novel_chapters(mock_interface, mock_logger, chapters_with_notes)
    
    print("\n--- Scrubbed Chapters (Mocked) ---")
    for i, chap_text in enumerate(scrubbed):
        print(f"Scrubbed Chapter {i+1}:\n---\n{chap_text}\n---\n")

    assert "TODO" not in scrubbed[0]
    assert "<!--" not in scrubbed[0]
    assert "## Scene 2" not in scrubbed[1]
    assert "No notes to remove" in scrubbed[2] # Should remain unchanged
    assert scrubbed[3] == "" # Empty chapter should remain empty
    
    print("--- Test with empty chapter list ---")
    empty_scrub = scrub_novel_chapters(mock_interface, mock_logger, [])
    print(f"Result for empty list: {empty_scrub}")
    assert empty_scrub == []