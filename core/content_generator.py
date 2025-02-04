# core/content_generator.py
import json
from typing import List

from core.book_spec import BookSpec
from core.plot_outline import ChapterOutline, PlotOutline, SceneOutline
from llm.llm_client import OllamaClient
from llm.prompt_manager import PromptManager
from utils.logger import logger
from pydantic import ValidationError
from utils.config import config


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

    def generate_book_spec(self, idea: str) -> BookSpec | None:
        """
        Generates a BookSpec object based on a user-provided story idea.

        Uses the PromptManager to create a book specification prompt and the OllamaClient
        to generate the book specification text. Parses the generated text into a BookSpec object.

        Args:
            idea (str): The user's initial story idea.

        Returns:
            BookSpec | None: A BookSpec object if generation is successful, None otherwise.
        """
        prompt = self.prompt_manager.create_book_spec_prompt(idea)
        generated_text = self.llm_client.generate_text(config.ollama_model_name, prompt)
        if generated_text:
            try:
                book_spec_data = json.loads(generated_text)
                book_spec = BookSpec(**book_spec_data)
                logger.info("Book specification generated successfully.")
                return book_spec
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON response for BookSpec: {e}")
                logger.debug(f"Raw LLM response: {generated_text}")
            except ValidationError as e:
                logger.error(f"Error validating BookSpec: {e}")
                logger.debug(f"Raw LLM response: {generated_text}")
            except Exception as e:
                logger.error(f"Unexpected error processing BookSpec response: {e}")
                logger.debug(f"Raw LLM response: {generated_text}")
        return None

    def enhance_book_spec(self, current_spec: BookSpec) -> BookSpec | None:
        """
        Enhances an existing BookSpec object using the LLM.

        Uses the PromptManager to create an enhancement prompt and the OllamaClient
        to generate enhanced book specification text. Parses the enhanced text into a BookSpec object.

        Args:
            current_spec (BookSpec): The current BookSpec object to be enhanced.

        Returns:
            BookSpec | None: An enhanced BookSpec object if successful, None otherwise.
        """
        prompt = self.prompt_manager.create_enhance_book_spec_prompt(current_spec)
        generated_text = self.llm_client.generate_text(config.get_ollama_model_name(), prompt)
        if generated_text:
            try:
                book_spec_data = json.loads(generated_text)
                enhanced_spec = BookSpec(**book_spec_data)
                logger.info("Book specification enhanced successfully.")
                return enhanced_spec
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON response for enhanced BookSpec: {e}")
                logger.debug(f"Raw LLM response: {generated_text}")
            except ValidationError as e:
                logger.error(f"Error validating enhanced BookSpec: {e}")
                logger.debug(f"Raw LLM response: {generated_text}")
            except Exception as e:
                logger.error(f"Unexpected error processing enhanced BookSpec response: {e}")
                logger.debug(f"Raw LLM response: {generated_text}")
        return None

    def generate_plot_outline(self, book_spec: BookSpec) -> PlotOutline | None:
        """
        Generates a PlotOutline object based on a BookSpec.

        Uses the PromptManager to create a plot outline prompt and the OllamaClient
        to generate the plot outline text. Parses the generated text into a PlotOutline object.

        Args:
            book_spec (BookSpec): The BookSpec object to base the plot outline on.

        Returns:
            PlotOutline | None: A PlotOutline object if successful, None otherwise.
        """
        prompt = self.prompt_manager.create_plot_outline_prompt(book_spec)
        generated_text = self.llm_client.generate_text(config.get_ollama_model_name(), prompt)
        if generated_text:
            try:
                plot_outline = PlotOutline(act_one="", act_two="", act_three="")
                acts = generated_text.split("Act ")
                if len(acts) >= 4:
                    plot_outline.act_one = acts[1].split("Act")[0].strip()
                    plot_outline.act_two = acts[2].split("Act")[0].strip()
                    plot_outline.act_three = acts[3].strip()
                else:
                    logger.warning("Unexpected plot outline format from LLM, basic parsing failed.")
                    plot_outline.act_one = generated_text

                logger.info("Plot outline generated successfully.")
                return plot_outline
            except Exception as e:
                logger.error(f"Error processing PlotOutline response: {e}")
                logger.debug(f"Raw LLM response: {generated_text}")
        return None

    def enhance_plot_outline(self, current_outline: str) -> PlotOutline | None:
        """
        Enhances an existing plot outline using the LLM.

        Uses the PromptManager to create an enhancement prompt and the OllamaClient
        to generate enhanced plot outline text. Parses the enhanced text into a PlotOutline object.

        Args:
            current_outline (str): The current plot outline text to be enhanced.

        Returns:
            PlotOutline | None: An enhanced PlotOutline object if successful, None otherwise.
        """
        prompt = self.prompt_manager.create_enhance_plot_outline_prompt(current_outline)
        generated_text = self.llm_client.generate_text(config.get_ollama_model_name(), prompt)
        if generated_text:
            try:
                plot_outline = PlotOutline(act_one="", act_two="", act_three="")
                acts = generated_text.split("Act ")
                if len(acts) >= 4:
                    plot_outline.act_one = acts[1].split("Act")[0].strip()
                    plot_outline.act_two = acts[2].split("Act")[0].strip()
                    plot_outline.act_three = acts[3].strip()
                else:
                    logger.warning("Unexpected enhanced plot outline format from LLM, basic parsing failed.")
                    plot_outline.act_one = generated_text

                logger.info("Plot outline enhanced successfully.")
                return plot_outline
            except Exception as e:
                logger.error(f"Error processing enhanced PlotOutline response: {e}")
                logger.debug(f"Raw LLM response: {generated_text}")
        return None

    def generate_chapter_outlines(self, plot_outline: PlotOutline, num_chapters: int) -> List[ChapterOutline] | None:
        """
        Generates chapter outlines based on a PlotOutline and the desired number of chapters.

        Uses the PromptManager to create a chapter outlines prompt and the OllamaClient
        to generate the chapter outlines text. Parses the generated text into a list of ChapterOutline objects.

        Args:
            plot_outline (PlotOutline): The PlotOutline object to base chapter outlines on.
            num_chapters (int): The desired number of chapters.

        Returns:
            List[ChapterOutline] | None: A list of ChapterOutline objects if successful, None otherwise.
        """
        plot_outline_text = "\n".join([
            "Act One:\n" + plot_outline.act_one,
            "Act Two:\n" + plot_outline.act_two,
            "Act Three:\n" + plot_outline.act_three
        ])
        prompt = self.prompt_manager.create_chapter_outlines_prompt(plot_outline_text, num_chapters)
        generated_text = self.llm_client.generate_text(config.get_ollama_model_name(), prompt)
        if generated_text:
            chapter_outlines = []
            try:
                chapter_splits = generated_text.strip().split("Chapter ")
                for i, chapter_text in enumerate(chapter_splits[1:], start=1):
                    chapter_summary = chapter_text.split("Chapter")[0].strip()
                    chapter_outlines.append(ChapterOutline(chapter_number=i, summary=chapter_summary))
                logger.info(f"{len(chapter_outlines)} chapter outlines generated successfully.")
                return chapter_outlines
            except Exception as e:
                logger.error(f"Error processing ChapterOutline responses: {e}")
                logger.debug(f"Raw LLM response: {generated_text}")
        return None

    def enhance_chapter_outlines(self, current_outlines: List[ChapterOutline]) -> List[ChapterOutline] | None:
        """
        Enhances existing chapter outlines using the LLM.

        Uses the PromptManager to create an enhancement prompt and the OllamaClient
        to generate enhanced chapter outlines text. Parses the enhanced text into a list of ChapterOutline objects.

        Args:
            current_outlines (List[ChapterOutline]): The current list of ChapterOutline objects to be enhanced.

        Returns:
            List[ChapterOutline] | None: An enhanced list of ChapterOutline objects if successful, None otherwise.
        """
        outline_texts = [f"Chapter {co.chapter_number}:\n{co.summary}" for co in current_outlines]
        prompt = self.prompt_manager.create_enhance_chapter_outlines_prompt(outline_texts)
        generated_text = self.llm_client.generate_text(config.get_ollama_model_name(), prompt)
        if generated_text:
            enhanced_chapter_outlines = []
            try:
                chapter_splits = generated_text.strip().split("Chapter ")
                for i, chapter_text in enumerate(chapter_splits[1:], start=1):
                    chapter_summary = chapter_text.split("Chapter")[0].strip()
                    enhanced_chapter_outlines.append(ChapterOutline(chapter_number=i, summary=chapter_summary))
                logger.info("Chapter outlines enhanced successfully.")
                return enhanced_chapter_outlines
            except Exception as e:
                logger.error(f"Error processing enhanced ChapterOutline responses: {e}")
                logger.debug(f"Raw LLM response: {generated_text}")
        return None

    def generate_scene_outlines(self, chapter_outline: ChapterOutline, num_scenes_per_chapter: int) -> List[SceneOutline] | None:
        """
        Generates scene outlines for a given chapter outline and desired number of scenes per chapter.

        Uses the PromptManager to create a scene outlines prompt and the OllamaClient
        to generate the scene outlines text. Parses the generated text into a list of SceneOutline objects.

        Args:
            chapter_outline (ChapterOutline): The ChapterOutline object to base scene outlines on.
            num_scenes_per_chapter (int): The desired number of scenes per chapter.

        Returns:
            List[SceneOutline] | None: A list of SceneOutline objects if successful, None otherwise.
        """
        prompt = self.prompt_manager.create_scene_outlines_prompt(chapter_outline.summary, num_scenes_per_chapter)
        generated_text = self.llm_client.generate_text(config.get_ollama_model_name(), prompt)
        if generated_text:
            scene_outlines = []
            try:
                scene_splits = generated_text.strip().split("Scene ")
                for i, scene_text in enumerate(scene_splits[1:], start=1):
                    scene_summary = scene_text.split("Scene")[0].strip()
                    scene_outlines.append(SceneOutline(scene_number=i, summary=scene_summary))
                logger.info(f"{len(scene_outlines)} scene outlines generated for chapter {chapter_outline.chapter_number} successfully.")
                return scene_outlines
            except Exception as e:
                logger.error(f"Error processing SceneOutline responses: {e}")
                logger.debug(f"Raw LLM response: {generated_text}")
        return None

    def enhance_scene_outlines(self, current_outlines: List[SceneOutline]) -> List[SceneOutline] | None:
        """
        Enhances existing scene outlines using the LLM.

        Uses the PromptManager to create an enhancement prompt and the OllamaClient
        to generate enhanced scene outlines text. Parses the enhanced text into a list of SceneOutline objects.

        Args:
            current_outlines (List[SceneOutline]): The current list of SceneOutline objects to be enhanced.

        Returns:
            List[SceneOutline] | None: An enhanced list of SceneOutline objects if successful, None otherwise.
        """
        outline_texts = [f"Scene {so.scene_number}:\n{so.summary}" for so in current_outlines]
        prompt = self.prompt_manager.create_enhance_scene_outlines_prompt(outline_texts)
        generated_text = self.llm_client.generate_text(config.get_ollama_model_name(), prompt)
        if generated_text:
            enhanced_scene_outlines = []
            try:
                scene_splits = generated_text.strip().split("Scene ")
                for i, scene_text in enumerate(scene_splits[1:], start=1):
                    scene_summary = scene_text.split("Scene")[0].strip()
                    enhanced_scene_outlines.append(SceneOutline(scene_number=i, summary=scene_summary))
                logger.info("Scene outlines enhanced successfully.")
                return enhanced_scene_outlines
            except Exception as e:
                logger.error(f"Error processing enhanced SceneOutline responses: {e}")
                logger.debug(f"Raw LLM response: {generated_text}")
        return None

    def generate_scene_part(
        self, scene_outline: SceneOutline, part_number: int, book_spec: BookSpec, chapter_outline: ChapterOutline, scene_outline_full: SceneOutline
    ) -> str | None:
        """
        Generates a part of a scene's text content using the LLM.

        Uses the PromptManager to create a scene part prompt and the OllamaClient
        to generate the text content for that part of the scene.

        Args:
            scene_outline (SceneOutline): The SceneOutline object for the current scene part.
            part_number (int): The part number of the scene (e.g., 1, 2, 3).
            book_spec (BookSpec): The BookSpec object for overall context.
            chapter_outline (ChapterOutline): The ChapterOutline object for chapter context.
            scene_outline_full (SceneOutline): The full SceneOutline object for scene context.

        Returns:
            str | None: The generated text content for the scene part if successful, None otherwise.
        """
        prompt = self.prompt_manager.create_scene_part_prompt(
            scene_outline.summary, part_number, book_spec, chapter_outline.summary, scene_outline_full.summary
        )
        generated_text = self.llm_client.generate_text(config.get_ollama_model_name(), prompt)
        if generated_text:
            logger.info("Scene part %d generated successfully.", part_number)
            return generated_text
        return None

    def enhance_scene_part(
        self, scene_part: str, part_number: int, book_spec: BookSpec, chapter_outline: ChapterOutline, scene_outline_full: SceneOutline
    ) -> str | None:
        """
        Enhances an existing scene part's text content using the LLM.

        Uses the PromptManager to create an enhancement prompt and the OllamaClient
        to generate enhanced text content for the scene part.

        Args:
            scene_part (str): The current text content of the scene part.
            part_number (int): The part number of the scene.
            book_spec (BookSpec): The BookSpec object for overall context.
            chapter_outline (ChapterOutline): The ChapterOutline object for chapter context.
            scene_outline_full (SceneOutline): The full SceneOutline object for scene context.

        Returns:
            str | None: The enhanced text content for the scene part if successful, None otherwise.
        """
        prompt = self.prompt_manager.create_enhance_scene_part_prompt(
            scene_part, part_number, book_spec, chapter_outline.summary, scene_outline_full.summary
        )
        generated_text = self.llm_client.generate_text(config.get_ollama_model_name(), prompt)
        if generated_text:
            logger.info("Scene part %d enhanced successfully.", part_number)
            return generated_text
        return None