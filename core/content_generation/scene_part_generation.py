# core/content_generation/scene_part_generation.py
from typing import Optional
import tomli_w # Import tomli_w

from core.book_spec import BookSpec
from core.plot_outline import ChapterOutline, SceneOutline
from llm.llm_client import OllamaClient
from llm.prompt_manager import PromptManager
from utils.logger import logger


async def generate_scene_part(
    content_generator,
    scene_outline: SceneOutline,
    part_number: int,
    book_spec: BookSpec,
    chapter_outline: ChapterOutline,
    scene_outline_full: SceneOutline,
) -> Optional[str]:
    """
    Asynchronously generates a part of a scene's text content.
    """
    ollama_client = OllamaClient()
    prompt_manager = PromptManager()
    try:
        generation_prompt_template = (
            prompt_manager.create_scene_part_generation_prompt()
        )
        structure_check_prompt_template = (
            prompt_manager.create_scene_part_structure_check_prompt()
        )
        structure_fix_prompt_template = (
            prompt_manager.create_scene_part_structure_fix_prompt()
        )

        variables = {
            "scene_outline": scene_outline.summary,
            "part_number": str(part_number),
            "book_spec_toml": tomli_w.dumps(book_spec.model_dump()),  # Use TOML
            "chapter_outline": chapter_outline.summary,
            "scene_outline_full": scene_outline_full.summary,
        }

        generation_prompt = generation_prompt_template.format(**variables)

        generated_text = await ollama_client.generate_text(
            prompt=generation_prompt,
            model_name=content_generator.model_name,
        )

        if not generated_text:
            logger.error("Failed to generate scene part.")
            return None

        # Structure Check (Still checking for basic structure, not TOML)
        structure_check_variables = {"scene_part": generated_text}
        structure_check_prompt = structure_check_prompt_template.format(
            **structure_check_variables
        )
        structure_check_result = await ollama_client.generate_text(
            model_name=content_generator.model_name,
            prompt=structure_check_prompt,
        )

        if structure_check_result != "STRUCTURE_OK":
            logger.warning("Scene Part structure check failed. Attempting to fix...")
            # Structure Fix
            structure_fix_variables = {
                "scene_part": generated_text,
                "structure_problems": structure_check_result,
            }
            structure_fix_prompt = structure_fix_prompt_template.format(
                **structure_fix_variables
            )
            structure_fix_prompt_formatted = structure_fix_prompt.format(
                **structure_fix_variables
            )

            fixed_text = await ollama_client.generate_text(
                model_name=content_generator.model_name,
                prompt=structure_fix_prompt_formatted,
            )
            if fixed_text:
                generated_text = fixed_text
                logger.info("Scene Part structure fixed successfully.")
            else:
                logger.error("Failed to fix Scene Part structure.")
                return None

        logger.info("Scene part %d generated successfully.", part_number)
        return generated_text

    except Exception as e:
        logger.error("Error generating scene part %d: %s", part_number, e)
        return None


async def enhance_scene_part(
    content_generator,
    scene_part: str,
    part_number: int,
    book_spec: BookSpec,
    chapter_outline: ChapterOutline,
    scene_outline_full: SceneOutline,
) -> Optional[str]:
    """
    Asynchronously enhances an existing scene part's text content.
    """
    ollama_client = OllamaClient()
    prompt_manager = PromptManager()
    try:
        # Get prompt templates from PromptManager
        critique_prompt_template = prompt_manager.create_scene_part_critique_prompt()
        rewrite_prompt_template = prompt_manager.create_scene_part_rewrite_prompt()

        # Prepare variables for the prompts
        variables = {
            "book_spec_toml": tomli_w.dumps(book_spec.model_dump()),  # Use TOML
            "chapter_outline": chapter_outline.summary,
            "scene_outline_full": scene_outline_full.summary,
            "part_number": str(part_number),
        }

        critique_prompt_str = critique_prompt_template.format(**variables)

        # Generate actionable critique
        critique = await ollama_client.generate_text(
            model_name=content_generator.model_name,
            prompt=critique_prompt_str,
        )

        if critique:
            rewrite_prompt_str = rewrite_prompt_template.format(
                **variables, critique=critique, content=scene_part
            )
            # Rewrite content based on the critique
            enhanced_scene_part = await ollama_client.generate_text(
                prompt=rewrite_prompt_str,
                model_name=content_generator.model_name,
            )

            if enhanced_scene_part:
                logger.info("Scene part %d enhanced successfully.", part_number)
                return enhanced_scene_part
            else:
                logger.error("Failed to rewrite scene part %d.", part_number)
                return None

        else:
            logger.error("Failed to generate critique for scene part %d.", part_number)
            return None
    except Exception as e:
        logger.error("Error enhancing scene part %d: %s", part_number, e)
        return None