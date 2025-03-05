# core/content_generator.py
import json
from typing import List
from pydantic import ValidationError
import streamlit as st
import random

from core.book_spec import BookSpec
from core.plot_outline import ChapterOutline, PlotOutline, SceneOutline
from llm.llm_client import OllamaClient
from llm.prompt_manager import PromptManager
from utils.logger import logger, config


class ContentGenerator:
    """
    Orchestrates the content generation process for the novel using asynchronous operations.
    """

    def __init__(self, prompt_manager: PromptManager, model_name: str):
        """
        Initializes the ContentGenerator with an LLM client and a prompt manager.
        """
        self.ollama_client = OllamaClient()
        self.prompt_manager = prompt_manager
        logger.debug(f"ContentGenerator initializing with model_name: {model_name}")
        logger.debug(f"ContentGenerator.__init__ - OllamaClient initialized.")

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
                model_name=config.get_ollama_model_name(), prompt=generation_prompt
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
                model_name=config.get_ollama_model_name(),
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
                    model_name=config.get_ollama_model_name(),
                    prompt=structure_fix_prompt,
                )
                if fixed_text:
                    generated_text = fixed_text
                    logger.info("BookSpec structure fixed successfully.")
                else:
                    logger.error("Failed to fix BookSpec structure.")
                    return None
            try:
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
                model_name=config.get_ollama_model_name(), prompt=critique_prompt_str
            )

            print(f"CRITIQUE: {critique}")

            if critique:
                # Rewrite content based on the critique
                rewrite_prompt_str = rewrite_prompt_template.format(
                    **variables, critique=critique
                )
                enhanced_spec_json = await self.ollama_client.generate_text(
                    model_name=config.get_ollama_model_name(),
                    prompt=rewrite_prompt_str,
                )

                if enhanced_spec_json:
                    try:
                        enhanced_spec = BookSpec(**json.loads(enhanced_spec_json))
                        logger.info("Book specification enhanced successfully.")
                        return enhanced_spec
                    except (json.JSONDecodeError, ValidationError) as e:
                        logger.error(
                            f"Error decoding or validating enhanced BookSpec: {e}"
                        )
                        return None
                else:
                    logger.error("Failed to rewrite book specification.")
                    return None
            else:
                logger.error("Failed to generate critique for book specification.")
                return None

        except Exception as e:
            logger.error(f"Error enhancing book spec: {e}")
            return None

    async def generate_plot_outline(self, book_spec: BookSpec) -> PlotOutline | None:
        """
        Asynchronously generates a PlotOutline object based on a BookSpec.
        """
        try:
            generation_prompt_template = (
                self.prompt_manager.create_plot_outline_generation_prompt()
            )
            logger.debug("generate_plot_outline - Generation prompt template loaded.")
            structure_check_prompt_template = (
                self.prompt_manager.create_plot_outline_structure_check_prompt()
            )
            structure_fix_prompt_template = (
                self.prompt_manager.create_plot_outline_structure_fix_prompt()
            )

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
                model_name=config.get_ollama_model_name(), prompt=full_prompt
            )

            if not generated_text:
                logger.error(
                    "generate_plot_outline - No text generated by OllamaClient."
                )
                logger.error("Failed to generate plot outline.")
                return None

            logger.debug(f"Raw LLM Plot Outline Response: {generated_text}")

            # Structure Check
            logger.debug("generate_plot_outline - Starting structure check.")
            structure_check_variables = {"plot_outline": generated_text}
            structure_check_prompt = structure_check_prompt_template.format(
                **structure_check_variables
            )
            logger.debug("generate_plot_outline - Structure check prompt formatted.")
            structure_check_result = await self.ollama_client.generate_text(
                model_name=config.get_ollama_model_name(),
                prompt=structure_check_prompt,
            )
            logger.debug(
                f"generate_plot_outline - Structure check result: {structure_check_result}"
            )

            if structure_check_result != "STRUCTURE_OK":
                logger.warning(
                    "PlotOutline structure check failed. Attempting to fix..."
                )

                structure_fix_variables = {
                    "plot_outline": generated_text,
                    "structure_problems": structure_check_result,
                }
                structure_fix_prompt = structure_fix_prompt_template.format(
                    **structure_fix_variables
                )
                logger.debug("generate_plot_outline - Structure fix prompt formatted.")

                fixed_text = await self.ollama_client.generate_text(
                    model_name=config.get_ollama_model_name(),
                    prompt=structure_fix_prompt,
                )
                if fixed_text:
                    generated_text = fixed_text
                    logger.info("PlotOutline structure fixed successfully.")
                else:
                    logger.error("Failed to fix PlotOutline structure.")
                    return None
            try:
                logger.debug("generate_plot_outline - Attempting to parse PlotOutline.")
                plot_outline = PlotOutline(act_one="", act_two="", act_three="")
                acts = generated_text.split("Act ")
                if len(acts) >= 4:
                    plot_outline.act_one = acts[1].split("Act")[0].strip()
                    plot_outline.act_two = acts[2].split("Act")[0].strip()
                    plot_outline.act_three = acts[3].strip()
                else:
                    logger.warning(
                        "Unexpected plot outline format from LLM, basic parsing failed."
                    )
                    plot_outline.act_one = generated_text

                logger.debug("generate_plot_outline - PlotOutline parsing successful.")
                logger.info("Plot outline generated successfully.")
                return plot_outline

            except (TypeError, ValueError) as e:
                logger.error(f"Error processing PlotOutline response: {e}")
                logger.debug("Raw LLM response: %s", generated_text)
                return None
        except Exception as e:
            logger.exception(
                "generate_plot_outline - Exception occurred during plot outline generation."
            )
            logger.error(f"Error generating plot outline: {e}")
            return None

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
                model_name=config.get_ollama_model_name(), prompt=critique_prompt_str
            )

            if not critique:
                logger.error("Failed to generate critique for plot outline.")
                return None

            rewrite_prompt_str = rewrite_prompt_template.format(
                current_outline=current_outline, critique=critique
            )
            enhanced_outline = await self.ollama_client.generate_text(
                model_name=config.get_ollama_model_name(), prompt=rewrite_prompt_str
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

    async def generate_chapter_outlines(
        self, plot_outline: PlotOutline, num_chapters: int
    ) -> List[ChapterOutline] | None:
        """
        Asynchronously generates chapter outlines based on a PlotOutline.
        """
        try:
            generation_prompt_template = (
                self.prompt_manager.create_chapter_outlines_generation_prompt()
            )
            structure_check_prompt_template = (
                self.prompt_manager.create_chapter_outlines_structure_check_prompt()
            )
            structure_fix_prompt_template = (
                self.prompt_manager.create_chapter_outlines_structure_fix_prompt()
            )

            variables = {
                "plot_outline": "\n".join(
                    [
                        "Act One:\n" + plot_outline.act_one,
                        "Act Two:\n" + plot_outline.act_two,
                        "Act Three:\n" + plot_outline.act_three,
                    ]
                ),
                "num_chapters": str(num_chapters),
            }

            generated_text = await self.ollama_client.generate_text(
                model_name=config.get_ollama_model_name(),
                prompt=generation_prompt_template.format(**variables),
            )

            if not generated_text:
                logger.error("Failed to generate chapter outlines.")
                return None

            # Structure Check
            structure_check_variables = {"chapter_outlines": generated_text}
            structure_check_prompt = structure_check_prompt_template.format(
                **structure_check_variables
            )
            structure_check_result = await self.ollama_client.generate_text(
                model_name=config.get_ollama_model_name(),
                prompt=structure_check_prompt,
            )

            if structure_check_result != "STRUCTURE_OK":
                logger.warning(
                    "Chapter outlines structure check failed. Attempting to fix..."
                )

                structure_fix_variables = {
                    "chapter_outlines": generated_text,
                    "structure_problems": structure_check_result,
                }
                structure_fix_prompt = structure_fix_prompt_template.format(
                    **structure_fix_variables
                )

                fixed_text = await self.ollama_client.generate_text(
                    model_name=config.get_ollama_model_name(),
                    prompt=structure_fix_prompt,
                )
                if fixed_text:
                    generated_text = fixed_text.strip()
                    logger.info("Chapter Outlines structure fixed successfully.")
                else:
                    logger.error("Failed to fix Chapter Outlines structure.")
                    return None
            logger.debug("Raw LLM output for chapter outlines: %s", generated_text)

            chapter_outlines = []
            try:
                chapter_splits = generated_text.strip().split("Chapter ")
                logger.debug(
                    f"Number of chapter splits found: {len(chapter_splits) - 1}"
                )
                for i, chapter_text in enumerate(chapter_splits[1:], start=1):
                    chapter_summary = chapter_text.split("Chapter")[0].strip()
                    if chapter_summary:
                        chapter_outlines.append(
                            ChapterOutline(chapter_number=i, summary=chapter_summary)
                        )
                        logger.debug(
                            f"Parsed chapter {i} outline: {chapter_summary[:50]}..."
                        )
            except Exception as e:
                logger.error(f"Error processing ChapterOutline responses: {e}")
                logger.debug("Raw LLM response: %s", generated_text)
                return None

            logger.info(
                "%d chapter outlines generated successfully.",
                len(chapter_outlines),
            )
            return chapter_outlines

        except Exception as e:
            logger.error(f"Error generating chapter outlines: {e}")
            return None

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
                model_name=config.get_ollama_model_name(), prompt=critique_prompt_str
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
                    model_name=config.get_ollama_model_name(),
                )

                if enhanced_outlines_text:
                    enhanced_chapter_outlines = []
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

    async def generate_scene_outlines(
        self, chapter_outline: ChapterOutline, num_scenes: int
    ) -> List[SceneOutline] | None:
        """
        Asynchronously generates scene outlines for a given chapter outline.
        """
        try:
            generation_prompt_template = (
                self.prompt_manager.create_scene_outlines_generation_prompt()
            )
            structure_check_prompt_template = (
                self.prompt_manager.create_scene_outlines_structure_check_prompt()
            )

            variables = {
                "chapter_outline": chapter_outline.summary,
                "num_scenes_per_chapter": str(num_scenes),
            }

            generation_prompt = generation_prompt_template.format(**variables)

            generated_text = await self.ollama_client.generate_text(
                prompt=generation_prompt, model_name=config.get_ollama_model_name()
            )

            if not generated_text or generated_text is None:
                logger.error("Failed to generate scene outlines.")
                return None

            # Structure Check
            structure_check_variables = {"scene_outlines": generated_text}
            structure_check_prompt = structure_check_prompt_template.format(
                **structure_check_variables
            )
            structure_check_result = await self.ollama_client.generate_text(
                model_name=config.get_ollama_model_name(),
                prompt=structure_check_prompt,
            )
            if (
                structure_check_result is not None
                and structure_check_result != "STRUCTURE_OK"
            ):
                logger.warning(
                    "Scene outlines structure check failed. Attempting to fix..."
                )
                # Attempting to fix the structure
                structure_fix_variables = {
                    "scene_outlines": generated_text,
                    "structure_problems": structure_check_result,
                }
                structure_fix_prompt = (
                    self.prompt_manager.create_scene_outlines_structure_fix_prompt()
                )
                structure_fix_prompt_formatted = structure_fix_prompt.format(
                    **structure_fix_variables
                )

                fixed_text = await self.ollama_client.generate_text(
                    model_name=config.get_ollama_model_name(),
                    prompt=structure_fix_prompt_formatted,
                )
                if fixed_text:
                    generated_text = fixed_text
                    logger.info(
                        f"Scene outlines structure fixed successfully. fixed_text: {fixed_text}"
                    )
                else:
                    logger.error("Failed to fix scene outlines structure.")
                    return None

            scene_outlines = []
            try:
                scene_splits = generated_text.strip().split("Scene ")
                for i, scene_text in enumerate(scene_splits[1:], start=1):
                    scene_summary = scene_text.split("Scene")[0].strip()
                    scene_outlines.append(
                        SceneOutline(scene_number=i, summary=scene_summary)
                    )
                logger.info(
                    "%d scene outlines generated for chapter %d successfully.",
                    len(scene_outlines),
                    chapter_outline.chapter_number,
                )
                return scene_outlines
            except (TypeError, ValueError) as e:
                logger.error("Error processing SceneOutline responses: %s", e)
                logger.debug("Raw LLM response: %s", generated_text)
                return None

        except Exception as e:
            logger.error(f"Error generating scene outlines: {e}")
            return None

    async def enhance_scene_outlines(
        self, current_outlines: List[SceneOutline]
    ) -> List[SceneOutline] | None:
        """
        Asynchronously enhances existing scene outlines.
        """
        outline_texts = [
            f"Scene {so.scene_number}:\n{so.summary}" for so in current_outlines
        ]
        prompt = self.prompt_manager.create_enhance_scene_outlines_prompt(outline_texts)
        generated_text = await self.ollama_client.generate_text(
            model_name=config.get_ollama_model_name(), prompt=prompt
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
                prompt=generation_prompt, model_name=config.get_ollama_model_name()
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
                model_name=config.get_ollama_model_name(),
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
                    model_name=config.get_ollama_model_name(),
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
            logger.error(f"Error generating scene part: {e}")
            return None

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

            critique_prompt_str = critique_prompt_template.format(
                **variables, content=scene_part
            )

            # Generate actionable critique
            critique = await self.ollama_client.generate_text(
                model_name=config.get_ollama_model_name(), prompt=critique_prompt_str
            )

            if critique:
                rewrite_prompt_str = rewrite_prompt_template.format(
                    **variables, critique=critique, content=scene_part
                )
                # Rewrite content based on the critique
                enhanced_scene_part = await self.ollama_client.generate_text(
                    prompt=rewrite_prompt_str,
                    model_name=config.get_ollama_model_name(),
                )

                if enhanced_scene_part:
                    logger.info(
                        "Scene part %d enhanced successfully.",
                        part_number,
                    )
                    return enhanced_scene_part
                else:
                    logger.error("Failed to rewrite scene part %d.", part_number)
                    return None

            else:
                logger.error(
                    "Failed to generate critique for scene part %d.",
                    part_number,
                )
                return None

        except Exception as e:
            logger.error(f"Error enhancing scene part {part_number}: {e}")
            return None
