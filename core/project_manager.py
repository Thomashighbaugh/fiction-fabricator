# core/project_manager.py
import os
from core.book_spec import BookSpec
from core.plot_outline import PlotOutline, ChapterOutline, SceneOutline
from core.content_generator import ChapterOutlineMethod
from utils.logger import logger
from utils.config import config
from utils.file_handler import save_toml, load_toml  # Corrected import


class ProjectManager:
    """
    Manages project saving and loading, using TOML.
    """

    def __init__(self, book_spec: BookSpec = None):
        """
        Initializes the ProjectManager.
        """
        self.book_spec = book_spec

    def save_project(
        self,
        project_name: str,
        story_idea: str = None,
        book_spec: BookSpec = None,
        plot_outline: PlotOutline = None,
        chapter_outlines: list[ChapterOutline] = None,
        chapter_outlines_27_method: list[ChapterOutlineMethod] = None,
        scene_outlines: dict[int, list[SceneOutline]] = None,
        scene_parts: dict[int, dict[int, str]] = None,
    ) -> None:
        """
        Saves the current project data to a TOML file.  Now with None checks.
        """
        project_data = {
            "story_idea": story_idea,
            "book_spec": book_spec.model_dump_toml() if book_spec else None,
            "plot_outline": plot_outline.model_dump_toml() if plot_outline else None,
            "chapter_outlines": (
                [co.model_dump_toml() for co in chapter_outlines]
                if chapter_outlines
                else None
            ),
            "chapter_outlines_27_method": (
                [co.model_dump_toml() for co in chapter_outlines_27_method]
                if chapter_outlines_27_method
                else None
            ),
            "scene_outlines": (
                {
                    str(chapter_num): [so.model_dump_toml() for so in scene_outlines]
                    for chapter_num, scene_outlines in scene_outlines.items()
                }
                if scene_outlines
                else None
            ),
            "scene_parts": (
                {
                    str(chapter_num): {
                        str(scene_num): {
                            str(part_number): part_text
                            for part_number, part_text in parts.items()
                        }
                        for scene_num, parts in scenes.items()
                    }
                    for chapter_num, scenes in scene_parts.items()
                }
                if scene_parts
                else None
            ),
        }

        # Check for None values and remove them
        cleaned_project_data = {}
        for key, value in project_data.items():
            if value is not None:
                cleaned_project_data[key] = value

        project_dir = config.get_project_directory()
        os.makedirs(project_dir, exist_ok=True)
        filepath = os.path.join(project_dir, f"{project_name}.toml")  # .toml extension

        save_toml(cleaned_project_data, filepath)  # Use save_toml and cleaned data
        logger.info(f"Project '{project_name}' saved to '{filepath}'")

    def load_project(self, project_name: str) -> dict | None:
        """
        Loads project data from a TOML file.
        """
        project_dir = config.get_project_directory()
        filepath = os.path.join(project_dir, f"{project_name}.toml")  # .toml extension

        try:
            project_data = load_toml(filepath)  # Use load_toml
            logger.info(f"Project '{project_name}' loaded from '{filepath}'")
            return project_data
        except FileNotFoundError:
            logger.warning(f"Project file '{filepath}' not found.")
            return None
        except Exception as e:
            logger.error(f"Error loading project from '{filepath}': {e}")
            return None
