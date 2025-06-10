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
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger
from Writer.Statistics import get_word_count
from typing import List, Dict, Any, Optional

# Heuristic: 1 word is approx 1.5 tokens in English, but can vary.
WORD_TO_TOKEN_RATIO = 1.5


def translate_text(
    interface: Interface,
    logger: Logger,
    text_to_translate: str,
    target_language: str,
    source_language: Optional[str] = None,
    max_tokens: Optional[int] = None,
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
        max_tokens (Optional[int]): Maximum number of tokens the LLM should generate for the translation.

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
        prompt_template = Prompts.TRANSLATE_PROMPT
        formatted_prompt = prompt_template.format(
            _Prompt=text_to_translate,
            _Language=target_language,
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
        original_word_count = get_word_count(text_to_translate)
        MIN_WORDS_FOR_TRANSLATION = max(1, int(original_word_count * 0.5))

        # If max_tokens is not provided, calculate a default.
        if max_tokens is None:
            max_tokens = int(original_word_count * WORD_TO_TOKEN_RATIO * 1.2)

        response_messages = interface.safe_generate_text(
            logger,
            messages,
            Config.TRANSLATOR_MODEL,
            min_word_count=MIN_WORDS_FOR_TRANSLATION,
            max_tokens=max_tokens,
        )

        translated_text: str = interface.get_last_message_text(response_messages)

        if not translated_text or "Error:" in translated_text:
            log_msg = f"LLM failed to translate text or returned an error. Returning original text."
            logger.Log(log_msg, 6)
            return text_to_translate

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
    target_language_for_llm: str,
    original_prompt_language: Optional[str] = None,
) -> str:
    """
    Translates the user's initial story prompt.

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
    MAX_TOKENS_FOR_PROMPT_TRANSLATION = int(
        get_word_count(user_prompt_text) * WORD_TO_TOKEN_RATIO * 1.5
    )

    return translate_text(
        interface,
        logger,
        user_prompt_text,
        target_language_for_llm,
        original_prompt_language,
        max_tokens=MAX_TOKENS_FOR_PROMPT_TRANSLATION,
    )


def translate_novel_chapters(
    interface: Interface,
    logger: Logger,
    chapters_to_translate: List[str],
    target_language: str,
    source_language_of_chapters: Optional[str] = "English",
) -> List[str]:
    """
    Translates a list of generated novel chapters into a specified target language.

    Args:
        interface (Interface): The LLM interaction wrapper.
        logger (Logger): The logging instance.
        chapters_to_translate (List[str]): Chapter texts to be translated.
        target_language (str): The language to translate the chapters into.
        source_language_of_chapters (Optional[str]): The language of the input chapters.

    Returns:
        List[str]: A list of translated chapter texts.
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
            translated_chapters_list.append(chapter_text)
            continue

        try:
            prompt_template = Prompts.CHAPTER_TRANSLATE_PROMPT
            formatted_prompt = prompt_template.format(
                _Chapter=chapter_text,
                _Language=target_language,
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
            original_chapter_word_count = get_word_count(chapter_text)
            MIN_WORDS_FOR_CHAPTER_TRANSLATION = max(
                10, int(original_chapter_word_count * 0.6)
            )
            MAX_TOKENS_FOR_CHAPTER_TRANSLATION = int(
                original_chapter_word_count * WORD_TO_TOKEN_RATIO * 1.2
            )

            response_messages = interface.safe_generate_text(
                logger,
                messages,
                Config.TRANSLATOR_MODEL,
                min_word_count=MIN_WORDS_FOR_CHAPTER_TRANSLATION,
                max_tokens=MAX_TOKENS_FOR_CHAPTER_TRANSLATION,
            )
            translated_chapter_text: str = interface.get_last_message_text(
                response_messages
            )

            if not translated_chapter_text or "Error:" in translated_chapter_text:
                log_msg = f"LLM failed to translate Chapter {chapter_num} or returned an error. Using original text for this chapter."
                logger.Log(log_msg, 6)
                translated_chapters_list.append(chapter_text)
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
