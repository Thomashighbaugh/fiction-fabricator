import os
import shutil
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import print_formatted_text
from src.book_setup import Book_Config
from src.outline import Outline
from src.settings import Settings
from src.characters import Characters
from src.chapter_selector import ChapterSelector

# ──────────────────────────────────────────────────────────────────────────────


# Initialize instances of different classes
book_config = Book_Config()
outline = Outline()
settings = Settings()
characters = Characters()
chapter_selector = ChapterSelector()

# ──────────────────────────────────────────────────────────────────────────────

def exit_app():
    """
    Function to exit the application.
    """
    print_formatted_text("See You Next Time!")
    exit()

# ──────────────────────────────────────────────────────────────────────────────

# Menu items with corresponding actions
menu_items = {
    "1": {"name": "Novel config: voice, style, genre", "action": lambda: book_config.menu()},
    "2": {"name": "Novel outline", "action": lambda: outline.menu()},
    "3": {"name": "Develop Settings/location", "action": lambda: settings.menu()},
    "4": {"name": "Develop Characters", "action": lambda: characters.menu()},
    "5": {"name": "Work on chapter", "action": lambda: chapter_selector.menu()},
    "6":{"name": "Clear the files generated and start again from scratch.", "action": lambda:backup_and_clear_settings()},
    "9": {"name": "Exit", "action": exit_app},
}

# ──────────────────────────────────────────────────────────────────────────────


DEVELOPMENT_DIR = 'development/'
TEMPLATE_DIR = 'template/'

def backup_and_clear_settings():
    """
    Back up the current settings files and directories to a user-specified directory
    and replace the original files with blank files, keeping the directory structure intact.
    """
    backup_dir = prompt("Enter the directory name for backup: ")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # Back up each file and directory in the development directory
    for item in os.listdir(DEVELOPMENT_DIR):
        item_path = os.path.join(DEVELOPMENT_DIR, item)
        backup_item_path = os.path.join(backup_dir, item)

        if os.path.isfile(item_path):
            # Back up the file
            shutil.copy(item_path, backup_item_path)
            # Replace the original file with a blank file
            open(item_path, 'w').close()
        elif os.path.isdir(item_path):
            # Back up the directory recursively
            shutil.copytree(item_path, backup_item_path)
            # Replace files inside the directory with blank files
            for root, dirs, files in os.walk(item_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    open(file_path, 'w').close()
        print_formatted_text("Work products have been backed up, and original files have been replaced with blank files.")

# ──────────────────────────────────────────────────────────────────────────────

def main():
    """
    Main function to run the application.
    """
    while True:
        print_formatted_text("\nHello! \n We Have Plenty We Can Work On Together! \n\nWhat would you like to do?")
        for item in menu_items:
            print_formatted_text(f"{item}. {menu_items[item]['name']}")

        user_input = prompt("> ")

        if user_input in menu_items:
            menu_items[user_input]["action"]()
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
