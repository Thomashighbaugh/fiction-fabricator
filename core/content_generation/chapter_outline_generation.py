# core/content_generation/chapter_outline_generation.py
from typing import Optional, List

import tomli  # Import tomli
import tomli_w

from core.book_spec import BookSpec
from llm.llm_client import OllamaClient
from llm.prompt_manager import PromptManager
from utils.logger import logger
from .content_generation_utils import (
    ChapterOutline,
    ChapterOutlineMethod,
    PlotOutline,
)


async def generate_chapter_outlines(
    content_generator, plot_outline: PlotOutline
) -> Optional[List[ChapterOutline]]:
    """
    Generates chapter outlines based on a PlotOutline. Now requests and parses TOML.
    """
    ollama_client = OllamaClient()
    prompt_manager = PromptManager()
    try:
        generation_prompt_template = (
            prompt_manager.create_chapter_outlines_generation_prompt()
        )
        # Convert PlotOutline to TOML for the prompt
        plot_outline_toml = tomli_w.dumps(plot_outline.model_dump_toml())

        variables = {
            "plot_outline_toml": plot_outline_toml,  # Pass TOML to prompt
            "num_chapters": "27",  # default
        }

        generation_prompt = generation_prompt_template.format(**variables)
        logger.debug(f"generate_chapter_outlines - PROMPT: {generation_prompt}")

        generated_text = await ollama_client.generate_text(
            model_name=content_generator.model_name,
            prompt=generation_prompt,
        )

        if not generated_text:
            logger.error("Failed to generate chapter outlines.")
            return None

        logger.debug(f"Raw LLM Chapter Outline Response: {generated_text}")

        # --- Critique and Rewrite ---
        critique_prompt_template = prompt_manager.create_chapter_outlines_critique_prompt()
        rewrite_prompt_template = prompt_manager.create_chapter_outlines_rewrite_prompt()

        critique_variables = {
            "current_outlines_toml": generated_text
        }
        critique_prompt = critique_prompt_template.format(**critique_variables)
        critique = await ollama_client.generate_text(
            model_name=content_generator.model_name,
            prompt=critique_prompt
        )

        if critique:
            rewrite_variables = {
                "current_outlines_toml": generated_text,
                "critique": critique
            }
            rewrite_prompt = rewrite_prompt_template.format(**rewrite_variables)
            generated_text = await ollama_client.generate_text(
                model_name=content_generator.model_name,
                prompt=rewrite_prompt
            )
            if not generated_text:
                logger.error("Failed to rewrite chapter outlines after critique.")
                return None
        else:
            logger.warning("No critique generated; proceeding with original output.")

        # --- TOML Validation and Correction ---
        expected_schema = """
        chapters = [
            {chapter_number = 1, summary = "string"},
            {chapter_number = 2, summary = "string"},
            # ... more chapters
        ]
        """
        validated_text = await content_generator._validate_and_correct_toml(
            generated_text, expected_schema
        )
        if not validated_text:
            logger.error("TOML Validation Failed")
            return None
        generated_text = validated_text
        # --- End TOML Validation ---

        try:
            # Parse the TOML
            chapter_data = tomli.loads(generated_text)
            chapter_outlines = []
            for chapter_info in chapter_data.get("chapters", []):
                chapter_outlines.append(
                    ChapterOutline(
                        chapter_number=chapter_info["chapter_number"],
                        summary=chapter_info["summary"],
                    )
                )
            logger.info(
                f"{len(chapter_outlines)} chapter outlines generated successfully."
            )
            return chapter_outlines

        except (tomli.TOMLDecodeError, KeyError, TypeError) as e:
            logger.error(f"Error processing ChapterOutline responses: {e}")
            logger.debug("Raw LLM response: %s", generated_text)
            return None

    except Exception as e:
        logger.error(f"Error generating chapter outlines: {e}")
        return None


async def enhance_chapter_outlines(
    content_generator, current_outlines: List[ChapterOutline]
) -> Optional[List[ChapterOutline]]:
    """
    Enhances existing chapter outlines.  Now uses TOML.
    """
    ollama_client = OllamaClient()
    prompt_manager = PromptManager()
    try:
        # Convert ChapterOutline objects to TOML
        outlines_dict = {"chapters": [co.model_dump_toml() for co in current_outlines]}
        current_outlines_toml = tomli_w.dumps(outlines_dict)

        # Define prompt templates for critique and rewrite
        critique_prompt_template = (
            prompt_manager.create_chapter_outlines_critique_prompt()
        )
        rewrite_prompt_template = (
            prompt_manager.create_chapter_outlines_rewrite_prompt()
        )

        # Prepare variables for the prompts
        variables = {
            "current_outlines_toml": current_outlines_toml,  # Pass TOML
        }

        critique_prompt_str = critique_prompt_template.format(**variables)

        # Generate actionable critique
        critique = await ollama_client.generate_text(
            model_name=content_generator.model_name,
            prompt=critique_prompt_str,
        )
        if not critique:
            logger.error("Failed to generate critique for chapter outlines.")
            return None

        rewrite_prompt_str = rewrite_prompt_template.format(
            **variables,
            critique=critique,
            current_outlines_toml=current_outlines_toml,  # Pass TOML
        )
        # Rewrite content based on the critique
        enhanced_outlines_toml = await ollama_client.generate_text(
            prompt=rewrite_prompt_str,
            model_name=content_generator.model_name,
        )

        if not enhanced_outlines_toml:
            logger.error("Failed to generate enhanced chapter outlines")
            return None

        # --- TOML Validation and Correction ---
        expected_schema = """
        chapters = [
            {chapter_number = 1, summary = "string"},
            {chapter_number = 2, summary = "string"},
            # ... more chapters
        ]
        """
        validated_text = await content_generator._validate_and_correct_toml(
            enhanced_outlines_toml, expected_schema
        )
        if not validated_text:
            logger.error("TOML Validation Failed")
            return None
        enhanced_outlines_toml = validated_text
        # --- End TOML Validation ---

        try:
            enhanced_chapter_data = tomli.loads(enhanced_outlines_toml)
            enhanced_chapter_outlines = []
            for chapter_info in enhanced_chapter_data.get("chapters", []):
                enhanced_chapter_outlines.append(
                    ChapterOutline(
                        chapter_number=chapter_info["chapter_number"],
                        summary=chapter_info["summary"],
                    )
                )
            logger.info("Chapter outlines enhanced successfully.")
            return enhanced_chapter_outlines
        except (tomli.TOMLDecodeError, KeyError, TypeError) as e:
            logger.error(f"Error processing enhanced ChapterOutline responses: {e}")
            logger.debug("Raw LLM response: %s", enhanced_outlines_toml)
            return None

    except Exception as e:
        logger.error(f"Error enhancing chapter outlines: {e}")
        return None


async def generate_chapter_outline_27_method(
    content_generator, book_spec: BookSpec
) -> Optional[List[ChapterOutlineMethod]]:
    """
    Generates 27 chapter outlines (27-chapter method). Requests TOML output.
    """
    ollama_client = OllamaClient()
    prompt_manager = PromptManager()
    try:
        generation_prompt_template = (
            prompt_manager.create_chapter_outline_27_method_generation_prompt()
        )
        # Convert book_spec to TOML
        book_spec_toml = tomli_w.dumps(book_spec.model_dump_toml())

        variables = {
            "book_spec_toml": book_spec_toml,  # Use TOML in prompt
            "methodology_markdown": prompt_manager.methodology_markdown,
        }
        generation_prompt = generation_prompt_template.format(**variables)
        logger.debug(
            f"generate_chapter_outline_27_method - PROMPT: {generation_prompt}"
        )

        generated_text = await ollama_client.generate_text(
            model_name=content_generator.model_name,
            prompt=generation_prompt,
        )

        if not generated_text:
            logger.error("Failed to generate 27 chapter outlines.")
            return None

        logger.debug(f"Raw LLM Chapter Outline 27 Method Response: {generated_text}")


        # --- Critique and Rewrite ---
        critique_prompt_template = prompt_manager.create_chapter_outline_27_method_critique_prompt()
        rewrite_prompt_template = prompt_manager.create_chapter_outline_27_method_rewrite_prompt()

        critique_variables = {
            "current_outlines_toml" : generated_text
        }
        critique_prompt = critique_prompt_template.format(**critique_variables)
        critique = await ollama_client.generate_text(
            model_name=content_generator.model_name,
            prompt=critique_prompt
        )
        if critique:
            rewrite_variables = {
                "current_outlines_toml": generated_text,
                "critique": critique
            }
            rewrite_prompt = rewrite_prompt_template.format(**rewrite_variables)
            generated_text = await ollama_client.generate_text(
                model_name=content_generator.model_name,
                prompt=rewrite_prompt
            )
            if not generated_text:
                logger.error("Failed to rewrite 27 chapter outlines after critique")
                return None
        else:
            logger.warning("No critique generated; proceeding with original output.")

        # --- TOML Validation and Correction ---
        expected_schema = """
        chapters = [
            {chapter_number = 1, role = "string", summary = "string"},
            {chapter_number = 2, role = "string", summary = "string"},
            # ... more chapters
        ]
        """
        validated_text = await content_generator._validate_and_correct_toml(
            generated_text, expected_schema
        )
        if not validated_text:
            logger.error("TOML Validation Failed")
            return None
        generated_text = validated_text
        # --- End TOML Validation ---

        try:
            # Parse the TOML
            chapter_data = tomli.loads(generated_text)
            chapter_outlines_27_method = []
            for chapter_info in chapter_data.get("chapters", []):
                chapter_outlines_27_method.append(
                    ChapterOutlineMethod(
                        chapter_number=chapter_info["chapter_number"],
                        role=chapter_info["role"],
                        summary=chapter_info["summary"],
                    )
                )
            logger.info(
                "%d chapter outlines (27 method) generated successfully.",
                len(chapter_outlines_27_method),
            )
            return chapter_outlines_27_method

        except (tomli.TOMLDecodeError, KeyError, TypeError) as e:
            logger.error(
                f"Error processing ChapterOutlineMethod responses: {e}, {chapter_data}"
            )
            logger.debug("Raw LLM response: %s", generated_text)
            return None

    except Exception as e:
        logger.error(f"Error generating 27 chapter outlines: {e}")
        return None


async def enhance_chapter_outlines_27_method(
    content_generator, current_outlines: List[ChapterOutlineMethod]
) -> Optional[List[ChapterOutlineMethod]]:
    """
    Enhances existing 27 chapter outlines (27-chapter method). Uses TOML.
    """
    ollama_client = OllamaClient()
    prompt_manager = PromptManager()
    try:
        # Convert ChapterOutlineMethod objects to TOML
        outlines_dict = {"chapters": [co.model_dump_toml() for co in current_outlines]}
        current_outlines_toml = tomli_w.dumps(outlines_dict)

        # Define prompt templates for critique and rewrite
        critique_prompt_template = (
            prompt_manager.create_chapter_outline_27_method_critique_prompt()
        )
        rewrite_prompt_template = (
            prompt_manager.create_chapter_outline_27_method_rewrite_prompt()
        )

        # Prepare variables for the prompts
        variables = {
            "current_outlines_toml": current_outlines_toml,  # Pass TOML
        }

        critique_prompt_str = critique_prompt_template.format(**variables)

        # Generate actionable critique
        critique = await ollama_client.generate_text(
            model_name=content_generator.model_name,
            prompt=critique_prompt_str,
        )

        if critique:
            rewrite_prompt_str = rewrite_prompt_template.format(
                **variables,
                critique=critique,
                current_outlines_toml=current_outlines_toml,  # Pass TOML
            )
            # Rewrite content based on the critique
            enhanced_outlines_toml = await ollama_client.generate_text(
                prompt=rewrite_prompt_str,
                model_name=content_generator.model_name,
            )

            if not enhanced_outlines_toml:
                logger.error("Failed to enhance chapter outlines")
                return None

            # --- TOML Validation and Correction ---
            expected_schema = """
            chapters = [
                {chapter_number = 1, role = "string", summary = "string"},
                {chapter_number = 2, role = "string", summary = "string"},
                # ... more chapters
            ]
            """
            validated_text = await content_generator._validate_and_correct_toml(
                enhanced_outlines_toml, expected_schema
            )
            if not validated_text:
                logger.error("TOML Validation Failed")
                return None
            enhanced_outlines_toml = validated_text
            # --- End TOML Validation ---

            try:
                # Parse TOML
                enhanced_chapter_data = tomli.loads(enhanced_outlines_toml)
                enhanced_chapter_outlines_27_method = []

                for chapter_info in enhanced_chapter_data.get("chapters", []):
                    enhanced_chapter_outlines_27_method.append(
                        ChapterOutlineMethod(
                            chapter_number=chapter_info["chapter_number"],
                            role=chapter_info["role"],
                            summary=chapter_info["summary"],
                        )
                    )
                logger.info("Chapter outlines (27 method) enhanced successfully.")
                return enhanced_chapter_outlines_27_method
            except (tomli.TOMLDecodeError, KeyError, TypeError) as e:
                logger.error(
                    "Error processing enhanced ChapterOutlineMethod responses: %s", e
                )
                logger.debug("Raw LLM response: %s", enhanced_outlines_toml)
                return None
        else:
            logger.error(
                "Failed to generate critique for chapter outlines (27 method)."
            )
            return None
    except Exception as e:
        logger.exception("Exception occurred during chapter outlines enhancement.")
        return None