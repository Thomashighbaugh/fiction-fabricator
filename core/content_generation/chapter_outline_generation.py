# core/content_generation/chapter_outline_generation.py
from typing import Optional, List

import re

from core.book_spec import BookSpec
from llm.llm_client import OllamaClient
from llm.prompt_manager import PromptManager
from utils.logger import logger
from .content_generation_utils import (
    ChapterOutline,
    ChapterOutlineMethod,
    PlotOutline,
)  # Import ChapterOutline and ChapterOutlineMethod models


async def generate_chapter_outlines(
    content_generator, plot_outline: PlotOutline
) -> Optional[List[ChapterOutline]]:
    """
    Generates chapter outlines based on a PlotOutline.
    """
    ollama_client = OllamaClient()
    prompt_manager = PromptManager()
    chapter_outlines: List[ChapterOutline] = []
    try:
        generation_prompt_template = (
            prompt_manager.create_chapter_outlines_generation_prompt()
        )

        num_chapters = sum(
            len(block)
            for act_blocks in [
                [
                    plot_outline.act_one_block_one,
                    plot_outline.act_one_block_two,
                    plot_outline.act_one_block_three,
                ],
                [
                    plot_outline.act_two_block_one,
                    plot_outline.act_two_block_two,
                    plot_outline.act_two_block_three,
                ],
                [
                    plot_outline.act_three_block_one,
                    plot_outline.act_three_block_two,
                    plot_outline.act_three_block_three,
                ],
            ]
            for block in act_blocks
        )  # Dynamically determine num_chapters from all blocks

        variables = {
            "plot_outline": "\n".join(
                [
                    "Act One - Block 1:\n" + "\n".join(plot_outline.act_one_block_one),
                    "Act One - Block 2:\n" + "\n".join(plot_outline.act_one_block_two),
                    "Act One - Block 3:\n"
                    + "\n".join(plot_outline.act_one_block_three),
                    "Act Two - Block 1:\n" + "\n".join(plot_outline.act_two_block_one),
                    "Act Two - Block 2:\n" + "\n".join(plot_outline.act_two_block_two),
                    "Act Two - Block 3:\n"
                    + "\n".join(plot_outline.act_two_block_three),
                    "Act Three - Block 1:\n"
                    + "\n".join(plot_outline.act_three_block_one),
                    "Act Three - Block 2:\n"
                    + "\n".join(plot_outline.act_three_block_two),
                    "Act Three - Block 3:\n"
                    + "\n".join(plot_outline.act_three_block_three),
                ]
            ),
            "num_chapters": str(num_chapters),  # Pass num_chapters to prompt
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

        try:
            chapter_pattern = re.compile(
                r"Chapter\s*(\d+):?\s*(.*?)(?=(?:\nChapter|$))",
                re.DOTALL | re.IGNORECASE,
            )
            chapter_matches = chapter_pattern.finditer(generated_text)

            found_chapters = 0
            for match in chapter_matches:
                chapter_number = int(match.group(1))
                chapter_summary = match.group(2).strip()
                if chapter_summary:
                    chapter_outlines.append(
                        ChapterOutline(
                            chapter_number=chapter_number, summary=chapter_summary
                        )
                    )
                    found_chapters += 1
                    logger.debug(
                        f"Parsed chapter {chapter_number} outline: {chapter_summary[:50]}..."
                    )
        except Exception as e:
            logger.error(f"Error processing ChapterOutline responses: {e}")
            logger.debug("Raw LLM response: %s", generated_text)
            return None

        logger.info(
            "%d chapter outlines generated successfully.", len(chapter_outlines)
        )
        return chapter_outlines

    except Exception as e:
        logger.error(f"Error generating chapter outlines: {e}")
        return None


async def enhance_chapter_outlines(
    content_generator, current_outlines: List[ChapterOutline]
) -> Optional[List[ChapterOutline]]:
    """
    Enhances existing chapter outlines using critique and rewrite.
    """
    ollama_client = OllamaClient()
    prompt_manager = PromptManager()
    try:
        # Convert ChapterOutline objects to text
        outline_texts = [
            f"Chapter {co.chapter_number}:\n{co.summary}" for co in current_outlines
        ]
        current_outlines_text = "\n\n".join(outline_texts)

        # Define prompt templates for critique and rewrite
        critique_prompt_template = (
            prompt_manager.create_chapter_outlines_critique_prompt()
        )
        rewrite_prompt_template = (
            prompt_manager.create_chapter_outlines_rewrite_prompt()
        )

        # Prepare variables for the prompts
        variables = {
            "current_outlines": current_outlines_text,
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
            current_outlines=current_outlines_text,
        )
        # Rewrite content based on the critique
        enhanced_outlines_text = await ollama_client.generate_text(
            prompt=rewrite_prompt_str,
            model_name=content_generator.model_name,
        )

        if enhanced_outlines_text:
            enhanced_chapter_outlines: List[ChapterOutline] = []
            try:
                chapter_splits = enhanced_outlines_text.strip().split("Chapter ")
                for i, chapter_text in enumerate(chapter_splits[1:], start=1):
                    chapter_summary = chapter_text.split("Chapter")[0].strip()
                    enhanced_chapter_outlines.append(
                        ChapterOutline(chapter_number=i, summary=chapter_summary)
                    )
                logger.info("Chapter outlines enhanced successfully.")
                return enhanced_chapter_outlines
            except (TypeError, ValueError) as e:
                logger.error(f"Error processing enhanced ChapterOutline responses: {e}")
                logger.debug("Raw LLM response: %s", enhanced_outlines_text)
                return None
        else:
            logger.error("Failed to rewrite chapter outlines.")
            return None

    except Exception as e:
        logger.error(f"Error enhancing chapter outlines: {e}")
        return None


async def generate_chapter_outline_27_method(
    content_generator, book_spec: BookSpec
) -> Optional[List[ChapterOutlineMethod]]:
    """
    Generates 27 chapter outlines using the 27-chapter method.
    """
    ollama_client = OllamaClient()
    prompt_manager = PromptManager()
    chapter_outlines_27_method: List[ChapterOutlineMethod] = []
    try:
        generation_prompt_template = (
            prompt_manager.create_chapter_outline_27_method_generation_prompt()
        )

        variables = {
            "book_spec_json": book_spec.model_dump_json(indent=4),
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

        chapter_pattern = re.compile(
            r"Chapter\s*(\d+)\s*–\s*(.*?)\s*–\s*(.*?)(?=(?:\nChapter|$))",
            re.DOTALL | re.IGNORECASE,
        )
        chapter_matches = chapter_pattern.finditer(generated_text)
        found_chapters = 0

        for match in chapter_matches:
            chapter_number = int(match.group(1))
            chapter_role = match.group(2).strip()
            chapter_summary = match.group(3).strip()

            if chapter_summary and chapter_role:
                chapter_outlines_27_method.append(
                    ChapterOutlineMethod(
                        chapter_number=chapter_number,
                        role=chapter_role,
                        summary=chapter_summary,
                    )
                )
                found_chapters += 1
                logger.debug(
                    f"Parsed chapter {chapter_number} outline: {chapter_summary[:50]}..."
                )

        logger.info(
            "%d chapter outlines (27 method) generated successfully.",
            len(chapter_outlines_27_method),
        )
        return chapter_outlines_27_method

    except Exception as e:
        logger.error(f"Error generating 27 chapter outlines: {e}")
        return None


async def enhance_chapter_outlines_27_method(
    content_generator, current_outlines: List[ChapterOutlineMethod]
) -> Optional[List[ChapterOutlineMethod]]:
    """
    Asynchronously enhances existing 27 chapter outlines using critique and rewrite.
    """
    ollama_client = OllamaClient()
    prompt_manager = PromptManager()
    try:
        # Convert ChapterOutlineMethod objects to text
        outline_texts = [
            f"Chapter {co.chapter_number} – {co.role}:\n{co.summary}"
            for co in current_outlines
        ]
        current_outlines_text = "\n\n".join(outline_texts)

        # Define prompt templates for critique and rewrite
        critique_prompt_template = (
            prompt_manager.create_chapter_outline_27_method_critique_prompt()
        )
        rewrite_prompt_template = (
            prompt_manager.create_chapter_outline_27_method_rewrite_prompt()
        )

        # Prepare variables for the prompts
        variables = {
            "current_outlines": current_outlines_text,
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
                current_outlines=current_outlines_text,
            )
            # Rewrite content based on the critique
            enhanced_outlines_text = await ollama_client.generate_text(
                prompt=rewrite_prompt_str,
                model_name=content_generator.model_name,
            )

            if enhanced_outlines_text:
                enhanced_chapter_outlines_27_method: List[ChapterOutlineMethod] = []
                try:
                    chapter_pattern = re.compile(
                        r"Chapter\s*(\d+)\s*–\s*(.*?)\s*–\s*(.*?)(?=(?:\nChapter|$))",
                        re.DOTALL | re.IGNORECASE,
                    )
                    chapter_matches = chapter_pattern.finditer(enhanced_outlines_text)

                    for match in chapter_matches:
                        chapter_number = int(match.group(1))
                        chapter_role = match.group(2).strip()
                        chapter_summary = match.group(3).strip()
                        enhanced_chapter_outlines_27_method.append(
                            ChapterOutlineMethod(
                                chapter_number=chapter_number,
                                role=chapter_role,
                                summary=chapter_summary,
                            )
                        )
                    logger.info("Chapter outlines (27 method) enhanced successfully.")
                    return enhanced_chapter_outlines_27_method
                except (TypeError, ValueError) as e:
                    logger.error(
                        "Error processing enhanced ChapterOutlineMethod responses: %s",
                        e,
                    )
                    logger.debug("Raw LLM response: %s", enhanced_outlines_text)
                    return None
            else:
                logger.error("Failed to rewrite chapter outlines (27 method).")
                return None
        else:
            logger.error(
                "Failed to generate critique for chapter outlines (27 method)."
            )
            return None
    except Exception as e:
        logger.exception("Exception occurred during chapter outlines enhancement.")
        return None
