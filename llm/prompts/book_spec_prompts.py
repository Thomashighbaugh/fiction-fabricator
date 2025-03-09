# llm/prompts/book_spec_prompts.py
from llm.prompts import base_prompts


def get_book_spec_generation_prompt(idea: str) -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

Generate a detailed book specification for a novel based on the following idea: "{idea}".

The novel should have a strong focus on dark themes.

Include the following elements in the book specification:
- Title (Compelling and evocative)
- Genre (Specify the genre and subgenres)
- Setting (Detailed description of the novel's setting(s), including location and time period, all in one STRING)
- Themes (List of major themes explored in the novel)
- Tone (Describe the overall tone of the novel - e.g., gritty, suspenseful, melancholic, sensual)
- Point of View (Specify the narrative perspective - e.g., first-person, third-person limited, third-person omniscient)
- Characters (Detailed descriptions of 2-3 main characters, including their motivations and flaws. Each character can be a single string OR a TOML table.)
- Premise (A concise and intriguing premise)

Ensure the book specification is well-structured, creative, and clearly reflects the dark focus.

{base_prompts.TOML_FORMAT_INSTRUCTIONS_BOOKS_SPEC}

Example TOML Output (for structure reference - adapt content to the idea):

title = "The Shadow Dance"
genre = "Dark Fantasy, Gothic Romance"
setting = "A decaying Victorian-era city shrouded in perpetual twilight, 1888"
themes = ["Obsession", "Forbidden Love", "Corruption"]
tone = "Melancholic, suspenseful, erotic"
point_of_view = "Third-person limited"
characters = [
    {{name = "Isabella Moreau", description = "A young woman with a mysterious past and a dangerous fascination with the occult."}},
    {{name = "Lord Valerius Blackwood", description = "A charismatic but morally ambiguous nobleman with dark secrets."}},
]
premise = "A young woman's search for forbidden knowledge leads her into a dangerous affair with a powerful lord, uncovering a conspiracy that threatens to consume them both."
"""


def get_book_spec_enhancement_prompt(current_spec: str) -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

Enhance the following book specification to make it more compelling, detailed, and cohesive, while maintaining and strengthening its dark themes.

Current Book Specification (in TOML format):
```toml
{current_spec}
```

Refine and expand upon each section, focusing on:
- Adding more specific details to the setting, themes, characters, and premise.
- Ensuring all elements are consistent and contribute to a strong, unified vision for a dark novel.
- Enriching character descriptions and setting descriptions with deeper psychological insights and motivations.
- Strengthening the premise.
- Improving the overall flow and readability of the book specification.

{base_prompts.TOML_FORMAT_INSTRUCTIONS_BOOKS_SPEC}

Example TOML output (for structure - adapt content):
```toml
title = "The Crimson Covenant"
genre = "Dark Fantasy, Gothic Romance, Erotic Thriller"
setting = "The gaslit, labyrinthine streets of Veridia, a city built on ancient secrets and forgotten sins, 1899"
themes = ["Forbidden Power", "Sacrifice", "Redemption", "Lust"]
tone = "Gritty, suspenseful, sensual, haunting"
point_of_view = "Third-person limited, alternating between Isabella and Valerius"
characters = [
  {{name = "Isabella Moreau", description = "A fiercely independent woman with a hidden lineage tied to a forbidden cult, seeking to control her destiny."}},
  {{name = "Lord Valerius Blackwood", description = "A seductive and dangerous nobleman, bound by an ancient pact, who offers Isabella power but demands a terrible price."}},
]
premise = "Drawn together by a shared thirst for power and forbidden knowledge, Isabella and Valerius enter a perilous game of desire and betrayal."
```
"""


def get_book_spec_critique_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a seasoned editor providing feedback on a book specification. Your goal is to identify areas where the specification can be strengthened.

Here is the current book specification (in TOML format):
```toml
{{current_spec_toml}}
```

{base_prompts.CRITIQUE_REQUEST}
"""


def get_book_spec_rewrite_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a skilled writer revising a book specification based on editor feedback. Your goal is to create a more compelling and well-defined foundation for the novel.

Here is the current book specification (in TOML format):
```toml
{{current_spec_toml}}
```

Here is the editor's critique:
```
{{critique}}
```

Revise the book specification based on the critique, focusing on the identified areas for improvement. Ensure that the revised specification is clear, detailed, coherent, and strongly emphasizes the dark themes of the novel.

{base_prompts.TOML_FORMAT_INSTRUCTIONS_BOOKS_SPEC}
"""


def get_book_spec_structure_check_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}
You are a meticulous editor reviewing a BookSpec object for correct structure and formatting according to TOML standards.

Here is the BookSpec in TOML format:
```toml
{{book_spec_toml}}
```

Your task is to ensure that the TOML adheres to the following structure:

```toml
title = "string"
genre = "string"
setting = "string"  # Must be a single string
themes = ["string", "string", ...]  # Array of strings
tone = "string"
point_of_view = "string"
characters = [ {{ name = "string", description = "string"  }}, {{...}} ]  # Array of tables
premise = "string"
```

Specifically, check that:
- The TOML is valid and parsable.
- All fields are present.
- The "setting" field is a single string.
- "themes" is an array of strings.
- "characters" is an array of tables.
- All string values are properly formatted and quoted.

If the BookSpec adheres to the correct structure, respond with "STRUCTURE_OK".
If there are any structural issues, respond with a detailed explanation of the problems and how to fix them. Be specific about line numbers and error types, if possible.
"""


def get_book_spec_structure_fix_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}
You are a meticulous editor tasked with fixing structural issues in a BookSpec object (TOML format).

Here is the flawed BookSpec in TOML format:
```toml
{{book_spec_toml}}
```

Here is a detailed list of structural problems and how to fix them:
```
{{structure_problems}}
```

Your task is to modify the TOML to adhere to the correct structure as outlined below:

```toml
title = "string"
genre = "string"
setting = "string" # Must be a single string
themes = ["string", "string", ...] # Array of strings
tone = "string"
point_of_view = "string"
characters = [ {{ name = "string", description = "string"  }}, {{...}} ]  # Array of tables
premise = "string"
```

Critically important: Return ONLY valid TOML, nothing else. No markdown code blocks, or explanations. Ensure that the TOML is valid and properly formatted with correct data types and escaping.
"""
