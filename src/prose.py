import json
import os
import subprocess

from src.llmconnection import call_g4f_api
from src.prompts import get_prose_prompt, get_rewrite_prose_prompt

def write_prose(beat, chapter_summary, genre, tone, pov, characters, style, premise, synopsis):
    """
    Writes prose based on the given parameters.

    Args:
        beat (dict): The action beat.
        chapter_summary (str): The summary of the chapter.
        genre (str): The genre of the novel.
        tone (str): The tone of the novel.
        pov (str): The point of view of the novel.
        characters (list): The list of characters in the novel.
        style (str): The style of the novel.
        premise (str): The premise of the novel.
        synopsis (str): The synopsis of the novel.

    Returns:
        dict: The updated beat dictionary with the rewritten content.
    """
    prompt = get_prose_prompt(beat["action_point"], chapter_summary, genre, tone, pov, characters, style, premise, synopsis)

    response = call_g4f_api(prompt)
    prose = response
    beat["expanded_content"] = prose
    return beat

def rewrite_prose(beat, chapter_summary, style, tone, genre, pov, premise, synopsis):
    """
    Rewrite the given prose based on the provided parameters.

    Args:
        beat (dict): The action beat.
        chapter_summary (str): The summary of the chapter.
        style (str): The style of the novel.
        tone (str): The tone of the novel.
        genre (str): The genre of the novel.
        pov (str): The point of view of the novel.
        premise (str): The premise of the novel.
        synopsis (str): The synopsis of the novel.

    Returns:
        dict: The updated beat dictionary with the rewritten content.
    """
    prompt = get_rewrite_prose_prompt(beat["expanded_content"], chapter_summary, style, tone, genre, pov, premise, beat["action_point"], synopsis)
    response = call_g4f_api(prompt)
    rewritten_prose = response
    beat["rewritten_content"] = rewritten_prose
    return beat
def chapters_to_json(chapters):
    """
    Converts a dictionary of chapters to a JSON string.

    Parameters:
        chapters (dict): A dictionary representing the chapters of a novel.

    Returns:
        str: A JSON string representation of the chapters dictionary, with an indentation of 4 spaces.
    """


    return json.dumps(chapters, indent=4)


def save_chapter_as_markdown(chapter_title, chapter_content, book_title):
    """
    Saves a chapter as a markdown file in the output directory.

    Args:
        chapter_title (str): The title of the chapter.
        chapter_content (str): The content of the chapter.
        book_title (str): The title of the book.

    Returns:
        None

    This function creates an output directory if it doesn't exist and saves the chapter content as a markdown file.
    It replaces spaces in the chapter title with underscores and removes special characters from the filename.
    The markdown file is saved in the output directory with the same name as the chapter title.
    The function prints a message indicating the chapter title and the filepath of the saved markdown file.
    """


    # Create the output directory if it doesn't exist
    output_dir = f"output/{book_title}"
    os.makedirs(output_dir, exist_ok=True)

    # Replace spaces with underscores and remove special characters for the filename
    filename = "".join(
        char for char in chapter_title if char.isalnum() or char in " "
    ).replace(" ", "_")
    filepath = f"{output_dir}/{filename}.md"

    # Save the chapter content to the markdown file
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(chapter_content)

    print(f"Chapter '{chapter_title}' saved as markdown file: {filepath}")


def print_and_edit_beat(chapter_title, beat, content_type):
    """
    Prints the content of a beat and allows for manual editing.

    Args:
        chapter_title (str): The title of the chapter.
        beat (dict): A dictionary containing the beat information.
        content_type (str): The type of content to print and edit. Must be either "expanded_content" or "rewritten_content".

    Returns:
        None

    This function prints the chapter title and action point of the beat. If the content_type is "expanded_content", it prints the expanded content. If the content_type is "rewritten_content", it prints the rewritten content. It then prompts the user if they want to do any manual editing for the section. If the user enters "Y", it opens a temporary file with the content of the specified content_type and opens it in the user's default editor. After editing, it reads the content from the temporary file and updates the corresponding key in the beat dictionary.

    Note:
        The function assumes that the beat dictionary has keys "expanded_content" and "rewritten_content" if the content_type is "expanded_content" or "rewritten_content", respectively.

    """


    print(f"Chapter: {chapter_title}")
    print(f"Action Point: {beat['action_point']}")

    if content_type == "expanded_content":
        print("Expanded Content:")
        print(beat["expanded_content"])
    elif content_type == "rewritten_content":
        print("Rewritten Content:")
        print(beat["rewritten_content"])

    manual_edit = input(
        "Would you like to do any manual editing for this section? (Y/N): "
    )
    if manual_edit.lower() == "y":
        editor = os.getenv("EDITOR", "vim")  # Default to 'vi' if $EDITOR is not set
        with open("temp_file.txt", "w") as temp_file:
            temp_file.write(beat[content_type])

        subprocess.call([editor, "temp_file.txt"])

        with open("temp_file.txt", "r") as temp_file:
            edited_content = temp_file.read()

        beat[content_type] = edited_content
