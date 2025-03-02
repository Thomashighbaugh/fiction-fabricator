# /home/tlh/refactored_gui_fict_fab/core/content_generation/chapter_outline_generator.py
from typing import List, Optional

from core.content_generation.base_generator import BaseContentGenerator
from core.plot_outline import ChapterOutline, PlotOutline

# from llm.prompt_manager.chapter_outline_prompts import ChapterOutlinePrompts # Removed incorrect import
from utils.logger import logger


class ChapterOutlineGenerator(BaseContentGenerator):
    """
    Content generator for ChapterOutline objects.

    Extends BaseContentGenerator to provide specific functionality for
    generating and enhancing chapter outlines for a novel.
    """

    def __init__(self, prompt_manager, model_name: str):
        """
        Initializes ChapterOutlineGenerator with prompt manager and model name.
        """
        super().__init__(prompt_manager, model_name)
        # self.prompts = ChapterOutlinePrompts(prompt_manager)  # Removed incorrect instantiation
        # self.prompts = prompt_manager # This was also incorrect, should not reassign prompt_manager
        pass  # No need to initialize prompts here anymore, PromptManager handles it

    async def generate(
        self, plot_outline: PlotOutline, num_chapters: int
    ) -> Optional[List[ChapterOutline]]:
        """
        Generates a list of ChapterOutlines based on a PlotOutline.
        """
        generation_prompt_template = self.prompt_manager.get_prompt(
            "chapter_outlines_generation_prompt"
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
        generated_text = await self._generate_content_from_prompt(
            generation_prompt_template, variables
        )
        if not generated_text:
            return None

        structure_check_prompt_template = self.prompt_manager.get_prompt(
            "chapter_outlines_structure_check_prompt"
        )
        structure_fix_prompt_template = self.prompt_manager.get_prompt(
            "chapter_outlines_structure_fix_prompt"
        )
        validated_text = await self._structure_check_and_fix(
            generated_text,
            structure_check_prompt_template,
            structure_fix_prompt_template,
        )
        if not validated_text:
            return None

        return self._parse_response(validated_text, num_chapters)

    async def enhance(
        self,
        current_content: List[
            ChapterOutline
        ],  # Parameter name consistent with base class
    ) -> Optional[List[ChapterOutline]]:
        """
        Enhances a list of existing ChapterOutline objects.
        """
        # Convert ChapterOutline objects to text for critique and rewrite prompts
        outline_texts = [
            f"Chapter {co.chapter_number}:\n{co.summary}" for co in current_content
        ]
        current_outlines_text = "\n\n".join(outline_texts)

        critique_prompt_template = self.prompt_manager.get_prompt(
            "chapter_outlines_critique_prompt"
        )
        rewrite_prompt_template = self.prompt_manager.get_prompt(
            "chapter_outlines_rewrite_prompt"
        )
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

        # Parse and return enhanced chapter outlines
        return self._parse_response(enhanced_outlines_text, len(current_content))

    def _parse_response(
        self, response_text: str, num_chapters: int
    ) -> Optional[List[ChapterOutline]]:
        """
        Parses the LLM response text into a list of ChapterOutline objects.
        """
        chapter_outlines: List[ChapterOutline] = []
        try:
            chapter_splits = response_text.strip().split("Chapter ")
            logger.debug(
                "Number of chapter splits found: %s, expected chapters: %s",
                len(chapter_splits) - 1,
                num_chapters,  # Lazy format
            )
            for i, chapter_text in enumerate(
                chapter_splits[1:], start=1
            ):  # Start from 1 to skip intro, enumerate for chapter number
                if i > num_chapters:
                    logger.warning(
                        "Parsed more chapters than requested (%s). Stopping after %s chapters.",
                        num_chapters,
                        num_chapters,  # Lazy format
                    )
                    break  # Limit chapters to requested number

                chapter_summary = chapter_text.split("Chapter")[
                    0
                ].strip()  # Split again in case "Chapter" is in summary text
                if chapter_summary:
                    chapter_outlines.append(
                        ChapterOutline(chapter_number=i, summary=chapter_summary)
                    )
                    logger.debug(
                        "Parsed chapter %s outline: %s...",
                        i,
                        chapter_summary[:50],  # Lazy format
                    )
            if not chapter_outlines:
                logger.error("No chapter outlines parsed from LLM response.")
                return None
            return chapter_outlines

        except (
            ValueError,
            TypeError,
            RuntimeError,
        ) as e:  # More specific exception catching
            logger.error("Error parsing ChapterOutline responses: %s", e)  # Lazy format
            logger.debug("Raw LLM response: %s", response_text)  # Lazy format
            logger.exception(e)  # Log full exception details
            return None
