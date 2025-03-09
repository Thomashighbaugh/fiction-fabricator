# core/content_generator.py
from typing import List, Optional
from pydantic import ValidationError
import tomli
import tomli_w

from core.book_spec import BookSpec
from core.content_generation.book_spec_generation import (
    enhance_book_spec as _enhance_book_spec,
)
from core.content_generation.book_spec_generation import (
    generate_book_spec as _generate_book_spec,
)
from core.content_generation.chapter_outline_generation import (
    enhance_chapter_outlines as _enhance_chapter_outlines,
)
from core.content_generation.chapter_outline_generation import (
    enhance_chapter_outlines_27_method as _enhance_chapter_outlines_27_method,
)
from core.content_generation.chapter_outline_generation import (
    generate_chapter_outline_27_method as _generate_chapter_outline_27_method,
)
from core.content_generation.chapter_outline_generation import (
    generate_chapter_outlines as _generate_chapter_outlines,
)
from core.content_generation.content_generation_utils import (
    ChapterOutline,
    ChapterOutlineMethod,
    PlotOutline,
    SceneOutline,
)
from core.content_generation.plot_outline_generation import (
    enhance_plot_outline as _enhance_plot_outline,
)
from core.content_generation.plot_outline_generation import (
    generate_plot_outline as _generate_plot_outline,
)
from core.content_generation.scene_outline_generation import (
    enhance_scene_outlines as _enhance_scene_outlines,
)
from core.content_generation.scene_outline_generation import (
    generate_scene_outlines as _generate_scene_outlines,
)
from core.content_generation.scene_part_generation import (
    enhance_scene_part as _enhance_scene_part,
)
from core.content_generation.scene_part_generation import (
    generate_scene_part as _generate_scene_part,
)
from llm.llm_client import OllamaClient
from utils.logger import logger
from utils.config import config  # For project saving


class ContentGenerator:
    """
    Orchestrates the content generation process for the novel.
    """

    plot_outline = PlotOutline
    chapter_outline = ChapterOutline
    scene_outline = SceneOutline
    chapter_outline_method = ChapterOutlineMethod

    def __init__(self, prompt_manager, model_name):
        """
        Initializes the ContentGenerator with a prompt manager and model name.
        """
        self.prompt_manager = prompt_manager
        self.model_name = model_name
        self.ollama_client = OllamaClient()
        logger.debug(f"ContentGenerator initializing with model_name: {model_name}")
        logger.debug("ContentGenerator.__init__ - OllamaClient initialized.")
        self.project_directory = config.get_project_directory()

    async def _validate_and_correct_toml(
        self, generated_text: str, expected_schema: str
    ) -> str | None:
        """
        Helper function to validate and correct TOML output.
        """
        validation_prompt = (
            f"Please validate and, if necessary, correct the following TOML to ensure it's valid "
            f"and conforms to the following schema:\n```toml\n{expected_schema}\n```\n"
            f"Input TOML:\n```toml\n{generated_text}\n```\n\n"
            f"Ensure that the output contains only the corrected TOML, with no additional text or explanations. "
            f"If the input is already valid, return the original input TOML unchanged."
        )
        validated_text = await self.ollama_client.generate_text(
            self.model_name, validation_prompt
        )
        return validated_text

    def _auto_save(self, session_state):
        """Helper function for auto-saving."""
        if session_state.project_name and session_state.new_project_requested:
            session_state.project_manager.save_project(
                project_name=session_state.project_name,
                story_idea=session_state.story_idea,
                book_spec=session_state.book_spec,
                plot_outline=session_state.plot_outline,
                chapter_outlines=session_state.chapter_outlines,
                chapter_outlines_27_method=session_state.chapter_outlines_27_method,
                scene_outlines=session_state.scene_outlines,
                scene_parts=session_state.scene_parts,
            )

    async def generate_book_spec(
        self, idea: str, session_state
    ) -> Optional[BookSpec]:  # Added session state
        book_spec = await _generate_book_spec(self, idea)
        if book_spec:  # Only update state and save if successful
            session_state.book_spec = book_spec
            self._auto_save(session_state)  # Auto save
        else:
            logger.error("generate_book_spec failed. Not updating session state.")
        return book_spec

    async def enhance_book_spec(
        self, current_spec: BookSpec, session_state
    ) -> Optional[BookSpec]:  # Added session state
        enhanced_spec = await _enhance_book_spec(self, current_spec)
        if enhanced_spec:
            session_state.book_spec = enhanced_spec
            self._auto_save(session_state)  # Auto save
        else:
            logger.error("enhance_book_spec failed. Not updating session state.")
        return enhanced_spec

    async def generate_plot_outline(
        self, book_spec: BookSpec, session_state
    ) -> Optional[PlotOutline]:  # Added session state
        plot_outline = await _generate_plot_outline(self, book_spec)
        if plot_outline:
            session_state.plot_outline = plot_outline
            self._auto_save(session_state)
        else:
            logger.error("generate_plot_outline failed. Not updating session state.")
        return plot_outline

    async def enhance_plot_outline(
        self, current_outline: PlotOutline, session_state
    ) -> Optional[PlotOutline]:  # Modified
        enhanced_outline = await _enhance_plot_outline(self, current_outline)
        if enhanced_outline:
            session_state.plot_outline = enhanced_outline
            self._auto_save(session_state)
        else:
            logger.error("enhance_plot_outline failed. Not updating session state.")
        return enhanced_outline

    async def generate_chapter_outlines(
        self, plot_outline: PlotOutline, session_state
    ) -> Optional[List[ChapterOutline]]:  # Added session state
        chapter_outlines = await _generate_chapter_outlines(self, plot_outline)
        if chapter_outlines:
            session_state.chapter_outlines = chapter_outlines
            self._auto_save(session_state)
        else:
            logger.error("generate_chapter_outlines failed.  Not updating session.")
        return chapter_outlines

    async def enhance_chapter_outlines(
        self, current_outlines: List[ChapterOutline], session_state
    ) -> Optional[List[ChapterOutline]]:  # Added session state
        enhanced_outlines = await _enhance_chapter_outlines(self, current_outlines)
        if enhanced_outlines:
            session_state.chapter_outlines = enhanced_outlines
            self._auto_save(session_state)
        else:
            logger.error("enhance_chapter_outlines failed. Not updating session state.")
        return enhanced_outlines

    async def generate_chapter_outline_27_method(
        self, book_spec: BookSpec, session_state
    ) -> Optional[List[ChapterOutlineMethod]]:  # Added session state
        chapter_outlines_27_method = await _generate_chapter_outline_27_method(
            self, book_spec
        )
        if chapter_outlines_27_method:
            session_state.chapter_outlines_27_method = chapter_outlines_27_method
            self._auto_save(session_state)
        else:
            logger.error(
                "generate_chapter_outline_27_method failed. Not updating session."
            )
        return chapter_outlines_27_method

    async def enhance_chapter_outlines_27_method(
        self, current_outlines: List[ChapterOutlineMethod], session_state
    ) -> Optional[List[ChapterOutlineMethod]]:  # Added session state
        enhanced_outlines = await _enhance_chapter_outlines_27_method(
            self, current_outlines
        )
        if enhanced_outlines:
            session_state.chapter_outlines_27_method = enhanced_outlines
            self._auto_save(session_state)
        else:
            logger.error(
                "enhance_chapter_outlines_27_method failed. Not updating session state"
            )
        return enhanced_outlines

    async def generate_scene_outlines(
        self, chapter_outline: ChapterOutline, num_scenes: int, session_state
    ) -> Optional[List[SceneOutline]]:  # Added session state
        scene_outlines = await _generate_scene_outlines(
            self, chapter_outline, num_scenes
        )
        if scene_outlines:
            session_state.scene_outlines[chapter_outline.chapter_number] = (
                scene_outlines
            )
            self._auto_save(session_state)
        else:
            logger.error("generate_scene_outlines failed. Not updating session state.")
        return scene_outlines

    async def enhance_scene_outlines(
        self, current_outlines: List[SceneOutline], session_state
    ) -> Optional[List[SceneOutline]]:  # Added session state
        enhanced_outlines = await _enhance_scene_outlines(self, current_outlines)
        if enhanced_outlines:
            # Assuming current_outlines belong to the current chapter
            if session_state.chapter_outlines_27_method:
                chapter_number = session_state.chapter_outlines_27_method[
                    session_state.current_chapter_index
                ].chapter_number
                session_state.scene_outlines[chapter_number] = enhanced_outlines
            self._auto_save(session_state)
        else:
            logger.error("enhance_scene_outlines failed. Not updating session state.")
        return enhanced_outlines

    async def generate_scene_part(
        self,
        scene_outline: SceneOutline,
        part_number: int,
        book_spec: BookSpec,
        chapter_outline: ChapterOutline,
        scene_outline_full: SceneOutline,
        session_state,  # Added session state
    ) -> Optional[str]:
        scene_part = await _generate_scene_part(
            self,
            scene_outline,
            part_number,
            book_spec,
            chapter_outline,
            scene_outline_full,
        )
        if scene_part:
            # Ensure the nested structure exists before saving
            session_state.scene_parts.setdefault(
                chapter_outline.chapter_number, {}
            ).setdefault(scene_outline.scene_number, {})[part_number] = scene_part
            self._auto_save(session_state)
        else:
            logger.error("generate_scene_part failed. Not updating session state.")
        return scene_part

    async def enhance_scene_part(
        self,
        scene_part: str,
        part_number: int,
        book_spec: BookSpec,
        chapter_outline: ChapterOutline,
        scene_outline_full: SceneOutline,
        session_state,  # Added session state
    ) -> Optional[str]:
        enhanced_scene_part = await _enhance_scene_part(
            self,
            scene_part,
            part_number,
            book_spec,
            chapter_outline,
            scene_outline_full,
        )
        if enhanced_scene_part:
            # Ensure the nested structure exists before saving
            session_state.scene_parts.setdefault(
                chapter_outline.chapter_number, {}
            ).setdefault(scene_outline.scene_number, {})[
                part_number
            ] = enhanced_scene_part
            self._auto_save(session_state)  # Auto Save
        else:
            logger.error("enhance_scene_part failed. Not updating session state.")
        return enhanced_scene_part
