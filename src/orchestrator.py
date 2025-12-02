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

from src import ui, utils, config
from src.llm_client import LLMClient
from src.project import Project
from src.generators import novel, short_story
from src.exporters import markdown, epub, html
from src.exporters import pdf, txt

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

        # Step 2: Manage Outline Chapters (Edit/Add/Delete)
        if Confirm.ask("\n[yellow]Would you like to review and edit the chapter outline?[/yellow]", default=True):
            ui.manage_outline_chapters(self.project)

        # Step 3: Review and Modify Story Elements
        modified_elements = ui.review_and_modify_story_elements(self.project)
        if modified_elements:
            self._update_story_elements(modified_elements)
        
        # Step 4: Content Generation
        if Confirm.ask("\n[yellow]Proceeding to Chapter/Scene Content Generation. Confirm?[/yellow]", default=True):
            self.run_content_generation()

        # Step 5: Editing
        if Confirm.ask("\n[yellow]Content generation complete. Proceed to Editing?[/yellow]", default=True):
            self.run_editing_loop()

        self.console.print(Panel("[bold green]📚 Fiction Fabricator session finished. 📚[/bold green]"))

    def setup_new_project(self, idea: str):
        """Guides the user through setting up a new project."""
        # Offer lorebook selection if none was provided via CLI
        if not self.lorebook_data:
            lorebook_path, is_import = ui.prompt_for_lorebook_creation_or_import()
            if lorebook_path:
                # For new lorebooks (not imports), use _load_or_create_lorebook to enable auto-generation
                # For imports, just load the existing file
                path = Path(lorebook_path)
                if is_import or path.exists():
                    self.lorebook_data = self._load_lorebook(lorebook_path)
                else:
                    # New lorebook - load/create with book idea for auto-generation
                    # Then open management interface for user to review/edit
                    self.lorebook_data = self._load_or_create_lorebook(path, book_idea=idea)
                    if self.lorebook_data:
                        # Save initial version
                        self._save_lorebook(path, self.lorebook_data)
                        # Open lorebook manager for user to review/edit entries
                        if self.lorebook_data.get("entries"):
                            if Confirm.ask("[yellow]Would you like to review and edit the generated lorebook entries now?[/yellow]", default=True):
                                self.manage_lorebook(str(path))
                                # Reload the potentially modified lorebook
                                self.lorebook_data = self._load_lorebook(str(path))
        
        # 1. Get initial title and synopsis
        title, synopsis = self._generate_initial_summary(idea)
        if not title or not synopsis:
            self.console.print("[bold red]Could not generate initial title and synopsis. Exiting.[/bold red]")
            return False

        # 2. Allow user to customize the generated title
        from rich.prompt import Prompt
        self.console.print(f"\n[bold green]Generated Title:[/bold green] {title}")
        if Confirm.ask("[yellow]Would you like to use a different title?[/yellow]", default=False):
            custom_title = Prompt.ask("[cyan]Enter your preferred title[/cyan]", default=title)
            if custom_title and custom_title.strip():
                title = custom_title.strip()
                self.console.print(f"[green]Using title: {title}[/green]")

        # 3. Initialize the project state
        self.project.setup_new_project(idea, title, synopsis)

        # 4. Ask for story type
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

    def _update_story_elements(self, modified_elements: dict):
        """
        Updates the story_elements in the project XML with user modifications.
        
        Args:
            modified_elements: Dictionary with title, genre, tone, perspective, and target_audience
        """
        if not self.project.book_root:
            self.console.print("[red]Error: No book root found.[/red]")
            return
        
        # Handle title separately as it's a direct child of book_root
        if "title" in modified_elements:
            title_element = self.project.book_root.find("title")
            if title_element is not None:
                title_element.text = modified_elements["title"]
            else:
                ET.SubElement(self.project.book_root, "title").text = modified_elements["title"]
        
        # Handle story_elements
        story_elements = self.project.book_root.find("story_elements")
        if story_elements is None:
            self.console.print("[yellow]Warning: story_elements not found in project. Creating new section.[/yellow]")
            story_elements = ET.SubElement(self.project.book_root, "story_elements")
        
        # Update or create each element (except title which was handled above)
        for key, value in modified_elements.items():
            if key == "title":
                continue  # Already handled above
            element = story_elements.find(key)
            if element is not None:
                element.text = value
            else:
                ET.SubElement(story_elements, key).text = value
        
        # Save the updated project
        if self.project.save_state("outline.xml"):
            self.console.print("[green]Story elements updated and saved.[/green]")
        else:
            self.console.print("[yellow]Warning: Could not save updated story elements.[/yellow]")

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
        # Don't clear chapters_generated_in_session for resumed projects - it was restored during loading

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
            "2": ("Make All Chapters Longer", self._edit_make_all_chapters_longer),
            "3": ("Rewrite Chapter (with instructions)", lambda: self._edit_rewrite_chapter(blackout=False)),
            "4": ("Rewrite Chapter (Fresh Rewrite)", lambda: self._edit_rewrite_chapter(blackout=True)),
            "5": ("Ask LLM for Edit Suggestions", self._edit_suggest_edits),
            "6": ("Apply LLM Advice to All Chapters", self._edit_apply_manuscript_advice),
            "7": ("Export Menu", self._show_export_menu),
            "8": ("Quit Editing", None),
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

    def _create_enhanced_context_for_book_editing(self, chapter_id: str) -> str:
        """Creates enhanced context for book-wide editing that includes narrative flow and continuity information."""
        if not self.project.book_root:
            return "<book></book>"
        
        # Create enhanced book structure for continuity-aware editing
        enhanced_book = ET.Element("book")
        
        # Add essential book metadata
        for elem_name in ["title", "synopsis", "story_elements"]:
            elem = self.project.book_root.find(elem_name)
            if elem is not None:
                enhanced_book.append(copy.deepcopy(elem))
        
        # Add complete character information for consistency
        characters_elem = self.project.book_root.find("characters")
        if characters_elem is not None:
            enhanced_book.append(copy.deepcopy(characters_elem))
        
        # Find target chapter
        all_chapters = self.project.book_root.findall(".//chapter")
        target_chapter = None
        target_index = -1
        
        for i, chapter in enumerate(all_chapters):
            if utils.get_chapter_id(chapter) == chapter_id:
                target_chapter = chapter
                target_index = i
                break
        
        if target_chapter is None:
            return ET.tostring(enhanced_book, encoding='unicode')
        
        # Add enhanced chapters section with broader context
        chapters_elem = ET.SubElement(enhanced_book, "chapters")
        
        # Include more chapters for better continuity (2 before, target, 2 after)
        context_range = range(max(0, target_index - 2), min(len(all_chapters), target_index + 3))
        
        for i in context_range:
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
            
            # For the target chapter, include full content
            if utils.get_chapter_id(chapter) == chapter_id:
                content_elem = chapter.find("content")
                if content_elem is not None:
                    chapter_copy.append(copy.deepcopy(content_elem))
            else:
                # For context chapters, include summary + first/last paragraphs for flow
                content_elem = chapter.find("content")
                if content_elem is not None:
                    context_content = ET.SubElement(chapter_copy, "content_context")
                    paragraphs = content_elem.findall("paragraph")
                    if paragraphs:
                        # Add first paragraph for lead-in context
                        if len(paragraphs) > 0:
                            first_para = ET.SubElement(context_content, "opening")
                            first_para.text = (paragraphs[0].text or "")[:300] + "..." if len(paragraphs[0].text or "") > 300 else paragraphs[0].text
                        
                        # Add last paragraph for lead-out context (if different from first)
                        if len(paragraphs) > 1:
                            last_para = ET.SubElement(context_content, "closing")
                            last_para.text = (paragraphs[-1].text or "")[:300] + "..." if len(paragraphs[-1].text or "") > 300 else paragraphs[-1].text
        
        # Add narrative flow summary for continuity awareness
        flow_elem = ET.SubElement(enhanced_book, "narrative_flow")
        flow_summary = f"This book has {len(all_chapters)} chapters. Target chapter {target_index + 1} of {len(all_chapters)}."
        
        if target_index > 0:
            prev_title = all_chapters[target_index - 1].findtext("title", "Previous Chapter")
            flow_summary += f" Follows '{prev_title}'."
        
        if target_index < len(all_chapters) - 1:
            next_title = all_chapters[target_index + 1].findtext("title", "Next Chapter")
            flow_summary += f" Leads to '{next_title}'."
        
        flow_elem.text = flow_summary
        
        return ET.tostring(enhanced_book, encoding='unicode')

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

IMPORTANT: Do not rewrite or replace existing content. Instead, expand it by:
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

    def _edit_make_all_chapters_longer(self):
        """Handler for making all chapters longer automatically."""
        # Check if book_root exists
        if not self.project.book_root:
            self.console.print("[red]No project loaded.[/red]")
            return
            
        # Get all chapters from the project
        chapters = sorted(self.project.book_root.findall(".//chapter"), 
                         key=lambda c: int(utils.get_chapter_id_with_default(c, "0")))
        
        if not chapters:
            self.console.print("[red]No chapters found in the project.[/red]")
            return

        word_count = ui.IntPrompt.ask("[yellow]Enter target word count per chapter[/yellow]", default=4500)
        
        # Auto-apply patches for all chapters
        self.console.print(f"[yellow]Auto-applying patches for all {len(chapters)} chapters (no confirmations)...[/yellow]")
        
        # Process each chapter individually to ensure all get expanded
        for chapter in chapters:
            chapter_id = utils.get_chapter_id(chapter)
            self.console.print(f"[cyan]Expanding Chapter {chapter_id}...[/cyan]")
            
            # Create reduced context to avoid token limits
            reduced_context = self._create_reduced_context_for_chapter(chapter_id)
            
            prompt = f"""
Expand the existing content for chapter {chapter_id} to approximately {word_count} words by building upon what's already written.

IMPORTANT: Do not rewrite or replace existing content. Instead, expand it by:
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
            self._handle_patch_result_auto(patch_xml, f"Make Longer (Ch {chapter_id})")

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
        if not self.project.book_root:
            self.console.print("[red]No book data available.[/red]")
            return
            
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
        
        # Ask if user wants to apply these suggestions to all chapters
        if Confirm.ask("\n[yellow]Apply these suggestions to all chapters?[/yellow]", default=False):
            self._apply_suggestions_to_all_chapters(suggestions_text)
        else:
            self.console.print("\n[yellow]Use the 'Rewrite Chapter' option to implement these suggestions.[/yellow]")

    def _edit_apply_manuscript_advice(self):
        """Handler for getting and applying LLM advice to all chapters."""
        self.console.print("[cyan]Generating manuscript-wide editing advice...[/cyan]")
        
        prompt = f"""
You are an expert editor providing manuscript-wide editing advice. Analyze this complete manuscript and provide specific, actionable suggestions that should be applied consistently across ALL chapters to improve the work.

Focus on:
- Consistent tone and voice improvements
- Character development enhancements
- Pacing adjustments
- Narrative consistency
- Style refinements
- Dialogue improvements
- Description and world-building enhancements

Provide your advice as a numbered list of specific, implementable suggestions that can be applied to each chapter.

Full Book Context:
```xml
{ET.tostring(self.project.book_root, encoding='unicode')}
```
"""
        suggestions_text = self.llm.get_response(prompt, "Generating manuscript advice", allow_stream=False)
        if not suggestions_text:
            self.console.print("[red]Failed to generate manuscript advice.[/red]")
            return
        
        self.console.print(Panel(suggestions_text, title="Manuscript-Wide Editing Advice", border_style="green"))
        
        if Confirm.ask("\n[yellow]Apply this advice to all chapters?[/yellow]", default=True):
            self._apply_suggestions_to_all_chapters(suggestions_text)
    
    def _apply_suggestions_to_all_chapters(self, suggestions_text: str):
        """Apply LLM suggestions to all chapters in the manuscript."""
        chapters = sorted(self.project.book_root.findall(".//chapter"), 
                         key=lambda c: int(utils.get_chapter_id_with_default(c, "0")))
        
        if not chapters:
            self.console.print("[yellow]No chapters found to apply suggestions to.[/yellow]")
            return
        
        self.console.print(f"[bold yellow]Applying advice to {len(chapters)} chapters...[/bold yellow]")
        self.console.print("[dim]This will auto-apply patches without individual confirmations.[/dim]")
        self.console.print("[cyan]Using enhanced continuity-aware context for each chapter.[/cyan]\n")
        
        failed_chapters = []
        
        for chapter in chapters:
            chapter_id = utils.get_chapter_id(chapter)
            self.console.print(f"[cyan]Applying advice to Chapter {chapter_id}...[/cyan]")
            
            # Use enhanced context for better inter-chapter continuity
            enhanced_context = self._create_enhanced_context_for_book_editing(chapter_id)
            
            prompt = f"""
Apply the following editing advice to Chapter {chapter_id}. Rewrite the chapter content incorporating these suggestions while maintaining the original plot, character development, and narrative flow.

EDITING ADVICE TO APPLY:
{suggestions_text}

IMPORTANT CONTINUITY REQUIREMENTS:
- Maintain the chapter's existing structure and plot points
- Keep all character actions and dialogue meaningful to the story
- Preserve the chapter's role in the overall narrative
- Ensure smooth transitions from previous chapter and to next chapter
- Maintain character consistency and development arcs across chapters
- Preserve any plot threads, foreshadowing, or story elements that connect to other chapters
- Focus on implementing the advice to improve writing quality, style, and consistency
- Do not change major plot elements, character motivations, or narrative dependencies

CONTEXT AWARENESS:
The enhanced context below includes surrounding chapters and narrative flow information to help you maintain continuity. Pay attention to:
- How this chapter connects to previous and following chapters
- Character states and development from previous chapters
- Ongoing plot threads and story elements that must be preserved
- Tone and style consistency with the broader narrative

Output format: Return ONLY an XML `<patch>` containing a `<chapter>` element with the complete updated content. Use this EXACT format:

<patch>
  <chapter id="{chapter_id}">
    <content>
      <paragraph>First updated paragraph...</paragraph>
      <paragraph>Second updated paragraph...</paragraph>
    </content>
  </chapter>
</patch>

Enhanced Context for Continuity:
```xml
{enhanced_context}
```
"""
            
            patch_xml = self.llm.get_response(prompt, f"Applying advice to chapter {chapter_id}")
            
            if patch_xml and self.project.apply_patch(patch_xml):
                patch_num = utils.get_next_patch_number(self.project.book_dir)
                self.project.save_state(f"patch-{patch_num:02d}.xml")
                self.console.print(f"[green]✓ Chapter {chapter_id} updated successfully[/green]")
            else:
                failed_chapters.append(chapter_id)
                self.console.print(f"[red]✗ Failed to update Chapter {chapter_id}[/red]")
        
        # Summary
        success_count = len(chapters) - len(failed_chapters)
        self.console.print(f"\n[bold green]Manuscript-wide advice application complete![/bold green]")
        self.console.print(f"Successfully updated: {success_count}/{len(chapters)} chapters")
        
        if failed_chapters:
            failed_list = ", ".join(failed_chapters)
            self.console.print(f"[yellow]Failed chapters: {failed_list}[/yellow]")
            self.console.print("[dim]You can try applying advice to failed chapters individually using 'Rewrite Chapter'.[/dim]")
        else:
            self.console.print("[bold cyan]All chapters updated with continuity-aware context! ✨[/bold cyan]")
            self.console.print("[dim]Inter-chapter narrative flow and character consistency have been preserved.[/dim]")


    def _show_export_menu(self):
        """Displays the export menu and handles user choice."""
        export_options = {
            "1": ("Edit Frontmatter", self._edit_frontmatter_menu),
            "2": ("Select Chapter Heading Font", self._select_font),
            "3": ("Export All Formats", self._export_all),
            "4": ("Export Full Book (Single Markdown)", self._export_single_md),
            "5": ("Export Chapters (Markdown per Chapter)", self._export_multi_md),
            "6": ("Export Full Book (Single HTML)", self._export_single_html),
            "7": ("Export Chapters (HTML per Chapter)", self._export_multi_html),
            "8": ("Export Full Book (EPUB)", self._export_epub),
            "9": ("Export Full Book (PDF)", self._export_pdf),
            "10": ("Export Full Book (TXT)", self._export_single_txt),
            "11": ("Export Chapters (TXT per Chapter)", self._export_multi_txt),
            "12": ("Return to Editing Menu", None),
        }
        choice = ui.display_menu("Export Options", export_options)
        handler = export_options.get(choice)[1]
        if handler:
            handler()

    def _edit_frontmatter_menu(self):
        """Displays the frontmatter editing menu."""
        frontmatter_options = {
            "1": ("Edit Author Name", lambda: self._edit_author_name()),
            "2": ("Edit Book Title", lambda: self._edit_book_title()),
            "3": ("Edit Title Page", lambda: self._edit_frontmatter_section("title_page")),
            "4": ("Edit Copyright Page", lambda: self._edit_frontmatter_section("copyright_page")),
            "5": ("Edit Dedication", lambda: self._edit_frontmatter_section("dedication")),
            "6": ("Edit Acknowledgements", lambda: self._edit_frontmatter_section("acknowledgements")),
            "7": ("Return to Export Menu", None),
        }
        
        while True:
            choice = ui.display_menu("Edit Frontmatter", frontmatter_options)
            handler = frontmatter_options.get(choice)[1]
            if handler:
                handler()
                # Save changes after editing
                if self.project.book_root is not None:
                    patch_num = utils.get_next_patch_number(self.project.book_dir)
                    self.project.save_state(f"patch-{patch_num:02d}.xml")
            else:
                break  # Return to Export Menu

    def _edit_author_name(self):
        """Edit the author name."""
        if self.project.edit_author_name():
            self.console.print("[green]Author name updated successfully.[/green]")
        else:
            self.console.print("[dim]Author name not changed.[/dim]")

    def _edit_book_title(self):
        """Edit the book title."""
        if self.project.edit_book_title():
            self.console.print("[green]Book title updated successfully.[/green]")
        else:
            self.console.print("[dim]Book title not changed.[/dim]")

    def _edit_frontmatter_section(self, section_name: str):
        """Edit a specific frontmatter section."""
        if self.project.edit_frontmatter_section(section_name):
            self.console.print(f"[green]Frontmatter section '{section_name.replace('_', ' ').title()}' saved.[/green]")
        else:
            self.console.print(f"[yellow]No changes made to frontmatter section '{section_name.replace('_', ' ').title()}'.[/yellow]")

    def _select_font(self):
        """Allow the user to select a custom font for chapter headings."""
        # Display current font selection
        current_font = getattr(self, 'selected_font', config.DEFAULT_CHAPTER_FONT)
        self.console.print(f"[dim]Current chapter heading font: {current_font}[/dim]")
        
        # Create font selection menu
        font_options = {str(i + 1): (font, None) for i, font in enumerate(config.GOOGLE_FONT_OPTIONS)}
        font_options[str(len(config.GOOGLE_FONT_OPTIONS) + 1)] = ("Use Default Font (Georgia)", None)
        font_options[str(len(config.GOOGLE_FONT_OPTIONS) + 2)] = ("Enter Custom Google Font URL", None)
        font_options[str(len(config.GOOGLE_FONT_OPTIONS) + 3)] = ("Return to Export Menu", None)
        
        choice = ui.display_menu("Select Chapter Heading Font", font_options)
        
        if choice == str(len(config.GOOGLE_FONT_OPTIONS) + 1):
            # Use default font
            self.selected_font = config.DEFAULT_CHAPTER_FONT
            self.selected_font_url = None
            self.console.print(f"[green]Chapter heading font set to default: {self.selected_font}[/green]")
        elif choice == str(len(config.GOOGLE_FONT_OPTIONS) + 2):
            # Custom font URL
            from rich.prompt import Prompt
            font_url = Prompt.ask("[cyan]Enter Google Font CSS URL[/cyan]")
            if font_url and font_url.strip():
                font_name = Prompt.ask("[cyan]Enter font family name (e.g., 'Open Sans')[/cyan]")
                if font_name and font_name.strip():
                    self.selected_font = font_name.strip()
                    self.selected_font_url = font_url.strip()
                    self.console.print(f"[green]Custom font set: {self.selected_font}[/green]")
                else:
                    self.console.print("[yellow]Font name is required for custom fonts[/yellow]")
            else:
                self.console.print("[yellow]No font URL provided[/yellow]")
        elif choice == str(len(config.GOOGLE_FONT_OPTIONS) + 3):
            # Return to menu
            return
        else:
            # Selected a predefined Google Font
            try:
                font_index = int(choice) - 1
                if 0 <= font_index < len(config.GOOGLE_FONT_OPTIONS):
                    selected_font = config.GOOGLE_FONT_OPTIONS[font_index]
                    self.selected_font = selected_font
                    self.selected_font_url = config.GOOGLE_FONT_URLS.get(selected_font)
                    self.console.print(f"[green]Chapter heading font set to: {self.selected_font}[/green]")
                else:
                    self.console.print("[red]Invalid font selection[/red]")
            except ValueError:
                self.console.print("[red]Invalid selection[/red]")

    def _export_single_md(self):
        filename = f"{self.project.book_title_slug}-full.md"
        output_path = self.project.book_dir / filename
        markdown.export_single_markdown(self.project.book_root, output_path, self.console)

    def _export_multi_md(self):
        markdown.export_markdown_per_chapter(self.project.book_root, self.project.book_dir, self.project.book_title_slug, self.console)

    def _export_single_html(self):
        filename = f"{self.project.book_title_slug}-full.html"
        output_path = self.project.book_dir / filename
        # Get selected font settings
        font_name = getattr(self, 'selected_font', None)
        font_url = getattr(self, 'selected_font_url', None)
        html.export_single_html(self.project.book_root, output_path, self.console, font_name, font_url)

    def _export_multi_html(self):
        # Get selected font settings
        font_name = getattr(self, 'selected_font', None)
        font_url = getattr(self, 'selected_font_url', None)
        html.export_html_per_chapter(self.project.book_root, self.project.book_dir, self.project.book_title_slug, self.console, font_name, font_url)

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
        
        # Get selected font settings
        font_name = getattr(self, 'selected_font', None)
        font_url = getattr(self, 'selected_font_url', None)
        
        epub.export_epub(
            self.project.book_root, 
            self.project.book_dir, 
            self.project.book_title_slug, 
            self.console,
            cover_image_path=cover_image_path,
            custom_font_name=font_name,
            custom_font_url=font_url
        )

    def _export_pdf(self):
        filename = f"{self.project.book_title_slug}-full.pdf"
        output_path = self.project.book_dir / filename
        # Get selected font settings
        font_name = getattr(self, 'selected_font', None)
        font_url = getattr(self, 'selected_font_url', None)
        pdf.export_pdf(self.project.book_root, output_path, self.console, font_name, font_url)

    def _export_single_txt(self):
        filename = f"{self.project.book_title_slug}-full.txt"
        output_path = self.project.book_dir / filename
        txt.export_single_txt(self.project.book_root, output_path, self.console)

    def _export_multi_txt(self):
        txt.export_txt_per_chapter(self.project.book_root, self.project.book_dir, self.project.book_title_slug, self.console)

    def _export_all(self):
        """Export the book in all available formats."""
        from rich.prompt import Prompt, Confirm
        from pathlib import Path
        
        self.console.print(Panel(
            "[bold cyan]Export All Formats[/bold cyan]\n"
            "This will create:\n"
            "• Full book (single Markdown)\n"
            "• Chapters (Markdown per chapter)\n"
            "• Full book (single HTML)\n"
            "• Chapters (HTML per chapter)\n"
            "• Full book (EPUB)\n"
            "• Full book (PDF)\n"
            "• Full book (TXT)\n"
            "• Chapters (TXT per chapter)",
            title="Export All"
        ))
        
        if not Confirm.ask("Proceed with exporting all formats?", default=True):
            return
        
        # Ask for optional cover image once for EPUB
        cover_path_str = Prompt.ask(
            "[cyan]Cover image path for EPUB (optional, press Enter to skip)[/cyan]",
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
        
        # Export all formats
        try:
            self.console.print("[cyan]Exporting full book (single Markdown)...[/cyan]")
            self._export_single_md()
            
            self.console.print("[cyan]Exporting chapters (Markdown per chapter)...[/cyan]")
            self._export_multi_md()
            
            self.console.print("[cyan]Exporting full book (single HTML)...[/cyan]")
            self._export_single_html()
            
            self.console.print("[cyan]Exporting chapters (HTML per chapter)...[/cyan]")
            self._export_multi_html()
            
            self.console.print("[cyan]Exporting full book (EPUB)...[/cyan]")
            # Temporarily store cover path for EPUB export
            from src.exporters import epub
            epub.export_epub(
                self.project.book_root, 
                self.project.book_dir, 
                self.project.book_title_slug, 
                self.console,
                cover_image_path=cover_image_path
            )
            
            self.console.print("[cyan]Exporting full book (PDF)...[/cyan]")
            self._export_pdf()
            
            self.console.print("[cyan]Exporting full book (TXT)...[/cyan]")
            self._export_single_txt()
            
            self.console.print("[cyan]Exporting chapters (TXT per chapter)...[/cyan]")
            self._export_multi_txt()
            
            self.console.print(Panel(
                "[bold green]✓ All formats exported successfully![/bold green]\n"
                f"Files saved to: {self.project.book_dir}",
                title="Export Complete"
            ))
            
        except Exception as e:
            self.console.print(f"[bold red]Error during export: {e}[/bold red]")
            self.console.print("[yellow]Some formats may have been exported successfully.[/yellow]")

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
            
            choice = ui.bullet_choice(
                "Select option:",
                [
                    "1. List entries",
                    "2. Add new entry",
                    "3. Edit existing entry",
                    "4. Remove entry",
                    "5. Condense entry with LLM",
                    "6. Expand entry with LLM",
                    "7. Save and exit",
                    "8. Exit without saving"
                ]
            )
            choice = choice[0]  # Extract the number from the choice
            
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

    def _generate_lorebook_entries(self, book_idea: str) -> list:
        """
        Auto-generates lorebook entries from the book idea using LLM.
        
        Args:
            book_idea: The initial book idea/prompt
            
        Returns:
            list: List of generated lorebook entry dictionaries
        """
        self.console.print("[cyan]Generating lorebook entries from your story idea...[/cyan]")
        
        prompt = f"""Based on the following story idea, generate 5-10 lorebook entries that would be helpful for maintaining consistency during story generation.

Story Idea:
---
{book_idea}
---

For each lorebook entry, identify:
1. Important world-building elements (locations, magic systems, technology, etc.)
2. Key concepts or rules unique to this story
3. Cultural or historical background information
4. Important objects or artifacts
5. Organizations or groups

Generate entries in the following JSON format:
{{
  "entries": [
    {{
      "comment": "Title/name of the entry",
      "keys": ["keyword1", "keyword2", "keyword3"],
      "content": "Complete, detailed description of this element. Include all relevant information to fully explain the concept, its significance, how it works, and its role in the story world. Write as much as needed to fully encapsulate the idea - do not cut descriptions short.",
      "enable": true,
      "disable": false
    }}
  ]
}}

Guidelines:
- Each entry should focus on ONE specific element
- Keywords should be terms that might appear in the story text
- Content should be thorough and complete - include ALL important details about each element
- Each content field should fully explain the concept without being cut off mid-thought
- Write complete sentences and paragraphs - quality and completeness over brevity
- Generate between 5-10 entries depending on story complexity
- Focus on world-building elements, not plot points or characters
- IMPORTANT: Complete each entry fully - do not truncate descriptions

Output ONLY the JSON object, no additional text.
"""
        
        response = self.llm.get_response(prompt, "Generating lorebook entries", allow_stream=True)
        
        if not response:
            self.console.print("[red]Failed to generate lorebook entries.[/red]")
            return []
        
        try:
            # Clean up the response
            cleaned = re.sub(r"^```json\s*|\s*```$", "", response.strip(), flags=re.IGNORECASE | re.MULTILINE)
            data = json.loads(cleaned)
            entries = data.get("entries", [])
            
            self.console.print(f"[green]Generated {len(entries)} lorebook entries.[/green]")
            return entries
            
        except (json.JSONDecodeError, AttributeError) as e:
            self.console.print(f"[yellow]Warning: Could not parse generated lorebook entries: {e}[/yellow]")
            return []

    def _load_or_create_lorebook(self, path: Path, book_idea: str | None = None) -> dict | None:
        """
        Load existing lorebook or create new one with auto-generated entries.
        
        Args:
            path: Path to lorebook file
            book_idea: Optional book idea to generate entries from
        """
        # The path is now already pointing to the correct location (lorebooks/ directory)
        # since main.py handles the directory creation and path construction
        
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.console.print(f"[green]Loaded existing lorebook: {path}[/green]")
                return data
            except (json.JSONDecodeError, IOError) as e:
                self.console.print(f"[red]Error loading lorebook: {e}[/red]")
                if not Confirm.ask("Create new lorebook instead?"):
                    return None
        
        # Create new lorebook
        self.console.print(f"[blue]Creating new lorebook: {path}[/blue]")
        
        lorebook_data = {
            "entries": [],
            "name": path.stem,
            "description": "Fiction Fabricator Lorebook"
        }
        
        # Auto-generate entries if book_idea is provided
        if book_idea and Confirm.ask(
            "[yellow]Would you like to auto-generate lorebook entries from your story idea?[/yellow]",
            default=True
        ):
            generated_entries = self._generate_lorebook_entries(book_idea)
            if generated_entries:
                lorebook_data["entries"] = generated_entries
                self.console.print("[green]Lorebook initialized with generated entries.[/green]")
                self.console.print("[cyan]You can now review, edit, add, or remove entries.[/cyan]")
        
        return lorebook_data

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
            # Show full content without truncation so users can see complete descriptions
            self.console.print(f"    Content: {content}\n")

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
        
        # Show current content
        self.console.print(Panel(
            current_content,
            title="[bold yellow]Current Content[/bold yellow]",
            border_style="yellow"
        ))
        
        self.console.print("\n[cyan]Requesting LLM to condense this content...[/cyan]")
        
        condensed_content = self._llm_condense_entry_content(title, current_content)
        
        if not condensed_content:
            self.console.print("[red]Failed to generate condensed content.[/red]")
            return
        
        if condensed_content == current_content:
            self.console.print("[yellow]LLM returned the same content - no condensing performed.[/yellow]")
            return
        
        # Show the condensed version
        self.console.print(Panel(
            condensed_content,
            title="[bold green]Condensed Content[/bold green]",
            border_style="green"
        ))
        
        # Show comparison stats
        original_length = len(current_content)
        condensed_length = len(condensed_content)
        reduction_percent = ((original_length - condensed_length) / original_length) * 100 if original_length > 0 else 0
        
        self.console.print(f"\n[dim]Original: {original_length} characters | Condensed: {condensed_length} characters | Reduction: {reduction_percent:.1f}%[/dim]")
        
        if Confirm.ask("\nUse condensed version?"):
            entry["content"] = condensed_content
            self.console.print(f"[green]Condensed entry: {title}[/green]")
        else:
            self.console.print("[dim]Keeping original content.[/dim]")

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

Remove redundancy and verbose descriptions while keeping the content informative and useful for writers.
Make the condensed version noticeably shorter than the original while retaining all critical information.

Return ONLY the condensed content, no explanations or meta-commentary."""

        try:
            response = self.llm.get_response(prompt, "Condensing lorebook entry", allow_stream=False)
            if response and response.strip():
                condensed = response.strip()
                # Basic validation - make sure it's actually shorter
                if len(condensed) < len(current_content):
                    return condensed
                else:
                    self.console.print("[yellow]Warning: LLM did not reduce content length significantly.[/yellow]")
                    return condensed
            return current_content
        except Exception as e:
            self.console.print(f"[red]Error condensing content: {e}[/red]")
            return current_content
        except Exception as e:
            self.console.print(f"[red]Error condensing content: {e}[/red]")
            return current_content

    def _save_lorebook(self, path: Path, lorebook_data: dict):
        """Save the lorebook data to file."""
        try:
            # The path is already correctly pointing to lorebooks/ directory
            # since main.py handles the directory creation and path construction
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(lorebook_data, f, indent=2, ensure_ascii=False)
            self.console.print(f"[green]Lorebook saved to: {path}[/green]")
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
        
        # Offer lorebook selection if none was provided via CLI
        if not self.lorebook_data:
            lorebook_path, is_import = ui.prompt_for_lorebook_creation_or_import()
            if lorebook_path:
                self.lorebook_data = self._load_lorebook(lorebook_path)
        
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
