# -*- coding: utf-8 -*-
"""
novel.py - Contains the specific logic for generating a novel outline.
"""
import xml.etree.ElementTree as ET
from rich.panel import Panel

from src.llm_client import LLMClient
from src.project import Project
from src import ui

def generate_outline(llm_client: LLMClient, project: Project, lorebook_context: str = ""):
    """
    Guides the LLM to generate a full book outline with characters and chapter summaries.
    Returns a new book_root ElementTree object or None on failure.
    """
    ui.console.print(Panel("Generating Novel Outline", style="bold blue"))

    # Get required info from the user
    num_chapters = ui.prompt_for_chapter_count()
    
    current_book_xml_for_prompt = ET.tostring(project.book_root, encoding="unicode")

    prompt = f"""
You are a creative assistant tasked with expanding a book concept into a detailed novel outline.
The current state of the book is:
```xml
{current_book_xml_for_prompt}
```

{lorebook_context}

Based on the title, synopsis, and initial idea, please generate a full outline:
1. Keep the existing title and synopsis exactly as provided
2. Create a condensed version of the initial_idea (maximum 500 words) that captures the key plot points
3. A `<story_elements>` section with:
   - `<genre>`: Primary genre(s) (e.g., "Dark Fantasy", "Psychological Thriller", "Science Fiction")
   - `<tone>`: Overall tone (e.g., "Dark and foreboding", "Light and humorous", "Intense and suspenseful")
   - `<perspective>`: Narrative perspective (e.g., "First person", "Third person limited", "Third person omniscient")
   - `<target_audience>`: Intended audience (e.g., "Adult", "Young Adult", "General Fiction readers")
4. A `<characters>` section with multiple `<character>` elements (with `id`, `name`, `description`)
5. A `<chapters>` section with approximately {num_chapters} `<chapter>` elements:
   - Each chapter needs a unique sequential string `id` (e.g., '1', '2', ...)
   - Each chapter opening tag must include a `setting` attribute with a brief description of the primary location/setting (e.g., <chapter id="1" setting="The dark forest near the village">)
   - Include `<number>`, `<title>`, and a detailed `<summary>` (150-200 words)
   - The `<content>` tag for each chapter must be present but EMPTY
   - Ensure the summaries form a coherent narrative arc and settings progress logically through the story

IMPORTANT XML REQUIREMENTS:
- Output ONLY valid XML starting with `<book>` and ending with `</book>`
- All XML content must be properly escaped (use &amp; for &, &lt; for <, &gt; for >, &quot; for ")
- No text before or after the XML tags
- Ensure all tags are properly closed and nested
- Keep content concise to avoid truncation

Output the complete `<book>` XML structure with condensed initial_idea, story_elements, and new characters/chapters sections.
"""
    response_xml_str = llm_client.get_response(prompt, "Generating full novel outline")

    if not response_xml_str:
        ui.console.print("[bold red]Failed to get a valid response from the LLM for the outline.[/bold red]")
        return None

    # The orchestrator will handle parsing and validation
    return response_xml_str
