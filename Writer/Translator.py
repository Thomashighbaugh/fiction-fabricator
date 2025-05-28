# File: Writer/Translator.py
# Purpose: Handles translation of story prompts and generated novel content.

"""
Translation Module.

This module provides functions to translate text using an LLM:
1.  `translate_prompt()`: Translates the user's initial story prompt into a
    specified target language (typically English, if the user provides a prompt
    in another language, or to another language if the user wishes to write in it
    but the LLMs perform better in English).
2.  `translate_novel_chapters()`: Translates a list of generated novel chapters
    into a specified target language.

Optimized prompts are used to guide the LLM for accurate and natural-sounding
translations that preserve the original meaning, style, and tone.
"""

import Writer.Config as Config
import Writer.Prompts as Prompts
from Writer.Interface.Wrapper import Interface  # LLM interaction
from Writer.PrintUtils import Logger  # Logging
from Writer.Statistics import get_word_count  # For logging word count
from typing import List, Dict, Any, Optional


def translate_text(
    interface: Interface,
    logger: Logger,
    text_to_translate: str,
    target_language: str,
    source_language: Optional[str] = None,  # Optional: helps LLM if source is known
) -> str:
    """
    Translates a given piece of text into the target language using an LLM.
    This is a generic helper that can be used by more specific translation functions.

    Args:
        interface (Interface): The LLM interaction wrapper.
        logger (Logger): The logging instance.
        text_to_translate (str): The text to be translated.
        target_language (str): The language to translate the text into (e.g., "English", "French").
        source_language (Optional[str]): The source language of the text, if known.
                                          Providing this can improve translation quality.

    Returns:
        str: The translated text. Returns an error message string or the original text
             if translation fails.
    """
    if not text_to_translate or not text_to_translate.strip():
        logger.Log("Text for translation is empty. Returning as is.", 5)
        return text_to_translate

    if not target_language or not target_language.strip():
        logger.Log(
            "Target language for translation is not specified. Returning original text.",
            6,
        )
        return text_to_translate

    log_source_lang = f" from '{source_language}'" if source_language else ""
    logger.Log(
        f"Attempting to translate text{log_source_lang} to '{target_language}'...", 3
    )

    try:
        # Using a more generic prompt if source_language might be complex for the LLM to auto-detect.
        # Prompts.TRANSLATE_PROMPT is designed for this.
        prompt_template = Prompts.TRANSLATE_PROMPT
        # The prompt itself handles the source language information if provided.
        # {_Language} in the prompt refers to the TARGET language.
        formatted_prompt = prompt_template.format(
            _Prompt=text_to_translate,  # Original prompt uses _Prompt for text
            _Language=target_language,  # Target language
            # The prompt text itself can specify "translate from X to Y"
            # Or the system prompt can guide it if _SourceLanguage is available.
        )
        system_message = f"You are an expert multilingual translator. Translate the given text accurately and naturally into {target_language}."
        if source_language:
            system_message += f" The source text is in {source_language}."

    except KeyError as e:
        error_msg = f"Formatting error in TRANSLATE_PROMPT: Missing key {e}"
        logger.Log(error_msg, 7)
        return f"Translation Error: {error_msg}. Original: {text_to_translate[:100]}..."
    except Exception as e:
        error_msg = f"Unexpected error formatting translation prompt: {e}"
        logger.Log(error_msg, 7)
        return f"Translation Error: {error_msg}. Original: {text_to_translate[:100]}..."

    messages: List[Dict[str, Any]] = [
        interface.build_system_query(system_message),
        interface.build_user_query(formatted_prompt),
    ]

    try:
        # TRANSLATOR_MODEL should be strong in multilingual capabilities.
        # min_word_count can be low as translation might shorten/lengthen text.
        # A better check might be character count ratio if really needed.
        # For now, a small min_word_count to ensure it's not empty.
        response_messages = interface.safe_generate_text(
            logger,
            messages,
            Config.TRANSLATOR_MODEL,
            min_word_count=max(
                1, int(get_word_count(text_to_translate) * 0.5)
            ),  # Expect at least half length
        )

        translated_text: str = interface.get_last_message_text(response_messages)

        if not translated_text or "Error:" in translated_text:
            log_msg = f"LLM failed to translate text or returned an error. Returning original text."
            logger.Log(log_msg, 6)
            return text_to_translate  # Fallback to original

        logger.Log(
            f"Text successfully translated to '{target_language}'. Original len: {len(text_to_translate)}, Translated len: {len(translated_text)}",
            4,
        )
        return translated_text

    except Exception as e:
        error_msg_runtime = (
            f"An unexpected critical error occurred during text translation: {e}"
        )
        logger.Log(error_msg_runtime, 7)
        return f"Translation Runtime Error: {error_msg_runtime}. Original: {text_to_translate[:100]}..."


def translate_user_prompt(
    interface: Interface,
    logger: Logger,
    user_prompt_text: str,
    target_language_for_llm: str,  # e.g., "English" if LLMs work best in it
    original_prompt_language: Optional[
        str
    ] = None,  # Detected or user-specified language of the prompt
) -> str:
    """
    Translates the user's initial story prompt, typically into a language
    that the primary story generation LLMs perform best in (e.g., English).

    Args:
        interface (Interface): The LLM interaction wrapper.
        logger (Logger): The logging instance.
        user_prompt_text (str): The user's original story prompt.
        target_language_for_llm (str): The language to translate the prompt into.
        original_prompt_language (Optional[str]): The original language of the prompt, if known.

    Returns:
        str: The translated user prompt.
    """
    logger.Log(
        f"Translating user prompt to '{target_language_for_llm}' for LLM processing.", 2
    )
    # Uses the generic translate_text utility
    return translate_text(
        interface,
        logger,
        user_prompt_text,
        target_language_for_llm,
        original_prompt_language,
    )


def translate_novel_chapters(
    interface: Interface,
    logger: Logger,
    chapters_to_translate: List[str],
    target_language: str,
    source_language_of_chapters: Optional[
        str
    ] = "English",  # Assuming chapters were generated in English
) -> List[str]:
    """
    Translates a list of generated novel chapters into a specified target language.

    Args:
        interface (Interface): The LLM interaction wrapper.
        logger (Logger): The logging instance.
        chapters_to_translate (List[str]): A list of strings, where each string is
                                           the text of a chapter (assumed to be in source_language_of_chapters).
        target_language (str): The language to translate the chapters into.
        source_language_of_chapters (Optional[str]): The language of the input chapters.

    Returns:
        List[str]: A list of translated chapter texts. If translation fails for a
                   chapter, the original chapter text might be returned for that entry.
    """
    if not chapters_to_translate:
        logger.Log("No chapters provided for translation. Returning empty list.", 1)
        return []

    if not target_language or not target_language.strip():
        logger.Log(
            "Target language for novel translation is not specified. Returning original chapters.",
            6,
        )
        return chapters_to_translate

    total_chapters = len(chapters_to_translate)
    logger.Log(
        f"Starting translation of {total_chapters} novel chapter(s) to '{target_language}'...",
        2,
    )

    translated_chapters_list: List[str] = []

    for i, chapter_text in enumerate(chapters_to_translate):
        chapter_num = i + 1
        logger.Log(
            f"Translating Chapter {chapter_num}/{total_chapters} to '{target_language}'...",
            3,
        )

        if not chapter_text or not chapter_text.strip():
            logger.Log(f"Chapter {chapter_num} is empty. Skipping translation.", 5)
            translated_chapters_list.append(chapter_text)  # Append empty/original
            continue

        # Use Prompts.CHAPTER_TRANSLATE_PROMPT which is specific for chapter content
        try:
            prompt_template = Prompts.CHAPTER_TRANSLATE_PROMPT
            formatted_prompt = prompt_template.format(
                _Chapter=chapter_text,
                _Language=target_language,  # _Language here is the target language
            )
            system_message = f"You are an expert literary translator. Translate the following book chapter into {target_language}, preserving its narrative style, character voices, and emotional tone."
            if source_language_of_chapters:
                system_message += (
                    f" The original chapter is in {source_language_of_chapters}."
                )

        except KeyError as e:
            error_msg = f"Formatting error in CHAPTER_TRANSLATE_PROMPT for Chapter {chapter_num}: Missing key {e}"
            logger.Log(error_msg, 7)
            translated_chapters_list.append(
                f"// Translation Error (Prompt): {error_msg} //\n{chapter_text}"
            )
            continue
        except Exception as e:
            error_msg = f"Unexpected error formatting chapter translation prompt for Chapter {chapter_num}: {e}"
            logger.Log(error_msg, 7)
            translated_chapters_list.append(
                f"// Translation Error (Prompt Format): {error_msg} //\n{chapter_text}"
            )
            continue

        messages: List[Dict[str, Any]] = [
            interface.build_system_query(system_message),
            interface.build_user_query(formatted_prompt),
        ]

        try:
            response_messages = interface.safe_generate_text(
                logger,
                messages,
                Config.TRANSLATOR_MODEL,
                min_word_count=max(
                    10, int(get_word_count(chapter_text) * 0.6)
                ),  # Translated text can vary in length
            )
            translated_chapter_text: str = interface.get_last_message_text(
                response_messages
            )

            if not translated_chapter_text or "Error:" in translated_chapter_text:
                log_msg = f"LLM failed to translate Chapter {chapter_num} or returned an error. Using original text for this chapter."
                logger.Log(log_msg, 6)
                translated_chapters_list.append(chapter_text)  # Fallback to original
            else:
                logger.Log(
                    f"Chapter {chapter_num} successfully translated to '{target_language}'. Word count: {get_word_count(translated_chapter_text)}.",
                    4,
                )
                translated_chapters_list.append(translated_chapter_text)

        except Exception as e:
            error_msg_runtime = f"An unexpected critical error occurred during translation of Chapter {chapter_num}: {e}"
            logger.Log(error_msg_runtime, 7)
            translated_chapters_list.append(
                f"// Translation Runtime Error: {error_msg_runtime} //\n{chapter_text}"
            )

    logger.Log(
        f"Novel translation process to '{target_language}' complete for all {total_chapters} chapter(s).",
        2,
    )
    return translated_chapters_list


# Example usage (typically called from Write.py)
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
                f"Mock LLM Call (safe_generate_text) to {mo} for translation. Min words: {min_word_count}"
            )
            # Simulate LLM translating the text
            original_text_for_translation = ""
            target_lang_for_translation = "MockLang"

            # Crude extraction for mock based on prompt structure
            user_query_content = m[-1]["content"]
            if Prompts.TRANSLATE_PROMPT.startswith(
                "<TEXT_TO_TRANSLATE>"
            ):  # Matches generic
                original_text_for_translation = (
                    user_query_content.split("<TEXT_TO_TRANSLATE>")[1]
                    .split("</TEXT_TO_TRANSLATE>")[0]
                    .strip()
                )
                # Extract target language from the prompt if possible (very specific to current Prompts.TRANSLATE_PROMPT)
                lang_match = re.search(r"into (.*?)\.", user_query_content)
                if lang_match:
                    target_lang_for_translation = lang_match.group(1)

            elif Prompts.CHAPTER_TRANSLATE_PROMPT.startswith(
                "<CHAPTER_TEXT>"
            ):  # Matches chapter
                original_text_for_translation = (
                    user_query_content.split("<CHAPTER_TEXT>")[1]
                    .split("</CHAPTER_TEXT>")[0]
                    .strip()
                )
                lang_match = re.search(
                    r"into (.*?)\.", user_query_content
                )  # Assuming prompt format
                if lang_match:
                    target_lang_for_translation = lang_match.group(1)

            return [
                *m,
                {
                    "role": "assistant",
                    "content": f"Translated to {target_lang_for_translation}: '{original_text_for_translation}' (mock)",
                },
            ]

    import re  # For mock

    mock_logger = MockLogger()
    mock_interface = MockInterface()

    Config.TRANSLATOR_MODEL = "mock_translator_model"
    # Simplified prompts for testing placeholders
    Prompts.TRANSLATE_PROMPT = "<TEXT_TO_TRANSLATE>\n{_Prompt}\n</TEXT_TO_TRANSLATE>\nTranslate into {_Language}."
    Prompts.CHAPTER_TRANSLATE_PROMPT = (
        "<CHAPTER_TEXT>\n{_Chapter}\n</CHAPTER_TEXT>\nTranslate into {_Language}."
    )

    print("--- Testing translate_user_prompt ---")
    original_user_prompt = "Un chevalier cherche une épée magique."
    translated_user_prompt = translate_user_prompt(
        mock_interface, mock_logger, original_user_prompt, "English", "French"
    )
    print(f"Original Prompt: {original_user_prompt}")
    print(f"Translated Prompt: {translated_user_prompt}\n")
    assert "English" in translated_user_prompt
    assert "chevalier" in translated_user_prompt  # Mock includes original

    print("--- Testing translate_novel_chapters ---")
    chapters_in_english = [
        "Chapter 1: The hero started his journey.",
        "Chapter 2: He faced many dangers and found a friend.",
    ]
    chapters_in_french = translate_novel_chapters(
        mock_interface, mock_logger, chapters_in_english, "French", "English"
    )

    print("Translated Chapters (Mocked):")
    for i, chap_text in enumerate(chapters_in_french):
        print(f"Chapter {i+1} (French Mock):\n---\n{chap_text}\n---\n")

    assert "French" in chapters_in_french[0]
    assert "hero started" in chapters_in_french[0]  # Mock includes original

    print("--- Test with empty chapter list for translation ---")
    empty_translated_list = translate_novel_chapters(
        mock_interface, mock_logger, [], "German"
    )
    print(f"Result for empty list: {empty_translated_list}")
    assert empty_translated_list == []

    print("\n--- Test translate_text with empty input ---")
    empty_text_trans = translate_text(mock_interface, mock_logger, "", "Spanish")
    print(f"Translation of empty text: '{empty_text_trans}'")
    assert empty_text_trans == ""

    print("\n--- Test translate_text with no target language ---")
    no_target_lang_trans = translate_text(mock_interface, mock_logger, "Some text", "")
    print(f"Translation with no target lang: '{no_target_lang_trans}'")
    assert no_target_lang_trans == "Some text"
