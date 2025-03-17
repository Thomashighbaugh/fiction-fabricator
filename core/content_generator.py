# core/content_generator.py
from typing import Optional, List

import tomli
import tomli_w

from core.book_spec import BookSpec
from core.plot_outline import PlotOutline, ChapterOutline, SceneOutline
from core.content_generation.content_generation_utils import ChapterOutlineMethod

from llm.llm_client import OllamaClient
from llm.prompt_manager import PromptManager
from utils.logger import logger

# Import the generation functions from their respective modules
from core.content_generation.book_spec_generation import (
    generate_book_spec,
    enhance_book_spec,
)
from core.content_generation.plot_outline_generation import (
    generate_plot_outline,
    enhance_plot_outline,
)
from core.content_generation.chapter_outline_generation import (
    generate_chapter_outlines,
    enhance_chapter_outlines,
    generate_chapter_outline_27_method,
    enhance_chapter_outlines_27_method,
)
from core.content_generation.scene_outline_generation import (
    generate_scene_outlines,
    enhance_scene_outlines,
)
from core.content_generation.scene_part_generation import (
    generate_scene_part,
    enhance_scene_part,
)


class ContentGenerator:
    """
    Central class to manage content generation using Ollama.
    """

    def __init__(self, prompt_manager: PromptManager, model_name: str):
        self.prompt_manager = prompt_manager
        self.ollama_client = OllamaClient()
        self.model_name = model_name

    async def _validate_and_correct_toml(
        self, toml_string: str, schema: str
    ) -> str | None:
        """
        Validates and corrects a TOML string against a schema. (Internal helper)
        """
        max_attempts = 3
        for attempt in range(max_attempts):
            # Initialize variables *before* the try block

            try:
                tomli.loads(toml_string)  # Attempt to parse
                return toml_string  # If successful, return original string
            except tomli.TOMLDecodeError as e:
                error_message = str(e)
                logger.warning(
                    f"TOML validation attempt {attempt+1}/{max_attempts} failed: {e}"
                )
                if attempt + 1 == max_attempts:  # Last attempt
                    logger.error(
                        f"TOML validation failed after {max_attempts} attempts."
                    )
                    return None
            # Generate correction prompt.  First, get the TEMPLATE:
            validation_prompt_template = (
                self.prompt_manager.create_book_spec_validation_prompt()
            )
            # NOW call the template with the variables:
            variables = {
                "toml_string": toml_string,
                "error_message": error_message,
                "schema": schema,
            }  # Now it is defined
            correction_prompt_str = validation_prompt_template(**variables)
            # The rest remains the same, but it's outside the except, so
            # variables *must* be initialized by this point.
            if attempt < max_attempts - 1:  # only if it is not the last attempt
                # Get corrected TOML from LLM
                corrected_toml = await self.ollama_client.generate_text(
                    model_name=self.model_name,
                    prompt=correction_prompt_str,
                )
                if not corrected_toml:
                    logger.error(
                        f"TOML correction attempt {attempt+1}/{max_attempts} failed: Empty response from LLM."
                    )
                    return None
                toml_string = corrected_toml  # Use corrected TOML for next attempt
        return None  # Should not reach here, kept for type consistency

    # --- Book Spec Generation ---
    async def generate_book_spec(self, idea: str, session_state) -> Optional[BookSpec]:
        return await generate_book_spec(self, idea)

    async def enhance_book_spec(
        self, current_spec: BookSpec, session_state
    ) -> Optional[BookSpec]:
        return await enhance_book_spec(self, current_spec)

    # --- Plot Outline Generation ---
    async def generate_plot_outline(
        self, book_spec: BookSpec, session_state
    ) -> Optional[PlotOutline]:
        return await generate_plot_outline(self, book_spec)

    async def enhance_plot_outline(
        self, current_outline: PlotOutline, session_state
    ) -> Optional[PlotOutline]:
        return await enhance_plot_outline(self, current_outline)

    # --- Chapter Outline Generation ---
    async def generate_chapter_outlines(
        self, plot_outline: PlotOutline, session_state
    ) -> Optional[List[ChapterOutline]]:
        return await generate_chapter_outlines(self, plot_outline)

    async def enhance_chapter_outlines(
        self, current_outlines: List[ChapterOutline], session_state
    ) -> Optional[List[ChapterOutline]]:
        return await enhance_chapter_outlines(self, current_outlines)

    async def generate_chapter_outline_27_method(
        self, book_spec: BookSpec, session_state
    ) -> Optional[List[ChapterOutlineMethod]]:
        return await generate_chapter_outline_27_method(self, book_spec)

    async def enhance_chapter_outlines_27_method(
        self, current_outlines: List[ChapterOutlineMethod], session_state
    ) -> Optional[List[ChapterOutlineMethod]]:
        return await enhance_chapter_outlines_27_method(self, current_outlines)

    # --- Scene Outline Generation ---
    async def generate_scene_outlines(
        self, chapter_outline: ChapterOutline, num_scenes: int, session_state
    ) -> Optional[List[SceneOutline]]:
        return await generate_scene_outlines(self, chapter_outline, num_scenes)

    async def enhance_scene_outlines(
        self, current_outlines: List[SceneOutline], session_state
    ) -> Optional[List[SceneOutline]]:
        return await enhance_scene_outlines(self, current_outlines)

    # --- Scene Part Generation ---

    async def generate_scene_part(
        self,
        scene_outline: SceneOutline,
        part_number: int,
        book_spec: BookSpec,
        chapter_outline: ChapterOutline,
        scene_outline_full: SceneOutline,
        session_state,
    ) -> Optional[str]:
        return await generate_scene_part(
            self,
            scene_outline,
            part_number,
            book_spec,
            chapter_outline,
            scene_outline_full,
        )

    async def enhance_scene_part(
        self,
        scene_part: str,
        part_number: int,
        book_spec: BookSpec,
        chapter_outline: ChapterOutline,
        scene_outline_full: SceneOutline,
        session_state,
    ) -> Optional[str]:
        return await enhance_scene_part(
            self,
            scene_part,
            part_number,
            book_spec,
            chapter_outline,
            scene_outline_full,
        )
