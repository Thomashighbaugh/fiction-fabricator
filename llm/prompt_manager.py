# llm/prompt_manager.py
from llm.prompts import base_prompts
from llm.prompts import book_spec_prompts
from llm.prompts import chapter_outline_prompts
from llm.prompts import plot_outline_prompts
from llm.prompts import scene_prompts


class PromptManager:
    def __init__(self, book_spec=None):
        self.book_spec = book_spec
        self.methodology_markdown = base_prompts.METHODOLOGY_MARKDOWN

    def create_book_spec_generation_prompt(self) -> str:
        return book_spec_prompts.get_book_spec_generation_prompt(
            "{idea}"
        )  # Corrected Call

    def create_book_spec_enhancement_prompt(self, current_spec) -> str:
        return book_spec_prompts.get_book_spec_enhancement_prompt(
            current_spec
        )  # No change needed - handled in generation function

    def create_book_spec_critique_prompt(self) -> str:
        return book_spec_prompts.get_book_spec_critique_prompt()

    def create_book_spec_rewrite_prompt(self) -> str:
        return book_spec_prompts.get_book_spec_rewrite_prompt()

    def create_book_spec_structure_check_prompt(self) -> str:
        return book_spec_prompts.get_book_spec_structure_check_prompt()

    def create_book_spec_structure_fix_prompt(self) -> str:
        return book_spec_prompts.get_book_spec_structure_fix_prompt()

    def create_chapter_outline_27_method_generation_prompt(self) -> str:
        return chapter_outline_prompts.get_chapter_outline_27_method_generation_prompt()

    def create_chapter_outline_27_method_critique_prompt(self) -> str:
        return chapter_outline_prompts.get_chapter_outline_27_method_critique_prompt()

    def create_chapter_outline_27_method_rewrite_prompt(self) -> str:
        return chapter_outline_prompts.get_chapter_outline_27_method_rewrite_prompt()

    def create_chapter_outlines_generation_prompt(self) -> str:
        return chapter_outline_prompts.get_chapter_outlines_generation_prompt()

    def create_chapter_outlines_critique_prompt(self) -> str:
        return chapter_outline_prompts.get_chapter_outlines_critique_prompt()

    def create_chapter_outlines_rewrite_prompt(self) -> str:
        return chapter_outline_prompts.get_chapter_outlines_rewrite_prompt()

    def create_plot_outline_generation_prompt(self) -> str:
        return plot_outline_prompts.get_plot_outline_generation_prompt()

    def create_plot_outline_critique_prompt(self) -> str:
        return plot_outline_prompts.get_plot_outline_critique_prompt()

    def create_plot_outline_rewrite_prompt(self) -> str:
        return plot_outline_prompts.get_plot_outline_rewrite_prompt()

    def create_scene_outlines_generation_prompt(self) -> str:
        return scene_prompts.get_scene_outlines_generation_prompt()

    def create_scene_outlines_critique_prompt(self) -> str:
        return scene_prompts.get_scene_outlines_critique_prompt()

    def create_scene_outlines_rewrite_prompt(self) -> str:
        return scene_prompts.get_scene_outlines_rewrite_prompt()

    def create_scene_part_generation_prompt(self) -> str:
        return scene_prompts.get_scene_part_generation_prompt()

    def create_scene_part_critique_prompt(self) -> str:
        return scene_prompts.get_scene_part_critique_prompt()

    def create_scene_part_rewrite_prompt(self) -> str:
        return scene_prompts.get_scene_part_rewrite_prompt()

    def create_scene_part_structure_check_prompt(self) -> str:
        return scene_prompts.get_scene_part_structure_check_prompt()

    def create_scene_part_structure_fix_prompt(self) -> str:
        return scene_prompts.get_scene_part_structure_fix_prompt()
