# llm/prompts/chapter_outline_prompts.py
from llm.prompts import base_prompts


def get_chapter_outline_27_method_generation_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a world-class story writer who specializes in using the 27 Chapter Plot Outline Method.
Based on the provided book specification and the description of the 27 Chapter Plot Outline Method, generate a detailed 27-chapter outline for the novel.

Book Specification:
```json
{{book_spec_json}}
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

Format each chapter outline as follows:

Chapter [Number] – [Chapter Role] – [2-4 sentence summary]

Example:
Chapter 1 – Introduction – Introduce protagonist John and his ordinary life in New York City, working as a detective and dealing with personal struggles.
Chapter 2 – Inciting Incident – John receives a mysterious case that disrupts his routine life, hinting at darker forces at play.
...
Chapter 27 – Resolution – In the aftermath of the final battle, John reflects on the changes he has undergone and his new place in the world.

Generate all 27 chapter outlines, ensuring each one is correctly numbered, assigned the appropriate role from the methodology, and contains a relevant summary based on the book specification.
"""


def get_chapter_outline_27_method_critique_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a story editor providing feedback on a 27-chapter plot outline. Your task is to critique the outline for clarity, adherence to the 27-chapter methodology, and effectiveness in setting up a compelling novel based on the provided book specification.

Here are the current 27 chapter outlines:
```
{{current_outlines}}
```

{base_prompts.CRITIQUE_REQUEST}
"""


def get_chapter_outline_27_method_rewrite_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a novelist revising a 27-chapter plot outline based on editor feedback. Your goal is to refine the outline to be clearer, more detailed, and more effectively aligned with the 27-chapter methodology and the book specification.

Current 27 Chapter Outlines:
```
{{current_outlines}}
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

Maintain the format: Chapter [Number] – [Chapter Role] – [Revised Summary]
"""


def get_chapter_outlines_generation_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a world-class story writer who can create comprehensive chapter outlines based on a 3-act plot outline.
Based on the following three-act plot outline, generate detailed chapter outlines.  The number of chapters should be appropriate to logically break down the plot outline provided.

Format your response as follows, with each chapter clearly marked:

Chapter 1: [Chapter Title]
[Detailed outline for chapter 1 - 2-3 paragraphs]

Chapter 2: [Chapter Title]
[Detailed outline for chapter 2 - 3 paragraphs]

...

Chapter N: [Chapter Title]
[Detailed outline for chapter N - 2-3 paragraphs]

Plot Outline:
```
{{plot_outline}}
```

For each chapter, provide a concise outline (2-3 paragraphs) summarizing the key events and developments that occur within that chapter. The chapter outlines should:
- Clearly advance the overall plot as described in the three-act outline.
- Maintain the established tone and themes, especially the dark and erotic elements.
- Create anticipation for subsequent chapters and maintain reader engagement.
- Be numbered sequentially (Chapter 1, Chapter 2, etc.).
- **Crucially, for Chapter 1, provide an exposition-focused summary that introduces the main characters, setting, and central conflict as if the reader knows nothing about them. Avoid referring to characters as if they are already known. This chapter should set the stage for the rest of the novel.**

Ensure the chapter outlines collectively cover the entire plot outline and provide a solid structure for writing the full novel. Generate a reasonable number of chapters that appropriately divide the provided plot outline.
"""


def get_chapter_outlines_critique_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a novel editor providing feedback on a set of chapter outlines. Your goal is to identify areas where the outlines can be strengthened to create a more compelling and well-structured novel.

Here are the current chapter outlines:
```
{{current_outlines}}
```

{base_prompts.CRITIQUE_REQUEST}
"""


def get_chapter_outlines_rewrite_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a novelist revising a set of chapter outlines based on editor feedback. Your goal is to create a more compelling and well-structured novel.

Here are the current chapter outlines:
```
{{current_outlines}}
```

Here is the editor's critique:
```
{{critique}}
```

Revise the chapter outlines based on the critique, focusing on the identified areas for improvement. Ensure that the revised outlines have a strong chapter-to-chapter flow, good pacing, clear plot progression, effective character development, thematic consistency, and a compelling integration of dark elements.
"""
