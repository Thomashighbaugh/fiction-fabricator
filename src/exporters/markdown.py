# -*- coding: utf-8 -*-
"""
markdown.py - Handles exporting the project to Markdown formats.
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from html import unescape

from rich.console import Console

from src import utils

def _get_sorted_chapters(book_root: ET.Element) -> list[ET.Element]:
    """Helper to get chapters sorted numerically by ID."""
    if book_root is None:
        return []
    chapters_raw = book_root.findall(".//chapter")
    try:
        return sorted(chapters_raw, key=lambda chap: int(chap.get("id", "0")))
    except ValueError:
        return chapters_raw # Fallback to XML order if IDs are not integers

def export_single_markdown(book_root: ET.Element, output_path: Path, console: Console):
    """Exports the entire book content to a single Markdown file."""
    if book_root is None:
        console.print("[red]Error: Book data is missing, cannot export.[/red]")
        return

    try:
        markdown_content = []
        title = book_root.findtext("title", "Untitled Book")
        
        # Add frontmatter sections if they exist and have content
        frontmatter = book_root.find("frontmatter")
        if frontmatter is not None:
            # Title Page
            title_page = frontmatter.findtext("title_page")
            if title_page and title_page.strip():
                markdown_content.append(f"{unescape(title_page.strip())}\n\n---\n")
            
            # Copyright Page
            copyright_page = frontmatter.findtext("copyright_page")
            if copyright_page and copyright_page.strip():
                markdown_content.append(f"{unescape(copyright_page.strip())}\n\n---\n")
            
            # Dedication
            dedication = frontmatter.findtext("dedication")
            if dedication and dedication.strip():
                markdown_content.append(f"## Dedication\n\n{unescape(dedication.strip())}\n\n---\n")
            
            # Acknowledgements
            acknowledgements = frontmatter.findtext("acknowledgements")
            if acknowledgements and acknowledgements.strip():
                markdown_content.append(f"## Acknowledgements\n\n{unescape(acknowledgements.strip())}\n\n---\n")
        
        # Add main title if no custom title page was provided
        has_custom_title_page = False
        if frontmatter is not None:
            title_page_text = frontmatter.findtext("title_page")
            has_custom_title_page = title_page_text and title_page_text.strip()
        
        if not has_custom_title_page:
            markdown_content.append(f"# {unescape(title)}\n")

        synopsis = book_root.findtext("synopsis")
        if synopsis:
            markdown_content.append(f"## Synopsis\n\n{unescape(synopsis.strip())}\n")

        markdown_content.append("## Chapters\n")
        chapters = _get_sorted_chapters(book_root)
        for chap in chapters:
            chap_num = chap.findtext("number", chap.get("id", "N/A"))
            chap_title = chap.findtext("title", "Untitled Chapter")
            markdown_content.append(f"### Chapter {unescape(chap_num)}: {unescape(chap_title)}\n")

            content = chap.find("content")
            if content is not None:
                for para in content.findall(".//paragraph"):
                    para_text = (para.text or "").strip()
                    if para_text:
                        markdown_content.append(f"{unescape(para_text)}\n")
            else:
                markdown_content.append("*[Chapter content missing]*\n")

        full_markdown = "\n".join(markdown_content)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_markdown)
        console.print(f"[green]Successfully exported single Markdown file to:[/green] [cyan]{output_path.resolve()}[/cyan]")
    except Exception as e:
        console.print(f"[bold red]Error exporting single Markdown file: {e}[/bold red]")

def export_markdown_per_chapter(book_root: ET.Element, output_parent_dir: Path, book_title_slug: str, console: Console):
    """Exports each chapter to its own Markdown file within a dedicated directory."""
    if book_root is None:
        console.print("[red]Error: Book data is missing, cannot export.[/red]")
        return

    export_dir = output_parent_dir / f"{book_title_slug}-markdown-chapters"
    try:
        export_dir.mkdir(parents=True, exist_ok=True)
        console.print(f"Exporting chapters to directory: [cyan]{export_dir.resolve()}[/cyan]")

        chapters = _get_sorted_chapters(book_root)
        if not chapters:
            console.print("[yellow]No chapters found to export.[/yellow]")
            return

        for chap in chapters:
            chap_num_str = chap.findtext("number", chap.get("id", "0"))
            chap_title = chap.findtext("title", "Untitled Chapter")
            chap_title_slug = utils.slugify(chap_title)

            try:
                filename = f"{int(chap_num_str):02d}-{chap_title_slug}.md"
            except ValueError:
                filename = f"{chap_num_str}-{chap_title_slug}.md"

            chapter_file_path = export_dir / filename
            chapter_markdown = [f"# Chapter {unescape(chap_num_str)}: {unescape(chap_title)}\n"]
            
            content = chap.find("content")
            if content is not None:
                for para in content.findall(".//paragraph"):
                    para_text = (para.text or "").strip()
                    if para_text:
                        chapter_markdown.append(f"{unescape(para_text)}\n")
            
            with open(chapter_file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(chapter_markdown))
        
        console.print(f"[green]Successfully exported {len(chapters)} chapters.[/green]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred during per-chapter export: {e}[/bold red]")
