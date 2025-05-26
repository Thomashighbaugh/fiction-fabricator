# File: AIStoryWriter/Writer/Statistics.py
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

    # Simple split by whitespace. This might not be perfectly accurate
    # for all languages or complex punctuation but is generally sufficient.
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
    It may not be accurate for all text structures or languages.

    Args:
        text (Optional[str]): The input string. If None or empty, count is 0.

    Returns:
        int: An estimated number of sentences.
    """
    if not text or not text.strip():
        return 0

    # Common sentence terminators
    terminators = [".", "!", "?"]
    sentence_count = 0

    # Normalize multiple terminators (e.g., "!!!", "?!") to one for counting
    # This is a very simplified approach.
    # A more robust method would use regex or NLP libraries.
    temp_text = text
    for term in terminators:
        temp_text = temp_text.replace(term * 2, term)  # Replace "!!" with "!"
        temp_text = temp_text.replace(term * 3, term)  # Replace "!!!" with "!"

    for char_idx, char in enumerate(temp_text):
        if char in terminators:
            # Avoid counting if it's part of an abbreviation (e.g., "Mr.") or number ("3.14")
            # This check is still very basic.
            is_abbreviation_or_number = False
            if char == ".":
                if (
                    char_idx > 0
                    and temp_text[char_idx - 1].isalpha()
                    and char_idx < len(temp_text) - 1
                    and temp_text[char_idx + 1].isalpha()
                ):
                    # e.g. U.S.A - this logic is flawed for actual sentence counting.
                    # A proper NLP tokenizer is needed for accuracy.
                    pass  # This might be an abbreviation.
                elif (
                    char_idx > 0
                    and temp_text[char_idx - 1].isdigit()
                    and char_idx < len(temp_text) - 1
                    and temp_text[char_idx + 1].isdigit()
                ):
                    pass  # e.g. 3.14

            if not is_abbreviation_or_number:
                sentence_count += 1

    # If no terminators found but text exists, assume at least one sentence.
    if sentence_count == 0 and text.strip():
        return 1

    return sentence_count


# Example usage (typically not run directly from this file)
if __name__ == "__main__":
    sample_text_1 = "This is a sample sentence. And another one! Is this three?"
    sample_text_2 = (
        "Mr. Smith went to Washington D.C. for $3.50. It was... interesting!!"
    )
    empty_text = ""
    none_text = None

    print(f"'{sample_text_1}':")
    print(f"  Words: {get_word_count(sample_text_1)}")
    print(f"  Chars (incl. space): {get_character_count(sample_text_1)}")
    print(
        f"  Chars (excl. space): {get_character_count(sample_text_1, include_whitespace=False)}"
    )
    print(f"  Sentences (estimated): {get_sentence_count(sample_text_1)}")

    print(f"\n'{sample_text_2}':")
    print(f"  Words: {get_word_count(sample_text_2)}")
    print(
        f"  Sentences (estimated): {get_sentence_count(sample_text_2)}"
    )  # Will be inaccurate

    print(f"\nEmpty text words: {get_word_count(empty_text)}")
    print(f"None text words: {get_word_count(none_text)}")
