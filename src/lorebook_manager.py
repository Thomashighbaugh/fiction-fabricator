"""
Lorebook management functionality extracted from Orchestrator.

Handles creation, modification, and AI-powered lorebook operations.
"""

import json
import re
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt

from src import ui
from src.exceptions import LorebookError
from src.logger import logger


class LorebookManager:
    """Manager for lorebook operations and AI-powered enhancements."""

    def __init__(self, llm, console: Console):
        """
        Initialize the LorebookManager.

        Args:
            llm: LLM client for AI-powered lorebook operations
            console: Rich console for output
        """
        self.llm = llm
        self.console = console

    def show_lorebook_menu(self) -> None:
        """Displays the lorebook management menu."""

        self.console.print(
            Panel(
                "[bold cyan]Lorebook Management[/bold cyan]\n"
                "Create, modify, or delete lorebooks for your projects.",
                title="Fiction Fabricator",
                border_style="cyan",
            )
        )

        while True:
            choice = ui.bullet_choice(
                "Select option:",
                [
                    "1. Create a new lorebook",
                    "2. Modify an existing lorebook",
                    "3. Delete a lorebook",
                    "4. Return to Editing Menu",
                ],
            )
            choice_num = choice[0]  # Extract the number from the choice

            if choice_num == "1":
                self._create_new_lorebook()
            elif choice_num == "2":
                self._modify_existing_lorebook()
            elif choice_num == "3":
                self._delete_lorebook()
            elif choice_num == "4":
                break

    def _create_new_lorebook(self) -> None:
        """Create a new lorebook file."""
        lorebooks_dir = Path("lorebooks")
        lorebooks_dir.mkdir(exist_ok=True)

        self.console.print("\n[bold]Create New Lorebook[/bold]")

        lorebook_name = Prompt.ask(
            "[cyan]Enter name for the new lorebook[/cyan]", default="lorebook"
        ).strip()

        if not lorebook_name:
            self.console.print("[red]Name cannot be empty.[/red]")
            return

        if not lorebook_name.endswith(".json"):
            lorebook_name += ".json"

        lorebook_path = lorebooks_dir / lorebook_name

        if lorebook_path.exists():
            if not Confirm.ask(
                f"[yellow]Lorebook '{lorebook_name}' already exists. Overwrite?[/yellow]"
            ):
                return

        self.console.print(f"[green]Creating lorebook: {lorebook_path}[/green]")
        self.manage_lorebook(str(lorebook_path))

    def _modify_existing_lorebook(self) -> None:
        """Modify an existing lorebook."""
        self.console.print("\n[bold]Modify Existing Lorebook[/bold]")

        lorebooks_dir = Path("lorebooks")
        lorebook_files = []

        if lorebooks_dir.exists():
            lorebook_files = sorted(lorebooks_dir.glob("*.json"))

        if not lorebook_files:
            self.console.print("[yellow]No lorebooks found in lorebooks/ directory.[/yellow]")
            self.console.print("[dim]Use 'Create a new lorebook' to create one.[/dim]")
            return

        self.console.print("\n[bold]Available Lorebooks:[/bold]")
        menu_choices = []
        for i, file in enumerate(lorebook_files, 1):
            menu_choices.append(f"{i}. {file.name}")

        menu_choices.append(f"{len(menu_choices) + 1}. Cancel")

        selected = ui.bullet_choice("Select a lorebook to modify:", menu_choices)

        selected_num = int(selected.split(".")[0])

        if selected_num > len(lorebook_files):
            self.console.print("[dim]Cancelled.[/dim]")
            return

        selected_lorebook = lorebook_files[selected_num - 1]
        self.console.print(f"[green]Opening: {selected_lorebook.name}[/green]")
        self.manage_lorebook(str(selected_lorebook))

    def _delete_lorebook(self) -> None:
        """Delete a lorebook file."""
        self.console.print("\n[bold]Delete Lorebook[/bold]")

        lorebooks_dir = Path("lorebooks")
        lorebook_files = []

        if lorebooks_dir.exists():
            lorebook_files = sorted(lorebooks_dir.glob("*.json"))

        if not lorebook_files:
            self.console.print("[yellow]No lorebooks found in lorebooks/ directory.[/yellow]")
            return

        self.console.print("\n[bold]Available Lorebooks:[/bold]")
        menu_choices = []
        for i, file in enumerate(lorebook_files, 1):
            menu_choices.append(f"{i}. {file.name}")

        menu_choices.append(f"{len(menu_choices) + 1}. Cancel")

        selected = ui.bullet_choice("Select a lorebook to delete:", menu_choices)

        selected_num = int(selected.split(".")[0])

        if selected_num > len(lorebook_files):
            self.console.print("[dim]Cancelled.[/dim]")
            return

        selected_lorebook = lorebook_files[selected_num - 1]

        if Confirm.ask(
            f"[red]Are you sure you want to delete '{selected_lorebook.name}'?[/red]",
            default=False,
        ):
            selected_lorebook.unlink()
            self.console.print(f"[green]Deleted: {selected_lorebook.name}[/green]")
        else:
            self.console.print("[dim]Deletion cancelled.[/dim]")

    def manage_lorebook(self, lorebook_path: str) -> None:
        """Interactive lorebook management interface."""

        path = Path(lorebook_path)
        lorebook_data = self._load_or_create_lorebook(path)

        if not lorebook_data:
            return

        self.console.print(
            Panel(
                f"[bold green]Lorebook Manager[/bold green]\n" f"File: {path.name}",
                title="Fiction Fabricator",
            )
        )

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
                    "8. Exit without saving",
                ],
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

    def generate_lorebook_entries(self, book_idea: str) -> list:
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
            cleaned = re.sub(
                r"^```json\s*|\s*```$", "", response.strip(), flags=re.IGNORECASE | re.MULTILINE
            )
            data = json.loads(cleaned)
            entries = data.get("entries", [])

            self.console.print(f"[green]Generated {len(entries)} lorebook entries.[/green]")
            return entries

        except (json.JSONDecodeError, AttributeError) as e:
            logger.error(f"Failed to parse lorebook entries: {e}", exc_info=True)
            self.console.print(
                f"[yellow]Warning: Could not parse generated lorebook entries: {e}[/yellow]"
            )
            return []

    def _load_or_create_lorebook(self, path: Path, book_idea: str | None = None) -> dict | None:
        """
        Load existing lorebook or create new one with auto-generated entries.

        Args:
            path: Path to lorebook file
            book_idea: Optional book idea to generate entries from
        """
        if path.exists():
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                self.console.print(f"[green]Loaded existing lorebook: {path}[/green]")
                return data
            except (OSError, json.JSONDecodeError) as e:
                logger.error(f"Error loading lorebook {path}: {e}", exc_info=True)
                self.console.print(f"[red]Error loading lorebook: {e}[/red]")
                if not Confirm.ask("Create new lorebook instead?"):
                    return None

        # Create new lorebook
        self.console.print(f"[blue]Creating new lorebook: {path}[/blue]")

        lorebook_data = {
            "entries": [],
            "name": path.stem,
            "description": "Fiction Fabricator Lorebook",
        }

        # Auto-generate entries if book_idea is provided
        if book_idea and Confirm.ask(
            "[yellow]Would you like to auto-generate lorebook entries from your story idea?[/yellow]",
            default=True,
        ):
            generated_entries = self.generate_lorebook_entries(book_idea)
            if generated_entries:
                lorebook_data["entries"] = generated_entries
                self.console.print("[green]Lorebook initialized with generated entries.[/green]")
                self.console.print("[cyan]You can now review, edit, add, or remove entries.[/cyan]")

        return lorebook_data

    def _list_lorebook_entries(self, lorebook_data: dict) -> None:
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

    def _add_lorebook_entry(self, lorebook_data: dict) -> None:
        """Add a new entry to the lorebook with LLM assistance."""
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
            "disable": False,
        }

        lorebook_data.setdefault("entries", []).append(new_entry)
        self.console.print(f"[green]Added entry: {title}[/green]")

    def _edit_lorebook_entry(self, lorebook_data: dict) -> None:
        """Edit an existing lorebook entry."""
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
        except (ValueError, KeyboardInterrupt, EOFError):
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

    def _remove_lorebook_entry(self, lorebook_data: dict) -> None:
        """Remove an entry from the lorebook."""
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
        except (ValueError, KeyboardInterrupt, EOFError):
            return

        entry = entries[index]
        title = entry.get("comment", entry.get("title", f"Entry {index+1}"))

        if Confirm.ask(f"Remove entry '{title}'?"):
            entries.pop(index)
            self.console.print(f"[green]Removed entry: {title}[/green]")

    def _condense_lorebook_entry(self, lorebook_data: dict) -> None:
        """Use LLM to condense an entry's content."""
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
        except (ValueError, KeyboardInterrupt, EOFError):
            return

        entry = entries[index]
        current_content = entry.get("content", "")

        if not current_content:
            self.console.print("[yellow]Entry has no content to condense.[/yellow]")
            return

        title = entry.get("comment", entry.get("title", "Entry"))
        self.console.print(f"\n[bold]Condensing: {title}[/bold]")

        # Show current content
        self.console.print(
            Panel(
                current_content,
                title="[bold yellow]Current Content[/bold yellow]",
                border_style="yellow",
            )
        )

        self.console.print("\n[cyan]Requesting LLM to condense this content...[/cyan]")

        condensed_content = self._llm_condense_entry_content(title, current_content)

        if not condensed_content:
            self.console.print("[red]Failed to generate condensed content.[/red]")
            return

        if condensed_content == current_content:
            self.console.print(
                "[yellow]LLM returned the same content - no condensing performed.[/yellow]"
            )
            return

        # Show the condensed version
        self.console.print(
            Panel(
                condensed_content,
                title="[bold green]Condensed Content[/bold green]",
                border_style="green",
            )
        )

        # Show comparison stats
        original_length = len(current_content)
        condensed_length = len(condensed_content)
        reduction_percent = (
            ((original_length - condensed_length) / original_length) * 100
            if original_length > 0
            else 0
        )

        self.console.print(
            f"\n[dim]Original: {original_length} characters | Condensed: {condensed_length} characters | Reduction: {reduction_percent:.1f}%[/dim]"
        )

        if Confirm.ask("\nUse condensed version?"):
            entry["content"] = condensed_content
            self.console.print(f"[green]Condensed entry: {title}[/green]")
        else:
            self.console.print("[dim]Keeping original content.[/dim]")

    def _expand_lorebook_entry(self, lorebook_data: dict) -> None:
        """Use LLM to expand an entry's content."""
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
        except (ValueError, KeyboardInterrupt, EOFError):
            return

        entry = entries[index]
        current_content = entry.get("content", "")

        if not current_content:
            self.console.print("[yellow]Entry has no content to expand.[/yellow]")
            return

        title = entry.get("comment", entry.get("title", "Entry"))
        self.console.print(f"\n[bold]Expanding: {title}[/bold]")

        expanded_content = self._llm_expand_entry_content(
            title, entry.get("keys", []), current_content
        )

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
            logger.error(f"Error expanding lorebook content: {e}", exc_info=True)
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
            response = self.llm.get_response(
                prompt, "Condensing lorebook entry", allow_stream=False
            )
            if response and response.strip():
                condensed = response.strip()
                # Basic validation - make sure it's actually shorter
                if len(condensed) < len(current_content):
                    return condensed
                else:
                    self.console.print(
                        "[yellow]Warning: LLM did not reduce content length significantly.[/yellow]"
                    )
                    return condensed
            return current_content
        except Exception as e:
            logger.error(f"Error condensing lorebook content: {e}", exc_info=True)
            self.console.print(f"[red]Error condensing content: {e}[/red]")
            return current_content

    def _save_lorebook(self, path: Path, lorebook_data: dict) -> None:
        """Save the lorebook data to file."""
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(lorebook_data, f, indent=2, ensure_ascii=False)
            self.console.print(f"[green]Lorebook saved to: {path}[/green]")
        except OSError as e:
            logger.error(f"Error saving lorebook {path}: {e}", exc_info=True)
            self.console.print(f"[red]Error saving lorebook: {e}[/red]")
            raise LorebookError(f"Failed to save lorebook: {e}") from e
