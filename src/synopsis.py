from src.llmconnection import call_g4f_api
from src.prompts import get_synopsis_prompt, get_synopsis_critique_prompt, get_synopsis_rewrite_prompt
import subprocess
import os


def generate_synopsis(genre, style, tone, pov, premise):
    """
    Generates a synopsis for the novel using the OpenAI API.
    """

    prompt = get_synopsis_prompt(genre, style, tone, pov, premise)
    response = call_g4f_api(prompt)

    synopsis = response
    return synopsis


def edit_synopsis(synopsis):
    """
    Opens the synopsis in the user's editor for manual editing.
    """

    editor = os.getenv("EDITOR", "vim")  # Default to 'vi' if $EDITOR is not set
    with open("temp_file.txt", "w") as temp_file:
        temp_file.write(synopsis)

    subprocess.call([editor, "temp_file.txt"])

    with open("temp_file.txt", "r") as temp_file:
        edited_synopsis = temp_file.read()

    return edited_synopsis


def expand_synopsis(synopsis):
    """
    Expands the synopsis using AI assistance.
    """

    prompt = f"Expand on the synopsis, focusing on adding into the existing synopsis additional key plot points and additional characters with some hint of whatever the character's motivations: {synopsis}"
    response = call_g4f_api(prompt)
    expanded_synopsis = response
    return expanded_synopsis


# ─────────────────────────────────────────────────────────────────
# synopsis.py function (for user interaction)
def critique_synopsis(synopsis):
    """
    Prompts the AI for a critique of the synopsis and then rewrites it based on the critique.
    """

    while True:
        print("Synopsis:")
        print(synopsis)

        choice = input("Do you want to 'edit', 'expand', or 'done'? ")
        if choice.lower() == "done":
            break
        elif choice.lower() == "edit":
            synopsis = edit_synopsis(synopsis)
        elif choice.lower() == "expand":
            synopsis = expand_synopsis(synopsis)
        else:
            print("Invalid choice. Please try again.")

    # Get AI critique
    critique_prompt = get_synopsis_critique_prompt(synopsis)
    critique_response = call_g4f_api(critique_prompt)
    critique = critique_response
    print("Critique:")
    print(critique)

    # Rewrite synopsis based on critique
    rewrite_prompt = get_synopsis_rewrite_prompt(synopsis, critique)
    rewrite_response = call_g4f_api(rewrite_prompt)
    updated_synopsis = rewrite_response

    return updated_synopsis
