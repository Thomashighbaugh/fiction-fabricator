#!/usr/bin/python3
# File: Tools/OutlineGeneratorTool.py
# Purpose: Generates a novel outline from a prompt.
# This script is self-contained and should be run from the project's root directory.

import argparse
import os
import sys
import datetime
import re
import json

# --- Add project root to path for imports and load .env explicitly ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

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
from Writer.LLMUtils import get_llm_selection_menu_for_tool
import Writer.OutlineGenerator
from Writer.NarrativeContext import NarrativeContext
import Writer.Prompts

def select_prompt_file(logger):
    """
    Lets the user select a prompt file from the Generated_Content/Prompts directory.
    """
    prompts_dir = os.path.join(project_root, "Generated_Content", "Prompts")
    if not os.path.exists(prompts_dir) or not os.listdir(prompts_dir):
        logger.Log("No prompts found in Generated_Content/Prompts. Please generate a prompt first.", 6)
        return None

    prompts = [f for f in os.listdir(prompts_dir) if f.endswith(".txt")]
    if not prompts:
        logger.Log("No .txt prompt files found in Generated_Content/Prompts.", 6)
        return None

    print("\nPlease select a prompt to use for outline generation:")
    for i, prompt_file in enumerate(prompts):
        print(f"[{i+1}] {prompt_file}")

    choice = input("> ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(prompts):
        return os.path.join(prompts_dir, prompts[int(choice) - 1])
    else:
        logger.Log("Invalid selection.", 6)
        return None

def generate_outline_tool(prompt_file: str, temp: float = 0.75, lore_book: str = None):
    """
    Generates a novel outline and saves it to a file.
    """
    generation_timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    sys_logger = Logger("OutlineGeneratorToolLogs")

    if not prompt_file:
        prompt_file = select_prompt_file(sys_logger)
        if not prompt_file:
            return

    try:
        with open(prompt_file, "r", encoding='utf-8') as f:
            prompt_content = f.read()
    except FileNotFoundError:
        sys_logger.Log(f"Error: Prompt file not found at {prompt_file}", 7)
        return

    lore_book_content = None
    if lore_book:
        try:
            with open(lore_book, "r", encoding='utf-8') as f:
                lore_book_content = f.read()
            sys_logger.Log(f"Successfully loaded lore book: {lore_book}", 3)
        except FileNotFoundError:
            sys_logger.Log(f"Error: Lore book file not found at {lore_book}", 7)
            return

    selected_model_uri = get_llm_selection_menu_for_tool(sys_logger, "Outline Generator")
    if not selected_model_uri:
        sys.exit(1)

    interface = Interface()
    interface.LoadModels([selected_model_uri])
    
    narrative_context = NarrativeContext(initial_prompt=prompt_content, style_guide=Writer.Prompts.LITERARY_STYLE_GUIDE, lore_book_content=lore_book_content)

    # Generate the outline
    sys_logger.Log("Generating novel outline...", 2)
    narrative_context = Writer.OutlineGenerator.GenerateOutline(interface, sys_logger, prompt_content, narrative_context, selected_model_uri)
    sys_logger.Log("Outline generation complete.", 5)

    # Save the outline
    output_dir = os.path.join(project_root, "Generated_Content", "Outlines")
    os.makedirs(output_dir, exist_ok=True)

    # Create a title for the outline file
    info_messages = [interface.BuildUserQuery(narrative_context.base_novel_outline_markdown)]
    # This is a bit of a hack, maybe there's a better way to get a title.
    title_prompt = f"Based on the following outline, what is a good title for this story? Just return the title and nothing else.\n\n{narrative_context.base_novel_outline_markdown}"
    title_response = interface.SafeGenerateText(sys_logger, [interface.BuildUserQuery(title_prompt)], selected_model_uri, min_word_count_target=1)
    title = interface.GetLastMessageText(title_response).strip()
    
    safe_title = re.sub(r'[^\w\s-]', '', title).strip()
    safe_title = re.sub(r'[-\s]+', '_', safe_title)
    output_filename = f"{safe_title}_{generation_timestamp}.json"
    output_path = os.path.join(output_dir, output_filename)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(narrative_context.to_dict(), f, indent=4)
        sys_logger.Log(f"Successfully saved outline to: {output_path}", 5)
    except Exception as e:
        sys_logger.Log(f"Error saving outline to file: {e}", 7)

    print(f"\n--- Outline Generation Complete. Find your outline at: {output_path} ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a novel outline from a prompt.")
    parser.add_argument("--prompt_file", type=str, help="Path to the prompt file.")
    parser.add_argument("--temp", type=float, default=0.75, help="Temperature for the LLM.")
    parser.add_argument("--lore_book", type=str, help="Path to a lore book file.")
    args = parser.parse_args()

    generate_outline_tool(args.prompt_file, args.temp, args.lore_book)
