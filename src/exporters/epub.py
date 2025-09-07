# -*- coding: utf-8 -*-
"""
epub.py - Handles exporting the project to EPUB format.
"""
import xml.etree.ElementTree as ET
import uuid
import html
import mimetypes
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.panel import Panel

from src import utils

try:
    from ebooklib import epub
except ImportError:
    epub = None

# --- Basic CSS for the EPUB ---
DEFAULT_CSS = """
body { font-family: Georgia, serif; line-height: 1.6; margin: 1em 1.5em; text-align: justify; }
h1.chapter-title { text-align: center; margin-top: 2.5em; margin-bottom: 1.5em; page-break-before: always; }
p { text-indent: 1.5em; margin-top: 0; margin-bottom: 0.2em; }
h1 + p { text-indent: 0; }
"""

def _get_sorted_chapters(book_root: ET.Element) -> list[ET.Element]:
    """Helper to get chapters sorted numerically by ID."""
    if book_root is None:
        return []
    chapters_raw = book_root.findall(".//chapter")
    try:
        return sorted(chapters_raw, key=lambda chap: int(chap.get("id", "0")))
    except ValueError:
        return chapters_raw

def _add_cover_image(book: "epub.EpubBook", cover_image_path: Path, console: Console) -> bool:
    """
    Adds a cover image to the EPUB book.
    Returns True if successful, False otherwise.
    """
    try:
        if not cover_image_path.exists():
            console.print(f"[yellow]Warning: Cover image not found at {cover_image_path}[/yellow]")
            return False
        
        # Read the image file
        with open(cover_image_path, 'rb') as img_file:
            cover_image_data = img_file.read()
        
        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(str(cover_image_path))
        if not mime_type or not mime_type.startswith('image/'):
            console.print(f"[yellow]Warning: File {cover_image_path} doesn't appear to be a valid image[/yellow]")
            return False
        
        # Get file extension for the cover image
        file_extension = cover_image_path.suffix.lower()
        cover_filename = f"cover{file_extension}"
        
        # Create the cover image item
        cover_image_item = epub.EpubImage()
        cover_image_item.id = "cover_image"
        cover_image_item.file_name = cover_filename
        cover_image_item.media_type = mime_type
        cover_image_item.content = cover_image_data
        
        # Add the image to the book
        book.add_item(cover_image_item)
        
        # Set as the cover image
        book.set_cover(cover_filename, cover_image_data)
        
        console.print(f"[green]✓ Cover image added: {cover_image_path.name}[/green]")
        return True
        
    except Exception as e:
        console.print(f"[yellow]Warning: Could not add cover image: {e}[/yellow]")
        return False

def _format_chapter_xhtml(chapter_element: ET.Element, chapter_title: str) -> bytes:
    """Formats a chapter's content into a valid XHTML string (as bytes)."""
    paragraphs_html = []
    content_element = chapter_element.find("content")
    if content_element is not None:
        for para in content_element.findall(".//paragraph"):
            para_text = (para.text or "").strip()
            if para_text:
                escaped_text = html.escape(para_text).replace("\n", "<br />\n    ")
                paragraphs_html.append(f"<p>{escaped_text}</p>")

    if not paragraphs_html:
        paragraphs_html.append("<p><i>[Chapter content is empty or missing]</i></p>")

    xhtml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
    <title>{html.escape(chapter_title)}</title>
    <link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
    <h1 class="chapter-title">{html.escape(chapter_title)}</h1>
    {''.join(paragraphs_html)}
</body>
</html>"""
    return xhtml_content.encode('utf-8')

def export_epub(book_root: ET.Element, output_dir: Path, book_title_slug: str, console: Console, author="Fiction Fabricator", cover_image_path: Path | None = None):
    """Exports the book content to an EPUB file."""
    if epub is None:
        console.print("[bold red]EPUB Export Failed: 'ebooklib' is not installed.[/bold red]")
        console.print("[bold red]Please run: uv pip install ebooklib[/bold red]")
        return

    if book_root is None:
        console.print("[red]Error: Book data is missing for EPUB export.[/red]")
        return

    try:
        title = book_root.findtext("title", book_title_slug.replace('-', ' ').title())
        chapters_sorted = _get_sorted_chapters(book_root)

        book = epub.EpubBook()
        book.set_identifier(f"urn:uuid:{uuid.uuid4()}")
        book.set_title(title)
        book.set_language("en")
        book.add_author(author)

        # Add story elements as metadata if available
        story_elements = book_root.find("story_elements")
        if story_elements is not None:
            genre = story_elements.findtext("genre")
            if genre:
                book.add_metadata('DC', 'subject', genre)
            
            # Add additional metadata as meta tags
            tone = story_elements.findtext("tone")
            perspective = story_elements.findtext("perspective")
            target_audience = story_elements.findtext("target_audience")
            
            if tone:
                book.add_metadata(None, 'meta', tone, {'name': 'tone'})
            if perspective:
                book.add_metadata(None, 'meta', perspective, {'name': 'perspective'})
            if target_audience:
                book.add_metadata(None, 'meta', target_audience, {'name': 'target-audience'})

        console.print(Panel(f"Generating EPUB for: [cyan]{title}[/cyan]", style="blue", title="EPUB Export"))

        # Add cover image if provided
        if cover_image_path:
            _add_cover_image(book, cover_image_path, console)

        # Add CSS
        css = epub.EpubItem(uid="style_default", file_name="style.css", media_type="text/css", content=DEFAULT_CSS.encode('utf-8'))
        book.add_item(css)

        epub_chapters = []
        for i, chapter_elem in enumerate(chapters_sorted):
            chap_num = chapter_elem.findtext("number", str(i + 1))
            chap_title_raw = chapter_elem.findtext("title", f"Chapter {chap_num}")
            chap_title = f"Chapter {chap_num}: {chap_title_raw}"

            xhtml_filename = f"chapter_{i+1}.xhtml"
            chapter_xhtml_item = epub.EpubHtml(title=chap_title, file_name=xhtml_filename, lang="en")
            chapter_xhtml_item.content = _format_chapter_xhtml(chapter_elem, chap_title)
            chapter_xhtml_item.add_item(css)
            book.add_item(chapter_xhtml_item)
            epub_chapters.append(chapter_xhtml_item)

        book.spine = ['nav'] + epub_chapters
        book.toc = [epub.Link(chap.file_name, chap.title, chap.id) for chap in epub_chapters]
        
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        epub_filename = f"{book_title_slug}.epub"
        output_path = output_dir / epub_filename
        epub.write_epub(output_path, book, {})

        console.print(Panel(f"[bold green]✓ EPUB generated successfully![/bold green]", style="green"))
        console.print(f"  Saved to: [link=file://{output_path.resolve()}]{output_path.resolve()}[/link]")

    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred during EPUB export: {e}[/bold red]")
        console.print_exception(show_locals=False, word_wrap=True)
