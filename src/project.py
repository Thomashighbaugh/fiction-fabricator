# -*- coding: utf-8 -*-
"""
project.py - Manages the state of a novel project, including loading, saving, and patching.
"""
import xml.etree.ElementTree as ET
import uuid
import copy
from pathlib import Path
from datetime import datetime

from rich.console import Console

from src import utils
from src.config import DATE_FORMAT_FOR_FOLDER

class Project:
    """Manages the entire state of a single writing project."""

    def __init__(self, console: Console, resume_folder_name: str | None = None):
        self.console = console
        self.book_root: ET.Element | None = None
        self.book_dir: Path | None = None
        self.book_id: str = ""
        self.book_title_slug: str = "untitled"
        self.chapters_generated_in_session: set = set()

        if resume_folder_name:
            self.console.print(f"Resuming project from: [cyan]{resume_folder_name}[/cyan]")
            self.book_dir = Path(resume_folder_name)
            if not self.book_dir.is_dir():
                raise FileNotFoundError(f"Project directory '{resume_folder_name}' not found.")
            
            # Parse folder name: YYYYMMDD-slug-uuid
            parts = self.book_dir.name.split("-", 2)
            if len(parts) >= 3:
                self.book_title_slug = parts[1]
                self.book_id = "-".join(parts[2:]) # Handle UUIDs with hyphens
            else:
                self.book_id = self.book_dir.name # Fallback
            
            self._load_state()
        else:
            self.console.print("Starting a new project.")
            # Directory and initial files will be created by setup_new_project
    
    def setup_new_project(self, idea: str, title: str, synopsis: str):
        """Initializes the structure for a new project."""
        self.book_id = str(uuid.uuid4())[:8]
        self.book_title_slug = utils.slugify(title)
        
        today_date_str = datetime.now().strftime(DATE_FORMAT_FOR_FOLDER)
        folder_name = f"{today_date_str}-{self.book_title_slug}-{self.book_id}"
        self.book_dir = Path(folder_name)

        try:
            self.book_dir.mkdir(parents=True, exist_ok=True)
            self.console.print(f"Created project directory: [cyan]{self.book_dir.resolve()}[/cyan]")
        except OSError as e:
            self.console.print(f"[bold red]Error creating directory {self.book_dir}: {e}[/bold red]")
            raise

        self.book_root = ET.Element("book")
        ET.SubElement(self.book_root, "title").text = title
        ET.SubElement(self.book_root, "synopsis").text = synopsis
        ET.SubElement(self.book_root, "initial_idea").text = idea
        
        # Add story elements section
        story_elements = ET.SubElement(self.book_root, "story_elements")
        ET.SubElement(story_elements, "genre").text = ""
        ET.SubElement(story_elements, "tone").text = ""
        ET.SubElement(story_elements, "perspective").text = ""
        ET.SubElement(story_elements, "target_audience").text = ""
        
        ET.SubElement(self.book_root, "characters")
        ET.SubElement(self.book_root, "chapters")

        self.save_state("outline.xml")

    def _load_state(self):
        """Loads the latest project state from XML files in the project directory."""
        if not self.book_dir:
            raise ValueError("Book directory not set.")
        
        outline_file = self.book_dir / "outline.xml"
        if not outline_file.exists():
            raise FileNotFoundError(f"Required outline.xml not found in '{self.book_dir}'")

        try:
            tree = ET.parse(outline_file)
            self.book_root = tree.getroot()
            self.console.print(f"Loaded base state from: [cyan]outline.xml[/cyan]")
        except ET.ParseError as e:
            self.console.print(f"[bold red]Error parsing outline.xml: {e}[/bold red]")
            raise
        
        # Apply patches in order
        patch_files = sorted(
            [p for p in self.book_dir.glob("patch-*.xml") if p.stem.split("-")[-1].isdigit()],
            key=lambda p: int(p.stem.split("-")[-1]),
        )

        if patch_files:
            self.console.print(f"Found {len(patch_files)} patch file(s). Applying...")
            for patch_file in patch_files:
                try:
                    patch_xml_str = patch_file.read_text(encoding="utf-8")
                    if not self.apply_patch(patch_xml_str, is_loading=True):
                        self.console.print(f"[yellow]Warning: Could not apply patch {patch_file.name}. State may be inconsistent.[/yellow]")
                except Exception as e:
                    self.console.print(f"[bold red]Error applying patch {patch_file.name}: {e}[/bold red]")
            self.console.print("[green]All patches applied.[/green]")

    def save_state(self, filename: str) -> bool:
        """Saves the current book_root to a specified XML file."""
        if self.book_root is None or self.book_dir is None:
            self.console.print("[bold red]Error: Cannot save state, project not fully initialized.[/bold red]")
            return False
        
        filepath = self.book_dir / filename
        try:
            xml_str = utils.pretty_xml(self.book_root)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(xml_str)
            self.console.print(f"[green]Project state saved to:[/green] [cyan]{filepath.name}[/cyan]")
            return True
        except Exception as e:
            self.console.print(f"[bold red]Error saving project state to {filepath}: {e}[/bold red]")
            return False

    def apply_patch(self, patch_xml_str: str, is_loading: bool = False) -> bool:
        """Applies a patch XML string to the current book_root."""
        patch_root = utils.parse_xml_string(patch_xml_str, self.console, expected_root_tag="patch")
        if patch_root is None or patch_root.tag != "patch":
            self.console.print("[bold red]Error: Invalid patch XML. Cannot apply.[/bold red]")
            return False

        applied_changes = False
        try:
            # Apply chapter patches
            for chapter_patch in patch_root.findall("chapter"):
                # Handle both attribute and child element ID formats
                chapter_id = chapter_patch.get("id") or chapter_patch.findtext("id")
                target_chapter = self.find_chapter(chapter_id)
                if not chapter_id or target_chapter is None:
                    continue

                new_content = chapter_patch.find("content")
                if new_content is not None:
                    # Clean paragraph text to remove unwanted line breaks
                    for paragraph in new_content.findall("paragraph"):
                        if paragraph.text:
                            paragraph.text = utils.clean_paragraph_text(paragraph.text)
                    
                    old_content = target_chapter.find("content")
                    if old_content is not None:
                        target_chapter.remove(old_content)
                    target_chapter.append(copy.deepcopy(new_content))
                    if not is_loading:
                        self.console.print(f"[green]Applied full content patch to Chapter {chapter_id}.[/green]")
                        self.chapters_generated_in_session.add(chapter_id)
                    applied_changes = True

            # Apply top-level element patches (title, synopsis, characters, story_elements)
            for element_patch in patch_root:
                if element_patch.tag not in ["title", "synopsis", "characters", "story_elements"]:
                    continue
                
                target_element = self.book_root.find(element_patch.tag)
                if target_element is not None:
                    self.book_root.remove(target_element)
                
                self.book_root.append(copy.deepcopy(element_patch))
                if not is_loading:
                    self.console.print(f"[green]Applied patch for <{element_patch.tag}>.[/green]")
                applied_changes = True

        except Exception as e:
            self.console.print(f"[bold red]Error while applying patch: {e}[/bold red]")
            self.console.print_exception(show_locals=False)
            return False

        if not applied_changes and not is_loading:
            self.console.print("[yellow]Patch processed, but no applicable changes were found.[/yellow]")

        return applied_changes

    def find_chapter(self, chapter_id: str) -> ET.Element | None:
        """Finds a chapter element by its 'id' attribute or child element."""
        if self.book_root is None:
            return None
        # Try attribute-based ID first
        chapter = self.book_root.find(f".//chapter[@id='{chapter_id}']")
        if chapter is not None:
            return chapter
        # Try child element-based ID
        for chapter in self.book_root.findall(".//chapter"):
            if chapter.findtext("id") == chapter_id:
                return chapter
        return None
