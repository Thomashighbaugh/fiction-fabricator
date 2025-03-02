# llm/prompt_manager/plot_outline_prompts.py

"""
Prompt templates for PlotOutline generation and enhancement.

This module defines the prompt templates used by the PlotOutlineGenerator
to generate and enhance PlotOutline objects. It utilizes base templates
from base_prompts.py for consistency and reduced redundancy.
"""

from llm.prompt_manager.base_prompts import (
    COMMON_INSTRUCTIONS_NOVELIST,
    STRUCTURE_CHECK_INSTRUCTIONS,
    STRUCTURE_FIX_PROMPT_TEMPLATE,
    CRITIQUE_PROMPT_TEMPLATE,
    REWRITE_PROMPT_TEMPLATE,
)


class PlotOutlinePrompts:
    """
    Encapsulates prompt templates for PlotOutline operations.

    Provides methods to retrieve specific prompt templates for
    generating, structure checking, fixing, critiquing, and rewriting PlotOutlines.
    """

    def __init__(self, prompt_manager=None):
        """
        Initializes PlotOutlinePrompts.
        Prompt manager is currently not used, but included for potential future use or consistency.
        """
        self.prompt_manager = prompt_manager  # Currently not used

    def create_plot_outline_generation_prompt(self) -> str:
        """
        Returns the prompt template for generating a PlotOutline from a BookSpec.
        """
        prompt_template = f"""
        {COMMON_INSTRUCTIONS_NOVELIST.format(task="create compelling and detailed 3-act plot outlines from book specifications")}

        Create a detailed and compelling three-act plot outline for a novel based on the following book specification. Ensure a balanced story arc with substantial plot points in each act.

        Book Specification:
        ```json
        {{book_spec_json}}
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

        The plot outline should be detailed enough to provide a clear and robust roadmap for writing the novel, with specific and impactful plot points driving significant character developments in each act. Each act should feel substantial and necessary to the overall narrative. Ensure the outline effectively incorporates and develops the themes from the book specification, avoiding superficial plot points.

        Your response MUST be ONLY the plot outline, structured into Act One, Act Two, and Act Three, with clear headings for each act and bullet points or numbered lists for plot points within each act.  Do not include any preamble or concluding remarks, only the plot outline itself.
        """
        return prompt_template

    def create_plot_outline_structure_check_prompt(self) -> str:
        """
        Returns the prompt template for checking the structure of a PlotOutline.
        """
        prompt_template = f"""
        {STRUCTURE_CHECK_INSTRUCTIONS}

        Here is the PlotOutline:
        ```
        {{content}}
        ```

        Your task is to ensure that the plot outline is structured in three acts, with clear headings for each act:

        - Act One: Setup
        - Act Two: Confrontation
        - Act Three: Resolution

        Each act should contain a reasonable number of plot points (ideally 3-5). Check if all three acts are present and clearly delineated.

        If the PlotOutline adheres to the correct 3-act structure with clear act headings, respond with 'STRUCTURE_OK'.
        If there are any structural issues, such as missing acts, unclear headings, or if it's not clearly divided into three acts, provide a detailed explanation of the problems and how to fix them.
        """
        return prompt_template

    def create_plot_outline_structure_fix_prompt(self) -> str:
        """
        Returns the prompt template for fixing structural issues in a PlotOutline.
        """
        prompt_template = f"""
        {STRUCTURE_FIX_PROMPT_TEMPLATE.format(content_with_structure_problems="{{content_with_structure_problems}}", structure_problems="{{structure_problems}}")}

        Your task is to modify the plot outline to ensure that it is correctly structured in three acts, with clear headings for each act:

        - Act One: Setup
        - Act Two: Confrontation
        - Act Three: Resolution

        Each act should contain a reasonable number of plot points (ideally 3-5). Ensure all three acts are present and clearly delineated with proper headings.

        Return ONLY the corrected plot outline, without any preamble or concluding remarks. The corrected plot outline should strictly adhere to the 3-act structure.
        """
        return prompt_template

    def create_plot_outline_critique_prompt(self) -> str:
        """
        Returns the prompt template for generating a critique of a PlotOutline.
        """
        prompt_template = f"""
        {CRITIQUE_PROMPT_TEMPLATE.format(content="{{content}}")}

        Focus your critique on:
        - **Plot Structure and Pacing:** Is the 3-act structure clearly defined and effectively used? Is the pacing appropriate across the acts? Does each act have a clear beginning, middle, and end in terms of plot progression?
        - **Clarity and Detail of Plot Points:** Are the plot points within each act clearly described and sufficiently detailed? Is it easy to understand the sequence of events and their impact on the story?
        - **Rising Action and Conflict:** Is there a clear sense of rising action in Act Two? Is the central conflict effectively developed and escalated? Are the stakes high enough?
        - **Resolution and Thematic Closure:** Does Act Three provide a satisfying resolution to the central conflict? Is there a sense of thematic closure? Are the consequences of earlier events adequately addressed?
        - **Consistency with Book Specification:** Does the plot outline consistently and effectively implement the elements defined in the Book Specification (genre, themes, setting, characters, premise)?
        - **Overall Compellingness:** How compelling and engaging is the plot outline? Does it create anticipation for the full story? What are its strengths and weaknesses in terms of making the reader want to know more?
        """
        return prompt_template

    def create_plot_outline_rewrite_prompt(self) -> str:
        """
        Returns the prompt template for rewriting a PlotOutline based on critique.
        """
        prompt_template = f"""
        {REWRITE_PROMPT_TEMPLATE.format(content="{{content}}", critique="{{critique}}")}

        When rewriting the plot outline, specifically focus on:
        - **Addressing all points raised in the critique** directly and thoroughly. Ensure that each issue identified by the editor is resolved in the revised plot outline.
        - **Strengthening the 3-act structure** to ensure a clear and effective narrative arc. Enhance the pacing within and between acts to build tension and maintain reader engagement.
        - **Adding detail and clarity to plot points**, making sure each point is well-defined and contributes to the overall plot progression. Expand on plot points that were identified as too vague or underdeveloped.
        - **Escalating the conflict in Act Two** to raise the stakes and increase dramatic tension. Ensure that the confrontation is significant and leads to a clear turning point.
        - **Ensuring a satisfying resolution in Act Three** that provides thematic closure and addresses all major plot threads. Make sure the resolution feels earned and consistent with the preceding acts.
        - **Improving consistency with the Book Specification**, double-checking that all elements of the plot outline align with and develop the genre, themes, setting, characters, and premise established in the Book Specification.

        Rewrite the ENTIRE plot outline, ensuring it is well-structured in three acts (Act One: Setup, Act Two: Confrontation, Act Three: Resolution) with clear headings for each act and detailed plot points within each.

        Return ONLY the revised plot outline, without any preamble or concluding remarks.
        """
        return prompt_template
