# -*- coding: utf-8 -*-
"""
orchestrator.py - The main workflow controller for the Fiction Fabricator application.
"""
import xml.etree.ElementTree as ET
import json
import re
from html import escape

from rich.prompt import Confirm
from rich.panel import Panel

from src import ui, utils
from src.llm_client import LLMClient
from src.project import Project
from src.generators import novel, short_story
from src.exporters import markdown, epub, html

class Orchestrator:
    """Orchestrates the entire novel generation process."""

    def __init__(self, project: Project, llm_client: LLMClient):
        self.project = project
        self.llm = llm_client
        self.console = ui.console

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
        prompt = f"""
Based on the following idea, generate a compelling title and a brief 1-2 sentence synopsis.

Idea:
---
{idea}
---

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
        
        response_xml_str = generator.generate_outline(self.llm, self.project)
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
            
            prompt = f"""
You are a novelist continuing a story. Write the full prose for the following {len(chapters_to_generate)} chapters/scenes based on their summaries and the full book context.
Aim for a substantial length (1500-4000 words per chapter).

Chapters/Scenes to write:
{chapter_details}

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
    
    def _edit_make_longer(self):
        """Handler for making chapters longer."""
        chapters = ui.get_chapter_selection(self.project, "Enter chapter ID(s) to make longer", allow_multiple=True)
        if not chapters: 
            return

        word_count = ui.IntPrompt.ask("[yellow]Enter target word count per chapter[/yellow]", default=3000)
        
        # Process each chapter individually to ensure all get expanded
        for chapter in chapters:
            chapter_id = utils.get_chapter_id(chapter)
            self.console.print(f"[cyan]Expanding Chapter {chapter_id}...[/cyan]")
            
            prompt = f"""
Rewrite the content for chapter {chapter_id} to be approximately {word_count} words.
Elaborate on existing scenes, add descriptive detail, and expand dialogue. Maintain consistency.
Output an XML `<patch>` with the rewritten `<chapter>` content.

Full Book Context:
```xml
{ET.tostring(self.project.book_root, encoding='unicode')}
```
"""
            patch_xml = self.llm.get_response(prompt, f"Expanding chapter {chapter_id}")
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
