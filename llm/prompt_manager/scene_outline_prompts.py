# llm/prompt_manager/scene_outline_prompts.py

"""
Prompt templates for SceneOutline generation and enhancement.

This module defines the prompt templates used by the SceneOutlineGenerator
to generate and enhance SceneOutline objects. It utilizes base templates
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


class SceneOutlinePrompts:
    """
    Encapsulates prompt templates for SceneOutline operations.

    Provides methods to retrieve specific prompt templates for
    generating, structure checking, fixing, critiquing, and rewriting SceneOutlines.
    """

    def __init__(self, prompt_manager=None):
        """
        Initializes SceneOutlinePrompts.
        Prompt manager is currently not used, but included for potential future use or consistency.
        """
        self.prompt_manager = prompt_manager

    def create_scene_outlines_generation_prompt(self) -> str:
        """
        Returns the prompt template for generating SceneOutlines from a ChapterOutline.
        """
        prompt_template = f"""
        {COMMON_INSTRUCTIONS_NOVELIST.format(task="break down chapter outlines into comprehensive lists of scene outlines")}

        Based on the following chapter outline, create detailed outlines for {{num_scenes_per_chapter}} scenes within this chapter. Ensure the scenes logically break down the chapter's events and contribute to the overall narrative.

        Chapter Outline:
        ```
        {{chapter_outline}}
        ```

        For each scene, provide a concise outline (1-2 paragraphs) summarizing the key events, setting, characters present, and purpose of the scene within the chapter and overall story. The scene outlines should:
        - Logically break down the events described in the chapter outline into smaller, manageable scene units.
        - Detail the setting (location, time of day, atmosphere) and characters involved in each scene.
        - Clearly indicate the purpose of each scene in advancing the plot, developing characters, enhancing themes, or building suspense (especially regarding dark and erotic themes).
        - Be numbered sequentially within the chapter (Scene 1, Scene 2, etc.).
        - Collectively, the scene outlines should comprehensively cover all key events and narrative beats of the chapter outline.

        Your response MUST be ONLY the scene outlines, with each scene clearly numbered (e.g., "Scene 1:", "Scene 2:", etc.) followed by its outline. Do not include any preamble or concluding remarks, just the scene outlines themselves.
        """
        return prompt_template

    def create_scene_outlines_structure_check_prompt(self) -> str:
        """
        Returns the prompt template for checking the structure of SceneOutlines.
        """
        prompt_template = f"""
        {STRUCTURE_CHECK_INSTRUCTIONS}

        Here are the scene outlines:
        ```
        {{content}}
        ```

        Your task is to ensure that each scene outline:
        - Is clearly numbered and sequentially ordered within the chapter (Scene 1, Scene 2, Scene 3, etc.).
        - Provides a concise summary of the key events, setting, and characters present in the scene.
        - Clearly indicates the purpose of the scene in advancing the plot, developing characters, or enhancing themes.
        - Is approximately 1-2 paragraphs in length.

        If the scene outlines adhere to the correct structure, numbering, and each provides a relevant summary and purpose, respond with 'STRUCTURE_OK'.
        If there are any structural issues, such as incorrect numbering, missing scenes, summaries that are too short or too long, lack of clear purpose, or outlines that do not logically break down the chapter outline, provide a detailed explanation of the problems and how to fix them.
        """
        return prompt_template

    def create_scene_outlines_structure_fix_prompt(self) -> str:
        """
        Returns the prompt template for fixing structural issues in SceneOutlines.
        """
        prompt_template = f"""
        {STRUCTURE_FIX_PROMPT_TEMPLATE.format(content_with_structure_problems="{{content_with_structure_problems}}", structure_problems="{{structure_problems}}", json_structure="")}

        Your task is to modify the scene outlines to ensure that they are correctly structured and formatted. Specifically:
        - Ensure each scene outline is clearly numbered and sequentially ordered within the chapter (Scene 1, Scene 2, Scene 3, etc.).
        - Ensure each scene outline provides a concise summary of the scene's key elements: events, setting, characters, and purpose.
        - Adjust the length of summaries to be approximately 1-2 paragraphs for each scene.
        - Verify that all scene outlines logically break down and comprehensively cover the provided chapter outline.
        - Ensure each scene outline clearly articulates its purpose within the chapter and overall narrative.

        Return ONLY the corrected scene outlines, with each scene clearly numbered and followed by its revised outline. Do not include any preamble or concluding remarks. The corrected scene outlines should strictly adhere to the specified numbering and formatting.
        """
        return prompt_template

    def create_scene_outlines_critique_prompt(self) -> str:
        """
        Returns the prompt template for generating a critique of SceneOutlines.
        """
        prompt_template = f"""
        {CRITIQUE_PROMPT_TEMPLATE.format(content="{{content}}")}

        Focus your critique on:
        - **Scene to Scene Flow within Chapter:** Do the scene outlines flow logically within the chapter, creating a coherent and well-paced sequence of events? Are the transitions between scenes effective?
        - **Contribution to Chapter Objectives:** Does each scene outline clearly contribute to the objectives of the chapter as defined in the chapter outline? Is the purpose of each scene evident and meaningful within the chapter's context?
        - **Scene Detail and Clarity:** Are the summaries for each scene sufficiently detailed and clear? Do they provide a good sense of the scene's setting, characters' actions, and key events? Is the purpose of each scene clearly articulated?
        - **Pacing and Dramatic Tension within Chapter:** Does the set of scene outlines create effective pacing and build dramatic tension within the chapter? Are there variations in scene length and intensity to maintain reader engagement?
        - **Thematic and Tone Consistency:** Do the scene outlines maintain consistency in tone and themes with the Book Specification, Plot Outline, and Chapter Outline, particularly regarding the dark and erotic elements of the novel?
        - **Overall Effectiveness as Scene Breakdown:** How effective are these scene outlines as a blueprint for writing the actual scenes of the chapter? Do they provide a solid and inspiring foundation for scene writing? What are its strengths and weaknesses in guiding the scene-writing process?
        """
        return prompt_template

    def create_scene_outlines_rewrite_prompt(self) -> str:
        """
        Returns the prompt template for rewriting SceneOutlines based on critique.
        """
        prompt_template = f"""
        {REWRITE_PROMPT_TEMPLATE.format(content="{{content}}", critique="{{critique}}")}

        When rewriting the scene outlines, specifically focus on:
        - **Addressing all points raised in the critique** directly and thoroughly. Ensure that each issue identified by the editor is resolved in the revised scene outlines.
        - **Improving scene-to-scene flow and transitions within the chapter** to create a smoother and more coherent reading experience. Strengthen the logical connections between scenes and ensure effective transitions.
        - **Ensuring each scene outline clearly contributes to chapter objectives**, verifying that every scene serves a purpose within the chapter's narrative and overall plot progression. Enhance the articulation of each scene's purpose for greater clarity.
        - **Adding detail and clarity to scene summaries**, providing richer descriptions of settings, character actions, and key events to give a stronger sense of each scene's content and atmosphere.
        - **Refining pacing and dramatic tension** across the chapter's scene outlines. Adjust scene lengths, intensity, and placement to optimize pacing and build dramatic tension effectively.
        - **Maintaining thematic and tone consistency** with the established Book Specification, Plot Outline, and Chapter Outline. Ensure that the dark and erotic themes are appropriately and consistently integrated into the scene outlines.

        Rewrite the ENTIRE set of scene outlines, ensuring each scene is clearly numbered and provides a detailed and purposeful summary that logically contributes to the chapter's objectives and maintains thematic consistency.

        Return ONLY the revised set of scene outlines, with each scene clearly numbered and followed by its revised outline. Do not include any preamble or concluding remarks.
        """
        return prompt_template
