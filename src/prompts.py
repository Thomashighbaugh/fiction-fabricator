def get_system_prompt():
    """
    Returns the default system prompt.
    """
    return "You are a helpful and creative writing assistant. Please follow the user's instructions and provide high-quality responses. Be informative and detailed."

def generate_synopsis_prompt(genre, tone, point_of_view, writing_style, premise):
    """
    Generates the prompt for generating a synopsis.

    Args:
        genre: The genre of the story.
        tone: The tone of the story.
        point_of_view: The point of view of the story.
        writing_style: The writing style of the story.
        premise: The premise or general idea of the story.

    Returns:
        The prompt string.
    """
    return f"Generate a synopsis for a story with the following characteristics:\nGenre: {genre}\nTone: {tone}\nPoint of View: {point_of_view}\nWriting Style: {writing_style}\nPremise: {premise}"

def generate_characters_prompt(genre, tone, point_of_view, writing_style, premise, synopsis):
    """
    Generates the prompt for generating characters.

    Args:
        genre: The genre of the story.
        tone: The tone of the story.
        point_of_view: The point of view of the story.
        writing_style: The writing style of the story.
        premise: The premise or general idea of the story.
        synopsis: The synopsis of the story.

    Returns:
        The prompt string.
    """
    return f"Generate characters for a story with the following characteristics:\nGenre: {genre}\nTone: {tone}\nPoint of View: {point_of_view}\nWriting Style: {writing_style}\nPremise: {premise}\nSynopsis: {synopsis}"

def generate_world_settings_prompt(genre, tone, point_of_view, writing_style, premise, synopsis):
    """
    Generates the prompt for generating world and settings.

    Args:
        genre: The genre of the story.
        tone: The tone of the story.
        point_of_view: The point of view of the story.
        writing_style: The writing style of the story.
        premise: The premise or general idea of the story.
        synopsis: The synopsis of the story.

    Returns:
        The prompt string.
    """
    return f"Generate the world and settings for a story with the following characteristics:\nGenre: {genre}\nTone: {tone}\nPoint of View: {point_of_view}\nWriting Style: {writing_style}\nPremise: {premise}\nSynopsis: {synopsis}"

def generate_title_prompt(genre, tone, premise):
    """
    Generates the prompt for generating a title.

    Args:
        genre: The genre of the story.
        tone: The tone of the story.
        premise: The premise or general idea of the story.

    Returns:
        The prompt string.
    """
    return f"Generate a list of potential titles for a story with the following characteristics:\nGenre: {genre}\nTone: {tone}\nPremise: {premise}"

def generate_outline_prompt(genre, tone, point_of_view, writing_style, premise, synopsis, characters, world_info):
    """
    Generates the prompt for generating an outline.

    Args:
        genre: The genre of the story.
        tone: The tone of the story.
        point_of_view: The point of view of the story.
        writing_style: The writing style of the story.
        premise: The premise or general idea of the story.
        synopsis: The synopsis of the story.
        characters: The list of characters in the story.
        world_info: The information about the world of the story.

    Returns:
        The prompt string.
    """
    return f"Generate a story outline with the following characteristics:\nGenre: {genre}\nTone: {tone}\nPoint of View: {point_of_view}\nWriting Style: {writing_style}\nPremise: {premise}\nSynopsis: {synopsis}\nCharacters: {characters}\nWorld Information: {world_info}"

def generate_scenes_summary_prompt(genre, tone, point_of_view, writing_style, premise, synopsis, characters, world_info, chapter_title):
    """
    Generates the prompt for generating scenes and summary for a chapter.

    Args:
        genre: The genre of the story.
        tone: The tone of the story.
        point_of_view: The point of view of the story.
        writing_style: The writing style of the story.
        premise: The premise or general idea of the story.
        synopsis: The synopsis of the story.
        characters: The list of characters in the story.
        world_info: The information about the world of the story.
        chapter_title: The title of the chapter.

    Returns:
        The prompt string.
    """
    return f"Generate detailed scenes and a summary for the chapter '{chapter_title}' based on the following:\nGenre: {genre}\nTone: {tone}\nPoint of View: {point_of_view}\nWriting Style: {writing_style}\nPremise: {premise}\nSynopsis: {synopsis}\nCharacters: {characters}\nWorld Information: {world_info}\nOutline: {chapter_title}"

def generate_chapter_prompt(genre, tone, point_of_view, writing_style, premise, synopsis, characters, world_info, chapter_title, scenes_and_summary):
    """
    Generates the prompt for generating a full chapter.

    Args:
        genre: The genre of the story.
        tone: The tone of the story.
        point_of_view: The point of view of the story.
        writing_style: The writing style of the story.
        premise: The premise or general idea of the story.
        synopsis: The synopsis of the story.
        characters: The list of characters in the story.
        world_info: The information about the world of the story.
        chapter_title: The title of the chapter.
        scenes_and_summary: The scenes and summary for the chapter.

    Returns:
        The prompt string.
    """
    return f"Generate a full chapter based on the following:\nGenre: {genre}\nTone: {tone}\nPoint of View: {point_of_view}\nWriting Style: {writing_style}\nPremise: {premise}\nSynopsis: {synopsis}\nCharacters: {characters}\nWorld Information: {world_info}\nOutline: {chapter_title}\nScenes & Summary: {scenes_and_summary}"

def critique_improve_prompt(text):
    """
    Generates a prompt for critiquing and improving text.

    Args:
        text: The text to critique and improve.

    Returns:
        The prompt string.
    """
    return f"Critique and improve the following {text}:\n{text}"
