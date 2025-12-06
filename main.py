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
        help="Create or edit a lorebook file interactively with LLM assistance. If JSON_FILE is provided and exists, it will be imported; otherwise a new lorebook will be created.",
        type=str,
        nargs="?",
        const="",
        default=None,
    )
    parser.add_argument(
        "--create-prompt",
        action="store_true",
        help="Create an enhanced story prompt from a basic idea using LLM assistance.",
        default=False,
    )
    parser.add_argument(
        "--character-card",
        metavar="FILE_PATH",
        help="Path to a TavernAI/SillyTavern character card file (JSON or PNG) to convert into a story premise.",
        type=str,
        default=None,
    )
    args = parser.parse_args()

    try:
        # --- Lorebook Creation Mode ---
        if args.create_lorebook is not None:
            from pathlib import Path
            from rich.prompt import Prompt, Confirm
            import json
            
            # Ensure lorebooks directory exists
            lorebooks_dir = Path("lorebooks")
            lorebooks_dir.mkdir(exist_ok=True)
            
            ui.console.print("\n[bold cyan]📚 Lorebook Creation[/bold cyan]")
            
            lorebook_path = None
            is_import = False
            
            # Check if a file path was provided and if it exists
            if args.create_lorebook:
                provided_path = Path(args.create_lorebook)
                if provided_path.exists():
                    # File exists - offer to import it
                    ui.console.print(f"[green]Found existing file: {provided_path}[/green]")
                    if Prompt.ask(
                        "[yellow]Import this existing lorebook?[/yellow]",
                        choices=["y", "n"],
                        default="y"
                    ).lower() == "y":
                        # Import the existing file
                        try:
                            # Test if it's valid JSON
                            with open(provided_path, 'r', encoding='utf-8') as f:
                                existing_data = json.load(f)
                            
                            # Determine where to save it in lorebooks directory
                            target_name = provided_path.name
                            if not target_name.endswith('.json'):
                                target_name += '.json'
                            
                            lorebook_path = lorebooks_dir / target_name
                            
                            # If target already exists, ask for confirmation
                            if lorebook_path.exists():
                                if not Confirm.ask(f"[yellow]Overwrite existing {lorebook_path}?[/yellow]"):
                                    # Ask for new name
                                    new_name = Prompt.ask(
                                        "[cyan]Enter a new name for the imported lorebook[/cyan]",
                                        default=f"imported_{target_name}"
                                    ).strip()
                                    if not new_name.endswith('.json'):
                                        new_name += '.json'
                                    lorebook_path = lorebooks_dir / new_name
                            
                            # Copy/import the file
                            import shutil
                            shutil.copy2(provided_path, lorebook_path)
                            ui.console.print(f"[green]Imported lorebook to: {lorebook_path}[/green]")
                            is_import = True
                            
                        except json.JSONDecodeError:
                            ui.console.print(f"[red]Error: {provided_path} is not a valid JSON file[/red]")
                            ui.console.print("[yellow]Continuing with lorebook creation instead...[/yellow]")
                        except Exception as e:
                            ui.console.print(f"[red]Error importing {provided_path}: {e}[/red]")
                            ui.console.print("[yellow]Continuing with lorebook creation instead...[/yellow]")
                    
                    # If import failed or declined, fall through to creation
                else:
                    # File doesn't exist - use provided path as basis for new lorebook name
                    ui.console.print(f"[yellow]File {provided_path} doesn't exist, will create new lorebook[/yellow]")
            
            # If no lorebook path set yet, create new one
            if not lorebook_path:
                # Get lorebook name from user
                default_name = Path(args.create_lorebook).stem if args.create_lorebook else "lorebook"
                lorebook_name = Prompt.ask(
                    "[yellow]Enter a name for your lorebook[/yellow]",
                    default=default_name
                ).strip()
                
                # Ensure .json extension
                if not lorebook_name.endswith('.json'):
                    lorebook_name += '.json'
                
                # Create full path in lorebooks directory
                lorebook_path = lorebooks_dir / lorebook_name
                
                ui.console.print(f"[green]Creating lorebook: {lorebook_path}[/green]")
            
            # Create LLM client for lorebook management
            llm_client = LLMClient(ui.console)
            # Create minimal orchestrator just for lorebook management
            project = Project(ui.console)  # Dummy project for lorebook mode
            orchestrator = Orchestrator(project, llm_client)
            
            # Run lorebook management interface
            orchestrator.manage_lorebook(str(lorebook_path))
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
        
        # Handle character card import if specified
        character_card_premise = None
        if args.character_card:
            from src.utils import load_character_card, convert_character_card_to_premise
            
            ui.console.print(f"[cyan]Loading character card from: {args.character_card}[/cyan]")
            character_data = load_character_card(args.character_card)
            
            if character_data:
                ui.console.print("[green]✓ Character card loaded successfully[/green]")
                character_card_premise = convert_character_card_to_premise(character_data)
                ui.console.print("[cyan]Converted character card to story premise[/cyan]")
            else:
                ui.console.print(f"[red]Error: Failed to load character card from {args.character_card}[/red]")
                ui.console.print("[yellow]Continuing with normal prompt workflow...[/yellow]")
        
        # If no --resume and no --prompt, ask user what they want to do
        resume_folder = args.resume
        if not resume_folder and not args.prompt and not character_card_premise:
            is_new, project_folder, imported_premise = ui.prompt_for_project_selection()
            if not is_new and project_folder:
                resume_folder = project_folder
            elif is_new and imported_premise:
                # User imported a character card
                character_card_premise = imported_premise
        
        project = Project(ui.console, resume_folder_name=resume_folder)
        ui.display_welcome(project.book_dir.name if project.book_dir else None)
        
        llm_client = LLMClient(ui.console)
        orchestrator = Orchestrator(project, llm_client, lorebook_path=args.lorebook)

        # --- Workflow ---
        if resume_folder:
            # If resuming, project is already loaded, go straight to the main run
            orchestrator.run()
        else:
            # New project workflow
            # Use character card premise if available, otherwise get idea normally
            if character_card_premise:
                idea = character_card_premise
            else:
                idea = ui.prompt_for_new_project_idea(args.prompt)
            # Note: prompt_for_new_project_idea now guarantees a non-empty idea
            
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
