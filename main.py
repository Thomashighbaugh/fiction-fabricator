# -*- coding: utf-8 -*-
"""
main.py - The main entry point for the Fiction Fabricator application.
"""
import argparse
from pathlib import Path

from src import ui
from src.llm_client import LLMClient
from src.project import Project
from src.orchestrator import Orchestrator

def main():
    """Initializes and runs the Fiction Fabricator application."""
    parser = argparse.ArgumentParser(description="An AI agent for drafting novels and short stories.")
    parser.add_argument(
        "--resume",
        metavar="FOLDER_PATH",
        help="Path to an existing project folder to resume.",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--prompt",
        metavar="FILE_PATH",
        help="Path to a text file with the initial idea (for new projects only).",
        type=str,
        default=None,
    )
    args = parser.parse_args()

    try:
        # --- Initialization ---
        project = Project(ui.console, resume_folder_name=args.resume)
        ui.display_welcome(project.book_dir.name if project.book_dir else None)
        
        llm_client = LLMClient(ui.console)
        orchestrator = Orchestrator(project, llm_client)

        # --- Workflow ---
        if args.resume:
            # If resuming, project is already loaded, go straight to the main run
            orchestrator.run()
        else:
            # New project workflow
            idea = ui.prompt_for_new_project_idea(args.prompt)
            if not idea:
                ui.console.print("[red]No idea provided. Exiting.[/red]")
                return
            
            # Setup new project (gets title, creates files)
            if orchestrator.setup_new_project(idea):
                # Run the main generation process
                orchestrator.run()

    except (ValueError, ConnectionError, FileNotFoundError) as e:
        ui.console.print(f"\n[bold red]Initialization Error: {e}[/bold red]")
    except KeyboardInterrupt:
        ui.console.print("\n[bold yellow]Operation interrupted by user. Exiting.[/bold yellow]")
    except Exception as e:
        ui.console.print("\n[bold red]An unexpected critical error occurred:[/bold red]")
        ui.console.print_exception(show_locals=False, word_wrap=True)

if __name__ == "__main__":
    main()
