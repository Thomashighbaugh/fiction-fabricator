import json
import os
import subprocess

from src.openaiconnection import call_g4f_api
from src.prompts import get_prose_prompt, get_rewrite_prose_prompt


def write_prose(beat, genre, tone, pov, characters, style, premise):
    """
    Writes prose for a single action beat using the OpenAI API.
    """

    prompt = get_prose_prompt(
        [beat["action_point"]], genre, tone, pov, characters, style, premise
    )
    response = call_g4f_api(prompt)
    prose = response
    beat["expanded_content"] = prose


def rewrite_prose(beat, style, tone, genre, pov, premise):
    """
    Rewrites prose for a single action beat using the OpenAI API, focusing on style and tone.
    """

    prompt = get_rewrite_prose_prompt(
        beat["expanded_content"], style, tone, genre, pov, premise
    )
    response = call_g4f_api(prompt)
    rewritten_prose = response
    beat["rewritten_content"] = rewritten_prose


def chapters_to_json(chapters):
    """
    Converts a dictionary of chapters to a JSON string.
    """

    return json.dumps(chapters, indent=4)


def save_chapter_as_markdown(chapter_title, chapter_content, book_title):
    """
    Saves a chapter as a markdown file in the output directory.
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
