# llm/prompt_manager.py
# Corrected and Complete (FOR REAL THIS TIME, I SWEAR, AND I ACTUALLY UNDERSTAND WHY)

from llm.prompts.book_spec_prompts import (
    create_book_spec_generation_prompt,
    create_book_spec_critique_prompt,
    create_book_spec_rewrite_prompt,
    create_book_spec_validation_prompt,
    create_book_spec_enhancement_prompt,
)
from llm.prompts.plot_outline_prompts import (
    create_plot_outline_generation_prompt,
    create_plot_outline_critique_prompt,
    create_plot_outline_rewrite_prompt,
    create_plot_outline_enhancement_prompt,
)
from llm.prompts.chapter_outline_prompts import (
    create_chapter_outlines_generation_prompt,
    create_chapter_outlines_critique_prompt,
    create_chapter_outlines_rewrite_prompt,
    create_chapter_outline_27_method_generation_prompt,
    create_chapter_outline_27_method_critique_prompt,
    create_chapter_outline_27_method_rewrite_prompt,
    create_chapter_outlines_enhancement_prompt,
    create_chapter_outline_27_method_enhancement_prompt,
)
from llm.prompts.scene_prompts import (  # CORRECTED IMPORT PATH
    create_scene_outlines_generation_prompt,
    create_scene_outlines_critique_prompt,
    create_scene_outlines_rewrite_prompt,
    create_scene_outlines_enhancement_prompt,
    create_scene_part_generation_prompt,
    create_scene_part_critique_prompt,
    create_scene_part_rewrite_prompt,
    create_scene_part_structure_check_prompt,
    create_scene_part_structure_fix_prompt,
    create_scene_part_enhancement_prompt,
)
from utils.logger import logger


class PromptManager:
    """
    Manages prompts by calling functions from the llm/prompts directory.
    """

    def __init__(self):
        logger.debug("PromptManager initialized.")
        pass

    # --- Book Spec Prompts ---
    def create_book_spec_generation_prompt(self):
        return create_book_spec_generation_prompt

    def create_book_spec_critique_prompt(self):
        return create_book_spec_critique_prompt

    def create_book_spec_rewrite_prompt(self):
        return create_book_spec_rewrite_prompt

    def create_book_spec_validation_prompt(self):
        return create_book_spec_validation_prompt

    def create_book_spec_enhancement_prompt(self):  # Added
        return create_book_spec_enhancement_prompt

    # --- Plot Outline Prompts ---
    def create_plot_outline_generation_prompt(self):
        return create_plot_outline_generation_prompt

    def create_plot_outline_critique_prompt(self):
        return create_plot_outline_critique_prompt

    def create_plot_outline_rewrite_prompt(self):
        return create_plot_outline_rewrite_prompt

    def create_plot_outline_enhancement_prompt(self):  # Added
        return create_plot_outline_enhancement_prompt

    # --- Chapter Outline Prompts (Regular) ---
    def create_chapter_outlines_generation_prompt(self):
        return create_chapter_outlines_generation_prompt

    def create_chapter_outlines_critique_prompt(self):
        return create_chapter_outlines_critique_prompt

    def create_chapter_outlines_rewrite_prompt(self):
        return create_chapter_outlines_rewrite_prompt

    def create_chapter_outlines_enhancement_prompt(self):  # Added
        return create_chapter_outlines_enhancement_prompt

    # --- Chapter Outline Prompts (27 Chapter Method) ---
    def create_chapter_outline_27_method_generation_prompt(self):
        return create_chapter_outline_27_method_generation_prompt

    def create_chapter_outline_27_method_critique_prompt(self):
        return create_chapter_outline_27_method_critique_prompt

    def create_chapter_outline_27_method_rewrite_prompt(self):
        return create_chapter_outline_27_method_rewrite_prompt

    def create_chapter_outline_27_method_enhancement_prompt(self):  # Added
        return create_chapter_outline_27_method_enhancement_prompt

    # --- Scene Outline Prompts ---
    def create_scene_outlines_generation_prompt(self):
        return create_scene_outlines_generation_prompt

    def create_scene_outlines_critique_prompt(self):
        return create_scene_outlines_critique_prompt

    def create_scene_outlines_rewrite_prompt(self):
        return create_scene_outlines_rewrite_prompt

    def create_scene_outlines_enhancement_prompt(self):  # Added
        return create_scene_outlines_enhancement_prompt

    # --- Scene Part Prompts ---
    def create_scene_part_generation_prompt(self):
        return create_scene_part_generation_prompt

    def create_scene_part_critique_prompt(self):
        return create_scene_part_critique_prompt

    def create_scene_part_rewrite_prompt(self):
        return create_scene_part_rewrite_prompt

    def create_scene_part_structure_check_prompt(self):
        return create_scene_part_structure_check_prompt

    def create_scene_part_structure_fix_prompt(self):
        return create_scene_part_structure_fix_prompt

    def create_scene_part_enhancement_prompt(self):  # Added
        return create_scene_part_enhancement_prompt
