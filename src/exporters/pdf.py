# -*- coding: utf-8 -*-
"""
pdf.py - Handles exporting the project to PDF format.
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from html import unescape
from datetime import datetime

from rich.console import Console

from src import utils

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_RIGHT
    reportlab_available = True
except ImportError:
    reportlab_available = False

def _get_sorted_chapters(book_root: ET.Element) -> list[ET.Element]:
    """Helper to get chapters sorted numerically by ID."""
    if book_root is None:
        return []
    chapters_raw = book_root.findall(".//chapter")
    try:
        return sorted(chapters_raw, key=lambda chap: int(chap.get("id", "0")))
    except ValueError:
        return chapters_raw

def export_pdf(book_root: ET.Element, output_path: Path, console: Console, custom_font_name: str | None = None, custom_font_url: str | None = None):
    """Exports the entire book content to a PDF file."""
    if not reportlab_available:
        console.print("[bold red]PDF Export Failed: 'reportlab' is not installed.[/bold red]")
        console.print("[bold red]Please run: uv add reportlab[/bold red]")
        return

    if book_root is None:
        console.print("[red]Error: Book data is missing, cannot export.[/red]")
        return

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles with font support
        base_title_fontname = custom_font_name if custom_font_name and custom_font_name in ['Helvetica', 'Times-Roman', 'Courier'] else 'Helvetica-Bold'
        base_heading_fontname = custom_font_name if custom_font_name and custom_font_name in ['Helvetica', 'Times-Roman', 'Courier'] else 'Helvetica-Bold'
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName=base_title_fontname
        )
        
        chapter_number_style = ParagraphStyle(
            'ChapterNumber',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=6,
            alignment=TA_RIGHT,
            keepWithNext=1,
            fontName=base_heading_fontname
        )
        
        chapter_title_style = ParagraphStyle(
            'ChapterTitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=18,
            alignment=TA_RIGHT,
            keepWithNext=1,
            fontName=base_heading_fontname
        )
        
        paragraph_style = ParagraphStyle(
            'CustomParagraph',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            firstLineIndent=18
        )
        
        frontmatter_style = ParagraphStyle(
            'Frontmatter',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_CENTER
        )
        
        # Story elements
        story = []
        title = book_root.findtext("title", "Untitled Book")
        
        # Add frontmatter sections if they exist and have content
        frontmatter = book_root.find("frontmatter")
        if frontmatter is not None:
            # Title Page
            title_page = frontmatter.findtext("title_page")
            if title_page and title_page.strip():
                lines = title_page.strip().split('\n')
                for line in lines:
                    if line.strip():
                        story.append(Paragraph(unescape(line.strip()), title_style))
                        story.append(Spacer(1, 12))
                story.append(PageBreak())
            
            # Copyright Page
            copyright_page = frontmatter.findtext("copyright_page")
            if copyright_page and copyright_page.strip():
                story.append(Paragraph(unescape(copyright_page.strip()), frontmatter_style))
                story.append(PageBreak())
            
            # Dedication
            dedication = frontmatter.findtext("dedication")
            if dedication and dedication.strip():
                story.append(Paragraph("Dedication", styles['Heading2']))
                story.append(Spacer(1, 12))
                story.append(Paragraph(unescape(dedication.strip()), frontmatter_style))
                story.append(PageBreak())
            
            # Acknowledgements
            acknowledgements = frontmatter.findtext("acknowledgements")
            if acknowledgements and acknowledgements.strip():
                story.append(Paragraph("Acknowledgements", styles['Heading2']))
                story.append(Spacer(1, 12))
                story.append(Paragraph(unescape(acknowledgements.strip()), styles['Normal']))
                story.append(PageBreak())
        
        # Add main title if no custom title page was provided
        has_custom_title_page = False
        if frontmatter is not None:
            title_page_text = frontmatter.findtext("title_page")
            has_custom_title_page = title_page_text and title_page_text.strip()
        
        if not has_custom_title_page:
            story.append(Paragraph(unescape(title), title_style))
            story.append(Spacer(1, 30))
            
            synopsis = book_root.findtext("synopsis")
            if synopsis:
                story.append(Paragraph("Synopsis", styles['Heading2']))
                story.append(Spacer(1, 12))
                story.append(Paragraph(unescape(synopsis.strip()), styles['Normal']))
                story.append(Spacer(1, 30))
        
        # Chapters
        chapters = _get_sorted_chapters(book_root)
        for i, chap in enumerate(chapters):
            if i > 0:  # Add page break before each chapter (except the first)
                story.append(PageBreak())
                
            chap_num = chap.findtext("number", chap.get("id", "N/A"))
            chap_title = chap.findtext("title", "Untitled Chapter")
            
            story.append(Paragraph(f"Chapter {unescape(chap_num)}", chapter_number_style))
            story.append(Paragraph(unescape(chap_title), chapter_title_style))
            story.append(Spacer(1, 18))
            
            content = chap.find("content")
            if content is not None:
                paragraphs = content.findall(".//paragraph")
                if paragraphs:
                    for para in paragraphs:
                        para_text = (para.text or "").strip()
                        if para_text:
                            story.append(Paragraph(unescape(para_text), paragraph_style))
                else:
                    story.append(Paragraph("[Chapter content missing]", styles['Italic']))
            else:
                story.append(Paragraph("[Chapter content missing]", styles['Italic']))
        
        # Build PDF
        doc.build(story)
        
        console.print(f"[green]Successfully exported PDF file to:[/green] [cyan]{output_path.resolve()}[/cyan]")
        
    except Exception as e:
        console.print(f"[bold red]Error exporting PDF file: {e}[/bold red]")