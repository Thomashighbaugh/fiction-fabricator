# core/project_manager.py
import json
import os
from core.book_spec import BookSpec
from core.plot_outline import PlotOutline, ChapterOutline, SceneOutline
from utils.config import config
from utils.logger import logger


class ProjectManager:
    """
    Manages project saving and loading.
    """

    def __init__(self, book_spec: BookSpec = None):
        """
        Initializes the ProjectManager.

        Args:
            book_spec (BookSpec, optional): An initial BookSpec object to provide context. Defaults to None.
        """
        self.book_spec = book_spec

    def save_project(
        self,
        project_name: str,
        book_spec: BookSpec = None,
        plot_outline: PlotOutline = None,
        chapter_outlines: list[ChapterOutline] = None,
        scene_outlines: dict[int, list[SceneOutline]] = None,
        scene_parts: dict[int, dict[int, str]] = None,
    ) -> None:
        """
        Saves the current project data to a JSON file.

        Args:
            project_name (str): The name of the project to save.
            book_spec (BookSpec, optional): The BookSpec object. Defaults to None.
            plot_outline (PlotOutline, optional): The PlotOutline object. Defaults to None.
            chapter_outlines (list[ChapterOutline], optional): The list of ChapterOutline objects. Defaults to None.
            scene_outlines (dict[int, list[SceneOutline]], optional): The dictionary of SceneOutline objects, keyed by chapter number. Defaults to None.
            scene_parts (dict[int, dict[int, str]], optional): The dictionary of scene parts, keyed by chapter number and scene number. Defaults to None.
        """
        project_data = {
            "book_spec": book_spec.model_dump() if book_spec else None,
            "plot_outline": plot_outline.model_dump() if plot_outline else None,
            "chapter_outlines": (
                [co.model_dump() for co in chapter_outlines]
                if chapter_outlines
                else None
            ),
            "scene_outlines": (
                {
                    chapter_num: [so.model_dump() for so in scene_outlines]
                    for chapter_num, scene_outlines in scene_outlines.items()
                }
                if scene_outlines
                else None
            ),
            "scene_parts": scene_parts if scene_parts else None,
        }

        project_dir = config.get_project_directory()
        os.makedirs(project_dir, exist_ok=True)  # Ensure directory exists
        filepath = os.path.join(project_dir, f"{project_name}.json")

        with open(filepath, "w") as f:
            json.dump(project_data, f, indent=4)
        logger.info(f"Project '{project_name}' saved to '{filepath}'")

    def load_project(self, project_name: str) -> dict | None:
        """
        Loads project data from a JSON file.

        Args:
            project_name (str): The name of the project to load.
        Returns:
            dict | None: A dictionary containing the project data, or None if the project file is not found or cannot be loaded.
        """
        project_dir = config.get_project_directory()
        filepath = os.path.join(project_dir, f"{project_name}.json")

        try:
            with open(filepath, "r") as f:
                project_data = json.load(f)
            logger.info(f"Project '{project_name}' loaded from '{filepath}'")
            return project_data
        except FileNotFoundError:
            logger.warning(f"Project file '{filepath}' not found.")
            return None
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from project file '{filepath}'.")
            return None
        except Exception as e:
            logger.error(f"Error loading project from '{filepath}': {e}")
            return None
