# llm/prompt_manager/scene_part_prompts.py

"""
Prompt templates for ScenePart generation and enhancement.

This module defines the prompt templates used by the ScenePartGenerator
to generate and enhance ScenePart objects. It utilizes base templates
from base_prompts.py for consistency and reduced redundancy.
"""

from llm.prompt_manager.base_prompts import (
    COMMON_INSTRUCTIONS_NOVELIST,
    STRUCTURE_CHECK_INSTRUCTIONS,
    STRUCTURE_FIX_PROMPT_TEMPLATE,
    CRITIQUE_PROMPT_TEMPLATE,
    REWRITE_PROMPT_TEMPLATE,
)


class ScenePartPrompts:
    """
    Encapsulates prompt templates for ScenePart operations.

    Provides methods to retrieve specific prompt templates for
    generating, structure checking, fixing, critiquing, and rewriting SceneParts.
    """

    def __init__(self, prompt_manager=None):
        """
        Initializes ScenePartPrompts.
        Prompt manager is currently not used, but included for potential future use or consistency.
        """
        self.prompt_manager = prompt_manager

    def create_scene_part_generation_prompt(self) -> str:
        """
        Returns the prompt template for generating a ScenePart.
        """
        prompt_template = f"""
        {COMMON_INSTRUCTIONS_NOVELIST.format(task="generate specific parts of scenes from scene outlines, creating vivid and engaging narrative text")}

        Generate part {{part_number}} of the text for the following scene, based on the provided book specification, chapter outline, and scene outline. Focus on writing compelling prose that brings the scene to life.

        Book Specification:
        ```json
        {{book_spec_text}}
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

        Write this part of the scene in a compelling and descriptive manner, consistent with the tone, themes, and characters established in the book specification. Emphasize the dark and erotic elements as appropriate for this scene and the overall novel, but ensure that these elements are integrated tastefully and contribute to the narrative's depth and complexity, rather than being gratuitous. Focus on vivid sensory descriptions, engaging dialogue that reveals character and advances the plot, and actions that move the scene forward dynamically.

        The generated text should be suitable for inclusion in a novel and should seamlessly connect with the preceding and subsequent parts of the scene (if applicable), creating a cohesive and immersive reading experience.

        Your response MUST be ONLY the text for scene part {{part_number}}. Do not include any preamble or concluding remarks, just the scene part text itself.
        """
        return prompt_template

    def create_scene_part_structure_check_prompt(self) -> str:
        """
        Returns the prompt template for checking the structure of a ScenePart.
        """
        prompt_template = f"""
        {STRUCTURE_CHECK_INSTRUCTIONS}

        Here is the scene part text:
        ```
        {{content}}
        ```

        Your task is to ensure that the scene part:
        - Is written in grammatically correct English with proper sentence structure and punctuation.
        - Is formatted as plain text, without any structural elements like headings, bullet points, or scene breaks within the part.
        - Is coherent and reads smoothly as a part of a narrative, logically connecting to the surrounding parts of the scene (even though the context of surrounding parts is not provided here).
        - Maintains a consistent tone and style appropriate for a dark and erotic novel, as established in the Book Specification (even though the Book Specification itself is not provided here).

        If the scene part adheres to these basic structural and grammatical criteria, and is presented as plain, coherent text, respond with 'STRUCTURE_OK'.
        If there are any structural issues, such as grammatical errors, formatting issues, incoherence, or significant deviations in tone, provide a detailed explanation of the problems and how to fix them.
        """
        return prompt_template

    def create_scene_part_structure_fix_prompt(self) -> str:
        """
        Returns the prompt template for fixing structural issues in a ScenePart.
        """
        prompt_template = f"""
        {STRUCTURE_FIX_PROMPT_TEMPLATE.format(content_with_structure_problems="{{content_with_structure_problems}}", structure_problems="{{structure_problems}}", json_structure="")}

        Your task is to modify the scene part text to correct the identified structural and grammatical issues. Specifically:
        - Correct any grammatical errors, punctuation mistakes, and awkward sentence structures to ensure the text is grammatically sound and easy to read.
        - Ensure the text is formatted as plain text, removing any unintended structural elements like headings or bullet points. The scene part should be a continuous block of narrative text.
        - Improve coherence and flow to ensure the scene part reads smoothly and logically. Enhance transitions and connections within the text as needed.
        - Adjust the tone and style to ensure consistency with the established tone for a dark and erotic novel, aligning with the overall project guidelines.

        Return ONLY the corrected scene part text, without any preamble or concluding remarks. The corrected scene part should be grammatically correct, formatted as plain text, and structurally sound.
        """
        return prompt_template

    def create_scene_part_critique_prompt(self) -> str:
        """
        Returns the prompt template for generating a critique of a ScenePart.
        """
        prompt_template = f"""
        {CRITIQUE_PROMPT_TEMPLATE.format(content="{{content}}")}

        Focus your critique on:
        - **Descriptive Writing and Imagery:** How vivid and engaging are the descriptions? Does the writing effectively use sensory details to immerse the reader in the scene's setting and atmosphere? Could the imagery be stronger or more evocative?
        - **Character Voice and Dialogue:** If dialogue is present, how effective is it in revealing character and advancing the plot? Is the character voice distinct and believable? Is the dialogue engaging and natural?
        - **Pacing and Engagement:** Is the pacing of the scene part effective? Does it maintain reader engagement and interest? Is there a sense of dramatic tension or emotional depth? Could the pacing be improved to enhance impact?
        - **Integration of Dark and Erotic Themes:** If applicable, how well are the dark and erotic themes integrated into this scene part? Are these elements handled tastefully and effectively contribute to the narrative, or do they feel gratuitous or underdeveloped?
        - **Consistency with Book/Chapter/Scene Outlines:** How well does this scene part realize the potential of the provided Book Specification, Chapter Outline, and Scene Outline? Does it effectively capture the intended events, tone, and purpose of this part of the scene?
        - **Overall Writing Quality and Impact:** Evaluate the overall quality of the writing in this scene part. What are its strengths and weaknesses? How could it be improved to be more compelling, immersive, and impactful for the reader?
        """
        return prompt_template

    def create_scene_part_rewrite_prompt(self) -> str:
        """
        Returns the prompt template for rewriting a ScenePart based on critique.
        """
        prompt_template = f"""
        {REWRITE_PROMPT_TEMPLATE.format(content="{{content}}", critique="{{critique}}")}

        When rewriting the scene part, specifically focus on:
        - **Addressing all points raised in the critique** directly and thoroughly. Ensure that each issue identified by the editor is resolved in the revised scene part text.
        - **Enhancing descriptive writing and imagery** to create a more vivid and immersive experience for the reader. Strengthen sensory details, atmosphere, and setting descriptions.
        - **Refining character voice and dialogue** to make it more engaging, revealing, and impactful. Improve the believability and distinctiveness of character voices and ensure dialogue effectively serves the narrative.
        - **Adjusting pacing and engagement** to optimize the scene part's impact. Enhance dramatic tension, emotional depth, and overall reader interest through pacing adjustments and more compelling prose.
        - **Improving the integration of dark and erotic themes**, if applicable, ensuring these elements are handled tastefully and contribute meaningfully to the narrative's complexity and depth. Avoid gratuitous or underdeveloped portrayals of these themes; instead, aim for nuanced and impactful integration.
        - **Ensuring stronger consistency with the Book Specification, Chapter Outline, and Scene Outline**, aligning the scene part more closely with the established guidelines and intended purpose. Enhance the realization of the outlined events, tone, and objectives within the scene part text.

        Rewrite the ENTIRE scene part text, focusing on enhancing its descriptive quality, character voice, pacing, thematic integration, and overall writing quality to create a more compelling and immersive narrative.

        Return ONLY the revised scene part text, without any preamble or concluding remarks.
        """
        return prompt_template
