# fiction-fabricator/src/config.py
from src.prompts import (
    get_genre_prompt,
    get_tone_prompt,
    get_style_prompt,
    get_pov_prompt,
)
from src.llmconnection import call_g4f_api


def input_premise():
    """
    Prompts the user to enter the general premise of the novel.

    Returns:
        The premise entered by the user.
    """

    premise = input("Please enter the general premise of the novel: ")
    return premise


def select_genre(premise):
    """
    Allows the user to either enter their own genre or have it generated by the AI.

    Args:
        premise: The premise of the novel.

    Returns:
        The selected genre.
    """

    choice = input(
        "Would you like to enter your own genre or have it generated? (enter/generate): "
    )
    if choice.lower() == "e" or choice.lower() == "enter":
        genre = input("Please enter your chosen genre: ")
    else:
        prompt = get_genre_prompt(premise)
        response = call_g4f_api(prompt)
        genre = response.strip()
    return genre


def select_tone(premise):
    """
    Allows the user to either enter their own tone or have it generated by the AI.

    Args:
        premise: The premise of the novel.

    Returns:
        The selected tone.
    """

    choice = input(
        "Would you like to enter your own tone or have it generated? (enter/generate): "
    )
    if choice.lower() == "enter" or choice.lower() == "e":
        tone = input("Please enter the intended tone of the novel: ")
    else:
        prompt = get_tone_prompt(premise)
        response = call_g4f_api(prompt)
        tone = response.strip()
    return tone


def select_style(premise):
    """
    Allows the user to either enter their own style or have it generated by the AI.

    Args:
        premise: The premise of the novel.

    Returns:
        The selected style.
    """

    choice = input(
        "Would you like to enter your own style or have it generated? (enter/generate): "
    )
    if choice.lower() == "enter" or choice.lower() == "e":
        style = input("Please enter the intended style of the novel: ")
    else:
        prompt = get_style_prompt(premise)
        response = call_g4f_api(prompt)
        style = response.strip()
    return style


def select_pov(premise):
    """
    Allows the user to either enter their own point of view or have it generated by the AI.

    Args:
        premise: The premise of the novel.

    Returns:
        The selected point of view.
    """

    choice = input(
        "Would you like to enter your own point of view or have it generated? (enter/generate): "
    )
    if choice.lower() == "enter" or choice.lower() == "e":
        pov = input("Please enter the point of view for the novel: ")
    else:
        prompt = get_pov_prompt(premise)
        response = call_g4f_api(prompt)
        pov = response.strip()
    return pov
