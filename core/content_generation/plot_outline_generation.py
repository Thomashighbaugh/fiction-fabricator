# core/content_generation/plot_outline_generation.py
from typing import Optional

import re

from core.book_spec import BookSpec
from llm.llm_client import OllamaClient
from llm.prompt_manager import PromptManager
from utils.logger import logger
from .content_generation_utils import PlotOutline  # Import PlotOutline model


async def generate_plot_outline(content_generator, book_spec: BookSpec) -> Optional[PlotOutline]:
    """
    Generates a PlotOutline object based on a BookSpec.
    """
    ollama_client = OllamaClient()
    prompt_manager = PromptManager()
    try:
        generation_prompt_template = prompt_manager.create_plot_outline_generation_prompt()
        logger.debug("generate_plot_outline - Generation prompt template loaded.")

        variables = {
            "book_spec_json": book_spec.model_dump_json(indent=4),
        }
        full_prompt = generation_prompt_template.format(**variables)
        logger.debug("generate_plot_outline - Generation prompt formatted.")
        logger.debug(
            f"generate_plot_outline - Full generation prompt: %s", full_prompt
        )

        logger.debug("generate_plot_outline - Sending prompt to OllamaClient...")
        generated_text = await ollama_client.generate_text(
            model_name=content_generator.model_name,
            prompt=full_prompt,
        )

        if not generated_text:
            logger.error("Failed to generate plot outline.")
            return None

        logger.debug(f"Raw LLM Plot Outline Response: {generated_text}")

        try:
            logger.debug("generate_plot_outline - Attempting to parse PlotOutline.")
            plot_outline = PlotOutline(
                act_one_block_one=[],
                act_one_block_two=[],
                act_one_block_three=[],
                act_two_block_one=[],
                act_two_block_two=[],
                act_two_block_three=[],
                act_three_block_one=[],
                act_three_block_two=[],
                act_three_block_three=[],
            )  # Initialize acts and blocks

            acts_text = generated_text.split("Act ")
            if len(acts_text) >= 4:
                # Act 1
                act_one_blocks = acts_text[1].split("BLOCK")
                if len(act_one_blocks) == 4:  # Expecting 3 blocks + intro text
                    plot_outline.act_one_block_one = [
                        p.strip()
                        for p in act_one_blocks[1].split("\n")
                        if p.strip()
                        and not p.strip().startswith(
                            ("#", "*", "##", "Plot Outline", "Act", ":")
                        )
                    ]
                    plot_outline.act_one_block_two = [
                        p.strip()
                        for p in act_one_blocks[2].split("\n")
                        if p.strip()
                        and not p.strip().startswith(
                            ("#", "*", "##", "Plot Outline", "Act", ":")
                        )
                    ]
                    plot_outline.act_one_block_three = [
                        p.strip()
                        for p in act_one_blocks[3].split("\n")
                        if p.strip()
                        and not p.strip().startswith(
                            ("#", "*", "##", "Plot Outline", "Act", ":")
                        )
                    ]
                # Act 2
                act_two_blocks = acts_text[2].split("BLOCK")
                if len(act_two_blocks) == 4:  # Expecting 3 blocks + intro text
                    plot_outline.act_two_block_one = [
                        p.strip()
                        for p in act_two_blocks[1].split("\n")
                        if p.strip()
                        and not p.strip().startswith(
                            ("#", "*", "##", "Plot Outline", "Act", ":")
                        )
                    ]
                    plot_outline.act_two_block_two = [
                        p.strip()
                        for p in act_two_blocks[2].split("\n")
                        if p.strip()
                        and not p.strip().startswith(
                            ("#", "*", "##", "Plot Outline", "Act", ":")
                        )
                    ]
                    plot_outline.act_two_block_three = [
                        p.strip()
                        for p in act_two_blocks[3].split("\n")
                        if p.strip()
                        and not p.strip().startswith(
                            ("#", "*", "##", "Plot Outline", "Act", ":")
                        )
                    ]
                # Act 3
                act_three_blocks = acts_text[3].split("BLOCK")
                if len(act_three_blocks) == 4:  # Expecting 3 blocks + intro text
                    plot_outline.act_three_block_one = [
                        p.strip()
                        for p in act_three_blocks[1].split("\n")
                        if p.strip()
                        and not p.strip().startswith(
                            ("#", "*", "##", "Plot Outline", "Act", ":")
                        )
                    ]
                    plot_outline.act_three_block_two = [
                        p.strip()
                        for p in act_three_blocks[2].split("\n")
                        if p.strip()
                        and not p.strip().startswith(
                            ("#", "*", "##", "Plot Outline", "Act", ":")
                        )
                    ]
                    plot_outline.act_three_block_three = [
                        p.strip()
                        for p in act_three_blocks[3].split("\n")
                        if p.strip()
                        and not p.strip().startswith(
                            ("#", "*", "##", "Plot Outline", "Act", ":")
                        )
                    ]
                else:
                    logger.warning(
                        "Unexpected plot outline format from LLM, basic parsing failed."
                    )
                    # Fallback: assign all to act_one_block_one if parsing fails
                    plot_outline.act_one_block_one = [generated_text]

                logger.debug(
                    "generate_plot_outline - PlotOutline parsing successful."
                )
                logger.info("Plot outline generated successfully.")
                return plot_outline
        except (TypeError, ValueError) as e:
            logger.error(f"Error processing PlotOutline response: {e}")
            logger.debug("Raw LLM response: %s", generated_text)
            return None

    except Exception as e:
        logger.exception("generate_plot_outline - Exception occurred: {e}")
        return None


async def enhance_plot_outline(content_generator, current_outline: str) -> Optional[str]:
    """
    Asynchronously enhances an existing plot outline.
    """
    ollama_client = OllamaClient()
    prompt_manager = PromptManager()
    try:
        critique_prompt_template = prompt_manager.create_plot_outline_critique_prompt()
        rewrite_prompt_template = prompt_manager.create_plot_outline_rewrite_prompt()

        variables = {"current_outline": current_outline}
        critique_prompt_str = critique_prompt_template.format(**variables)

        critique = await ollama_client.generate_text(
            model_name=content_generator.model_name,
            prompt=critique_prompt_str,
        )

        if not critique:
            logger.error("Failed to generate critique for plot outline.")
            return None

        rewrite_prompt_str = rewrite_prompt_template.format(
            current_outline=current_outline, critique=critique
        )
        enhanced_outline = await ollama_client.generate_text(
            model_name=content_generator.model_name,
            prompt=rewrite_prompt_str,
        )

        if enhanced_outline:
            logger.info("Plot outline enhanced successfully.")
            return enhanced_outline
        else:
            logger.error("Failed to enhance plot outline.")
            return None
    except Exception as e:
        logger.exception("Exception occurred during plot outline enhancement.")
        return None