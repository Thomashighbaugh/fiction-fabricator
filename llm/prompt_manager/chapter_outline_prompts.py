# llm/prompt_manager/chapter_outline_prompts.py
chapter_outline_prompts = {
    "chapter_outlines_generation_prompt": r"""
You are a world-class story writer who can create comprehensive chapter outlines based on a 3-act plot outline.
Based on the following three-act plot outline, generate exactly {num_chapters} detailed chapter outlines. I need precisely {num_chapters} chapters, no fewer, no more. Divide the plot events roughly equally across these {num_chapters} chapters, ensuring a logical flow and pacing.

Plot Outline:
```
{plot_outline}
```

For each chapter, provide a concise outline (2-3 paragraphs) summarizing the key events and developments that occur within that chapter. The chapter outlines should:
- Clearly advance the overall plot as described in the three-act outline.
- Maintain the established tone and themes, especially the dark and erotic elements.
- Create anticipation for subsequent chapters and maintain reader engagement.
- Be numbered sequentially (Chapter 1, Chapter 2, etc.).
- **Crucially, for Chapter 1, provide an exposition-focused summary that introduces the main characters, setting, and central conflict as if the reader knows nothing about them. Avoid referring to characters as if they are already known. This chapter should set the stage for the rest of the novel.**

Ensure the chapter outlines collectively cover the entire plot outline and provide a solid structure for writing the full novel.
""",
    "chapter_outlines_structure_check_prompt": r"""
You are a meticulous editor reviewing chapter outlines for overall structure and completeness.

Here are the chapter outlines:
```
{chapter_outlines}
```

Your task is to ensure that each chapter outline:
- Is numbered sequentially (Chapter 1, Chapter 2, etc.).
- Provides a concise summary of the key events and developments that occur within that chapter.
- Clearly advances the overall plot.

If the chapter outlines adhere to the correct structure, respond with "STRUCTURE_OK".
If there are any structural issues, respond with a detailed explanation of the problems.
""",
    "chapter_outlines_structure_fix_prompt": r"""
You are a meticulous editor tasked with fixing structural issues in a set of chapter outlines.

Here are the flawed chapter outlines:
```
{chapter_outlines}
```

Here is a detailed list of structural problems and how to fix them:
```
{structure_problems}
```

Your task is to modify the chapter outlines to ensure that each chapter outline:
- Is numbered sequentially (Chapter 1, Chapter 2, etc.).
- Provides a concise summary of the key events and developments that occur within that chapter.
- Clearly advances the overall plot.

Return a corrected version of the chapter outlines, without deviations or extra explanation.
""",
    "chapter_outlines_critique_prompt": r"""
You are a novel editor providing feedback on a set of chapter outlines. Your goal is to identify areas where the outlines can be strengthened to create a more compelling and well-structured novel.

Here are the current chapter outlines:
```
{current_outlines}
```

Provide a concise critique (2-3 sentences) that identifies specific areas for improvement. Focus on aspects such as chapter-to-chapter flow, pacing, plot progression, character development, thematic consistency, and the integration of dark elements. The critique should be actionable and guide the revision process.
""",
    "chapter_outlines_rewrite_prompt": r"""
You are a novelist revising a set of chapter outlines based on editor feedback. Your goal is to create a more compelling and well-structured novel.

Here are the current chapter outlines:
```
{current_outlines}
```

Here is the editor's critique:
```
{critique}
```

Revise the chapter outlines based on the critique, focusing on the identified areas for improvement. Ensure that the revised outlines have a strong chapter-to-chapter flow, good pacing, clear plot progression, effective character development, thematic consistency, and a compelling integration of dark elements.
""",
    "enhance_chapter_outlines_prompt": r"""
Enhance the following chapter outlines to make them more detailed, logically connected, and compelling. Ensure each chapter outline effectively contributes to the overall plot progression and thematic development, especially the dark and erotic elements of the novel.

Current Chapter Outlines:
```
{current_outlines}
```

Refine and expand upon each chapter outline, focusing on:
- Adding more specific details about events, character actions, and setting within each chapter.
- Strengthening the transitions and connections between chapters to ensure a smooth narrative flow.
- Ensuring each chapter outline clearly contributes to the overall three-act plot structure.
- Deepening the integration of dark and erotic themes within the chapter events.
- Checking for consistency and pacing across all chapter outlines.
- Making sure each chapter outline creates sufficient intrigue and motivation to read the full chapter.

Output should be a set of enhanced chapter outlines in text format, clearly numbered and formatted as individual chapter outlines.
""",
}
