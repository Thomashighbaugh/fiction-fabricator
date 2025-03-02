# llm/prompt_manager/chapter_outline_prompts.py

"""
Prompt templates for ChapterOutline generation and enhancement.

This module defines the prompt templates used by the ChapterOutlineGenerator
to generate and enhance ChapterOutline objects. It utilizes base templates
from base_prompts.py for consistency and reduced redundancy.
"""

from llm.prompt_manager.base_prompts import (
    COMMON_INSTRUCTIONS_NOVELIST,
    STRUCTURE_CHECK_INSTRUCTIONS,
    STRUCTURE_FIX_PROMPT_TEMPLATE,
    CRITIQUE_PROMPT_TEMPLATE,
    REWRITE_PROMPT_TEMPLATE,
    JSON_OUTPUT_FORMAT_INSTRUCTIONS,
)


class ChapterOutlinePrompts:
    """
    Encapsulates prompt templates for ChapterOutline operations.

    Provides methods to retrieve specific prompt templates for
    generating, structure checking, fixing, critiquing, and rewriting ChapterOutlines.
    """

    def __init__(self, prompt_manager=None):
        """
        Initializes ChapterOutlinePrompts.
        Prompt manager is currently not used, but included for potential future use or consistency.
        """
        self.prompt_manager = prompt_manager

    def create_chapter_outlines_generation_prompt(self) -> str:
        """
        Returns the prompt template for generating ChapterOutlines from a PlotOutline.
        """
        prompt_template = f"""
        {COMMON_INSTRUCTIONS_NOVELIST.format(task="create comprehensive chapter outlines based on a 3-act plot outline")}

        Based on the following three-act plot outline, generate exactly {{num_chapters}} detailed chapter outlines. I need precisely {{num_chapters}} chapters, no fewer, no more. Divide the plot events roughly equally across these {{num_chapters}} chapters, ensuring a logical flow and pacing.

        Plot Outline:
        ```
        {{plot_outline}}
        ```

        For each chapter, provide a concise outline (2-3 paragraphs) summarizing the key events and developments that occur within that chapter. The chapter outlines should:
        - Clearly advance the overall plot as described in the three-act outline.
        - Maintain the established tone and themes, especially the dark and erotic elements.
        - Create anticipation for subsequent chapters and maintain reader engagement.
        - Be numbered sequentially (Chapter 1, Chapter 2, etc.).
        - **Crucially, for Chapter 1, provide an exposition-focused summary that introduces the main characters, setting, and central conflict as if the reader knows nothing about them. Avoid referring to characters as if they are already known. This chapter should set the stage for the rest of the novel.**

        Ensure the chapter outlines collectively cover the entire plot outline and provide a solid structure for writing the full novel.

        Your response MUST be ONLY the chapter outlines, with each chapter clearly numbered (e.g., "Chapter 1:", "Chapter 2:", etc.) followed by its outline. Do not include any preamble or concluding remarks, just the chapter outlines themselves.
        """
        return prompt_template

    def create_chapter_outlines_structure_check_prompt(self) -> str:
        """
        Returns the prompt template for checking the structure of ChapterOutlines.
        """
        prompt_template = f"""
        {STRUCTURE_CHECK_INSTRUCTIONS}

        Here are the chapter outlines:
        ```
        {{content}}
        ```

        Your task is to ensure that each chapter outline:
        - Is clearly numbered and sequentially ordered (Chapter 1, Chapter 2, Chapter 3, etc.).
        - Provides a concise summary of the key events and developments within that chapter.
        - Clearly advances the overall plot as outlined in the provided 3-act plot outline.
        - Is approximately 2-3 paragraphs in length.

        If the chapter outlines adhere to the correct structure and numbering, and each provides a relevant summary, respond with 'STRUCTURE_OK'.
        If there are any structural issues, such as incorrect numbering, missing chapters, summaries that are too short or too long, or outlines that do not clearly relate to the plot outline, provide a detailed explanation of the problems and how to fix them.
        """
        return prompt_template

    def create_chapter_outlines_structure_fix_prompt(self) -> str:
        """
        Returns the prompt template for fixing structural issues in ChapterOutlines.
        """
        prompt_template = f"""
        {STRUCTURE_FIX_PROMPT_TEMPLATE.format(content_with_structure_problems="{{content_with_structure_problems}}", structure_problems="{{structure_problems}}", json_structure="")}

        Your task is to modify the chapter outlines to ensure that they are correctly structured and formatted. Specifically:
        - Ensure each chapter outline is clearly numbered and sequentially ordered (Chapter 1, Chapter 2, Chapter 3, etc.).
        - Ensure each chapter outline provides a concise and relevant summary of the chapter's events.
        - Adjust the length of summaries to be approximately 2-3 paragraphs for each chapter.
        - Verify that all chapter outlines logically follow and advance the provided 3-act plot outline.

        Return ONLY the corrected chapter outlines, with each chapter clearly numbered and followed by its revised outline. Do not include any preamble or concluding remarks. The corrected chapter outlines should strictly adhere to the specified numbering and formatting.
        """
        return prompt_template

    def create_chapter_outlines_critique_prompt(self) -> str:
        """
        Returns the prompt template for generating a critique of ChapterOutlines.
        """
        prompt_template = f"""
        {CRITIQUE_PROMPT_TEMPLATE.format(content="{{content}}")}

        Focus your critique on:
        - **Chapter to Chapter Flow:** Do the chapter outlines flow logically from one to the next, creating a smooth and coherent progression of the story? Are the transitions between chapters effective?
        - **Pacing and Plot Progression:** Is the pacing appropriate across the chapter outlines? Does each chapter outline advance the plot effectively, building upon previous chapters and setting up future developments?
        - **Coverage of Plot Outline:** Do the chapter outlines collectively cover all the key plot points from the provided 3-act plot outline? Are there any significant plot points missing or glossed over?
        - **Chapter Summary Detail and Clarity:** Are the summaries for each chapter sufficiently detailed and clear? Do they provide a good sense of the chapter's main events, character developments, and contributions to the overall story?
        - **Thematic Consistency:** Do the chapter outlines maintain consistency in tone and themes with the Book Specification and Plot Outline, particularly regarding the dark and erotic elements of the novel?
        - **Engagement and Intrigue:** Do the chapter outlines, as a set, create a sense of anticipation and engagement? Do they make you want to read the full novel? What are their strongest and weakest points in terms of capturing reader interest?
        """
        return prompt_template

    def create_chapter_outlines_rewrite_prompt(self) -> str:
        """
        Returns the prompt template for rewriting ChapterOutlines based on critique.
        """
        prompt_template = f"""
        {REWRITE_PROMPT_TEMPLATE.format(content="{{content}}", critique="{{critique}}")}

        When rewriting the chapter outlines, specifically focus on:
        - **Addressing all points raised in the critique** directly and thoroughly. Ensure that each issue identified by the editor is resolved in the revised chapter outlines.
        - **Improving chapter-to-chapter flow and transitions** to create a smoother and more coherent narrative progression. Strengthen the logical connections between consecutive chapters.
        - **Refining pacing and plot progression** to ensure that the story advances at an engaging and effective rate across the chapters. Adjust the distribution of plot points across chapters as needed.
        - **Ensuring comprehensive coverage of the Plot Outline**, verifying that all key plot points from the 3-act plot outline are adequately addressed within the chapter outlines. Add detail or expand summaries where necessary to fully incorporate all essential plot elements.
        - **Enhancing detail and clarity in chapter summaries**, providing richer descriptions of events, character actions, and setting to give a stronger sense of each chapter's content.
        - **Maintaining thematic consistency** with the Book Specification and Plot Outline. Ensure that the dark and erotic themes are appropriately integrated and consistently present throughout the chapter outlines.

        Rewrite the ENTIRE set of chapter outlines, ensuring each chapter is clearly numbered and provides a detailed and engaging summary that logically advances the plot and maintains thematic consistency.

        Return ONLY the revised set of chapter outlines, with each chapter clearly numbered and followed by its revised outline. Do not include any preamble or concluding remarks.
        """
        return prompt_template
