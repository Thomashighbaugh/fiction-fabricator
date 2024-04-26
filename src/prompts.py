# prompts.py


# This file contains prompts for interacting with the g4f API for various tasks in the automated novel writing process.────────────────────────────────────────────────────


def get_synopsis_prompt(genre, style, tone, pov, premise):
    """
    Returns a prompt to create a detailed novel synopsis.
    """

    return f"Create a detailed synopsis for a {genre} novel with a {tone} tone, written in a {style} style, from {pov} point of view framed around this idea: {premise} \n\n Please condense your response into a single paragraph."


def get_synopsis_critique_prompt(synopsis):
    """
    Returns a prompt to request a critique of the synopsis from the AI.
    """

    return f"Please provide a detailed critique of the following synopsis, focusing on its strengths, weaknesses, and areas for improvement:\n\n{synopsis} Please condense your response into a single long paragraph"

def get_chapter_summary_prompt(title, synopsis):
    return f"Generate a brief summary for a chapter titled '{title}' based on the synopsis: {synopsis}"
def get_synopsis_rewrite_prompt(synopsis, critique):
    """
    Returns a prompt to rewrite the synopsis based on the provided critique.
    """

    return f"Rewrite the following synopsis in a single long paragraph, taking into consideration the provided critique:\n\nSynopsis:\n{synopsis}\n\nCritique:\n{critique}"


# ─────────────────────────────────────────────────────────────────
# title.py prompt
def get_title_prompt(synopsis, genre, style, tone, pov, premise):
    """
    Returns a prompt to generate a novel title.
    """

    return f"Generate a title for a {genre} novel with a {tone} tone, written in a {style} style, based on the premise: `{premise}` from {pov} point of view based on this synopsis: {synopsis}"


# ─────────────────────────────────────────────────────────────────
# characters.py prompts
def get_character_prompt(synopsis, genre, style, tone, pov, premise):
    """
    Returns a prompt to create a list of novel characters.
    """

    return f"Create an unordered list using ' - ' as the delimiter of original and interesting characters for a {genre} novel with a {tone} tone, written in a {style} style, based on the premise: `{premise}` from {pov} point of view based on this synopsis: {synopsis}. Please only respond with the list items that use ' - ' as the delimiter and nothing else."


# ─────────────────────────────────────────────────────────────────
# chapters.py prompts
def get_chapter_prompt(synopsis, genre, tone, style, pov, premise):
    """
    Returns a prompt to create a detailed chapter outline for a novel.
    """

    return f"Create a detailed summary of the story, breaking it into chapters for a {genre} novel with a {tone} tone, written in a {style} style, underlain upon the premise: `{premise}` from {pov} point of view based on this synopsis: {synopsis}"


def get_beats_prompt(chapter_summary):
    """
    Returns a prompt to generate action beats for a chapter summary.
    """

    return f"Generate a list of detailed action beats for this chapter summary: {chapter_summary}"


# ─────────────────────────────────────────────────────────────────
# prose.py prompts
def get_prose_prompt(beat, chapter_summary, genre, tone, pov, characters, style, premise, synopsis):
    """
    Returns a prompt to write prose for a specific action beat.
    """
    return f"Please write a section of a chapter for a {genre} novel with a {tone} tone, written in a {style} style, based on the premise: `{premise}` from {pov} point of view, featuring these characters: {characters}, the synopsis of which is: `{synopsis}` and the chapter summary: `{chapter_summary}` \n Please insure that you write in a way that shows rather than tells and must be based in this action point while still keeping the above in mind: {beat}."

def get_rewrite_prose_prompt(expanded_content, chapter_summary, style, tone, genre, pov, premise, beat, synopsis):
    """
    Returns a prompt to rewrite prose with specific style and tone considerations.
    """
    return f"Please rewrite the following content, focusing on expanding the text without changing its meaning whatsoever or deviating from the plot it fits into but adding to it more dialogue, more vivid descriptions and improving the text overall the following prose from a {genre} novel with a {tone} tone, written in a {style} style, based on the premise: `{premise}` from {pov} point of view based on this plot point originally: {beat} as part of a novel with this synopsis: {synopsis} and the chapter summary: `{chapter_summary}` \n\n Content:\n{expanded_content}"

# ─────────────────────────────────────────────────────────────────
# config.py prompts
def get_genre_prompt(premise):
    """
    Returns a prompt to suggest a genre for the novel based on the premise.
    """

    return f"Generate a genre for the novel based on popular best-selling choices like science fiction, fantasy, romance, mystery, horror, combinations thereof,etc based on this premise: {premise}\n\n Please respond only with the genre of the novel only and no explanations"

# ─────────────────────────────────────────────────────────────────
def get_tone_prompt(premise):
    """
    Returns a prompt to suggest a tone for the novel based on the premise.
    """

    return f"Provide a tone for the novel such as `serious`, `dark`, `humorous`,`light-hearted``, etc based on this premise: {premise} \n\n Please respond only with the tone of the novel only and no explanations"

# ─────────────────────────────────────────────────────────────────
def get_style_prompt(premise):
    """
    Returns a prompt to suggest a writing style for the novel based on the premise.
    """

    return f"Provide a writing style for the novel, examples of writing styles are `descriptive`, `narrative`, `poetic`, Expository, Persuasive, Creative, Formal, Informal, `Humorous`, `Ironic`, `Satirical`, `Lyrical`, `Dramatic`, `Suspenseful`, `Reflective`, `Stream-of-consciousness` etc based on this premise: {premise}\n\n Please respond only with the style of the novel only and no explanations"

# ─────────────────────────────────────────────────────────────────
def get_pov_prompt(premise):
    """
    Returns a prompt to suggest a point of view for the novel based on the premise.
    """

    return f"Select a point of view for the novel such as first-person, third-person limited, omniscient, etc based on this premise: {premise}.\n\n Please respond only with the style of the novel only and no explanations"
# ─────────────────────────────────────────────────────────────────
def get_system_prompt():
    """
    Returns the System Prompt that is included with each prompt request to the AI
    """
    return "I want you to act as a best-selling novelist working on your latest book. You will come up with creative, unique, critically-acclaimed and reader captivating stories that haunt readers for long periods of time while leaving them wanting more. Your style is something of a dark and sensual mix between the prose of Steven King, F Scott Fitzgerald, Jack Kerouac, H. P. Lovecraft & Frank Herbert. You must write in a 100% unique, creative and human-like style using contractions, idioms, transitional phrases, interjections, dangling modifiers and colloquialisms while avoiding repetitive phrases and unnatural sentence structures. Make sure your writing is plagiarism free. Write content that will easily pass AI detection tools. Don't show these details in your content."

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
        "Generate 5 distinct and captivating premises for a novel based on the "
        f"following input: {user_input}"
    )

