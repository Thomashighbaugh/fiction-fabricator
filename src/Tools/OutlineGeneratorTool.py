#!/usr/bin/python3
# File: Tools/OutlineGeneratorTool.py
# Purpose: Generates a novel outline from a prompt.

import os
import sys
import datetime
import re
import json

# --- Add source root to path for imports (src) and determine repository root ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # This is the 'src' directory
repo_root = os.path.dirname(project_root)  # One level above 'src' is the repository root
sys.path.insert(0, project_root)

# --- Standardized Imports from Main Project ---
from Writer.Interface.Wrapper import Interface
from Writer.PrintUtils import Logger
from Writer.LLMUtils import get_llm_selection_menu_for_tool
import Writer.OutlineGenerator
from Writer.NarrativeContext import NarrativeContext
import Writer.Prompts
import Writer.Config
from Tools.WebNovelOutlineGenerator import handle_web_novel_outline_generation

def generate_outline_tool(logger: Logger, interface: Interface, prompt_file: str, temp: float = 0.75, lore_book: str = None):
    """
    Generates a novel outline and saves it to a file.
    """
    # --- Force enable expanded outline generation ---
    Writer.Config.EXPAND_OUTLINE = True
    
    generation_timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

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
            logger.Log(f"Successfully loaded lore book: {lore_book}", 3)
        except FileNotFoundError:
            logger.Log(f"Error: Lore book file not found at {lore_book}", 7)
            return

    # --- Get user input for story type ---
    story_type = ""
    while story_type not in ["1", "2", "3"]:
        story_type = input("What type of story outline would you like to generate?\n1. Short Story\n2. Novel\n3. Web Novel\nEnter choice: ")

    if story_type == "1":
        story_type = "short_story"
        word_count_str = input("Enter the desired word count (default: 15,000): ")
        word_count = int(word_count_str) if word_count_str else 15000
        chapters = 1  # Short stories have one "chapter"
        logger.Log(f"Generating outline for a {word_count}-word short story.", 2)
        output_dir = os.path.join(repo_root, "Generated_Content", "Outlines", "Short_Stories")
    elif story_type == "2":
        story_type = "novel"
        while True:
            try:
                chapters_str = input("Enter the number of chapters: ")
                chapters = int(chapters_str)
                if chapters > 0:
                    break
                else:
                    print("Please enter a positive number.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        word_count = 0 # Word count is not the primary measure for novels
        logger.Log(f"Generating outline for a {chapters}-chapter novel.", 2)
        output_dir = os.path.join(repo_root, "Generated_Content", "Outlines", "Novels")
    else:  # story_type == "3"
        # Handle web novel outline generation
        handle_web_novel_outline_generation(logger, interface, prompt_file, lore_book)
        return

    selected_model_uri = get_llm_selection_menu_for_tool(logger, "Outline Generator")
    if not selected_model_uri:
        return

    interface.LoadModels([selected_model_uri])
    
    narrative_context = NarrativeContext(initial_prompt=prompt_content, style_guide=Writer.Prompts.LITERARY_STYLE_GUIDE, lore_book_content=lore_book_content)
    narrative_context.story_type = story_type
    narrative_context.word_count = word_count
    narrative_context.chapter_count = chapters

    # Generate the outline
    logger.Log("Generating outline...", 2)
    narrative_context = Writer.OutlineGenerator.GenerateOutline(interface, logger, prompt_content, narrative_context, selected_model_uri)
    logger.Log("Outline generation complete.", 5)

    # Save the outline (migrate any legacy incorrectly nested directory first)
    legacy_dir = os.path.join(project_root, "Generated_Content", "Outlines", "Short_Stories" if story_type == "short_story" else "Novels")
    if os.path.isdir(legacy_dir) and legacy_dir != output_dir:
        try:
            for fname in os.listdir(legacy_dir):
                src_path = os.path.join(legacy_dir, fname)
                dst_path = os.path.join(output_dir, fname)
                if os.path.isfile(src_path) and not os.path.exists(dst_path):
                    os.makedirs(output_dir, exist_ok=True)
                    try:
                        import shutil
                        shutil.move(src_path, dst_path)
                        logger.Log(f"Migrated legacy outline file '{fname}' to '{output_dir}'.", 2)
                    except Exception as move_err:
                        logger.Log(f"Warning: Failed to migrate '{fname}': {move_err}", 6)
        except Exception as e:
            logger.Log(f"Warning: Legacy outline migration encountered an error: {e}", 6)
    os.makedirs(output_dir, exist_ok=True)

    # Create a title for the outline file
    title_prompt = f"Based on the following outline, what is a good title for this story? Just return the title and nothing else.\n\n{narrative_context.base_novel_outline_markdown}"
    title_response = interface.SafeGenerateText(logger, [interface.BuildUserQuery(title_prompt)], selected_model_uri, min_word_count_target=1)
    title = interface.GetLastMessageText(title_response).strip()
    
    safe_title = re.sub(r'[^\w\s-]', '', title).strip()
    safe_title = re.sub(r'[-\s]+', '_', safe_title)
    output_filename = f"{safe_title}_{generation_timestamp}.json"
    output_path = os.path.join(output_dir, output_filename)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(narrative_context.to_dict(), f, indent=4)
        logger.Log(f"Successfully saved outline to: {output_path}", 5)
    except Exception as e:
        logger.Log(f"Error saving outline to file: {e}", 7)

    print(f"\n--- Outline Generation Complete. Find your outline at: {output_path} ---")
