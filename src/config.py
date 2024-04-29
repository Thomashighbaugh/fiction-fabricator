from src.prompts import (
    get_genre_prompt,
    get_tone_prompt,
    get_style_prompt,
    get_pov_prompt,
)
from src.llmconnection import call_g4f_api
def edit_config_variables(book_data):
    """
    Allows the user to edit the config variables (genre, tone, style, pov) stored in book_data.
    """
    while True:
        print("\nCurrent configuration:")
        for key, value in book_data.items():
            if key in ["genre", "tone", "style", "pov"]:
                print(f"{key}: {value}")

        choice = input("\nEnter the variable to edit (genre, tone, style, pov) or 'done': ")
        if choice.lower() == "done":
            break

        if choice.lower() in book_data:
            new_value = input(f"Enter new value for {choice}: ")
            book_data[choice.lower()] = new_value
            print(f"{choice} updated.")
        else:
            print("Invalid variable name. Please try again.")

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
    """

    choice = input(
        "Would you like to enter your own genre or have it generated? (e/g): "
    )
    if choice.lower() == "e":
        genre = input("Please enter your chosen genre: ")
    else:
        prompt = get_genre_prompt(premise)
        response = call_g4f_api(prompt)
        genre = response
    return genre


def select_tone(premise):
    """
    Allows the user to either enter their own tone or have it generated by the AI.
    """

    choice = input(
        "Would you like to enter your own tone or have it generated? (e/g): "
    )
    if choice.lower() == "e":
        tone = input("Please enter the intended tone of the novel: ")
    else:
        prompt = get_tone_prompt(premise)
        response = call_g4f_api(prompt)
        tone = response
    return tone


def select_style(premise):
    """
    Allows the user to either enter their own style or have it generated by the AI.
    """

    choice = input(
        "Would you like to enter your own style or have it generated? (e/g): "
    )
    if choice.lower() == "e":
        style = input("Please enter the intended style of the novel: ")
    else:
        prompt = get_style_prompt(premise)
        response = call_g4f_api(prompt)
        style = response
    return style


def select_pov(premise):
    """
    Allows the user to either enter their own point of view or have it generated by the AI.
    """

    choice = input(
        "Would you like to enter your own point of view or have it generated? (e/g): "
    )
    if choice.lower() == "e":
        pov = input("Please enter the point of view for the novel: ")
    else:
        prompt = get_pov_prompt(premise)
        response = call_g4f_api(prompt)
        pov = response
    return pov
