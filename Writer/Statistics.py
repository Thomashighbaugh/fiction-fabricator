# File: AIStoryWriter/Writer/Statistics.py
# Purpose: Provides utility functions for text statistics, primarily word count.

"""
Utility functions for calculating simple text statistics.
Currently, this module focuses on word count, but could be expanded
for other metrics like sentence count, character count, readability scores, etc.
"""


def GetWordCount(text: str) -> int:
    """
    Calculates the number of words in a given string.
    Words are defined as sequences of characters separated by whitespace.

    Args:
        text: The input string.

    Returns:
        The total number of words in the string. Returns 0 for None or empty/whitespace-only strings.
    """
    if not text or not text.strip():
        return 0

    # Simple split by whitespace. This is a basic word count and doesn't
    # handle complex punctuation or hyphenation in a sophisticated way,
    # but is generally sufficient for LLM output estimation.
    words = text.split()
    return len(words)


# Example usage (not typically run directly from here)
if __name__ == "__main__":
    test_string_1 = "This is a simple test string with seven words."
    test_string_2 = "  Leading and trailing whitespace.  "
    test_string_3 = "OneWord"
    test_string_4 = ""
    test_string_5 = "    "  # Whitespace only
    test_string_6 = None  # type: ignore

    print(
        f"'{test_string_1}' -> Word count: {GetWordCount(test_string_1)}"
    )  # Expected: 7
    print(
        f"'{test_string_2}' -> Word count: {GetWordCount(test_string_2)}"
    )  # Expected: 4
    print(
        f"'{test_string_3}' -> Word count: {GetWordCount(test_string_3)}"
    )  # Expected: 1
    print(
        f"'{test_string_4}' -> Word count: {GetWordCount(test_string_4)}"
    )  # Expected: 0
    print(
        f"'{test_string_5}' -> Word count: {GetWordCount(test_string_5)}"
    )  # Expected: 0
    print(
        f"'{test_string_6}' -> Word count: {GetWordCount(test_string_6)}"
    )  # Expected: 0

    multi_line_string = """
    This is a
    multi-line string.
    It should count words correctly.
    """
    print(
        f"\nMulti-line string -> Word count: {GetWordCount(multi_line_string)}"
    )  # Expected: 10

    # Test with punctuation
    punctuation_string = "Hello, world! This is a test. (With parentheses)."
    # Basic split will count "world!" as one word, "parentheses)." as one word.
    print(
        f"'{punctuation_string}' -> Word count: {GetWordCount(punctuation_string)}"
    )  # Expected: 8
