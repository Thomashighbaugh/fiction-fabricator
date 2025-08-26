#!/usr/bin/python3
# File: Tools/WebNovelOutlineGenerator.py
# Purpose: Generates and manages web novel outlines that support chapter appending.

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

def select_web_novel_outline(logger: Logger):
    """Scans the Web_Novels directory for existing outlines and returns the path to a selected outline.json file."""
    outline_dir = os.path.join(repo_root, "Generated_Content", "Outlines", "Web_Novels")
    
    if not os.path.isdir(outline_dir):
        os.makedirs(outline_dir, exist_ok=True)
        logger.Log(f"Created missing web novel outline directory: '{outline_dir}'. No outlines exist yet—generate one first.", 4)

    outline_files = [f for f in os.listdir(outline_dir) if f.endswith('.json')]

    if not outline_files:
        logger.Log(f"No web novel outlines found in the '{outline_dir}' directory.", 4)
        return None

    print("\nPlease select a web novel outline:")
    for i, filename in enumerate(outline_files):
        print(f"{i + 1}. {filename}")
    print(f"{len(outline_files) + 1}. Create new outline")
    print(f"{len(outline_files) + 2}. Go back")

    while True:
        try:
            choice = int(input(f"Enter your choice (1-{len(outline_files) + 2}): "))
            if 1 <= choice <= len(outline_files):
                return os.path.join(outline_dir, outline_files[choice - 1])
            elif choice == len(outline_files) + 1:
                return "CREATE_NEW"
            elif choice == len(outline_files) + 2:
                return None
            else:
                logger.Log("Invalid choice. Please enter a number from the list.", 6)
        except ValueError:
            logger.Log("Invalid input. Please enter a number.", 6)

def append_chapters_to_web_novel(logger: Logger, interface: Interface, outline_file: str, chapters_to_add: int, events_description: str):
    """Appends new chapters to an existing web novel outline."""
    try:
        with open(outline_file, "r", encoding='utf-8') as f:
            outline_data = json.load(f)
        
        narrative_context = NarrativeContext.from_dict(outline_data)
        logger.Log(f"Successfully loaded existing web novel outline: {os.path.basename(outline_file)}", 3)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.Log(f"Error loading outline file: {e}", 7)
        return

    # Get current chapter count
    current_chapters = narrative_context.chapter_count or 0
    new_total_chapters = current_chapters + chapters_to_add
    
    logger.Log(f"Current chapters: {current_chapters}, Adding: {chapters_to_add}, New total: {new_total_chapters}", 2)

    # Get model selection
    selected_model_uri = get_llm_selection_menu_for_tool(logger, "Web Novel Outline Expander")
    if not selected_model_uri:
        return

    interface.LoadModels([selected_model_uri])

    # Create expansion prompt
    expansion_prompt = f"""
Based on the existing web novel outline below, generate {chapters_to_add} additional chapter outlines that continue the story.

Current Outline:
{narrative_context.base_novel_outline_markdown}

Events to include in the new chapters:
{events_description}

Please provide detailed chapter outlines for chapters {current_chapters + 1} through {new_total_chapters}, ensuring continuity with the existing story and incorporating the requested events. Each chapter should have a clear purpose, character development, and plot progression.

Format your response as a continuation of the existing outline, with clear chapter headings and detailed descriptions.
"""

    logger.Log("Generating additional chapters...", 2)
    expansion_response = interface.SafeGenerateText(
        logger, 
        [interface.BuildUserQuery(expansion_prompt)], 
        selected_model_uri, 
        min_word_count_target=500
    )
    
    expanded_outline = interface.GetLastMessageText(expansion_response)
    
    # Append to existing outline
    narrative_context.base_novel_outline_markdown += f"\n\n## Additional Chapters ({current_chapters + 1}-{new_total_chapters})\n\n{expanded_outline}"
    narrative_context.chapter_count = new_total_chapters

    # Save the updated outline
    try:
        with open(outline_file, "w", encoding="utf-8") as f:
            json.dump(narrative_context.to_dict(), f, indent=4)
        logger.Log(f"Successfully updated web novel outline with {chapters_to_add} additional chapters.", 5)
    except Exception as e:
        logger.Log(f"Error saving updated outline: {e}", 7)

def generate_web_novel_outline(logger: Logger, interface: Interface, prompt_file: str, initial_chapters: int, temp: float = 0.75, lore_book: str = None):
    """Generates a new web novel outline with the specified number of initial chapters."""
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

    selected_model_uri = get_llm_selection_menu_for_tool(logger, "Web Novel Outline Generator")
    if not selected_model_uri:
        return

    interface.LoadModels([selected_model_uri])
    
    narrative_context = NarrativeContext(
        initial_prompt=prompt_content, 
        style_guide=Writer.Prompts.LITERARY_STYLE_GUIDE, 
        lore_book_content=lore_book_content
    )
    narrative_context.story_type = "web_novel"
    narrative_context.word_count = 0  # Web novels don't have fixed word counts
    narrative_context.chapter_count = initial_chapters

    # Generate the outline
    logger.Log(f"Generating web novel outline with {initial_chapters} initial chapters...", 2)
    narrative_context = Writer.OutlineGenerator.GenerateOutline(interface, logger, prompt_content, narrative_context, selected_model_uri)
    logger.Log("Web novel outline generation complete.", 5)

    # Create output directory
    output_dir = os.path.join(repo_root, "Generated_Content", "Outlines", "Web_Novels")
    os.makedirs(output_dir, exist_ok=True)

    # Create a title for the outline file
    title_prompt = f"Based on the following web novel outline, what is a good title for this story? Just return the title and nothing else.\n\n{narrative_context.base_novel_outline_markdown}"
    title_response = interface.SafeGenerateText(logger, [interface.BuildUserQuery(title_prompt)], selected_model_uri, min_word_count_target=1)
    title = interface.GetLastMessageText(title_response).strip()
    
    safe_title = re.sub(r'[^\w\s-]', '', title).strip()
    safe_title = re.sub(r'[-\s]+', '_', safe_title)
    output_filename = f"{safe_title}_{generation_timestamp}.json"
    output_path = os.path.join(output_dir, output_filename)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(narrative_context.to_dict(), f, indent=4)
        logger.Log(f"Successfully saved web novel outline to: {output_path}", 5)
    except Exception as e:
        logger.Log(f"Error saving web novel outline to file: {e}", 7)

    print(f"\n--- Web Novel Outline Generation Complete. Find your outline at: {output_path} ---")
    return output_path

def handle_web_novel_outline_generation(logger: Logger, interface: Interface, prompt_file: str, lore_book: str = None):
    """Main handler for web novel outline generation and management."""
    
    print("\n--- Web Novel Outline Options ---")
    print("1. Create a new web novel outline")
    print("2. Add chapters to an existing web novel outline")
    print("3. Go back")
    
    choice = input("Enter your choice (1-3): ")
    
    if choice == "1":
        # Create new outline
        while True:
            try:
                initial_chapters = int(input("Enter the number of initial chapters to outline: "))
                if initial_chapters > 0:
                    break
                else:
                    print("Please enter a positive number.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        generate_web_novel_outline(logger, interface, prompt_file, initial_chapters, lore_book=lore_book)
        
    elif choice == "2":
        # Add chapters to existing outline
        outline_file = select_web_novel_outline(logger)
        if outline_file == "CREATE_NEW":
            # Redirect to create new
            handle_web_novel_outline_generation(logger, interface, prompt_file, lore_book)
            return
        elif not outline_file:
            return
        
        while True:
            try:
                chapters_to_add = int(input("How many chapters would you like to add? "))
                if chapters_to_add > 0:
                    break
                else:
                    print("Please enter a positive number.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        events_description = input("What events should occur in these new chapters? ")
        
        append_chapters_to_web_novel(logger, interface, outline_file, chapters_to_add, events_description)
        
    elif choice == "3":
        return
    else:
        logger.Log("Invalid choice. Please select 1, 2, or 3.", 6)
        handle_web_novel_outline_generation(logger, interface, prompt_file, lore_book)