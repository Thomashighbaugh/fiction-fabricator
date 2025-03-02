# /home/tlh/refactored_gui_fict_fab/core/content_generation/plot_outline_generator.py
from typing import Optional

from core.book_spec import BookSpec
from core.content_generation.base_generator import BaseContentGenerator
from core.plot_outline import PlotOutline

# from llm.prompt_manager.plot_outline_prompts import PlotOutlinePrompts # Removed incorrect import
from utils.logger import logger


class PlotOutlineGenerator(BaseContentGenerator):
    """
    Content generator for PlotOutline objects.

    Inherits from BaseContentGenerator and provides specific functionality
    for generating and enhancing plot outlines.
    """

    def __init__(self, prompt_manager, model_name: str):
        """
        Initializes PlotOutlineGenerator with prompt manager and model name.
        """
        super().__init__(prompt_manager, model_name)
        # self.prompts = PlotOutlinePrompts(prompt_manager)  # Removed incorrect instantiation
        # self.prompts = prompt_manager # This was also incorrect, should not reassign prompt_manager
        pass  # No need to initialize prompts here anymore, PromptManager handles it

    async def generate(self, book_spec: BookSpec) -> Optional[PlotOutline]:
        """
        Generates a PlotOutline based on a BookSpec.
        """
        generation_prompt_template = self.prompt_manager.get_prompt(
            "plot_outline_generation_prompt"
        )  # Use prompt_manager to get prompt
        variables = {"book_spec_json": book_spec.model_dump_json(indent=4)}
        generated_text = await self._generate_content_from_prompt(
            generation_prompt_template, variables
        )
        if not generated_text:
            return None

        structure_check_prompt_template = self.prompt_manager.get_prompt(
            "plot_outline_structure_check_prompt"
        )  # Use prompt_manager to get prompt
        structure_fix_prompt_template = self.prompt_manager.get_prompt(
            "plot_outline_structure_fix_prompt"
        )  # Use prompt_manager to get prompt
        validated_text = await self._structure_check_and_fix(
            generated_text,
            structure_check_prompt_template,
            structure_fix_prompt_template,
        )
        if not validated_text:
            return None

        return self._parse_response(validated_text)

    async def enhance(
        self, current_content: PlotOutline
    ) -> Optional[PlotOutline]:  # Parameter name consistent with base class
        """
        Enhances an existing plot outline.
        """
        critique_prompt_template = self.prompt_manager.get_prompt(
            "plot_outline_critique_prompt"
        )  # Use prompt_manager to get prompt
        rewrite_prompt_template = self.prompt_manager.get_prompt(
            "plot_outline_rewrite_prompt"
        )  # Use prompt_manager to get prompt
        variables = {
            "current_outline": "\n".join(
                [
                    f"Act One:\n{current_content.act_one}",
                    f"Act Two:\n{current_content.act_two}",
                    f"Act Three:\n{current_content.act_three}",
                ]
            )
        }  # Pass string for critique

        critique_text = await self._generate_content_from_prompt(
            critique_prompt_template, variables
        )
        if not critique_text:
            return None

        rewrite_variables = {**variables, "critique": critique_text}
        enhanced_outline_text = await self._generate_content_from_prompt(
            rewrite_prompt_template, rewrite_variables
        )
        if not enhanced_outline_text:
            return None

        return self._parse_response(enhanced_outline_text)

    def _parse_response(self, response_text: str) -> Optional[PlotOutline]:
        """
        Parses the LLM response text into a PlotOutline object.
        """
        try:
            plot_outline = PlotOutline(act_one="", act_two="", act_three="")
            acts = response_text.split("Act ")
            if len(acts) >= 4:
                plot_outline.act_one = acts[1].split("Act")[0].strip()
                plot_outline.act_two = acts[2].split("Act")[0].strip()
                plot_outline.act_three = acts[3].strip()
            else:
                logger.warning(
                    "Unexpected plot outline format from LLM, basic parsing failed."
                )
                plot_outline.act_one = (
                    response_text  # Fallback: use the whole response as act_one
                )
            return plot_outline
        except (
            ValueError,
            TypeError,
            RuntimeError,
        ) as e:  # More specific exception catching
            logger.error("Error parsing PlotOutline response: %s", e)  # Lazy format
            logger.debug("Raw LLM response: %s", response_text)  # Lazy format
            logger.exception(e)  # Log full exception details
            return None
