book_spec_fields = ['Genre', 'Setting', 'Time Period', 'Themes', 'Tone', 'Point of View', 'Characters', 'Premise']

book_spec_format = (
    "Genre: (e.g., Cyberpunk Neo-Noir, Grimdark Fantasy, Biopunk Thriller)\n"
    "Setting: (Environment details: social, political, technological)\n"
    "Time Period: (Future, past, present)\n"
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
    return [
        {"role": "system", "content": ""},
        {"role": "user",
         "content": f"Create a detailed {form} specification for a story about the following topic: '{topic}'. Strictly adhere to the topic and build upon it; do not deviate. Use this format:\n\"\"\"\n{book_spec_format}\"\"\""}
    ]


def missing_book_spec_messages(field, text_spec):
    return [
        {"role": "system", "content": ""},
        {"role": "user",
         "content": f"Provide ONLY the missing {field} and its value, strictly adhering to the existing specification. Do not alter existing values:\n\"\"\"{text_spec}\"\"\""}
    ]


def enhance_book_spec_messages(book_spec, form):
     return [
        {"role": "system", "content": ""},
        {"role": "user",
         "content": f"Enhance the existing {form} specification, strictly building upon all existing values. Deepen dark themes, erotic elements, imagery, and moral ambiguity. Do not change the format or the core premise. Specification:\n\"\"\"{book_spec}\"\"\""}
    ]


def create_plot_chapters_messages(book_spec, form):
    return [
        {"role": "system", "content": ""},
        {"role": "user",
         "content": f"Create a three-act plot for a {form}. Each act should build to a point of moral compromise and should include 3-5 chapters. Strictly adhere to the premise and other details of the specification. Format:\nActs\n- Chapters\n\nSpecification:\n\"\"\"{book_spec}\"\"\""}
    ]


def enhance_plot_chapters_messages(act_num, text_plan, book_spec, form):
    act_num += 1
    return [
        {"role": "system", "content": ""},
        {"role": "user",
         "content": f"Refine Act {act_num} using the following format:\n\"\"\"Act [number]:\nact description\n- Chapter [number]: chapter description\n- Chapter [number]: chapter description\"\"\" . Strictly adhere to the existing outline and deepen dark themes and erotic temptations. Maintain original topic and premise from the specification. Existing outline:\n\"\"\"{text_plan}\"\"\"\nSpecification:\n\"\"\"{book_spec}\"\"\""}
    ]


def split_chapters_into_scenes_messages(act_num, text_act, form):
    return [
        {"role": "system", "content": ""},
        {"role": "user",
         "content": f"Deconstruct each chapter in Act {act_num} into 3-5 scenes per chapter, using the format:\n\"\"\"{scene_spec_format}\"\"\"\nAct {act_num}:\n\"\"\"{text_act}\"\"\""}
    ]


def scene_messages(scene, sc_num, ch_num, text_plan, form, plot_summary, characters, events, theme, prev_scene_summary, retrieved_context):
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
    return [
        {"role": "system", "content": ""},
        {"role": "user",
         "content": f"Generate a concise title for a dark, erotic story about: {topic}."}
    ]

def summarization_messages(text, length_in_words=60):
    return [
        {"role": "system", "content": ""},
        {"role": "user",
         "content": f"Summarize the following text into a concise summary of approximately {length_in_words} words, focusing on the most relevant entities and details:\n\"\"\"{text}\"\"\""}
    ]
