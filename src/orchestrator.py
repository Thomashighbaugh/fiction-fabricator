# -*- coding: utf-8 -*-
"""
orchestrator.py - The main workflow controller for the Fiction Fabricator application.
"""
import xml.etree.ElementTree as ET
import json
import re
import copy
from html import escape
from pathlib import Path

from rich.prompt import Confirm
from rich.panel import Panel

from src import ui, utils
from src.llm_client import LLMClient
from src.project import Project
from src.generators import novel, short_story
from src.exporters import markdown, epub, html

class Orchestrator:
    """Orchestrates the entire novel generation process."""

    def __init__(self, project: Project, llm_client: LLMClient, lorebook_path: str | None = None):
        self.project = project
        self.llm = llm_client
        self.console = ui.console
        self.lorebook_data = self._load_lorebook(lorebook_path) if lorebook_path else None

    def _load_lorebook(self, lorebook_path: str) -> dict | None:
        """Loads and parses a Tavern AI format lorebook JSON file."""
        try:
            path = Path(lorebook_path)
            if not path.exists():
                self.console.print(f"[yellow]Warning: Lorebook file not found at {path}[/yellow]")
                return None
            
            with open(path, 'r', encoding='utf-8') as f:
                lorebook_data = json.load(f)
            
            self.console.print(f"[green]Loaded lorebook: {path.name}[/green]")
            return lorebook_data
            
        except (json.JSONDecodeError, IOError) as e:
            self.console.print(f"[red]Error loading lorebook: {e}[/red]")
            return None

    def _extract_lorebook_context(self, text: str) -> str:
        """Extracts relevant lorebook entries based on keywords found in the text."""
        if not self.lorebook_data:
            return ""
        
        # Extract entries from lorebook structure
        entries = []
        if "entries" in self.lorebook_data:
            entries = self.lorebook_data["entries"]
        elif isinstance(self.lorebook_data, list):
            entries = self.lorebook_data
        elif "worldInfos" in self.lorebook_data:
            entries = self.lorebook_data["worldInfos"]
        
        if not entries:
            return ""
        
        relevant_entries = []
        text_lower = text.lower()
        
        for entry in entries:
            # Skip disabled entries
            if entry.get("disable", False) or not entry.get("enable", True):
                continue
            
            # Check for keywords (keys field)
            keys = entry.get("keys", [])
            if isinstance(keys, str):
                keys = [k.strip() for k in keys.split(",")]
            
            # Check if any keyword matches
            matches = any(key.lower() in text_lower for key in keys if key.strip())
            
            if matches:
                content = entry.get("content", "").strip()
                if content:
                    relevant_entries.append({
                        "title": entry.get("comment", entry.get("title", "Entry")),
                        "content": content
                    })
        
        if not relevant_entries:
            return ""
        
        # Format the lorebook context
        context_parts = ["## Lorebook Context\n"]
        for entry in relevant_entries:
            context_parts.append(f"**{entry['title']}:**\n{entry['content']}\n")
        
        return "\n".join(context_parts)

    def run(self):
        """The main execution flow of the application."""
        # Step 1: Outline Generation
        if not self._has_full_outline():
            self.console.print("[yellow]Outline is incomplete. Running outline generation.[/yellow]")
            if not self.run_outline_generation():
                self.console.print("[bold red]Outline generation failed. Cannot proceed.[/bold red]")
                return
        else:
            self.console.print("[green]Existing full outline loaded.[/green]")
            ui.display_summary(self.project)
            if Confirm.ask("[yellow]Regenerate outline? (This replaces existing structure)[/yellow]", default=False):
                if not self.run_outline_generation():
                    self.console.print("[bold red]Outline re-generation failed.[/bold red]")

        # Step 2: Content Generation
        if Confirm.ask("\n[yellow]Proceed to Chapter/Scene Content Generation?[/yellow]", default=True):
            self.run_content_generation()

        # Step 3: Editing
        if Confirm.ask("\n[yellow]Content generation complete. Proceed to Editing?[/yellow]", default=True):
            self.run_editing_loop()

        self.console.print(Panel("[bold green]📚 Fiction Fabricator session finished. 📚[/bold green]"))

    def setup_new_project(self, idea: str):
        """Guides the user through setting up a new project."""
        # 1. Get initial title and synopsis
        title, synopsis = self._generate_initial_summary(idea)
        if not title or not synopsis:
            self.console.print("[bold red]Could not generate initial title and synopsis. Exiting.[/bold red]")
            return False

        # 2. Initialize the project state
        self.project.setup_new_project(idea, title, synopsis)

        # 3. Ask for story type
        self.project.story_type = ui.prompt_for_story_type()
        return True

    def _generate_initial_summary(self, idea: str) -> tuple[str | None, str | None]:
        """Generates a title and synopsis from the user's initial idea."""
        self.console.print("[cyan]Generating initial title and synopsis...[/cyan]")
        
        # Add lorebook context if available
        lorebook_context = self._extract_lorebook_context(idea)
        
        prompt = f"""
Based on the following idea, generate a compelling title and a brief 1-2 sentence synopsis.

Idea:
---
{idea}
---

{lorebook_context}

Output ONLY a JSON object in the format:
{{
  "title": "Your Generated Title",
  "synopsis": "Your generated synopsis."
}}
"""
        response_json_str = self.llm.get_response(prompt, "Generating Title/Synopsis", allow_stream=False)
        if not response_json_str:
            return None, None
        
        try:
            cleaned_json_str = re.sub(r"^```json\s*|\s*```$", "", response_json_str.strip(), flags=re.IGNORECASE | re.MULTILINE)
            data = json.loads(cleaned_json_str)
            return data.get("title"), data.get("synopsis")
        except (json.JSONDecodeError, AttributeError):
            self.console.print("[yellow]Warning: Could not parse title/synopsis JSON from LLM.[/yellow]")
            return "Untitled Project", "Synopsis pending."

    def _has_full_outline(self) -> bool:
        """Checks if the project appears to have a complete outline."""
        if not self.project.book_root:
            return False
        
        chapters = self.project.book_root.findall(".//chapter")
        characters = self.project.book_root.findall(".//character")
        has_summaries = any(c.findtext("summary", "").strip() for c in chapters)

        return bool(chapters and characters and has_summaries)

    def run_outline_generation(self) -> bool:
        """Executes the outline generation step."""
        generator = novel if getattr(self.project, 'story_type', 'novel') == 'novel' else short_story
        
        # Extract lorebook context from the initial idea
        initial_idea = ""
        if self.project.book_root is not None:
            initial_idea_elem = self.project.book_root.find("initial_idea")
            if initial_idea_elem is not None:
                initial_idea = initial_idea_elem.text or ""
        
        lorebook_context = self._extract_lorebook_context(initial_idea)
        
        response_xml_str = generator.generate_outline(self.llm, self.project, lorebook_context)
        if not response_xml_str:
            return False
        
        new_book_root = utils.parse_xml_string(response_xml_str, self.console, expected_root_tag="book")
        if new_book_root is None or new_book_root.tag != "book":
            self.console.print("[bold red]Failed to parse generated outline or root tag was not <book>.[/bold red]")
            return False
        
        # Simple validation and replacement
        self.project.book_root = new_book_root
        if self.project.save_state("outline.xml"):
            self.console.print("[green]Full outline generated and saved as outline.xml[/green]")
            ui.display_summary(self.project)
            return True
        return False
        
    def run_content_generation(self):
        """Generates content for batches of chapters/scenes."""
        self.console.print(Panel("Generating Chapter/Scene Content", style="bold blue"))
        self.project.chapters_generated_in_session.clear()

        while True:
            chapters_to_generate = self._select_chapters_to_generate(batch_size=5)
            if not chapters_to_generate:
                self.console.print("[bold green]\nAll chapters/scenes appear to have content![/bold green]")
                break

            ids_str = ", ".join([utils.get_chapter_id_with_default(c) for c in chapters_to_generate])

            chapter_details = "".join(f'- Chapter {c.findtext("number", "N/A")} (ID: {utils.get_chapter_id(c)}): "{c.findtext("title", "N/A")}"\n  Summary: {c.findtext("summary", "N/A")}\n' for c in chapters_to_generate)
            
            # Extract lorebook context from chapter summaries and titles
            context_text = " ".join([c.findtext("title", "") + " " + c.findtext("summary", "") for c in chapters_to_generate])
            lorebook_context = self._extract_lorebook_context(context_text)
            
            prompt = f"""
You are a novelist continuing a story. Write the full prose for the following {len(chapters_to_generate)} chapters/scenes based on their summaries and the full book context.
Aim for substantial, detailed chapters (3000-6000 words per chapter).

Chapters/Scenes to write:
{chapter_details}

{lorebook_context}

Output ONLY an XML `<patch>` containing a `<chapter>` for each requested ID. Each chapter must have a `<content>` tag filled with sequentially ID'd `<paragraph>` tags.

Full Book Context:
```xml
{ET.tostring(self.project.book_root, encoding='unicode')}
```
"""
            patch_xml = self.llm.get_response(prompt, f"Writing chapters {ids_str}")
            if patch_xml and self.project.apply_patch(patch_xml):
                patch_num = utils.get_next_patch_number(self.project.book_dir)
                self.project.save_state(f"patch-{patch_num:02d}.xml")
                ui.display_summary(self.project)
            else:
                self.console.print(f"[bold red]Failed to apply patch for batch {ids_str}.[/bold red]")
                if not Confirm.ask("[yellow]Continue to the next batch?[/yellow]", default=True):
                    break
    
    def _select_chapters_to_generate(self, batch_size=5) -> list:
        """Selects the next batch of chapters to write using a fill-gaps strategy."""
        all_chapters = sorted(self.project.book_root.findall(".//chapter"), key=lambda c: int(utils.get_chapter_id_with_default(c, "0")))
        
        chapters_needing_content = []
        for chap in all_chapters:
            paras = chap.findall(".//paragraph")
            if not any(p.text and p.text.strip() for p in paras):
                chapters_needing_content.append(chap)
        
        return chapters_needing_content[:batch_size]

    def run_editing_loop(self):
        """Runs the interactive editing menu loop."""
        self.console.print(Panel("Interactive Editing Mode", style="bold blue"))
        
        edit_options = {
            "1": ("Make Chapter(s) Longer", self._edit_make_longer),
            "2": ("Rewrite Chapter (with instructions)", lambda: self._edit_rewrite_chapter(blackout=False)),
            "3": ("Rewrite Chapter (Fresh Rewrite)", lambda: self._edit_rewrite_chapter(blackout=True)),
            "4": ("Ask LLM for Edit Suggestions", self._edit_suggest_edits),
            "5": ("Export Menu", self._show_export_menu),
            "6": ("Quit Editing", None),
        }

        while True:
            ui.display_summary(self.project)
            choice = ui.display_menu("Editing Options", edit_options)
            
            handler = edit_options.get(choice)[1]
            if handler:
                handler()
            else: # Quit
                break
    
    def _handle_patch_result(self, patch_xml: str | None, operation_desc: str):
        """Helper to apply, save, and report the result of an edit operation."""
        if not patch_xml:
            self.console.print(f"[red]{operation_desc} failed: No patch generated by LLM.[/red]")
            return

        ui.display_patch_suggestion(patch_xml)
        if Confirm.ask("\n[yellow]Apply this suggested patch?[/yellow]", default=True):
            if self.project.apply_patch(patch_xml):
                patch_num = utils.get_next_patch_number(self.project.book_dir)
                self.project.save_state(f"patch-{patch_num:02d}.xml")
                self.console.print(f"[green]{operation_desc} successful. Patch saved.[/green]")
            else:
                self.console.print(f"[red]{operation_desc} failed to apply.[/red]")
        else:
            self.console.print("Patch discarded.")
    
    def _handle_patch_result_auto(self, patch_xml: str | None, operation_desc: str):
        """Helper to automatically apply patches without confirmation (for bulk operations)."""
        if not patch_xml:
            self.console.print(f"[red]{operation_desc} failed: No patch generated by LLM.[/red]")
            return

        if self.project.apply_patch(patch_xml):
            patch_num = utils.get_next_patch_number(self.project.book_dir)
            self.project.save_state(f"patch-{patch_num:02d}.xml")
            self.console.print(f"[green]{operation_desc} successful. Patch auto-applied.[/green]")
        else:
            self.console.print(f"[red]{operation_desc} failed to apply.[/red]")
    
    def _create_reduced_context_for_chapter(self, chapter_id: str) -> str:
        """Creates a reduced book context focused on the target chapter and surrounding chapters."""
        if not self.project.book_root:
            return "<book></book>"
        
        # Create a minimal book structure
        reduced_book = ET.Element("book")
        
        # Add essential book metadata
        for elem_name in ["title", "synopsis", "story_elements"]:
            elem = self.project.book_root.find(elem_name)
            if elem is not None:
                reduced_book.append(copy.deepcopy(elem))
        
        # Add character information (summarized)
        characters_elem = self.project.book_root.find("characters")
        if characters_elem is not None:
            reduced_chars = ET.SubElement(reduced_book, "characters")
            for char in characters_elem.findall("character"):
                char_copy = ET.SubElement(reduced_chars, "character")
                # Only include essential character info, not full descriptions
                for attr in ["name", "role", "description"]:
                    char_attr = char.find(attr)
                    if char_attr is not None:
                        attr_copy = ET.SubElement(char_copy, attr)
                        # Truncate long descriptions to save tokens
                        text = char_attr.text or ""
                        attr_copy.text = text[:200] + "..." if len(text) > 200 else text
        
        # Find target chapter and surrounding chapters
        all_chapters = self.project.book_root.findall(".//chapter")
        target_chapter = None
        target_index = -1
        
        for i, chapter in enumerate(all_chapters):
            if utils.get_chapter_id(chapter) == chapter_id:
                target_chapter = chapter
                target_index = i
                break
        
        if target_chapter is None:
            return ET.tostring(reduced_book, encoding='unicode')
        
        # Add chapters section with target + surrounding chapters
        chapters_elem = ET.SubElement(reduced_book, "chapters")
        
        # Include previous chapter (summary only), target chapter (full), and next chapter (summary only)
        for i in range(max(0, target_index - 1), min(len(all_chapters), target_index + 2)):
            chapter = all_chapters[i]
            chapter_copy = ET.SubElement(chapters_elem, "chapter")
            
            # Copy chapter metadata
            if chapter.get("id"):
                chapter_copy.set("id", chapter.get("id"))
            
            for elem_name in ["id", "number", "title", "summary"]:
                elem = chapter.find(elem_name)
                if elem is not None:
                    elem_copy = ET.SubElement(chapter_copy, elem_name)
                    elem_copy.text = elem.text
            
            # For the target chapter, include full content; for others, just summary
            if utils.get_chapter_id(chapter) == chapter_id:
                content_elem = chapter.find("content")
                if content_elem is not None:
                    chapter_copy.append(copy.deepcopy(content_elem))
        
        return ET.tostring(reduced_book, encoding='unicode')

    def _edit_make_longer(self):
        """Handler for making chapters longer."""
        chapters = ui.get_chapter_selection(self.project, "Enter chapter ID(s) to make longer", allow_multiple=True)
        if not chapters: 
            return

        word_count = ui.IntPrompt.ask("[yellow]Enter target word count per chapter[/yellow]", default=4500)
        
        # For multiple chapters, notify user that patches will be auto-applied
        if len(chapters) > 1:
            self.console.print(f"[yellow]Auto-applying patches for {len(chapters)} chapters (no confirmations)...[/yellow]")
        
        # Process each chapter individually to ensure all get expanded
        for chapter in chapters:
            chapter_id = utils.get_chapter_id(chapter)
            self.console.print(f"[cyan]Expanding Chapter {chapter_id}...[/cyan]")
            
            # Create reduced context to avoid token limits
            reduced_context = self._create_reduced_context_for_chapter(chapter_id)
            
            prompt = f"""
Expand the existing content for chapter {chapter_id} to approximately {word_count} words by building upon what's already written.

**IMPORTANT**: Do not rewrite or replace existing content. Instead, expand it by:
- Adding more descriptive detail to existing scenes
- Expanding dialogue with additional exchanges and character reactions  
- Including internal thoughts and emotions of characters
- Adding sensory details (sight, sound, smell, touch, taste)
- Developing existing scenes with more depth and pacing
- Adding transitional moments between existing plot points
- Enhancing character interactions and relationships

Maintain the original narrative flow, character voices, and plot progression. The expanded content should feel like a natural extension of what's already there, not a replacement.

Output an XML `<patch>` with the expanded `<chapter>` content that preserves all key story elements while making them richer and more detailed.

Relevant Context:
```xml
{reduced_context}
```
"""
            patch_xml = self.llm.get_response(prompt, f"Expanding chapter {chapter_id}")
            if len(chapters) > 1:
                self._handle_patch_result_auto(patch_xml, f"Make Longer (Ch {chapter_id})")
            else:
                self._handle_patch_result(patch_xml, f"Make Longer (Ch {chapter_id})")

    def _edit_rewrite_chapter(self, blackout: bool):
        """Handler for rewriting a chapter."""
        chapter = ui.get_chapter_selection(self.project, "Enter the chapter ID to rewrite", allow_multiple=False)
        if not chapter: return
        target_chapter = chapter[0]
        chapter_id = utils.get_chapter_id(target_chapter)

        instructions = ui.Prompt.ask("[yellow]Enter specific instructions for the rewrite[/yellow]")
        if not instructions.strip(): return

        temp_root = self.project.book_root
        if blackout:
            temp_root = copy.deepcopy(self.project.book_root)
            content_to_clear = temp_root.find(f".//chapter[@id='{chapter_id}']/content")
            if content_to_clear is not None:
                content_to_clear.clear()

        prompt = f"""
Rewrite the entire content for Chapter {chapter_id} based on these instructions:
"{escape(instructions)}"
{"The original content has been omitted from the context to encourage a fresh take." if blackout else ""}
Ensure the new content respects the chapter's summary and the overall plot.
Output an XML `<patch>` with the rewritten `<chapter>` content.

Full Book Context:
```xml
{ET.tostring(temp_root, encoding='unicode')}
```
"""
        patch_xml = self.llm.get_response(prompt, f"Rewriting chapter {chapter_id}")
        self._handle_patch_result(patch_xml, f"Rewrite (Ch {chapter_id})")

    def _edit_suggest_edits(self):
        """Handler for asking the LLM for edit suggestions."""
        prompt = f"""
You are an expert editor. Analyze the manuscript below and provide a numbered list of 5-10 concrete, actionable suggestions for improvement.

Full Book Context:
```xml
{ET.tostring(self.project.book_root, encoding='unicode')}
```
"""
        suggestions_text = self.llm.get_response(prompt, "Generating edit suggestions", allow_stream=False)
        if not suggestions_text: return
        
        self.console.print(Panel(suggestions_text, title="LLM Edit Suggestions", border_style="cyan"))
        # This feature is simplified in the refactor. A full implementation would parse the list
        # and let the user pick one to generate a patch for, as in the original code.
        self.console.print("\n[yellow]Use the 'Rewrite Chapter' option to implement these suggestions.[/yellow]")


    def _show_export_menu(self):
        """Displays the export menu and handles user choice."""
        export_options = {
            "1": ("Export Full Book (Single Markdown)", self._export_single_md),
            "2": ("Export Chapters (Markdown per Chapter)", self._export_multi_md),
            "3": ("Export Full Book (Single HTML)", self._export_single_html),
            "4": ("Export Chapters (HTML per Chapter)", self._export_multi_html),
            "5": ("Export Full Book (EPUB)", self._export_epub),
            "6": ("Return to Editing Menu", None),
        }
        choice = ui.display_menu("Export Options", export_options)
        handler = export_options.get(choice)[1]
        if handler:
            handler()

    def _export_single_md(self):
        filename = f"{self.project.book_title_slug}-full.md"
        output_path = self.project.book_dir / filename
        markdown.export_single_markdown(self.project.book_root, output_path, self.console)

    def _export_multi_md(self):
        markdown.export_markdown_per_chapter(self.project.book_root, self.project.book_dir, self.project.book_title_slug, self.console)

    def _export_single_html(self):
        filename = f"{self.project.book_title_slug}-full.html"
        output_path = self.project.book_dir / filename
        html.export_single_html(self.project.book_root, output_path, self.console)

    def _export_multi_html(self):
        html.export_html_per_chapter(self.project.book_root, self.project.book_dir, self.project.book_title_slug, self.console)

    def _export_epub(self):
        # Prompt for optional cover image
        from rich.prompt import Prompt
        from pathlib import Path
        
        cover_path_str = Prompt.ask(
            "[cyan]Cover image path (optional, press Enter to skip)[/cyan]",
            default="",
            show_default=False
        )
        
        cover_image_path = None
        if cover_path_str.strip():
            cover_image_path = Path(cover_path_str.strip())
            if not cover_image_path.exists():
                self.console.print(f"[yellow]Warning: Cover image not found at {cover_image_path}[/yellow]")
                self.console.print("[yellow]Proceeding without cover image...[/yellow]")
                cover_image_path = None
            elif not cover_image_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                self.console.print(f"[yellow]Warning: {cover_image_path} may not be a supported image format[/yellow]")
                self.console.print("[yellow]Supported formats: JPG, PNG, GIF, BMP, WebP[/yellow]")
        
        epub.export_epub(
            self.project.book_root, 
            self.project.book_dir, 
            self.project.book_title_slug, 
            self.console,
            cover_image_path=cover_image_path
        )

    def manage_lorebook(self, lorebook_path: str):
        """Interactive lorebook management interface."""
        from rich.prompt import Prompt
        
        path = Path(lorebook_path)
        lorebook_data = self._load_or_create_lorebook(path)
        
        if not lorebook_data:
            return
        
        self.console.print(Panel(
            f"[bold green]Lorebook Manager[/bold green]\n"
            f"File: {path.name}",
            title="Fiction Fabricator"
        ))
        
        while True:
            self.console.print("\n[bold]Lorebook Management Options:[/bold]")
            self.console.print("1. List entries")
            self.console.print("2. Add new entry")
            self.console.print("3. Edit existing entry")
            self.console.print("4. Remove entry")
            self.console.print("5. Condense entry with LLM")
            self.console.print("6. Expand entry with LLM")
            self.console.print("7. Save and exit")
            self.console.print("8. Exit without saving")
            
            choice = Prompt.ask("\nSelect option", choices=["1", "2", "3", "4", "5", "6", "7", "8"])
            
            if choice == "1":
                self._list_lorebook_entries(lorebook_data)
            elif choice == "2":
                self._add_lorebook_entry(lorebook_data)
            elif choice == "3":
                self._edit_lorebook_entry(lorebook_data)
            elif choice == "4":
                self._remove_lorebook_entry(lorebook_data)
            elif choice == "5":
                self._condense_lorebook_entry(lorebook_data)
            elif choice == "6":
                self._expand_lorebook_entry(lorebook_data)
            elif choice == "7":
                self._save_lorebook(path, lorebook_data)
                self.console.print("[green]Lorebook saved successfully![/green]")
                break
            elif choice == "8":
                if Confirm.ask("Exit without saving changes?"):
                    break

    def _load_or_create_lorebook(self, path: Path) -> dict | None:
        """Load existing lorebook or create new one."""
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.console.print(f"[green]Loaded existing lorebook: {path.name}[/green]")
                return data
            except (json.JSONDecodeError, IOError) as e:
                self.console.print(f"[red]Error loading lorebook: {e}[/red]")
                if not Confirm.ask("Create new lorebook instead?"):
                    return None
        
        # Create new lorebook
        self.console.print(f"[blue]Creating new lorebook: {path.name}[/blue]")
        return {
            "entries": [],
            "name": path.stem,
            "description": "Fiction Fabricator Lorebook"
        }

    def _list_lorebook_entries(self, lorebook_data: dict):
        """List all entries in the lorebook."""
        entries = lorebook_data.get("entries", [])
        
        if not entries:
            self.console.print("[yellow]No entries found in lorebook.[/yellow]")
            return
        
        self.console.print(f"\n[bold]Lorebook Entries ({len(entries)}):[/bold]")
        for i, entry in enumerate(entries):
            title = entry.get("comment", entry.get("title", f"Entry {i+1}"))
            keys = entry.get("keys", [])
            if isinstance(keys, str):
                keys = [k.strip() for k in keys.split(",")]
            
            enabled = not entry.get("disable", False) and entry.get("enable", True)
            status = "[green]✓[/green]" if enabled else "[red]✗[/red]"
            
            self.console.print(f"{i+1:2d}. {status} [bold]{title}[/bold]")
            self.console.print(f"    Keywords: {', '.join(keys) if keys else 'None'}")
            
            content = entry.get("content", "")
            content_preview = content[:100] + "..." if len(content) > 100 else content
            self.console.print(f"    Content: {content_preview}\n")

    def _add_lorebook_entry(self, lorebook_data: dict):
        """Add a new entry to the lorebook with LLM assistance."""
        from rich.prompt import Prompt
        
        self.console.print("\n[bold]Add New Lorebook Entry[/bold]")
        
        # Get basic information
        title = Prompt.ask("Entry title/name")
        keywords_input = Prompt.ask("Keywords (comma-separated)")
        keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
        
        # Get initial content
        content = Prompt.ask("Initial content description (LLM will help expand this)")
        
        # Use LLM to help create the entry
        if content and Confirm.ask("Would you like LLM assistance to expand this entry?"):
            content = self._llm_expand_entry_content(title, keywords, content)
        
        # Create the entry
        new_entry = {
            "keys": keywords,
            "content": content,
            "comment": title,
            "enable": True,
            "disable": False
        }
        
        lorebook_data.setdefault("entries", []).append(new_entry)
        self.console.print(f"[green]Added entry: {title}[/green]")

    def _edit_lorebook_entry(self, lorebook_data: dict):
        """Edit an existing lorebook entry."""
        from rich.prompt import Prompt, IntPrompt
        
        entries = lorebook_data.get("entries", [])
        if not entries:
            self.console.print("[yellow]No entries to edit.[/yellow]")
            return
        
        self._list_lorebook_entries(lorebook_data)
        
        try:
            index = IntPrompt.ask("Select entry number to edit", default=1) - 1
            if index < 0 or index >= len(entries):
                self.console.print("[red]Invalid entry number.[/red]")
                return
        except:
            return
        
        entry = entries[index]
        current_title = entry.get("comment", entry.get("title", "Entry"))
        
        self.console.print(f"\n[bold]Editing: {current_title}[/bold]")
        
        # Edit fields
        new_title = Prompt.ask("Title", default=current_title)
        
        current_keys = entry.get("keys", [])
        if isinstance(current_keys, str):
            current_keys = [k.strip() for k in current_keys.split(",")]
        current_keys_str = ", ".join(current_keys)
        
        new_keywords_str = Prompt.ask("Keywords", default=current_keys_str)
        new_keywords = [k.strip() for k in new_keywords_str.split(",") if k.strip()]
        
        current_content = entry.get("content", "")
        self.console.print(f"\nCurrent content:\n{current_content}\n")
        
        if Confirm.ask("Edit content?"):
            new_content = Prompt.ask("New content", default=current_content)
            entry["content"] = new_content
        
        # Update entry
        entry["comment"] = new_title
        entry["keys"] = new_keywords
        
        self.console.print(f"[green]Updated entry: {new_title}[/green]")

    def _remove_lorebook_entry(self, lorebook_data: dict):
        """Remove an entry from the lorebook."""
        from rich.prompt import IntPrompt
        
        entries = lorebook_data.get("entries", [])
        if not entries:
            self.console.print("[yellow]No entries to remove.[/yellow]")
            return
        
        self._list_lorebook_entries(lorebook_data)
        
        try:
            index = IntPrompt.ask("Select entry number to remove", default=1) - 1
            if index < 0 or index >= len(entries):
                self.console.print("[red]Invalid entry number.[/red]")
                return
        except:
            return
        
        entry = entries[index]
        title = entry.get("comment", entry.get("title", f"Entry {index+1}"))
        
        if Confirm.ask(f"Remove entry '{title}'?"):
            entries.pop(index)
            self.console.print(f"[green]Removed entry: {title}[/green]")

    def _condense_lorebook_entry(self, lorebook_data: dict):
        """Use LLM to condense an entry's content."""
        from rich.prompt import IntPrompt
        
        entries = lorebook_data.get("entries", [])
        if not entries:
            self.console.print("[yellow]No entries to condense.[/yellow]")
            return
        
        self._list_lorebook_entries(lorebook_data)
        
        try:
            index = IntPrompt.ask("Select entry number to condense", default=1) - 1
            if index < 0 or index >= len(entries):
                self.console.print("[red]Invalid entry number.[/red]")
                return
        except:
            return
        
        entry = entries[index]
        current_content = entry.get("content", "")
        
        if not current_content:
            self.console.print("[yellow]Entry has no content to condense.[/yellow]")
            return
        
        title = entry.get("comment", entry.get("title", "Entry"))
        self.console.print(f"\n[bold]Condensing: {title}[/bold]")
        
        condensed_content = self._llm_condense_entry_content(title, current_content)
        
        if condensed_content and Confirm.ask("Use condensed version?"):
            entry["content"] = condensed_content
            self.console.print(f"[green]Condensed entry: {title}[/green]")

    def _expand_lorebook_entry(self, lorebook_data: dict):
        """Use LLM to expand an entry's content."""
        from rich.prompt import IntPrompt
        
        entries = lorebook_data.get("entries", [])
        if not entries:
            self.console.print("[yellow]No entries to expand.[/yellow]")
            return
        
        self._list_lorebook_entries(lorebook_data)
        
        try:
            index = IntPrompt.ask("Select entry number to expand", default=1) - 1
            if index < 0 or index >= len(entries):
                self.console.print("[red]Invalid entry number.[/red]")
                return
        except:
            return
        
        entry = entries[index]
        current_content = entry.get("content", "")
        
        if not current_content:
            self.console.print("[yellow]Entry has no content to expand.[/yellow]")
            return
        
        title = entry.get("comment", entry.get("title", "Entry"))
        self.console.print(f"\n[bold]Expanding: {title}[/bold]")
        
        expanded_content = self._llm_expand_entry_content(title, entry.get("keys", []), current_content)
        
        if expanded_content and Confirm.ask("Use expanded version?"):
            entry["content"] = expanded_content
            self.console.print(f"[green]Expanded entry: {title}[/green]")

    def _llm_expand_entry_content(self, title: str, keywords: list, current_content: str) -> str:
        """Use LLM to expand/improve entry content."""
        keywords_str = ", ".join(keywords) if keywords else "None"
        
        prompt = f"""You are helping to expand a lorebook entry for a creative writing project.

Entry Title: {title}
Keywords: {keywords_str}
Current Content: {current_content}

Please expand and improve this lorebook entry. Make it more detailed, engaging, and useful for writers. Include:
- More descriptive details
- Relevant background information
- Potential plot hooks or story elements
- Atmosphere and tone details

Keep the expanded content focused and well-organized. Write in a clear, informative style that would be helpful for creative writing."""

        try:
            response = self.llm.get_response(prompt, "Expanding lorebook entry", allow_stream=False)
            return response.strip() if response else current_content
        except Exception as e:
            self.console.print(f"[red]Error expanding content: {e}[/red]")
            return current_content

    def _llm_condense_entry_content(self, title: str, current_content: str) -> str:
        """Use LLM to condense entry content."""
        prompt = f"""You are helping to condense a lorebook entry for a creative writing project.

Entry Title: {title}
Current Content: {current_content}

Please condense this lorebook entry while preserving all essential information. Focus on:
- Key facts and details
- Important characteristics
- Core concepts
- Essential plot elements

Remove redundancy and verbose descriptions while keeping the content informative and useful for writers."""

        try:
            response = self.llm.get_response(prompt, "Condensing lorebook entry", allow_stream=False)
            return response.strip() if response else current_content
        except Exception as e:
            self.console.print(f"[red]Error condensing content: {e}[/red]")
            return current_content

    def _save_lorebook(self, path: Path, lorebook_data: dict):
        """Save the lorebook data to file."""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(lorebook_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            self.console.print(f"[red]Error saving lorebook: {e}[/red]")
            raise

    def create_enhanced_prompt(self):
        """Interactive prompt enhancement interface using LLM assistance."""
        from rich.prompt import Prompt
        
        self.console.print("\n[bold cyan]📝 Fiction Fabricator - Prompt Enhancement[/bold cyan]")
        self.console.print(Panel(
            "Transform your basic story idea into a comprehensive, detailed prompt\n"
            "that will help generate richer, more engaging fiction.",
            title="Prompt Enhancement",
            border_style="cyan"
        ))
        
        # Get basic idea from user
        basic_idea = Prompt.ask(
            "\n[yellow]Enter your basic story idea or concept[/yellow]",
            default=""
        ).strip()
        
        if not basic_idea:
            self.console.print("[red]No idea provided. Exiting.[/red]")
            return
        
        self.console.print(f"\n[dim]Your basic idea: {basic_idea}[/dim]\n")
        
        # Get optional story preferences
        story_type = self._prompt_for_enhancement_type()
        target_length = self._prompt_for_target_length(story_type)
        genre_preference = self._prompt_for_genre_preference()
        
        # Add lorebook context if available
        lorebook_context = ""
        if self.lorebook_data:
            lorebook_context = self._extract_lorebook_context(basic_idea)
            if lorebook_context:
                self.console.print("[cyan]Found relevant lorebook context to include.[/cyan]")
        
        # Generate enhanced prompt using LLM
        self.console.print("\n[bold yellow]⚡ Enhancing your prompt with AI...[/bold yellow]")
        
        enhanced_prompt = self._llm_enhance_prompt(
            basic_idea, story_type, target_length, genre_preference, lorebook_context
        )
        
        if not enhanced_prompt:
            self.console.print("[red]Failed to enhance prompt. Using original idea.[/red]")
            enhanced_prompt = basic_idea
        
        # Display the enhanced prompt
        self.console.print("\n" + "="*60)
        self.console.print(Panel(
            enhanced_prompt,
            title="[bold green]Enhanced Story Prompt[/bold green]",
            border_style="green"
        ))
        self.console.print("="*60)
        
        # Ask if user wants to save or use the prompt
        self._handle_enhanced_prompt_output(enhanced_prompt)

    def _prompt_for_enhancement_type(self) -> str:
        """Ask user what type of story they want to create."""
        from rich.prompt import Prompt
        
        choice = Prompt.ask(
            "\n[cyan]What type of story do you want to create?[/cyan]\n"
            "[1] Novel (longer, multi-chapter)\n"
            "[2] Short Story (shorter, focused)\n"
            "[3] Let AI decide based on the idea\n"
            "Choose option",
            choices=["1", "2", "3"],
            default="3"
        )
        
        if choice == "1":
            return "novel"
        elif choice == "2": 
            return "short_story"
        else:
            return "auto"

    def _prompt_for_target_length(self, story_type: str) -> str:
        """Ask for target length preferences."""
        from rich.prompt import Prompt
        
        if story_type == "auto":
            return "flexible"
        
        if story_type == "novel":
            choice = Prompt.ask(
                "\n[cyan]Target novel length?[/cyan]\n"
                "[1] Short novel (50,000-70,000 words)\n"
                "[2] Standard novel (70,000-100,000 words)\n"
                "[3] Long novel (100,000+ words)\n"
                "[4] Let AI decide\n"
                "Choose option",
                choices=["1", "2", "3", "4"],
                default="4"
            )
            
            length_map = {
                "1": "short novel (50k-70k words)",
                "2": "standard novel (70k-100k words)", 
                "3": "long novel (100k+ words)",
                "4": "flexible"
            }
            return length_map.get(choice, "flexible")
        
        else:  # short_story
            choice = Prompt.ask(
                "\n[cyan]Target short story length?[/cyan]\n"
                "[1] Flash fiction (under 1,000 words)\n"
                "[2] Short story (1,000-5,000 words)\n"
                "[3] Novelette (5,000-15,000 words)\n"
                "[4] Let AI decide\n"
                "Choose option",
                choices=["1", "2", "3", "4"],
                default="4"
            )
            
            length_map = {
                "1": "flash fiction (under 1k words)",
                "2": "short story (1k-5k words)",
                "3": "novelette (5k-15k words)",
                "4": "flexible"
            }
            return length_map.get(choice, "flexible")

    def _prompt_for_genre_preference(self) -> str:
        """Ask for genre preferences."""
        from rich.prompt import Prompt
        
        return Prompt.ask(
            "\n[cyan]Genre preference (optional)[/cyan]\n"
            "e.g., fantasy, sci-fi, mystery, romance, literary fiction, etc.\n"
            "Leave blank to let AI determine from your idea",
            default=""
        ).strip()

    def _llm_enhance_prompt(self, basic_idea: str, story_type: str, target_length: str, 
                           genre: str, lorebook_context: str) -> str:
        """Use LLM to transform basic idea into comprehensive prompt."""
        
        # Build the enhancement prompt
        prompt_parts = [
            "You are an expert writing coach helping transform a basic story idea into a comprehensive, detailed prompt for fiction generation.",
            "",
            f"Basic Story Idea: {basic_idea}",
            "",
            "Transform this basic idea into a rich, detailed story prompt that includes:",
            "- An engaging premise with clear stakes and conflict",
            "- Well-defined main characters with motivations and goals", 
            "- A compelling setting with atmospheric details",
            "- Plot direction and story structure hints",
            "- Tone, mood, and style guidance",
            "- Themes or deeper meaning to explore",
            "",
        ]
        
        # Add story type guidance
        if story_type == "novel":
            prompt_parts.extend([
                f"Target Format: Novel ({target_length})",
                "- Focus on epic scope, multiple plot threads, character development arcs",
                "- Include subplots, supporting characters, and world-building depth",
                "- Consider pacing across multiple chapters",
                "",
            ])
        elif story_type == "short_story":
            prompt_parts.extend([
                f"Target Format: Short Story ({target_length})",
                "- Focus on a single central conflict or moment of change",
                "- Emphasize tight pacing and concentrated impact",
                "- Limit characters and settings for focused storytelling",
                "",
            ])
        else:  # auto
            prompt_parts.extend([
                "Target Format: Let the story idea determine the best format",
                "- Suggest whether this works better as a novel or short story",
                "- Explain your reasoning for the format choice",
                "",
            ])
        
        # Add genre guidance
        if genre:
            prompt_parts.extend([
                f"Genre: {genre}",
                f"- Incorporate typical {genre} elements, tropes, and expectations",
                f"- Consider {genre} audience preferences and conventions",
                "",
            ])
        
        # Add lorebook context if available
        if lorebook_context:
            prompt_parts.extend([
                "Relevant World Context:",
                lorebook_context,
                "- Integrate this world-building seamlessly into the enhanced prompt",
                "",
            ])
        
        prompt_parts.extend([
            "Write the enhanced prompt as a single, cohesive description that a fiction generator AI could use to create an engaging story.",
            "Make it detailed but not overly prescriptive - leave room for creative interpretation.",
            "Focus on inspiring rich, vivid storytelling."
        ])
        
        full_prompt = "\n".join(prompt_parts)
        
        try:
            response = self.llm.get_response(full_prompt, "Enhancing story prompt", allow_stream=False)
            return response.strip() if response else basic_idea
        except Exception as e:
            self.console.print(f"[red]Error enhancing prompt: {e}[/red]")
            return basic_idea

    def _handle_enhanced_prompt_output(self, enhanced_prompt: str):
        """Handle what to do with the enhanced prompt."""
        from rich.prompt import Prompt
        
        choice = Prompt.ask(
            "\n[yellow]What would you like to do with this enhanced prompt?[/yellow]\n"
            "[1] Save to a text file\n"
            "[2] Copy to clipboard (display for manual copy)\n"
            "[3] Use immediately to start generating a story\n"
            "[4] Exit without saving\n"
            "Choose option",
            choices=["1", "2", "3", "4"],
            default="1"
        )
        
        if choice == "1":
            self._save_enhanced_prompt_to_file(enhanced_prompt)
        elif choice == "2":
            self.console.print("\n[cyan]Copy the enhanced prompt below:[/cyan]")
            self.console.print(f"\n{enhanced_prompt}\n")
        elif choice == "3":
            self._start_story_generation_with_prompt(enhanced_prompt)
        else:
            self.console.print("\n[dim]Exiting without saving.[/dim]")

    def _save_enhanced_prompt_to_file(self, enhanced_prompt: str):
        """Save the enhanced prompt to a text file."""
        from rich.prompt import Prompt
        from datetime import datetime
        import re
        
        # Generate default filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"enhanced_prompt_{timestamp}.txt"
        
        while True:
            filename = Prompt.ask(
                f"[cyan]Filename for enhanced prompt[/cyan]",
                default=default_filename
            )
            
            # Clean and validate filename
            # Remove or replace invalid characters
            clean_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            
            # Truncate if too long (max 200 chars to be safe)
            if len(clean_filename) > 200:
                # Try to extract first few words as filename
                words = clean_filename.split()[:5]  # First 5 words
                clean_filename = "_".join(words) + f"_{timestamp}.txt"
                self.console.print(f"[yellow]Filename too long, using: {clean_filename}[/yellow]")
            
            # Ensure .txt extension
            if not clean_filename.lower().endswith('.txt'):
                clean_filename += '.txt'
            
            try:
                file_path = Path(clean_filename)
                file_path.write_text(enhanced_prompt, encoding='utf-8')
                self.console.print(f"[green]✓ Enhanced prompt saved to: {file_path.absolute()}[/green]")
                
                # Ask if they want to use this file to start generation
                if Confirm.ask("\nStart story generation using this prompt file?"):
                    self._start_story_generation_with_file(file_path)
                break
                    
            except Exception as e:
                if "File name too long" in str(e) or "name too long" in str(e):
                    self.console.print(f"[red]Filename still too long. Please enter a shorter name.[/red]")
                    continue
                else:
                    self.console.print(f"[red]Error saving prompt file: {e}[/red]")
                    break

    def _start_story_generation_with_prompt(self, prompt: str):
        """Start story generation workflow with the enhanced prompt."""
        self.console.print("\n[bold green]🚀 Starting story generation with enhanced prompt...[/bold green]")
        
        # This would integrate with the main generation workflow
        if self.setup_new_project(prompt):
            self.run()

    def _start_story_generation_with_file(self, prompt_file: Path):
        """Start story generation using a prompt file.""" 
        self.console.print(f"\n[bold green]🚀 Starting story generation with prompt file: {prompt_file.name}[/bold green]")
        
        try:
            prompt = prompt_file.read_text(encoding='utf-8')
            if self.setup_new_project(prompt):
                self.run()
        except Exception as e:
            self.console.print(f"[red]Error reading prompt file: {e}[/red]")
