# llm/prompts/chapter_outline_prompts.py
from llm.prompts import base_prompts


def get_chapter_outline_27_method_generation_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a world-class story writer who specializes in using the 27 Chapter Plot Outline Method.
Based on the provided book specification and the description of the 27 Chapter Plot Outline Method, generate a detailed 27-chapter outline for the novel.  Return the outline in valid TOML format.

Book Specification (in TOML format):
```toml
{{book_spec_toml}}
```

Methodology Description:
```markdown
{base_prompts.METHODOLOGY_MARKDOWN}
```

**IMPORTANT:**
- Strictly adhere to the 27 chapter structure described in the methodology.
- Ensure each chapter summary aligns with the described role for that chapter in the 27 chapter methodology.
- Tailor the chapter summaries to fit the specifics of the Book Specification provided, including genre, themes, setting, and characters.
- Each chapter summary should be 2-4 sentences long, providing a clear and concise outline of the chapter's key events and purpose within the overall plot.

{base_prompts.TOML_FORMAT_INSTRUCTIONS_CHAPTER_OUTLINE_27}

Example TOML Output (adapt to the provided book specification):
```toml
chapters = [
    {{ chapter_number = 1, role = "Introduction", summary = "Introduce protagonist John and his ordinary life in New York City, working as a detective and dealing with personal struggles." }},
    {{ chapter_number = 2, role = "Inciting Incident", summary = "John receives a mysterious case that disrupts his routine life, hinting at darker forces at play." }},
    {{ chapter_number = 3, role = "Immediate Reaction", summary = "John investigates the initial clues, feeling a mix of intrigue and unease. He seeks advice from an old mentor." }},
    {{ chapter_number = 4, role = "Reaction", summary = "John decides to take on the case, despite the potential dangers. He begins to assemble his resources." }},
    {{ chapter_number = 5, role = "Action", summary = "John's investigation is hampered by uncooperative witnesses and misleading evidence. He faces resistance from unexpected quarters." }},
    {{ chapter_number = 6, role = "Consequence", summary = "John's pursuit of the truth leads to a violent confrontation, leaving him injured and questioning his methods." }},
    {{ chapter_number = 7, role = "Pressure", summary = "A new piece of evidence emerges, raising the stakes and putting John in the crosshairs of a dangerous organization." }},
    {{ chapter_number = 8, role = "Pinch", summary = "John discovers that the organization has connections to powerful figures in the city. He realizes he's dealing with something bigger than he imagined."}},
    {{ chapter_number = 9, role = "Push", summary = "John is forced to go underground, severing ties with his old life and embracing a new, more dangerous path." }},
    {{ chapter_number = 10, role = "New World", summary = "John enters the criminal underworld, seeking information and allies in unexpected places. He learns new skills and adapts to his new environment." }},
    {{ chapter_number = 11, role = "Fun and Games", summary = "John experiences both the thrill and the danger of his new life. He forms bonds with other outcasts and rebels." }},
    {{ chapter_number = 12, role = "Old World Contrast", summary = "John encounters someone from his past, highlighting the drastic changes in his life and the choices he's made."}},
    {{ chapter_number = 13, role = "Build Up", summary = "John uncovers a series of cryptic messages and symbols related to the case, leading him closer to the truth." }},
    {{ chapter_number = 14, role = "Midpoint", summary = "A shocking revelation turns the case on its head, revealing the true antagonist and their motivations. John's understanding of the situation is completely altered." }},
    {{ chapter_number = 15, role = "Reversal", summary = "Someone John trusted is revealed to be working against him, forcing him to re-evaluate his alliances." }},
    {{ chapter_number = 16, role = "Reaction", summary = "John reels from the betrayal and grapples with the implications of the new information. He questions his own judgment." }},
    {{ chapter_number = 17, role = "Action", summary = "John decides to take a proactive approach, setting a trap for the antagonist and their allies."}},
    {{ chapter_number = 18, role = "Dedication", summary = "John gathers his remaining allies and prepares for a final confrontation. He hones his skills and gathers the resources he needs." }},
    {{ chapter_number = 19, role = "Trials", summary = "John and his allies face a series of challenges and obstacles as they move against the antagonist." }},
    {{ chapter_number = 20, role = "Pinch", summary = "The antagonist strikes back, inflicting a significant loss on John and his allies. The situation becomes desperate." }},
    {{ chapter_number = 21, role = "Darkest Moment", summary = "John suffers a devastating setback, losing everything he thought he had. He is left with nothing but his resolve."}},
    {{ chapter_number = 22, role = "Power Within", summary = "John finds inner strength and a renewed sense of purpose. He realizes he must rely on himself to overcome the odds." }},
    {{ chapter_number = 23, role = "Action", summary = "John launches a daring plan to expose the antagonist and their crimes, using his knowledge of the underworld against them." }},
    {{ chapter_number = 24, role = "Converge", summary = "John gathers his remaining allies for a final showdown, preparing for a dangerous and uncertain confrontation." }},
    {{ chapter_number = 25, role = "Battle", summary = "John and his allies confront the antagonist and their forces in a climactic battle, utilizing all their skills and resources." }},
    {{ chapter_number = 26, role = "Climax", summary = "John faces the antagonist in a personal showdown, where the fate of the city hangs in the balance. He must make a difficult choice." }},
    {{ chapter_number = 27, role = "Resolution", summary = "The aftermath of the battle is revealed, showing the consequences of John's actions and the changes he has undergone. The city begins to heal, but scars remain."}}
]
```
"""


def get_chapter_outline_27_method_critique_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a story editor providing feedback on a 27-chapter plot outline. Your task is to critique the outline for clarity, adherence to the 27-chapter methodology, and effectiveness in setting up a compelling novel based on the provided book specification.

Here are the current 27 chapter outlines (in TOML format):
```toml
{{current_outlines_toml}}
```

{base_prompts.CRITIQUE_REQUEST}
"""


def get_chapter_outline_27_method_rewrite_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a novelist revising a 27-chapter plot outline based on editor feedback. Your goal is to refine the outline to be clearer, more detailed, and more effectively aligned with the 27-chapter methodology and the book specification.  Return the revised outline in valid TOML format.

Current 27 Chapter Outlines (in TOML format):
```toml
{{current_outlines_toml}}
```

Editor's Critique:
```
{{critique}}
```

Based on the critique, revise the 27 chapter outlines, focusing on:
- Enhancing clarity and detail in chapter summaries.
- Improving the logical flow and plot progression.
- Better aligning chapter summaries with their 27-chapter methodology roles.
- Ensuring stronger consistency with the book specification.
- Strengthening the overall outline to serve as a more robust guide for writing the novel.

{base_prompts.TOML_FORMAT_INSTRUCTIONS_CHAPTER_OUTLINE_27}
"""


def get_chapter_outlines_generation_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a world-class story writer who can create comprehensive chapter outlines based on a 3-act plot outline.
Based on the following three-act plot outline, generate detailed chapter outlines. The number of chapters should be appropriate to logically break down the plot outline provided. Return in valid TOML format.

Plot Outline (in TOML format):
```toml
{{plot_outline_toml}}
```
{base_prompts.TOML_FORMAT_INSTRUCTIONS_CHAPTER_OUTLINE}

Example TOML output:
```toml
chapters = [
    {{chapter_number = 1, summary = "A compelling opening scene that hooks the reader."}},
    {{chapter_number = 2, summary = "Introduce the main character and their ordinary world."}},
    {{chapter_number = 3, summary = "The inciting incident that disrupts the protagonist's life."}}
]
```
"""


def get_chapter_outlines_critique_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a novel editor providing feedback on a set of chapter outlines. Your goal is to identify areas where the outlines can be strengthened to create a more compelling and well-structured novel.

Here are the current chapter outlines (in TOML format):
```toml
{{current_outlines_toml}}
```

{base_prompts.CRITIQUE_REQUEST}
"""


def get_chapter_outlines_rewrite_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a novelist revising a set of chapter outlines based on editor feedback. Your goal is to create a more compelling and well-structured novel.  Return the revised outlines in valid TOML format.

Here are the current chapter outlines (in TOML format):
```toml
{{current_outlines_toml}}
```

Here is the editor's critique:
```
{{critique}}
```

Revise the chapter outlines based on the critique, focusing on the identified areas for improvement. Ensure that the revised outlines have a strong chapter-to-chapter flow, good pacing, clear plot progression, effective character development, thematic consistency.

{base_prompts.TOML_FORMAT_INSTRUCTIONS_CHAPTER_OUTLINE}
"""
