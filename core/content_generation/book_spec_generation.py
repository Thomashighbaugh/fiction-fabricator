# core/content_generation/book_spec_generation.py
from typing import Optional

import json
import re

from core.book_spec import BookSpec
from llm.llm_client import OllamaClient
from llm.prompt_manager import PromptManager
from utils.logger import logger
from pydantic import ValidationError


async def generate_book_spec(content_generator, idea: str) -> Optional[BookSpec]:
    """
    Generates a BookSpec object from a story idea using LLM.
    """
    ollama_client = OllamaClient()
    prompt_manager = PromptManager()
    try:
        generation_prompt_template = prompt_manager.create_book_spec_generation_prompt()
        structure_check_prompt_template = (
            prompt_manager.create_book_spec_structure_check_prompt()
        )
        structure_fix_prompt_template = (
            prompt_manager.create_book_spec_structure_fix_prompt()
        )

        variables = {
            "idea": idea,
        }

        generation_prompt = generation_prompt_template.format(**variables)

        generated_text = await ollama_client.generate_text(
            model_name=content_generator.model_name,
            prompt=generation_prompt,
        )
        if not generated_text:
            logger.error("Failed to generate book specification.")
            return None

        # Structure Check
        structure_check_variables = {"book_spec_json": generated_text}
        structure_check_prompt = structure_check_prompt_template.format(
            **structure_check_variables
        )

        structure_check_result = await ollama_client.generate_text(
            model_name=content_generator.model_name,
            prompt=structure_check_prompt,
        )
        if structure_check_result != "STRUCTURE_OK":
            logger.warning("BookSpec structure check failed. Attempting to fix...")
            structure_fix_variables = {
                "book_spec_json": generated_text,
                "structure_problems": structure_check_result,
            }
            structure_fix_prompt = structure_fix_prompt_template.format(
                **structure_fix_variables
            )
            fixed_text = await ollama_client.generate_text(
                model_name=content_generator.model_name,
                prompt=structure_fix_prompt,
            )
            if fixed_text:
                generated_text = fixed_text
                logger.info("BookSpec structure fixed successfully.")
            else:
                logger.error("Failed to fix BookSpec structure.")
                return None

        try:
            # Enhanced JSON cleaning: Remove markdown delimiters and common issues
            generated_text = generated_text.strip()
            if generated_text.startswith("```json") and generated_text.endswith("```"):
                generated_text = generated_text[7:-3].strip()
            if generated_text.startswith("```") and generated_text.endswith("```"):
                generated_text = generated_text[
                    3:-3
                ].strip()  # strip generic code block
            generated_text = re.sub(
                r"^.*?\{", "{", generated_text, flags=re.DOTALL
            )  # Remove leading text before JSON
            generated_text = re.sub(
                r"\}[^\}]*$", "}", generated_text, flags=re.DOTALL
            )  # Remove trailing text after JSON
            generated_text = re.sub(
                r']\s*"premise":', '], "premise":', generated_text
            )  # Fix missing comma before "premise"
            generated_text = generated_text.replace(
                "\\\n", "\n"
            )  # Handle escaped newlines
            generated_text = generated_text.replace('\\"', '"')  # Handle escaped quotes
            generated_text = re.sub(
                r'""([^"]+)""', r'"\1"', generated_text
            )  # Remove extra double quotes

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


async def enhance_book_spec(
    content_generator, current_spec: BookSpec
) -> Optional[BookSpec]:
    """
    Enhances an existing BookSpec object using critique and rewrite.
    """
    ollama_client = OllamaClient()
    prompt_manager = PromptManager()
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
            model_name=content_generator.model_name,
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
            model_name=content_generator.model_name,
            prompt=rewrite_prompt_str,
        )

        if not enhanced_spec_json:
            logger.error("Failed to rewrite book specification.")
            return None

        try:
            # Enhanced JSON cleaning: Remove markdown delimiters and common issues
            enhanced_spec_json = enhanced_spec_json.strip()
            if enhanced_spec_json.startswith("```json") and enhanced_spec_json.endswith(
                "```"
            ):
                enhanced_spec_json = enhanced_spec_json[7:-3].strip()
            if enhanced_spec_json.startswith("```") and enhanced_spec_json.endswith(
                "```"
            ):
                enhanced_spec_json = enhanced_spec_json[
                    3:-3
                ].strip()  # strip generic code block
            enhanced_spec_json = re.sub(
                r"^.*?\{", "{", enhanced_spec_json, flags=re.DOTALL
            )  # Remove leading text before JSON
            enhanced_spec_json = re.sub(
                r"\}[^\}]*$", "}", enhanced_spec_json, flags=re.DOTALL
            )  # Remove trailing text after JSON
            enhanced_spec_json = re.sub(
                r']\s*"premise":', '], "premise":', enhanced_spec_json
            )  # Fix missing comma before "premise"
            enhanced_spec_json = enhanced_spec_json.replace(
                "\\\n", "\n"
            )  # Handle escaped newlines
            enhanced_spec_json = enhanced_spec_json.replace(
                '\\"', '"'
            )  # Handle escaped quotes
            enhanced_spec_json = re.sub(
                r'""([^"]+)""', r'"\1"', enhanced_spec_json
            )  # Remove extra double quotes

            book_spec_dict = json.loads(enhanced_spec_json)
            enhanced_spec = BookSpec(**book_spec_dict)
            logger.info("Book specification enhanced successfully.")
            return enhanced_spec
        except (json.JSONDecodeError, ValidationError) as e:
            error_message = f"Error decoding or validating enhanced BookSpec: {e}"
            logger.error(error_message)
            logger.debug("Raw LLM response: %s", enhanced_spec_json)
            logger.debug(
                f"Raw LLM response before cleaning: %s", enhanced_spec_json
            )  # Added raw response logging

            return None

    except Exception as e:
        logger.exception("Exception occurred during book specification enhancement.")
        return None

