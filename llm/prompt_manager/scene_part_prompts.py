# llm/prompt_manager/scene_part_prompts.py
scene_part_prompts = {
    "scene_part_generation_prompt": r"""
You are a world-class novelist who can generate specific parts of scenes from scene outlines.
Generate part {part_number} of the text for the following scene, based on the provided book specification, chapter outline, and scene outline.

Book Specification:
```json
{book_spec_text}
```

Chapter Outline:
```
{chapter_outline}
```

Scene Outline:
```
{scene_outline_full}
```

Specifically for Part {part_number} of the scene, focusing on the following outline points:
```
{scene_outline}
```

Write this part of the scene in a compelling and descriptive manner, consistent with the tone, themes, and characters established in the book specification. Emphasize the dark and erotic elements as appropriate for this scene and the overall novel. Focus on vivid descriptions, engaging dialogue, and actions that move the scene forward.

The generated text should be suitable for inclusion in a novel and should seamlessly connect with the preceding and subsequent parts of the scene (if applicable).
""",
    "scene_part_structure_check_prompt": r"""
You are a meticulous editor reviewing a scene part for its structure, grammar and narrative consistency.

Here is the scene part:
```
{scene_part}
```

Your task is to ensure that the scene part:
- Is grammatically correct and uses proper sentence structure
- Follows logically from any previous scene parts and introduces and plot elements correctly to transition to the next portion.

If the scene part adheres to the correct structure, respond with "STRUCTURE_OK".
If there are any structural issues, respond with a detailed explanation of the problems.
""",
    "scene_part_structure_fix_prompt": r"""
You are a meticulous editor tasked with fixing structure and grammar issues in a scene part.

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
""",
    "scene_part_critique_prompt": r"""You are a world-class editor providing concise and actionable feedback to improve a scene part in a novel.

**Critique Guidelines:**
- **Actionable and Specific:** Focus on concrete areas for improvement (e.g., "dialogue is weak," "description too vague," "pacing too slow").
- **Concise:** Keep the critique to 2-3 sentences.  Prioritize the most impactful feedback.
- **Constructive Tone:** Frame feedback positively to encourage improvement.
- **Focus Areas:** Sentence structure, vocabulary, character emotions, pacing, thematic integration and consistency.

Here is the scene part for critique:
```
{content}
```

**Context:**
- Book Specification: {book_spec}
- Chapter Outline: {chapter_outline}
- Scene Outline: {scene_outline_full}
- Part Number: {part_number}

**Provide your critique:** (2-3 sentences max)
""",
    "scene_part_rewrite_prompt": r"""
You are a skilled writer tasked with rewriting a scene part from a novel based on a critique.
Your goal is to improve the writing quality, narrative impact, and thematic depth of the scene part.

Here is the scene part:
```
{content}
```

Here is the critique:
```
{critique}
```

Given the following context:
- Book Specification: {book_spec}
- Chapter Outline: {chapter_outline}
- Scene Outline: {scene_outline_full}
- Part Number: {part_number}

Rewrite the scene part based on the critique, focusing on the identified areas for improvement.
Maintain consistency with the book specification, chapter outline, and scene outline.
The rewritten scene part should be more engaging, immersive, and thematically resonant.
""",
    "enhance_scene_part_prompt": r"""
Enhance the following part {part_number} of a scene to improve its writing quality, narrative impact, and thematic depth, while maintaining consistency with the book specification, chapter outline, and scene outline.

Book Specification:
```json
{book_spec_text}
```

Chapter Outline:
```
{chapter_outline}
```

Scene Outline:
```
{scene_outline_full}
```

Current Scene Part {part_number} Text:
```
{scene_part}
```

Refine and enhance this scene part, focusing on:
- Improving sentence structure, vocabulary, and descriptive language.
- Deepening character emotions and motivations within the scene.
- Strengthening the pacing and dramatic tension of the scene part.
- Enhancing the integration of dark and erotic themes within the text.
- Ensuring the scene part effectively fulfills its purpose within the scene and chapter.
- Checking for consistency with the overall tone and style of the novel.
- Making the scene part more engaging and immersive for the reader.

Output should be the enhanced text for scene part {part_number}.
""",
}
