# llm/prompt_manager/book_spec_prompts.py
book_spec_prompts = {
    "book_spec_generation_prompt": r"""You are a world-class novelist who can generate entire book specifications based on short story ideas.
Generate a detailed book specification for a novel based on the following idea: "{idea}".

The novel should have a strong focus on dark themes.

Include the following elements in the book specification:
- Title (Compelling and evocative)
- Genre (Specify the genre and subgenres)
- Setting(s) (Detailed description of locations and time period)
- Themes (List of major themes explored in the novel)
- Tone (Describe the overall tone of the novel - e.g., gritty, suspenseful, melancholic, sensual)
- Point of View (Specify the narrative perspective - e.g., first-person, third-person limited, third-person omniscient)
- Characters (Detailed descriptions of 2-3 main characters, including their motivations and flaws)
- Premise (A concise and intriguing premise that sets up the central conflict and hints at the dark and erotic nature of the story)

Ensure the book specification is well-structured, creative, and clearly reflects the dark focus.

Critically important: Your ENTIRE response MUST be valid JSON. Adhere strictly to this format, ensuring correct data types and escaping. The JSON object should have the following structure: {"title": "string", "genre": "string", "setting": "string", "themes": ["string", "string", "string"], "tone": "string", "point_of_view": "string", "characters": ["string", "string", "string"], "premise": "string"}

Each character description in "characters" should be a SINGLE string. The LLM was generating a dictionary instead of a string.
Do not include any explanation or introductory text, just the valid JSON. Ensure that the JSON is properly formatted with correct escaping of special characters.
""",
    "book_spec_structure_check_prompt": """You are a meticulous editor reviewing a BookSpec object for correct structure and formatting.

Here is the BookSpec in JSON format:
```json
{book_spec_json}
```

Your task is to ensure that the JSON adheres to the following structure:

```json
{"title": "string", "genre": "string", "setting": "string", "themes": ["string", "string", "string"], "tone": "string", "point_of_view": "string", "characters": ["string", "string", "string"], "premise": "string"}
```

Specifically, check that:
- The JSON is valid and parsable.
- All fields are present.
- All string values are properly formatted.
- The "themes" and "characters" fields are lists of strings.

If the BookSpec adheres to the correct structure, respond with "STRUCTURE_OK".
If there are any structural issues, respond with a detailed explanation of the problems and how to fix them.
""",
    "book_spec_structure_fix_prompt": """You are a meticulous editor tasked with fixing structural issues in a BookSpec object.

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
{"title": "string", "genre": "string", "setting": "string", "themes": ["string", "string", "string"], "tone": "string", "point_of_view": "string", "characters": ["string", "string", "string"], "premise": "string"}
```

Return only valid JSON, without deviations or extra explanation. Adhere strictly to this format, ensuring correct data types and escaping.
""",
    "book_spec_critique_prompt": """You are a seasoned editor providing feedback on a book specification. Your goal is to identify areas where the specification can be strengthened to create a more compelling and well-defined foundation for the novel.

Here is the current book specification:
```json
{current_spec_json}
```

Provide a concise critique (2-3 sentences) that identifies specific areas for improvement. Focus on aspects such as clarity, detail, coherence, and the strength of the dark themes. The critique should be actionable and guide the revision process.
""",
    "book_spec_rewrite_prompt": """You are a skilled writer revising a book specification based on editor feedback. Your goal is to create a more compelling and well-defined foundation for the novel.

Here is the current book specification:
```json
{current_spec_json}
```

Here is the editor's critique:
```
{critique}
```

Revise the book specification based on the critique, focusing on the identified areas for improvement. Ensure that the revised specification is clear, detailed, coherent, and strongly emphasizes the dark themes of the novel.
""",
    "enhance_book_spec_prompt": """Enhance the following book specification to make it more compelling, detailed, and cohesive, while maintaining and strengthening its dark themes.

Current Book Specification:
```json
{current_spec_json}
```

Refine and expand upon each section, focusing on:
- Adding more specific details to the setting, themes, characters, and premise.
- Ensuring all elements are consistent and contribute to a strong, unified vision for a dark and erotic novel.
- Enriching character descriptions with deeper psychological insights and motivations related to the dark and erotic aspects of the story.
- Strengthening the premise to be even more intriguing and suggestive of the novel's nature.
- Improving the overall flow and readability of the book specification.

 Critically important: Your ENTIRE response MUST be valid JSON. Adhere strictly to this format, ensuring correct data types and escaping. The JSON object should have the following structure: {"title": "string", "genre": "string", "setting": "string", "themes": ["string", "string", "string"], "tone": "string", "point_of_view": "string", "characters": ["string", "string", "string"], "premise": "string"}

Each character description in "characters" should be a SINGLE string. The LLM was generating a dictionary instead of a string.
Do not include any explanation or introductory text, just the valid JSON. Ensure that the JSON is properly formatted with correct escaping of special characters.
""",
}
