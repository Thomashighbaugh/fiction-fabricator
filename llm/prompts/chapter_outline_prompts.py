# llm/prompts/chapter_outline_prompts.py
from llm.prompts.base_prompts import COMMON_PREAMBLE, TOML_FORMAT_INSTRUCTIONS_CHAPTER_OUTLINE, TOML_FORMAT_INSTRUCTIONS_CHAPTER_OUTLINE_27, CRITIQUE_REQUEST, REWRITE_REQUEST, METHODOLOGY_MARKDOWN, ENHANCE_REQUEST

def create_chapter_outlines_generation_prompt():
    """
    Prompt for generating chapter outlines in TOML format.
    """
    prompt = f"""{COMMON_PREAMBLE}

{TOML_FORMAT_INSTRUCTIONS_CHAPTER_OUTLINE}

Generate chapter outlines in TOML format based on the following plot outline:
```toml
{{plot_outline_toml}}
```
Provide summaries for {{num_chapters}} chapters.
"""
    return prompt


def create_chapter_outlines_critique_prompt():
    """
    Prompt for critiquing chapter outlines.
    """
    prompt = f"""{COMMON_PREAMBLE}

{CRITIQUE_REQUEST}

Critique the following chapter outlines (in TOML format):
```toml
{{current_outlines_toml}}
```
"""
    return prompt


def create_chapter_outlines_rewrite_prompt():
    """
    Prompt for rewriting chapter outlines.
    """
    prompt = f"""{COMMON_PREAMBLE}

{REWRITE_REQUEST}

Original Chapter Outlines (TOML):
```toml
{{current_outlines_toml}}
```

Critique:
```
{{critique}}
```

Enhanced Chapter Outlines (ONLY TOML):
"""
    return prompt
def create_chapter_outlines_enhancement_prompt():
    prompt = f"""{COMMON_PREAMBLE}
{ENHANCE_REQUEST}
Original Chapter Outlines (TOML):
```toml
{{current_outlines_toml}}
```

Critique:
```
{{critique}}
```

Enhanced Chapter Outlines (ONLY TOML):
"""
    return prompt

def create_chapter_outline_27_method_generation_prompt():
    """Prompt for generating 27 chapter outlines using the 27-chapter method."""
    prompt = f"""{COMMON_PREAMBLE}

{TOML_FORMAT_INSTRUCTIONS_CHAPTER_OUTLINE_27}

Generate 27 chapter outlines in TOML format based on the following book specification and the 27-chapter methodology described below:

Book Specification (TOML):
```toml
{{book_spec_toml}}
```

27 Chapter Methodology:
```md
{METHODOLOGY_MARKDOWN}
```
"""
    return prompt


def create_chapter_outline_27_method_critique_prompt():
    """Critique prompt for 27 chapter outlines."""
    prompt = f"""{COMMON_PREAMBLE}

{CRITIQUE_REQUEST}

Critique the following 27 chapter outlines (in TOML format):
```toml
{{current_outlines_toml}}
```
"""
    return prompt


def create_chapter_outline_27_method_rewrite_prompt():
    """Rewrite prompt for 27 chapter outlines."""
    prompt = f"""{COMMON_PREAMBLE}

{REWRITE_REQUEST}

Original 27 Chapter Outlines (TOML):
```toml
{{current_outlines_toml}}
```

Critique:
```
{{critique}}
```

Enhanced 27 Chapter Outlines (ONLY TOML):
"""
    return prompt

def create_chapter_outline_27_method_enhancement_prompt():
    prompt = f"""{COMMON_PREAMBLE}
{ENHANCE_REQUEST}
Original 27 Chapter Outlines (TOML):
```toml
{{current_outlines_toml}}
```

Critique:
```
{{critique}}
```

Enhanced 27 Chapter Outlines (ONLY TOML):
"""
    return prompt
