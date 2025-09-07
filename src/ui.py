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
