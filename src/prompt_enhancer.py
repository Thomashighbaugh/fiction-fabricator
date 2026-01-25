"""
Prompt enhancement functionality for transforming basic story ideas into detailed prompts.

Provides AI-powered prompt expansion with genre, length, and lorebook integration.
"""

import re
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from src import ui
from src.logger import logger


class PromptEnhancer:
    """Manager for AI-powered story prompt enhancement."""

    def __init__(self, llm, console: Console, orchestrator):
        """
        Initialize the PromptEnhancer.

        Args:
            llm: LLM client for prompt enhancement
            console: Rich console for output
            orchestrator: Reference to main orchestrator for project setup
        """
        self.llm = llm
        self.console = console
        self.orchestrator = orchestrator

    def create_enhanced_prompt(self, lorebook_data: dict | None = None) -> None:
        """Interactive prompt enhancement interface using LLM assistance."""
        self.console.print("\n[bold cyan]📝 Fiction Fabricator - Prompt Enhancement[/bold cyan]")
        self.console.print(
            Panel(
                "Transform your basic story idea into a comprehensive, detailed prompt\n"
                "that will help generate richer, more engaging fiction.",
                title="Prompt Enhancement",
                border_style="cyan",
            )
        )

        # Get basic idea from user
        basic_idea = Prompt.ask(
            "\n[yellow]Enter your basic story idea or concept[/yellow]", default=""
        ).strip()

        if not basic_idea:
            self.console.print("[red]No idea provided. Exiting.[/red]")
            return

        self.console.print(f"\n[dim]Your basic idea: {basic_idea}[/dim]\n")

        # Offer lorebook selection if none was provided via CLI
        if not lorebook_data:
            lorebook_path, is_import = ui.prompt_for_lorebook_creation_or_import()
            if lorebook_path:
                lorebook_data = self.orchestrator._load_lorebook(lorebook_path)

        # Get optional story preferences
        story_type = self._prompt_for_enhancement_type()
        target_length = self._prompt_for_target_length(story_type)
        genre_preference = self._prompt_for_genre_preference()

        # Add lorebook context if available
        lorebook_context = ""
        if lorebook_data:
            lorebook_context = self.orchestrator._extract_lorebook_context(basic_idea)
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
        self.console.print("\n" + "=" * 60)
        self.console.print(
            Panel(
                enhanced_prompt,
                title="[bold green]Enhanced Story Prompt[/bold green]",
                border_style="green",
            )
        )
        self.console.print("=" * 60)

        # Ask if user wants to save or use the prompt
        self._handle_enhanced_prompt_output(enhanced_prompt)

    def _prompt_for_enhancement_type(self) -> str:
        """Ask user what type of story they want to create."""
        choice = Prompt.ask(
            "\n[cyan]What type of story do you want to create?[/cyan]\n"
            "[1] Novel (longer, multi-chapter)\n"
            "[2] Short Story (shorter, focused)\n"
            "[3] Let AI decide based on the idea\n"
            "Choose option",
            choices=["1", "2", "3"],
            default="3",
        )

        if choice == "1":
            return "novel"
        elif choice == "2":
            return "short_story"
        else:
            return "auto"

    def _prompt_for_target_length(self, story_type: str) -> str:
        """Ask for target length preferences."""
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
                default="4",
            )

            length_map = {
                "1": "short novel (50k-70k words)",
                "2": "standard novel (70k-100k words)",
                "3": "long novel (100k+ words)",
                "4": "flexible",
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
                default="4",
            )

            length_map = {
                "1": "flash fiction (under 1k words)",
                "2": "short story (1k-5k words)",
                "3": "novelette (5k-15k words)",
                "4": "flexible",
            }
            return length_map.get(choice, "flexible")

    def _prompt_for_genre_preference(self) -> str:
        """Ask for genre preferences."""
        return Prompt.ask(
            "\n[cyan]Genre preference (optional)[/cyan]\n"
            "e.g., fantasy, sci-fi, mystery, romance, literary fiction, etc.\n"
            "Leave blank to let AI determine from your idea",
            default="",
        ).strip()

    def _llm_enhance_prompt(
        self,
        basic_idea: str,
        story_type: str,
        target_length: str,
        genre: str,
        lorebook_context: str,
    ) -> str:
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
            prompt_parts.extend(
                [
                    f"Target Format: Novel ({target_length})",
                    "- Focus on epic scope, multiple plot threads, character development arcs",
                    "- Include subplots, supporting characters, and world-building depth",
                    "- Consider pacing across multiple chapters",
                    "",
                ]
            )
        elif story_type == "short_story":
            prompt_parts.extend(
                [
                    f"Target Format: Short Story ({target_length})",
                    "- Focus on a single central conflict or moment of change",
                    "- Emphasize tight pacing and concentrated impact",
                    "- Limit characters and settings for focused storytelling",
                    "",
                ]
            )
        else:  # auto
            prompt_parts.extend(
                [
                    "Target Format: Let the story idea determine the best format",
                    "- Suggest whether this works better as a novel or short story",
                    "- Explain your reasoning for the format choice",
                    "",
                ]
            )

        # Add genre guidance
        if genre:
            prompt_parts.extend(
                [
                    f"Genre: {genre}",
                    f"- Incorporate typical {genre} elements, tropes, and expectations",
                    f"- Consider {genre} audience preferences and conventions",
                    "",
                ]
            )

        # Add lorebook context if available
        if lorebook_context:
            prompt_parts.extend(
                [
                    "Relevant World Context:",
                    lorebook_context,
                    "- Integrate this world-building seamlessly into the enhanced prompt",
                    "",
                ]
            )

        prompt_parts.extend(
            [
                "Write the enhanced prompt as a single, cohesive description that a fiction generator AI could use to create an engaging story.",
                "Make it detailed but not overly prescriptive - leave room for creative interpretation.",
                "Focus on inspiring rich, vivid storytelling.",
            ]
        )

        full_prompt = "\n".join(prompt_parts)

        try:
            response = self.llm.get_response(
                full_prompt, "Enhancing story prompt", allow_stream=False
            )
            return response.strip() if response else basic_idea
        except Exception as e:
            logger.error(f"Error enhancing prompt: {e}", exc_info=True)
            self.console.print(f"[red]Error enhancing prompt: {e}[/red]")
            return basic_idea

    def _handle_enhanced_prompt_output(self, enhanced_prompt: str) -> None:
        """Handle what to do with the enhanced prompt."""
        choice = Prompt.ask(
            "\n[yellow]What would you like to do with this enhanced prompt?[/yellow]\n"
            "[1] Save to a text file\n"
            "[2] Copy to clipboard (display for manual copy)\n"
            "[3] Use immediately to start generating a story\n"
            "[4] Exit without saving\n"
            "Choose option",
            choices=["1", "2", "3", "4"],
            default="1",
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

    def _save_enhanced_prompt_to_file(self, enhanced_prompt: str) -> None:
        """Save the enhanced prompt to a text file."""
        # Generate default filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"enhanced_prompt_{timestamp}.txt"

        while True:
            filename = Prompt.ask(
                "[cyan]Filename for enhanced prompt[/cyan]", default=default_filename
            )

            # Clean and validate filename
            # Remove or replace invalid characters
            clean_filename = re.sub(r'[<>:"/\\|?*]', "_", filename)

            # Truncate if too long (max 200 chars to be safe)
            if len(clean_filename) > 200:
                # Try to extract first few words as filename
                words = clean_filename.split()[:5]  # First 5 words
                clean_filename = "_".join(words) + f"_{timestamp}.txt"
                self.console.print(f"[yellow]Filename too long, using: {clean_filename}[/yellow]")

            # Ensure .txt extension
            if not clean_filename.lower().endswith(".txt"):
                clean_filename += ".txt"

            try:
                file_path = Path(clean_filename)
                file_path.write_text(enhanced_prompt, encoding="utf-8")
                self.console.print(
                    f"[green]✓ Enhanced prompt saved to: {file_path.absolute()}[/green]"
                )

                # Ask if they want to use this file to start generation
                if Confirm.ask("\nStart story generation using this prompt file?"):
                    self._start_story_generation_with_file(file_path)
                break

            except Exception as e:
                if "File name too long" in str(e) or "name too long" in str(e):
                    self.console.print(
                        "[red]Filename still too long. Please enter a shorter name.[/red]"
                    )
                    continue
                else:
                    logger.error(f"Error saving prompt file: {e}", exc_info=True)
                    self.console.print(f"[red]Error saving prompt file: {e}[/red]")
                    break

    def _start_story_generation_with_prompt(self, prompt: str) -> None:
        """Start story generation workflow with the enhanced prompt."""
        self.console.print(
            "\n[bold green]🚀 Starting story generation with enhanced prompt...[/bold green]"
        )

        # This would integrate with the main generation workflow
        if self.orchestrator.setup_new_project(prompt):
            self.orchestrator.run()

    def _start_story_generation_with_file(self, prompt_file: Path) -> None:
        """Start story generation using a prompt file."""
        self.console.print(
            f"\n[bold green]🚀 Starting story generation with prompt file: {prompt_file.name}[/bold green]"
        )

        try:
            prompt = prompt_file.read_text(encoding="utf-8")
            if self.orchestrator.setup_new_project(prompt):
                self.orchestrator.run()
        except Exception as e:
            logger.error(f"Error reading prompt file: {e}", exc_info=True)
            self.console.print(f"[red]Error reading prompt file: {e}[/red]")
