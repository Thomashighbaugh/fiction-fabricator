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
    prompt = f"""{COMMON_PREAMBLE}

Validate the following TOML data as a book specification, and rewrite to fit this schema:

title = "string"
genre = "string"
setting = "string"
themes = ["string"]
tone = "string"
point_of_view = "string"
characters = ["string", "string"] # characters is now list of strings
premise = "string"

Input TOML:
```toml
{{toml_input}}
```
Output (Corrected TOML - ONLY THIS):
"""
    return prompt