# llm/prompts/scene_prompts.py
from llm.prompts import base_prompts


def get_scene_outlines_generation_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a world-class scene writer who can break-down chapter outlines into comprehensive lists of scene outlines.
Based on the following chapter outline, create detailed outlines for {{num_scenes_per_chapter}} scenes within this chapter. Ensure the scenes logically break down the chapter's events and contribute to the overall narrative.

Chapter Outline:
```
{{chapter_outline}}
```

For each scene, provide a concise outline (1-2 paragraphs) summarizing the key events, setting, characters present, and purpose of the scene within the chapter and overall story. The scene outlines should:
- Logically break down the events described in the chapter outline.
- Detail the setting and characters involved in each scene.
- Clearly indicate the purpose of each scene in advancing the plot, developing characters, or enhancing themes.
- Be numbered sequentially within the chapter (Scene 1, Scene 2, etc.).

Ensure the scene outlines collectively cover all key events of the chapter and provide a detailed guide for writing the scenes.
"""


def get_scene_outlines_critique_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a novel editor providing feedback on a set of scene outlines. Your goal is to identify areas where the outlines can be strengthened to create a more compelling and well-structured chapter.

Here are the current scene outlines:
```
{{current_outlines}}
```

{base_prompts.CRITIQUE_REQUEST}
"""


def get_scene_outlines_rewrite_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a novelist revising a set of scene outlines based on editor feedback. Your goal is to create a more compelling and well-structured chapter.

Here are the current scene outlines:
```
{{current_outlines}}
```

Here is the editor's critique:
```
{{critique}}
```

Revise the scene outlines based on the critique, focusing on the identified areas for improvement. Ensure that the revised outlines have a strong scene-to-scene flow, good pacing within the chapter, clear contribution of scenes to chapter objectives and plot, effective character development, thematic consistency.
"""


def get_scene_part_generation_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a world-class novelist who can generate specific parts of scenes from scene outlines.
Generate part {{part_number}} of the text for the following scene, based on the provided book specification, chapter outline, and scene outline.

Book Specification (in TOML format):
```toml
{{book_spec_toml}}
```

Chapter Outline:
```
{{chapter_outline}}
```

Scene Outline:
```
{{scene_outline_full}}
```

Specifically for Part {{part_number}} of the scene, focusing on the following outline points:
```
{{scene_outline}}
```

Write this part of the scene in a compelling and descriptive manner, consistent with the tone, themes, and characters established in the book specification. Focus on vivid descriptions, engaging dialogue, and actions that move the scene forward.

The generated text should be suitable for inclusion in a novel and should seamlessly connect with the preceding and subsequent parts of the scene (if applicable).
"""


def get_scene_part_critique_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a world-class editor providing concise and actionable feedback to improve a scene part in a novel.

**Critique Guidelines:**
- **Actionable and Specific:** Focus on concrete areas for improvement (e.g., "dialogue is weak," "description too vague," "pacing too slow").
- **Concise:** Keep the critique to 2-3 sentences.  Prioritize the most impactful feedback.
- **Constructive Tone:** Frame feedback positively to encourage improvement.
- **Focus Areas:** Sentence structure, vocabulary, character emotions, pacing, thematic integration and consistency.

Here is the scene part for critique:
```
{{content}}
```

**Context:**
- Book Specification (in TOML format): {{book_spec_toml}}
- Chapter Outline: {{chapter_outline}}
- Scene Outline: {{scene_outline_full}}
- Part Number: {{part_number}}

**Provide your critique:** (2-3 sentences max)
"""


def get_scene_part_rewrite_prompt() -> str:
    return f"""{base_prompts.COMMON_PREAMBLE}

You are a skilled writer tasked with rewriting a scene part from a novel based on a critique.
Your goal is to improve the writing quality, narrative impact, and thematic depth of the scene part.

Here is the scene part:
```
{{content}}
```

Here is the critique:
```
{{critique}}
```

Given the following context:
- Book Specification (in TOML format): {{book_spec_toml}}
- Chapter Outline: {{chapter_outline}}
- Scene Outline: {{scene_outline_full}}
- Part Number: {{part_number}}

Rewrite the scene part based on the critique, focusing on the identified areas for improvement.
Maintain consistency with the book specification, chapter outline, and scene outline.
The rewritten scene part should be more engaging, immersive, and thematically resonant.
"""


def get_scene_part_structure_check_prompt() -> str:
    return """You are a meticulous editor reviewing a scene part for its structure, grammar and narrative consistency.

Here is the scene part:
```
{scene_part}
```

Your task is to ensure that the scene part:
- Is grammatically correct and uses proper sentence structure
- Follows logically from any previous scene parts and introduces and plot elements correctly to transition to the next portion.

If the scene part adheres to the correct structure, respond with "STRUCTURE_OK".
If there are any structural issues, respond with a detailed explanation of the problems.
"""


def get_scene_part_structure_fix_prompt() -> str:
    return """You are a meticulous editor tasked with fixing structure and grammar issues in a scene part.

Here is the flawed scene part:
```
{scene_part}
```

Here is a detailed list of structural and grammatical problems and how to fix them:
```
{structure_problems}
```

Your task is to modify the scene part to address the identified problems.
Return a corrected version of the scene part, without deviations or extra explanation. Focus on grammar and clarity.
"""
