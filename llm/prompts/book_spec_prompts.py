
# llm/prompts/book_spec_prompts.py
from llm.prompts.base_prompts import COMMON_PREAMBLE, TOML_FORMAT_INSTRUCTIONS_BOOKS_SPEC, CRITIQUE_REQUEST, REWRITE_REQUEST, ENHANCE_REQUEST

def create_book_spec_generation_prompt():
    """Creates the prompt for generating the initial book specification."""
    prompt = f"""{COMMON_PREAMBLE}

{TOML_FORMAT_INSTRUCTIONS_BOOKS_SPEC}

Generate a book specification in TOML format based on the following story idea:
```{{idea}}```
"""
    return prompt


def create_book_spec_critique_prompt():
    """Creates the prompt for critiquing a book specification."""
    prompt = f"""{COMMON_PREAMBLE}

{CRITIQUE_REQUEST}

Critique the following book specification (in TOML format):
```toml
{{current_spec_toml}}
```
"""
    return prompt


def create_book_spec_rewrite_prompt():
    """Creates the prompt for rewriting a book specification based on a critique."""
    prompt = f"""{COMMON_PREAMBLE}

{REWRITE_REQUEST}

Original Book Specification (TOML):
```toml
{{current_spec_toml}}
```

Critique:
```
{{critique}}
```

Enhanced Book Specification (ONLY TOML):
"""
    return prompt

def create_book_spec_enhancement_prompt():
    prompt = f"""{COMMON_PREAMBLE}
{ENHANCE_REQUEST}
Original Book Specification (TOML):
```toml
{{current_spec_toml}}
```

Critique:
```
{{critique}}
```

Enhanced Book Specification (ONLY TOML):
"""
    return prompt

def create_book_spec_validation_prompt():
    """
    Creates the prompt for validating a book specification in TOML format.
    """
    schema = """
title = "string"
genre = "string"
setting = "string"
themes = ["string"]
tone = "string"
point_of_view = "string"
characters = ["string", "string"] # characters is now list of strings
premise = "string"
"""
    prompt = f"""{COMMON_PREAMBLE}

{TOML_FORMAT_INSTRUCTIONS_BOOKS_SPEC}

**CRITICAL INSTRUCTION: TOML VALIDATION AND CORRECTION ONLY**

Your task is to validate the following TOML data as a book specification. You MUST ensure it strictly conforms to the schema below. If the TOML is valid, return it EXACTLY AS IS, without ANY modifications. If it is invalid, you MUST CORRECT IT to strictly adhere to the schema.

**SCHEMA:**
```toml
{schema}
```

**Input TOML:**
```toml
{{toml_input}}
```

**IMPORTANT:**

*   **Output ONLY VALID TOML.**
*   **Do NOT include ANY text, explanations, or markdown formatting in your response.**
*   **If the input TOML is already valid, return it UNCHANGED.**
*   **If correction is needed, output ONLY the corrected TOML.**
*   **ABSOLUTELY NO EXTRA TEXT BEFORE OR AFTER THE TOML OUTPUT.**

**Output (Corrected TOML - VALID TOML ONLY - ABSOLUTELY NOTHING ELSE):**
"""
    return prompt
