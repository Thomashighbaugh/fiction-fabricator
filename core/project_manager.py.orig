# core/project_manager.py
import json
import os
from core.book_spec import BookSpec
from core.plot_outline import PlotOutline, ChapterOutline, SceneOutline
from core.content_generator import ChapterOutlineMethod  # Import ChapterOutlineMethod
from utils.logger import logger
from utils.config import config


class ProjectManager:
    """
    Manages project saving and loading, now including story_idea.
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
        chapter_outlines_27_method: list[
            ChapterOutlineMethod
        ] = None,  # Add chapter_outlines_27_method here
        scene_outlines: dict[int, list[SceneOutline]] = None,
        scene_parts: dict[int, dict[int, str]] = None,
    ) -> None:
        """
        Saves the current project data to a JSON file, including story_idea.
        """
        project_data = {
            "story_idea": story_idea,
            "book_spec": book_spec.model_dump() if book_spec else None,
            "plot_outline": plot_outline.model_dump() if plot_outline else None,
            "chapter_outlines": (
                [co.model_dump() for co in chapter_outlines]
                if chapter_outlines
                else None
            ),
            "chapter_outlines_27_method": (  # Add chapter_outlines_27_method here
                [co.model_dump() for co in chapter_outlines_27_method]
                if chapter_outlines_27_method
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
        logger.info(
            f"Project '{project_name}' saved to '{filepath}' (including story_idea)"
        )

    def load_project(self, project_name: str) -> dict | None:
        """
        Loads project data from a JSON file and returns project data including story_idea.
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
