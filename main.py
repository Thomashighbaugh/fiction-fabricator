import sys
import os
import dotenv
import json

# --- Environment Initialization ---
dotenv.load_dotenv(verbose=True)

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.Tools.PremiseGenerator import generate_premises
from src.Tools.PromptGenerator import generate_prompt
from src.Tools.ShortStoryWriter import write_short_story
from src.Tools.NovelWriter import write_novel
from src.Tools.OutlineGeneratorTool import generate_outline_tool
from src.Tools.WebNovelWriter import write_web_novel_chapter
from src.Tools.LoreBookManager import LoreBookManager
from src.Writer.Interface.Wrapper import Interface
from src.Writer.PrintUtils import Logger
from src.Tools.Evaluate import evaluate_stories

def get_user_input(prompt, default=None, input_type=str):
    """Generic function to get validated user input."""
    while True:
        user_input = input(prompt).strip()
        if not user_input and default is not None:
            return default
        try:
            return input_type(user_input)
        except ValueError:
            print(f"Invalid input. Please enter a valid {input_type.__name__}.")

def handle_premise_generation(logger: Logger, interface: Interface):
    """Handles the premise generation process."""
    idea = get_user_input("Enter your story idea or theme: ")
    temp = get_user_input("Enter the temperature for the LLM (0.0-2.0, default: 0.8): ", 0.8, float)
    generate_premises(logger, interface, idea, temp)

def handle_prompt_generation(logger: Logger, interface: Interface):
    """Handles the prompt generation process."""
    title = get_user_input("Enter the title for your story: ")
    idea = get_user_input("Enter your story idea or concept: ")
    generate_prompt(logger, interface, title, idea)

def select_outline(logger: Logger, story_type: str):
    """Scans the Outlines/ directory for the given story type and returns the path to a selected outline.json file.
    If the directory does not exist yet, it will be created so the user can immediately generate an outline.
    """
    outline_dir = os.path.join("Generated_Content", "Outlines", story_type)
    repo_root = os.path.dirname(os.path.abspath(__file__))
    legacy_dir = os.path.join("src", "Generated_Content", "Outlines", story_type)

    # If outlines exist in legacy_dir but not in outline_dir, migrate them
    if os.path.isdir(legacy_dir):
        try:
            for fname in os.listdir(legacy_dir):
                if fname.endswith('.json'):
                    os.makedirs(outline_dir, exist_ok=True)
                    src_path = os.path.join(legacy_dir, fname)
                    dst_path = os.path.join(outline_dir, fname)
                    if not os.path.exists(dst_path):
                        import shutil
                        shutil.move(src_path, dst_path)
                        logger.Log(f"Migrated legacy outline file '{fname}' to '{outline_dir}'.", 2)
        except Exception as e:
            logger.Log(f"Warning: Failed during legacy outline migration: {e}", 6)

    if not os.path.isdir(outline_dir):
        os.makedirs(outline_dir, exist_ok=True)
        logger.Log(f"Created missing outline directory: '{outline_dir}'. No outlines exist yet—generate one first.", 4)

    outline_files = [f for f in os.listdir(outline_dir) if f.endswith('.json')]

    if not outline_files:
        logger.Log(f"No outlines found in the '{outline_dir}' directory.", 4)
        logger.Log("Please generate an outline first using option 3.", 4)
        return None

    print("\nPlease select an outline:")
    for i, filename in enumerate(outline_files):
        print(f"{i + 1}. {filename}")
    print(f"{len(outline_files) + 1}. Go back")

    while True:
        choice = get_user_input(f"Enter your choice (1-{len(outline_files) + 1}): ", input_type=int)
        if 1 <= choice <= len(outline_files):
            return os.path.join(outline_dir, outline_files[choice - 1])
        elif choice == len(outline_files) + 1:
            return None
        else:
            logger.Log("Invalid choice. Please enter a number from the list.", 6)

def select_web_novel_outline(logger: Logger):
    """Scans the Web_Novels directory for existing outlines and returns the path to a selected outline.json file."""
    outline_dir = os.path.join("Generated_Content", "Outlines", "Web_Novels")
    
    if not os.path.isdir(outline_dir):
        os.makedirs(outline_dir, exist_ok=True)
        logger.Log(f"Created missing web novel outline directory: '{outline_dir}'. No outlines exist yet—generate one first.", 4)

    outline_files = [f for f in os.listdir(outline_dir) if f.endswith('.json')]

    if not outline_files:
        logger.Log(f"No web novel outlines found in the '{outline_dir}' directory.", 4)
        logger.Log("Please generate a web novel outline first using option 3.", 4)
        return None

    print("\nPlease select a web novel outline:")
    for i, filename in enumerate(outline_files):
        print(f"{i + 1}. {filename}")
    print(f"{len(outline_files) + 1}. Go back")

    while True:
        choice = get_user_input(f"Enter your choice (1-{len(outline_files) + 1}): ", input_type=int)
        if 1 <= choice <= len(outline_files):
            return os.path.join(outline_dir, outline_files[choice - 1])
        elif choice == len(outline_files) + 1:
            return None
        else:
            logger.Log("Invalid choice. Please enter a number from the list.", 6)

def handle_short_story_writing(logger: Logger, interface: Interface):
    """Handles the short story writing process."""
    logger.Log("Short story generation now requires a pre-generated outline.", 3)
    outline_file = select_outline(logger, "Short_Stories")
    if not outline_file:
        return

    temp = get_user_input("Enter the temperature for the LLM (0.0-2.0, default: 0.75): ", 0.75, float)
    max_iterations = get_user_input("Enter the maximum number of iterations (default: 10): ", 10, int)
    
    # Ask user if they want critique and revision
    enable_critique = get_user_input("Enable critique and revision cycle? (y/n, default: y): ", "y", str).lower()
    enable_critique_revision = enable_critique in ["y", "yes", "1", "true"]
    
    write_short_story(logger, interface, outline_file=outline_file, temp=temp, max_iterations=max_iterations, enable_critique_revision=enable_critique_revision)

def select_prompt(logger: Logger):
    """Scans the Prompts/ directory and returns the path to a selected prompt.txt file and its title."""
    prompt_dir = os.path.join("Generated_Content", "Prompts")
    if not os.path.isdir(prompt_dir):
        logger.Log(f"Error: Directory '{prompt_dir}' not found.", 6)
        return None, None

    prompt_files = []
    for subdir in os.listdir(prompt_dir):
        if os.path.isdir(os.path.join(prompt_dir, subdir)):
            prompt_file = os.path.join(prompt_dir, subdir, "prompt.txt")
            if os.path.exists(prompt_file):
                prompt_files.append((subdir, prompt_file))

    if not prompt_files:
        logger.Log("No prompts found in the 'Prompts' directory.", 4)
        logger.Log("Please generate a prompt first using option 2.", 4)
        return None, None

    print("\nPlease select a prompt:")
    for i, (name, _) in enumerate(prompt_files):
        print(f"{i + 1}. {name}")
    print(f"{len(prompt_files) + 1}. Go back")


    while True:
        choice = get_user_input(f"Enter your choice (1-{len(prompt_files) + 1}): ", input_type=int)
        if 1 <= choice <= len(prompt_files):
            return prompt_files[choice - 1]
        elif choice == len(prompt_files) + 1:
            return None, None
        else:
            logger.Log("Invalid choice. Please enter a number from the list.", 6)

def handle_outline_generation(logger: Logger, interface: Interface):
    """Handles the outline generation process."""
    prompt_title, prompt_file = select_prompt(logger)
    if not prompt_file:
        return
    
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt_content = f.read()

    print("\n--- Lorebook Options ---")
    print("1. Generate a new lorebook from this prompt")
    print("2. Select an existing lorebook")
    print("3. Continue without a lorebook")
    lore_choice = get_user_input("Enter your choice: ", '3', str)

    lore_book_path = None
    if lore_choice == '1':
        manager = LoreBookManager(interface=interface, logger=logger)
        # Use the current interface and selected model, not a hardcoded Gemini model
        generation_manager = LoreBookManager(interface, logger)
        generated_path = generation_manager.generate_lorebook_from_prompt(prompt=prompt_content)
        
        if generated_path:
            # After generating, re-run selection to let the user pick the new one
            lore_book_path = manager.select_lorebook()
        else:
            logger.Log("Lorebook generation failed, proceeding without a lorebook.", 7)

    elif lore_choice == '2':
        manager = LoreBookManager(interface=interface, logger=logger)
        lore_book_path = manager.select_lorebook()

    # The tool itself now handles asking for story type and length.
    generate_outline_tool(logger, interface, prompt_file, lore_book=lore_book_path)

def handle_novel_writing(logger: Logger):
    """Handles the complete novel writing process."""
    logger.Log("Novel generation requires a pre-generated outline.", 3)
    outline_file = select_outline(logger, "Novels")
    if not outline_file:
        return
    # The write_novel function handles its own interface creation
    write_novel(outline_file=outline_file)

def handle_web_novel_chapter_writing(logger: Logger, interface: Interface):
    """Handles the web novel chapter writing process."""
    
    print("\n--- Web Novel Writing Options ---")
    print("1. Write a chapter from a prompt (original method)")
    print("2. Write a chapter from a web novel outline")
    print("3. Go back")
    
    choice = input("Enter your choice (1-3): ")
    
    if choice == "1":
        # Original method using prompt
        prompt_title, prompt_file = select_prompt(logger)
        if not prompt_file:
            return
        
        chapter_number = get_user_input("Enter the chapter number to generate: ", input_type=int)
        while chapter_number <= 0:
            logger.Log("Please enter a positive integer for the chapter number.", 6)
            chapter_number = get_user_input("Enter the chapter number to generate: ", input_type=int)

        print("\n--- Lorebook Options ---")
        print("1. Select an existing lorebook")
        print("2. Continue without a lorebook")
        lore_choice = get_user_input("Enter your choice: ", '2', str)

        lore_book_path = None
        if lore_choice == '1':
            manager = LoreBookManager(interface=interface, logger=logger)
            lore_book_path = manager.select_lorebook()
            
        write_web_novel_chapter(logger, interface, prompt_file, chapter_number, lore_book=lore_book_path)
        
    elif choice == "2":
        # New method using web novel outline
        outline_file = select_web_novel_outline(logger)
        if not outline_file:
            return
            
        chapter_number = get_user_input("Enter the chapter number to generate: ", input_type=int)
        while chapter_number <= 0:
            logger.Log("Please enter a positive integer for the chapter number.", 6)
            chapter_number = get_user_input("Enter the chapter number to generate: ", input_type=int)
            
        # Use the outline-based web novel chapter writer
        write_web_novel_chapter_from_outline(logger, interface, outline_file, chapter_number)
        
    elif choice == "3":
        return
    else:
        logger.Log("Invalid choice. Please select 1, 2, or 3.", 6)
        handle_web_novel_chapter_writing(logger, interface)

def write_web_novel_chapter_from_outline(logger: Logger, interface: Interface, outline_file: str, chapter_number: int):
    """Writes a web novel chapter using an outline instead of just a prompt."""
    try:
        with open(outline_file, "r", encoding='utf-8') as f:
            outline_data = json.load(f)
        
        from Writer.NarrativeContext import NarrativeContext
        narrative_context = NarrativeContext.from_dict(outline_data)
        logger.Log(f"Successfully loaded web novel outline: {os.path.basename(outline_file)}", 3)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.Log(f"Error loading outline file: {e}", 7)
        return
    
    # Create a temporary prompt file from the outline
    import tempfile
    temp_prompt_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(narrative_context.base_novel_outline_markdown)
            temp_prompt_path = temp_file.name
        
        # Use the existing web novel chapter writer with the outline as prompt
        write_web_novel_chapter(logger, interface, temp_prompt_path, chapter_number, lore_book=None)
        
    finally:
        # Clean up temporary file
        if temp_prompt_path and os.path.exists(temp_prompt_path):
            os.unlink(temp_prompt_path)


def handle_evaluation(logger: Logger, interface: Interface):
    """Handles the story evaluation process."""
    story1_path = get_user_input("Enter the path to the first story's JSON file: ")
    story2_path = get_user_input("Enter the path to the second story's JSON file: ")
    output_path = get_user_input("Enter the output path for the report (default: Report.md): ", "Report.md")
    model = get_user_input("Enter the model to use for evaluation (default: google://gemini-1.5-pro-latest): ", "google://gemini-1.5-pro-latest")
    evaluate_stories(logger, interface, story1_path, story2_path, output_path, model)

def handle_lorebook_management(logger: Logger, interface: Interface):
    """Handles all lorebook management tasks."""
    manager = LoreBookManager(interface, logger)
    manager.main_menu()

def main_menu():
    """Displays the main menu and returns the user's choice."""
    print("\nWelcome to the Fiction Fabricator!")
    print("Please select an option:")
    print("1. Generate a new premise for a story.")
    print("2. Generate a new prompt for a story.")
    print("3. Generate an outline (short story, novel, or web novel).")
    print("4. Write a short story.")
    print("5. Write a complete novel from an outline.")
    print("6. Write a web novel chapter.")
    print("7. Evaluate two stories.")
    print("8. Manage Lorebooks.")
    print("9. Exit.")

    choice = input("Enter your choice (1-9): ")
    return choice

def main():
    """The main function of the Fiction Fabricator."""
    logger = Logger()
    # Initialize a base interface. Tools can add models as needed.
    interface = Interface(Models=[])

    while True:
        choice = main_menu()

        if choice == '1':
            handle_premise_generation(logger, interface)
        elif choice == '2':
            handle_prompt_generation(logger, interface)
        elif choice == '3':
            handle_outline_generation(logger, interface)
        elif choice == '4':
            handle_short_story_writing(logger, interface)
        elif choice == '5':
            handle_novel_writing(logger)
        elif choice == '6':
            handle_web_novel_chapter_writing(logger, interface)
        elif choice == '7':
            handle_evaluation(logger, interface)
        elif choice == '8':
            handle_lorebook_management(logger, interface)
        elif choice == '9':
            print("Exiting the Fiction Fabricator. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 9.")

if __name__ == "__main__":
    main()
