# /home/tlh/fiction-fabricator/prompts.py
book_spec_fields = ['Genre', 'Setting', 'Themes', 'Tone', 'Point of View', 'Characters', 'Premise']

book_spec_format = (
    "Genre: (e.g., Cyberpunk Neo-Noir, Grimdark Fantasy, Biopunk Thriller)\n"
    "Setting: (Environment details: social, political, technological)\n"
    "Themes: (Social and psychological issues)\n"
    "Tone: (Dark, cynical, sensual)\n"
    "Point of View: (First, third-limited, omniscient)\n"
    "Characters: (Names, motivations, backstories)\n"
    "Premise: (Story's central conflict, must adhere to topic)"
)

scene_spec_format = (
    "Chapter [number]:\n"
    "Scene [number]:\n"
    "Characters: (In this scene)\n"
    "Setting: (Immediate environment)\n"
    "Time: (Absolute/relative)\n"
    "Events: (Actions and dialogue)\n"
    "Conflict: (Scene's conflict)\n"
    "Story Value Shift: (Scene's impact)\n"
    "Story Value Charge: (Emotional charge)\n"
    "Mood: (Atmosphere)\n"
    "Outcome: (Consequences)"
)

prev_scene_intro = "\n\nPrevious scene:\n"
cur_scene_intro = "\n\nCurrent scene:\n"

def init_book_spec_messages(topic, form):
    """
    Construct a prompt for initializing a book specification based on a topic and form type.
    
    Args:
        topic (str): The topic of the story.
        form (str): The type of book specification to generate (e.g., "novel", "short story").
    
    Returns:
        list[dict]: A list of two prompts. The first prompt is empty, and the second prompt is a single user prompt to generate the book specification.
    """
    return [
        {"role": "system", "content": ""},
        {"role": "user",
         "content": f"Create a detailed {form} specification for a story about the following topic: '{topic}'. Strictly adhere to the topic and build upon it; do not deviate. Use this format:\n\"\"\"\n{book_spec_format}\"\"\"\n\nInfer a suitable setting from the premise, and if one cannot be clearly inferred, default to a modern-day setting. If the setting is historic or futuristic, please ensure that the setting chosen does not make use of overly-used clichés or obvious tropes like Victorian era, steam-punk, or other such similar settings unless the topic *explicitly* demands them."}
    ]

def missing_book_spec_messages(field, text_spec):
    """
    Construct a prompt for adding a missing field to a book specification.

    Args:
        field: The missing field (e.g. 'Genre', 'Setting', etc.).
        text_spec: The existing book specification.

    Returns:
        A list of messages for the prompt, with the role of the first message set to "system" and the second message set to "user".
    """
    
    return [
        {"role": "system", "content": ""},
        {"role": "user",
         "content": f"Provide ONLY the missing {field} and its value, strictly adhering to the existing specification. Do not alter existing values:\n\"\"\"{text_spec}\"\"\""}
    ]

def enhance_book_spec_messages(book_spec, form):
    """
    Construct a prompt for enhancing a book specification.

    Args:
        book_spec: The existing book specification.
        form: The story form (e.g. novel, novella, etc.).

    Returns:
        A list of messages for the prompt, with the role of the first message set to "system" and the second message set to "user".
    """
    
    return [
        {"role": "system", "content": ""},
        {"role": "user",
         "content": f"Enhance the existing {form} specification, strictly building upon all existing values. Deepen dark themes, erotic elements, imagery, and moral ambiguity. Do not add additional top level keys or alter the format. The specification MUST BE EXACTLY the following:\n\"\"\"\n{book_spec_format}\"\"\"\nProvide only the enhanced specification, without any additional conversational text. Existing Specification:\n\"\"\"{book_spec}\"\"\""}
    ]

def create_plot_chapters_messages(book_spec, form):
    """
    Construct a prompt for creating a three-act plot outline.

    Args:
        book_spec: The book specification.
        form: The story form (e.g. novel, novella, etc.).

    Returns:
        A list of messages for the prompt, with the role of the first message set to "system" and the second message set to "user".
    """
    return [
        {"role": "system", "content": ""},
        {"role": "user",
         "content": f"Create a three-act plot for a {form}, strictly adhering to the premise and other details of the specification. Each act should build to a point of moral compromise. Format:\nActs\n\nSpecification:\n\"\"\"{book_spec}\"\"\""}
    ]

def create_chapters_messages(act_num, text_plan, book_spec, form, num_chapters_in_act):
    """
    Constructs a prompt for generating chapter descriptions for a specific act.

    Args:
        act_num (int): The act number for which to generate chapter descriptions.
        text_plan (str): The existing text plan of the story.
        book_spec (str): The book specification.
        form (str): The story form (e.g., novel, novella).
        num_chapters_in_act (int): The number of chapters to generate for this act.

    Returns:
        list: A list of messages for the prompt.
    """
    return [
        {"role": "system", "content": ""},
        {"role": "user",
         "content": f"Generate descriptions for {num_chapters_in_act} chapters in Act {act_num + 1} of a {form}. "
                    f"Each chapter should advance the plot, focusing on character development and building tension. "
                    f"Strictly adhere to the existing plan and book specification. "
                    f"Provide a concise description for each chapter, outlining key events and character interactions.\n\n"
                    f"Existing Plan:\n\"\"\"{text_plan}\"\"\"\n\n"
                    f"Book Specification:\n\"\"\"{book_spec}\"\"\""}
    ]

def enhance_plot_chapters_messages(act_num, text_plan, book_spec, form):
    """
    Creates a prompt for refining a plot act.

    Args:
        act_num: The act number to refine.
        text_plan: The existing outline of the story.
        book_spec: The book specification.
        form: The story form (e.g. novel, novella, etc.).

    Returns:
        A list of messages for the prompt.
    """
    return [
        {"role": "system", "content": ""},
        {"role": "user",
         "content": f"Enhance the following act from the plot outline, ensuring it aligns with the dark and morally ambiguous tone of the book specification. "
                    f"Expand on the existing plot points, adding depth and complexity to character motivations and interactions. "
                    f"The enhanced act should maintain the overall structure and progression of the original plot while enriching the narrative with more detailed and nuanced storytelling.\n\n"
                    f"Act to Enhance: Act {act_num + 1}\n\n"
                    f"Existing Plot Outline:\n\"\"\"{text_plan}\"\"\"\n\n"
                    f"Book Specification:\n\"\"\"{book_spec}\"\"\""}
    ]

def split_chapters_into_scenes_messages(act_num, text_act, form):
    """
    Construct a prompt for splitting chapters into scenes.

    :param act_num: The number of the act to split
    :param text_act: The text of the act to split
    :param form: The form of the book (e.g. novel, novella)
    :return: A list of two dictionaries, the first with role "system" and the second with role "user" and content set to the generated prompt
    """
    return [
        {"role": "system", "content": ""},
        {"role": "user",
         "content": f"Deconstruct each chapter in Act {act_num} into 3-5 scenes per chapter, using the format:\n\"\"\"{scene_spec_format}\"\"\"\nAct {act_num}:\n\"\"\"{text_act}\"\"\""}
    ]

def scene_messages(scene, sc_num, ch_num, text_plan, form, plot_summary, characters, events, theme, prev_scene_summary, retrieved_context):
    """
    Construct a prompt for a scene, including the scene specification, chapter number, book form, overall plot summary, key characters, important events, and overall plot.

    :param scene: The scene specification
    :param sc_num: The scene number
    :param ch_num: The chapter number
    :param text_plan: The overall plot plan
    :param form: The form of the book (e.g. novel, novella)
    :param plot_summary: A short summary of the overall plot
    :param characters: A dictionary of key characters with descriptions
    :param events: A list of important events
    :param theme: The theme of the story
    :param prev_scene_summary: A short summary of the previous scene (if any)
    :param retrieved_context: Any additional context retrieved from the embeddings manager (if any)
    :return: A list of two dictionaries, the first with role "system" and the second with role "user" and content set to the generated prompt
    """
    character_details = "\n".join([f"- {name}: {data.get('description', 'No description')} " for name, data in characters.items()])
    event_list = "\n".join([f"- {event}" for event in events])

    prompt_content = f"Write a detailed scene for {form}, using dark, cynical, erotic speculative fiction. Use sensual imagery, depth, and unsettling implications. Prioritize literary prose and realistic dialogue. Scene {sc_num}, Chapter {ch_num}. Scene:\n\"\"\"{scene}\"\"\"\n\nOverall plot summary:\n\"\"\"{plot_summary}\"\"\"\n\nTheme:\n\"\"\"{theme}\"\"\"\n\nKey characters:\n{character_details}\n\nImportant events:\n{event_list}\n\nOverall plot:\n\"\"\"{text_plan}\"\"\""

    if prev_scene_summary:
        prompt_content += f'\n\nPrevious Scene Summary: \"\"\"{prev_scene_summary}\"\"\"'

    if retrieved_context:
        prompt_content += f"\n\nRetrieved context:\n{retrieved_context}"

    return [
        {"role": "system", "content": ""},
        {"role": "user",
         "content": prompt_content}
    ]

def title_generation_messages(topic):
    """
    Returns a list of message dictionaries for generating a title.

    The single user message requests a concise title for a dark, erotic story
    about the given topic.

    :param topic: The topic of the story to generate a title for.
    :return: A list of message dictionaries.
    """
    return [
        {"role": "system", "content": ""},
        {"role": "user",
         "content": f"Generate a single, concise title for a dark, erotic story about: {topic}. Do not include any additional text beyond the title itself."}
    ]

def summarization_messages(text, length_in_words=60):
    """
    Returns a list of message dictionaries for generating a summary.

    The single user message requests a concise summary of the given text,
    focusing on the most relevant entities and details. The summary should be
    approximately the given number of words in length.

    :param text: The text to summarize.
    :param length_in_words: The desired length of the summary in words. Defaults to 60.
    :return: A list of message dictionaries.
    """
    return [
        {"role": "system", "content": ""},
        {"role": "user",
         "content": f"Summarize the following text into a concise summary of approximately {length_in_words} words, focusing on the most relevant entities and details:\n\"\"\"{text}\"\"\""}
    ]