
# llm/prompts/scene_outline_prompts.py
from llm.prompts.base_prompts import COMMON_PREAMBLE, CRITIQUE_REQUEST, REWRITE_REQUEST, ENHANCE_REQUEST

def create_scene_outlines_generation_prompt():
    """
    Creates the prompt for generating scene outlines for a chapter.
    """
    prompt = f"""{COMMON_PREAMBLE}

Generate scene outlines for a chapter with the following summary:
```
{{chapter_outline}}
```
Generate approximately {{num_scenes_per_chapter}} scene outlines.
Each scene should include a scene number and a brief summary.
Output (Plain Text):
"""
    return prompt


def create_scene_outlines_critique_prompt():
    """Creates the prompt for critiquing scene outlines."""
    prompt = f"""{COMMON_PREAMBLE}

{CRITIQUE_REQUEST}

Provide a critique of the following scene outlines:
```
{{current_outlines}}
```
"""
    return prompt


def create_scene_outlines_rewrite_prompt():
    """Creates the prompt for rewriting scene outlines based on a critique."""
    prompt = f"""{COMMON_PREAMBLE}

{REWRITE_REQUEST}

Original Scene Outlines:
```
{{current_outlines}}
```

Critique:
```
{{critique}}
```

Enhanced Scene Outlines:
"""
    return prompt

def create_scene_outlines_enhancement_prompt():
    prompt = f"""{COMMON_PREAMBLE}
    {ENHANCE_REQUEST}
Original Scene Outlines:
```
{{current_outlines}}
```

Critique:
```
{{critique}}
```

Enhanced Scene Outlines:
"""
    return prompt


def create_scene_part_generation_prompt():
    """Creates prompt for generating a scene part."""
    prompt = f"""{COMMON_PREAMBLE}

Generate part {{part_number}} of a scene with the following outline:
Scene Outline:
```
{{scene_outline}}
```

Book Specification (TOML):
```toml
{{book_spec_toml}}
```

Chapter Outline:
```
{{chapter_outline}}
```

Full Scene Outline:
```
{{scene_outline_full}}
```

Output (Scene Part):
"""
    return prompt


def create_scene_part_critique_prompt():
    """Creates prompt for critiquing a scene part."""
    prompt = f"""{COMMON_PREAMBLE}

{CRITIQUE_REQUEST}

Critique the following scene part, considering the book specification, chapter outline, and full scene outline:

Book Specification (TOML):
```toml
{{book_spec_toml}}
```

Chapter Outline:
```
{{chapter_outline}}
```

Full Scene Outline:
```
{{scene_outline_full}}
```

Part Number:
```
{{part_number}}
```

Scene Part Content:
```
{{content}}
```
"""
    return prompt


def create_scene_part_rewrite_prompt():
    """Creates prompt for rewriting a scene part based on a critique."""
    prompt = f"""{COMMON_PREAMBLE}

{REWRITE_REQUEST}

Book Specification (TOML):
```toml
{{book_spec_toml}}
```

Chapter Outline:
```
{{chapter_outline}}
```

Full Scene Outline:
```
{{scene_outline_full}}
```

Part Number: {{part_number}}

Critique:
```
{{critique}}
```

Original Content:
```
{{content}}
```

Enhanced Scene Part:
"""
    return prompt


def create_scene_part_structure_check_prompt():
    """Checks if the generated scene part has a basic, coherent structure."""
    prompt = f"""{COMMON_PREAMBLE}

Check if the following scene part has a basic, coherent structure (e.g., clear sentences, logical flow):
```
{{scene_part}}
```
If the structure is OK, output ONLY 'STRUCTURE_OK'.
If there are structural problems, output a concise description of the issues.
Output:
"""
    return prompt


def create_scene_part_structure_fix_prompt():
    """Attempts to fix structural issues in a scene part."""
    prompt = f"""{COMMON_PREAMBLE}

The following scene part has structural problems.  Rewrite it to improve clarity, flow, and coherence:

Original Scene Part:
```
{{scene_part}}
```

Identified Structural Problems:
```
{{structure_problems}}
```

Fixed Scene Part:
"""
    return prompt

def create_scene_part_enhancement_prompt():
    prompt = f"""{COMMON_PREAMBLE}

{ENHANCE_REQUEST}

Book Specification (TOML):
```toml
{{book_spec_toml}}
```

Chapter Outline:
```
{{chapter_outline}}
```

Full Scene Outline:
```
{{scene_outline_full}}
```

Part Number: {{part_number}}

Critique:
```
{{critique}}
```

Original Content:
```
{{content}}
```
Enhanced Scene Part:"""
    return prompt