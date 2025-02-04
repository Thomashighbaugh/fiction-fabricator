# fiction_fabricator/src/llm/prompt_manager.py
from core.book_spec import BookSpec
from utils.logger import logger


class PromptManager:
    """
    Manages prompt creation for different stages of the novel generation process.

    This class provides methods to generate prompts for creating book specifications,
    plot outlines, chapter outlines, scene outlines, and scene parts. It also includes
    methods for enhancing existing content. Prompts are designed to guide the LLM
    to generate creative and relevant content.
    """

    def __init__(self, book_spec: BookSpec = None):
        """
        Initializes the PromptManager.

        Args:
            book_spec (BookSpec, optional): An initial BookSpec object to provide context. Defaults to None.
        """
        self.book_spec = book_spec

    def create_book_spec_prompt(self, idea: str) -> str:
        """
        Generates a prompt for creating a book specification based on a user-provided idea.

        Emphasizes dark elements in the generated book specification.

        Args:
            idea (str): The user's initial story idea.

        Returns:
            str: The generated prompt for book specification creation.
        """
        prompt = f"""
        Generate a detailed book specification for a novel based on the following idea: "{idea}".

        The novel should have a strong focus on dark themes.

        Include the following elements in the book specification:
        - Title (Compelling and evocative)
        - Genre (Specify the genre and subgenres)
        - Setting(s) (Detailed description of locations and time period)
        - Themes (List of major themes explored in the novel)
        - Tone (Describe the overall tone of the novel - e.g., gritty, suspenseful, melancholic, sensual)
        - Point of View (Specify the narrative perspective - e.g., first-person, third-person limited, third-person omniscient)
        - Characters (Detailed descriptions of 2-3 main characters, including their motivations and flaws)
        - Premise (A concise and intriguing premise that sets up the central conflict)

        Ensure the book specification is well-structured, creative, and clearly reflects the dark focus.
        """
        prompt = self.optimize_prompt_tokens(prompt)
        logger.debug(f"Generated book spec prompt: {prompt}")
        return prompt

    def create_enhance_book_spec_prompt(self, current_spec: BookSpec) -> str:
        """
        Generates a prompt to enhance an existing BookSpec object.

        Asks the LLM to refine and expand upon the existing book specification,
        further emphasizing dark elements and ensuring coherence.

        Args:
            current_spec (BookSpec): The current BookSpec object to be enhanced.

        Returns:
            str: The generated prompt for enhancing the book specification.
        """
        spec_text = current_spec.model_dump_json(indent=4)
        prompt = f"""
        Enhance the following book specification to make it more compelling, detailed, and cohesive, while maintaining and strengthening its dark themes.

        Current Book Specification:
        ```json
        {spec_text}
        ```

        Refine and expand upon each section, focusing on:
        - Adding more specific details to the setting, themes, characters, and premise.
        - Ensuring all elements are consistent and contribute to a strong, unified vision.
        - Enriching character descriptions with deeper psychological insights and motivations.
        - Strengthening the premise to be even more intriguing and suggestive of the novel's nature.
        - Improving the overall flow and readability of the book specification.

        Output should be a complete, enhanced book specification in the same JSON format.
        """
        prompt = self.optimize_prompt_tokens(prompt)
        logger.debug(f"Generated enhance book spec prompt: {prompt}")
        return prompt

    def create_plot_outline_prompt(self, book_spec: BookSpec) -> str:
        """
        Generates a prompt to create a three-act plot outline based on the BookSpec.

        The plot outline should translate the book specification into a structured narrative,
        maintaining themes and focusing on creating compelling conflict
        and character arcs within a three-act structure.

        Args:
            book_spec (BookSpec): The BookSpec object guiding the plot outline creation.

        Returns:
            str: The generated prompt for plot outline creation.
        """
        spec_text = book_spec.model_dump_json(indent=4)
        prompt = f"""
        Create a three-act plot outline for a novel based on the following book specification.

        Book Specification:
        ```json
        {spec_text}
        ```

        The plot outline should be structured in three acts:
        - Act One: Setup - Introduce the characters, setting, and premise. Establish the initial conflict and the protagonist's goals.
        - Act Two: Confrontation - Develop the central conflict, raise the stakes, introduce obstacles and challenges for the protagonist.
        - Act Three: Resolution - Climax of the story, resolution of the main conflict, and thematic closure.

        The plot outline should be detailed enough to provide a clear roadmap for writing the novel, with specific plot points and character developments in each act. Ensure the outline effectively incorporates and develops the themes from the book specification.
        """
        prompt = self.optimize_prompt_tokens(prompt)
        logger.debug(f"Generated plot outline prompt: {prompt}")
        return prompt

    def create_enhance_plot_outline_prompt(self, current_outline: str) -> str:
        """
        Generates a prompt to enhance an existing plot outline.

        Asks the LLM to refine and expand upon the existing plot outline, ensuring
        it is detailed, well-structured, and effectively develops the themes from the book specification.

        Args:
            current_outline (str): The current plot outline text to be enhanced.

        Returns:
            str: The generated prompt for enhancing the plot outline.
        """
        prompt = f"""
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
        """
        prompt = self.optimize_prompt_tokens(prompt)
        logger.debug(f"Generated enhance plot outline prompt: {prompt}")
        return prompt

    def create_chapter_outlines_prompt(
        self, plot_outline: str, num_chapters: int
    ) -> str:
        """
        Generates a prompt to create chapter outlines based on the plot outline.

        Divides the three-act plot outline into a specified number of chapters,
        creating a brief outline for each chapter that advances the plot and maintains
        the thematic focus.

        Args:
            plot_outline (str): The three-act plot outline.
            num_chapters (int): The desired number of chapters for the novel.

        Returns:
            str: The generated prompt for chapter outline creation.
        """
        prompt = f"""
        Based on the following three-act plot outline, create detailed outlines for {num_chapters} chapters. Divide the plot events roughly equally across the chapters, ensuring a logical flow and pacing.

        Plot Outline:
        ```
        {plot_outline}
        ```

        For each chapter, provide a concise outline (2-3 paragraphs) summarizing the key events and developments that occur within that chapter. The chapter outlines should:
        - Clearly advance the overall plot as described in the three-act outline.
        - Maintain the established tone and themes.
        - Create anticipation for subsequent chapters and maintain reader engagement.
        - Be numbered sequentially (Chapter 1, Chapter 2, etc.).

        Ensure the chapter outlines collectively cover the entire plot outline and provide a solid structure for writing the full novel.
        """
        prompt = self.optimize_prompt_tokens(prompt)
        logger.debug(f"Generated chapter outlines prompt: {prompt}")
        return prompt

    def create_enhance_chapter_outlines_prompt(
        self, current_outlines: list[str]
    ) -> str:
        """
        Generates a prompt to enhance existing chapter outlines.

        Refines and expands upon the existing chapter outlines, ensuring they are detailed,
        logically connected, and effectively contribute to the overall plot and thematic
        development.

        Args:
            current_outlines (list[str]): A list of current chapter outline texts.

        Returns:
            str: The generated prompt for enhancing chapter outlines.
        """
        outlines_text = "\n\n".join(current_outlines)
        prompt = f"""
        Enhance the following chapter outlines to make them more detailed, logically connected, and compelling. Ensure each chapter outline effectively contributes to the overall plot progression and thematic development.

        Current Chapter Outlines:
        ```
        {outlines_text}
        ```

        Refine and expand upon each chapter outline, focusing on:
        - Adding more specific details about events, character actions, and setting within each chapter.
        - Strengthening the transitions and connections between chapters to ensure a smooth narrative flow.
        - Ensuring each chapter outline clearly contributes to the overall three-act plot structure.
        - Deepening the integration of the themes within the chapter events.
        - Checking for consistency and pacing across all chapter outlines.
        - Making sure each chapter outline creates sufficient intrigue and motivation to read the full chapter.

        Output should be a set of enhanced chapter outlines in text format, clearly numbered and formatted as individual chapter outlines.
        """
        prompt = self.optimize_prompt_tokens(prompt)
        logger.debug(f"Generated enhance chapter outlines prompt: {prompt}")
        return prompt

    def create_scene_outlines_prompt(
        self, chapter_outline: str, num_scenes_per_chapter: int
    ) -> str:
        """
        Generates a prompt to create scene outlines for a given chapter outline.

        Breaks down a chapter outline into a specified number of scenes, providing
        a brief outline for each scene that details the events, setting, and characters
        involved, while continuing to emphasize the themes.

        Args:
            chapter_outline (str): The outline for the chapter.
            num_scenes_per_chapter (int): The desired number of scenes within the chapter.

        Returns:
            str: The generated prompt for scene outline creation.
        """
        prompt = f"""
        Based on the following chapter outline, create detailed outlines for {num_scenes_per_chapter} scenes within this chapter. Ensure the scenes logically break down the chapter's events and contribute to the overall narrative.

        Chapter Outline:
        ```
        {chapter_outline}
        ```

        For each scene, provide a concise outline (1-2 paragraphs) summarizing the key events, setting, characters present, and purpose of the scene within the chapter and overall story. The scene outlines should:
        - Logically break down the events described in the chapter outline.
        - Detail the setting and characters involved in each scene.
        - Clearly indicate the purpose of each scene in advancing the plot, developing characters, or enhancing themes.
        - Be numbered sequentially within the chapter (Scene 1, Scene 2, etc.).

        Ensure the scene outlines collectively cover all key events of the chapter and provide a detailed guide for writing the scenes.
        """
        prompt = self.optimize_prompt_tokens(prompt)
        logger.debug(f"Generated scene outlines prompt: {prompt}")
        return prompt

    def create_enhance_scene_outlines_prompt(self, current_outlines: list[str]) -> str:
        """
        Generates a prompt to enhance existing scene outlines for a chapter.

        Refines and expands upon the existing scene outlines, ensuring they are detailed,
        logically sequenced, and effectively contribute to the chapter's and novel's
        plot and themes.

        Args:
            current_outlines (list[str]): A list of current scene outline texts for a chapter.

        Returns:
            str: The generated prompt for enhancing scene outlines.
        """
        outlines_text = "\n\n".join(current_outlines)
        prompt = f"""
        Enhance the following scene outlines for a chapter to make them more detailed, logically sequenced, and compelling. Ensure each scene outline effectively contributes to the chapter's narrative and the overall themes of the novel.

        Current Scene Outlines:
        ```
        {outlines_text}
        ```

        Refine and expand upon each scene outline, focusing on:
        - Adding more specific details about actions, dialogue, setting descriptions, and character emotions within each scene.
        - Strengthening the transitions and connections between scenes to ensure a smooth flow within the chapter.
        - Ensuring each scene outline clearly contributes to the chapter's objectives and the overall plot.
        - Deepening the integration of the themes within the scene events and character interactions.
        - Checking for pacing and dramatic tension within and across the scene outlines.
        - Ensuring each scene outline provides a strong foundation for writing the full scene.

        Output should be a set of enhanced scene outlines in text format, clearly numbered and formatted as individual scene outlines.
        """
        prompt = self.optimize_prompt_tokens(prompt)
        logger.debug(f"Generated enhance scene outlines prompt: {prompt}")
        return prompt

    def create_scene_part_prompt(
        self,
        scene_outline: str,
        part_number: int,
        book_spec: BookSpec,
        chapter_outline: str,
        scene_outline_full: str,
    ) -> str:
        """
        Generates a prompt to create a specific part of a scene's text content.

        This prompt is used to generate the actual narrative text for a scene, broken down into parts.
        It provides context from the book specification, chapter outline, and scene outline to ensure
        consistency and thematic relevance.

        Args:
            scene_outline (str): The outline for the specific scene part.
            part_number (int): The part number of the scene (e.g., 1, 2, 3 for beginning, middle, end).
            book_spec (BookSpec): The BookSpec object for overall context.
            chapter_outline (str): The outline for the chapter containing the scene.
            scene_outline_full (str): The complete outline for the scene.

        Returns:
            str: The generated prompt for creating a part of the scene's text content.
        """
        book_spec_text = book_spec.model_dump_json(indent=4)
        prompt = f"""
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

        Write this part of the scene in a compelling and descriptive manner, consistent with the tone, themes, and characters established in the book specification. Focus on vivid descriptions, engaging dialogue, and actions that move the scene forward.

        The generated text should be suitable for inclusion in a novel and should seamlessly connect with the preceding and subsequent parts of the scene (if applicable).
        """
        prompt = self.optimize_prompt_tokens(prompt)
        logger.debug(f"Generated scene part prompt (part {part_number}): {prompt}")
        return prompt

    def create_enhance_scene_part_prompt(
        self,
        scene_part: str,
        part_number: int,
        book_spec: BookSpec,
        chapter_outline: str,
        scene_outline_full: str,
    ) -> str:
        """
        Generates a prompt to enhance an existing part of a scene's text content.

        Refines and improves an existing scene part, using the book specification, chapter outline,
        and scene outline for context. Focuses on enhancing the writing quality, deepening
        thematic elements, and ensuring consistency and impact.

        Args:
            scene_part (str): The existing text content of the scene part.
            part_number (int): The part number of the scene.
            book_spec (BookSpec): The BookSpec object for overall context.
            chapter_outline (str): The outline for the chapter containing the scene.
            scene_outline_full (str): The complete outline for the scene.

        Returns:
            str: The generated prompt for enhancing a scene part.
        """
        book_spec_text = book_spec.model_dump_json(indent=4)
        prompt = f"""
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
        - Ensuring the scene part effectively fulfills its purpose within the scene and chapter.
        - Checking for consistency with the overall tone and style of the novel.
        - Making the scene part more engaging and immersive for the reader.

        Output should be the enhanced text for scene part {part_number}.
        """
        prompt = self.optimize_prompt_tokens(prompt)
        logger.debug(
            f"Generated enhance scene part prompt (part {part_number}): {prompt}"
        )
        return prompt

    def optimize_prompt_tokens(self, prompt: str) -> str:
        """
        Optimizes prompt tokens to reduce prompt length (future implementation).

        This method is intended to implement techniques for reducing the token count of prompts
        to improve efficiency and potentially reduce LLM processing costs.

        Args:
            prompt (str): The prompt text to be optimized.

        Returns:
            str: The optimized prompt text.
        """
        max_length = 500  # Example maximum prompt length
        if len(prompt) > max_length:
            optimized_prompt = prompt[:max_length] + "..."  # Truncate and add ellipsis
            logger.info(
                f"Prompt optimized (truncated) from {len(prompt)} to {len(optimized_prompt)} characters."
            )
            return optimized_prompt
        else:
            logger.debug("Prompt token optimization - returning original prompt.")
            return prompt

    def batch_prompts(self, prompts: list[str]) -> list[str]:
        """
        Batches prompts for more efficient LLM processing (future implementation).

        This method is intended to implement prompt batching techniques to send multiple prompts
        to the LLM in a single request.  Currently, basic batching is not supported.

        Args:
            prompts (list[str]): A list of prompt texts to be batched.

        Returns:
            list[str]: A list of batched prompts (currently returns the original list).
        """
        # In the current implementation, actual batching is not supported.  We simply log a message.
        logger.warning(
            "Prompt batching is not currently implemented. Returning original prompts."
        )
        return prompts
