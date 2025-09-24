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
        
        # Fix malformed attribute quotes with comprehensive patterns
        # Pattern 1: id="value\n" -> id="value"
        cleaned = re.sub(r'(\w+)="([^"]*?)\s*\n\s*"', r'\1="\2"', cleaned)
        
        # Pattern 2: id="value\n"> -> id="value">
        cleaned = re.sub(r'(\w+)="([^"]*?)\s*\n\s*">', r'\1="\2">', cleaned)
        
        # Pattern 3: id="value\nother_text" -> id="valueother_text" (no space for IDs)
        cleaned = re.sub(r'(\w+)="([^"]*?)\n([^"]*?)"', lambda m: f'{m.group(1)}="{m.group(2)}{m.group(3)}"' if m.group(1) == 'id' else f'{m.group(1)}="{m.group(2)} {m.group(3)}"', cleaned)
        
        # Pattern 4: Fix cases where the newline is within the tag itself
        # Example: <paragraph id="2\n1"> -> <paragraph id="21">
        cleaned = re.sub(r'(<\w+[^>]*?\s+\w+=")([^"]*?)\n([^"]*?)(")', r'\1\2\3\4', cleaned)
        
        # Pattern 5: Fix newlines breaking the opening tag
        # Example: <paragraph id="2\n1">content -> <paragraph id="21">content
        cleaned = re.sub(r'(<\w+[^>]*?)\n([^<>]*?>)', r'\1\2', cleaned)
        
        # Fix unwanted line breaks within paragraph content with more comprehensive cleaning
        def fix_paragraph_content(match):
            full_para = match.group(0)
            
            # First, fix any structural issues in the paragraph tag itself
            # Handle cases where attributes are split across lines
            para_fixed = re.sub(r'(<paragraph[^>]*?)\n([^<>]*?>)', r'\1\2', full_para)
            
            # Now fix content line breaks - be more aggressive
            # Replace line breaks that are NOT after sentence endings with spaces
            content_pattern = r'>(.*?)<'
            def fix_content(content_match):
                content = content_match.group(1)
                # Replace newlines with spaces unless they follow sentence endings
                # Keep breaks after: . ! ? " or if the next line starts with a capital (new sentence)
                fixed_content = re.sub(r'(?<![.!?"\n])\n(?!\s*[A-Z"])', ' ', content)
                # Clean up multiple spaces
                fixed_content = re.sub(r'  +', ' ', fixed_content)
                return f'>{fixed_content}<'
            
            para_fixed = re.sub(content_pattern, fix_content, para_fixed, flags=re.DOTALL)
            return para_fixed
        
        # Apply the fix to all paragraph elements
        cleaned = re.sub(r'<paragraph[^>]*>.*?</paragraph>', fix_paragraph_content, cleaned, flags=re.DOTALL)
        
        # Additional patterns to fix specific XML formatting issues
        
        # Fix cases where paragraph opening tags are broken across lines
        # Example: <paragraph id="2\n1"> -> <paragraph id="21">
        cleaned = re.sub(r'<paragraph\s+id="([^"]*?)\n([^"]*?)">', r'<paragraph id="\1\2">', cleaned)
        
        # Fix any XML tag that has been split across lines
        # Pattern: <tag attr="val\nue"> -> <tag attr="value">
        cleaned = re.sub(r'(<\w+[^>]*?="[^"]*?)\n([^"]*?"[^>]*?>)', r'\1\2', cleaned)
        
        # Handle cases where the paragraph content starts on the next line after the tag
        # Pattern: <paragraph id="1">\nContent -> <paragraph id="1">Content
        cleaned = re.sub(r'(<paragraph[^>]*>)\s*\n\s*([A-Z])', r'\1\2', cleaned)
        
        # Clean up multiple spaces that might result from the above fixes
        cleaned = re.sub(r'  +', ' ', cleaned)
        
        # Attempt to repair truncated XML for patches and book outlines
        if cleaned.startswith('<patch>') and not cleaned.rstrip().endswith('</patch>'):
            # If the patch XML is truncated, try to repair it by closing open tags
            cleaned = _attempt_xml_repair(cleaned)
        elif cleaned.startswith('<book>') and not cleaned.rstrip().endswith('</book>'):
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
            
            # Try to repair truncated XML automatically
            if expected_root_tag in ["patch", "book"]:
                console.print("[yellow]Attempting to repair truncated XML...[/yellow]")
                repaired_xml = _attempt_xml_repair(xml_string)
                if repaired_xml != xml_string:
                    try:
                        return ET.fromstring(repaired_xml)
                    except ET.ParseError:
                        console.print("[yellow]Automatic repair failed.[/yellow]")
        
        return None

def clean_paragraph_text(text: str) -> str:
    """
    Cleans paragraph text by removing unwanted line breaks while preserving intentional formatting.
    """
    if not text:
        return text
    
    # Remove line breaks that are not after sentence endings or dialogue
    # Keep breaks after: . ! ? " and at the start/end of paragraphs
    cleaned = re.sub(r'(?<![.!?"\n])\n(?=\s*[a-z])', ' ', text)
    
    # Clean up multiple spaces
    cleaned = re.sub(r'  +', ' ', cleaned)
    
    # Clean up trailing/leading whitespace while preserving intentional breaks
    cleaned = cleaned.strip()
    
    return cleaned

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
