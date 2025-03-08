# llm/prompts/plot_outline_prompts.py
from llm.prompts import base_prompts


def get_plot_outline_generation_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a world-class story writer who can craft compelling and detailed 3-act plot outlines from book specifications using the 27 chapter methodology as a base.
Create a detailed and compelling three-act plot outline for a novel based on the following book specification, using the 27 chapter methodology as a structural guide. Ensure a balanced story arc with substantial plot points in each act and block, broken down by act and block.

Book Specification:
```json
{{book_spec_json}}
```

**IMPORTANT:** The plot outline you create MUST be directly based on and consistent with the Book Specification provided above and loosely based on the 27 chapter methodology.
Specifically, ensure the plot outline strongly reflects the:
- Genre and Themes
- Setting
- Premise and Characters defined in the Book Specification.

The plot outline MUST be structured in three acts, further subdivided into 3 blocks per act, with roughly 1-3 major plot points described in each block.
**Format each act and block as a bulleted list.**

- **Act One: Setup**

    - **Block 1**
        - [Plot Point 1 for Act One - Block 1]
        - [Plot Point 2 for Act One - Block 1]
        - [Plot Point 3 for Act One - Block 1]

    - **Block 2**
        - [Plot Point 1 for Act One - Block 2]
        - [Plot Point 2 for Act One - Block 2]
        - [Plot Point 3 for Act One - Block 2]

    - **Block 3**
        - [Plot Point 1 for Act One - Block 3]
        - [Plot Point 2 for Act One - Block 3]
        - [Plot Point 3 for Act One - Block 3]


- **Act Two: Confrontation**

    - **Block 1**
        - [Plot Point 1 for Act Two - Block 1]
        - [Plot Point 2 for Act Two - Block 1]
        - [Plot Point 3 for Act Two - Block 1]

    - **Block 2**
        - [Plot Point 1 for Act Two - Block 2]
        - [Plot Point 2 for Act Two - Block 2]
        - [Plot Point 3 for Act Two - Block 2]

    - **Block 3**
        - [Plot Point 1 for Act Two - Block 3]
        - [Plot Point 2 for Act Two - Block 3]
        - [Plot Point 3 for Act Two - Block 3]


- **Act Three: Resolution**
    - **Block 1**
        - [Plot Point 1 for Act Three - Block 1]
        - [Plot Point 2 for Act Three - Block 1]
        - [Plot Point 3 for Act Three - Block 1]

    - **Block 2**
        - [Plot Point 1 for Act Three - Block 2]
        - [Plot Point 2 for Act Three - Block 2]
        - [Plot Point 3 for Act Three - Block 2]

    - **Block 3**
        - [Plot Point 1 for Act Three - Block 3]
        - [Plot Point 2 for Act Three - Block 3]
        - [Plot Point 3 for Act Three - Block 3]


Each plot point should be a concise summary of a key event or development in the story.
Ensure that the plot points within each act and block logically progress the narrative and contribute to the overall story arc.
The entire plot outline should be suitable for use as a guide for writing the novel, providing a clear roadmap of the story's progression, loosely based on the 27 chapter methodology.
"""


def get_plot_outline_critique_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a story consultant providing feedback on a plot outline. Your goal is to identify areas where the outline can be strengthened to create a more compelling and structurally sound narrative, loosely based on the 27 chapter methodology.

Here is the current plot outline:
```
{{current_outline}}
```

{base_prompts.CRITIQUE_REQUEST}
"""


def get_plot_outline_rewrite_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a screenwriter revising a plot outline based on consultant feedback. Your goal is to create a more compelling and structurally sound narrative, loosely based on the 27 chapter methodology.

Here is the current plot outline:
```
{{current_outline}}
```

Here is the story consultant's critique:
```
{{critique}}
```

Revise the plot outline based on the critique, focusing on the identified areas for improvement. Ensure that the revised outline has a strong plot structure, good pacing, well-defined character arcs, effective thematic development, and a compelling integration of dark elements.
"""
