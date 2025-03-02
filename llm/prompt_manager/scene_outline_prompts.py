# llm/prompt_manager/scene_outline_prompts.py
scene_outline_prompts = {
    "scene_outlines_generation_prompt": r"""
You are a world-class scene writer who can break-down chapter outlines into comprehensive lists of scene outlines.
Based on the following chapter outline, create detailed outlines for {num_scenes_per_chapter} scenes within this chapter. Ensure the scenes logically break down the chapter's events and contribute to the overall narrative.

Chapter Outline:
```
{chapter_outline}
```

For each scene, provide a concise outline (1-2 paragraphs) summarizing the key events, setting, characters present, and purpose of the scene within the chapter and overall story. The scene outlines should:
- Logically break down the events described in the chapter outline.
- Detail the setting and characters involved in each scene.
- Clearly indicate the purpose of each scene in advancing the plot, developing characters, or enhancing themes (especially dark and erotic themes).
- Be numbered sequentially within the chapter (Scene 1, Scene 2, etc.).

Ensure the scene outlines collectively cover all key events of the chapter and provide a detailed guide for writing the scenes.
""",
    "scene_outlines_structure_check_prompt": r"""
You are a meticulous editor reviewing scene outlines for overall structure and completeness.

Here are the scene outlines:
```
{scene_outlines}
```

Your task is to ensure that each scene outline:
- Is numbered sequentially within the chapter (Scene 1, Scene 2, etc.).
- Summarizes the key events, setting, and characters present in the scene.
- Clearly indicates the purpose of the scene in advancing the plot.

If the scene outlines adhere to the correct structure, respond with "STRUCTURE_OK".
If there are any structural issues, respond with a detailed explanation of the problems.
""",
    "scene_outlines_structure_fix_prompt": r"""
You are a meticulous editor tasked with fixing structural issues in a set of scene outlines.

Here are the flawed scene outlines:
```
{scene_outlines}
```

Here is a detailed list of structural problems and how to fix them:
```
{structure_problems}
```

Your task is to modify the scene outlines to ensure that each scene outline:
- Is numbered sequentially within the chapter (Scene 1, Scene 2, etc.).
- Summarizes the key events, setting, and characters present in the scene.
- Clearly indicates the purpose of the scene in advancing the plot.

Return a corrected version of the scene outlines, without deviations or extra explanation.
""",
    "scene_outlines_critique_prompt": r"""
You are a novel editor providing feedback on a set of scene outlines. Your goal is to identify areas where the outlines can be strengthened to create a more compelling and well-structured chapter.

Here are the current scene outlines:
```
{current_outlines}
```

Provide a concise critique (2-3 sentences) that identifies specific areas for improvement. Focus on aspects such as scene-to-scene flow, pacing within the chapter, contribution of scenes to chapter objectives and plot, character consistency, and integration of dark elements. The critique should be actionable and guide the revision process.
""",
    "scene_outlines_rewrite_prompt": r"""
You are a novelist revising a set of scene outlines based on editor feedback. Your goal is to create a more compelling and well-structured chapter.

Here are the current scene outlines:
```
{current_outlines}
```

Here is the editor's critique:
```
{critique}
```

Revise the scene outlines based on the critique, focusing on the identified areas for improvement. Ensure that the revised outlines have a strong scene-to-scene flow, good pacing within the chapter, clear contribution of scenes to chapter objectives and plot, effective character development, thematic consistency, and a compelling integration of dark elements.
""",
    "enhance_scene_outlines_prompt": r"""
Enhance the following scene outlines for a chapter to make them more detailed, logically sequenced, and compelling. Ensure each scene outline effectively contributes to the chapter's narrative and the overall dark and erotic themes of the novel.

Current Scene Outlines:
```
{current_outlines}
```

Refine and expand upon each scene outline, focusing on:
- Adding more specific details about actions, dialogue, setting descriptions, and character emotions within each scene.
- Strengthening the transitions and connections between scenes to ensure a smooth flow within the chapter.
- Ensuring each scene outline clearly contributes to the chapter's objectives and the overall plot.
- Deepening the integration of dark and erotic themes within the scene events and character interactions.
- Checking for pacing and dramatic tension within and across the scene outlines.
- Ensuring each scene outline provides a strong foundation for writing the full scene.

Output should be a set of enhanced scene outlines in text format, clearly numbered and formatted as individual scene outlines.
""",
}


