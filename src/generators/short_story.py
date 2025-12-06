# -*- coding: utf-8 -*-
"""
short_story.py - Contains the specific logic for generating a short story outline.
"""
import xml.etree.ElementTree as ET
from rich.panel import Panel

from src.llm_client import LLMClient
from src.project import Project
from src import ui

def generate_outline(llm_client: LLMClient, project: Project, lorebook_context: str = ""):
    """
    Guides the LLM to generate a short story outline with characters and scene summaries.
    Returns a new book_root ElementTree object or None on failure.
    """
    ui.console.print(Panel("Generating Short Story Outline", style="bold blue"))

    # For a short story, we'll aim for a fixed number of scenes (e.g., 3-5)
    num_scenes = 5 
    
    current_book_xml_for_prompt = ET.tostring(project.book_root, encoding="unicode")

    prompt = f"""
You are a creative assistant tasked with expanding a concept into a short story outline.
The current state of the project is:
```xml
{current_book_xml_for_prompt}
```

{lorebook_context}

Based on the title, synopsis, and initial idea, please generate a complete outline for a short story:
1. Keep the existing title and synopsis exactly as provided
2. A `<story_elements>` section with:
   - `<genre>`: Primary genre(s) (e.g., "Literary Fiction", "Mystery", "Romance")
   - `<tone>`: Overall tone (e.g., "Melancholic", "Suspenseful", "Uplifting")
   - `<perspective>`: Narrative perspective (e.g., "First person", "Third person limited", "Third person omniscient")
   - `<target_audience>`: Intended audience (e.g., "Adult", "Literary fiction readers", "General audience")
3. A `<characters>` section with the main characters (`id`, `name`, `description`).
4. A `<chapters>` section containing exactly {num_scenes} `<chapter>` elements. Treat each chapter as a distinct 'Scene' of the short story.
   * Each scene/chapter needs a unique sequential string `id` (e.g., '1', '2', ...).
   * Each chapter opening tag must include a `setting` attribute with a brief description of the primary location/setting (e.g., <chapter id="1" setting="A dimly lit cafe on a rainy evening">)
   * Include `<number>`, a descriptive `<title>` for the scene, and a detailed `<summary>` (100-150 words) outlining the key events of that scene.
   * The `<content>` tag for each scene/chapter must be present but EMPTY.
   * The summaries should follow a clear narrative structure (e.g., Beginning, Inciting Incident, Rising Action, Climax, Resolution) with settings that progress logically.

Output ONLY the complete `<book>` XML structure, merging the generated details. Do not include any text outside the `<book>` tags.
"""
    response_xml_str = llm_client.get_response(prompt, "Generating short story outline")

    if not response_xml_str:
        ui.console.print("[bold red]Failed to get a valid response from the LLM for the outline.[/bold red]")
        return None

    # The orchestrator will handle parsing and validation
    return response_xml_str

