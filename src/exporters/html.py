# -*- coding: utf-8 -*-
"""
html.py - Handles exporting the project to HTML format.
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from html import escape
from datetime import datetime

from rich.console import Console

from src import utils

# --- Default CSS for the HTML export ---
DEFAULT_CSS = """
body {
    font-family: Georgia, 'Times New Roman', serif;
    line-height: 1.6;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    color: #333;
    background-color: #fff;
}

.book-header {
    text-align: center;
    margin-bottom: 3em;
    border-bottom: 2px solid #ccc;
    padding-bottom: 2em;
}

.book-title {
    font-size: 2.5em;
    font-weight: bold;
    margin-bottom: 0.5em;
    color: #2c3e50;
}

.book-synopsis {
    font-style: italic;
    font-size: 1.1em;
    margin: 1em 0;
    padding: 1em;
    background-color: #f8f9fa;
    border-left: 4px solid #007bff;
}

.story-elements {
    margin: 2em 0;
    padding: 1em;
    background-color: #fff3cd;
    border-left: 4px solid #ffc107;
    border-radius: 5px;
}

.story-elements h2 {
    color: #856404;
    margin-top: 0;
}

.story-element {
    margin: 0.5em 0;
}

.element-label {
    font-weight: bold;
    color: #6c757d;
}

.characters-section {
    margin: 2em 0;
    padding: 1em;
    background-color: #f1f3f4;
    border-radius: 5px;
}

.characters-section h2 {
    color: #2c3e50;
    border-bottom: 1px solid #bdc3c7;
    padding-bottom: 0.5em;
}

.character {
    margin: 0.5em 0;
}

.character-name {
    font-weight: bold;
    color: #34495e;
}

.chapter {
    margin: 3em 0;
    page-break-before: always;
}

.chapter-title {
    font-size: 1.8em;
    font-weight: bold;
    text-align: center;
    margin: 2em 0 1.5em 0;
    color: #2c3e50;
    border-bottom: 1px solid #bdc3c7;
    padding-bottom: 0.5em;
}

.chapter-content p {
    text-indent: 1.5em;
    margin: 0.8em 0;
    text-align: justify;
}

.chapter-content p:first-child {
    text-indent: 0;
}

.missing-content {
    font-style: italic;
    color: #7f8c8d;
    text-align: center;
    padding: 2em;
    background-color: #ecf0f1;
    border-radius: 5px;
}

.export-info {
    margin-top: 3em;
    padding: 1em;
    background-color: #f8f9fa;
    border-top: 1px solid #dee2e6;
    font-size: 0.9em;
    color: #6c757d;
    text-align: center;
}

@media print {
    body {
        max-width: none;
        margin: 0;
        padding: 1in;
    }
    
    .chapter {
        page-break-before: always;
    }
    
    .export-info {
        display: none;
    }
}
"""

def _get_sorted_chapters(book_root: ET.Element) -> list[ET.Element]:
    """Helper to get chapters sorted numerically by ID."""
    if book_root is None:
        return []
    chapters_raw = book_root.findall(".//chapter")
    try:
        return sorted(chapters_raw, key=lambda chap: int(chap.get("id", "0")))
    except ValueError:
        return chapters_raw  # Fallback to XML order if IDs are not integers

def export_single_html(book_root: ET.Element, output_path: Path, console: Console):
    """Exports the entire book content to a single HTML file."""
    if book_root is None:
        console.print("[red]Error: Book data is missing, cannot export.[/red]")
        return

    try:
        html_parts = []
        title = book_root.findtext("title", "Untitled Book")
        
        # HTML document structure
        html_parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)}</title>
    <style>
{DEFAULT_CSS}
    </style>
</head>
<body>""")

        # Book header
        html_parts.append('<div class="book-header">')
        html_parts.append(f'<h1 class="book-title">{escape(title)}</h1>')
        
        synopsis = book_root.findtext("synopsis")
        if synopsis:
            html_parts.append(f'<div class="book-synopsis">{escape(synopsis.strip())}</div>')
        
        # Story elements
        story_elements = book_root.find("story_elements")
        if story_elements is not None:
            html_parts.append('<div class="story-elements">')
            html_parts.append('<h2>Story Elements</h2>')
            
            genre = story_elements.findtext("genre")
            tone = story_elements.findtext("tone")
            perspective = story_elements.findtext("perspective")
            target_audience = story_elements.findtext("target_audience")
            
            if genre:
                html_parts.append(f'<div class="story-element"><span class="element-label">Genre:</span> {escape(genre)}</div>')
            if tone:
                html_parts.append(f'<div class="story-element"><span class="element-label">Tone:</span> {escape(tone)}</div>')
            if perspective:
                html_parts.append(f'<div class="story-element"><span class="element-label">Perspective:</span> {escape(perspective)}</div>')
            if target_audience:
                html_parts.append(f'<div class="story-element"><span class="element-label">Target Audience:</span> {escape(target_audience)}</div>')
            
            html_parts.append('</div>')
        
        html_parts.append('</div>')

        # Characters section
        characters = book_root.findall(".//character")
        if characters:
            html_parts.append('<div class="characters-section">')
            html_parts.append('<h2>Characters</h2>')
            for char in characters:
                name = escape(char.findtext("name", "N/A"))
                desc = escape(char.findtext("description", "N/A"))
                html_parts.append(f'<div class="character"><span class="character-name">{name}:</span> {desc}</div>')
            html_parts.append('</div>')

        # Chapters
        chapters = _get_sorted_chapters(book_root)
        for chap in chapters:
            chap_num = chap.findtext("number", chap.get("id", "N/A"))
            chap_title = chap.findtext("title", "Untitled Chapter")
            
            html_parts.append('<div class="chapter">')
            html_parts.append(f'<h2 class="chapter-title">Chapter {escape(chap_num)}: {escape(chap_title)}</h2>')
            html_parts.append('<div class="chapter-content">')

            content = chap.find("content")
            if content is not None:
                paragraphs = content.findall(".//paragraph")
                if paragraphs:
                    for para in paragraphs:
                        para_text = (para.text or "").strip()
                        if para_text:
                            html_parts.append(f'<p>{escape(para_text)}</p>')
                else:
                    html_parts.append('<div class="missing-content">[Chapter content missing]</div>')
            else:
                html_parts.append('<div class="missing-content">[Chapter content missing]</div>')
            
            html_parts.append('</div>')
            html_parts.append('</div>')

        # Export info
        export_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html_parts.append(f'''<div class="export-info">
            <p>Exported by Fiction Fabricator on {export_time}</p>
        </div>''')

        # Close HTML
        html_parts.append('</body>\n</html>')

        # Write file
        full_html = '\n'.join(html_parts)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_html)
        
        console.print(f"[green]Successfully exported HTML file to:[/green] [cyan]{output_path.resolve()}[/cyan]")
    except Exception as e:
        console.print(f"[bold red]Error exporting HTML file: {e}[/bold red]")

def export_html_per_chapter(book_root: ET.Element, output_parent_dir: Path, book_title_slug: str, console: Console):
    """Exports each chapter to its own HTML file within a dedicated directory."""
    if book_root is None:
        console.print("[red]Error: Book data is missing, cannot export.[/red]")
        return

    export_dir = output_parent_dir / f"{book_title_slug}-html-chapters"
    try:
        export_dir.mkdir(parents=True, exist_ok=True)
        console.print(f"Exporting chapters to directory: [cyan]{export_dir.resolve()}[/cyan]")

        title = book_root.findtext("title", "Untitled Book")
        chapters = _get_sorted_chapters(book_root)
        if not chapters:
            console.print("[yellow]No chapters found to export.[/yellow]")
            return

        # Create an index file
        index_parts = []
        index_parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)} - Table of Contents</title>
    <style>
{DEFAULT_CSS}
.toc-list {{ list-style: none; padding: 0; }}
.toc-item {{ margin: 0.5em 0; }}
.toc-link {{ text-decoration: none; color: #007bff; font-size: 1.1em; }}
.toc-link:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="book-header">
        <h1 class="book-title">{escape(title)}</h1>
        <h2>Table of Contents</h2>
    </div>
    <ul class="toc-list">""")

        for chap in chapters:
            chap_num_str = chap.findtext("number", chap.get("id", "0"))
            chap_title = chap.findtext("title", "Untitled Chapter")
            chap_title_slug = utils.slugify(chap_title)

            try:
                filename = f"{int(chap_num_str):02d}-{chap_title_slug}.html"
            except ValueError:
                filename = f"{chap_num_str}-{chap_title_slug}.html"

            # Add to index
            index_parts.append(f'        <li class="toc-item"><a href="{filename}" class="toc-link">Chapter {escape(chap_num_str)}: {escape(chap_title)}</a></li>')

            # Create individual chapter file
            chapter_file_path = export_dir / filename
            chapter_html = []
            
            chapter_html.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chapter {escape(chap_num_str)}: {escape(chap_title)}</title>
    <style>
{DEFAULT_CSS}
.nav-link {{ color: #007bff; text-decoration: none; margin: 0 1em; }}
.nav-link:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div style="text-align: center; margin-bottom: 2em;">
        <a href="index.html" class="nav-link">← Table of Contents</a>
    </div>
    <div class="chapter">
        <h1 class="chapter-title">Chapter {escape(chap_num_str)}: {escape(chap_title)}</h1>
        <div class="chapter-content">""")
            
            content = chap.find("content")
            if content is not None:
                paragraphs = content.findall(".//paragraph")
                if paragraphs:
                    for para in paragraphs:
                        para_text = (para.text or "").strip()
                        if para_text:
                            chapter_html.append(f'            <p>{escape(para_text)}</p>')
                else:
                    chapter_html.append('            <div class="missing-content">[Chapter content missing]</div>')
            else:
                chapter_html.append('            <div class="missing-content">[Chapter content missing]</div>')
            
            chapter_html.append("""        </div>
    </div>
</body>
</html>""")
            
            with open(chapter_file_path, "w", encoding="utf-8") as f:
                f.write('\n'.join(chapter_html))

        # Finish index file
        index_parts.append("""    </ul>
</body>
</html>""")
        
        index_path = export_dir / "index.html"
        with open(index_path, "w", encoding="utf-8") as f:
            f.write('\n'.join(index_parts))
        
        console.print(f"[green]Successfully exported {len(chapters)} HTML chapters with index.[/green]")
        console.print(f"[green]Open [cyan]{index_path.resolve()}[/cyan] to start reading.[/green]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred during per-chapter HTML export: {e}[/bold red]")