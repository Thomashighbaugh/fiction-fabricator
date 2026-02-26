"""
export_manager.py - Manages all export operations for the Fiction Fabricator.

Extracted from Orchestrator to improve code organization and maintainability.
"""

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from src import config, ui
from src.exporters import epub, html, markdown, pdf, txt
from src.logger import get_logger
from src.project import Project

logger = get_logger(__name__)


class ExportManager:
    """Handles all export-related operations including format selection and frontmatter editing."""

    def __init__(self, project: Project, console: Console) -> None:
        """
        Initialize the export manager.

        Args:
            project: The Project instance containing book data
            console: Rich console for output
        """
        self.project = project
        self.console = console
        self.selected_font: str | None = None
        self.selected_font_url: str | None = None

    def show_export_menu(self) -> None:
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

    def _edit_frontmatter_menu(self) -> None:
        """Displays the frontmatter editing menu."""
        from src import utils

        frontmatter_options = {
            "1": ("Edit Author Name", lambda: self._edit_author_name()),
            "2": ("Edit Book Title", lambda: self._edit_book_title()),
            "3": ("Edit Title Page", lambda: self._edit_frontmatter_section("title_page")),
            "4": ("Edit Copyright Page", lambda: self._edit_frontmatter_section("copyright_page")),
            "5": ("Edit Dedication", lambda: self._edit_frontmatter_section("dedication")),
            "6": (
                "Edit Acknowledgements",
                lambda: self._edit_frontmatter_section("acknowledgements"),
            ),
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

    def _edit_author_name(self) -> None:
        """Edit the author name."""
        if self.project.edit_author_name():
            self.console.print("[green]Author name updated successfully.[/green]")
        else:
            self.console.print("[dim]Author name not changed.[/dim]")

    def _edit_book_title(self) -> None:
        """Edit the book title."""
        if self.project.edit_book_title():
            self.console.print("[green]Book title updated successfully.[/green]")
        else:
            self.console.print("[dim]Book title not changed.[/dim]")

    def _edit_frontmatter_section(self, section_name: str) -> None:
        """Edit a specific frontmatter section."""
        if self.project.edit_frontmatter_section(section_name):
            self.console.print(
                f"[green]Frontmatter section '{section_name.replace('_', ' ').title()}' saved.[/green]"
            )
        else:
            self.console.print(
                f"[yellow]No changes made to frontmatter section '{section_name.replace('_', ' ').title()}'.[/yellow]"
            )

    def _select_font(self) -> None:
        """Allow the user to select a custom font for chapter headings."""
        # Display current font selection
        current_font = self.selected_font or config.DEFAULT_CHAPTER_FONT
        self.console.print(f"[dim]Current chapter heading font: {current_font}[/dim]")

        # Create font selection menu
        font_options = {
            str(i + 1): (font, None) for i, font in enumerate(config.GOOGLE_FONT_OPTIONS)
        }
        font_options[str(len(config.GOOGLE_FONT_OPTIONS) + 1)] = (
            "Use Default Font (Georgia)",
            None,
        )
        font_options[str(len(config.GOOGLE_FONT_OPTIONS) + 2)] = (
            "Enter Custom Google Font URL",
            None,
        )
        font_options[str(len(config.GOOGLE_FONT_OPTIONS) + 3)] = ("Return to Export Menu", None)

        choice = ui.display_menu("Select Chapter Heading Font", font_options)

        if choice == str(len(config.GOOGLE_FONT_OPTIONS) + 1):
            # Use default font
            self.selected_font = config.DEFAULT_CHAPTER_FONT
            self.selected_font_url = None
            self.console.print(
                f"[green]Chapter heading font set to default: {self.selected_font}[/green]"
            )
        elif choice == str(len(config.GOOGLE_FONT_OPTIONS) + 2):
            # Custom font URL
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
                    self.console.print(
                        f"[green]Chapter heading font set to: {self.selected_font}[/green]"
                    )
                else:
                    self.console.print("[red]Invalid font selection[/red]")
            except ValueError:
                self.console.print("[red]Invalid selection[/red]")

    def _export_single_md(self) -> None:
        """Export full book as a single Markdown file."""
        filename = f"{self.project.book_title_slug}-full.md"
        output_path = self.project.book_dir / filename
        markdown.export_single_markdown(self.project.book_root, output_path, self.console)

    def _export_multi_md(self) -> None:
        """Export book as multiple Markdown files (one per chapter)."""
        markdown.export_markdown_per_chapter(
            self.project.book_root,
            self.project.book_dir,
            self.project.book_title_slug,
            self.console,
        )

    def _export_single_html(self) -> None:
        """Export full book as a single HTML file."""
        filename = f"{self.project.book_title_slug}-full.html"
        output_path = self.project.book_dir / filename
        html.export_single_html(
            self.project.book_root,
            output_path,
            self.console,
            self.selected_font,
            self.selected_font_url,
        )

    def _export_multi_html(self) -> None:
        """Export book as multiple HTML files (one per chapter)."""
        html.export_html_per_chapter(
            self.project.book_root,
            self.project.book_dir,
            self.project.book_title_slug,
            self.console,
            self.selected_font,
            self.selected_font_url,
        )

    def _export_epub(self) -> None:
        """Export full book as EPUB format with optional cover image."""
        # Prompt for optional cover image
        cover_path_str = Prompt.ask(
            "[cyan]Cover image path (optional, press Enter to skip)[/cyan]",
            default="",
            show_default=False,
        )

        cover_image_path = None
        if cover_path_str.strip():
            cover_image_path = Path(cover_path_str.strip())
            if not cover_image_path.exists():
                self.console.print(
                    f"[yellow]Warning: Cover image not found at {cover_image_path}[/yellow]"
                )
                self.console.print("[yellow]Proceeding without cover image...[/yellow]")
                cover_image_path = None
            elif cover_image_path.suffix.lower() not in [
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".bmp",
                ".webp",
            ]:
                self.console.print(
                    f"[yellow]Warning: {cover_image_path} may not be a supported image format[/yellow]"
                )
                self.console.print("[yellow]Supported formats: JPG, PNG, GIF, BMP, WebP[/yellow]")

        epub.export_epub(
            self.project.book_root,
            self.project.book_dir,
            self.project.book_title_slug,
            self.console,
            cover_image_path=cover_image_path,
            custom_font_name=self.selected_font,
            custom_font_url=self.selected_font_url,
        )

    def _export_pdf(self) -> None:
        """Export full book as PDF format."""
        filename = f"{self.project.book_title_slug}-full.pdf"
        output_path = self.project.book_dir / filename
        pdf.export_pdf(
            self.project.book_root,
            output_path,
            self.console,
            self.selected_font,
            self.selected_font_url,
        )

    def _export_single_txt(self) -> None:
        """Export full book as a single text file."""
        filename = f"{self.project.book_title_slug}-full.txt"
        output_path = self.project.book_dir / filename
        txt.export_single_txt(self.project.book_root, output_path, self.console)

    def _export_multi_txt(self) -> None:
        """Export book as multiple text files (one per chapter)."""
        txt.export_txt_per_chapter(
            self.project.book_root,
            self.project.book_dir,
            self.project.book_title_slug,
            self.console,
        )

    def _export_all(self) -> None:
        """Export the book in all available formats."""
        self.console.print(
            Panel(
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
                title="Export All",
            )
        )

        if not Confirm.ask("Proceed with exporting all formats?", default=True):
            return

        # Ask for optional cover image once for EPUB
        cover_path_str = Prompt.ask(
            "[cyan]Cover image path for EPUB (optional, press Enter to skip)[/cyan]",
            default="",
            show_default=False,
        )

        cover_image_path = None
        if cover_path_str.strip():
            cover_image_path = Path(cover_path_str.strip())
            if not cover_image_path.exists():
                self.console.print(
                    f"[yellow]Warning: Cover image not found at {cover_image_path}[/yellow]"
                )
                self.console.print("[yellow]Proceeding without cover image...[/yellow]")
                cover_image_path = None
            elif cover_image_path.suffix.lower() not in [
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".bmp",
                ".webp",
            ]:
                self.console.print(
                    f"[yellow]Warning: {cover_image_path} may not be a supported image format[/yellow]"
                )

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
            epub.export_epub(
                self.project.book_root,
                self.project.book_dir,
                self.project.book_title_slug,
                self.console,
                cover_image_path=cover_image_path,
                custom_font_name=self.selected_font,
                custom_font_url=self.selected_font_url,
            )

            self.console.print("[cyan]Exporting full book (PDF)...[/cyan]")
            self._export_pdf()

            self.console.print("[cyan]Exporting full book (TXT)...[/cyan]")
            self._export_single_txt()

            self.console.print("[cyan]Exporting chapters (TXT per chapter)...[/cyan]")
            self._export_multi_txt()

            self.console.print(
                Panel(
                    "[bold green]✓ All formats exported successfully![/bold green]\n"
                    f"Files saved to: {self.project.book_dir}",
                    title="Export Complete",
                )
            )

        except Exception as e:
            logger.error(f"Export operation failed: {e}", exc_info=True)
            self.console.print(f"[bold red]Error during export: {e}[/bold red]")
            self.console.print("[yellow]Some formats may have been exported successfully.[/yellow]")
