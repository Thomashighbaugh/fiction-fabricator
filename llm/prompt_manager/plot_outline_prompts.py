# llm/prompt_manager/plot_outline_prompts.py
plot_outline_prompts = {
    "plot_outline_generation_prompt": r"""
You are a world-class story writer who can craft compelling and detailed 3-act plot outlines from book specifications.
Create a detailed and compelling three-act plot outline for a novel based on the following book specification.  Ensure a balanced story arc with substantial plot points in each act.

Book Specification:
```json
{book_spec_json}
```

**IMPORTANT:** The plot outline you create MUST be directly based on and consistent with the Book Specification provided above.
Specifically, ensure the plot outline strongly reflects the:
- Genre and Themes
- Setting
- Premise and Characters defined in the Book Specification.

The plot outline MUST be structured in three acts, with roughly 3-5 major plot points described in each act:
- **Act One: Setup** - Introduce the characters, setting, and premise from the Book Spec in a captivating way. Establish the initial conflict and the protagonist's primary goals and motivations, all consistent with the Book Spec. Detail at least 3-5 significant plot points that drive the story forward and establish the world as described in the Book Spec. This act should build intrigue and set the stage for the rising action, firmly within the boundaries of the Book Spec.

- **Act Two: Confrontation** - Develop the central conflict with rising stakes. The protagonist faces significant obstacles and challenges, leading to a major turning point. Explore the dark and erotic themes through specific plot events and character interactions. Detail at least 3-5 major plot points showcasing the escalating conflict, including a midpoint twist or revelation that changes the protagonist's course.

- **Act Three: Resolution** - The climax of the story, where the central conflict reaches its peak. The main conflict is resolved, and the protagonist experiences a significant transformation or realization. Address the consequences of the dark and erotic elements explored throughout the novel, leading to thematic closure. Detail at least 3-5 major plot points that lead to the resolution, including the climax itself and the immediate aftermath/denouement. Each point should show clear consequences of previous actions.

The plot outline should be detailed enough to provide a clear and robust roadmap for writing the novel, with specific and impactful plot points driving significant character developments in each act.  Each act should feel substantial and necessary to the overall narrative. Ensure the outline effectively incorporates and develops the themes from the book specification, avoiding superficial plot points.
""",
    "plot_outline_structure_check_prompt": r"""
You are a meticulous editor reviewing a PlotOutline object for correct structure and completeness.

Here is the PlotOutline:
```
{plot_outline}
```

Your task is to ensure that the plot outline is structured in three acts, with roughly 3-5 major plot points described in each act:

- Act One: Setup
- Act Two: Confrontation
- Act Three: Resolution

Check that each act is present and contains a reasonable number of plot points. If the structure is valid, respond with "STRUCTURE_OK".
If there are any structural issues or missing acts, respond with a detailed explanation of the problems.
""",
    "plot_outline_structure_fix_prompt": r"""
You are a meticulous editor tasked with fixing structural issues in a PlotOutline object.

Here is the flawed PlotOutline:
```
{plot_outline}
```

Here is a detailed list of structural problems and how to fix them:
```
{structure_problems}
```

Your task is to modify the plot outline to ensure that it is structured in three acts, with roughly 3-5 major plot points described in each act:

- Act One: Setup
- Act Two: Confrontation
- Act Three: Resolution

Return a corrected version of the plot outline, without deviations or extra explanation.
""",
    "plot_outline_critique_prompt": r"""
You are a story consultant providing feedback on a plot outline. Your goal is to identify areas where the outline can be strengthened to create a more compelling and structurally sound narrative.

Here is the current plot outline:
```
{current_outline}
```

Provide a concise critique (2-3 sentences) that identifies specific areas for improvement. Focus on aspects such as plot structure, pacing, character arcs, thematic development, and the integration of dark elements. The critique should be actionable and guide the revision process.
""",
    "plot_outline_rewrite_prompt": r"""
You are a screenwriter revising a plot outline based on consultant feedback. Your goal is to create a more compelling and structurally sound narrative.

Here is the current plot outline:
```
{current_outline}
```

Here is the story consultant's critique:
```
{critique}
```

Revise the plot outline based on the critique, focusing on the identified areas for improvement. Ensure that the revised outline has a strong plot structure, good pacing, well-defined character arcs, effective thematic development, and a compelling integration of dark elements.
""",
    "enhance_plot_outline_prompt": r"""
Enhance the following three-act plot outline to make it more detailed, compelling, and structurally sound, while ensuring it effectively develops the themes of the novel.

Current Plot Outline:
```
{current_outline}
```

Refine and expand upon each act, focusing on:
- Adding more specific plot points and events within each act.
- Strengthening the cause-and-effect relationships between plot points.
- Ensuring a clear progression of conflict and rising stakes throughout the three acts.
- Deepening the integration of the themes into the plot events and character actions.
- Checking for pacing and narrative flow, ensuring a compelling and engaging structure.
- Ensuring the resolution in Act Three is satisfying and thematically resonant with the elements explored in the novel.
""",
}
