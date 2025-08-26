# File: Tools/ShortStoryWriter.py
# Purpose: Generates a complete short story using an iterative process.

import os
import sys
import datetime
import re

# --- Add src root to path for imports and determine repository root ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # This is the 'src' directory
repo_root = os.path.dirname(project_root)  # One level above 'src' is the repository root
sys.path.insert(0, project_root)

# --- Standardized Imports from Main Project ---
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger
from Writer.LLMUtils import get_llm_selection_menu_for_tool
import Writer.CritiqueRevision
import Writer.Config

# --- Short Story Prompts ---

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

import json
from Writer.NarrativeContext import NarrativeContext
from Writer.Scene.SceneFileManager import SceneFileManager

def sanitize_filename(name: str) -> str:
    """Sanitizes a string for use as a filename."""
    name = re.sub(r'[^\w\s-]', '', name).strip()
    name = re.sub(r'[-\s]+', '_', name)
    return name if name else "Untitled_Story"

def write_short_story(logger: Logger, interface: Interface, outline_file: str, temp: float = 0.75, max_iterations: int = 10, enable_critique_revision: bool = True):
    """
    Generates a complete short story from a pre-generated outline file using an iterative process.
    """
    generation_timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # --- Step 1: Load NarrativeContext from Outline ---
    logger.Log(f"Loading outline from: {outline_file}", 3)
    try:
        with open(outline_file, "r", encoding='utf-8') as f:
            narrative_context_dict = json.load(f)
        narrative_context = NarrativeContext.from_dict(narrative_context_dict)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.Log(f"Error loading or parsing outline file: {e}", 7)
        return

    premise = narrative_context.initial_prompt
    outline = narrative_context.base_novel_outline_markdown
    lore_book_content = narrative_context.lore_book_content

    if not outline:
        logger.Log("The selected outline file does not contain a valid outline. Exiting.", 7)
        return

    lore_book_section = LORE_BOOK_PROMPT_SECTION.format(lore_book_content=lore_book_content) if lore_book_content else ""

    selected_model_uri = get_llm_selection_menu_for_tool(logger, "Short Story Writer")
    if not selected_model_uri:
        return

    # Get critique/revision model selection
    critique_model_uri = None
    if enable_critique_revision:
        print("\nSelect model for critique and revision (can be same as writing model):")
        critique_model_uri = get_llm_selection_menu_for_tool(logger, "Short Story Critique & Revision")
        if not critique_model_uri:
            logger.Log("No critique model selected. Disabling critique/revision cycle.", 6)
            enable_critique_revision = False

    interface.LoadModels([selected_model_uri] + ([critique_model_uri] if critique_model_uri and critique_model_uri != selected_model_uri else []))
    model_with_params = f"{selected_model_uri}?temperature={temp}&max_tokens=2000"

    # --- Step 2: Generate Title (if needed) and Start of Story ---
    # The title is now derived from the outline file name or generated if needed
    base_filename = os.path.basename(outline_file).rsplit('.', 1)[0]
    # Clean up timestamp if present
    title = base_filename.replace('_', ' ')
    
    logger.Log(f"Title: {title}", 5)
    logger.Log(f"Outline:\n{outline}", 4)

    logger.Log("Generating the beginning of the story...", 2)
    start_prompt = STARTING_PROMPT_TEMPLATE.format(persona=PERSONA, premise=premise, title=title, outline=outline, guidelines=GUIDELINES, lore_book_section=lore_book_section)
    response_history = interface.SafeGenerateText(logger, [interface.BuildUserQuery(start_prompt)], model_with_params, min_word_count_target=500)
    story_draft = interface.GetLastMessageText(response_history)

    # --- Step 3: Iteratively Continue Story ---
    logger.Log("Continuing story generation iteratively...", 2)
    iteration_count = 1
    while 'IAMDONE' not in story_draft and iteration_count <= max_iterations:
        logger.Log(f"--- Continuing generation (Iteration {iteration_count}) ---", 3)
        continuation_prompt = CONTINUATION_PROMPT_TEMPLATE.format(
            persona=PERSONA, premise=premise, title=title, outline=outline, story_text=story_draft, guidelines=GUIDELINES, lore_book_section=lore_book_section
        )
        response_history = interface.SafeGenerateText(logger, [interface.BuildUserQuery(continuation_prompt)], model_with_params, min_word_count_target=500)
        continuation = interface.GetLastMessageText(response_history)
        story_draft += '\n\n' + continuation
        iteration_count += 1

    if iteration_count > max_iterations:
        logger.Log(f"Reached max iterations ({max_iterations}). Story may be incomplete.", 6)

    logger.Log("Story generation complete.", 5)

    # --- Step 4: Critique and Revision Cycle ---
    final_story = story_draft.replace('IAMDONE', '').strip()
    
    if enable_critique_revision and critique_model_uri:
        logger.Log("Starting critique and revision cycle for short story...", 2)
        
        task_description = f"You are reviewing a complete short story titled '{title}'. The story should be a compelling, well-structured narrative that follows the provided outline and maintains consistent style, pacing, and character development throughout."
        
        narrative_context_summary = f"Title: {title}\nPremise: {premise}\nOutline:\n{outline}"
        if lore_book_content:
            narrative_context_summary += f"\nLore Book Context: {lore_book_content[:500]}..."  # Truncate for summary
            
        revised_story = Writer.CritiqueRevision.critique_and_revise_creative_content(
            interface,
            logger,
            initial_content=final_story,
            task_description=task_description,
            narrative_context_summary=narrative_context_summary,
            initial_user_prompt=premise,
            style_guide=GUIDELINES,  # Use the short story guidelines as style guide
            selected_model=critique_model_uri,
            justification="Short story critique and revision cycle"
        )
        
        if revised_story and not "[ERROR:" in revised_story:
            final_story = revised_story
            logger.Log("Critique and revision cycle completed successfully.", 5)
        else:
            logger.Log("Critique and revision cycle failed. Using original story.", 6)
    elif enable_critique_revision:
        logger.Log("Critique and revision was enabled but no model was selected. Skipping.", 6)
    else:
        logger.Log("Critique and revision disabled. Using original story.", 4)

    # --- Step 5: Finalize and Save with Scene-Based File Management ---

    output_dir = os.path.join(repo_root, "Generated_Content", "Short_Story")
    os.makedirs(output_dir, exist_ok=True)

    safe_title = sanitize_filename(title)
    
    # Initialize file manager for error-resilient output
    file_manager = SceneFileManager(logger, output_dir, safe_title)
    
    # Create a mock narrative context for the short story to use file manager
    short_story_context = NarrativeContext(initial_prompt=premise, style_guide=GUIDELINES, lore_book_content=lore_book_content)
    short_story_context.story_type = "short_story"
    
    # Create a single chapter context for the entire short story
    from Writer.NarrativeContext import ChapterContext, SceneContext
    chapter_context = ChapterContext(chapter_number=1, initial_outline=outline)
    chapter_context.set_generated_content(final_story)
    chapter_context.set_summary(f"Complete short story: {title}")
    
    # Create a single scene context containing the entire story
    scene_context = SceneContext(scene_number=1, initial_outline=outline)
    scene_context.add_piece(final_story, f"Complete short story: {title}")
    scene_context.set_final_summary(f"Complete short story: {title}")
    
    chapter_context.add_scene(scene_context)
    short_story_context.add_chapter(chapter_context)
    
    # Save individual files using the file manager
    scene_file_path = file_manager.save_scene_file(scene_context, 1, len(final_story.split()))
    chapter_file_path = file_manager.stitch_chapter_from_scenes(chapter_context)
    book_file_path = file_manager.stitch_book_from_chapters(short_story_context, title)
    report_file_path = file_manager.create_generation_report(short_story_context)

    # Also save the traditional format
    output_filename = f"{safe_title}_{generation_timestamp}.md"
    output_path = os.path.join(output_dir, output_filename)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            f.write(f"**Premise:** {premise}\n\n")
            if lore_book_content:
                f.write(f"**Lore Book:** Used from outline\n\n")
            f.write(f"**Generated on:** {generation_timestamp}\n\n")
            f.write("---\n\n")
            f.write(f"## Outline\n\n{outline}\n\n")
            f.write("---\n\n")
            f.write(final_story)
        logger.Log(f"Successfully saved short story to: {output_path}", 5)
    except Exception as e:
        logger.Log(f"Error saving story to file: {e}", 7)

    # Get all generated files for final summary
    all_files = file_manager.get_all_output_files()

    logger.Log("Short story generation complete!", 5)
    final_message = f"""
--- Short Story Generation Complete with Error-Resilient Output ---

Main Story File: {output_path}

Scene-Based Files Created:
- Scene File: {scene_file_path or 'Failed to create'}
- Chapter File: {chapter_file_path or 'Failed to create'}  
- Complete Book: {book_file_path or 'Failed to create'}
- Generation Report: {report_file_path or 'Failed to create'}

Total Files: Scene({len(all_files.get('scenes', []))}), Chapter({len(all_files.get('chapters', []))}), Book({len(all_files.get('book', []))})

All files are preserved individually to prevent data loss!
"""
    print(final_message)


