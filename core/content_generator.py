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
from llm import langchain_client  # Modified import statement
from langchain.prompts import PromptTemplate
from utils.logger import logger


class ContentGenerator:
    """
    Orchestrates the content generation process for the novel.

    This class uses the OllamaClient to interact with the LLM and the PromptManager
    to generate prompts for each stage of content creation, from book specification
    to scene parts. It handles the generation, enhancement, and user interaction
    workflow for creating the novel's content.
    """

    def __init__(self, llm_client: OllamaClient, prompt_manager: PromptManager):
        """
        Initializes the ContentGenerator with an LLM client and a prompt manager.

        Args:
            llm_client (OllamaClient): The Ollama client instance for interacting with the LLM.
            prompt_manager (PromptManager): The PromptManager instance for generating prompts.
        """
        self.llm_client = llm_client
        self.prompt_manager = prompt_manager
        self.langchain_client = langchain_client.LangchainClient()  # Initialize LangchainClient using modified import

    def generate_book_spec(self, idea: str) -> BookSpec | None:
        """
        Generates a BookSpec object based on a user-provided story idea, using Langchain for generation and structure validation.
        """
        try:
            generation_prompt_template = self.prompt_manager.create_book_spec_generation_prompt()
            structure_check_prompt_template = self.prompt_manager.create_book_spec_structure_check_prompt()
            structure_fix_prompt_template = self.prompt_manager.create_book_spec_structure_fix_prompt()

            variables = {
                "idea": idea,
            }

            generated_text = self.langchain_client.generate_text(
                PromptTemplate(template=generation_prompt_template, input_variables=["idea"]).format(**variables)
            )

            if not generated_text:
                logger.error("Failed to generate book specification using Langchain.")
                return None

            # Structure Check
            structure_check_variables = {"book_spec_json": generated_text}
            structure_check_prompt = PromptTemplate(
                template=structure_check_prompt_template, input_variables=["book_spec_json"]
            ).format(**structure_check_variables)
            structure_check_result = self.langchain_client.generate_text(structure_check_prompt)

            if structure_check_result != "STRUCTURE_OK":
                logger.warning("BookSpec structure check failed. Attempting to fix...")
                # Structure Fix
                structure_fix_variables = {
                    "book_spec_json": generated_text,
                    "structure_problems": structure_check_result,
                }
                structure_fix_prompt = PromptTemplate(
                    template=structure_fix_prompt_template, input_variables=["book_spec_json", "structure_problems"]
                ).format(**structure_fix_variables)

                fixed_text = self.langchain_client.generate_text(structure_fix_prompt)
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

    def enhance_book_spec(self, current_spec: BookSpec) -> BookSpec | None:
        """
        Enhances an existing BookSpec object using a Langchain chain for critique and rewrite.
        """
        try:
            # Define prompt templates for critique and rewrite
            critique_prompt_template = self.prompt_manager.create_book_spec_critique_prompt()
            rewrite_prompt_template = self.prompt_manager.create_book_spec_rewrite_prompt()

            # Prepare variables for the prompts
            variables = {
                "current_spec_json": current_spec.model_dump_json(indent=4),
            }

            # Generate actionable critique using Langchain
            critique = self.langchain_client.create_actionable_critique(
                current_spec.model_dump_json(), variables, critique_prompt_template
            )

            if critique:
                # Rewrite content based on the critique using Langchain
                enhanced_spec_json = self.langchain_client.rewrite_content(
                    current_spec.model_dump_json(), critique, variables, rewrite_prompt_template
                )

                if enhanced_spec_json:
                    try:
                        enhanced_spec = BookSpec(**json.loads(enhanced_spec_json))
                        logger.info("Book specification enhanced successfully using Langchain.")
                        return enhanced_spec
                    except (json.JSONDecodeError, ValidationError) as e:
                        logger.error(f"Error decoding or validating enhanced BookSpec: {e}")
                        return None
                else:
                    logger.error("Failed to rewrite book specification using Langchain.")
                    return None
            else:
                logger.error("Failed to generate critique for book specification using Langchain.")
                return None

        except Exception as e:
            logger.error(f"Error enhancing book spec: {e}")
            return None

    def generate_plot_outline(self, book_spec: BookSpec) -> PlotOutline | None:
        """
        Generates a PlotOutline object based on a BookSpec, using Langchain for generation and structure validation.
        """
        try:
            generation_prompt_template = self.prompt_manager.create_plot_outline_generation_prompt()
            structure_check_prompt_template = self.prompt_manager.create_plot_outline_structure_check_prompt()
            structure_fix_prompt_template = self.prompt_manager.create_plot_outline_structure_fix_prompt()

            variables = {
                "book_spec_json": book_spec.model_dump_json(indent=4),
            }

            generated_text = self.langchain_client.generate_text(
                PromptTemplate(template=generation_prompt_template, input_variables=["book_spec_json"]).format(**variables)
            )

            if not generated_text:
                logger.error("Failed to generate plot outline using Langchain.")
                return None

            # Structure Check
            structure_check_variables = {"plot_outline": generated_text}
            structure_check_prompt = PromptTemplate(
                template=structure_check_prompt_template, input_variables=["plot_outline"]
            ).format(**structure_check_variables)
            structure_check_result = self.langchain_client.generate_text(structure_check_prompt)

            if structure_check_result != "STRUCTURE_OK":
                logger.warning("PlotOutline structure check failed. Attempting to fix...")
                # Structure Fix
                structure_fix_variables = {
                    "plot_outline": generated_text,
                    "structure_problems": structure_check_result,
                }
                structure_fix_prompt = PromptTemplate(
                    template=structure_fix_prompt_template, input_variables=["plot_outline", "structure_problems"]
                ).format(**structure_fix_variables)

                fixed_text = self.langchain_client.generate_text(structure_fix_prompt)
                if fixed_text:
                    generated_text = fixed_text
                    logger.info("PlotOutline structure fixed successfully.")
                else:
                    logger.error("Failed to fix PlotOutline structure.")
                    return None

            try:
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

                logger.info("Plot outline generated successfully.")
                return plot_outline

            except (TypeError, ValueError) as e:
                logger.error(f"Error processing PlotOutline response: %s", e)
                logger.debug("Raw LLM response: %s", generated_text)
                return None

        except Exception as e:
            logger.error(f"Error generating plot outline: {e}")
            return None

    def enhance_plot_outline(self, current_outline: str) -> PlotOutline | None:
        """
        Enhances an existing plot outline using a Langchain chain for critique and rewrite.
        """
        try:
            # Define prompt templates for critique and rewrite
            critique_prompt_template = self.prompt_manager.create_plot_outline_critique_prompt()
            rewrite_prompt_template = self.prompt_manager.create_plot_outline_rewrite_prompt()

            # Prepare variables for the prompts
            variables = {
                "current_outline": current_outline,
            }

            # Generate actionable critique using Langchain
            critique = self.langchain_client.create_actionable_critique(
                current_outline, variables, critique_prompt_template
            )

            if critique:
                # Rewrite content based on the critique using Langchain
                enhanced_outline_text = self.langchain_client.rewrite_content(
                    current_outline, critique, variables, rewrite_prompt_template
                )

                if enhanced_outline_text:
                    try:
                        plot_outline = PlotOutline(act_one="", act_two="", act_three="")
                        acts = enhanced_outline_text.split("Act ")
                        if len(acts) >= 4:
                            plot_outline.act_one = acts[1].split("Act")[0].strip()
                            plot_outline.act_two = acts[2].split("Act")[0].strip()
                            plot_outline.act_three = acts[3].strip()
                        else:
                            logger.warning(
                                "Unexpected enhanced plot outline format from LLM, basic parsing failed."
                            )
                            plot_outline.act_one = enhanced_outline_text

                        logger.info("Plot outline enhanced successfully using Langchain.")
                        return plot_outline
                    except (TypeError, ValueError) as e:
                        logger.error(f"Error processing enhanced PlotOutline response: {e}")
                        logger.debug("Raw LLM response: %s", enhanced_outline_text)
                        return None
                else:
                    logger.error("Failed to rewrite plot outline using Langchain.")
                    return None
            else:
                logger.error("Failed to generate critique for plot outline using Langchain.")
                return None

        except Exception as e:
            logger.error(f"Error enhancing plot outline: {e}")
            return None

    def generate_chapter_outlines(
        self, plot_outline: PlotOutline, num_chapters: int
    ) -> List[ChapterOutline] | None:
        """
        Generates chapter outlines based on a PlotOutline and the desired number of chapters, using Langchain for generation and structure validation.
        """
        try:
            generation_prompt_template = self.prompt_manager.create_chapter_outlines_generation_prompt()
            structure_check_prompt_template = self.prompt_manager.create_chapter_outlines_structure_check_prompt()
            structure_fix_prompt_template = self.prompt_manager.create_chapter_outlines_structure_fix_prompt()

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

            generated_text = self.langchain_client.generate_text(
                PromptTemplate(template=generation_prompt_template, input_variables=["plot_outline", "num_chapters"]).format(**variables)
            )

            if not generated_text:
                logger.error("Failed to generate chapter outlines using Langchain.")
                return None

            # Structure Check
            structure_check_variables = {"chapter_outlines": generated_text}
            structure_check_prompt = PromptTemplate(
                template=structure_check_prompt_template, input_variables=["chapter_outlines"]
            ).format(**structure_check_variables)
            structure_check_result = self.langchain_client.generate_text(structure_check_prompt)

            if structure_check_result != "STRUCTURE_OK":
                logger.warning("Chapter outlines structure check failed. Attempting to fix...")

                structure_fix_variables = {
                    "chapter_outlines":  generated_text,
                    "structure_problems": structure_check_result,
                }
                structure_fix_prompt = PromptTemplate(
                    template=self.prompt_manager.create_chapter_outlines_structure_fix_prompt(), input_variables=["chapter_outlines", "structure_problems"]
                ).format(**structure_fix_variables)

                fixed_text = self.langchain_client.generate_text(structure_fix_prompt)
                if fixed_text:
                    generated_text = fixed_text
                    logger.info("Chapter Outlines structure fixed successfully.")
                else:
                    logger.error("Failed to fix Chapter Outlines structure.")
                    return None

            chapter_outlines = []
            try:
                chapter_splits = generated_text.strip().split("Chapter ")
                for i, chapter_text in enumerate(chapter_splits[1:], start=1):
                    chapter_summary = chapter_text.split("Chapter")[0].strip()
                    chapter_outlines.append(
                        ChapterOutline(chapter_number=i, summary=chapter_summary)
                    )
                logger.info(
                    "%d chapter outlines generated successfully.",
                    len(chapter_outlines),
                )
                return chapter_outlines
            except (TypeError, ValueError) as e:
                logger.error("Error processing ChapterOutline responses: %s", e)
                logger.debug("Raw LLM response: %s", generated_text)
                return None

        except Exception as e:
            logger.error(f"Error generating chapter outlines: {e}")
            return None

    def enhance_chapter_outlines(
        self, current_outlines: List[ChapterOutline]
    ) -> List[ChapterOutline] | None:
        """
        Enhances existing chapter outlines using a Langchain chain for critique and rewrite.
        """
        try:
            # Convert ChapterOutline objects to text
            outline_texts = [f"Chapter {co.chapter_number}:\n{co.summary}" for co in current_outlines]
            current_outlines_text = "\n\n".join(outline_texts)

            # Define prompt templates for critique and rewrite
            critique_prompt_template = self.prompt_manager.create_chapter_outlines_critique_prompt()
            rewrite_prompt_template = self.prompt_manager.create_chapter_outlines_rewrite_prompt()

            # Prepare variables for the prompts
            variables = {
                "current_outlines": current_outlines_text,
            }

            # Generate actionable critique using Langchain
            critique = self.langchain_client.create_actionable_critique(
                current_outlines_text, variables, critique_prompt_template
            )

            if critique:
                # Rewrite content based on the critique using Langchain
                enhanced_outlines_text = self.langchain_client.rewrite_content(
                    current_outlines_text, critique, variables, rewrite_prompt_template
                )

                if enhanced_outlines_text:
                    enhanced_chapter_outlines = []
                    try:
                        chapter_splits = enhanced_outlines_text.strip().split("Chapter ")
                        for i, chapter_text in enumerate(chapter_splits[1:], start=1):
                            chapter_summary = chapter_text.split("Chapter")[0].strip()
                            enhanced_chapter_outlines.append(
                                ChapterOutline(chapter_number=i, summary=chapter_summary)
                            )
                        logger.info("Chapter outlines enhanced successfully using Langchain.")
                        return enhanced_chapter_outlines
                    except (TypeError, ValueError) as e:
                        logger.error(f"Error processing enhanced ChapterOutline responses: {e}")
                        logger.debug("Raw LLM response: %s", enhanced_outlines_text)
                        return None
                else:
                    logger.error("Failed to rewrite chapter outlines using Langchain.")
                    return None
            else:
                logger.error("Failed to generate critique for chapter outlines using Langchain.")
                return None

        except Exception as e:
            logger.error(f"Error enhancing chapter outlines: {e}")
            return None

    def generate_scene_outlines(
        self, chapter_outline: ChapterOutline, num_scenes: int
    ) -> List[SceneOutline] | None:
        """
        Generates scene outlines for a given chapter outline and desired number of scenes, using Langchain for generation and structure validation.
        """
        try:
            generation_prompt_template = self.prompt_manager.create_scene_outlines_generation_prompt()
            structure_check_prompt_template = self.prompt_manager.create_scene_outlines_structure_check_prompt()

            variables = {
                "chapter_outline": chapter_outline.summary,
                "num_scenes_per_chapter": str(num_scenes),
            }

            generated_text = self.langchain_client.generate_text(
                PromptTemplate(template=generation_prompt_template, input_variables=["chapter_outline", "num_scenes_per_chapter"]).format(**variables)
            )

            if not generated_text:
                logger.error("Failed to generate scene outlines using Langchain.")
                return None

            # Structure Check
            structure_check_variables = {"scene_outlines": generated_text}
            structure_check_prompt = PromptTemplate(
                template=structure_check_prompt_template, input_variables=["scene_outlines"]
            ).format(**structure_check_variables)
            structure_check_result = self.langchain_client.generate_text(structure_check_prompt)

            if structure_check_result != "STRUCTURE_OK":
                logger.warning("Scene outlines structure check failed. Attempting to fix...")
                # Attempting to fix the structure
                structure_fix_variables = {
                    "scene_outlines": generated_text,
                    "structure_problems": structure_check_result,
                }
                structure_fix_prompt = PromptTemplate(
                    template=self.prompt_manager.create_scene_outlines_structure_fix_prompt(), input_variables=["scene_outlines", "structure_problems"]
                ).format(**structure_fix_variables)

                fixed_text = self.langchain_client.generate_text(structure_fix_prompt)
                if fixed_text:
                    generated_text = fixed_text
                    logger.info("Scene outlines structure fixed successfully.")
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

    def enhance_scene_outlines(
        self, current_outlines: List[SceneOutline]
    ) -> List[SceneOutline] | None:
        """
        Enhances existing scene outlines using the LLM.

        Uses the PromptManager to create an enhancement prompt and the OllamaClient
        to generate enhanced scene outlines text. Parses the generated text into a list of SceneOutline objects.

        Args:
            current_outlines (List[SceneOutline]): The current list of SceneOutline objects to be enhanced.

        Returns:
            List[SceneOutline] | None: A list of SceneOutline objects if successful, None otherwise.
        """
        outline_texts = [
            f"Scene {so.scene_number}:\n{so.summary}" for so in current_outlines
        ]
        prompt = self.prompt_manager.create_enhance_scene_outlines_prompt(outline_texts)
        generated_text = self.llm_client.generate_text(
            st.session_state.selected_model, prompt
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

    def generate_scene_part(
        self,
        scene_outline: SceneOutline,
        part_number: int,
        book_spec: BookSpec,
        chapter_outline: ChapterOutline,
        scene_outline_full: SceneOutline,
    ) -> str | None:
        """
        Generates a part of a scene's text content using the LLM.

        Uses the PromptManager to create a scene part prompt and the OllamaClient
        to generate the text content for that part of the scene.

        Args:
            scene_outline (SceneOutline): The SceneOutline object for the current scene part.
            part_number (int): The part number of the scene (e.g., 1, 2, 3 for beginning, middle, end).
            book_spec (BookSpec): The BookSpec object for overall context.
            chapter_outline (ChapterOutline): The ChapterOutline object for chapter context.
            scene_outline_full (SceneOutline): The full SceneOutline object for scene context.

        Returns:
            str | None: The generated text content for the scene part if successful, None otherwise.
        """
        try:
            generation_prompt_template = self.prompt_manager.create_scene_part_generation_prompt()
            structure_check_prompt_template = self.prompt_manager.create_scene_part_structure_check_prompt()
            structure_fix_prompt_template = self.prompt_manager.create_scene_part_structure_fix_prompt()

            variables = {
                "scene_outline": scene_outline.summary,
                "part_number": str(part_number),
                "book_spec_text": book_spec.model_dump_json(indent=4),
                "chapter_outline": chapter_outline.summary,
                "scene_outline_full": scene_outline_full.summary,
            }

            generated_text = self.langchain_client.generate_text(
                PromptTemplate(template=generation_prompt_template, input_variables=["scene_outline", "part_number", "book_spec_text", "chapter_outline", "scene_outline_full"]).format(**variables)
            )

            if not generated_text:
                logger.error("Failed to generate scene part using Langchain.")
                return None

            # Structure Check
            structure_check_variables = {"scene_part": generated_text}
            structure_check_prompt = PromptTemplate(
                template=structure_check_prompt_template, input_variables=["scene_part"]
            ).format(**structure_check_variables)
            structure_check_result = self.langchain_client.generate_text(structure_check_prompt)

            if structure_check_result != "STRUCTURE_OK":
                logger.warning("Scene Part structure check failed. Attempting to fix...")
                # Structure Fix
                structure_fix_variables = {
                    "scene_part": generated_text,
                    "structure_problems": structure_check_result,
                }
                structure_fix_prompt = PromptTemplate(
                    template=self.prompt_manager.create_scene_part_structure_fix_prompt(), input_variables=["scene_part", "structure_problems"]
                ).format(**structure_fix_variables)

                fixed_text = self.langchain_client.generate_text(structure_fix_prompt)
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

    def enhance_scene_part(
        self,
        scene_part: str,
        part_number: int,
        book_spec: BookSpec,
        chapter_outline: ChapterOutline,
        scene_outline_full: SceneOutline,
    ) -> str | None:
        """
        Enhances an existing scene part's text content using the LLM, utilizing a Langchain chain for critique and rewrite.

        Args:
            scene_part (str): The current text content of the scene part.
            part_number (int): The part number of the scene.
            book_spec (BookSpec): The BookSpec object for overall context.
            chapter_outline (ChapterOutline): The ChapterOutline object for chapter context.
            scene_outline_full (SceneOutline): The full SceneOutline object for scene context.

        Returns:
            str | None: The enhanced text content for the scene part if successful, None otherwise.
        """

        try:
            # Get prompt templates from PromptManager
            critique_prompt_template = self.prompt_manager.create_scene_part_critique_prompt()
            rewrite_prompt_template = self.prompt_manager.create_scene_part_rewrite_prompt()

            # Prepare variables for the prompts
            variables = {
                "book_spec": book_spec.model_dump_json(indent=4),
                "chapter_outline": chapter_outline.summary,
                "scene_outline_full": scene_outline_full.summary,
                "part_number": str(part_number),
            }

            # Generate actionable critique using Langchain
            critique = self.langchain_client.create_actionable_critique(
                scene_part, variables, critique_prompt_template
            )

            if critique:
                # Rewrite content based on the critique using Langchain
                enhanced_scene_part = self.langchain_client.rewrite_content(
                    scene_part, critique, variables, rewrite_prompt_template
                )

                if enhanced_scene_part:
                    logger.info("Scene part %d enhanced successfully using Langchain.", part_number)
                    return enhanced_scene_part
                else:
                    logger.error("Failed to rewrite scene part %d using Langchain.", part_number)
                    # Fallback to original implementation if rewrite fails
                    logger.info("Falling back to original enhance_scene_part implementation.")
                    prompt = self.prompt_manager.create_enhance_scene_part_prompt(
                        scene_part,
                        part_number,
                        book_spec,
                        chapter_outline.summary,
                        scene_outline_full.summary,
                    )
                    enhanced_scene_part = self.llm_client.generate_text(
                        st.session_state.selected_model, prompt
                    )
                    if enhanced_scene_part:
                        logger.info("Scene part %d enhanced successfully using original implementation.", part_number)
                        return enhanced_scene_part
                    else:
                         logger.error("Failed to enhance scene part %d using original implementation.", part_number)
                         return None
            else:
                logger.error("Failed to generate critique for scene part %d using Langchain.", part_number)
                # Fallback to original implementation if critique fails
                logger.info("Falling back to original enhance_scene_part implementation.")
                prompt = self.prompt_manager.create_enhance_scene_part_prompt(
                    scene_part,
                    part_number,
                    book_spec,
                    chapter_outline.summary,
                    scene_outline_full.summary,
                )
                enhanced_scene_part = self.llm_client.generate_text(
                    st.session_state.selected_model, prompt
                    ) # Corrected line: added closing parenthesis here
                if enhanced_scene_part:
                    logger.info("Scene part %d enhanced successfully using original implementation.", part_number)
                    return enhanced_scene_part
                else:
                     logger.error("Failed to enhance scene part %d using original implementation.", part_number)
                     return None

        except Exception as e:
            logger.error(f"Error enhancing scene part {part_number}: {e}")
            # Fallback to original implementation if any exception occurs
            logger.info("Falling back to original enhance_scene_part implementation due to exception.")
            prompt = self.prompt_manager.create_enhance_scene_part_prompt(
                scene_part,
                part_number,
                book_spec,
                chapter_outline.summary,
                scene_outline_full.summary,
            )
            enhanced_scene_part = self.llm_client.generate_text(
                st.session_state.selected_model, prompt
            )
            if enhanced_scene_part:
                logger.info("Scene part %d enhanced successfully using original implementation.", part_number)
                return enhanced_scene_part
            else:
                logger.error("Failed to enhance scene part %d using original implementation.", part_number)
                return None