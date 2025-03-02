# /home/tlh/refactored_gui_fict_fab/core/content_generation/scene_part_generator.py
from typing import Optional

from core.content_generation.base_generator import BaseContentGenerator
from core.plot_outline import SceneOutline, ChapterOutline
from core.book_spec import BookSpec

# from llm.prompt_manager.scene_part_prompts import ScenePartPrompts # Removed incorrect import
from utils.logger import logger


class ScenePartGenerator(BaseContentGenerator):
    """
    Content generator for scene parts, which are sections of text within a scene.

    Inherits from BaseContentGenerator and provides functionality to generate
    and enhance individual parts of a scene's narrative.
    """

    def __init__(self, prompt_manager, model_name: str):
        """
        Initializes ScenePartGenerator with prompt manager and model name.
        """
        super().__init__(prompt_manager, model_name)
        # self.prompts = ScenePartPrompts(prompt_manager) # Removed incorrect instantiation
        # self.prompts = prompt_manager # This was also incorrect, should not reassign prompt_manager
        pass  # No need to initialize prompts here anymore, PromptManager handles it

    async def generate(
        self,
        scene_outline: SceneOutline,
        part_number: int,
        book_spec: BookSpec,
        chapter_outline: ChapterOutline,
        scene_outline_full: SceneOutline,
    ) -> Optional[str]:
        """
        Generates a part of a scene's text content.
        """
        generation_prompt_template = self.prompt_manager.get_prompt(
            "scene_part_generation_prompt"
        )
        variables = {
            "scene_outline": scene_outline.summary,
            "part_number": str(part_number),
            "book_spec_text": book_spec.model_dump_json(indent=4),
            "chapter_outline": chapter_outline.summary,
            "scene_outline_full": scene_outline_full.summary,
        }
        generated_text = await self._generate_content_from_prompt(
            generation_prompt_template, variables
        )
        if not generated_text:
            return None

        structure_check_prompt_template = self.prompt_manager.get_prompt(
            "scene_part_structure_check_prompt"
        )
        structure_fix_prompt_template = self.prompt_manager.get_prompt(
            "scene_part_structure_fix_prompt"
        )
        validated_text = await self._structure_check_and_fix(
            generated_text,
            structure_check_prompt_template,
            structure_fix_prompt_template,
        )
        if not validated_text:
            return None

        return self._parse_response(validated_text)

    async def enhance(
        self,
        current_content: str,  # Parameter name consistent with base class - now current_content
        part_number: int,
        book_spec: BookSpec,
        chapter_outline: ChapterOutline,
        scene_outline_full: SceneOutline,
    ) -> Optional[str]:
        """
        Enhances an existing scene part's text content.
        """
        critique_prompt_template = self.prompt_manager.get_prompt(
            "scene_part_critique_prompt"
        )
        rewrite_prompt_template = self.prompt_manager.get_prompt(
            "scene_part_rewrite_prompt"
        )
        variables = {
            "book_spec": book_spec.model_dump_json(indent=4),
            "chapter_outline": chapter_outline.summary,
            "scene_outline_full": scene_outline_full.summary,
            "part_number": str(part_number),
        }
        critique_variables = {
            **variables,
            "content": current_content,
        }  # Now using current_content

        critique_text = await self._generate_content_from_prompt(
            critique_prompt_template, critique_variables
        )
        if not critique_text:
            return None

        rewrite_variables = {
            **variables,
            "critique": critique_text,
            "content": current_content,  # Now using current_content
        }
        enhanced_part_text = await self._generate_content_from_prompt(
            rewrite_prompt_template, rewrite_variables
        )
        if not enhanced_part_text:
            return None

        return self._parse_response(enhanced_part_text)

    def _parse_response(self, response_text: str) -> Optional[str]:
        """
        Parses the LLM response text for a scene part.
        """
        if (
            response_text and response_text.strip()
        ):  # Check for non-empty and non-whitespace
            return response_text.strip()  # Return text content, stripping whitespace
        else:
            logger.warning(
                "LLM response for scene part was empty or only whitespace."
            )  # warning style

            return None  # Handle empty or whitespace-only response
