# -*- coding: utf-8 -*-
"""
epub.py - Handles exporting the project to EPUB format.
"""
import xml.etree.ElementTree as ET
import uuid
import mimetypes
from pathlib import Path
from html import escape
import html
import re
from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel
import ebooklib
from ebooklib import epub

from src import utils

if TYPE_CHECKING:
    from ebooklib.epub import EpubBook, EpubImage

try:
    from ebooklib import epub
except ImportError:
    epub = None

def _generate_epub_css_with_font(custom_font_name: str | None = None) -> str:
    """Generate CSS for EPUB with custom font applied to headings."""
    # Base font for body text
    body_font = "Georgia, serif"
    
    # Chapter heading font
    heading_font = f"'{custom_font_name}', {body_font}" if custom_font_name else body_font
    
    return f"""
body {{ font-family: {body_font}; line-height: 1.6; margin: 1em 1.5em; text-align: justify; }}
h1.chapter-number {{ font-family: {heading_font}; text-align: right; margin-top: 2.5em; margin-bottom: 0.5em; page-break-before: always; font-size: 1.8em; }}
h2.chapter-title {{ font-family: {heading_font}; text-align: right; margin-top: 0; margin-bottom: 1.5em; font-size: 1.4em; }}
h1, h2 {{ font-family: {heading_font}; }}
p {{ text-indent: 1.5em; margin-top: 0; margin-bottom: 0.2em; }}
h1 + p, h2 + p {{ text-indent: 0; }}
"""

# --- Basic CSS for the EPUB ---
DEFAULT_CSS = """
body { font-family: Georgia, serif; line-height: 1.6; margin: 1em 1.5em; text-align: justify; }
h1.chapter-number { text-align: right; margin-top: 2.5em; margin-bottom: 0.5em; page-break-before: always; font-size: 1.8em; }
h2.chapter-title { text-align: right; margin-top: 0; margin-bottom: 1.5em; font-size: 1.4em; }
p { text-indent: 1.5em; margin-top: 0; margin-bottom: 0.2em; }
h1 + p, h2 + p { text-indent: 0; }
"""

def _convert_markdown_to_html(text: str) -> str:
    """Convert basic markdown formatting to HTML."""
    if not text:
        return text
    
    # Convert italic (*text*) to <em>
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    
    # Convert bold (**text**) to <strong>
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    
    # Convert underline (_text_) to <u> (alternative italic)
    text = re.sub(r'_([^_]+)_', r'<em>\1</em>', text)
    
    return text

def _get_sorted_chapters(book_root: ET.Element) -> list[ET.Element]:
    """Helper to get chapters sorted numerically by ID."""
    if book_root is None:
        return []
    chapters_raw = book_root.findall(".//chapter")
    try:
        return sorted(chapters_raw, key=lambda chap: int(chap.get("id", "0")))
    except ValueError:
        return chapters_raw

def _add_cover_image(book: epub.EpubBook, cover_image_path: Path, console: Console) -> bool:
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

def _format_chapter_xhtml(chapter_element: ET.Element, chapter_number: str, chapter_title: str) -> bytes:
    """Formats a chapter's content into a valid XHTML string (as bytes)."""
    paragraphs_html = []
    content_element = chapter_element.find("content")
    if content_element is not None:
        for para in content_element.findall(".//paragraph"):
            para_text = (para.text or "").strip()
            if para_text:
                # First convert markdown to HTML
                html_text = _convert_markdown_to_html(para_text)
                # Then escape any remaining HTML entities (but preserve our converted tags)
                html_text = html_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                # Restore our converted markdown tags
                html_text = html_text.replace("&lt;em&gt;", "<em>").replace("&lt;/em&gt;", "</em>")
                html_text = html_text.replace("&lt;strong&gt;", "<strong>").replace("&lt;/strong&gt;", "</strong>")
                html_text = html_text.replace("&lt;u&gt;", "<u>").replace("&lt;/u&gt;", "</u>")
                # Handle line breaks
                html_text = html_text.replace("\n", "<br />\n    ")
                paragraphs_html.append(f"<p>{html_text}</p>")

    if not paragraphs_html:
        paragraphs_html.append("<p><i>[Chapter content is empty or missing]</i></p>")

    xhtml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
    <title>Chapter {html.escape(chapter_number)}: {html.escape(chapter_title)}</title>
    <link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
    <h1 class="chapter-number">Chapter {html.escape(chapter_number)}</h1>
    <h2 class="chapter-title">{html.escape(chapter_title)}</h2>
    {''.join(paragraphs_html)}
</body>
</html>"""
    return xhtml_content.encode('utf-8')

def export_epub(book_root: ET.Element, output_dir: Path, book_title_slug: str, console: Console, author="Fiction Fabricator", cover_image_path: Path | None = None, custom_font_name: str | None = None, custom_font_url: str | None = None):
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

        # Add CSS with custom font
        css_content = _generate_epub_css_with_font(custom_font_name) if custom_font_name else DEFAULT_CSS
        css = epub.EpubItem(uid="style_default", file_name="style.css", media_type="text/css", content=css_content.encode('utf-8'))
        book.add_item(css)

        # Add frontmatter sections if they exist and have content
        frontmatter_items = []
        frontmatter = book_root.find("frontmatter")
        if frontmatter is not None:
            # Title Page
            title_page = frontmatter.findtext("title_page")
            if title_page and title_page.strip():
                lines = title_page.strip().split('\n')
                title_page_content = []
                
                if len(lines) >= 1:
                    title_page_content.append(f'<h1>{html.escape(lines[0].strip())}</h1>')
                if len(lines) >= 2:
                    title_page_content.append(f'<h2>{html.escape(lines[1].strip())}</h2>')
                if len(lines) > 2:
                    # Handle any additional lines as regular text
                    for line in lines[2:]:
                        if line.strip():
                            title_page_content.append(f'<div>{html.escape(line.strip())}</div>')
                
                title_page_html = f"""<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Title Page</title>
    <link rel="stylesheet" type="text/css" href="style.css"/>
    <style>
        body {{ text-align: center; padding: 2em; }}
        .title-page {{ font-size: 1.2em; line-height: 1.6; }}
        h1, h2 {{ text-align: center; }}
    </style>
</head>
<body>
    <div class="title-page">{''.join(title_page_content)}</div>
</body>
</html>"""
                title_page_item = epub.EpubHtml(title="Title Page", file_name="title_page.xhtml", lang="en")
                title_page_item.content = title_page_html.encode('utf-8')
                title_page_item.add_item(css)
                book.add_item(title_page_item)
                frontmatter_items.append(title_page_item)

            # Copyright Page
            copyright_page = frontmatter.findtext("copyright_page")
            if copyright_page and copyright_page.strip():
                copyright_html = f"""<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Copyright Page</title>
    <link rel="stylesheet" type="text/css" href="style.css"/>
    <style>
        body {{ padding: 2em; font-size: 0.9em; line-height: 1.6; }}
    </style>
</head>
<body>
    <div class="copyright-page">{html.escape(copyright_page.strip()).replace(chr(10), '<br/>')}</div>
</body>
</html>"""
                copyright_item = epub.EpubHtml(title="Copyright Page", file_name="copyright_page.xhtml", lang="en")
                copyright_item.content = copyright_html.encode('utf-8')
                copyright_item.add_item(css)
                book.add_item(copyright_item)
                frontmatter_items.append(copyright_item)

            # Dedication
            dedication = frontmatter.findtext("dedication")
            if dedication and dedication.strip():
                dedication_html = f"""<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Dedication</title>
    <link rel="stylesheet" type="text/css" href="style.css"/>
    <style>
        body {{ padding: 2em; text-align: center; font-style: italic; }}
    </style>
</head>
<body>
    <h2>Dedication</h2>
    <div class="dedication">{html.escape(dedication.strip()).replace(chr(10), '<br/>')}</div>
</body>
</html>"""
                dedication_item = epub.EpubHtml(title="Dedication", file_name="dedication.xhtml", lang="en")
                dedication_item.content = dedication_html.encode('utf-8')
                dedication_item.add_item(css)
                book.add_item(dedication_item)
                frontmatter_items.append(dedication_item)

            # Acknowledgements
            acknowledgements = frontmatter.findtext("acknowledgements")
            if acknowledgements and acknowledgements.strip():
                acknowledgements_html = f"""<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Acknowledgements</title>
    <link rel="stylesheet" type="text/css" href="style.css"/>
    <style>
        body {{ padding: 2em; }}
    </style>
</head>
<body>
    <h2>Acknowledgements</h2>
    <div class="acknowledgements">{html.escape(acknowledgements.strip()).replace(chr(10), '<br/>')}</div>
</body>
</html>"""
                acknowledgements_item = epub.EpubHtml(title="Acknowledgements", file_name="acknowledgements.xhtml", lang="en")
                acknowledgements_item.content = acknowledgements_html.encode('utf-8')
                acknowledgements_item.add_item(css)
                book.add_item(acknowledgements_item)
                frontmatter_items.append(acknowledgements_item)

        epub_chapters = []
        for i, chapter_elem in enumerate(chapters_sorted):
            chap_num = chapter_elem.findtext("number", str(i + 1))
            chap_title_raw = chapter_elem.findtext("title", f"Chapter {chap_num}")
            chap_title_display = f"Chapter {chap_num}: {chap_title_raw}"

            xhtml_filename = f"chapter_{i+1}.xhtml"
            chapter_xhtml_item = epub.EpubHtml(title=chap_title_display, file_name=xhtml_filename, lang="en")
            chapter_xhtml_item.content = _format_chapter_xhtml(chapter_elem, chap_num, chap_title_raw)
            chapter_xhtml_item.add_item(css)
            book.add_item(chapter_xhtml_item)
            epub_chapters.append(chapter_xhtml_item)

        book.spine = ['nav'] + frontmatter_items + epub_chapters
        
        # Create TOC with frontmatter sections first, then chapters
        toc_items = []
        for item in frontmatter_items:
            toc_items.append(epub.Link(item.file_name, item.title, item.id))
        for chap in epub_chapters:
            toc_items.append(epub.Link(chap.file_name, chap.title, chap.id))
        book.toc = toc_items
        
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
