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
            
            # Check if it's a direct path or just a folder name
            resume_path = Path(resume_folder_name)
            if resume_path.is_dir():
                # Direct path provided
                self.book_dir = resume_path
            else:
                # Look in projects directory
                projects_dir = Path("projects")
                potential_path = projects_dir / resume_folder_name
                if potential_path.is_dir():
                    self.book_dir = potential_path
                else:
                    # Fallback to original behavior for backward compatibility
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
        
        # Ensure projects directory exists
        projects_dir = Path("projects")
        projects_dir.mkdir(exist_ok=True)
        
        self.book_dir = projects_dir / folder_name

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
        
        # Add frontmatter section
        frontmatter = ET.SubElement(self.book_root, "frontmatter")
        ET.SubElement(frontmatter, "author").text = ""
        ET.SubElement(frontmatter, "title_page").text = ""
        ET.SubElement(frontmatter, "copyright_page").text = ""
        ET.SubElement(frontmatter, "dedication").text = ""
        ET.SubElement(frontmatter, "acknowledgements").text = ""
        
        ET.SubElement(self.book_root, "chapters")

        self.save_state("outline.xml")

    def _load_state(self):
        """Loads the latest project state from XML files in the project directory."""
        if not self.book_dir:
            raise ValueError("Book directory not set.")
        
        outline_file = self.book_dir / "outline.xml"
        if not outline_file.exists():
            raise FileNotFoundError(f"Required outline.xml not found in '{self.book_dir}'")

        # Find all patch files and get the latest one (highest number)
        patch_files = sorted(
            [p for p in self.book_dir.glob("patch-*.xml") if p.stem.split("-")[-1].isdigit()],
            key=lambda p: int(p.stem.split("-")[-1]),
        )
        
        if patch_files:
            # Load from the latest patch file (which contains the complete state)
            latest_patch = patch_files[-1]
            try:
                tree = ET.parse(latest_patch)
                self.book_root = tree.getroot()
                self.console.print(f"Loaded project state from: [cyan]{latest_patch.name}[/cyan]")
            except ET.ParseError as e:
                self.console.print(f"[bold red]Error parsing {latest_patch.name}: {e}[/bold red]")
                raise
        else:
            # No patch files, load from outline.xml
            try:
                tree = ET.parse(outline_file)
                self.book_root = tree.getroot()
                self.console.print(f"Loaded base state from: [cyan]outline.xml[/cyan]")
            except ET.ParseError as e:
                self.console.print(f"[bold red]Error parsing outline.xml: {e}[/bold red]")
                raise
        
        # Restore chapters_generated_in_session based on chapters with content
        self._restore_generated_chapters_set()

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
            if not is_loading:
                self.console.print("[bold red]Error: Invalid patch XML. Cannot apply.[/bold red]")
            return False

        applied_changes = False
        try:
            # Apply chapter patches
            for chapter_patch in patch_root.findall("chapter"):
                # Handle both attribute and child element ID formats
                chapter_id = chapter_patch.get("id") or chapter_patch.findtext("id")
                if not chapter_id:
                    if not is_loading:
                        self.console.print("[yellow]Warning: Chapter patch missing ID, skipping.[/yellow]")
                    continue
                
                target_chapter = self.find_chapter(chapter_id)
                if target_chapter is None:
                    if not is_loading:
                        self.console.print(f"[yellow]Warning: Chapter {chapter_id} not found in book structure, skipping patch.[/yellow]")
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
                
                if self.book_root is not None:
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

    def find_chapter(self, chapter_id: str | None) -> ET.Element | None:
        """Finds a chapter element by its 'id' attribute or child element."""
        if self.book_root is None or not chapter_id:
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

    def debug_patch_failure(self, patch_xml_str: str):
        """Debug helper to understand why patches fail during project resume."""
        self.console.print("[bold yellow]Debugging patch failure...[/bold yellow]")
        
        # Show current book structure
        if self.book_root is not None:
            chapters = self.book_root.findall(".//chapter")
            self.console.print(f"[cyan]Current book has {len(chapters)} chapters:[/cyan]")
            for chapter in chapters:
                chapter_id = chapter.get("id") or chapter.findtext("id")
                self.console.print(f"  - Chapter ID: {chapter_id}")
        
        # Parse and show patch structure
        try:
            patch_root = utils.parse_xml_string(patch_xml_str, self.console, expected_root_tag="patch")
            if patch_root is not None:
                patch_chapters = patch_root.findall("chapter")
                self.console.print(f"[cyan]Patch contains {len(patch_chapters)} chapters:[/cyan]")
                for chapter_patch in patch_chapters:
                    chapter_id = chapter_patch.get("id") or chapter_patch.findtext("id")
                    self.console.print(f"  - Patch for Chapter ID: {chapter_id}")
        except Exception as e:
            self.console.print(f"[red]Error parsing patch: {e}[/red]")

    def _restore_generated_chapters_set(self):
        """Restores the chapters_generated_in_session set based on chapters with content."""
        if not self.book_root:
            return
        
        chapters_with_content = []
        all_chapters = self.book_root.findall(".//chapter")
        
        for chapter in all_chapters:
            # Check if chapter has content with paragraphs that contain text
            content_elem = chapter.find("content")
            if content_elem is not None:
                paragraphs = content_elem.findall("paragraph")
                has_text_content = any(p.text and p.text.strip() for p in paragraphs)
                
                if has_text_content:
                    chapter_id = chapter.get("id") or chapter.findtext("id")
                    if chapter_id:
                        self.chapters_generated_in_session.add(chapter_id)
                        chapters_with_content.append(chapter_id)
        
        if chapters_with_content:
            self.console.print(f"[green]Restored {len(chapters_with_content)} chapters with existing content.[/green]")
        else:
            self.console.print("[dim]No chapters with content found to restore.[/dim]")

    def edit_frontmatter_section(self, section_name: str) -> bool:
        """
        Edit a frontmatter section using the user's preferred editor.
        
        Args:
            section_name: One of 'author', 'title_page', 'copyright_page', 'dedication', 'acknowledgements'
        
        Returns:
            bool: True if the section was edited successfully, False otherwise
        """
        import os
        import tempfile
        import subprocess
        
        if not self.book_root:
            self.console.print("[bold red]Error: No book loaded.[/bold red]")
            return False
        
        # Ensure frontmatter section exists
        frontmatter = self.book_root.find("frontmatter")
        if frontmatter is None:
            frontmatter = ET.SubElement(self.book_root, "frontmatter")
            ET.SubElement(frontmatter, "author").text = ""
            ET.SubElement(frontmatter, "title_page").text = ""
            ET.SubElement(frontmatter, "copyright_page").text = ""
            ET.SubElement(frontmatter, "dedication").text = ""
            ET.SubElement(frontmatter, "acknowledgements").text = ""
        
        section_element = frontmatter.find(section_name)
        if section_element is None:
            section_element = ET.SubElement(frontmatter, section_name)
            section_element.text = ""
        
        # Get current content
        current_content = section_element.text or ""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(current_content)
            temp_file_path = temp_file.name
        
        try:
            # Get editor from environment, default to nano
            editor = os.environ.get('EDITOR', 'nano')
            
            self.console.print(f"[yellow]Opening {section_name.replace('_', ' ')} in {editor}...[/yellow]")
            self.console.print("[dim]Save and exit the editor when finished.[/dim]")
            
            # Launch editor
            result = subprocess.run([editor, temp_file_path])
            
            if result.returncode == 0:
                # Read the updated content
                with open(temp_file_path, 'r') as temp_file:
                    updated_content = temp_file.read().strip()
                
                # Update the XML element
                section_element.text = updated_content
                
                # Save the changes
                if self.book_dir:
                    patch_num = utils.get_next_patch_number(self.book_dir)
                    self.save_state(f"patch-{patch_num:02d}.xml")
                    self.console.print(f"[green]✓ {section_name.replace('_', ' ')} updated successfully.[/green]")
                    return True
            else:
                self.console.print(f"[red]Editor exited with error code {result.returncode}[/red]")
                return False
                
        except Exception as e:
            self.console.print(f"[bold red]Error editing {section_name}: {e}[/bold red]")
            return False
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass
        
        return False

    def edit_book_title(self) -> bool:
        """Edit the book title using interactive prompt."""
        from rich.prompt import Prompt
        
        if not self.book_root:
            self.console.print("[bold red]Error: No book loaded.[/bold red]")
            return False
        
        # Get current title
        current_title = self.book_root.findtext("title", "")
        
        # Prompt for new title
        new_title = Prompt.ask(
            "[cyan]Enter new book title[/cyan]",
            default=current_title
        ).strip()
        
        if new_title and new_title != current_title:
            # Update the title
            title_elem = self.book_root.find("title")
            if title_elem is None:
                title_elem = ET.SubElement(self.book_root, "title")
            title_elem.text = new_title
            
            self.console.print(f"[green]✓ Book title updated to: {new_title}[/green]")
            return True
        else:
            self.console.print("[dim]Title unchanged.[/dim]")
            return False

    def edit_author_name(self) -> bool:
        """Edit the author name using interactive prompt."""
        from rich.prompt import Prompt
        
        if not self.book_root:
            self.console.print("[bold red]Error: No book loaded.[/bold red]")
            return False
        
        # Ensure frontmatter section exists
        frontmatter = self.book_root.find("frontmatter")
        if frontmatter is None:
            frontmatter = ET.SubElement(self.book_root, "frontmatter")
            ET.SubElement(frontmatter, "author").text = ""
            ET.SubElement(frontmatter, "title_page").text = ""
            ET.SubElement(frontmatter, "copyright_page").text = ""
            ET.SubElement(frontmatter, "dedication").text = ""
            ET.SubElement(frontmatter, "acknowledgements").text = ""
        
        # Get current author
        author_elem = frontmatter.find("author")
        if author_elem is None:
            author_elem = ET.SubElement(frontmatter, "author")
            author_elem.text = ""
        current_author = author_elem.text or ""
        
        # Prompt for new author name
        new_author = Prompt.ask(
            "[cyan]Enter author name[/cyan]",
            default=current_author
        ).strip()
        
        if new_author != current_author:
            author_elem.text = new_author
            self.console.print(f"[green]✓ Author name updated to: {new_author}[/green]")
            return True
        else:
            self.console.print("[dim]Author name unchanged.[/dim]")
            return False
