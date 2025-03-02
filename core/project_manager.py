# /home/tlh/refactored_gui_fict_fab/core/project_manager.py
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
        logger.debug(
            f"ProjectManager initialized, project directory: {self.project_dir}"
        )

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
        # Enforce lowercase project directory names:
        project_dir_name = (
            project_name.lower()
        )  # Convert project name to lowercase for directory
        project_dir = os.path.join(
            self.project_dir, project_dir_name
        )  # Use lowercase name for directory
        os.makedirs(project_dir, exist_ok=True)  # Create project folder if not exists
        project_filepath = os.path.join(
            project_dir, f"{project_name}.json"
        )  # Filename still uses original project_name

        logger.debug(f"Saving project '{project_name}', filepath: {project_filepath}")

        try:
            # Convert Pydantic models to dictionaries
            book_spec_data = book_spec.model_dump() if book_spec else None
            plot_outline_data = plot_outline.model_dump() if plot_outline else None
            chapter_outlines_data = (
                [co.model_dump() for co in chapter_outlines]
                if chapter_outlines
                else None
            )
            scene_outlines_data = (
                {
                    chapter_num: [so.model_dump() for so in scene_outlines]
                    for chapter_num, scene_outlines in scene_outlines.items()
                }
                if scene_outlines
                else None
            )

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
            logger.debug(f"Project data before save_json: {project_data}")

            save_json(project_data, project_filepath)
            logger.info("Project '%s' saved successfully.", project_name)
        except Exception as e:
            logger.error("Error saving project '%s': %s", project_name, e)
            raise

    def load_project(self, project_name: str) -> Optional[Dict[str, Any]]:
        """
        Loads project data from a JSON file.
        """
        # Enforce lowercase project directory names for loading as well:
        project_dir_name = (
            project_name.lower()
        )  # Convert project name to lowercase for directory
        project_dir = os.path.join(
            self.project_dir, project_dir_name
        )  # Use lowercase directory name
        project_filepath = os.path.join(
            project_dir, f"{project_name}.json"
        )  # Filename still uses original project_name

        logger.debug(f"Loading project '{project_name}', filepath: {project_filepath}")

        if not os.path.exists(project_filepath):
            logger.error(f"Project file NOT found at: {project_filepath}")
            raise FileNotFoundError(f"Project file not found: {project_filepath}")

        if not os.path.isfile(project_filepath):
            logger.error(f"Path is not a file: {project_filepath}")
            raise FileNotFoundError(f"Project file is not a file: {project_filepath}")

        try:
            project_data = load_json(project_filepath)
            logger.info("Project '%s' loaded successfully.", project_name)
            logger.debug(f"Project data after load_json: {project_data}")
            return project_data
        except FileNotFoundError:
            logger.error(f"Project file not found: %s", project_filepath)
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from %s: %s", project_filepath, e)
            raise
        except Exception as e:
            logger.error(f"Error loading project '%s': %s", project_name, e)
            raise
