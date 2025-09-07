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
        markdown_content.append(f"# {unescape(title)}\n")

        synopsis = book_root.findtext("synopsis")
        if synopsis:
            markdown_content.append(f"## Synopsis\n\n{unescape(synopsis.strip())}\n")

        # Story elements
        story_elements = book_root.find("story_elements")
        if story_elements is not None:
            markdown_content.append("## Story Elements\n")
            genre = story_elements.findtext("genre")
            tone = story_elements.findtext("tone") 
            perspective = story_elements.findtext("perspective")
            target_audience = story_elements.findtext("target_audience")
            
            if genre:
                markdown_content.append(f"**Genre:** {unescape(genre)}")
            if tone:
                markdown_content.append(f"**Tone:** {unescape(tone)}")
            if perspective:
                markdown_content.append(f"**Perspective:** {unescape(perspective)}")
            if target_audience:
                markdown_content.append(f"**Target Audience:** {unescape(target_audience)}")
            markdown_content.append("\n")

        characters = book_root.findall(".//character")
        if characters:
            markdown_content.append("## Characters\n")
            for char in characters:
                name = unescape(char.findtext("name", "N/A"))
                desc = unescape(char.findtext("description", "N/A"))
                markdown_content.append(f"*   **{name}**: {desc}")
            markdown_content.append("\n")

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
