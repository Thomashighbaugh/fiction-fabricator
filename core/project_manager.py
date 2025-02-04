# fiction_fabricator/src/core/project_manager.py
import json
import os

from core.book_spec import BookSpec
from  core.plot_outline import ChapterOutline, PlotOutline, SceneOutline
from  utils.file_handler import load_json, save_json
from  utils.logger import logger


class ProjectManager:
    """
    Manages project loading, saving, and state persistence for the Fiction Fabricator.

    This class handles saving project data to JSON files and loading project data
    from JSON files, allowing users to save their progress and resume work later.
    It supports saving and loading BookSpec, PlotOutline, ChapterOutlines, and
    SceneOutlines.
    """

    def __init__(self, project_dir: str = "data"):
        """
        Initializes the ProjectManager with a specified project directory.

        Args:
            project_dir (str): The directory where project files will be saved and loaded.
                               Defaults to "data" in the project root.
        """
        self.project_dir = project_dir
        os.makedirs(self.project_dir, exist_ok=True)  # Ensure project directory exists

    def save_project(self, project_name: str, book_spec: BookSpec, plot_outline: PlotOutline = None, chapter_outlines: list[ChapterOutline] = None, scene_outlines: dict[int, list[SceneOutline]] = None, scene_parts: dict[int, dict[int, dict[int, str]]] = None) -> None:
        """
        Saves the current project state to a JSON file.

        Saves BookSpec, PlotOutline, ChapterOutlines, and SceneOutlines into a JSON file
        within the project directory. The filename is derived from the project name.

        Args:
            project_name (str): The name of the project, used to create the filename.
            book_spec (BookSpec): The BookSpec object for the project.
            plot_outline (PlotOutline, optional): The PlotOutline object. Defaults to None.
            chapter_outlines (list[ChapterOutline], optional): List of ChapterOutline objects. Defaults to None.
            scene_outlines (dict[int, list[SceneOutline]], optional): Dictionary of scene outlines, keyed by chapter number. Defaults to None.
            scene_parts (dict[int, dict[int, dict[int, str]]], optional): Dictionary of scene parts, keyed by chapter, scene, and part number. Defaults to None.
        """
        if not project_name:
            raise ValueError("Project name cannot be empty for saving.")
        filepath = os.path.join(self.project_dir, f"{project_name}.json")
        project_data = {
            "book_spec": book_spec.dict() if book_spec else None,
            "plot_outline": plot_outline.dict() if plot_outline else None,
            "chapter_outlines": [co.dict() for co in chapter_outlines] if chapter_outlines else None,
            "scene_outlines": {chap_num: [so.dict() for so in scene_list] for chap_num, scene_list in scene_outlines.items()} if scene_outlines else None,
            "scene_parts": scene_parts if scene_parts else None,
        }
        try:
            save_json(project_data, filepath)
            logger.info("Project '%s' saved to: %s", project_name, filepath)
        except Exception as e:
            logger.error("Error saving project '%s': %s", project_name, e)
            raise

    def load_project(self, project_name: str) -> dict | None:
        """
        Loads project data from a JSON file.

        Loads and reconstructs BookSpec, PlotOutline, ChapterOutlines, and SceneOutlines
        from a JSON file within the project directory.

        Args:
            project_name (str): The name of the project to load.

        Returns:
            dict | None: A dictionary containing project data if loading is successful, None otherwise.
                         The dictionary will contain keys: 'book_spec', 'plot_outline', 'chapter_outlines', 'scene_outlines', 'scene_parts',
                         with corresponding objects or None if not saved.
        """
        filepath = os.path.join(self.project_dir, f"{project_name}.json")
        try:
            project_data_raw = load_json(filepath)
            if not project_data_raw:
                logger.warning(f"No data loaded from project file: {filepath}")
                return None

            project_data = {}
            project_data['book_spec'] = BookSpec(**project_data_raw.get('book_spec')) if project_data_raw.get('book_spec') else None
            project_data['plot_outline'] = PlotOutline(**project_data_raw.get('plot_outline')) if project_data_raw.get('plot_outline') else None
            project_data['chapter_outlines'] = [ChapterOutline(**co_data) for co_data in project_data_raw.get('chapter_outlines', [])] if project_data_raw.get('chapter_outlines') else None
            project_data['scene_outlines'] = {int(chap_num): [SceneOutline(**so_data) for so_data in scene_list] for chap_num, scene_list in project_data_raw.get('scene_outlines', {}).items()} if project_data_raw.get('scene_outlines') else None
            project_data['scene_parts'] = project_data_raw.get('scene_parts') if project_data_raw.get('scene_parts') else None

            logger.info(f"Project '{project_name}' loaded from: {filepath}")
            return project_data
        except FileNotFoundError:
            logger.error(f"Project file not found: {filepath}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding project JSON file {filepath}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading project '{project_name}' from {filepath}: {e}")
            return None