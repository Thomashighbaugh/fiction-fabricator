# core/content_generator.py
from core.content_generation.book_spec_generation import (
    generate_book_spec as _generate_book_spec,
)
from core.content_generation.book_spec_generation import (
    enhance_book_spec as _enhance_book_spec,
)
from core.content_generation.plot_outline_generation import (
    generate_plot_outline as _generate_plot_outline,
)
from core.content_generation.plot_outline_generation import (
    enhance_plot_outline as _enhance_plot_outline,
)
from core.content_generation.chapter_outline_generation import (
    generate_chapter_outlines as _generate_chapter_outlines,
)
from core.content_generation.chapter_outline_generation import (
    enhance_chapter_outlines as _enhance_chapter_outlines,
)
from core.content_generation.chapter_outline_generation import (
    generate_chapter_outline_27_method as _generate_chapter_outline_27_method,
)
from core.content_generation.chapter_outline_generation import (
    enhance_chapter_outlines_27_method as _enhance_chapter_outlines_27_method,
)
from core.content_generation.scene_outline_generation import (
    generate_scene_outlines as _generate_scene_outlines,
)
from core.content_generation.scene_outline_generation import (
    enhance_scene_outlines as _enhance_scene_outlines,
)
from core.content_generation.scene_part_generation import (
    generate_scene_part as _generate_scene_part,
)  # Import from scene_part_generation.py
from core.content_generation.scene_part_generation import (
    enhance_scene_part as _enhance_scene_part,
)  # Import from scene_part_generation.py
from core.content_generation.content_generation_utils import (
    PlotOutline,
    ChapterOutline,
    SceneOutline,
    ChapterOutlineMethod,
)

from llm.llm_client import OllamaClient
from utils.logger import logger  # ADDED LOGGER IMPORT HERE
import json
from core.book_spec import BookSpec


class ContentGenerator:
    """
    Orchestrates the content generation process for the novel,
    delegating specific tasks to submodule functions.
    """

    plot_outline = PlotOutline
    chapter_outline = ChapterOutline
    scene_outline = SceneOutline
    chapter_outline_method = ChapterOutlineMethod

    def __init__(self, prompt_manager, model_name):
        """
        Initializes the ContentGenerator with a prompt manager and model name.
        """
        self.prompt_manager = prompt_manager
        self.model_name = model_name
        self.ollama_client = OllamaClient()  # Initialize OllamaClient here
        logger.debug(f"ContentGenerator initializing with model_name: {model_name}")
        logger.debug("ContentGenerator.__init__ - OllamaClient initialized.")

    async def _validate_and_correct_json(
        self, generated_text: str, expected_schema: str
    ) -> str | None:
        """
        Helper function to validate and correct JSON output.
        """
        validation_prompt = (
            f"Please validate and, if necessary, correct the following JSON to ensure it's valid "
            f"and conforms to the following schema:\n```json\n{expected_schema}\n```\n"
            f"Input JSON:\n```json\n{generated_text}\n```\n\n"
            f"Ensure that the output contains only the corrected JSON, with no additional text or explanations. "
            f"If the input is already valid, return the original input JSON unchanged."
        )
        validated_text = await self.ollama_client.generate_text(
            self.model_name, validation_prompt
        )
        return validated_text

    async def generate_book_spec(self, idea: str) -> Optional[BookSpec]:
        """
        Generates a BookSpec object from a story idea using LLM.
        """
        ollama_client = self.ollama_client  # Use the instance client
        prompt_manager = self.prompt_manager
        try:
            generation_prompt_template = (
                prompt_manager.create_book_spec_generation_prompt()
            )
            variables = {
                "idea": idea,
            }

            generation_prompt = generation_prompt_template.format(**variables)

            generated_text = await ollama_client.generate_text(
                model_name=self.model_name,
                prompt=generation_prompt,
            )
            if not generated_text:
                logger.error("Failed to generate book specification.")
                return None

            # --- JSON Validation ---
            expected_schema = """
            {
                "title": "string",
                "genre": "string",
                "setting": "string",
                "themes": ["string", "string", ...],
                "tone": "string",
                "point_of_view": "string",
                "characters": ["string", "string", ...],
                "premise": "string"
            }
            """
            validated_text = await self._validate_and_correct_json(
                generated_text, expected_schema
            )
            if not validated_text:
                logger.error("Failed to validate/correct book specification JSON.")
                return None
            generated_text = validated_text  # Use the validated text
            # --- End JSON Validation ---

            try:
                book_spec_dict = json.loads(generated_text)
                book_spec = BookSpec(**book_spec_dict)
                logger.info("Book specification generated successfully.")
                return book_spec
            except (json.JSONDecodeError, ValidationError) as e:
                error_message = f"Error decoding or validating BookSpec: {e}"
                logger.error(error_message)
                logger.debug("Raw LLM response: %s", generated_text)
                return None

        except Exception as e:
            logger.error(f"Error generating book spec: {e}")
            return None

    async def enhance_book_spec(self, current_spec: BookSpec) -> Optional[BookSpec]:
        """
        Enhances an existing BookSpec object using critique and rewrite.
        """
        ollama_client = self.ollama_client  # Use instance client
        prompt_manager = self.prompt_manager
        try:
            # Define prompt templates for critique and rewrite
            critique_prompt_template = prompt_manager.create_book_spec_critique_prompt()
            rewrite_prompt_template = prompt_manager.create_book_spec_rewrite_prompt()

            # Prepare variables for the prompts
            variables = {
                "current_spec_json": current_spec.model_dump_json(indent=4),
            }

            critique_prompt_str = critique_prompt_template.format(**variables)

            # Generate actionable critique
            critique = await ollama_client.generate_text(
                model_name=self.model_name,
                prompt=critique_prompt_str,
            )

            if not critique:
                logger.error("Failed to generate critique for book specification.")
                return None

            # Rewrite content based on the critique
            rewrite_prompt_str = rewrite_prompt_template.format(
                **variables, critique=critique
            )
            enhanced_spec_json = await ollama_client.generate_text(
                model_name=self.model_name,
                prompt=rewrite_prompt_str,
            )

            if not enhanced_spec_json:
                logger.error("Failed to rewrite book specification.")
                return None

            # --- JSON Validation ---
            expected_schema = """
            {
                "title": "string",
                "genre": "string",
                "setting": "string",
                "themes": ["string", "string", ...],
                "tone": "string",
                "point_of_view": "string",
                "characters": ["string", "string", ...],
                "premise": "string"
            }
            """
            validated_text = await self._validate_and_correct_json(
                enhanced_spec_json, expected_schema
            )

            if not validated_text:
                logger.error(
                    "Failed to validate/correct enhanced book specification JSON."
                )
                return None
            enhanced_spec_json = validated_text  # Use validated JSON
            # --- End JSON Validation ---

            try:

                book_spec_dict = json.loads(enhanced_spec_json)
                enhanced_spec = BookSpec(**book_spec_dict)
                logger.info("Book specification enhanced successfully.")
                return enhanced_spec
            except (json.JSONDecodeError, ValidationError) as e:
                error_message = f"Error decoding or validating enhanced BookSpec: {e}"
                logger.error(error_message)
                logger.debug("Raw LLM response: %s", enhanced_spec_json)
                return None

        except Exception as e:
            logger.exception(
                "Exception occurred during book specification enhancement."
            )
            return None

    generate_plot_outline = _generate_plot_outline
    enhance_plot_outline = _enhance_plot_outline
    generate_chapter_outlines = _generate_chapter_outlines
    enhance_chapter_outlines = _enhance_chapter_outlines
    generate_chapter_outline_27_method = _generate_chapter_outline_27_method
    enhance_chapter_outlines_27_method = _enhance_chapter_outlines_27_method
    generate_scene_outlines = _generate_scene_outlines
    enhance_scene_outlines = _enhance_scene_outlines
    generate_scene_part = (
        _generate_scene_part  # Correctly assigned to imported function
    )
    enhance_scene_part = _enhance_scene_part  # Correctly assigned to imported function
