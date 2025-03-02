# core/content_generation/book_spec_generator.py
import json
from typing import Optional

from pydantic import ValidationError

from core.book_spec import BookSpec
from core.content_generation.base_generator import BaseContentGenerator
from llm.prompt_manager.prompt_manager import DynamicPromptManager # type: ignore
from utils.logger import logger


class BookSpecGenerator(BaseContentGenerator):
    """
    Content generator for BookSpec objects.

    Inherits from BaseContentGenerator and implements specific logic
    for generating and enhancing BookSpec content.
    """

    def __init__(self, prompt_manager, model_name: str):
        """
        Initializes BookSpecGenerator with prompt manager and model name.
        """
        super().__init__(prompt_manager, model_name)
        self.prompts = prompt_manager
        logger.debug("prompt: %s...", self.prompts)

    async def generate(
        self, idea: str, project_name: str = "Untitled"
    ) -> Optional[BookSpec]:  # Add type hint for the return type
        """
        Generates a BookSpec based on a story idea.

        Args:
            idea (str): The initial story idea to generate a BookSpec from.
            project_name (str): The name of the project, used as a default title.

        Returns:
            Optional[BookSpec]: The generated BookSpec object, or None if generation fails.
        """
        logger.debug(f"Generating BookSpec with idea: {idea}")
        generation_prompt_template = self.prompts.get_prompt("book_spec_generation_prompt")
        logger.debug("generation_prompt_template: %s...", generation_prompt_template)
        variables = {"idea": idea, "project_name": project_name}
        generated_text = await self._generate_content_from_prompt(
            generation_prompt_template, variables
        )
        if not generated_text:
            logger.error("Initial content generation failed.")
            return None


        book_spec = self._parse_response(generated_text)
        if not book_spec:
             logger.error("Parsing failed.")
             return None

        logger.debug("Parsing successful.  Returning BookSpec.")
        return book_spec

    async def enhance(
        self, current_content: BookSpec, enhance_target: str
    ) -> Optional[BookSpec]:  # Renamed parameter to current_content
        """
        Enhances an existing BookSpec object.
        """
        critique_prompt_template = self.prompts.get_prompt("book_spec_critique_prompt")
        rewrite_prompt_template = self.prompts.get_prompt("book_spec_rewrite_prompt")
        variables = {
            "title": current_content.title,
            "genre": current_content.genre,
            "setting": current_content.setting,
            "themes": ", ".join(current_content.themes),
            "tone": current_content.tone,
            "point_of_view": current_content.point_of_view,
            "characters": ", ".join(current_content.characters),
            "premise": current_content.premise
        }  # Now using current_content

        critique_text = await self._generate_content_from_prompt(
            critique_prompt_template, variables
        )
        if not critique_text:
            return None

        rewrite_variables = {**variables, "critique": critique_text}
        enhanced_spec_json = await self._generate_content_from_prompt(
            rewrite_prompt_template, rewrite_variables
        )
        if not enhanced_spec_json:
            return None

        return self._parse_response(enhanced_spec_json)

    def _parse_response(self, response_text: str) -> Optional[BookSpec]:
        """
        Parses the JSON response from the LLM and validates it against the BookSpec model.
        """
        try:
            book_spec_data = json.loads(response_text)
            return BookSpec(**book_spec_data)
        except json.JSONDecodeError as e:
            logger.error("JSONDecodeError: %s", e)  # Lazy format
            logger.debug("Problematic JSON string: %s", response_text)  # Lazy format
            return None
        except ValidationError as e:
            logger.error("ValidationError: %s", e)  # Lazy format
            logger.debug(
                "Problematic JSON data: %s",
                (
                    book_spec_data
                    if "book_spec_data" in locals()
                    else "JSON data not parsed"
                ),
            )  # Lazy format
            return None
        except (
            ValueError,
            TypeError,
            RuntimeError,
        ) as e:  # Catch specific operational errors
            logger.error(
                "Operational error during parsing BookSpec JSON: %s", e
            )  # Lazy format
            logger.exception(e)  # Log full exception details
            return None