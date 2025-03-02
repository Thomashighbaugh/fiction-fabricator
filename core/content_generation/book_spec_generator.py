# /home/tlh/refactored_gui_fict_fab/core/content_generation/book_spec_generator.py
import json
from typing import Optional

from pydantic import ValidationError

from core.book_spec import BookSpec
from core.content_generation.base_generator import BaseContentGenerator
from llm.prompt_manager.prompt_manager import PromptManager
from utils.logger import logger


class BookSpecGenerator(BaseContentGenerator):
    """
    Content generator for BookSpec objects.
    """

    def __init__(self, prompt_manager, model_name: str):
        logger.debug("BookSpecGenerator.__init__ START")  # <-- ADDED LOGGING
        super().__init__(prompt_manager, model_name)
        self.prompts = prompt_manager
        logger.debug("prompt: %s...", self.prompts)
        logger.debug("BookSpecGenerator.__init__ END")  # <-- ADDED LOGGING

    async def generate(
        self, idea: str, project_name: str = "Untitled"
    ) -> Optional[BookSpec]:  # Add type hint for the return type
        """
        Generates a BookSpec based on a story idea.
        """
        logger.debug(
            f"Generating BookSpec with idea: {idea}, project_name: {project_name}"
        )  # Log input

        generation_prompt_template = self.prompts.get_prompt(
            "book_spec_generation_prompt"
        )
        logger.debug("generation_prompt_template: %s...", generation_prompt_template)

        variables = {"idea": idea, "project_name": project_name}
        logger.debug(
            f"Prompt variables: {variables}"
        )  # Log variables BEFORE formatting

        try:  # Add try-except around prompt formatting
            formatted_prompt = generation_prompt_template.format(
                **variables
            )  # Format prompt HERE
            logger.debug(
                f"Formatted prompt (first 200 chars): {formatted_prompt[:200]}..."
            )  # Log formatted prompt
        except KeyError as e:
            logger.error(
                f"KeyError during prompt formatting: {e}"
            )  # More specific error log
            logger.error(
                f"Prompt template: {generation_prompt_template}"
            )  # Log template on error
            logger.error(f"Variables: {variables}")  # Log variables on error
            return None  # Return None on formatting error

        generated_text = await self._generate_content_from_prompt(
            formatted_prompt,
            {},  # Use formatted_prompt, no need to pass variables again
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
            "premise": current_content.premise,
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
