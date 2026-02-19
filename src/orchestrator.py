"""
orchestrator.py - The main workflow controller for the Fiction Fabricator application.
"""

import copy
import json
import re
import xml.etree.ElementTree as ET
from html import escape
from pathlib import Path

from rich.panel import Panel
from rich.prompt import Confirm

from src import config, ui, utils
from src.exceptions import LorebookLoadError, ProjectError, XMLParseError
from src.export_manager import ExportManager
from src.exporters import epub, html, markdown, pdf, txt
from src.generators import novel, short_story
from src.llm_client import LLMClient
from src.logger import get_logger
from src.lorebook_manager import LorebookManager
from src.project import Project
from src.prompt_enhancer import PromptEnhancer

logger = get_logger(__name__)


class Orchestrator:
    """Orchestrates the entire novel generation process."""

    def __init__(
        self, project: Project, llm_client: LLMClient, lorebook_path: str | None = None
    ) -> None:
        self.project = project
        self.llm = llm_client
        self.console = ui.console
        self.lorebook_data = self._load_lorebook(lorebook_path) if lorebook_path else None

        self.export_manager = ExportManager(self.project, self.console)
        self.lorebook_manager = LorebookManager(self.llm, self.console)
        self.prompt_enhancer = PromptEnhancer(self.llm, self.console, self)

    def _load_lorebook(self, lorebook_path: str) -> dict | None:
        """Loads and parses a Tavern AI format lorebook JSON file."""
        path = Path(lorebook_path)
        try:
            if not path.exists():
                raise LorebookLoadError(f"Lorebook file not found: {path}")

            with open(path, encoding="utf-8") as f:
                lorebook_data = json.load(f)

            self.console.print(f"[green]Loaded lorebook: {path.name}[/green]")
            return lorebook_data

        except LorebookLoadError as e:
            logger.warning(str(e))
            self.console.print(f"[yellow]Warning: {e}[/yellow]")
            return None
        except (OSError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load lorebook from {path}: {e}", exc_info=True)
            self.console.print(f"[red]Error loading lorebook: {e}[/red]")
            return None

    def _extract_lorebook_context(self, text: str) -> str:
        """Extracts relevant lorebook entries based on keywords found in the text."""
        if not self.lorebook_data:
            return ""

        # Extract entries from lorebook structure
        entries = []
        if "entries" in self.lorebook_data:
            entries_data = self.lorebook_data["entries"]
            # Handle both dict (TavernAI format with IDs as keys) and list formats
            if isinstance(entries_data, dict):
                entries = list(entries_data.values())
            elif isinstance(entries_data, list):
                entries = entries_data
        elif isinstance(self.lorebook_data, list):
            entries = self.lorebook_data
        elif "worldInfos" in self.lorebook_data:
            entries = self.lorebook_data["worldInfos"]

        if not entries:
            return ""

        relevant_entries = []
        text_lower = text.lower()

        for entry in entries:
            # Skip non-dict entries
            if not isinstance(entry, dict):
                continue

            # Skip disabled entries
            if entry.get("disable", False) or not entry.get("enable", True):
                continue

            # Check for keywords (supports both "keys" and "key" fields)
            keys = entry.get("keys", entry.get("key", []))
            if isinstance(keys, str):
                keys = [k.strip() for k in keys.split(",")]
            elif not isinstance(keys, list):
                keys = []

            # Check if any keyword matches
            matches = any(
                key.lower() in text_lower for key in keys if isinstance(key, str) and key.strip()
            )

            if matches:
                content = entry.get("content", "").strip()
                if content:
                    relevant_entries.append(
                        {
                            "title": entry.get("comment", entry.get("title", "Entry")),
                            "content": content,
                        }
                    )

        if not relevant_entries:
            return ""

        # Format the lorebook context
        context_parts = ["## Lorebook Context\n"]
        for entry in relevant_entries:
            context_parts.append(f"**{entry['title']}:**\n{entry['content']}\n")

        return "\n".join(context_parts)

    def run(self) -> None:
        """The main execution flow of the application."""
        # Step 1: Outline Generation
        if not self._has_full_outline():
            self.console.print(
                "[yellow]Outline is incomplete. Running outline generation.[/yellow]"
            )
            if not self.run_outline_generation():
                self.console.print(
                    "[bold red]Outline generation failed. Cannot proceed.[/bold red]"
                )
                return
        else:
            self.console.print("[green]Existing full outline loaded.[/green]")
            ui.display_summary(self.project)
            if Confirm.ask(
                "[yellow]Regenerate outline? (This replaces existing structure)[/yellow]",
                default=False,
            ):
                if not self.run_outline_generation():
                    self.console.print("[bold red]Outline re-generation failed.[/bold red]")

        # Step 2: Manage Outline Chapters (Edit/Add/Delete)
        if Confirm.ask(
            "\n[yellow]Would you like to review and edit the chapter outline?[/yellow]",
            default=True,
        ):
            ui.manage_outline_chapters(self.project)

        # Step 3: Review and Modify Story Elements
        modified_elements = ui.review_and_modify_story_elements(self.project)
        if modified_elements:
            self._update_story_elements(modified_elements)

        # Step 4: Content Generation
        if Confirm.ask(
            "\n[yellow]Proceeding to Chapter/Scene Content Generation. Confirm?[/yellow]",
            default=True,
        ):
            self.run_content_generation()

        # Step 5: Editing
        if Confirm.ask(
            "\n[yellow]Content generation complete. Proceed to Editing?[/yellow]", default=True
        ):
            self.run_editing_loop()
            self.run_editing_loop()

        # Step 5.1: LLM Edit Suggestions (run once, auto-apply)
        if Confirm.ask(
            "[yellow]Ask LLM for overall manuscript editing suggestions?[/yellow]", default=False
        ):
            self._edit_suggest_edits()

        # Step 5.2: Engagement Optimization
        if self.project.book_root is not None:
            if Confirm.ask(
                "[yellow]Run engagement optimization on generated chapters?[/yellow]", default=True
            ):
                all_chapters = self.project.book_root.findall(".//chapter")
                self._run_engagement_optimization(all_chapters)

        self.console.print(
            Panel("[bold green]📚 Fiction Fabricator session finished. 📚[/bold green]")
        )

    def setup_new_project(self, idea: str) -> bool:
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
                            if Confirm.ask(
                                "[yellow]Would you like to review and edit the generated lorebook entries now?[/yellow]",
                                default=True,
                            ):
                                self.manage_lorebook(str(path))
                                # Reload the potentially modified lorebook
                                self.lorebook_data = self._load_lorebook(str(path))

        # 1. Get initial title and synopsis
        title, synopsis = self._generate_initial_summary(idea)
        if not title or not synopsis:
            self.console.print(
                "[bold red]Could not generate initial title and synopsis. Exiting.[/bold red]"
            )
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
        response_json_str = self.llm.get_response(
            prompt, "Generating Title/Synopsis", allow_stream=False
        )
        if not response_json_str:
            return None, None

        try:
            cleaned_json_str = re.sub(
                r"^```json\s*|\s*```$",
                "",
                response_json_str.strip(),
                flags=re.IGNORECASE | re.MULTILINE,
            )
            data = json.loads(cleaned_json_str)
            return data.get("title"), data.get("synopsis")
        except (json.JSONDecodeError, AttributeError):
            self.console.print(
                "[yellow]Warning: Could not parse title/synopsis JSON from LLM.[/yellow]"
            )
            return "Untitled Project", "Synopsis pending."

    def _has_full_outline(self) -> bool:
        """Checks if the project appears to have a complete outline."""
        if not self.project.book_root:
            return False

        chapters = self.project.book_root.findall(".//chapter")
        characters = self.project.book_root.findall(".//character")
        has_summaries = any(c.findtext("summary", "").strip() for c in chapters)

        return bool(chapters and characters and has_summaries)

    def _update_story_elements(self, modified_elements: dict) -> None:
        """
        Updates the story_elements in the project XML with user modifications.

        Args:
            modified_elements: Dictionary with title, genre, tone, perspective, target_audience,
                              and optionally character_names (a dict of char_id -> new_name)
        """
        if not self.project.book_root:
            self.console.print("[red]Error: No book root found.[/red]")
            return

        # Handle title separately as it's a direct child of book_root
        if "title" in modified_elements:
            title_element = self.project.book_root.find("title")
            if title_element is not None:
                title_element.text = str(modified_elements["title"])
            else:
                ET.SubElement(self.project.book_root, "title").text = str(
                    modified_elements["title"]
                )

        # Handle story_elements
        story_elements = self.project.book_root.find("story_elements")
        if story_elements is None:
            self.console.print(
                "[yellow]Warning: story_elements not found in project. Creating new section.[/yellow]"
            )
            story_elements = ET.SubElement(self.project.book_root, "story_elements")

        # Handle character names separately (not a story element)
        if "character_names" in modified_elements:
            character_names = modified_elements["character_names"]
            characters = self.project.book_root.find("characters")
            if characters is not None:
                for char in characters.findall("character"):
                    char_id = char.get("id")
                    if char_id in character_names:
                        name_elem = char.find("name")
                        if name_elem is not None:
                            name_elem.text = str(character_names[char_id])
                        else:
                            ET.SubElement(char, "name").text = str(character_names[char_id])
                self.console.print(
                    f"[green]Updated {len(character_names)} character name(s).[/green]"
                )

        # Update or create each story element (except title and character_names)
        for key, value in modified_elements.items():
            if key in ("title", "character_names"):
                continue  # Already handled above
            element = story_elements.find(key)
            if element is not None:
                element.text = str(value)
            else:
                ET.SubElement(story_elements, key).text = str(value)

        # Save the updated project
        if self.project.save_state("outline.xml"):
            self.console.print("[green]Story elements updated and saved.[/green]")
        else:
            self.console.print("[yellow]Warning: Could not save updated story elements.[/yellow]")

    def run_outline_generation(self) -> bool:
        """Executes the outline generation step."""
        generator = (
            novel if getattr(self.project, "story_type", "novel") == "novel" else short_story
        )

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

        new_book_root = utils.parse_xml_string(
            response_xml_str, self.console, expected_root_tag="book"
        )
        if new_book_root is None or new_book_root.tag != "book":
            self.console.print(
                "[bold red]Failed to parse generated outline or root tag was not <book>.[/bold red]"
            )
            self.console.print("[yellow]This may be due to:[/yellow]")
            self.console.print("  1. LLM response was truncated (hit token limit)")
            self.console.print("  2. LLM generated invalid XML")
            self.console.print("  3. LLM included text before/after the XML")

            # Save the failed response for debugging
            if self.project.book_dir:
                debug_file = self.project.book_dir / "failed_outline_response.xml"
                try:
                    with open(debug_file, "w", encoding="utf-8") as f:
                        f.write(response_xml_str)
                    self.console.print(
                        f"\n[dim]Debug: Raw LLM response saved to {debug_file.name}[/dim]"
                    )
                except Exception as e:
                    self.console.print(f"[dim]Could not save debug file: {e}[/dim]")

            self.console.print("\n[cyan]You can:[/cyan]")
            self.console.print("  - Try again (the LLM may generate valid XML on retry)")
            self.console.print("  - Use a shorter initial idea/prompt")
            self.console.print("  - Request fewer chapters")
            return False

        # Simple validation and replacement
        self.project.book_root = new_book_root
        if self.project.save_state("outline.xml"):
            self.console.print("[green]Full outline generated and saved as outline.xml[/green]")
            ui.display_summary(self.project)
            return True
        return False

    def run_content_generation(self) -> None:
        """Generates content for batches of chapters/scenes."""
        self.console.print(Panel("Generating Chapter/Scene Content", style="bold blue"))
        # Don't clear chapters_generated_in_session for resumed projects - it was restored during loading

        while True:
            chapters_to_generate = self._select_chapters_to_generate(batch_size=1)
            if not chapters_to_generate:
                self.console.print(
                    "[bold green]\nAll chapters/scenes appear to have content![/bold green]"
                )
                break

            ids_str = ", ".join(
                [utils.get_chapter_id_with_default(c) for c in chapters_to_generate]
            )

            chapter_details = "".join(
                f'- Chapter {c.findtext("number", "N/A")} (ID: {utils.get_chapter_id(c)}): "{c.findtext("title", "N/A")}"\n  Summary: {c.findtext("summary", "N/A")}\n'
                for c in chapters_to_generate
            )

            # Extract lorebook context from chapter summaries and titles
            context_text = " ".join(
                [
                    c.findtext("title", "") + " " + c.findtext("summary", "")
                    for c in chapters_to_generate
                ]
            )
            lorebook_context = self._extract_lorebook_context(context_text)

            prompt = f"""
You are a novelist continuing a story. Write the full prose for the following {len(chapters_to_generate)} chapters/scenes based on their summaries and the full book context.
Aim for substantial, detailed chapters (3000-6000 words per chapter).

Chapters/Scenes to write:
{chapter_details}

{lorebook_context}

IMPORTANT: Keep the narrative grounded in the setting described in each chapter's `setting` attribute. This keeps the scene focused and prevents setting drift.

Output ONLY an XML `<patch>` containing a `<chapter>` for each requested ID. Each chapter must:
- Include the `setting` attribute from the outline (e.g., <chapter id="1" setting="The dark forest near the village">)
- Have a `<content>` tag filled with sequentially ID'd `<paragraph>` tags
- Stay true to the setting description throughout the chapter

Full Book Context:
```xml
{ET.tostring(self.project.book_root, encoding="unicode")}
```
"""
            patch_xml = self.llm.get_response(prompt, f"Writing chapters {ids_str}")
            if patch_xml and self.project.apply_patch(patch_xml):
                patch_num = utils.get_next_patch_number(self.project.book_dir)
                self.project.save_state(f"patch-{patch_num:02d}.xml")
                ui.display_summary(self.project)
            else:
                self.console.print(
                    f"[bold red]Failed to apply patch for batch {ids_str}.[/bold red]"
                )
                if not Confirm.ask("[yellow]Continue to the next batch?[/yellow]", default=True):
                    break

    def _select_chapters_to_generate(self, batch_size=2) -> list:
        """Selects the next batch of chapters to write using a fill-gaps strategy."""
        all_chapters = sorted(
            self.project.book_root.findall(".//chapter"),
            key=lambda c: int(utils.get_chapter_id_with_default(c, "0")),
        )

        chapters_needing_content = []
        for chap in all_chapters:
            paras = chap.findall(".//paragraph")
            if not any(p.text and p.text.strip() for p in paras):
                chapters_needing_content.append(chap)

        return chapters_needing_content[:batch_size]

    def run_editing_loop(self) -> None:
        """Runs the interactive editing menu loop."""
        self.console.print(Panel("Interactive Editing Mode", style="bold blue"))

        edit_options = {
            "1": ("Make Chapter(s) Longer", self._edit_make_longer),
            "2": ("Make All Chapters Longer", self._edit_make_all_chapters_longer),
            "3": (
                "Rewrite Chapter (with instructions)",
                lambda: self._edit_rewrite_chapter(blackout=False),
            ),
            "4": (
                "Rewrite Chapter (Fresh Rewrite)",
                lambda: self._edit_rewrite_chapter(blackout=True),
            ),
            "5": ("Ask LLM for Edit Suggestions", self._edit_suggest_edits),
            "6": ("Manage Lorebooks", self.lorebook_manager.show_lorebook_menu),
            "7": ("Export Menu", self.export_manager.show_export_menu),
            "8": ("Quit Editing", None),
        }

        while True:
            ui.display_summary(self.project)
            choice = ui.display_menu("Editing Options", edit_options)

            handler = edit_options.get(choice)[1]
            if handler:
                handler()
            else:  # Quit
                break

    def _handle_patch_result(self, patch_xml: str | None, operation_desc: str) -> None:
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

    def _handle_patch_result_auto(self, patch_xml: str | None, operation_desc: str) -> None:
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
            return ET.tostring(reduced_book, encoding="unicode")

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

        return ET.tostring(reduced_book, encoding="unicode")

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
            return ET.tostring(enhanced_book, encoding="unicode")

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
                            first_para.text = (
                                (paragraphs[0].text or "")[:300] + "..."
                                if len(paragraphs[0].text or "") > 300
                                else paragraphs[0].text
                            )

                        # Add last paragraph for lead-out context (if different from first)
                        if len(paragraphs) > 1:
                            last_para = ET.SubElement(context_content, "closing")
                            last_para.text = (
                                (paragraphs[-1].text or "")[:300] + "..."
                                if len(paragraphs[-1].text or "") > 300
                                else paragraphs[-1].text
                            )

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

        return ET.tostring(enhanced_book, encoding="unicode")

    def _edit_make_longer(self) -> None:
        """Handler for making chapters longer."""
        chapters = ui.get_chapter_selection(
            self.project, "Enter chapter ID(s) to make longer", allow_multiple=True
        )
        if not chapters:
            return

        word_count = ui.IntPrompt.ask(
            "[yellow]Enter target word count per chapter[/yellow]", default=4500
        )

        # For multiple chapters, notify user that patches will be auto-applied
        if len(chapters) > 1:
            self.console.print(
                f"[yellow]Auto-applying patches for {len(chapters)} chapters (no confirmations)...[/yellow]"
            )

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

Keep the narrative grounded in the setting described in the chapter's `setting` attribute to prevent setting drift.

Output an XML `<patch>` with the expanded `<chapter>` content that preserves all key story elements while making them richer and more detailed. Make sure to include the `setting` attribute in the chapter tag.

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

    def _edit_make_all_chapters_longer(self) -> None:
        """Handler for making all chapters longer automatically."""
        # Check if book_root exists
        if not self.project.book_root:
            self.console.print("[red]No project loaded.[/red]")
            return

        # Get all chapters from the project
        chapters = sorted(
            self.project.book_root.findall(".//chapter"),
            key=lambda c: int(utils.get_chapter_id_with_default(c, "0")),
        )

        if not chapters:
            self.console.print("[red]No chapters found in the project.[/red]")
            return

        word_count = ui.IntPrompt.ask(
            "[yellow]Enter target word count per chapter[/yellow]", default=4500
        )

        # Auto-apply patches for all chapters
        self.console.print(
            f"[yellow]Auto-applying patches for all {len(chapters)} chapters (no confirmations)...[/yellow]"
        )

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

Keep the narrative grounded in the setting described in the chapter's `setting` attribute to prevent setting drift.

Output an XML `<patch>` with the expanded `<chapter>` content that preserves all key story elements while making them richer and more detailed. Make sure to include the `setting` attribute in the chapter tag.

Relevant Context:
```xml
{reduced_context}
```
"""
            patch_xml = self.llm.get_response(prompt, f"Expanding chapter {chapter_id}")
            self._handle_patch_result_auto(patch_xml, f"Make Longer (Ch {chapter_id})")

    def _edit_rewrite_chapter(self, blackout: bool) -> None:
        """Handler for rewriting a chapter."""
        chapter = ui.get_chapter_selection(
            self.project, "Enter the chapter ID to rewrite", allow_multiple=False
        )
        if not chapter:
            return
        target_chapter = chapter[0]
        chapter_id = utils.get_chapter_id(target_chapter)

        instructions = ui.Prompt.ask("[yellow]Enter specific instructions for the rewrite[/yellow]")
        if not instructions.strip():
            return

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

IMPORTANT: Keep the narrative grounded in the setting described in the chapter's `setting` attribute. This keeps the scene focused and prevents setting drift.

Output an XML `<patch>` with the rewritten `<chapter>` content. Make sure to include the `setting` attribute in the chapter tag (e.g., <chapter id="{chapter_id}" setting="...">).

Full Book Context:
```xml
{ET.tostring(temp_root, encoding="unicode")}
```
"""
        patch_xml = self.llm.get_response(prompt, f"Rewriting chapter {chapter_id}")
        self._handle_patch_result(patch_xml, f"Rewrite (Ch {chapter_id})")

    def _edit_suggest_edits(self) -> None:
        """Handler for asking the LLM for edit suggestions."""
        if not self.project.book_root:
            self.console.print("[red]No book data available.[/red]")
            return

        prompt = f"""
You are an expert editor. Analyze the manuscript below and provide a numbered list of 5-10 concrete, actionable suggestions for improvement.

Full Book Context:
```xml
{ET.tostring(self.project.book_root, encoding="unicode")}
```
"""
        suggestions_text = self.llm.get_response(
            prompt, "Generating edit suggestions", allow_stream=False
        )
        if not suggestions_text:
            return

        self.console.print(
            Panel(suggestions_text, title="LLM Edit Suggestions", border_style="cyan")
        )

        # Ask if user wants to apply these suggestions to all chapters
        if Confirm.ask(
            "\n[yellow]Apply these suggestions to all chapters?[/yellow]", default=False
        ):
            self._apply_suggestions_to_all_chapters(suggestions_text)
        else:
            self.console.print(
                "\n[yellow]Use the 'Rewrite Chapter' option to implement these suggestions.[/yellow]"
            )

    def _apply_suggestions_to_all_chapters(self, suggestions_text: str) -> None:
        """Apply LLM suggestions to all chapters in the manuscript."""
        chapters = sorted(
            self.project.book_root.findall(".//chapter"),
            key=lambda c: int(utils.get_chapter_id_with_default(c, "0")),
        )

        if not chapters:
            self.console.print("[yellow]No chapters found to apply suggestions to.[/yellow]")
            return

        self.console.print(
            f"[bold yellow]Applying advice to {len(chapters)} chapters...[/bold yellow]"
        )
        self.console.print(
            "[dim]This will auto-apply patches without individual confirmations.[/dim]"
        )
        self.console.print(
            "[cyan]Using enhanced continuity-aware context for each chapter.[/cyan]\n"
        )

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
- Keep the narrative grounded in the setting described in the chapter's `setting` attribute to prevent setting drift

CONTEXT AWARENESS:
The enhanced context below includes surrounding chapters and narrative flow information to help you maintain continuity. Pay attention to:
- How this chapter connects to previous and following chapters
- Character states and development from previous chapters
- Ongoing plot threads and story elements that must be preserved
- Tone and style consistency with the broader narrative

Output format: Return ONLY an XML `<patch>` containing a `<chapter>` element with the complete updated content. Use this EXACT format and include the `setting` attribute:

<patch>
  <chapter id="{chapter_id}" setting="...">
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
        self.console.print(
            "\n[bold green]Manuscript-wide advice application complete![/bold green]"
        )
        self.console.print(f"Successfully updated: {success_count}/{len(chapters)} chapters")

        if failed_chapters:
            failed_list = ", ".join(failed_chapters)
            self.console.print(f"[yellow]Failed chapters: {failed_list}[/yellow]")
            self.console.print(
                "[dim]You can try applying advice to failed chapters individually using 'Rewrite Chapter'.[/dim]"
            )
        else:
            self.console.print(
                "[bold cyan]All chapters updated with continuity-aware context! ✨[/bold cyan]"
            )
            self.console.print(
                "[dim]Inter-chapter narrative flow and character consistency have been preserved.[/dim]"
            )
