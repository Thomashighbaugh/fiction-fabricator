# core/content_generator.py
import json
from typing import List

from pydantic import BaseModel, ValidationError
import streamlit as st
import random
import re

from core.book_spec import BookSpec
from llm.llm_client import OllamaClient
from llm.prompt_manager import PromptManager
from utils.logger import logger, config


#  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫


class PlotOutline(BaseModel):
    """
    Represents a three-act plot outline for a novel, with acts and blocks as lists of plot points,
    following the 27 chapter methodology structure.
    """

    act_one_block_one: List[str] = []
    act_one_block_two: List[str] = []
    act_one_block_three: List[str] = []
    """Act One: Setup - Divided into three blocks representing different phases of setup."""

    act_two_block_one: List[str] = []
    act_two_block_two: List[str] = []
    act_two_block_three: List[str] = []
    """Act Two: Confrontation - Divided into three blocks representing different phases of confrontation."""

    act_three_block_one: List[str] = []
    act_three_block_two: List[str] = []
    act_three_block_three: List[str] = []
    """Act Three: Resolution - Divided into three blocks representing different phases of resolution."""


#  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫


class ChapterOutline(BaseModel):
    """
    Represents an outline for a single chapter in the novel.

    This Pydantic model defines the structure for a chapter outline,
    including the chapter number and a summary of the chapter's events.
    """

    chapter_number: int
    """The chapter number (e.g., 1, 2, 3...)."""
    summary: str
    """A summary of the key events and developments within this chapter."""


#  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫


class ChapterOutlineMethod(BaseModel):
    """
    Represents an outline for a single chapter in the novel,
    specifically for the 27 chapter methodology.

    This Pydantic model defines the structure for a chapter outline,
    including the chapter number, its role in the 27 chapter methodology
    and a summary of the chapter's events.
    """

    chapter_number: int
    """The chapter number (e.g., 1 to 27)."""
    role: str
    """The role of this chapter in the 27 chapter methodology (e.g., "Introduction", "Inciting Incident", etc.)."""
    summary: str


#  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫


class SceneOutline(BaseModel):
    """
    Represents an outline for a single scene within a chapter.

    This Pydantic model defines the structure for a scene outline,
    including the scene number and a summary of the scene's events,
    setting, and characters involved.
    """

    scene_number: int
    """The scene number within the chapter (e.g., 1, 2, 3...)."""
    summary: str
    """A summary of the key events, setting, and characters in this scene."""


#  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫


class ContentGenerator:
    """
    Orchestrates the content generation process for the novel using asynchronous operations.
    """

    def __init__(self, prompt_manager: PromptManager, model_name: str):
        """
        Initializes the ContentGenerator with an LLM client and a prompt manager.
        Now also stores the model_name.
        """
        self.ollama_client = OllamaClient()
        self.prompt_manager = prompt_manager
        self.model_name = model_name  # Store the model_name
        logger.debug(
            f"ContentGenerator initializing with model_name: {model_name}"
        )  # Log the model_name upon initialization
        logger.debug(f"ContentGenerator.__init__ - OllamaClient initialized.")

    #  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫

    async def generate_book_spec(self, idea: str) -> BookSpec | None:
        """
        Asynchronously generates a BookSpec object based on a user-provided story idea.
        """
        try:
            generation_prompt_template = (
                self.prompt_manager.create_book_spec_generation_prompt()
            )
            structure_check_prompt_template = (
                self.prompt_manager.create_book_spec_structure_check_prompt()
            )
            structure_fix_prompt_template = (
                self.prompt_manager.create_book_spec_structure_fix_prompt()
            )

            variables = {
                "idea": idea,
            }

            generation_prompt = generation_prompt_template.format(**variables)

            generated_text = await self.ollama_client.generate_text(
                model_name=self.model_name,
                prompt=generation_prompt,
            )
            print(f"GEN TEXT: {generated_text}")
            if not generated_text:
                logger.error("Failed to generate book specification.")
                return None

            # Structure Check
            structure_check_variables = {"book_spec_json": generated_text}
            structure_check_prompt = structure_check_prompt_template.format(
                **structure_check_variables
            )

            structure_check_result = await self.ollama_client.generate_text(
                model_name=self.model_name,
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
                fixed_text = await self.ollama_client.generate_text(
                    model_name=self.model_name,
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
                if generated_text.startswith("```json") and generated_text.endswith(
                    "```"
                ):
                    generated_text = generated_text[7:-3].strip()
                if generated_text.startswith("```") and generated_text.endswith("```"):
                    generated_text = generated_text[
                        3:-3
                    ].strip()  # strip generic code block
                generated_text = generated_text.replace(
                    "\\\n", "\n"
                )  # Handle escaped newlines
                generated_text = generated_text.replace(
                    '\\"', '"'
                )  # Handle escaped quotes

                book_spec = BookSpec(**json.loads(generated_text))
                logger.info("Book specification generated successfully.")
                return book_spec
            except (json.JSONDecodeError, ValidationError) as e:
                logger.error(f"Error decoding or validating BookSpec: {e}")
                logger.debug("Raw LLM response: %s", generated_text)
                return None

        except Exception as e:
            logger.error(f"Error generating book spec: {e}")
            return None

    #  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
    async def enhance_book_spec(self, current_spec: BookSpec) -> BookSpec | None:
        """
        Asynchronously enhances an existing BookSpec object using critique and rewrite.
        """
        try:
            # Define prompt templates for critique and rewrite
            critique_prompt_template = (
                self.prompt_manager.create_book_spec_critique_prompt()
            )
            rewrite_prompt_template = (
                self.prompt_manager.create_book_spec_rewrite_prompt()
            )

            # Prepare variables for the prompts
            variables = {
                "current_spec_json": current_spec.model_dump_json(indent=4),
            }

            critique_prompt_str = critique_prompt_template.format(**variables)

            # Generate actionable critique
            critique = await self.ollama_client.generate_text(
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
            enhanced_spec_json = await self.ollama_client.generate_text(
                model_name=self.model_name,
                prompt=rewrite_prompt_str,
            )

            if not enhanced_spec_json:
                logger.error("Failed to rewrite book specification.")
                return None

            try:
                enhanced_spec = BookSpec(**json.loads(enhanced_spec_json))
                logger.info("Book specification enhanced successfully.")
                return enhanced_spec
            except (json.JSONDecodeError, ValidationError) as e:
                logger.error("Error decoding or validating enhanced BookSpec: %s", e)
                return None

        except Exception as e:
            logger.exception(
                "Exception occurred during book specification enhancement."
            )
            return None

            #  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
            generation_prompt = generation_prompt_template.format(**variables)
            logger.debug(
                f"generate_chapter_outline_27_method - PROMPT: {generation_prompt}"
            )

            generated_text = await self.ollama_client.generate_text(
                model_name=self.model_name,
                prompt=generation_prompt,
            )

            if not generated_text:
                logger.error("Failed to generate 27 chapter outlines.")
                return None

            logger.debug(
                f"Raw LLM Chapter Outline 27 Method Response: {generated_text}"
            )

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

    #  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫

    async def enhance_chapter_outlines_27_method(
        self, current_outlines: List[ChapterOutlineMethod]
    ) -> List[ChapterOutlineMethod] | None:
        """
        Asynchronously enhances existing 27 chapter outlines using critique and rewrite.
        """
        try:
            # Convert ChapterOutlineMethod objects to text
            outline_texts = [
                f"Chapter {co.chapter_number} – {co.role}:\n{co.summary}"
                for co in current_outlines
            ]
            current_outlines_text = "\n\n".join(outline_texts)

            # Define prompt templates for critique and rewrite
            critique_prompt_template = (
                self.prompt_manager.create_chapter_outline_27_method_critique_prompt()
            )
            rewrite_prompt_template = (
                self.prompt_manager.create_chapter_outline_27_method_rewrite_prompt()
            )

            # Prepare variables for the prompts
            variables = {
                "current_outlines": current_outlines_text,
            }

            critique_prompt_str = critique_prompt_template.format(**variables)

            # Generate actionable critique
            critique = await self.ollama_client.generate_text(
                model_name=self.model_name,
                prompt=critique_prompt_str,
            )
            print(f"CRITIQUE: {critique}")

            if critique:
                rewrite_prompt_str = rewrite_prompt_template.format(
                    **variables,
                    critique=critique,
                    current_outlines=current_outlines_text,
                )
                # Rewrite content based on the critique
                enhanced_outlines_text = await self.ollama_client.generate_text(
                    prompt=rewrite_prompt_str,
                    model_name=self.model_name,
                )

                if enhanced_outlines_text:
                    enhanced_chapter_outlines_27_method = []
                    try:
                        chapter_pattern = re.compile(
                            r"Chapter\s*(\d+)\s*–\s*(.*?)\s*–\s*(.*?)(?=(?:\nChapter|$))",
                            re.DOTALL | re.IGNORECASE,
                        )
                        chapter_matches = chapter_pattern.finditer(
                            enhanced_outlines_text
                        )

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
                        logger.info(
                            "Chapter outlines (27 method) enhanced successfully."
                        )
                        return enhanced_chapter_outlines_27_method
                    except (TypeError, ValueError) as e:
                        logger.error(
                            "Error processing enhanced ChapterOutlineMethod responses: %s",
                            e,
                        )
                        logger.debug("Raw LLM response: %s", enhanced_outlines_text)
                        return []
                else:
                    logger.error("Failed to rewrite chapter outlines (27 method).")
                    return []
            else:
                logger.error(
                    "Failed to generate critique for chapter outlines (27 method)."
                )
                return []
        except Exception as e:
            logger.exception("Exception occurred during chapter outlines enhancement.")
            return []

    #  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫

    async def generate_plot_outline(self, book_spec: BookSpec) -> PlotOutline | None:
        """
        Asynchronously generates a PlotOutline object based on a BookSpec.
        """
        try:
            generation_prompt_template = (
                self.prompt_manager.create_plot_outline_generation_prompt()
            )
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
            generated_text = await self.ollama_client.generate_text(
                model_name=self.model_name,
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

    #  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫

    async def enhance_plot_outline(self, current_outline: str) -> str | None:
        """
        Asynchronously enhances an existing plot outline.
        """
        try:
            critique_prompt_template = (
                self.prompt_manager.create_plot_outline_critique_prompt()
            )
            rewrite_prompt_template = (
                self.prompt_manager.create_plot_outline_rewrite_prompt()
            )

            variables = {"current_outline": current_outline}
            critique_prompt_str = critique_prompt_template.format(**variables)

            critique = await self.ollama_client.generate_text(
                model_name=self.model_name,
                prompt=critique_prompt_str,
            )

            if not critique:
                logger.error("Failed to generate critique for plot outline.")
                return None

            rewrite_prompt_str = rewrite_prompt_template.format(
                current_outline=current_outline, critique=critique
            )
            enhanced_outline = await self.ollama_client.generate_text(
                model_name=self.model_name,
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

    #  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫

    async def generate_chapter_outlines(
        self, plot_outline: PlotOutline
    ) -> List[ChapterOutline] | None:
        """
        Asynchronously generates chapter outlines based on a PlotOutline.
        Dynamically determines the number of chapters based on the plot outline.
        """
        chapter_outlines = []
        try:
            generation_prompt_template = (
                self.prompt_manager.create_chapter_outlines_generation_prompt()
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
                        "Act One - Block 1:\n"
                        + "\n".join(plot_outline.act_one_block_one),
                        "Act One - Block 2:\n"
                        + "\n".join(plot_outline.act_one_block_two),
                        "Act One - Block 3:\n"
                        + "\n".join(plot_outline.act_one_block_three),
                        "Act Two - Block 1:\n"
                        + "\n".join(plot_outline.act_two_block_one),
                        "Act Two - Block 2:\n"
                        + "\n".join(plot_outline.act_two_block_two),
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
            logger.debug(
                f"generate_chapter_outlines - PROMPT: {generation_prompt}"
            )  # Log Prompt

            generated_text = await self.ollama_client.generate_text(
                model_name=self.model_name,
                prompt=generation_prompt,
            )

            if not generated_text:
                logger.error("Failed to generate chapter outlines.")
                return None

            logger.debug(
                f"Raw LLM Chapter Outline Response: {generated_text}"
            )  # Log LLM Response

            try:
                # Use regex to find chapter headings and summaries more reliably
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

    #  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫

    async def enhance_chapter_outlines(
        self, current_outlines: List[ChapterOutline]
    ) -> List[ChapterOutline] | None:
        """
        Asynchronously enhances existing chapter outlines using critique and rewrite.
        """
        try:
            # Convert ChapterOutline objects to text
            outline_texts = [
                f"Chapter {co.chapter_number}:\n{co.summary}" for co in current_outlines
            ]
            current_outlines_text = "\n\n".join(outline_texts)

            # Define prompt templates for critique and rewrite
            critique_prompt_template = (
                self.prompt_manager.create_chapter_outlines_critique_prompt()
            )
            rewrite_prompt_template = (
                self.prompt_manager.create_chapter_outlines_rewrite_prompt()
            )

            # Prepare variables for the prompts
            variables = {
                "current_outlines": current_outlines_text,
            }

            critique_prompt_str = critique_prompt_template.format(**variables)

            # Generate actionable critique
            critique = await self.ollama_client.generate_text(
                model_name=self.model_name,
                prompt=critique_prompt_str,
            )
            print(f"CRITIQUE: {critique}")

            if critique:
                rewrite_prompt_str = rewrite_prompt_template.format(
                    **variables,
                    critique=critique,
                    current_outlines=current_outlines_text,
                )
                # Rewrite content based on the critique
                enhanced_outlines_text = await self.ollama_client.generate_text(
                    prompt=rewrite_prompt_str,
                    model_name=self.model_name,
                )

                if enhanced_outlines_text:
                    enhanced_chapter_outlines: List[ChapterOutline] = []
                    try:
                        chapter_splits = enhanced_outlines_text.strip().split(
                            "Chapter "
                        )
                        for i, chapter_text in enumerate(chapter_splits[1:], start=1):
                            chapter_summary = chapter_text.split("Chapter")[0].strip()
                            enhanced_chapter_outlines.append(
                                ChapterOutline(
                                    chapter_number=i, summary=chapter_summary
                                )
                            )
                        logger.info("Chapter outlines enhanced successfully.")
                        return enhanced_chapter_outlines
                    except (TypeError, ValueError) as e:
                        logger.error(
                            f"Error processing enhanced ChapterOutline responses: {e}"
                        )
                        logger.debug("Raw LLM response: %s", enhanced_outlines_text)
                        return None
                    else:
                        logger.error("Failed to rewrite chapter outlines.")
                        return None
                else:
                    logger.error("Failed to generate critique for chapter outlines.")
                    return None

        except Exception as e:
            logger.error(f"Error enhancing chapter outlines: {e}")
            return None

    #  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
    async def generate_scene_outlines(
        self, chapter_outline: ChapterOutline, num_scenes: int
    ) -> List[SceneOutline] | None:
        """
        Asynchronously generates scene outlines for a given chapter outline.
        Refactored for robust scene parsing using regex.
        """
        try:
            generation_prompt_template = (
                self.prompt_manager.create_scene_outlines_generation_prompt()
            )
            variables = {
                "chapter_outline": chapter_outline.summary,
                "num_scenes_per_chapter": str(num_scenes),
            }

            generation_prompt = generation_prompt_template.format(**variables)

            generated_text = await self.ollama_client.generate_text(
                prompt=generation_prompt,
                model_name=self.model_name,
            )

            if not generated_text:
                logger.error("Failed to generate scene outlines.")
                return None

            scene_outlines: List[SceneOutline] = []
            scene_pattern = re.compile(
                r"Scene\s*(\d+):?\s*(.*?)(?=(?:\nScene|$))",
                re.DOTALL | re.IGNORECASE,
            )
            scene_matches = scene_pattern.finditer(generated_text)
            found_scenes = 0

            for match in scene_matches:
                scene_number = int(match.group(1))
                scene_summary = match.group(2).strip()
                if scene_summary:
                    scene_outlines.append(
                        SceneOutline(scene_number=scene_number, summary=scene_summary)
                    )
                    found_scenes += 1
                    logger.debug(
                        "Parsed scene %d-%d outline: %s...",
                        chapter_outline.chapter_number,
                        scene_number,
                        scene_summary[:50],
                    )

            if found_scenes < num_scenes:
                logger.warning(
                    "Expected %d scenes, but only parsed %d for chapter %d. "
                    "Review LLM output for parsing errors.",
                    num_scenes,
                    found_scenes,
                    chapter_outline.chapter_number,
                )
            elif found_scenes > num_scenes:
                scene_outlines = scene_outlines[
                    :num_scenes
                ]  # Trim if LLM over-generates
                logger.warning(
                    "LLM generated %d scenes, trimming to requested %d for chapter %d.",
                    found_scenes,
                    num_scenes,
                    chapter_outline.chapter_number,
                )

            logger.debug(
                "%d scene outlines generated for chapter %d successfully.",
                len(scene_outlines),
                chapter_outline.chapter_number,
            )
            return scene_outlines

        except (TypeError, ValueError, re.error) as e:
            logger.error("Error processing SceneOutline responses: %s", e)
            logger.debug("Raw LLM response: %s", generated_text)
            return None
            #  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫

            async def enhance_scene_outlines(
                self, current_outlines: List[SceneOutline]
            ) -> List[SceneOutline] | None:
                """
                Asynchronously enhances existing scene outlines.
                """
                outline_texts = [
                    f"Scene {so.scene_number}:\n{so.summary}" for so in current_outlines
                ]
                prompt = self.prompt_manager.create_enhance_scene_outlines_prompt(
                    outline_texts
                )
                generated_text = await self.ollama_client.generate_text(
                    model_name=self.model_name,
                    prompt=prompt,  # Use self.model_name here
                )
                if generated_text:
                    scene_outlines = []
                    try:
                        scene_splits = generated_text.strip().split("Scene ")
                        for i, scene_text in enumerate(scene_splits[1:], start=1):
                            scene_summary = scene_text.split("Scene")[0].strip()
                            scene_outlines.append(
                                SceneOutline(scene_number=i, summary=scene_summary)
                            )
                        logger.info("Scene outlines enhanced successfully.")
                        return scene_outlines
                    except (TypeError, ValueError) as e:
                        logger.error("Error processing SceneOutline responses: %s", e)
                        logger.debug("Raw LLM response: %s", generated_text)
                    return None

        #  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫

        async def generate_scene_part(
            self,
            scene_outline: SceneOutline,
            part_number: int,
            book_spec: BookSpec,
            chapter_outline: ChapterOutline,
            scene_outline_full: SceneOutline,
        ) -> str | None:
            """
            Asynchronously generates a part of a scene's text content.
            """
            try:
                generation_prompt_template = (
                    self.prompt_manager.create_scene_part_generation_prompt()
                )
                structure_check_prompt_template = (
                    self.prompt_manager.create_scene_part_structure_check_prompt()
                )
                structure_fix_prompt_template = (
                    self.prompt_manager.create_scene_part_structure_fix_prompt()
                )

                variables = {
                    "scene_outline": scene_outline.summary,
                    "part_number": str(part_number),
                    "book_spec_text": book_spec.model_dump_json(indent=4),
                    "chapter_outline": chapter_outline.summary,
                    "scene_outline_full": scene_outline_full.summary,
                }

                generation_prompt = generation_prompt_template.format(**variables)

                generated_text = await self.ollama_client.generate_text(
                    prompt=generation_prompt,
                    model_name=self.model_name,  # Use self.model_name here
                )

                if not generated_text:
                    logger.error("Failed to generate scene part.")
                    return None

                # Structure Check
                structure_check_variables = {"scene_part": generated_text}
                structure_check_prompt = structure_check_prompt_template.format(
                    **structure_check_variables
                )
                structure_check_result = await self.ollama_client.generate_text(
                    model_name=self.model_name,  # Use self.model_name here
                    prompt=structure_check_prompt,
                )

                if structure_check_result != "STRUCTURE_OK":
                    logger.warning(
                        "Scene Part structure check failed. Attempting to fix..."
                    )
                    # Structure Fix
                    structure_fix_variables = {
                        "scene_part": generated_text,
                        "structure_problems": structure_check_result,
                    }
                    structure_fix_prompt = (
                        self.prompt_manager.create_scene_part_structure_fix_prompt()
                    )
                    structure_fix_prompt_formatted = structure_fix_prompt.format(
                        **structure_fix_variables
                    )

                    fixed_text = await self.ollama_client.generate_text(
                        model_name=self.model_name,  # Use self.model_name here
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

        #  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫

        async def enhance_scene_part(
            self,
            scene_part: str,
            part_number: int,
            book_spec: BookSpec,
            chapter_outline: ChapterOutline,
            scene_outline_full: SceneOutline,
        ) -> str | None:
            """
            Asynchronously enhances an existing scene part's text content.
            """
            try:
                # Get prompt templates from PromptManager
                critique_prompt_template = (
                    self.prompt_manager.create_scene_part_critique_prompt()
                )
                rewrite_prompt_template = (
                    self.prompt_manager.create_scene_part_rewrite_prompt()
                )

                # Prepare variables for the prompts
                variables = {
                    "book_spec": book_spec.model_dump_json(indent=4),
                    "chapter_outline": chapter_outline.summary,
                    "scene_outline_full": scene_outline_full.summary,
                    "part_number": str(part_number),
                }

                critique_prompt_str = critique_prompt_template.format(**variables)

                # Generate actionable critique
                critique = await self.ollama_client.generate_text(
                    model_name=self.model_name,
                    prompt=critique_prompt_str,  # Use self.model_name here
                )

                if critique:
                    rewrite_prompt_str = rewrite_prompt_template.format(
                        **variables, critique=critique, content=scene_part
                    )
                    # Rewrite content based on the critique
                    enhanced_scene_part = await self.ollama_client.generate_text(
                        prompt=rewrite_prompt_str,
                        model_name=self.model_name,  # Use self.model_name here
                    )

                    if enhanced_scene_part:
                        logger.info("Scene part %d enhanced successfully.", part_number)
                        return enhanced_scene_part
                    else:
                        logger.error("Failed to rewrite scene part %d.", part_number)
                        return None

                else:
                    logger.error(
                        "Failed to generate critique for scene part %d.", part_number
                    )
                    return None
            except Exception as e:
                logger.error("Error enhancing scene part %d: %s", part_number, e)
                return None
