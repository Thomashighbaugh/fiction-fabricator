
# File: Writer/Statistics.py
# Purpose: Utility functions for text statistics, e.g., word count.

"""
Text Statistics Utilities.

This module provides simple functions for calculating basic statistics
from text data, such as word counts. These can be used to monitor
the length of generated content or for other analytical purposes.
"""

from typing import Optional


def get_word_count(text: Optional[str]) -> int:
    """
    Calculates the number of words in a given string.
    Words are assumed to be separated by whitespace.

    Args:
        text (Optional[str]): The input string. If None or empty,
                              word count is 0.

    Returns:
        int: The total number of words in the text.
    """
    if not text or not text.strip():
        return 0
    words = text.split()
    return len(words)


def get_character_count(text: Optional[str], include_whitespace: bool = True) -> int:
    """
    Calculates the number of characters in a given string.

    Args:
        text (Optional[str]): The input string. If None, count is 0.
        include_whitespace (bool): If True (default), counts all characters
                                   including spaces, tabs, newlines.
                                   If False, counts only non-whitespace characters.

    Returns:
        int: The total number of characters.
    """
    if not text:
        return 0

    if include_whitespace:
        return len(text)
    else:
        return len("".join(text.split()))


def get_sentence_count(text: Optional[str]) -> int:
    """
    Estimates the number of sentences in a given string.
    This is a naive implementation based on common sentence-ending punctuation.

    Args:
        text (Optional[str]): The input string. If None or empty, count is 0.

    Returns:
        int: An estimated number of sentences.
    """
    if not text or not text.strip():
        return 0

    terminators = [".", "!", "?"]
    sentence_count = 0
    temp_text = text
    for term in terminators:
        temp_text = temp_text.replace(term * 2, term)
        temp_text = temp_text.replace(term * 3, term)

    for char_idx, char in enumerate(temp_text):
        if char in terminators:
            is_abbreviation_or_number = False
            if char == ".":
                if (
                    char_idx > 0
                    and temp_text[char_idx - 1].isalpha()
                    and char_idx < len(temp_text) - 1
                    and temp_text[char_idx + 1].isalpha()
                ):
                    pass
                elif (
                    char_idx > 0
                    and temp_text[char_idx - 1].isdigit()
                    and char_idx < len(temp_text) - 1
                    and temp_text[char_idx + 1].isdigit()
                ):
                    pass

            if not is_abbreviation_or_number:
                sentence_count += 1

    if sentence_count == 0 and text.strip():
        return 1

    return sentence_count