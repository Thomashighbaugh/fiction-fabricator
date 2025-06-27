#!/usr/bin/python3

def GetWordCount(_Text: str) -> int:
    """
    Calculates the total number of words in a given string.
    Words are determined by splitting the string by whitespace.

    Args:
        _Text: The string to be analyzed.

    Returns:
        The integer word count. Returns 0 if input is not a string.
    """
    if not isinstance(_Text, str):
        return 0
    return len(_Text.split())
