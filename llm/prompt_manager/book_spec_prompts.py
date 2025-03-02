# llm/prompt_manager/book_spec_prompts.py
from llm.prompt_manager.base_prompts import (
    COMMON_INSTRUCTIONS_NOVELIST,
    JSON_OUTPUT_FORMAT_INSTRUCTIONS,
    STRUCTURE_CHECK_INSTRUCTIONS,
    STRUCTURE_FIX_PROMPT_TEMPLATE,
    CRITIQUE_PROMPT_TEMPLATE,
    REWRITE_PROMPT_TEMPLATE,
)


class BookSpecPrompts:
    """
    Encapsulates prompt templates for BookSpec operations.

    Provides methods to retrieve specific prompt templates for
    generating, structure checking, fixing, critiquing, and rewriting BookSpecs.
    """

    def __init__(self, prompt_manager=None):
        """
        Initializes BookSpecPrompts.
        Prompt manager is currently not used, but included for potential future use or consistency.
        """
        self.prompt_manager = prompt_manager

    def create_book_spec_generation_prompt(self) -> str:
        """
        Returns the prompt template for generating a new BookSpec from a story idea.
        """
        json_structure = """
        {
            "title": "string",
            "genre": "string",
            "setting": "string",
            "themes": ["string", "string", "string"],
            "tone": "string",
            "point_of_view": "string",
            "characters": ["string", "string", "string"],
            "premise": "string"
        }
        """
        prompt_template = f"""
        {COMMON_INSTRUCTIONS_NOVELIST.format(task="generate detailed book specifications based on short story ideas")}

        Generate a detailed book specification for a novel based on the following idea: "{{idea}}".

        The novel should have a strong focus on dark themes.

        Include the following elements in the book specification:
        - Title (Compelling and evocative)
        - Genre (Specify the genre and subgenres - be specific, e.g., Dark Fantasy, Erotic Thriller)
        - Setting(s) (Detailed description of locations and time period, make it vivid)
        - Themes (List of 3-5 major themes explored in the novel, particularly dark and erotic themes)
        - Tone (Describe the overall tone of the novel - e.g., gritty, suspenseful, melancholic, sensual, noir, gothic)
        - Point of View (Specify the narrative perspective - e.g., first-person, third-person limited, third-person omniscient)
        - Characters (Detailed descriptions of 2-3 main characters, including their motivations, flaws, backstories, and key personality traits.  Focus on aspects related to dark and erotic elements. Each character description should be a single string, detailed and evocative.)
        - Premise (A concise and intriguing premise that sets up the central conflict and hints at the dark and erotic nature of the story. Make it immediately captivating.)

        Ensure the book specification is well-structured, creative, and clearly reflects the dark focus.  Be expansive and detailed in your descriptions.

        {JSON_OUTPUT_FORMAT_INSTRUCTIONS.format(json_structure=json_structure)}

        Do not include any explanation or introductory text, just the valid JSON.
        """
        return prompt_template

    def create_book_spec_structure_check_prompt(self) -> str:
        """
        Returns the prompt template for checking the structure of a BookSpec JSON.
        """
        prompt_template = f"""
        {STRUCTURE_CHECK_INSTRUCTIONS}

        Here is the BookSpec in JSON format:
        ```json
        {{content}}
        ```

        Specifically, check that:
        - The JSON is valid and parsable.
        - All fields are present: title, genre, setting, themes, tone, point_of_view, characters, premise.
        - All values are strings, EXCEPT for 'themes' and 'characters', which must be lists of strings.
        - The lists 'themes' and 'characters' contain at least one item.

        If the BookSpec adheres to the correct structure, respond with 'STRUCTURE_OK'.
        If there are any structural issues, respond with a detailed explanation of the problems and how to fix them.
        """
        return prompt_template

    def create_book_spec_structure_fix_prompt(self) -> str:
        """
        Returns the prompt template for fixing structural issues in a BookSpec JSON.
        """
        json_structure = """
        {
            "title": "string",
            "genre": "string",
            "setting": "string",
            "themes": ["string", "string", "string"],
            "tone": "string",
            "point_of_view": "string",
            "characters": ["string", "string", "string"],
            "premise": "string"
        }
        """
        prompt_template = f"""
        {STRUCTURE_FIX_PROMPT_TEMPLATE.format(json_structure=json_structure, content_with_structure_problems="{{content_with_structure_problems}}", structure_problems="{{structure_problems}}")}

        Your task is to modify the JSON to adhere to the correct structure as outlined below and fix the structural problems described:

        ```json
        {json_structure}
        ```

        Return only valid JSON, without deviations or extra explanation. Adhere strictly to this format, ensuring correct data types and escaping.
        """
        return prompt_template

    def create_book_spec_critique_prompt(self) -> str:
        """
        Returns the prompt template for generating a critique of a BookSpec.
        """
        prompt_template = f"""
        {CRITIQUE_PROMPT_TEMPLATE.format(content="{{content}}")}

        Focus your critique on:
        - **Clarity and Detail:** Are all sections sufficiently detailed and clear? Could any section be expanded or made more specific?
        - **Cohesion and Consistency:** Does the BookSpec present a unified and coherent vision for the novel? Are all elements consistent with each other?
        - **Strength of Dark Themes:** How effectively does the BookSpec establish and emphasize the dark and erotic themes of the novel? Is the premise intriguing and suggestive of the novel's nature?
        - **Character Depth:** Are the character descriptions compelling and insightful? Do they adequately explore motivations and flaws related to the dark and erotic elements?
        - **Overall Impact:** How compelling and well-defined is the BookSpec as a foundation for writing a novel? What are its strongest and weakest points?
        """
        return prompt_template

    def create_book_spec_rewrite_prompt(self) -> str:
        """
        Returns the prompt template for rewriting a BookSpec based on critique.
        """
        json_structure = """
        {
            "title": "string",
            "genre": "string",
            "setting": "string",
            "themes": ["string", "string", "string"],
            "tone": "string",
            "point_of_view": "string",
            "characters": ["string", "string", "string"],
            "premise": "string"
        }
        """
        prompt_template = f"""
        {REWRITE_PROMPT_TEMPLATE.format(content="{{content}}", critique="{{critique}}")}

        When rewriting, specifically focus on:
        - **Addressing all points raised in the critique** directly and thoroughly.
        - **Enhancing detail and clarity** in all sections, especially those identified as weak in the critique.
        - **Strengthening the dark and erotic themes** throughout the specification.
        - **Deepening character descriptions** to add more psychological insight and compelling motivations.
        - **Ensuring overall cohesion and impact** of the BookSpec as a robust foundation for novel writing.

        Output the ENTIRE revised BookSpec in JSON format.

        {JSON_OUTPUT_FORMAT_INSTRUCTIONS.format(json_structure=json_structure)}
        """
        return prompt_template