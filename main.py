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
    parser.add_argument(
        "--lorebook",
        metavar="JSON_FILE",
        help="Path to a JSON lorebook file (Tavern AI format) to provide additional context.",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--create-lorebook",
        metavar="JSON_FILE",
        help="Create or edit a lorebook file interactively with LLM assistance.",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--create-prompt",
        action="store_true",
        help="Create an enhanced story prompt from a basic idea using LLM assistance.",
        default=False,
    )
    args = parser.parse_args()

    try:
        # --- Lorebook Creation Mode ---
        if args.create_lorebook:
            # Create LLM client for lorebook management
            llm_client = LLMClient(ui.console)
            # Create minimal orchestrator just for lorebook management
            project = Project(ui.console)  # Dummy project for lorebook mode
            orchestrator = Orchestrator(project, llm_client)
            
            # Run lorebook management interface
            orchestrator.manage_lorebook(args.create_lorebook)
            return

        # --- Prompt Enhancement Mode ---
        if args.create_prompt:
            # Create LLM client for prompt expansion
            llm_client = LLMClient(ui.console)
            # Create minimal orchestrator just for prompt expansion  
            project = Project(ui.console)  # Dummy project for prompt mode
            orchestrator = Orchestrator(project, llm_client, lorebook_path=args.lorebook)
            
            # Run prompt enhancement interface
            orchestrator.create_enhanced_prompt()
            return

        # --- Standard Fiction Generation Mode ---
        # --- Initialization ---
        project = Project(ui.console, resume_folder_name=args.resume)
        ui.display_welcome(project.book_dir.name if project.book_dir else None)
        
        llm_client = LLMClient(ui.console)
        orchestrator = Orchestrator(project, llm_client, lorebook_path=args.lorebook)

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
