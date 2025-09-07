# -*- coding: utf-8 -*-
"""
utils.py - General-purpose helper functions for the Fiction Fabricator project.
"""
import re
import unicodedata
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path

from rich.console import Console

def count_words(text: str) -> int:
    """Counts the number of words in a given string."""
    if not text or not text.strip():
        return 0
    return len(text.split())

def slugify(value: str, allow_unicode: bool = False) -> str:
    """
    Converts a string into a URL-friendly slug.

    Converts to ASCII if 'allow_unicode' is False. Converts spaces or repeated
    dashes to single dashes. Removes characters that aren't alphanumerics,
    underscores, or hyphens. Converts to lowercase. Also strips leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    value = re.sub(r"[-\s]+", "-", value).strip("-_")
    # Limit length and ensure not empty
    slug = value[:50] or "untitled"
    return slug

def pretty_xml(elem: ET.Element) -> str:
    """Returns a pretty-printed XML string for an ElementTree element."""
    try:
        rough_string = ET.tostring(elem, "utf-8")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    except Exception:
        # Fallback to basic tostring if pretty-printing fails
        return ET.tostring(elem, encoding="unicode")

def clean_llm_xml_output(xml_string: str) -> str:
    """
    Attempts to clean potential markdown fences or text surrounding LLM XML output.
    Also fixes common LLM XML formatting issues and attempts to repair truncated XML.
    """
    if not isinstance(xml_string, str):
        return ""
    # Find the first '<' and the last '>'
    start = xml_string.find("<")
    end = xml_string.rfind(">")
    if start != -1 and end != -1:
        cleaned = xml_string[start : end + 1].strip()
        # Remove markdown code fences
        cleaned = re.sub(r"^```xml\s*", "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        
        # Fix malformed attribute quotes (e.g., id="1\n" -> id="1")
        # Match attributes with quotes that have newlines or extra whitespace
        cleaned = re.sub(r'(\w+)="([^"]*?)\s*\n\s*"', r'\1="\2"', cleaned)
        
        # Fix specific case where paragraph IDs are split across lines
        # Pattern: id="4.22\n">  becomes id="4.22">
        cleaned = re.sub(r'(\w+)="([^"]*?)\s*\n\s*">', r'\1="\2">', cleaned)
        
        # Fix case where closing quote is completely missing after newline
        # Pattern: id="4.22\n">  becomes id="4.22">
        cleaned = re.sub(r'(\w+)="([^"]*?)\n">', r'\1="\2">', cleaned)
        
        # More aggressive fix for any attribute value with newlines in quotes
        # This handles cases like: attribute="value\nmore stuff"
        cleaned = re.sub(r'(\w+)="([^"]*?)\n([^"]*?)"', r'\1="\2\3"', cleaned)
        
        # Attempt to repair truncated XML for book outlines
        if cleaned.startswith('<book>') and not cleaned.rstrip().endswith('</book>'):
            # If the XML is truncated, try to repair it by closing open tags
            cleaned = _attempt_xml_repair(cleaned)
        
        return cleaned
    return xml_string  # Return original if no tags found

def _attempt_xml_repair(xml_string: str) -> str:
    """
    Attempts to repair truncated XML by closing open tags.
    """
    # Track open tags using a simple stack
    import re
    
    # Find all opening and closing tags
    tag_pattern = r'<(/?)(\w+)(?:\s[^>]*)?>'
    matches = re.findall(tag_pattern, xml_string)
    
    tag_stack = []
    for is_closing, tag_name in matches:
        if is_closing:  # Closing tag
            if tag_stack and tag_stack[-1] == tag_name:
                tag_stack.pop()
        else:  # Opening tag
            # Skip self-closing tags or tags that don't need closing
            if tag_name not in ['br', 'hr', 'img', 'input', 'meta', 'link']:
                tag_stack.append(tag_name)
    
    # Close any remaining open tags in reverse order
    repaired = xml_string
    for tag in reversed(tag_stack):
        repaired += f'</{tag}>'
    
    return repaired

def parse_xml_string(
    xml_string: str,
    console: Console,
    expected_root_tag: str = "patch",
    attempt_clean: bool = True
) -> ET.Element | None:
    """
    Safely parses an XML string, optionally cleaning it first.
    """
    if not xml_string:
        console.print("[bold red]Error: Received empty XML string from LLM.[/bold red]")
        return None

    if attempt_clean:
        xml_string = clean_llm_xml_output(xml_string)

    if not xml_string.strip():
        console.print("[bold red]Error: XML string is empty after cleaning.[/bold red]")
        return None

    try:
        # Heuristic: If expecting a patch and it's missing the root tag, wrap it.
        if expected_root_tag == "patch" and not xml_string.strip().startswith("<patch>"):
            if "<chapter" in xml_string and "</chapter>" in xml_string:
                console.print("[yellow]Warning: LLM output is missing root <patch> tag, attempting to wrap.[/yellow]")
                xml_string = f"<patch>{xml_string}</patch>"

        return ET.fromstring(xml_string)
    except ET.ParseError as e:
        console.print(f"[bold red]Error parsing XML (expecting <{expected_root_tag}>):[/bold red] {e}")
        console.print("[yellow]Attempted to parse:[/yellow]")
        
        # Show more context around the error for debugging
        error_line = getattr(e, 'lineno', None)
        if error_line:
            lines = xml_string.split('\n')
            start_line = max(0, error_line - 3)
            end_line = min(len(lines), error_line + 3)
            console.print("[dim]Context around error:[/dim]")
            for i in range(start_line, end_line):
                marker = ">>>" if i == error_line - 1 else "   "
                console.print(f"[dim]{marker} {i+1:3d}: {lines[i]}[/dim]")
        else:
            console.print(f"[dim]{xml_string[:2000]}{'...' if len(xml_string) > 2000 else ''}[/dim]")
        
        # Try to detect if this is a truncation issue
        if not xml_string.rstrip().endswith(f'</{expected_root_tag}>'):
            console.print(f"[yellow]Warning: XML appears to be truncated (missing closing </{expected_root_tag}> tag)[/yellow]")
            console.print("[yellow]This often indicates the LLM response was cut off due to token limits.[/yellow]")
        
        return None

def get_chapter_id(chapter_element) -> str:
    """
    Gets the chapter ID from either an attribute or child element.
    Returns the ID as a string, or empty string if not found.
    """
    return chapter_element.get("id") or chapter_element.findtext("id", "")

def get_chapter_id_with_default(chapter_element, default="N/A") -> str:
    """
    Gets the chapter ID from either an attribute or child element.
    Returns the ID as a string, or the default value if not found.
    """
    return chapter_element.get("id") or chapter_element.findtext("id", default)

def get_next_patch_number(book_dir: Path) -> int:
    """Finds the next available patch number based on existing files."""
    if not book_dir or not book_dir.is_dir():
        return 1
    try:
        patch_files = sorted(
            [p for p in book_dir.glob("patch-*.xml") if p.stem.split("-")[-1].isdigit()],
            key=lambda p: int(p.stem.split("-")[-1]),
        )
        if not patch_files:
            return 1
        last_patch = patch_files[-1].stem
        return int(last_patch.split("-")[-1]) + 1
    except (IndexError, ValueError):
        return len(list(book_dir.glob("patch-*.xml"))) + 1
