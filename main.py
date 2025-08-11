import sys
import os
import dotenv

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
import Writer.Interface.Wrapper
from src.Writer.PrintUtils import Logger
from src.Tools.Evaluate import evaluate_stories

def handle_premise_generation():
    """Handles the premise generation process."""
    idea = input("Enter your story idea or theme: ")
    temp_str = input("Enter the temperature for the LLM (0.0-2.0, default: 0.8): ")
    try:
        temp = float(temp_str) if temp_str else 0.8
    except ValueError:
        print("Invalid temperature format. Using default value 0.8.")
        temp = 0.8
    generate_premises(idea, temp)

def handle_prompt_generation():
    """Handles the prompt generation process."""
    title = input("Enter the title for your story: ")
    idea = input("Enter your story idea or concept: ")
    generate_prompt(title, idea)

def handle_short_story_writing():
    """Handles the short story writing process."""
    premise = input("Enter the premise for your short story: ")
    logger = Logger()
    
    print("\n--- Lorebook Options ---")
    print("1. Select an existing lorebook")
    print("2. Continue without a lorebook")
    lore_choice = input("Enter your choice: ").strip()

    lore_book_path = None
    if lore_choice == '1':
        manager = LoreBookManager(interface=Writer.Interface.Wrapper.Interface(Models=[]), logger=logger) 
        lore_book_path = manager.select_lorebook()

    temp_str = input("Enter the temperature for the LLM (0.0-2.0, default: 0.75): ")
    try:
        temp = float(temp_str) if temp_str else 0.75
    except ValueError:
        print("Invalid temperature format. Using default value 0.75.")
        temp = 0.75
    max_iterations_str = input("Enter the maximum number of iterations (default: 10): ")
    try:
        max_iterations = int(max_iterations_str) if max_iterations_str else 10
    except ValueError:
        print("Invalid number of iterations. Using default value 10.")
        max_iterations = 10
    write_short_story(premise, temp, max_iterations, lore_book_path)

def select_prompt():
    """Scans the Prompts/ directory and returns the path to a selected prompt.txt file and its title."""
    prompt_dir = os.path.join("Generated_Content", "Prompts")
    if not os.path.isdir(prompt_dir):
        print(f"Error: Directory '{prompt_dir}' not found.")
        return None, None

    prompt_files = []
    for subdir in os.listdir(prompt_dir):
        if os.path.isdir(os.path.join(prompt_dir, subdir)):
            prompt_file = os.path.join(prompt_dir, subdir, "prompt.txt")
            if os.path.exists(prompt_file):
                prompt_files.append((subdir, prompt_file))

    if not prompt_files:
        print("No prompts found in the 'Prompts' directory.")
        print("Please generate a prompt first using option 2.")
        return None, None

    print("\nPlease select a prompt:")
    for i, (name, _) in enumerate(prompt_files):
        print(f"{i + 1}. {name}")

    while True:
        try:
            choice_str = input(f"Enter your choice (1-{len(prompt_files)}): ")
            choice = int(choice_str)
            if 1 <= choice <= len(prompt_files):
                return prompt_files[choice - 1]
            else:
                print("Invalid choice. Please enter a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def handle_outline_generation():
    """Handles the outline generation process."""
    prompt_title, prompt_file = select_prompt()
    if not prompt_file:
        return
    logger = Logger()
    with open(prompt_file, 'r') as f:
        prompt_content = f.read()

    print("\n--- Lorebook Options ---")
    print("1. Generate a new lorebook from this prompt")
    print("2. Select an existing lorebook")
    print("3. Continue without a lorebook")
    lore_choice = input("Enter your choice: ").strip()

    lore_book_path = None
    manager = LoreBookManager(interface=Writer.Interface.Wrapper.Interface(Models=[]), logger=logger) 

    if lore_choice == '1':
        generation_interface = Writer.Interface.Wrapper.Interface(Models=["google://gemini-1.5-pro-latest"])
        generation_manager = LoreBookManager(generation_interface, logger)
        generated_path = generation_manager.generate_lorebook_from_prompt(prompt=prompt_content)
        
        if generated_path:
            lore_book_path = manager.select_lorebook()
        else:
            logger.Log("Lorebook generation failed, proceeding without a lorebook.", 7)

    elif lore_choice == '2':
        lore_book_path = manager.select_lorebook()

    generate_outline_tool(prompt_file, lore_book=lore_book_path)

def handle_novel_writing():
    """Handles the complete novel writing process."""
    write_novel(outline_file=None)

def handle_web_novel_chapter_writing():
    """Handles the web novel chapter writing process."""
    prompt_title, prompt_file = select_prompt()
    if not prompt_file:
        return
    
    while True:
        try:
            chapter_number_str = input("Enter the chapter number to generate: ")
            chapter_number = int(chapter_number_str)
            if chapter_number > 0:
                break
            else:
                print("Please enter a positive integer for the chapter number.")
        except ValueError:
            print("Invalid input. Please enter a valid integer for the chapter number.")
    
    logger = Logger()
    print("\n--- Lorebook Options ---")
    print("1. Select an existing lorebook")
    print("2. Continue without a lorebook")
    lore_choice = input("Enter your choice: ").strip()

    lore_book_path = None
    if lore_choice == '1':
        manager = LoreBookManager(interface=Writer.Interface.Wrapper.Interface(Models=[]), logger=logger)
        lore_book_path = manager.select_lorebook()
        
    write_web_novel_chapter(prompt_file, chapter_number, lore_book=lore_book_path)


def handle_evaluation():
    """Handles the story evaluation process."""
    story1_path = input("Enter the path to the first story's JSON file: ")
    story2_path = input("Enter the path to the second story's JSON file: ")
    output_path = input("Enter the output path for the report (default: Report.md): ")
    if not output_path:
        output_path = "Report.md"
    model = input("Enter the model to use for evaluation (default: google://gemini-1.5-pro-latest): ")
    if not model:
        model = "google://gemini-1.5-pro-latest"
    evaluate_stories(story1_path, story2_path, output_path, model)

def handle_lorebook_management():
    """Handles all lorebook management tasks."""
    logger = Logger()
    # This is a temporary interface for the lorebook manager.
    # A more robust solution would be to initialize the interface once
    # and pass it to the tools that need it.
    import Writer.Interface.Wrapper
    interface = Writer.Interface.Wrapper.Interface(Models=[])
    manager = LoreBookManager(interface, logger)
    manager.main_menu()

def main_menu():
    """Displays the main menu and returns the user's choice."""
    print("\nWelcome to the Fiction Fabricator!")
    print("Please select an option:")
    print("1. Generate a new premise for a story.")
    print("2. Generate a new prompt for a story.")
    print("3. Generate a novel outline.")
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
    while True:
        choice = main_menu()

        if choice == '1':
            handle_premise_generation()
        elif choice == '2':
            handle_prompt_generation()
        elif choice == '3':
            handle_outline_generation()
        elif choice == '4':
            handle_short_story_writing()
        elif choice == '5':
            handle_novel_writing()
        elif choice == '6':
            handle_web_novel_chapter_writing()
        elif choice == '7':
            handle_evaluation()
        elif choice == '8':
            handle_lorebook_management()
        elif choice == '9':
            print("Exiting the Fiction Fabricator. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 9.")

if __name__ == "__main__":
    main()
