"""
This module contains functions for generating prompts for a language model 
used in a writing assistant application.
"""


def get_system_prompt():
    """
    Returns the default system prompt instructing the LLM on its persona and goals.

    This prompt sets the initial behavior of the language model.
    It is loaded when the application starts and can be modified by the user.

    Returns:
        str: The default system prompt for the language model.
    """
    return "You are a helpful and creative writing assistant. Please follow the user's instructions and provide high-quality responses. Be informative and detailed."


def generate_synopsis_prompt(genre, tone, point_of_view, writing_style, premise):
    """
    Generates a prompt for requesting a story synopsis from the language model.

    Args:
        genre (str): The desired genre of the story.
        tone (str): The desired tone of the story.
        point_of_view (str): The point of view from which the story is told.
        writing_style (str): The writing style to be used in the story.
        premise (str): The core premise or idea behind the story.

    Returns:
        str: The generated prompt string for requesting a synopsis.
    """
    return (
        f"Generate a synopsis for a story with the following characteristics:\n"
        f"Genre: {genre}\n"
        f"Tone: {tone}\n"
        f"Point of View: {point_of_view}\n"
        f"Writing Style: {writing_style}\n"
        f"Premise: {premise}"
    )


def generate_characters_prompt(
    genre, tone, point_of_view, writing_style, premise, synopsis
):
    """
    Generates a prompt to request character ideas from the language model.

    Args:
        genre (str): The story's genre.
        tone (str): The story's tone.
        point_of_view (str): The story's point of view.
        writing_style (str): The story's writing style.
        premise (str): The story's premise.
        synopsis (str): A synopsis of the story.

    Returns:
        str: The crafted prompt for the language model.
    """
    return (
        f"Generate characters for a story with the following characteristics:\n"
        f"Genre: {genre}\n"
        f"Tone: {tone}\n"
        f"Point of View: {point_of_view}\n"
        f"Writing Style: {writing_style}\n"
        f"Premise: {premise}\n"
        f"Synopsis: {synopsis}"
    )


def generate_world_settings_prompt(
    genre, tone, point_of_view, writing_style, premise, synopsis
):
    """
    Crafts a prompt for generating world and setting details for a story.

    Args:
        genre (str): The genre of the story.
        tone (str): The intended tone.
        point_of_view (str): The story's narration perspective.
        writing_style (str): The desired writing style.
        premise (str): The basic story idea.
        synopsis (str): A summary of the story.

    Returns:
        str: The assembled prompt to feed to the language model.
    """
    return (
        f"Generate the world and settings for a story with the following characteristics:\n"
        f"Genre: {genre}\n"
        f"Tone: {tone}\n"
        f"Point of View: {point_of_view}\n"
        f"Writing Style: {writing_style}\n"
        f"Premise: {premise}\n"
        f"Synopsis: {synopsis}"
    )


def generate_title_prompt(genre, tone, premise):
    """
    Creates a prompt for requesting potential titles from the language model.

    Args:
        genre (str): The genre of the story.
        tone (str): The desired tone of the title.
        premise (str): A short description of the story's core concept.

    Returns:
        str: The generated prompt, ready for the language model.
    """
    return (
        f"Generate a list of potential titles for a story with the following characteristics:\n"
        f"Genre: {genre}\n"
        f"Tone: {tone}\n"
        f"Premise: {premise}"
    )


def generate_outline_prompt(
    genre, tone, point_of_view, writing_style, premise, synopsis, characters, world_info
):
    """
    Constructs a prompt for generating a detailed story outline.

    Args:
        genre (str): The genre of the story.
        tone (str): The intended tone.
        point_of_view (str): Narration perspective (e.g., 1st person, 3rd person).
        writing_style (str): The writing style to be used.
        premise (str): The basic story idea or concept.
        synopsis (str): A brief summary of the story.
        characters (list): List of characters involved.
        world_info (str): Information about the story's world.

    Returns:
        str: The prompt, ready to be processed by the language model.
    """
    return (
        f"Generate a story outline with the following characteristics:\n"
        f"Genre: {genre}\n"
        f"Tone: {tone}\n"
        f"Point of View: {point_of_view}\n"
        f"Writing Style: {writing_style}\n"
        f"Premise: {premise}\n"
        f"Synopsis: {synopsis}\n"
        f"Characters: {characters}\n"
        f"World Information: {world_info}"
    )


def generate_scenes_summary_prompt(
    genre,
    tone,
    point_of_view,
    writing_style,
    premise,
    synopsis,
    characters,
    world_info,
    chapter_title,
):
    """
    Creates a prompt specifically aimed at generating detailed scenes and a summary
    for a particular chapter within a story.

    Args:
        genre (str): Genre of the story.
        tone (str): Story's overall tone.
        point_of_view (str): Perspective from which the story is narrated.
        writing_style (str): Desired writing style to be employed.
        premise (str): Fundamental story idea or concept.
        synopsis (str): Concise overview of the entire story.
        characters (list): A list of relevant characters.
        world_info (str): Description or information about the story's world.
        chapter_title (str): The title of the specific chapter in question.

    Returns:
        str: The assembled prompt string for scene generation.
    """
    return (
        f"Generate detailed scenes and a summary for the chapter '{chapter_title}' based on the following:\n"
        f"Genre: {genre}\n"
        f"Tone: {tone}\n"
        f"Point of View: {point_of_view}\n"
        f"Writing Style: {writing_style}\n"
        f"Premise: {premise}\n"
        f"Synopsis: {synopsis}\n"
        f"Characters: {characters}\n"
        f"World Information: {world_info}\n"
        f"Outline: {chapter_title}"  # Note: The function uses 'Outline' in the prompt here
    )


def generate_chapter_prompt(
    genre,
    tone,
    point_of_view,
    writing_style,
    premise,
    synopsis,
    characters,
    world_info,
    chapter_title,
    scenes_and_summary,
):
    """
    Constructs a detailed prompt for generating a complete chapter of a story,
    leveraging a range of information provided as context.

    Args:
        genre (str): Story's genre classification.
        tone (str): The overall tone or mood.
        point_of_view (str): Narrative perspective.
        writing_style (str): Style of writing to be employed.
        premise (str): Core idea or concept driving the story.
        synopsis (str): Short summary of the overall narrative.
        characters (list): Relevant characters for the chapter.
        world_info (str): Information about the world.
        chapter_title (str): Title of the specific chapter.
        scenes_and_summary (str): Existing scenes and chapter summary.

    Returns:
        str: A fully constructed prompt prepared for the language model.
    """
    return (
        f"Generate a full chapter based on the following:\n"
        f"Genre: {genre}\n"
        f"Tone: {tone}\n"
        f"Point of View: {point_of_view}\n"
        f"Writing Style: {writing_style}\n"
        f"Premise: {premise}\n"
        f"Synopsis: {synopsis}\n"
        f"Characters: {characters}\n"
        f"World Information: {world_info}\n"
        f"Outline: {chapter_title}\n"
        f"Scenes & Summary: {scenes_and_summary}"
    )


def critique_improve_prompt(text):
    """
    Generates a prompt for critiquing and suggesting improvements to a piece of text.

    Args:
        text (str): The text to be evaluated and improved.

    Returns:
        str: The formatted prompt for critique and improvement.
    """
    return f"Critique and improve the following {text}:\n{text}"
