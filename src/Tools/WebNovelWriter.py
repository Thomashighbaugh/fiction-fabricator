#!/usr/bin/python3
import time
import os
import sys
import json
import termcolor

# --- Add necessary paths ---
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger
import Writer.Config
import Writer.Chapter.ChapterGenerator
import Writer.StoryInfo
import Writer.Prompts
from Writer.NarrativeContext import NarrativeContext
from Writer.LLMUtils import get_llm_selection_menu_for_tool

def write_web_novel_chapter(logger: Logger, interface: Interface, prompt_file: str, chapter_number: int, lore_book: str = None):
    """
    Writes a single chapter of a web novel, maintaining context from previous chapters.
    """
    StartTime = time.time()
    logger.Log(f"Welcome to the {Writer.Config.PROJECT_NAME} Web Novel Chapter Generator!", 2)

    # --- Configuration and Model Selection ---
    # Unlike NovelWriter, WebNovel is more interactive, so we select a model each time.
    selected_model = get_llm_selection_menu_for_tool(logger, "Web Novel Chapter Writer")
    if not selected_model:
        return
    interface.LoadModels([selected_model])

    # --- Determine Story Name and Paths ---
    story_name = os.path.splitext(os.path.basename(prompt_file))[0]
    story_dir = os.path.join("Generated_Content", "Web_Novel_Chapters", story_name)
    os.makedirs(story_dir, exist_ok=True)
    context_file_path = os.path.join(story_dir, f"{story_name}_context.json")

    # --- Load or Initialize Narrative Context ---
    narrative_context = None
    if os.path.exists(context_file_path):
        logger.Log(f"Found existing context file: {os.path.basename(context_file_path)}", 3)
        try:
            with open(context_file_path, "r", encoding='utf-8') as f:
                narrative_context = NarrativeContext.from_dict(json.load(f))
            logger.Log("Successfully loaded previous context.", 3)
        except (json.JSONDecodeError, TypeError) as e:
            logger.Log(f"Error decoding context file: {e}. A new context will be created.", 6)

    if narrative_context is None:
        logger.Log("Creating new narrative context from prompt file.", 3)
        try:
            with open(prompt_file, "r", encoding='utf-8') as f:
                prompt_content = f.read()
        except FileNotFoundError:
            logger.Log(f"Error: Prompt file not found at {prompt_file}", 7)
            return
        
        lore_book_content = None
        if lore_book:
            try:
                with open(lore_book, "r", encoding='utf-8') as f:
                    lore_book_content = f.read()
            except FileNotFoundError:
                logger.Log(f"Warning: Lore book file not found at {lore_book}", 6)

        narrative_context = NarrativeContext(
            initial_prompt=prompt_content,
            style_guide=Writer.Prompts.LITERARY_STYLE_GUIDE,
            lore_book_content=lore_book_content
        )
        # For web novels, the entire prompt is treated as the base outline
        narrative_context.base_novel_outline_markdown = prompt_content

    # --- Chapter Generation ---
    # Check if the requested chapter has already been generated
    if any(chap.chapter_number == chapter_number for chap in narrative_context.chapters):
        logger.Log(f"Chapter {chapter_number} has already been generated. To regenerate, please remove it from the context file first.", 6)
        return

    logger.Log(f"Starting Generation for Chapter {chapter_number}...", 2)
    
    # The total number of chapters is unknown, so we pass 0.
    # The model is passed directly to the chapter generator.
    Writer.Chapter.ChapterGenerator.GenerateChapter(interface, logger, chapter_number, 0, narrative_context, selected_model)

    # --- Finalization and Saving ---
    if not narrative_context.chapters or narrative_context.chapters[-1].chapter_number != chapter_number:
        logger.Log(f"Chapter {chapter_number} generation failed. No new content was produced.", 7)
        return

    # Save the updated full context
    with open(context_file_path, "w", encoding="utf-8") as f:
        json.dump(narrative_context.to_dict(), f, indent=4)
    logger.Log(f"Updated story context saved to: {os.path.basename(context_file_path)}", 2)

    # Save the individual chapter files
    new_chapter = narrative_context.chapters[-1]
    chapter_content = new_chapter.generated_content
    Title = f"Chapter {chapter_number}"

    logger.Log(f"Chapter Title: {Title}", 5)
    ElapsedTime = time.time() - StartTime
    TotalWords = len(chapter_content.split())
    logger.Log(f"Total chapter word count: {TotalWords}", 4)

    StatsString = f"""
## Work Statistics
- **Title**: {Title}
- **Generation Time**: {ElapsedTime:.2f}s
- **Average WPM**: {60 * (TotalWords / ElapsedTime) if ElapsedTime > 0 else 0:.2f}
- **Generator**: {Writer.Config.PROJECT_NAME} (Web Novel Mode)
"""

    md_file_path = os.path.join(story_dir, f"Chapter_{chapter_number}.md")
    json_file_path = os.path.join(story_dir, f"Chapter_{chapter_number}.json")

    with open(md_file_path, "w", encoding="utf-8") as f:
        f.write(f"# {Title}\n\n{chapter_content}\n\n---\n\n{StatsString}")

    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(new_chapter.to_dict(), f, indent=4)

    logger.Log("Chapter generation complete!", 5)
    final_message = f"""
--------------------------------------------------
Output Files Saved:
- Markdown Chapter: {os.path.abspath(md_file_path)}
- JSON Data File: {os.path.abspath(json_file_path)}
- Story Context File: {os.path.abspath(context_file_path)}
--------------------------------------------------"""
    print(termcolor.colored(final_message, "green"))
