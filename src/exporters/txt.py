# -*- coding: utf-8 -*-
"""
txt.py - Handles exporting the project to plain text format.
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from html import unescape
from datetime import datetime

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
        return chapters_raw

def export_single_txt(book_root: ET.Element, output_path: Path, console: Console):
    """Exports the entire book content to a single plain text file."""
    if book_root is None:
        console.print("[red]Error: Book data is missing, cannot export.[/red]")
        return

    try:
        text_content = []
        title = book_root.findtext("title", "Untitled Book")
        
        # Add frontmatter sections if they exist and have content
        frontmatter = book_root.find("frontmatter")
        if frontmatter is not None:
            # Title Page
            title_page = frontmatter.findtext("title_page")
            if title_page and title_page.strip():
                text_content.append(unescape(title_page.strip()))
                text_content.append("\n" + "="*60 + "\n")
            
            # Copyright Page
            copyright_page = frontmatter.findtext("copyright_page")
            if copyright_page and copyright_page.strip():
                text_content.append(unescape(copyright_page.strip()))
                text_content.append("\n" + "="*60 + "\n")
            
            # Dedication
            dedication = frontmatter.findtext("dedication")
            if dedication and dedication.strip():
                text_content.append("DEDICATION\n")
                text_content.append("-" * 10)
                text_content.append(f"\n{unescape(dedication.strip())}")
                text_content.append("\n" + "="*60 + "\n")
            
            # Acknowledgements
            acknowledgements = frontmatter.findtext("acknowledgements")
            if acknowledgements and acknowledgements.strip():
                text_content.append("ACKNOWLEDGEMENTS\n")
                text_content.append("-" * 16)
                text_content.append(f"\n{unescape(acknowledgements.strip())}")
                text_content.append("\n" + "="*60 + "\n")
        
        # Add main title if no custom title page was provided
        has_custom_title_page = False
        if frontmatter is not None:
            title_page_text = frontmatter.findtext("title_page")
            has_custom_title_page = title_page_text and title_page_text.strip()
        
        if not has_custom_title_page:
            text_content.append(unescape(title).upper())
            text_content.append("\n" + "="*len(title) + "\n")
            
            synopsis = book_root.findtext("synopsis")
            if synopsis:
                text_content.append("SYNOPSIS\n")
                text_content.append("-" * 8)
                text_content.append(f"\n{unescape(synopsis.strip())}")
                text_content.append("\n" + "="*60 + "\n")
        
        # Chapters
        chapters = _get_sorted_chapters(book_root)
        for chap in chapters:
            chap_num = chap.findtext("number", chap.get("id", "N/A"))
            chap_title = chap.findtext("title", "Untitled Chapter")
            
            # Chapter header
            chapter_header = f"CHAPTER {unescape(chap_num)}: {unescape(chap_title).upper()}"
            text_content.append(chapter_header)
            text_content.append("-" * len(chapter_header))
            text_content.append("")  # Empty line after chapter header
            
            content = chap.find("content")
            if content is not None:
                paragraphs = content.findall(".//paragraph")
                if paragraphs:
                    for para in paragraphs:
                        para_text = (para.text or "").strip()
                        if para_text:
                            # Add paragraph with proper spacing
                            text_content.append(f"    {unescape(para_text)}")
                            text_content.append("")  # Empty line between paragraphs
                else:
                    text_content.append("    [Chapter content missing]")
                    text_content.append("")
            else:
                text_content.append("    [Chapter content missing]")
                text_content.append("")
            
            # Add separator between chapters
            text_content.append("\n" + "="*60 + "\n")
        
        # Add export information
        export_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text_content.append(f"\n\nExported by Fiction Fabricator on {export_time}")
        
        # Write to file
        full_text = "\n".join(text_content)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_text)
        
        console.print(f"[green]Successfully exported TXT file to:[/green] [cyan]{output_path.resolve()}[/cyan]")
        
    except Exception as e:
        console.print(f"[bold red]Error exporting TXT file: {e}[/bold red]")

def export_txt_per_chapter(book_root: ET.Element, output_parent_dir: Path, book_title_slug: str, console: Console):
    """Exports each chapter to its own plain text file within a dedicated directory."""
    if book_root is None:
        console.print("[red]Error: Book data is missing, cannot export.[/red]")
        return

    export_dir = output_parent_dir / f"{book_title_slug}-txt-chapters"
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
                filename = f"{int(chap_num_str):02d}-{chap_title_slug}.txt"
            except ValueError:
                filename = f"{chap_num_str}-{chap_title_slug}.txt"

            chapter_file_path = export_dir / filename
            
            # Chapter content
            chapter_text = []
            chapter_header = f"CHAPTER {unescape(chap_num_str)}: {unescape(chap_title).upper()}"
            chapter_text.append(chapter_header)
            chapter_text.append("=" * len(chapter_header))
            chapter_text.append("")  # Empty line
            
            content = chap.find("content")
            if content is not None:
                paragraphs = content.findall(".//paragraph")
                if paragraphs:
                    for para in paragraphs:
                        para_text = (para.text or "").strip()
                        if para_text:
                            chapter_text.append(unescape(para_text))
                            chapter_text.append("")  # Empty line between paragraphs
                else:
                    chapter_text.append("[Chapter content missing]")
            else:
                chapter_text.append("[Chapter content missing]")
            
            with open(chapter_file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(chapter_text))
        
        console.print(f"[green]Successfully exported {len(chapters)} TXT chapters.[/green]")
        
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred during per-chapter TXT export: {e}[/bold red]")