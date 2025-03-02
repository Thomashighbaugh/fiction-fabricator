# core/project_manager.py
import json
import os
from typing import Dict, Any, Optional

from utils.file_handler import save_json, load_json
from utils.config import config
from utils.logger import logger

class ProjectManager:
    """
    Manages project-related operations such as saving and loading project data.
    """

    def __init__(self):
        """
        Initializes the ProjectManager with the project directory from config.
        """
        self.project_dir = config.get_project_directory()
        os.makedirs(self.project_dir, exist_ok=True)  # Ensure project directory exists

    def save_project(
        self,
        project_name: str,
        story_idea: str,
        book_spec: Any,  # BookSpec | None,
        plot_outline: Any,  # PlotOutline | None,
        chapter_outlines: list[Any],  # list[ChapterOutline] | None,
        scene_outlines: Dict[int, list[Any]],  # Dict[int, list[SceneOutline]] | None,
        scene_parts: Dict[int, Dict[int, Any]],  # Dict[int, Dict[int, str]] | None,
        scene_parts_text: Dict[int, Dict[int, Dict[int, str]]],
        book_text: Optional[str],
    ) -> None:
        """
        Saves the project data to a JSON file.
        """
        project_dir = os.path.join(self.project_dir, project_name) # Create project folder
        os.makedirs(project_dir, exist_ok=True)  # Create project folder if not exists
        project_filepath = os.path.join(project_dir, f"{project_name}.json") # Add project name to the path
        try:
            # Convert Pydantic models to dictionaries
            book_spec_data = book_spec.model_dump() if book_spec else None
            plot_outline_data = plot_outline.model_dump() if plot_outline else None
            chapter_outlines_data = [co.model_dump() for co in chapter_outlines] if chapter_outlines else None
            scene_outlines_data = {
                chapter_num: [so.model_dump() for so in scene_outlines]
                for chapter_num, scene_outlines in scene_outlines.items()
            } if scene_outlines else None

            project_data: Dict[str, Any] = {
                "story_idea": story_idea,
                "book_spec": book_spec_data,
                "plot_outline": plot_outline_data,
                "chapter_outlines": chapter_outlines_data,
                "scene_outlines": scene_outlines_data,
                "scene_parts": scene_parts,
                "scene_parts_text": scene_parts_text,
                "book_text": book_text,
            }

            save_json(project_data, project_filepath)
            logger.info("Project '%s' saved successfully.", project_name)
        except Exception as e:
            logger.error("Error saving project '%s': %s", project_name, e)
            raise

    def load_project(self, project_name: str) -> Optional[Dict[str, Any]]:
        """
        Loads project data from a JSON file.
        """
        project_dir = os.path.join(self.project_dir, project_name) # added to the start so it reads the correct directory
        project_filepath = os.path.join(project_dir, f"{project_name}.json")
        try:
            project_data = load_json(project_filepath)
            logger.info("Project '%s' loaded successfully.", project_name)
            return project_data
        except FileNotFoundError:
            logger.error("Project file not found: %s", project_filepath)
            raise
        except Exception as e:
            logger.error("Error loading project '%s': %s", project_name, e)
            raise