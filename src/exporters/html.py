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

def _generate_css_with_font(custom_font_name: str | None = None, custom_font_url: str | None = None) -> str:
    """Generate CSS with custom font applied to headings."""
    # Base font for body text
    body_font = "Georgia, 'Times New Roman', serif"
    
    # Chapter heading font
    heading_font = f"'{custom_font_name}', {body_font}" if custom_font_name else body_font
    
    return f"""
body {{
    font-family: {body_font};
    line-height: 1.6;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    color: #333;
    background-color: #fff;
}}

.book-header {{
    text-align: center;
    margin-bottom: 3em;
    border-bottom: 2px solid #ccc;
    padding-bottom: 2em;
}}

.book-title {{
    font-family: {heading_font};
    font-size: 2.5em;
    font-weight: bold;
    margin-bottom: 0.5em;
    color: #2c3e50;
}}

.book-synopsis {{
    font-style: italic;
    font-size: 1.1em;
    margin: 1em 0;
    padding: 1em;
    background-color: #f8f9fa;
    border-left: 4px solid #007bff;
}}

.chapter {{
    margin: 3em 0;
    page-break-before: always;
}}

.chapter-number {{
    font-family: {heading_font};
    font-size: 1.8em;
    font-weight: bold;
    text-align: right;
    margin: 2em 0 0.5em 0;
    color: #2c3e50;
}}

.chapter-title {{
    font-family: {heading_font};
    font-size: 1.4em;
    font-weight: bold;
    text-align: right;
    margin: 0 0 1.5em 0;
    color: #2c3e50;
    border-bottom: 1px solid #bdc3c7;
    padding-bottom: 0.5em;
}}

.chapter-content p {{
    text-indent: 1.5em;
    margin: 0.8em 0;
    text-align: justify;
}}

.chapter-content p:first-child {{
    text-indent: 0;
}}

.missing-content {{
    font-style: italic;
    color: #7f8c8d;
    text-align: center;
    padding: 2em;
    background-color: #ecf0f1;
    border-radius: 5px;
}}

.export-info {{
    margin-top: 3em;
    padding: 1em;
    background-color: #f8f9fa;
    border-top: 1px solid #dee2e6;
    font-size: 0.9em;
    color: #6c757d;
    text-align: center;
}}

.frontmatter-section {{
    margin-bottom: 2em;
    page-break-after: always;
    border-bottom: 1px solid #ddd;
    padding-bottom: 2em;
}}
.frontmatter-section h2 {{
    font-family: {heading_font};
    color: #666;
    border-bottom: 2px solid #ddd;
}}
.title-page {{
    text-align: center;
    font-size: 1.2em;
}}
.title-page h1, .title-page h2 {{
    font-family: {heading_font};
}}
.copyright-page {{
    font-size: 0.9em;
    line-height: 1.6;
}}

@media print {{
    body {{
        max-width: none;
        margin: 0;
        padding: 1in;
    }}
    
    .chapter {{
        page-break-before: always;
    }}
    
    .export-info {{
        display: none;
    }}
}}
"""

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

.chapter {
    margin: 3em 0;
    page-break-before: always;
}

.chapter-number {
    font-size: 1.8em;
    font-weight: bold;
    text-align: right;
    margin: 2em 0 0.5em 0;
    color: #2c3e50;
}

.chapter-title {
    font-size: 1.4em;
    font-weight: bold;
    text-align: right;
    margin: 0 0 1.5em 0;
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

def export_single_html(book_root: ET.Element, output_path: Path, console: Console, custom_font_name: str | None = None, custom_font_url: str | None = None):
    """Exports the entire book content to a single HTML file."""
    if book_root is None:
        console.print("[red]Error: Book data is missing, cannot export.[/red]")
        return

    try:
        html_parts = []
        title = book_root.findtext("title", "Untitled Book")
        
        # Generate CSS with custom font
        css_content = _generate_css_with_font(custom_font_name, custom_font_url)
        
        # Generate font imports
        font_imports = ""
        if custom_font_url:
            font_imports = f'    <link href="{custom_font_url}" rel="stylesheet">\n'
        
        html_parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)}</title>
{font_imports}    <style>
{css_content}
        .frontmatter-section {{
            margin-bottom: 2em;
            page-break-after: always;
            border-bottom: 1px solid #ddd;
            padding-bottom: 2em;
        }}
        .frontmatter-section h2 {{
            color: #666;
            border-bottom: 2px solid #ddd;
        }}
        .title-page {{
            text-align: center;
            font-size: 1.2em;
        }}
        .copyright-page {{
            font-size: 0.9em;
            line-height: 1.6;
        }}
    </style>
</head>
<body>""")

        # Add frontmatter sections if they exist and have content
        frontmatter = book_root.find("frontmatter")
        if frontmatter is not None:
            # Title Page
            title_page = frontmatter.findtext("title_page")
            if title_page and title_page.strip():
                html_parts.append('<div class="frontmatter-section title-page">')
                lines = title_page.strip().split('\n')
                if len(lines) >= 1:
                    html_parts.append(f'<h1>{escape(lines[0].strip())}</h1>')
                if len(lines) >= 2:
                    html_parts.append(f'<h2>{escape(lines[1].strip())}</h2>')
                if len(lines) > 2:
                    # Handle any additional lines as regular text
                    for line in lines[2:]:
                        if line.strip():
                            html_parts.append(f'<div>{escape(line.strip())}</div>')
                html_parts.append('</div>')
            
            # Copyright Page
            copyright_page = frontmatter.findtext("copyright_page")
            if copyright_page and copyright_page.strip():
                html_parts.append('<div class="frontmatter-section copyright-page">')
                html_parts.append(f'<div>{escape(copyright_page.strip()).replace(chr(10), "<br>")}</div>')
                html_parts.append('</div>')
            
            # Dedication
            dedication = frontmatter.findtext("dedication")
            if dedication and dedication.strip():
                html_parts.append('<div class="frontmatter-section">')
                html_parts.append('<h2>Dedication</h2>')
                html_parts.append(f'<div>{escape(dedication.strip()).replace(chr(10), "<br>")}</div>')
                html_parts.append('</div>')
            
            # Acknowledgements
            acknowledgements = frontmatter.findtext("acknowledgements")
            if acknowledgements and acknowledgements.strip():
                html_parts.append('<div class="frontmatter-section">')
                html_parts.append('<h2>Acknowledgements</h2>')
                html_parts.append(f'<div>{escape(acknowledgements.strip()).replace(chr(10), "<br>")}</div>')
                html_parts.append('</div>')

        # Book header (only if no custom title page was provided)
        has_custom_title_page = False
        if frontmatter is not None:
            title_page_text = frontmatter.findtext("title_page")
            has_custom_title_page = title_page_text and title_page_text.strip()
        
        if not has_custom_title_page:
            html_parts.append('<div class="book-header">')
            html_parts.append(f'<h1 class="book-title">{escape(title)}</h1>')
            
            synopsis = book_root.findtext("synopsis")
            if synopsis:
                html_parts.append(f'<div class="book-synopsis">{escape(synopsis.strip())}</div>')
            
            html_parts.append('</div>')
        else:
            # Add synopsis separately if we have a custom title page
            synopsis = book_root.findtext("synopsis")
            if synopsis:
                html_parts.append('<div class="frontmatter-section">')
                html_parts.append('<h2>Synopsis</h2>')
                html_parts.append(f'<div class="book-synopsis">{escape(synopsis.strip())}</div>')
                html_parts.append('</div>')

        # Chapters
        chapters = _get_sorted_chapters(book_root)
        for chap in chapters:
            chap_num = chap.findtext("number", chap.get("id", "N/A"))
            chap_title = chap.findtext("title", "Untitled Chapter")
            
            html_parts.append('<div class="chapter">')
            html_parts.append(f'<h2 class="chapter-number">Chapter {escape(chap_num)}</h2>')
            html_parts.append(f'<h3 class="chapter-title">{escape(chap_title)}</h3>')
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

def export_html_per_chapter(book_root: ET.Element, output_parent_dir: Path, book_title_slug: str, console: Console, custom_font_name: str | None = None, custom_font_url: str | None = None):
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

        # Generate CSS with custom font
        css_content = _generate_css_with_font(custom_font_name, custom_font_url)
        
        # Generate font imports
        font_imports = ""
        if custom_font_url:
            font_imports = f'    <link href="{custom_font_url}" rel="stylesheet">\n'
        
        # Create an index file
        index_parts = []
        index_parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)} - Table of Contents</title>
{font_imports}    <style>
{css_content}
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
{font_imports}    <style>
{css_content}
.nav-link {{ color: #007bff; text-decoration: none; margin: 0 1em; }}
.nav-link:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div style="text-align: center; margin-bottom: 2em;">
        <a href="index.html" class="nav-link">← Table of Contents</a>
    </div>
     <div class="chapter">
         <h2 class="chapter-number">Chapter {escape(chap_num_str)}</h2>
         <h3 class="chapter-title">{escape(chap_title)}</h3>
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