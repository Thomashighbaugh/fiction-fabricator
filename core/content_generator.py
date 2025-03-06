# core/content_generator.py
from core.content_generation.book_spec_generation import (
    generate_book_spec as _generate_book_spec,
)
from core.content_generation.book_spec_generation import (
    enhance_book_spec as _enhance_book_spec,
)
from core.content_generation.plot_outline_generation import (
    generate_plot_outline as _generate_plot_outline,
)
from core.content_generation.plot_outline_generation import (
    enhance_plot_outline as _enhance_plot_outline,
)
from core.content_generation.chapter_outline_generation import (
    generate_chapter_outlines as _generate_chapter_outlines,
)
from core.content_generation.chapter_outline_generation import (
    enhance_chapter_outlines as _enhance_chapter_outlines,
)
from core.content_generation.chapter_outline_generation import (
    generate_chapter_outline_27_method as _generate_chapter_outline_27_method,
)
from core.content_generation.chapter_outline_generation import (
    enhance_chapter_outlines_27_method as _enhance_chapter_outlines_27_method,
)
from core.content_generation.scene_outline_generation import (
    generate_scene_outlines as _generate_scene_outlines,
)
from core.content_generation.scene_outline_generation import (
    enhance_scene_outlines as _enhance_scene_outlines,
)
from core.content_generation.scene_part_generation import (
    generate_scene_part as _generate_scene_part,
)  # Import from scene_part_generation.py
from core.content_generation.scene_part_generation import (
    enhance_scene_part as _enhance_scene_part,
)  # Import from scene_part_generation.py
from core.content_generation.content_generation_utils import (
    PlotOutline,
    ChapterOutline,
    SceneOutline,
    ChapterOutlineMethod,
)

from llm.llm_client import OllamaClient
from utils.logger import logger  # ADDED LOGGER IMPORT HERE


class ContentGenerator:
    """
    Orchestrates the content generation process for the novel,
    delegating specific tasks to submodule functions.
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
        self.ollama_client = OllamaClient()  # Initialize OllamaClient here
        logger.debug(f"ContentGenerator initializing with model_name: {model_name}")
        logger.debug("ContentGenerator.__init__ - OllamaClient initialized.")

    generate_book_spec = _generate_book_spec
    enhance_book_spec = _enhance_book_spec
    generate_plot_outline = _generate_plot_outline
    enhance_plot_outline = _enhance_plot_outline
    generate_chapter_outlines = _generate_chapter_outlines
    enhance_chapter_outlines = _enhance_chapter_outlines
    generate_chapter_outline_27_method = _generate_chapter_outline_27_method
    enhance_chapter_outlines_27_method = _enhance_chapter_outlines_27_method
    generate_scene_outlines = _generate_scene_outlines
    enhance_scene_outlines = _enhance_scene_outlines
    generate_scene_part = (
        _generate_scene_part  # Correctly assigned to imported function
    )
    enhance_scene_part = _enhance_scene_part  # Correctly assigned to imported function

