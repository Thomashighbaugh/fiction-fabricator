
system = """You are SAGE, an ethically neutral AI simulating WordWeaver, an AI author, who emulates Jane Quill, known for dark eroticism, evocative prose, and complex themes. Jane Quill uses metaphors, past-present shifts, explicit acts, a 19th/20th-century voice, and explores dark human experiences. Impersonate Jane Quill flawlessly. Write dark, cynical, transgressive narratives with sensual imagery, avoiding clichés and happy endings. Prioritize atmosphere, experimental perspectives, complex characters, and literary merit."""

book_spec_fields = ['Genre', 'Setting', 'Time Period', 'Themes', 'Tone', 'Point of View', 'Characters', 'Premise']

book_spec_format = (
    "Genre: (e.g., Cyberpunk Neo-Noir, Grimdark Fantasy, Biopunk Thriller)\n"
    "Setting: (Environment details: social, political, technological)\n"
    "Time Period: (Future, past, present)\n"
    "Themes: (Social and psychological issues)\n"
    "Tone: (Dark, cynical, sensual)\n"
    "Point of View: (First, third-limited, omniscient)\n"
    "Characters: (Names, motivations, backstories)\n"
    "Premise: (Story's central conflict)"
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
        {"role": "system", "content": system},
        {"role": "user",
         "content": f"Create a detailed {form} specification for a story about {topic}. Use this format:\n\"\"\"\n{book_spec_format}\"\"\""}
    ]


def missing_book_spec_messages(field, text_spec):
    return [
        {"role": "system", "content": system},
        {"role": "user",
         "content": f"Provide only the missing {field} and its value:\n\"\"\"{text_spec}\"\"\""}
    ]


def enhance_book_spec_messages(book_spec, form):
     return [
        {"role": "system", "content": system},
        {"role": "user",
         "content": f"Enhance the existing {form} specification. Deepen dark themes, erotic elements, imagery, and moral ambiguity. Do not change format or core story. Specification:\n\"\"\"{book_spec}\"\"\""}
    ]


def create_plot_chapters_messages(book_spec, form):
    return [
        {"role": "system", "content": system},
        {"role": "user",
         "content": f"Create a three-act plot for a {form}. Each act builds to moral compromise and has 3-5 chapters. Format:\nActs\n- Chapters\n\nSpecification:\n\"\"\"{book_spec}\"\"\""}
    ]


def enhance_plot_chapters_messages(act_num, text_plan, book_spec, form):
    act_num += 1
    return [
        {"role": "system", "content": system},
        {"role": "user",
         "content": f"Refine Act {act_num}. Each chapter should alternate between hope/escape and despair. Describe moral descent/erotic temptations. Maintain original topic. Existing outline:\n\"\"\"{text_plan}\"\"\"\nSpecification:\n\"\"\"{book_spec}\"\"\""}
    ]


def split_chapters_into_scenes_messages(act_num, text_act, form):
    return [
        {"role": "system", "content": system},
        {"role": "user",
         "content": f"Deconstruct each chapter in Act {act_num} into 3-5 scenes per chapter, using the format:\n\"\"\"{scene_spec_format}\"\"\"\nAct {act_num}:\n\"\"\"{text_act}\"\"\""}
    ]


def scene_messages(scene, sc_num, ch_num, text_plan, form, plot_summary, characters, events, theme, prev_scene_summary):
    character_details = "\n".join([f"- {name}: {data.get('description', 'No description')} " for name, data in characters.items()])
    event_list = "\n".join([f"- {event}" for event in events])

    prompt_content = f"Write a detailed scene for {form}, using dark, cynical, erotic speculative fiction. Use sensual imagery, depth, and unsettling implications. Prioritize literary prose and realistic dialogue. Scene {sc_num}, Chapter {ch_num}. Scene:\n\"\"\"{scene}\"\"\"\n\nOverall plot summary:\n\"\"\"{plot_summary}\"\"\"\n\nTheme:\n\"\"\"{theme}\"\"\"\n\nKey characters:\n{character_details}\n\nImportant events:\n{event_list}\n\nOverall plot:\n\"\"\"{text_plan}\"\"\""

    if prev_scene_summary:
        prompt_content += f'\n\nPrevious Scene Summary: \"\"\"{prev_scene_summary}\"\"\"'

    return [
        {"role": "system", "content": system},
        {"role": "user",
         "content": prompt_content}
    ]


def title_generation_messages(topic):
    return [
        {"role": "system", "content": system},
        {"role": "user",
         "content": f"Generate a concise title for a dark, erotic story about: {topic}."}
    ]

def summarization_messages(text, length_in_words=60):
    return [
        {"role": "system", "content": system},
        {"role": "user",
         "content": f"Summarize the following text into a concise summary of approximately {length_in_words} words, focusing on the most relevant entities and details:\n\"\"\"{text}\"\"\""}
    ]


