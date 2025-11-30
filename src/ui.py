# -*- coding: utf-8 -*-
"""
ui.py - Manages all user interface interactions using the rich library.
"""
from typing import List
import xml.etree.ElementTree as ET

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table
from rich.syntax import Syntax
from pathlib import Path

from src import utils

# --- Global Console Instance ---
console = Console()

def display_welcome(project_name: str | None):
    """Displays the welcome message."""
    title = f"📚 Welcome to Fiction Fabricator! (Project: {project_name or 'New Project'}) 📚"
    console.print(Panel(title, style="bold green"))

def display_summary(project):
    """Displays a summary of the current project state."""
    if project.book_root is None:
        console.print("[red]Cannot display summary, book data not loaded.[/red]")
        return

    title = project.book_root.findtext("title", "N/A")
    synopsis = project.book_root.findtext("synopsis", "N/A")
    chapters = sorted(project.book_root.findall(".//chapter"), key=lambda c: int(utils.get_chapter_id_with_default(c, "0")))

    # Total word count from all paragraphs
    total_wc = sum(utils.count_words(p.text) for p in project.book_root.findall(".//paragraph"))

    console.print(Panel(f"Book Summary: {project.book_root.findtext('title', 'Untitled')}\nTotal Word Count: {total_wc:,}", title=f"Current Status ({project.book_dir.name})", border_style="blue"))

    # Story elements summary
    story_elements = project.book_root.find("story_elements")
    if story_elements is not None:
        elements_table = Table(title="Story Elements", title_style="bold yellow")
        elements_table.add_column("Element", style="bold")
        elements_table.add_column("Value")
        
        genre = story_elements.findtext("genre", "Not specified")
        tone = story_elements.findtext("tone", "Not specified")
        perspective = story_elements.findtext("perspective", "Not specified")
        target_audience = story_elements.findtext("target_audience", "Not specified")
        
        elements_table.add_row("Genre", genre)
        elements_table.add_row("Tone", tone)
        elements_table.add_row("Perspective", perspective)
        elements_table.add_row("Target Audience", target_audience)
        console.print(elements_table)

    # Characters summary
    characters = project.book_root.findall(".//character")
    if characters:
        char_table = Table(title="Characters", title_style="bold magenta")
        char_table.add_column("ID", style="dim")
        char_table.add_column("Name", style="bold")
        char_table.add_column("Description")

        for char in characters:
            desc = char.findtext("description", "")
            char_table.add_row(utils.get_chapter_id_with_default(char), char.findtext("name", ""), f"{desc[:100]}...")
        console.print(char_table)

    # Chapters summary
    if chapters:
        console.print(f"\nChapter count: {len(chapters)}")
        chap_table = Table(title=f"Chapters ({len(chapters)} total)", title_style="bold cyan")
        chap_table.add_column("ID", style="dim")
        chap_table.add_column("Title")
        chap_table.add_column("Summary", justify="center")
        chap_table.add_column("Content", justify="center")
        chap_table.add_column("Word Count", style="magenta", justify="right")

        for chap in chapters:
            # Check for ID as both attribute and child element
            chap_id = utils.get_chapter_id_with_default(chap)
            summary_status = "[green]✓[/green]" if chap.findtext("summary", "").strip() else "[red]✗[/red]"
            paras = chap.findall(".//paragraph")
            has_content = any(p.text and p.text.strip() for p in paras)
            content_status = "[green]✓[/green]" if has_content else "[red]✗[/red]"
            if chap_id in project.chapters_generated_in_session:
                content_status += " [cyan](new)[/cyan]"
            
            word_count = sum(utils.count_words(p.text) for p in paras)
            chap_table.add_row(chap_id, chap.findtext("title", ""), summary_status, content_status, f"{word_count:,}")
        console.print(chap_table)

def prompt_for_new_project_idea(prompt_file: str | None) -> str:
    """Gets the initial book idea from a file or interactive prompt."""
    idea = ""
    if prompt_file:
        try:
            idea = Path(prompt_file).read_text(encoding="utf-8")
            console.print(f"[green]✓ Read book idea from file: {prompt_file}[/green]")
            console.print(f"[dim]Preview: {idea[:200]}...[/dim]")
        except Exception as e:
            console.print(f"[bold red]Error reading prompt file '{prompt_file}': {e}.[/bold red]")
            idea = "" # Fallback to interactive
    
    if not idea:
        idea = Prompt.ask("[yellow]Enter your book idea/description[/yellow]")
    
    return idea.strip()

def prompt_for_story_type() -> str:
    """Asks the user to choose between a novel and a short story."""
    console.print(Panel("Select Project Type", style="bold blue"))
    # CORRECTED LINE: Removed the positional argument that was causing the TypeError.
    choice = Prompt.ask(
        prompt="[1] Novel\n[2] Short Story\nChoose an option",
        choices=["1", "2"],
        default="1",
        show_choices=False,
        console=console
    )
    return "novel" if choice == "1" else "short_story"

def prompt_for_chapter_count() -> int:
    """Asks the user for the approximate number of chapters."""
    return IntPrompt.ask(
        "[yellow]Approximate number of chapters for the full outline? (e.g., 20)[/yellow]",
        default=20,
    )

def display_menu(title: str, options: dict) -> str:
    """A generic function to display a menu and get a choice."""
    console.print(f"\n[bold cyan]{title}:[/bold cyan]")
    choices = []
    for key, (desc, _) in options.items():
        console.print(f"{key}. {desc}")
        choices.append(key)
    
    # Assume the last key is the default/exit option
    return Prompt.ask(
        "[yellow]Choose an action[/yellow]",
        choices=choices,
        default=choices[-1],
    )

def display_patch_suggestion(patch_xml: str):
    """Displays a formatted XML patch for user review."""
    console.print(Panel("[bold cyan]Suggested Patch from LLM:[/bold cyan]", border_style="magenta"))
    syntax = Syntax(patch_xml, "xml", theme="default", line_numbers=True)
    console.print(syntax)

def get_chapter_selection(project, prompt_text: str, allow_multiple: bool) -> List[ET.Element]:
    """Prompts the user for chapter IDs and validates them."""
    all_chapter_ids = {utils.get_chapter_id(chap) for chap in project.book_root.findall(".//chapter")}
    if not all_chapter_ids:
        console.print("[yellow]No chapters found in the project.[/yellow]")
        return []

    while True:
        sorted_ids = sorted(all_chapter_ids, key=int)
        raw_input = Prompt.ask(f"{prompt_text} (Available: {', '.join(sorted_ids)})")
        selected_ids = {s.strip() for s in raw_input.split(",") if s.strip()}

        if not allow_multiple and len(selected_ids) > 1:
            console.print("[red]Only one chapter ID is allowed. Please try again.[/red]")
            continue
        
        invalid_ids = selected_ids - all_chapter_ids
        if invalid_ids:
            console.print(f"[red]Invalid chapter IDs: {', '.join(invalid_ids)}. Please try again.[/red]")
            continue

        return [project.find_chapter(cid) for cid in sorted(selected_ids, key=int) if project.find_chapter(cid) is not None]

def prompt_for_lorebook_selection() -> str | None:
    """Prompts the user to optionally select a lorebook file."""
    import glob
    from pathlib import Path
    
    console.print("\n[bold cyan]Lorebook Integration[/bold cyan]")
    
    # Look for JSON files in current directory and lorebooks subdirectory
    json_files = glob.glob("*.json")
    lorebooks_dir = Path("lorebooks")
    if lorebooks_dir.exists():
        lorebook_files = list(lorebooks_dir.glob("*.json"))
        if lorebook_files:
            console.print("[cyan]Found lorebook files in lorebooks/ directory:[/cyan]")
            for i, file in enumerate(lorebook_files, 1):
                console.print(f"  {i}. {file}")
    
    if json_files:
        console.print("[cyan]Found JSON files in current directory that could be lorebooks:[/cyan]")
        for i, file in enumerate(json_files, 1):
            console.print(f"  {i}. {file}")
    
    if not Confirm.ask("[yellow]Would you like to use a lorebook for additional world-building context?[/yellow]", default=False):
        return None
    
    while True:
        lorebook_path = Prompt.ask(
            "[cyan]Enter the path to your lorebook JSON file[/cyan]\n"
            "(Tavern AI format supported)",
            default=""
        ).strip()
        
        if not lorebook_path:
            console.print("[dim]No lorebook selected.[/dim]")
            return None
        
        path = Path(lorebook_path)
        if not path.exists():
            console.print(f"[red]File not found: {lorebook_path}[/red]")
            if not Confirm.ask("Try again?", default=True):
                return None
            continue
        
        if not path.suffix.lower() == '.json':
            console.print(f"[yellow]Warning: {lorebook_path} doesn't have a .json extension[/yellow]")
            if not Confirm.ask("Use anyway?", default=True):
                continue
        
        console.print(f"[green]Selected lorebook: {lorebook_path}[/green]")
        return lorebook_path

def prompt_for_lorebook_creation_or_import() -> tuple[str | None, bool]:
    """
    Prompts the user to create a new lorebook or import an existing one.
    
    Returns:
        tuple: (lorebook_path, is_import) where is_import indicates if this is an import operation
    """
    import glob
    from pathlib import Path
    
    console.print("\n[bold cyan]Lorebook Setup[/bold cyan]")
    
    # Show available options
    console.print("Options:")
    console.print("1. Create a new lorebook")
    console.print("2. Import from TavernAI/SillyTavern lorebook")
    console.print("3. Use existing Fiction Fabricator lorebook")
    console.print("4. Skip lorebook setup")
    
    choice = Prompt.ask(
        "[yellow]Choose an option[/yellow]",
        choices=["1", "2", "3", "4"],
        default="4"
    )
    
    if choice == "1":
        # Create new lorebook - return path where it should be saved
        lorebook_name = Prompt.ask(
            "[cyan]Enter name for the new lorebook[/cyan]",
            default="lorebook"
        ).strip()
        
        # Ensure lorebooks directory exists
        lorebooks_dir = Path("lorebooks")
        lorebooks_dir.mkdir(exist_ok=True)
        
        # Create filename with .json extension
        if not lorebook_name.endswith(".json"):
            lorebook_name += ".json"
        
        lorebook_path = lorebooks_dir / lorebook_name
        return str(lorebook_path), False
        
    elif choice == "2":
        # Import from TavernAI
        console.print("\n[cyan]Import from TavernAI/SillyTavern Lorebook[/cyan]")
        
        while True:
            import_path = Prompt.ask(
                "[cyan]Enter path to TavernAI/SillyTavern lorebook JSON file[/cyan]",
                default=""
            ).strip()
            
            if not import_path:
                console.print("[dim]Import cancelled.[/dim]")
                return None, False
            
            path = Path(import_path)
            if not path.exists():
                console.print(f"[red]File not found: {import_path}[/red]")
                if not Confirm.ask("Try again?", default=True):
                    return None, False
                continue
            
            if not path.suffix.lower() == '.json':
                console.print(f"[yellow]Warning: {import_path} doesn't have a .json extension[/yellow]")
                if not Confirm.ask("Import anyway?", default=True):
                    continue
            
            # Ask where to save the converted lorebook
            default_name = path.stem + "_converted.json"
            output_name = Prompt.ask(
                "[cyan]Enter name for the converted lorebook[/cyan]",
                default=default_name
            ).strip()
            
            # Ensure lorebooks directory exists
            lorebooks_dir = Path("lorebooks")
            lorebooks_dir.mkdir(exist_ok=True)
            
            # Create output filename with .json extension
            if not output_name.endswith(".json"):
                output_name += ".json"
            
            output_path = lorebooks_dir / output_name
            
            # Perform the import
            try:
                from src.utils import convert_tavern_lorebook_to_fiction_fabricator
                import json
                
                console.print(f"[yellow]Converting lorebook from {import_path}...[/yellow]")
                converted_data = convert_tavern_lorebook_to_fiction_fabricator(import_path)
                
                # Save the converted lorebook
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(converted_data, f, indent=2, ensure_ascii=False)
                
                console.print(f"[green]✓ Successfully imported and converted lorebook to: {output_path}[/green]")
                console.print(f"[green]✓ Converted {len(converted_data['entries'])} entries[/green]")
                
                return str(output_path), True
                
            except Exception as e:
                console.print(f"[red]Error importing lorebook: {e}[/red]")
                if not Confirm.ask("Try a different file?", default=True):
                    return None, False
                continue
    
    elif choice == "3":
        # Use existing Fiction Fabricator lorebook
        # Look for JSON files in current directory and lorebooks subdirectory
        json_files = glob.glob("*.json")
        lorebooks_dir = Path("lorebooks")
        lorebook_files = []
        
        if lorebooks_dir.exists():
            lorebook_files = list(lorebooks_dir.glob("*.json"))
            if lorebook_files:
                console.print("[cyan]Found lorebook files in lorebooks/ directory:[/cyan]")
                for i, file in enumerate(lorebook_files, 1):
                    console.print(f"  {i}. {file}")
        
        if json_files:
            console.print("[cyan]Found JSON files in current directory that could be lorebooks:[/cyan]")
            for i, file in enumerate(json_files, 1):
                console.print(f"  {i}. {file}")
        
        while True:
            lorebook_path = Prompt.ask(
                "[cyan]Enter the path to your Fiction Fabricator lorebook JSON file[/cyan]",
                default=""
            ).strip()
            
            if not lorebook_path:
                console.print("[dim]No lorebook selected.[/dim]")
                return None, False
            
            path = Path(lorebook_path)
            if not path.exists():
                console.print(f"[red]File not found: {lorebook_path}[/red]")
                if not Confirm.ask("Try again?", default=True):
                    return None, False
                continue
            
            if not path.suffix.lower() == '.json':
                console.print(f"[yellow]Warning: {lorebook_path} doesn't have a .json extension[/yellow]")
                if not Confirm.ask("Use anyway?", default=True):
                    continue
            
            console.print(f"[green]Selected lorebook: {lorebook_path}[/green]")
            return lorebook_path, False
    
    else:  # choice == "4"
        console.print("[dim]Skipping lorebook setup.[/dim]")
        return None, False
