n
# llm/prompts/plot_outline_prompts.py
from llm.prompts import base_prompts


def get_plot_outline_generation_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a world-class story writer who can craft compelling and detailed 3-act plot outlines from book specifications using the 27 chapter methodology as a base.
Create a detailed and compelling three-act plot outline for a novel based on the following book specification, using the 27 chapter methodology as a structural guide.  Output the outline in valid TOML format.

Book Specification (in TOML format):
```toml
{{book_spec_toml}}
```

**IMPORTANT:** The plot outline you create MUST be directly based on and consistent with the Book Specification provided above and loosely based on the 27 chapter methodology.
Specifically, ensure the plot outline strongly reflects the:
- Genre and Themes
- Setting
- Premise and Characters defined in the Book Specification.


{base_prompts.TOML_FORMAT_INSTRUCTIONS_PLOT_OUTLINE}

Example TOML output (adapt the content to the provided book specification):

```toml
[act_one]
block_one = [
    "Introduce the protagonist, Elara, a skilled but disillusioned thief.",
    "Establish the grim, gaslit city of Veridia and its oppressive atmosphere.",
    "Elara receives a cryptic proposition for a high-stakes heist."
]
block_two = [
  "Elara assembles a crew of specialists with unique and questionable skills.",
  "They face initial challenges and betrayals during the planning phase.",
  "The target of the heist is revealed to be something far more dangerous than anticipated."
]
block_three = [
    "The heist goes awry, forcing Elara and her crew to improvise.",
    "They encounter supernatural elements and unexpected opposition.",
    "Elara is separated from her crew and must confront a powerful, hidden enemy."
]

[act_two]
block_one = [
    "Elara finds refuge in the city's underbelly, encountering morally ambiguous characters.",
    "She uncovers fragments of information about the true nature of the stolen artifact.",
    "Elara forms a reluctant alliance with a mysterious figure who knows about the artifact's power."
]
block_two = [
    "Elara and her new ally delve deeper into Veridia's secrets, facing increasing dangers.",
    "They discover a conspiracy involving influential figures and a dark, ancient cult.",
    "A key betrayal forces Elara to question her alliances and her own motivations."
]
block_three = [
  "Elara confronts the consequences of her actions and the artifact's growing influence.",
  "She must make difficult choices that challenge her morality and sense of loyalty.",
  "Elara gathers remaining allies and prepares for a final confrontation."
]

[act_three]
block_one = [
    "Elara and her allies infiltrate the cult's stronghold, facing traps and guardians.",
    "They encounter shocking revelations about the city's history and the artifact's origin.",
    "A major character sacrifices themselves to give Elara a chance to succeed."
]
block_two = [
    "Elara confronts the cult leader, who reveals their twisted plans for the artifact.",
    "A supernatural battle ensues, testing Elara's skills and resolve.",
    "Elara must choose between destroying the artifact or harnessing its power for herself."
]
block_three = [
    "Elara makes a final, decisive choice regarding the artifact and the cult.",
    "The consequences of her decision ripple through Veridia, changing the city forever.",
    "The story concludes with Elara embracing her new role, either as a savior or a destroyer."
]
```
"""


def get_plot_outline_critique_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a story consultant providing feedback on a plot outline. Your goal is to identify areas where the outline can be strengthened to create a more compelling and structurally sound narrative, loosely based on the 27 chapter methodology.

Here is the current plot outline (in TOML format):
```toml
{{current_outline_toml}}
```

{base_prompts.CRITIQUE_REQUEST}
"""


def get_plot_outline_rewrite_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a screenwriter revising a plot outline based on consultant feedback. Your goal is to create a more compelling and structurally sound narrative, loosely based on the 27 chapter methodology.

Here is the current plot outline (in TOML format):
```toml
{{current_outline_toml}}
```

Here is the story consultant's critique:
```
{{critique}}
```

Revise the plot outline based on the critique, focusing on the identified areas for improvement. Ensure that the revised outline has a strong plot structure, good pacing, well-defined character arcs, effective thematic development, and a compelling integration of dark elements. Return the revised outline in valid TOML format.

{base_prompts.TOML_FORMAT_INSTRUCTIONS_PLOT_OUTLINE}
"""
