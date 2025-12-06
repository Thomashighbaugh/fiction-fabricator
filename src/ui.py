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
from bullet import Bullet, colors

from src import utils

# --- Global Console Instance ---
console = Console()

def bullet_choice(prompt: str, choices: List[str]) -> str:
    """
    Creates an interactive bullet menu using the star style from bullet.
    
    Args:
        prompt: The prompt text to display
        choices: List of choice strings
    
    Returns:
        The selected choice string
    """
    cli = Bullet(
        prompt=f"\n{prompt}",
        choices=choices,
        indent=0,
        align=5,
        margin=2,
        bullet="★",
        bullet_color=colors.bright(colors.foreground["cyan"]),
        word_color=colors.bright(colors.foreground["yellow"]),
        word_on_switch=colors.bright(colors.foreground["yellow"]),
        background_color=colors.background["black"],
        background_on_switch=colors.background["black"],
        pad_right=5
    )
    return cli.launch()

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
    """Gets the initial book idea from a file, character card import, or interactive prompt."""
    idea = ""
    if prompt_file:
        try:
            idea = Path(prompt_file).read_text(encoding="utf-8")
            console.print(f"[green]✓ Read book idea from file: {prompt_file}[/green]")
            console.print(f"[dim]Preview: {idea[:200]}...[/dim]")
        except Exception as e:
            console.print(f"[bold red]Error reading prompt file '{prompt_file}': {e}.[/bold red]")
            idea = "" # Fallback to interactive
    
    # Loop until a non-empty idea is provided
    while not idea:
        try:
            console.print("\n[bold cyan]Let's create a new story![/bold cyan]")
            
            # Offer character card import option
            character_premise = prompt_for_character_card_import()
            if character_premise:
                return character_premise
            
            console.print("[dim]Enter a brief description of your story idea (a few sentences or paragraphs)[/dim]")
            idea = Prompt.ask("[yellow]Your book idea/description[/yellow]")
            idea = idea.strip()
            
            if not idea:
                console.print("[red]Error: Book idea cannot be empty. Please provide a description.[/red]")
        except EOFError:
            # Handle EOF (Ctrl+D or piped empty input)
            console.print("\n[red]Error: No input provided. Please provide a book idea.[/red]")
            console.print("[yellow]Tip: Use --prompt FILE to provide a book idea from a file[/yellow]")
            raise KeyboardInterrupt("No input available")
    
    return idea

def prompt_for_story_type() -> str:
    """Asks the user to choose between a novel and a short story."""
    console.print(Panel("Select Project Type", style="bold blue"))
    
    choice = bullet_choice(
        "Choose project type:",
        ["Novel", "Short Story"]
    )
    
    return "novel" if choice == "Novel" else "short_story"

def prompt_for_chapter_count() -> int:
    """Asks the user for the approximate number of chapters."""
    return IntPrompt.ask(
        "[yellow]Approximate number of chapters for the full outline? (e.g., 20)[/yellow]",
        default=20,
    )

def review_and_modify_story_elements(project) -> dict:
    """
    Displays current story elements and allows user to modify them.
    
    Args:
        project: The project object containing story elements
    
    Returns:
        dict: Dictionary with potentially modified title, genre, tone, perspective, and target_audience
    """
    console.print("\n" + "="*80)
    console.print(Panel("[bold cyan]Story Elements Review[/bold cyan]", style="bold blue"))
    
    # Get current title
    current_title = project.book_root.findtext("title", "Untitled")
    
    # Get current story elements
    story_elements = project.book_root.find("story_elements")
    if story_elements is None:
        console.print("[red]Warning: No story elements found in project.[/red]")
        return {}
    
    current_genre = story_elements.findtext("genre", "Not specified")
    current_tone = story_elements.findtext("tone", "Not specified")
    current_perspective = story_elements.findtext("perspective", "Not specified")
    current_target_audience = story_elements.findtext("target_audience", "Not specified")
    
    # Display current elements in a table
    table = Table(title="Generated Story Elements", title_style="bold yellow")
    table.add_column("Element", style="bold cyan", width=20)
    table.add_column("Current Value", style="yellow", width=50)
    
    table.add_row("Title", current_title)
    table.add_row("Genre", current_genre)
    table.add_row("Tone", current_tone)
    table.add_row("Perspective", current_perspective)
    table.add_row("Target Audience", current_target_audience)
    
    console.print(table)
    console.print()
    
    # Ask if user wants to modify
    if not Confirm.ask(
        "[yellow]Would you like to modify any of these story elements?[/yellow]",
        default=False
    ):
        console.print("[green]Keeping generated story elements as-is.[/green]")
        return {
            "title": current_title,
            "genre": current_genre,
            "tone": current_tone,
            "perspective": current_perspective,
            "target_audience": current_target_audience
        }
    
    # Prompt for modifications
    console.print("\n[dim]Press Enter to keep the current value, or type a new value to change it.[/dim]\n")
    
    new_title = Prompt.ask(
        f"[cyan]Title[/cyan] [dim](current: {current_title})[/dim]",
        default=current_title
    ).strip()
    
    new_genre = Prompt.ask(
        f"[cyan]Genre[/cyan] [dim](current: {current_genre})[/dim]",
        default=current_genre
    ).strip()
    
    new_tone = Prompt.ask(
        f"[cyan]Tone[/cyan] [dim](current: {current_tone})[/dim]",
        default=current_tone
    ).strip()
    
    new_perspective = Prompt.ask(
        f"[cyan]Perspective[/cyan] [dim](current: {current_perspective})[/dim]",
        default=current_perspective
    ).strip()
    
    new_target_audience = Prompt.ask(
        f"[cyan]Target Audience[/cyan] [dim](current: {current_target_audience})[/dim]",
        default=current_target_audience
    ).strip()
    
    # Display summary of changes
    changes_made = []
    if new_title != current_title:
        changes_made.append(f"Title: {current_title} → {new_title}")
    if new_genre != current_genre:
        changes_made.append(f"Genre: {current_genre} → {new_genre}")
    if new_tone != current_tone:
        changes_made.append(f"Tone: {current_tone} → {new_tone}")
    if new_perspective != current_perspective:
        changes_made.append(f"Perspective: {current_perspective} → {new_perspective}")
    if new_target_audience != current_target_audience:
        changes_made.append(f"Target Audience: {current_target_audience} → {new_target_audience}")
    
    if changes_made:
        console.print("\n[bold green]Changes made:[/bold green]")
        for change in changes_made:
            console.print(f"  • {change}")
    else:
        console.print("\n[dim]No changes made.[/dim]")
    
    console.print("="*80 + "\n")
    
    return {
        "title": new_title,
        "genre": new_genre,
        "tone": new_tone,
        "perspective": new_perspective,
        "target_audience": new_target_audience
    }

def display_menu(title: str, options: dict) -> str:
    """A generic function to display a menu and get a choice."""
    console.print(f"\n[bold cyan]{title}:[/bold cyan]")
    
    # Build choices list with descriptions
    choice_items = []
    key_mapping = {}
    for key, (desc, _) in options.items():
        choice_items.append(f"{key}. {desc}")
        key_mapping[f"{key}. {desc}"] = key
    
    # Use bullet for interactive selection
    selected = bullet_choice(
        "Choose an action:",
        choice_items
    )
    
    return key_mapping[selected]

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
    
    # Show available options using bullet
    choice = bullet_choice(
        "Choose an option:",
        [
            "1. Create a new lorebook",
            "2. Import from TavernAI/SillyTavern lorebook",
            "3. Use existing Fiction Fabricator lorebook",
            "4. Skip lorebook setup"
        ]
    )
    
    choice_num = choice[0]  # Get the first character (the number)
    
    if choice_num == "1":
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
        
    elif choice_num == "2":
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
    
    elif choice_num == "3":
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
    
    else:  # choice_num == "4"
        console.print("[dim]Skipping lorebook setup.[/dim]")
        return None, False

def prompt_for_project_selection() -> tuple[bool, str | None, str | None]:
    """
    Prompts the user to start a new project or load an existing one.
    
    Returns:
        tuple: (is_new_project, project_folder_name, character_card_premise)
               - is_new_project: True if starting new, False if loading existing
               - project_folder_name: Name of existing project folder or None for new project
               - character_card_premise: Converted character card premise if imported, None otherwise
    """
    console.print("\n[bold cyan]Fiction Fabricator[/bold cyan]")
    
    # Check if projects directory exists and has projects
    projects_dir = Path("projects")
    existing_projects = []
    
    if projects_dir.exists():
        # Get all subdirectories in projects/
        existing_projects = [p for p in projects_dir.iterdir() if p.is_dir()]
        existing_projects.sort(key=lambda p: p.stat().st_mtime, reverse=True)  # Sort by most recent
    
    choices = ["1. Start a new project"]
    
    if existing_projects:
        choices.append("2. Load an existing project")
    
    # Always show character card import option
    choices.append(f"{len(choices) + 1}. Import character card to start new project")
    
    choice = bullet_choice(
        "What would you like to do?",
        choices
    )
    
    choice_num = choice[0]  # Get the first character (the number)
    
    if choice_num == "1":
        # Start new project
        return True, None, None
    
    elif choice_num == "2" and existing_projects:
        # Load existing project
        console.print("\n[bold]Available Projects:[/bold]")
        
        # Display projects with details
        project_choices = []
        for i, project_path in enumerate(existing_projects, 1):
            # Try to get project title from outline.xml
            title = "Unknown Title"
            outline_file = project_path / "outline.xml"
            if outline_file.exists():
                try:
                    tree = ET.parse(outline_file)
                    root = tree.getroot()
                    title_elem = root.find("title")
                    if title_elem is not None and title_elem.text:
                        title = title_elem.text
                except:
                    pass
            
            project_choices.append(f"{i}. {project_path.name} - {title}")
        
        project_choices.append(f"{len(project_choices) + 1}. Cancel (start new project instead)")
        
        selected = bullet_choice(
            "Select a project to load:",
            project_choices
        )
        
        # Extract the number from the selection
        selected_num = int(selected.split(".")[0])
        
        # Check if user cancelled
        if selected_num > len(existing_projects):
            console.print("[dim]Starting new project instead.[/dim]")
            return True, None, None
        
        # Return the selected project folder name
        selected_project = existing_projects[selected_num - 1]
        console.print(f"[green]Loading project: {selected_project.name}[/green]")
        return False, selected_project.name, None
    
    else:
        # Import character card
        console.print("\n[bold cyan]Import Character Card[/bold cyan]")
        console.print("[dim]Supports TavernAI/SillyTavern character cards (JSON or PNG format)[/dim]")
        
        file_path = Prompt.ask(
            "[cyan]Enter path to character card file (.json or .png)[/cyan]",
            default=""
        ).strip()
        
        if not file_path:
            console.print("[yellow]No file provided, starting new project instead.[/yellow]")
            return True, None, None
        
        path = Path(file_path)
        
        if not path.exists():
            console.print(f"[red]Error: File not found: {file_path}[/red]")
            console.print("[yellow]Starting new project instead.[/yellow]")
            return True, None, None
        
        # Try to load the character card
        from src.utils import load_character_card, convert_character_card_to_premise
        
        console.print("[cyan]Loading character card...[/cyan]")
        character_data = load_character_card(str(path))
        
        if not character_data:
            console.print("[red]Error: Failed to load character card. The file may be corrupted or in an unsupported format.[/red]")
            console.print("[yellow]Starting new project instead.[/yellow]")
            return True, None, None
        
        # Convert to premise
        console.print("[cyan]Converting character card to story premise...[/cyan]")
        premise = convert_character_card_to_premise(character_data)
        
        # Display preview
        console.print(Panel(
            premise[:500] + ("..." if len(premise) > 500 else ""),
            title="[bold green]Character Card Converted to Premise[/bold green]",
            border_style="green"
        ))
        
        if not Confirm.ask("\n[yellow]Use this character card as the story premise?[/yellow]", default=True):
            console.print("[dim]Character card import cancelled, starting new project instead.[/dim]")
            return True, None, None
        
        return True, None, premise
    
    # Fallback to new project
    return True, None, None

def manage_outline_chapters(project) -> bool:
    """
    Interactive chapter management interface for editing the outline.
    
    Args:
        project: The project object containing the outline
        
    Returns:
        bool: True if changes were made, False otherwise
    """
    if not project.book_root:
        console.print("[red]Error: No project loaded.[/red]")
        return False
    
    chapters = project.book_root.findall(".//chapter")
    if not chapters:
        console.print("[red]Error: No chapters found in outline.[/red]")
        return False
    
    changes_made = False
    
    while True:
        console.print("\n" + "="*80)
        console.print(Panel("[bold cyan]Outline Chapter Management[/bold cyan]", style="bold blue"))
        
        choice = bullet_choice(
            "Select an action:",
            [
                "1. List all chapters",
                "2. Edit a chapter",
                "3. Add a new chapter",
                "4. Delete a chapter",
                "5. Reorder chapters",
                "6. Save and continue"
            ]
        )
        
        choice_num = choice[0]
        
        if choice_num == "1":
            _list_chapters(project)
        elif choice_num == "2":
            if _edit_chapter(project):
                changes_made = True
        elif choice_num == "3":
            if _add_chapter(project):
                changes_made = True
        elif choice_num == "4":
            if _delete_chapter(project):
                changes_made = True
        elif choice_num == "5":
            if _reorder_chapters(project):
                changes_made = True
        elif choice_num == "6":
            if changes_made:
                if project.save_state("outline.xml"):
                    console.print("[green]Outline saved successfully![/green]")
                else:
                    console.print("[red]Error saving outline.[/red]")
            break
    
    return changes_made

def _list_chapters(project):
    """List all chapters in the outline."""
    chapters = project.book_root.findall(".//chapter")
    
    console.print(f"\n[bold]Chapters in Outline ({len(chapters)}):[/bold]\n")
    
    table = Table(title="Chapter Outline", title_style="bold yellow")
    table.add_column("#", style="bold cyan", width=5)
    table.add_column("ID", style="dim", width=15)
    table.add_column("Title", style="yellow", width=30)
    table.add_column("Summary", style="white", width=50)
    
    for i, chapter in enumerate(chapters, 1):
        chapter_id = chapter.get("id", "N/A")
        number = chapter.findtext("number", str(i))
        title = chapter.findtext("title", "Untitled")
        summary = chapter.findtext("summary", "No summary")
        
        # Truncate summary if too long
        if len(summary) > 100:
            summary = summary[:97] + "..."
        
        table.add_row(number, chapter_id, title, summary)
    
    console.print(table)

def _edit_chapter(project) -> bool:
    """Edit an existing chapter."""
    chapters = project.book_root.findall(".//chapter")
    
    console.print("\n[bold]Select a chapter to edit:[/bold]")
    _list_chapters(project)
    
    chapter_num = IntPrompt.ask(
        f"\n[cyan]Enter chapter number to edit (1-{len(chapters)})[/cyan]",
        default=1
    )
    
    if chapter_num < 1 or chapter_num > len(chapters):
        console.print("[red]Invalid chapter number.[/red]")
        return False
    
    chapter = chapters[chapter_num - 1]
    
    current_title = chapter.findtext("title", "")
    current_summary = chapter.findtext("summary", "")
    
    console.print(f"\n[bold]Editing Chapter {chapter_num}[/bold]")
    console.print(f"Current Title: [yellow]{current_title}[/yellow]")
    console.print(f"Current Summary: [dim]{current_summary}[/dim]\n")
    
    new_title = Prompt.ask(
        "[cyan]New title[/cyan] (press Enter to keep current)",
        default=current_title
    ).strip()
    
    new_summary = Prompt.ask(
        "[cyan]New summary[/cyan] (press Enter to keep current)",
        default=current_summary
    ).strip()
    
    if new_title != current_title or new_summary != current_summary:
        title_elem = chapter.find("title")
        if title_elem is not None:
            title_elem.text = new_title
        else:
            ET.SubElement(chapter, "title").text = new_title
        
        summary_elem = chapter.find("summary")
        if summary_elem is not None:
            summary_elem.text = new_summary
        else:
            ET.SubElement(chapter, "summary").text = new_summary
        
        console.print("[green]Chapter updated![/green]")
        return True
    
    console.print("[dim]No changes made.[/dim]")
    return False

def _add_chapter(project) -> bool:
    """Add a new chapter to the outline."""
    chapters = project.book_root.findall(".//chapter")
    
    console.print("\n[bold]Add New Chapter[/bold]")
    
    # Ask for position
    position = IntPrompt.ask(
        f"[cyan]Insert at position (1-{len(chapters) + 1})[/cyan]",
        default=len(chapters) + 1
    )
    
    if position < 1 or position > len(chapters) + 1:
        console.print("[red]Invalid position.[/red]")
        return False
    
    title = Prompt.ask("[cyan]Chapter title[/cyan]").strip()
    summary = Prompt.ask("[cyan]Chapter summary[/cyan]").strip()
    
    if not title or not summary:
        console.print("[red]Title and summary are required.[/red]")
        return False
    
    # Create new chapter element
    new_chapter = ET.Element("chapter")
    new_chapter.set("id", f"ch-{len(chapters) + 1}")
    ET.SubElement(new_chapter, "number").text = str(position)
    ET.SubElement(new_chapter, "title").text = title
    ET.SubElement(new_chapter, "summary").text = summary
    
    # Find parent element (outline or book root)
    parent = project.book_root.find("outline")
    if parent is None:
        parent = project.book_root
    
    # Insert at the specified position
    if position > len(chapters):
        parent.append(new_chapter)
    else:
        parent.insert(position - 1, new_chapter)
    
    # Renumber all chapters
    for i, ch in enumerate(parent.findall(".//chapter"), 1):
        num_elem = ch.find("number")
        if num_elem is not None:
            num_elem.text = str(i)
    
    console.print(f"[green]Added new chapter at position {position}![/green]")
    return True

def _delete_chapter(project) -> bool:
    """Delete a chapter from the outline."""
    chapters = project.book_root.findall(".//chapter")
    
    if len(chapters) <= 1:
        console.print("[red]Cannot delete the only chapter.[/red]")
        return False
    
    console.print("\n[bold]Select a chapter to delete:[/bold]")
    _list_chapters(project)
    
    chapter_num = IntPrompt.ask(
        f"\n[cyan]Enter chapter number to delete (1-{len(chapters)})[/cyan]",
        default=1
    )
    
    if chapter_num < 1 or chapter_num > len(chapters):
        console.print("[red]Invalid chapter number.[/red]")
        return False
    
    chapter = chapters[chapter_num - 1]
    title = chapter.findtext("title", "Untitled")
    
    if not Confirm.ask(f"[yellow]Delete chapter {chapter_num}: '{title}'?[/yellow]", default=False):
        console.print("[dim]Deletion cancelled.[/dim]")
        return False
    
    # Find parent and remove chapter
    parent = project.book_root.find("outline")
    if parent is None:
        parent = project.book_root
    
    parent.remove(chapter)
    
    # Renumber remaining chapters
    for i, ch in enumerate(parent.findall(".//chapter"), 1):
        num_elem = ch.find("number")
        if num_elem is not None:
            num_elem.text = str(i)
    
    console.print(f"[green]Chapter {chapter_num} deleted and chapters renumbered![/green]")
    return True

def _reorder_chapters(project) -> bool:
    """Reorder chapters in the outline."""
    chapters = project.book_root.findall(".//chapter")
    
    console.print("\n[bold]Reorder Chapters[/bold]")
    _list_chapters(project)
    
    from_pos = IntPrompt.ask(
        f"\n[cyan]Move chapter from position (1-{len(chapters)})[/cyan]",
        default=1
    )
    
    if from_pos < 1 or from_pos > len(chapters):
        console.print("[red]Invalid position.[/red]")
        return False
    
    to_pos = IntPrompt.ask(
        f"[cyan]Move to position (1-{len(chapters)})[/cyan]",
        default=1
    )
    
    if to_pos < 1 or to_pos > len(chapters):
        console.print("[red]Invalid position.[/red]")
        return False
    
    if from_pos == to_pos:
        console.print("[dim]No change needed.[/dim]")
        return False
    
    # Find parent
    parent = project.book_root.find("outline")
    if parent is None:
        parent = project.book_root
    
    # Remove and reinsert
    chapter_to_move = chapters[from_pos - 1]
    parent.remove(chapter_to_move)
    parent.insert(to_pos - 1, chapter_to_move)
    
    # Renumber all chapters
    for i, ch in enumerate(parent.findall(".//chapter"), 1):
        num_elem = ch.find("number")
        if num_elem is not None:
            num_elem.text = str(i)
    
    console.print(f"[green]Moved chapter from position {from_pos} to {to_pos}![/green]")
    return True

def prompt_for_character_card_import() -> str | None:
    """
    Prompts the user to import a character card and returns the converted premise.
    
    Returns:
        str: Converted premise, or None if import is cancelled or fails
    """
    console.print("\n[bold cyan]Import Character Card[/bold cyan]")
    console.print("[dim]Supports TavernAI/SillyTavern character cards (JSON or PNG format)[/dim]")
    
    if not Confirm.ask("\n[yellow]Would you like to import a character card?[/yellow]", default=False):
        return None
    
    file_path = Prompt.ask(
        "[cyan]Enter path to character card file (.json or .png)[/cyan]",
        default=""
    ).strip()
    
    if not file_path:
        return None
    
    from pathlib import Path
    path = Path(file_path)
    
    if not path.exists():
        console.print(f"[red]Error: File not found: {file_path}[/red]")
        return None
    
    # Try to load the character card
    from src.utils import load_character_card, convert_character_card_to_premise
    
    console.print("[cyan]Loading character card...[/cyan]")
    character_data = load_character_card(str(path))
    
    if not character_data:
        console.print("[red]Error: Failed to load character card. The file may be corrupted or in an unsupported format.[/red]")
        return None
    
    # Convert to premise
    console.print("[cyan]Converting character card to story premise...[/cyan]")
    premise = convert_character_card_to_premise(character_data)
    
    # Display preview
    console.print(Panel(
        premise[:500] + ("..." if len(premise) > 500 else ""),
        title="[bold green]Character Card Converted to Premise[/bold green]",
        border_style="green"
    ))
    
    if Confirm.ask("\n[yellow]Use this character card as the story premise?[/yellow]", default=True):
        return premise
    
    return None
