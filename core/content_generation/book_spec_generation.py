# core/content_generation/book_spec_generation.py
from typing import Optional, List, Dict

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
        generation_prompt_template = prompt_manager.create_book_spec_generation_prompt()
        generation_prompt = generation_prompt_template()  # Get the template
        generation_prompt = generation_prompt.replace(
            "{idea}", idea
        )  # Manually replace {idea}

        logger.debug(f"generate_book_spec: Formatted Prompt:\n{generation_prompt}")

        generated_text = await ollama_client.generate_text(
            model_name=content_generator.model_name,
            prompt=generation_prompt,
        )
        if not generated_text:
            logger.error("Failed to generate book specification. (Empty response)")
            return None

        logger.debug(f"generate_book_spec: Raw LLM response:\n{generated_text}")

        # --- TOML Validation and Correction ---
        validated_text = await content_generator._validate_and_correct_toml(
            generated_text,
            """
title = "string"
genre = "string"
setting = "string"
themes = ["string"]
tone = "string"
point_of_view = "string"
characters = ["string"]
premise = "string"
""",
        )
        if not validated_text:
            logger.error("TOML Validation Failed after multiple attempts.")
            return None
        logger.debug(f"generate_book_spec: Validated TOML:\n{validated_text}")

        # --- End TOML Validation ---

        try:
            logger.debug(
                f"generate_book_spec: Attempting to parse TOML:\n{validated_text}"
            )
            book_spec_dict = tomli.loads(validated_text)
            logger.debug(
                f"generate_book_spec: Parsed TOML Dictionary:\n{book_spec_dict}"
            )
            # Transform character data:
            if "characters" in book_spec_dict and isinstance(
                book_spec_dict["characters"], list
            ):
                book_spec_dict["characters"] = [
                    f"{char['name']}: {char['description']}"
                    for char in book_spec_dict["characters"]
                    if isinstance(char, dict)
                    and "name" in char
                    and "description" in char
                ]

            # --- Data Transformation ---

            if "themes" in book_spec_dict and isinstance(book_spec_dict["themes"], str):
                book_spec_dict["themes"] = [book_spec_dict["themes"]]
            elif "themes" not in book_spec_dict:
                book_spec_dict["themes"] = []  # Handle missing themes
                logger.warning(
                    "No themes found in generated TOML, defaulting to empty list."
                )

            book_spec = BookSpec(**book_spec_dict)
            logger.info("Book specification generated successfully.")
            return book_spec

        except tomli.TOMLDecodeError as e:
            logger.error(f"Error decoding TOML: {e}")
            logger.debug(f"Problematic TOML:\n{validated_text}")  # Log validated text
            return None
        except ValidationError as e:
            logger.error(f"Pydantic validation error: {e}")
            logger.debug(f"Book spec dictionary: {book_spec_dict}")
            return None
        except Exception as e:  # catch any other exception
            logger.exception(f"Unexpected error during BookSpec creation: {e}")
            return None

    except Exception as e:
        logger.exception(f"Error generating book spec: {e}")
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
        logger.debug(
            f"enhance_book_spec: Critique Prompt Template:\n{critique_prompt_template}"
        )
        logger.debug(
            f"enhance_book_spec: Rewrite Prompt Template:\n{rewrite_prompt_template}"
        )

        variables = {
            "current_spec_toml": tomli_w.dumps(
                current_spec.model_dump()
            ),  # Convert to TOML
            "critique": "",  # Placeholder, will be filled in later
        }
        critique_prompt_str = critique_prompt_template(
            **variables
        )  # Get template, THEN call.
        logger.debug(
            f"enhance_book_spec: Formatted Critique Prompt:\n{critique_prompt_str}"
        )

        critique = await ollama_client.generate_text(
            model_name=content_generator.model_name, prompt=critique_prompt_str
        )

        if not critique:
            logger.error("Failed to generate critique")
            return None

        logger.debug(f"enhance_book_spec: Critique from LLM:\n{critique}")

        variables["critique"] = critique
        rewrite_prompt_str = rewrite_prompt_template(
            **variables
        )  # Get template, THEN call.
        logger.debug(
            f"enhance_book_spec: Formatted Rewrite Prompt:\n{rewrite_prompt_str}"
        )

        enhanced_spec_toml = await ollama_client.generate_text(
            model_name=content_generator.model_name, prompt=rewrite_prompt_str
        )
        if not enhanced_spec_toml:
            logger.error("Failed to generate enhanced book spec")
            return None

        logger.debug(
            f"enhance_book_spec: Raw Enhanced Spec TOML from LLM:\n{enhanced_spec_toml}"
        )

        # --- TOML Validation and Correction ---
        validated_text = await content_generator._validate_and_correct_toml(
            enhanced_spec_toml,
            """
title = "string"
genre = "string"
setting = "string"
themes = ["string"]
tone = "string"
point_of_view = "string"
characters = ["string"]
premise = "string"
""",
        )
        if not validated_text:
            logger.error("TOML Validation Failed")
            return None

        logger.debug(
            f"enhance_book_spec: Validated Enhanced Spec TOML:\n{validated_text}"
        )

        # --- End TOML Validation ---

        try:
            logger.debug(
                f"enhance_book_spec: Attempting to parse TOML:\n{validated_text}"
            )
            book_spec_dict = tomli.loads(validated_text)
            logger.debug(
                f"enhance_book_spec: Parsed Enhanced Spec Dictionary:\n{book_spec_dict}"
            )

            # Transform character data:
            if "characters" in book_spec_dict and isinstance(
                book_spec_dict["characters"], list
            ):
                book_spec_dict["characters"] = [
                    f"{char['name']}: {char['description']}"
                    for char in book_spec_dict["characters"]
                    if isinstance(char, dict)
                    and "name" in char
                    and "description" in char
                ]

            # --- Data Transformation (as in generate_book_spec)---

            # Ensure themes is a list
            if "themes" in book_spec_dict and isinstance(book_spec_dict["themes"], str):
                book_spec_dict["themes"] = [book_spec_dict["themes"]]
            elif "themes" not in book_spec_dict:  # Handle missing
                book_spec_dict["themes"] = []
                logger.warning(
                    "No themes found in enhanced TOML, defaulting to empty list."
                )

            enhanced_spec = BookSpec(**book_spec_dict)
            logger.info("Book specification enhanced successfully.")
            return enhanced_spec

        except (tomli.TOMLDecodeError, ValidationError) as e:
            logger.error(f"Error decoding/validating enhanced book spec: {e}")
            logger.debug(f"Raw TOML: {enhanced_spec_toml}")
            return None
        except Exception as e:  # catch any other exceptions
            logger.exception(f"Unexpected error during enhanced BookSpec creation: {e}")
            return None
    except Exception as e:
        logger.exception("Exception during book spec enhancement")
        return None
