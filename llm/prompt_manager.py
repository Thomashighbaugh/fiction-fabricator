# llm/prompt_manager.py
# llm/prompt_manager.py
from core.book_spec import BookSpec
from utils.logger import logger
from core.plot_outline import SceneOutline


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

    # BookSpec Prompts
    def create_book_spec_generation_prompt(self) -> str:
        return self.create_book_spec_prompt("{idea}")

    def create_book_spec_prompt(self, idea: str) -> str:
        """
        Generates a prompt for creating a book specification based on a user-provided idea.
        """
        prompt_template = """
        You are a world-class novelist who can generate entire book specifications based on short story ideas.
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
        - Premise (A concise and intriguing premise that sets up the central conflict and hints at the dark and erotic nature of the story)

        Ensure the book specification is well-structured, creative, and clearly reflects the dark focus.

        Critically important: Your ENTIRE response MUST be valid JSON. Adhere strictly to this format, ensuring correct data types and escaping. The JSON object should have the following structure:

        {{
            "title": "string",
            "genre": "string",
            "setting": "string",
            "themes": ["string", "string", "string"],
            "tone": "string",
            "point_of_view": "string",
            "characters": ["string", "string", "string"],
            "premise": "string"
        }}

        Each character description in "characters" should be a SINGLE string. The LLM was generating a dictionary instead of a string.
        Do not include any explanation or introductory text, just the valid JSON. Ensure that the JSON is properly formatted with correct escaping of special characters.
        """
        return prompt_template

    def create_enhance_book_spec_prompt(self, current_spec: BookSpec) -> str:
        """
        Generates a prompt to enhance an existing BookSpec object.
        """
        prompt_template = """
        Enhance the following book specification to make it more compelling, detailed, and cohesive, while maintaining and strengthening its dark themes.

        Current Book Specification:
        ```json
        {current_spec_json}
        ```

        Refine and expand upon each section, focusing on:
        - Adding more specific details to the setting, themes, characters, and premise.
        - Ensuring all elements are consistent and contribute to a strong, unified vision for a dark and erotic novel.
        - Enriching character descriptions with deeper psychological insights and motivations related to the dark and erotic aspects of the story.
        - Strengthening the premise to be even more intriguing and suggestive of the novel's nature.
        - Improving the overall flow and readability of the book specification.

         Critically important: Your ENTIRE response MUST be valid JSON. Adhere strictly to this format, ensuring correct data types and escaping. The JSON object should have the following structure:

        {{
            "title": "string",
            "genre": "string",
            "setting": "string",
            "themes": ["string", "string", "string"],
            "tone": "string",
            "point_of_view": "string",
            "characters": ["string", "string", "string"],
            "premise": "string"
        }}

        Each character description in "characters" should be a SINGLE string. The LLM was generating a dictionary instead of a string.
        Do not include any explanation or introductory text, just the valid JSON. Ensure that the JSON is properly formatted with correct escaping of special characters.
        """
        return prompt_template

    def create_book_spec_critique_prompt(self) -> str:
        """
        Returns a prompt template for generating an actionable critique of a book specification.
        """
        return """You are a seasoned editor providing feedback on a book specification. Your goal is to identify areas where the specification can be strengthened to create a more compelling and well-defined foundation for the novel.

        Here is the current book specification:
        ```json
        {current_spec_json}
        ```

        Provide a concise critique (2-3 sentences) that identifies specific areas for improvement. Focus on aspects such as clarity, detail, coherence, and the strength of the dark themes. The critique should be actionable and guide the revision process.
        """

    def create_book_spec_rewrite_prompt(self) -> str:
        """
        Returns a prompt template for rewriting a book specification based on a critique.
        """
        return """
        You are a skilled writer revising a book specification based on editor feedback. Your goal is to create a more compelling and well-defined foundation for the novel.

        Here is the current book specification:
        ```json
        {current_spec_json}
        ```

        Here is the editor's critique:
        ```
        {critique}
        ```

        Revise the book specification based on the critique, focusing on the identified areas for improvement. Ensure that the revised specification is clear, detailed, coherent, and strongly emphasizes the dark themes of the novel.
        """

    def create_book_spec_structure_check_prompt(self) -> str:
        """
        Returns a prompt template for checking the structure of a BookSpec object.
        """
        return """
        You are a meticulous editor reviewing a BookSpec object for correct structure and formatting.

        Here is the BookSpec in JSON format:
        ```json
        {book_spec_json}
        ```

        Your task is to ensure that the JSON adheres to the following structure:

        ```json
        {{
            "title": "string",
            "genre": "string",
            "setting": "string",
            "themes": ["string", "string", "string"],
            "tone": "string",
            "point_of_view": "string",
            "characters": ["string", "string", "string"],
            "premise": "string"
        }}

        Specifically, check that:
        - The JSON is valid and parsable.
        - All fields are present.
        - All string values are properly formatted.
        - The "themes" and "characters" fields are lists of strings.

        If the BookSpec adheres to the correct structure, respond with "STRUCTURE_OK".
        If there are any structural issues, respond with a detailed explanation of the problems and how to fix them.
        """

    def create_book_spec_structure_fix_prompt(self) -> str:
        """
        Returns a prompt template for fixing the structure of a BookSpec object.
        """
        return """
        You are a meticulous editor tasked with fixing structural issues in a BookSpec object.

        Here is the flawed BookSpec in JSON format:
        ```json
        {book_spec_json}
        ```

        Here is a detailed list of structural problems and how to fix them:
        ```
        {structure_problems}
        ```

        Your task is to modify the JSON to adhere to the correct structure as outlined below:

        ```json
        {{
            "title": "string",
            "genre": "string",
            "setting": "string",
            "themes": ["string", "string", "string"],
            "tone": "string",
            "point_of_view": "string",
            "characters": ["string", "string", "string"],
            "premise": "string"
        }}

        Return only valid JSON, without deviations or extra explanation. Adhere strictly to this format, ensuring correct data types and escaping.
        """

        # Plot Outline Prompts
    def create_plot_outline_generation_prompt(self) -> str:
            """
            Returns a prompt template for generating a plot outline.
            """
            return """
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

            The plot outline MUST be structured in three acts, with roughly 3-5 major plot points described in each act.
            **Format each act as a bulleted list.**

            - **Act One: Setup**
            - [Plot Point 1 for Act One]
            - [Plot Point 2 for Act One]
            - [Plot Point 3 for Act One]
            - [Plot Point 4 for Act One]
            - [Plot Point 5 for Act One]

            - **Act Two: Confrontation**
            - [Plot Point 1 for Act Two]
            - [Plot Point 2 for Act Two]
            - [Plot Point 3 for Act Two]
            - [Plot Point 4 for Act Two]
            - [Plot Point 5 for Act Two]

            - **Act Three: Resolution**
            - [Plot Point 1 for Act Three]
            - [Plot Point 2 for Act Three]
            - [Plot Point 3 for Act Three]
            - [Plot Point 4 for Act Three]
            - [Plot Point 5 for Act Three]

            Each plot point should be a concise summary of a key event or development in the story.
            Ensure that the plot points within each act logically progress the narrative and contribute to the overall story arc.
            The entire plot outline should be suitable for use as a guide for writing the novel, providing a clear roadmap of the story's progression.
            """

    def create_plot_outline_structure_check_prompt(self) -> str:
        """
        Returns a prompt template for checking the structure of a PlotOutline object.
        """
        return """
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
        """

    def create_plot_outline_structure_fix_prompt(self) -> str:
        """
        Returns a prompt template for fixing the structure of a PlotOutline object.
        """
        return """
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
        """

    def create_plot_outline_critique_prompt(self) -> str:
        """
        Returns a prompt template for generating an actionable critique of a plot outline.
        """
        return """
        You are a story consultant providing feedback on a plot outline. Your goal is to identify areas where the outline can be strengthened to create a more compelling and structurally sound narrative.

        Here is the current plot outline:
        ```
        {current_outline}
        ```

        Provide a concise critique (2-3 sentences) that identifies specific areas for improvement. Focus on aspects such as plot structure, pacing, character arcs, thematic development, and the integration of dark elements. The critique should be actionable and guide the revision process.
        """

    def create_plot_outline_rewrite_prompt(self) -> str:
        """
        Returns a prompt template for rewriting a plot outline based on a critique.
        """
        return """
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
        """

    def create_enhance_plot_outline_prompt(self, current_outline: str) -> str:
        """
        Generates a prompt to enhance an existing plot outline.
        """
        return """
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

        Maintain the three-act structure and the formatting of the plot outline.
        """
    # Chapter Outline Prompts
    def create_chapter_outlines_generation_prompt(self) -> str:
        """
                Returns a prompt template for generating chapter outlines.
        +       Now generates chapters dynamically based on the plot outline, without a fixed number.
        """
        return """
        You are a world-class story writer who can create comprehensive chapter outlines based on a 3-act plot outline.
        Based on the following three-act plot outline, generate detailed chapter outlines.  The number of chapters should be appropriate to logically break down the plot outline provided.

        Format your response as follows, with each chapter clearly marked:

        Chapter 1: [Chapter Title]
        [Detailed outline for chapter 1 - 2-3 paragraphs]

        Chapter 2: [Chapter Title]
        [Detailed outline for chapter 2 - 3 paragraphs]

        ...

        Chapter N: [Chapter Title]
        [Detailed outline for chapter N - 2-3 paragraphs]


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

        Ensure the chapter outlines collectively cover the entire plot outline and provide a solid structure for writing the full novel. Generate a reasonable number of chapters that appropriately divide the provided plot outline.
        """

    def create_chapter_outlines_structure_check_prompt(self) -> str:
        """
        Returns a prompt template for checking the structure of chapter outlines.
        """
        return """
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
        """

    def create_chapter_outlines_structure_fix_prompt(self) -> str:
        """
        Returns a prompt template for fixing the structure of chapter outlines.
        """
        return """
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
        """

    def create_chapter_outlines_critique_prompt(self) -> str:
        """
        Returns a prompt template for generating an actionable critique of chapter outlines.
        """
        return """
        You are a novel editor providing feedback on a set of chapter outlines. Your goal is to identify areas where the outlines can be strengthened to create a more compelling and well-structured novel.

        Here are the current chapter outlines:
        ```
        {current_outlines}
        ```

        Provide a concise critique (2-3 sentences) that identifies specific areas for improvement. Focus on aspects such as chapter-to-chapter flow, pacing, plot progression, character development, thematic consistency, and the integration of dark elements. The critique should be actionable and guide the revision process.
        """

    def create_chapter_outlines_rewrite_prompt(self) -> str:
        """
        Returns a prompt template for rewriting chapter outlines based on a critique.
        """
        return """
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
        """

    def create_enhance_chapter_outlines_prompt(
        self, current_outlines: list[str]
    ) -> str:
        """
        Generates a prompt to enhance existing chapter outlines.
        """
        return """
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
        """

    # Scene Outline Prompts
    def create_scene_outlines_generation_prompt(self) -> str:
        """
        Returns a prompt template for generating scene outlines.
        """
        return """
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
        """

    def create_scene_outlines_structure_check_prompt(self) -> str:
        """
        Returns a prompt template for checking the structure of scene outlines.
        """
        return """
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
        """

    def create_scene_outlines_structure_fix_prompt(self) -> str:
        """
        Returns a prompt template for fixing the structure of scene outlines.
        """
        return """
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
        """

    def create_scene_outlines_critique_prompt(self) -> str:
        """
        Returns a prompt template for generating an actionable critique of scene outlines.
        """
        return """
        You are a novel editor providing feedback on a set of scene outlines. Your goal is to identify areas where the outlines can be strengthened to create a more compelling and well-structured chapter.

        Here are the current scene outlines:
        ```
        {current_outlines}
        ```

        Provide a concise critique (2-3 sentences) that identifies specific areas for improvement. Focus on aspects such as scene-to-scene flow, pacing within the chapter, contribution of scenes to chapter objectives and plot, character consistency, and integration of dark elements. The critique should be actionable and guide the revision process.
        """

    def create_scene_outlines_rewrite_prompt(self) -> str:
        """
        Returns a prompt template for rewriting scene outlines based on a critique.
        """
        return """
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
        """

    def create_enhance_scene_outlines_prompt(self, current_outlines: list[str]) -> str:
        """
        Generates a prompt to enhance existing scene outlines for a chapter.
        """
        return """
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
        """

    # Scene Part Prompts
    def create_scene_part_generation_prompt(self) -> str:
        """
        Returns a prompt template for generating a scene part.
        """
        return """
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
        """

    def create_scene_part_structure_check_prompt(self) -> str:
        """
        Returns a prompt template for checking the structure of a scene part.
        """
        return """
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
        """

    def create_scene_part_structure_fix_prompt(self) -> str:
        """
        Returns a prompt template for fixing the structure of a scene part.
        """
        return """
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
        """

    def create_scene_part_critique_prompt(self) -> str:
        """
        Returns a prompt template for generating an actionable critique of a scene part.
        """
        return """You are a world-class editor providing concise and actionable feedback to improve a scene part in a novel.

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
        """

    def create_scene_part_rewrite_prompt(self) -> str:
        """
        Returns a prompt template for rewriting a scene part based on a critique.
        """
        return """
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
        """

    def create_enhance_scene_part_prompt(
        self,
        scene_part: str,
        part_number: int,
        book_spec: BookSpec,
        chapter_outline: str,
        scene_outline_full: SceneOutline,
    ) -> str:
        """
        Generates a prompt to enhance an existing part of a scene's text content.
        """
        book_spec_text = book_spec.model_dump_json(indent=4)
        return f"""
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
        """
