# core/content_generation/book_spec_generation.py
from typing import Optional

import re
import tomli
import tomli_w

from core.book_spec import BookSpec
from llm.llm_client import OllamaClient
from llm.prompt_manager import PromptManager
from utils.logger import logger
from pydantic import ValidationError


async def generate_book_spec(content_generator, idea: str) -> Optional[BookSpec]:
    """
    Generates a BookSpec object from a story idea, expecting TOML output.
    """
    ollama_client = content_generator.ollama_client
    prompt_manager = content_generator.prompt_manager
    try:
        generation_prompt_template = (
            prompt_manager.create_book_spec_generation_prompt()
        )  # Will be updated in prompt_manager
        variables = {"idea": idea}
        generation_prompt = generation_prompt_template.format(**variables)

        generated_text = await ollama_client.generate_text(
            model_name=content_generator.model_name,
            prompt=generation_prompt,
        )
        if not generated_text:
            logger.error("Failed to generate book specification.")
            return None

        # --- TOML Validation and Correction ---
        expected_schema = """
title = "string"
genre = "string"
setting = "string"
themes = ["string", "string"]
tone = "string"
point_of_view = "string"
characters = [ { name = "string", description = "string"  } ] #example
premise = "string"
"""
        validated_text = await content_generator._validate_and_correct_toml(
            generated_text, expected_schema
        )  # New helper function
        if not validated_text:
            logger.error("TOML Validation Failed")
            return None
        generated_text = validated_text
        # --- End TOML Validation ---

        try:
            book_spec_dict = tomli.loads(generated_text)  # Use tomli.loads()
            book_spec = BookSpec(**book_spec_dict)
            logger.info("Book specification generated successfully.")
            return book_spec
        except (tomli.TOMLDecodeError, ValidationError) as e:
            error_message = f"Error decoding or validating BookSpec: {e}"
            logger.error(error_message)
            logger.debug("Raw LLM response: %s", generated_text)
            return None

    except Exception as e:
        logger.error(f"Error generating book spec: {e}")
        return None


async def enhance_book_spec(
    content_generator, current_spec: BookSpec
) -> Optional[BookSpec]:
    """
    Enhances a BookSpec, expecting TOML input and output.
    """
    ollama_client = content_generator.ollama_client
    prompt_manager = content_generator.prompt_manager
    try:
        critique_prompt_template = prompt_manager.create_book_spec_critique_prompt()
        rewrite_prompt_template = prompt_manager.create_book_spec_rewrite_prompt()

        variables = {
            "current_spec_toml": tomli_w.dumps(
                current_spec.model_dump()
            ),  # Convert to TOML
            "critique": "",  # Placeholder, will be filled in later
        }
        critique_prompt_str = critique_prompt_template.format(**variables)
        critique = await ollama_client.generate_text(
            model_name=content_generator.model_name, prompt=critique_prompt_str
        )

        if not critique:
            logger.error("Failed to generate critique")
            return None

        variables["critique"] = critique
        rewrite_prompt_str = rewrite_prompt_template.format(**variables)
        enhanced_spec_toml = await ollama_client.generate_text(
            model_name=content_generator.model_name, prompt=rewrite_prompt_str
        )
        if not enhanced_spec_toml:
            logger.error("Failed to generate enhanced book spec")
            return None
        # --- TOML Validation and Correction ---
        expected_schema = """
title = "string"
genre = "string"
setting = "string"
themes = ["string", "string"]
tone = "string"
point_of_view = "string"
characters = [ { name = "string", description = "string"  } ] #example
premise = "string"
"""

        validated_text = await content_generator._validate_and_correct_toml(
            enhanced_spec_toml, expected_schema
        )
        if not validated_text:
            logger.error("TOML Validation Failed")
            return None
        enhanced_spec_toml = validated_text
        # --- End TOML Validation ---

        try:
            book_spec_dict = tomli.loads(enhanced_spec_toml)
            enhanced_spec = BookSpec(**book_spec_dict)
            logger.info("Book specification enhanced successfully.")
            return enhanced_spec

        except (tomli.TOMLDecodeError, ValidationError) as e:
            logger.error(f"Error decoding/validating enhanced book spec: {e}")
            logger.debug(f"Raw TOML: {enhanced_spec_toml}")
            return None
    except Exception as e:
        logger.exception("Exception during book spec enhancement")
        return None