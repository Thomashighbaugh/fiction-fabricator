# File: Tools/ShortStoryWriter.py
# Purpose: Generates a complete short story using an iterative process.
# This script is self-contained and should be run from the project's root directory.

"""
FictionFabricator Short Story Writer.

This tool takes a single premise and uses an LLM to generate a complete,
self-contained short story. It follows an iterative generation process.

The process involves:
1. Dynamically selecting an LLM from available providers.
2. Generating a title and a structured 5-point outline from the user's premise.
3. Writing the beginning of the story.
4. Iteratively generating the rest of the story in chunks until the LLM
   signals completion by outputting 'IAMDONE'.
5. Saving the final story to the `Short_Story/` directory.

Usage:
python Tools/ShortStoryWriter.py --premise "A librarian discovers that every book is a portal to the world it describes, but can only enter a book once."
"""

import argparse
import os
import sys
import datetime
import re

# --- Add project root to path for imports and load .env explicitly ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# dotenv is loaded by the centralized utilities, but we'll try here too for robustness.
try:
    from dotenv import load_dotenv
    dotenv_path = os.path.join(project_root, '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path)
        print(f"--- Successfully loaded .env file from: {dotenv_path} ---")
    else:
        print("--- .env file not found, proceeding with environment variables if available. ---")
except (ImportError, Exception) as e:
    print(f"--- Info: Could not load .env file: {e} ---")

# --- Standardized Imports from Main Project ---
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger
# --- Refactored Import for Centralized LLM Utilities ---
from Writer.LLMUtils import get_llm_selection_menu_for_tool


# --- Short Story Prompts (Refactored for Better Structure) ---

PERSONA = """
You are a celebrated author of short stories, known for crafting concise yet deeply impactful narratives that linger in the reader's mind. Your goal is to write a complete, compelling short story from beginning to end, following a clear narrative structure.
"""

GUIDELINES = """
## Writing Guidelines

- **Focus on Brevity and Impact:** Every sentence must count. Focus on a single, compelling narrative arc.
- **Show, Don't Tell:** Use vivid descriptions and character actions to convey emotion and plot.
- **Complete Arc:** The story must have a clear beginning, rising action, climax, falling action, and a definitive resolution, as defined in your outline.
- **Embrace the Premise:** Fully explore the core concept of the premise within the confines of the short story format.
"""

LORE_BOOK_PROMPT_SECTION = """
**Lore Book (Context):**
---
{lore_book_content}
---
"""

TITLE_AND_OUTLINE_PROMPT_TEMPLATE = """
{persona}

You have been given a gripping premise for a short story:

**Premise:** "{premise}"
{lore_book_section}
Your first task is to:
1.  **Create a Title:** Generate a fitting and evocative title for this short story.
2.  **Create a 5-Point Outline:** Write a clear, bullet-point outline covering the five essential plot points of a complete narrative arc.

Your entire response must be in the following format, with nothing else:

**Title:** [Your Title Here]

**Outline:**
- **Beginning:** [Introduce the main character, setting, and the inciting incident.]
- **Rising Action:** [Describe the series of events and conflicts that build tension and lead to the climax.]
- **Climax:** [Detail the story's peak, the main turning point for the protagonist.]
- **Falling Action:** [Explain the immediate aftermath of the climax.]
- **Resolution:** [Provide a definitive conclusion, showing the final outcome for the protagonist.]
"""

STARTING_PROMPT_TEMPLATE = """
{persona}

**Premise:** "{premise}"

**Title:** "{title}"
{lore_book_section}
**Your Full Outline (Roadmap):**
---
{outline}
---

{guidelines}

---
First, silently review the outline and premise.

Now, begin writing the story. Your task is to write the **Beginning** of the story, covering the start of your outline. Write at least 500 words. Do **not** finish the entire story now.
"""

CONTINUATION_PROMPT_TEMPLATE = """
{persona}

**Premise:** "{premise}"

**Title:** "{title}"
{lore_book_section}
**Your Full Outline (Roadmap):**
---
{outline}
---

**Here is the story you have written so far:**
---
{story_text}
---

{guidelines}

---
First, silently review the story so far and your full outline. Identify the next logical part of the outline to write (e.g., if you just wrote the 'Beginning', now write the 'Rising Action').

Your task is to continue where the story left off. Write the next section, moving the plot forward according to your outline. Write at least 500 words.

**IMPORTANT:** Once the story's conclusion (the **Resolution**) is fully written and the narrative is complete based on your outline, and only then, write the exact phrase `IAMDONE` on a new line at the very end of your response. Do NOT write `IAMDONE` if you are only writing the rising action or climax.
"""

def sanitize_filename(name: str) -> str:
    """Sanitizes a string for use as a filename."""
    name = re.sub(r'[^\w\s-]', '', name).strip()
    name = re.sub(r'[-\s]+', '_', name)
    return name if name else "Untitled_Story"

def write_short_story(premise: str, temp: float = 0.75, max_iterations: int = 10, lore_book: str = None):

    generation_timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    sys_logger = Logger("ShortStoryLogs")

    lore_book_content = None
    if lore_book:
        try:
            with open(lore_book, "r", encoding='utf-8') as f:
                lore_book_content = f.read()
            sys_logger.Log(f"Successfully loaded lore book: {lore_book}", 3)
        except FileNotFoundError:
            sys_logger.Log(f"Error: Lore book file not found at {lore_book}", 7)
            return

    lore_book_section = LORE_BOOK_PROMPT_SECTION.format(lore_book_content=lore_book_content) if lore_book_content else ""

    selected_model_uri = get_llm_selection_menu_for_tool(sys_logger, "Short Story Writer")
    if not selected_model_uri:
        sys.exit(1)

    interface = Interface()
    interface.LoadModels([selected_model_uri])
    model_with_params = f"{selected_model_uri}?temperature={temp}&max_tokens=2000"

    # --- Step 1: Generate Title and Outline ---
    sys_logger.Log("Generating title and a structured 5-point outline...", 2)
    title_prompt = TITLE_AND_OUTLINE_PROMPT_TEMPLATE.format(persona=PERSONA, premise=premise, lore_book_section=lore_book_section)
    response_history = interface.SafeGenerateText(sys_logger, [interface.BuildUserQuery(title_prompt)], model_with_params, min_word_count_target=50)
    title_and_outline_text = interface.GetLastMessageText(response_history)

    try:
        title = re.search(r"Title:\s*(.*)", title_and_outline_text, re.IGNORECASE).group(1).strip()
        outline = title_and_outline_text.split("Outline:")[1].strip()
    except (AttributeError, IndexError):
        sys_logger.Log("Failed to parse title and outline from the LLM response. Exiting.", 7)
        print("--- LLM Response ---")
        print(title_and_outline_text)
        print("--------------------")
        sys.exit(1)

    sys_logger.Log(f"Title: {title}", 5)
    sys_logger.Log(f"Outline:\n{outline}", 4)

    # --- Step 2: Generate Start of Story ---
    sys_logger.Log("Generating the beginning of the story...", 2)
    start_prompt = STARTING_PROMPT_TEMPLATE.format(persona=PERSONA, premise=premise, title=title, outline=outline, guidelines=GUIDELINES, lore_book_section=lore_book_section)
    response_history = interface.SafeGenerateText(sys_logger, [interface.BuildUserQuery(start_prompt)], model_with_params, min_word_count_target=500)
    story_draft = interface.GetLastMessageText(response_history)


    # --- Step 3: Iteratively Continue Story ---
    sys_logger.Log("Continuing story generation iteratively...", 2)
    iteration_count = 1
    while 'IAMDONE' not in story_draft and iteration_count <= max_iterations:
        sys_logger.Log(f"--- Continuing generation (Iteration {iteration_count}) ---", 3)
        continuation_prompt = CONTINUATION_PROMPT_TEMPLATE.format(
            persona=PERSONA, premise=premise, title=title, outline=outline, story_text=story_draft, guidelines=GUIDELINES, lore_book_section=lore_book_section
        )
        response_history = interface.SafeGenerateText(sys_logger, [interface.BuildUserQuery(continuation_prompt)], model_with_params, min_word_count_target=500)
        continuation = interface.GetLastMessageText(response_history)
        story_draft += '\n\n' + continuation
        iteration_count += 1

    if iteration_count > max_iterations:
        sys_logger.Log(f"Reached max iterations ({max_iterations}). Story may be incomplete.", 6)

    sys_logger.Log("Story generation complete.", 5)

    # --- Step 4: Finalize and Save ---
    final_story = story_draft.replace('IAMDONE', '').strip()

    output_dir = os.path.join(project_root, "Generated_Content", "Short_Story")
    os.makedirs(output_dir, exist_ok=True)

    safe_title = sanitize_filename(title)
    output_filename = f"{safe_title}_{generation_timestamp}.md"
    output_path = os.path.join(output_dir, output_filename)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            f.write(f"**Premise:** {premise}\n\n")
            if lore_book_content:
                f.write(f"**Lore Book:** {os.path.basename(lore_book)}\n\n")
            f.write(f"**Generated on:** {generation_timestamp}\n\n")
            f.write("---\n\n")
            f.write(f"## Outline\n\n{outline}\n\n")
            f.write("---\n\n")
            f.write(final_story)
        sys_logger.Log(f"Successfully saved short story to: {output_path}", 5)
    except Exception as e:
        sys_logger.Log(f"Error saving story to file: {e}", 7)

    print(f"\n--- Short Story Generation Complete. Find your story at: {output_path} ---")


