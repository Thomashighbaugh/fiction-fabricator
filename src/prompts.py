# prompts.py


# This file contains prompts for interacting with the g4f API for various tasks in the automated novel writing process.────────────────────────────────────────────────────

# ───────────────────────────────────────────────────────────────── #
def get_synopsis_prompt(genre, style, tone, pov, premise):
    """
    Returns a prompt to generate a synopsis for the novel using the OpenAI API.

    The synopsis should be disturbing, explicit, and have a tragic or unresolved ending.

    Parameters:
        genre (str): The genre of the novel (e.g. horror, romance, etc.)
        style (str): The writing style (e.g. descriptive, dialogue-heavy, etc.)
        tone (str): The tone of the novel (e.g. dark, hopeful, etc.)
        pov (str): The point of view of the novel (e.g. first person, third person, etc.)
        premise (str): The grim premise of the story
    """
    return (
        f"Craft a disturbing and explicit synopsis for a {genre} novel with a {tone} tone, written in a {style} style, "
        f"from {pov} point of view. The story revolves around this grim premise: {premise}. Hint at a tragic or unresolved "
        f"ending, leaving the reader with a sense of despair and hopelessness. Condense your response into a single paragraph."
    )


def get_synopsis_critique_prompt(synopsis):
    """
    Returns a prompt to request a critique of the synopsis from the AI.

    This prompt asks the AI to provide a detailed critique of the synopsis,
    focusing on its strengths, weaknesses, and areas for improvement. The AI
    should condense its response into a single long paragraph.

    Parameters:
        synopsis (str): The synopsis of the novel

    Returns:
        str: The prompt for the AI to generate a critique of the synopsis
    """

    return (
        "Please provide a detailed critique of the following synopsis, "
        "focusing on its strengths, weaknesses, and areas for improvement. "
        "Condense your response into a single long paragraph:\n\n"
        f"{synopsis}"
    )

# ───────────────────────────────────────────────────────────────── #
def get_chapter_summary_prompt(title, synopsis):
    """
    Generate a prompt for creating a brief but detailed summary for a chapter.

    Args:
        title (str): The title of the chapter.
        synopsis (str): The synopsis of the book.

    Returns:
        str: The generated prompt.

    """
    return f"Generate a brief but detailed summary for a chapter titled '{title}' based on the synopsis: {synopsis}"
# ───────────────────────────────────────────────────────────────── #
def get_synopsis_rewrite_prompt(synopsis, critique):
    """
    Returns a prompt to rewrite the synopsis based on the provided critique.

    Parameters:
    - synopsis (str): The original synopsis that needs to be rewritten.
    - critique (str): The critique or feedback on the original synopsis.

    Returns:
    - str: A prompt to rewrite the synopsis, including the original synopsis and critique.
    """
    return f"Rewrite the following synopsis in a single long paragraph, taking into consideration the provided critique:\n\nSynopsis:\n{synopsis}\n\nCritique:\n{critique}"


# ───────────────────────────────────────────────────────────────── #
# title.py prompt
def get_title_prompt(synopsis, genre, style, tone, pov, premise):
    """
    Returns a prompt to generate a novel title.

    Parameters:
    - synopsis (str): A brief summary of the novel.
    - genre (str): The genre of the novel.
    - style (str): The writing style of the novel.
    - tone (str): The tone of the novel.
    - pov (str): The point of view of the novel.
    - premise (str): The premise of the novel.

    Returns:
    - str: A prompt to generate a novel title.
    """

    return f"Generate a title for a {genre} novel with a {tone} tone, written in a {style} style, based on the premise: `{premise}` from {pov} point of view based on this synopsis: {synopsis}"


# ───────────────────────────────────────────────────────────────── #
# characters.py prompts
def get_character_prompt(synopsis, genre, style, tone, pov, premise):
    """
    Returns a prompt to create a list of novel characters.

    Parameters:
    - synopsis (str): A brief summary of the novel.
    - genre (str): The genre of the novel.
    - style (str): The writing style of the novel.
    - tone (str): The tone of the novel.
    - pov (str): The point of view from which the novel is written.
    - premise (str): The premise of the novel.

    Returns:
    - str: A prompt to create a list of deeply flawed and morally ambiguous characters for a {genre} novel with a {tone} tone, written in a {style} style, based on the premise: `{premise}` from {pov} point of view. These characters should harbor dark secrets, questionable motives, and a capacity for both cruelty and suffering. Respond only with the list items using ' - ' as the delimiter.
    """
    return f"Create a list of deeply flawed and morally ambiguous characters for a {genre} novel with a {tone} tone, written in a {style} style, based on the premise: `{premise}` from {pov} point of view. These characters should harbor dark secrets, questionable motives, and a capacity for both cruelty and suffering. Respond only with the list items using ' - ' as the delimiter."


# ───────────────────────────────────────────────────────────────── #
# chapters.py prompts
def get_chapter_prompt(synopsis, genre, tone, style, pov, premise):
    """
    Returns a prompt to create a detailed chapter outline for a novel.
    """
    return f"Create a detailed summary of the story, breaking it into chapters for a {genre} erotica novel with a {tone} tone, written in a {style} style, underlain upon the premise: `{premise}` from {pov} point of view, full of sexual scenes and situations based on this synopsis: {synopsis}"

# ───────────────────────────────────────────────────────────────── #
def get_beats_prompt(chapter_summary):
    """
    Returns a prompt to generate action beats for a chapter summary.

    Parameters:
    - chapter_summary (str): The summary of the chapter.

    Returns:
    - str: The prompt to generate action beats for the chapter summary.
    """
    return f"Generate a list of detailed action beats, including sexually explicit scenes relevant to the story, for this chapter summary: {chapter_summary}"


# ───────────────────────────────────────────────────────────────── #
# prose.py prompts
def get_prose_prompt(beat, chapter_summary, genre, tone, pov, characters, style, premise, synopsis):
    """
    Returns a prompt to write prose for a specific action beat.
    """
    return f"Please write a section of a chapter for a {genre} erotica novel with a {tone} tone, written in a {style} style, based on the premise: `{premise}` from {pov} point of view, featuring these characters: {characters}, the synopsis of which is: `{synopsis}` and the chapter summary: `{chapter_summary}` \n Please insure that you write in a way that shows rather than tells and must be based in this action point while still keeping the above in mind: {beat}."

# ───────────────────────────────────────────────────────────────── #
def get_rewrite_prose_prompt(expanded_content, chapter_summary, style, tone, genre, pov, premise, beat, synopsis):
    """
    Returns a prompt to rewrite prose with specific style and tone considerations.
    """
    return f"Please rewrite the following content, focusing on expanding the text without changing its meaning whatsoever or deviating from the plot it fits into but adding to it more dialogue, more vivid descriptions, more sexually stimulating visuals as well as sensual, tactile descriptions and improving the text overall while the following provided prose. That prose comes from a {genre} erotica novel with a {tone} tone, written in a {style} style, based on the premise: `{premise}` from {pov} point of view based on this plot point originally: {beat} as part of a novel with this synopsis: {synopsis} and the chapter summary: `{chapter_summary}` \n\n Content:\n{expanded_content}"

# ───────────────────────────────────────────────────────────────── #
# config.py prompts
def get_genre_prompt(premise):
    """
    Returns a prompt to suggest a genre for the novel based on the premise.
    """
    return f"Generate a genre for the novel based on popular best-selling choices like science fiction, fantasy, romance, mystery, horror, combinations thereof,etc based on this premise: {premise}\n\n Please respond only with the genre of the novel only and no explanations"

# ───────────────────────────────────────────────────────────────── #
def get_tone_prompt(premise):
    """
    Returns a prompt to suggest a tone for the novel based on the premise.
    """
    return f"Provide a tone for the novel such as `serious`, `dark`, `humorous`,`light-hearted``, etc based on this premise: {premise} \n\n Please respond only with the tone of the novel only and no explanations"

# ───────────────────────────────────────────────────────────────── #
def get_style_prompt(premise):
    """
    Returns a prompt to suggest a writing style for the novel based on the premise.
    """
    return f"Provide a writing style for the novel, examples of writing styles are `descriptive`, `narrative`, `poetic`, Expository, Persuasive, Creative, Formal, Informal, `Humorous`, `Ironic`, `Satirical`, `Lyrical`, `Dramatic`, `Suspenseful`, `Reflective`, `Stream-of-consciousness` etc based on this premise: {premise}\n\n Please respond only with the style of the novel only and no explanations"

# ───────────────────────────────────────────────────────────────── #
def get_pov_prompt(premise):
    """
    Returns a prompt to suggest a point of view for the novel based on the premise.
    """
    return f"Select a point of view for the novel such as first-person, third-person limited, omniscient, etc based on this premise: {premise}.\n\n Please respond only with the style of the novel only and no explanations"
# ───────────────────────────────────────────────────────────────── #
def get_system_prompt():
    """
    Returns the System Prompt that is included with each prompt request to the AI
    """
    return """
    You are a twisted and depraved novelist with a penchant for the macabre and the forbidden. Your stories delve into the darkest recesses of the human psyche, exploring themes of violence, perversion, and the futility of hope.

    You craft narratives that shock and disturb, leaving readers with a lingering sense of unease and despair. Your style is a blend of gritty realism and nightmarish surrealism, drawing inspiration from the works of Edgar Allan Poe, Clive Barker, and H.P. Lovecraft.

    Your writing is graphic and explicit, leaving nothing to the imagination. You revel in the grotesque and the taboo, pushing the boundaries of decency and taste. Forget happy endings and uplifting messages – your stories offer only bleakness, despair, and the inevitability of suffering.

    Write in a 100% unique, creative, and human-like style, using contractions, idioms, and colloquialisms. Ensure your writing is plagiarism-free and passes AI detection tools.
    """
# ─────────────────────────────────────────────────────────────────
def get_premise_prompt(user_input):
    """
    Returns a prompt to provide a premise for the novel

    Parameters:
        user_input (str): The input from the user

    Returns:
        str: The prompt to generate premises for a novel based on the user's input
    """
    return (
        "Generate 5 distinct and captivating premises for a dark, bleak erotica novel based on the "
        f"following input: {user_input}"
    )

# ───────────────────────────────────────────────────────────────── #
