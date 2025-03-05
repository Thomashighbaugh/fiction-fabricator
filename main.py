
# fiction_fabricator/main.py
import argparse

from  core.project_manager import ProjectManager
from utils.logger import logger


def main():
    """
    Main function for the Fiction Fabricator command-line interface.

    Provides basic command-line access to project management functionalities.
    Currently supports loading and saving projects.
    """
    parser = argparse.ArgumentParser(description="Fiction Fabricator CLI")
    subparsers = parser.add_subparsers(title="commands", dest="command")

    # Save project command
    save_parser = subparsers.add_parser("save", help="Save a project")
    save_parser.add_argument("project_name", help="Name of the project to save")

    # Load project command
    load_parser = subparsers.add_parser("load", help="Load a project")
    load_parser.add_argument("project_name", help="Name of the project to load")

    args = parser.parse_args()

    project_manager = ProjectManager()

    if args.command == "save":
        try:
            # In a real CLI, you would likely load project data into memory first,
            # but for this basic example, we'll just indicate the save action.
            # A more complete CLI would load the current project state from a file or memory.
            project_manager.save_project(args.project_name, book_spec=None) # BookSpec needs to be loaded or passed in a real CLI
            logger.info(f"Project '{args.project_name}' save command executed (data handling not fully implemented in CLI).")
            print(f"Project '{args.project_name}' save command executed (data handling not fully implemented in CLI).")
        except Exception as e:
            logger.error(f"Error saving project from CLI: {e}")
            print(f"Error saving project: {e}")

    elif args.command == "load":
        try:
            project_data = project_manager.load_project(args.project_name)
            if project_data:
                logger.info(f"Project '{args.project_name}' loaded via CLI.")
                print(f"Project '{args.project_name}' loaded successfully (data loaded but not displayed in CLI).")
                # In a real CLI, you might process or display the loaded data here.
            else:
                logger.warning(f"Project '{args.project_name}' not loaded or not found via CLI.")
                print(f"Project '{args.project_name}' not loaded or not found.")
        except Exception as e:
            logger.error(f"Error loading project from CLI: {e}")
            print(f"Error loading project: {e}")

    elif args.command is None:
        parser.print_help()


if __name__ == "__main__":
    main()