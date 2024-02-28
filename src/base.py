import fnmatch
import os
import retrying
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import print_formatted_text
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
import openai
from openai import OpenAI
import g4f

# Import the necessary module
import os
from openai import OpenAI

# Initialize the OpenAI client with the API key and base URL
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url="http://0.0.0.0:1337/v1")


# Define a class to store ANSI escape codes for text color and style
class style:
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"


# Define a base class
class Base:
    def __init__(self):
        # Set the root directory to the parent directory of the current file
        self.root_dir = os.path.dirname(os.path.abspath(__file__)) + "/.."

        # Set the model prompt and response styles using color codes
        self.MODEL_PROMPT_STYLE = "#44ffcc italic"
        self.MODEL_RESPONSE_STYLE = "#44ff44 bold"

    # Method to get the configuration settings
    def get_config(self):
        return {
            "tone": self.get_text(self.path("development/config/tone.txt")),
            "genre": self.get_text(self.path("development/config/genre.txt")),
            "description": self.get_text(
                self.path("development/config/description.txt")
            ),
            "author_style": self.get_text(
                self.path("development/config/author_style.txt")
            ),
            "themes": self.get_text(self.path("development/config/themes.txt")),
            "seed_summary": self.get_text(
                self.path("development/outline/seed_summary.txt")
            ),
        }

    def path(self, *args):
        # Construct the file path using the root directory and the provided arguments
        return os.path.join(self.root_dir, *args)

    def replace_prompts_in_template(self, template_text, prompts_obj):
        # Replace prompts in the template text with the corresponding values in the prompts object
        for key, value in prompts_obj.items():
            template_text = template_text.replace(f"[{key}]", value)
        return template_text

    def object_has_keys(self, obj, keys):
        # Check if the object contains all the specified keys
        for key in keys:
            if key not in obj:
                print("PLEASE MAKE SURE YOU HAVE FILE FOR EACH OF THE FOLLOWING:")
                print(keys)
                return False
        return True

    def output_menu_with_prompt(self, menu_items):
        # Display the menu items and prompt the user to select an option
        print_formatted_text("\nSelect an option:")
        for item in menu_items:
            print_formatted_text(f"{item}. {menu_items[item]['name']}")
        user_input = prompt("> ")
        return user_input

    def get_text(self, path_name):
        # Read text from the file at the specified path
        path_name = self.path(path_name)
        if not os.path.exists(path_name):
            raise ValueError("WARNING: File does not exist: " + path_name)
        with open(path_name, "r") as file:
            return file.read()

    def set_text(self, path_name, text):
        # Write the text to the file at the specified path
        path_name = self.path(path_name)
        if not os.path.exists(path_name):
            os.makedirs(os.path.dirname(path_name), exist_ok=True)
        with open(path_name, "w") as file:
            file.write(text)

    def edit_text(self, description, path_name):
        # Display the current text, prompt for new text, and update the file if confirmed
        text = self.get_text(path_name)
        print_formatted_text(f"\n{description}:")
        print_formatted_text(text)

        new_text = prompt("Enter the new text or x to cancel the update: ")
        if new_text == "x":
            return

        confirmation = prompt(f"Replace the current text with the new text? (y/n): ")

        def path(self, *args):
            # Construct the file path using the root directory and the provided arguments
            return os.path.join(self.root_dir, *args)

        def replace_prompts_in_template(self, template_text, prompts_obj):
            # Replace prompts in the template text with the corresponding values in the prompts object
            for key, value in prompts_obj.items():
                template_text = template_text.replace(f"[{key}]", value)
            return template_text

        def object_has_keys(self, obj, keys):
            # Check if the object contains all the specified keys
            for key in keys:
                if key not in obj:
                    print("PLEASE MAKE SURE YOU HAVE FILE FOR EACH OF THE FOLLOWING:")
                    print(keys)
                    return False
            return True

        def output_menu_with_prompt(self, menu_items):
            # Display the menu items and prompt the user to select an option
            print_formatted_text("\nSelect an option:")
            for item in menu_items:
                print_formatted_text(f"{item}. {menu_items[item]['name']}")
            user_input = prompt("> ")
            return user_input

        def get_text(self, path_name):
            # Read text from the file at the specified path
            path_name = self.path(path_name)
            if not os.path.exists(path_name):
                raise ValueError("WARNING: File does not exist: " + path_name)
            with open(path_name, "r") as file:
                return file.read()

        def set_text(self, path_name, text):
            # Write the text to the file at the specified path
            path_name = self.path(path_name)
            if not os.path.exists(path_name):
                os.makedirs(os.path.dirname(path_name), exist_ok=True)
            with open(path_name, "w") as file:
                file.write(text)

        def edit_text(self, description, path_name):
            # Display the current text, prompt for new text, and update the file if confirmed
            text = self.get_text(path_name)
            print_formatted_text(f"\n{description}:")
            print_formatted_text(text)

            new_text = prompt("Enter the new text or x to cancel the update: ")
            if new_text == "x":
                return

            confirmation = prompt(
                f"Replace the current text with the new text? (y/n): "
            )

        if confirmation.lower() == "y":
            self.set_text(path_name, new_text)
            print("Text updated.")
        elif confirmation.lower() == "n":
            return
        else:
            print("Invalid input. Please try again.")

    @retrying.retry(wait_fixed=5000, stop_max_attempt_number=3)
    def call_llm(self, prompt, temperature=0.7):
        print("LLM PROMPT:")
        print(style.GREEN + prompt + style.RESET)
        print("processing... please wait...")
        completion = g4f.ChatCompletion.create(
            model="mixtral-8x7b",
            messages=[{"role": "user", "content": prompt}],
        )

        result = completion
        print("RESPONSE FROM LLM:")
        print(style.YELLOW + result + style.RESET)
        return result

    def get_menu_from_folder(self, folder: str, file_mask="*"):
        menu = {}
        counter = 1
        for f in sorted(os.listdir(folder)):
            if fnmatch.fnmatch(f, file_mask):
                menu[str(counter)] = {"name": f}
                counter += 1
        menu["x"] = {"name": "Back (x)"}
        return menu

    def get_menu_from_files(self, folder, file_mask):
        menu = {}
        counter = 1
        for f in sorted(os.listdir(folder)):
            if fnmatch.fnmatch(f, file_mask):
                menu[str(counter)] = {"name": f}
                counter += 1
        menu["x"] = {"name": "Back (x)"}
        return menu

    def get_list_of_files(self, folder, file_mask):
        files = []
        for f in sorted(os.listdir(folder)):
            if fnmatch.fnmatch(f, file_mask):
                files.append(f)
        return files
