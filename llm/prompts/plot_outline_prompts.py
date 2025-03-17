# llm/prompts/plot_outline_prompts.py
from llm.prompts.base_prompts import COMMON_PREAMBLE, TOML_FORMAT_INSTRUCTIONS_PLOT_OUTLINE, CRITIQUE_REQUEST, REWRITE_REQUEST, ENHANCE_REQUEST

def create_plot_outline_generation_prompt():
    """
    Prompt for generating a plot outline in TOML.
    """
    prompt = f"""{COMMON_PREAMBLE}

{TOML_FORMAT_INSTRUCTIONS_PLOT_OUTLINE}

Generate a three-act plot outline in TOML format, based on the following book specification:
```toml
{{book_spec_toml}}
```
"""
    return prompt


def create_plot_outline_critique_prompt():
    """
    Prompt for critiquing a plot outline.
    """
    prompt = f"""{COMMON_PREAMBLE}

{CRITIQUE_REQUEST}

Critique the following plot outline (in TOML format):
```toml
{{current_outline_toml}}
```
"""
    return prompt


def create_plot_outline_rewrite_prompt():
    """
    Prompt for rewriting a plot outline.
    """
    prompt = f"""{COMMON_PREAMBLE}

{REWRITE_REQUEST}

Original Plot Outline (TOML):
```toml
{{current_outline_toml}}
```

Critique:
```
{{critique}}
```

Enhanced Plot Outline (ONLY TOML):
"""
    return prompt

def create_plot_outline_enhancement_prompt():
    prompt = f"""{COMMON_PREAMBLE}
{ENHANCE_REQUEST}
Original Plot Outline (TOML):
```toml
{{current_outline_toml}}
```

Critique:
```
{{critique}}
```

Enhanced Plot Outline (ONLY TOML):
"""
    return prompt
