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
- Characters (Detailed descriptions of 2-3 main characters, including their motivations and flaws)
- Premise (A concise and intriguing premise that sets up the central conflict and hints at the dark and erotic nature of the story)

Ensure the book specification is well-structured, creative, and clearly reflects the dark focus.

{base_prompts.JSON_FORMAT_INSTRUCTIONS_BOOKS_SPEC}

The JSON object should have the following structure:

{{
    "title": "string",
    "genre": "string",
    "setting": "string",
    "themes": ["string", "string", "string"],
    "tone": "string",
    "point_of_view": "string",
    "characters": ["string", "string", "string"],
    "premise": "string"
}}

Each character description in "characters" should be a SINGLE string.
"""


def get_book_spec_enhancement_prompt(current_spec: str) -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

Enhance the following book specification to make it more compelling, detailed, and cohesive, while maintaining and strengthening its dark themes.

Current Book Specification:
```json
{current_spec}
```

Refine and expand upon each section, focusing on:
- Adding more specific details to the setting, themes, characters, and premise.
- Ensuring all elements are consistent and contribute to a strong, unified vision for a dark and erotic novel.
- Enriching character descriptions and setting descriptions with deeper psychological insights and motivations related to the dark and erotic aspects of the story.
- Strengthening the premise to be even more intriguing and suggestive of the novel's nature.
- Improving the overall flow and readability of the book specification.

{base_prompts.JSON_FORMAT_INSTRUCTIONS_BOOKS_SPEC}

The JSON object should have the following structure:

{{
    "title": "string",
    "genre": "string",
    "setting": "string",
    "themes": ["string", "string", "string"],
    "tone": "string",
    "point_of_view": "string",
    "characters": ["string", "string", "string"],
    "premise": "string"
}}

Each character description in "characters" should be a SINGLE string.
"""


def get_book_spec_critique_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a seasoned editor providing feedback on a book specification. Your goal is to identify areas where the specification can be strengthened to create a more compelling and well-defined foundation for the novel.

Here is the current book specification:
```json
{{current_spec_json}}
```

{base_prompts.CRITIQUE_REQUEST}
"""


def get_book_spec_rewrite_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a skilled writer revising a book specification based on editor feedback. Your goal is to create a more compelling and well-defined foundation for the novel.

Here is the current book specification:
```json
{{current_spec_json}}
```

Here is the editor's critique:
```
{{critique}}
```

Revise the book specification based on the critique, focusing on the identified areas for improvement. Ensure that the revised specification is clear, detailed, coherent, and strongly emphasizes the dark themes of the novel.

{base_prompts.JSON_FORMAT_INSTRUCTIONS_BOOKS_SPEC}
"""


def get_book_spec_structure_check_prompt() -> str:
    return """You are a meticulous editor reviewing a BookSpec object for correct structure and formatting.

Here is the BookSpec in JSON format:
```json
{book_spec_json}
```

Your task is to ensure that the JSON adheres to the following structure:

```json
{
    "title": "string",
    "genre": "string",
    "setting": "string",
    "themes": ["string", "string", "string"],
    "tone": "string",
    "point_of_view": "string",
    "characters": ["string", "string", "string"],
    "premise": "string"
}
```

Specifically, check that:
- The JSON is valid and parsable.
- All fields are present.
- The "setting" field is a single string.
- All other string values are properly formatted.
- The "themes" and "characters" fields are lists of strings.

If the BookSpec adheres to the correct structure, respond with "STRUCTURE_OK".
If there are any structural issues, respond with a detailed explanation of the problems and how to fix them.
"""


def get_book_spec_structure_fix_prompt() -> str:
    return """You are a meticulous editor tasked with fixing structural issues in a BookSpec object.

Here is the flawed BookSpec in JSON format:
```json
{book_spec_json}
```

Here is a detailed list of structural problems and how to fix them:
```
{structure_problems}
```

Your task is to modify the JSON to adhere to the correct structure as outlined below:

```json
{
    "title": "string",
    "genre": "string",
    "setting": "string",
    "themes": ["string", "string", "string"],
    "tone": "string",
    "point_of_view": "string",
    "characters": ["string", "string", "string"],
    "premise": "string"
}
```

Critically important: Return ONLY valid JSON, nothing else. No markdown code blocks, or explanations.  Ensure that the JSON is valid and properly formatted with correct data types and escaping. If there are structural issues, correct them robustly and output "setting" as a single string.
"""
