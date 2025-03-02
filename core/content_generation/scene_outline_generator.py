# core/content_generation/scene_outline_generator.py
from typing import List, Optional

from core.content_generation.base_generator import BaseContentGenerator
from core.plot_outline import ChapterOutline, SceneOutline
from llm.prompt_manager.scene_outline_prompts import SceneOutlinePrompts
from utils.logger import logger


class SceneOutlineGenerator(BaseContentGenerator):
    """
    Content generator for SceneOutline objects.

    Inherits from BaseContentGenerator and specializes in generating
    and enhancing scene outlines for each chapter.
    """

    def __init__(self, prompt_manager, model_name: str):
        """
        Initializes SceneOutlineGenerator with prompt manager and model name.
        """
        super().__init__(prompt_manager, model_name)
        self.prompts = SceneOutlinePrompts(
            prompt_manager
        )  # Initialize scene outline specific prompts

    async def generate(
        self, chapter_outline: ChapterOutline, num_scenes: int
    ) -> Optional[List[SceneOutline]]:
        """
        Generates a list of SceneOutlines for a given ChapterOutline.
        """
        generation_prompt_template = (
            self.prompts.create_scene_outlines_generation_prompt()
        )
        variables = {
            "chapter_outline": chapter_outline.summary,
            "num_scenes_per_chapter": str(num_scenes),
        }
        generated_text = await self._generate_content_from_prompt(
            generation_prompt_template, variables
        )
        if not generated_text:
            return None

        structure_check_prompt_template = (
            self.prompts.create_scene_outlines_structure_check_prompt()
        )
        structure_fix_prompt_template = (
            self.prompts.create_scene_outlines_structure_fix_prompt()
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
        current_content: List[
            SceneOutline
        ],  # Parameter name consistent with base class
    ) -> Optional[List[SceneOutline]]:
        """
        Enhances a list of existing SceneOutline objects.
        """
        # Convert SceneOutline objects to text for critique and rewrite prompts
        outline_texts = [
            f"Scene {so.scene_number}:\n{so.summary}" for so in current_content
        ]
        current_outlines_text = "\n\n".join(outline_texts)

        critique_prompt_template = self.prompts.create_scene_outlines_critique_prompt()
        rewrite_prompt_template = self.prompts.create_scene_outlines_rewrite_prompt()
        variables = {"current_outlines": current_outlines_text}

        critique_text = await self._generate_content_from_prompt(
            critique_prompt_template, variables
        )
        if not critique_text:
            return None

        rewrite_variables = {**variables, "critique": critique_text}
        enhanced_outlines_text = await self._generate_content_from_prompt(
            rewrite_prompt_template, rewrite_variables
        )
        if not enhanced_outlines_text:
            return None

        # Parse and return enhanced scene outlines
        return self._parse_response(enhanced_outlines_text)

    def _parse_response(self, response_text: str) -> Optional[List[SceneOutline]]:
        """
        Parses the LLM response text into a list of SceneOutline objects.
        """
        scene_outlines: List[SceneOutline] = []
        try:
            scene_splits = response_text.strip().split("Scene ")
            for i, scene_text in enumerate(scene_splits[1:], start=1):
                scene_summary = scene_text.split("Scene")[
                    0
                ].strip()  # Split again in case "Scene" is in summary text
                if scene_summary:
                    scene_outlines.append(
                        SceneOutline(scene_number=i, summary=scene_summary)
                    )
                else:
                    logger.warning(
                        "Skipping empty scene outline in LLM response."
                    )  # No lazy format - simple string
                    # logger.warning("%s", "Skipping empty scene outline in LLM response.") # Lazy format - but no variable to pass

            if not scene_outlines:
                logger.error(
                    "No scene outlines parsed from LLM response."
                )  # No lazy format - simple string
                # logger.error("%s", "No scene outlines parsed from LLM response.") # Lazy format - but no variable to pass
                return None
            return scene_outlines

        except (
            ValueError,
            TypeError,
            RuntimeError,
        ) as e:  # Specific exception handling
            logger.error("Error parsing SceneOutline responses: %s", e)  # Lazy format
            logger.debug("Raw LLM response: %s", response_text)  # Lazy format
            logger.exception(e)  # Log full exception details
            return None
