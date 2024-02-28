from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import print_formatted_text
from src.base import Base

# ──────────────────────────────────────────────────────────────────────────────


class Book_Config(Base):

    def __init__(self):
        super().__init__()

        self.GENRE_FILE = "development/config/genre.txt"
        self.AUTHOR_STYLE_FILE = "development/config/author_style.txt"
        self.THEMES_FILE = "development/config/themes.txt"
        self.TONE_FILE = "development/config/tone.txt"
        self.DESCRIPTION_FILE = "development/config/description.txt"

    # ──────────────────────────────────────────────────────────────────────────────

    def menu(self):
        print_formatted_text("\nSelect a config to edit:")
        submenu_items = {
            "1": {
                "name": "Genre",
                "action": lambda: self.edit_text("Genre", self.GENRE_FILE),
            },
            "2": {
                "name": "Author Style",
                "action": lambda: self.edit_text(
                    "Author style", self.AUTHOR_STYLE_FILE
                ),
            },
            "3": {
                "name": "Tone",
                "action": lambda: self.edit_text("Tone", self.TONE_FILE),
            },
            "4": {
                "name": "Book Description",
                "action": lambda: self.create_description(),
            },
            "5": {
                "name": "Themes",
                "action": lambda: self.generate_themes(),
            },
            "7": {"name": "Back (x)", "action": lambda: None},
        }

        while True:
            user_input = self.output_menu_with_prompt(submenu_items)

            if user_input == "x":
                break

            if user_input in submenu_items:
                submenu_items[user_input]["action"]()
                if user_input == "5":
                    break
            else:
                print("Invalid option. Please try again.")

    # ──────────────────────────────────────────────────────────────────────────────

    def generate_themes(self):
        """
        Generate a novel themes based on the config settings.
        """
        output_file = self.THEMES_FILE
        themes_prompt = self.get_text("prompts/setup/generate-themes.txt")
        settings = self.get_config()
        if not self.object_has_keys(
            settings, ["genre", "author_style", "tone", "description"]
        ):
            return
        llm_prompt = self.replace_prompts_in_template(themes_prompt, settings)

        print("Prompt is:")
        print(llm_prompt)

        confirmation = prompt(f"Call LLM with prompt (y/n): ")
        if confirmation.lower() == "n":
            return

        response = self.call_llm(llm_prompt)

        confirmation = prompt(
            # Replace the placeholder in the prompt with the user in
            f"Replace the current text in {output_file} with the new text? (y/n): "
        )

        if confirmation.lower() == "y":
            self.set_text(output_file, response)
            print("Text updated.")
        elif confirmation.lower() == "n":
            return
        else:
            print("Invalid input. Please try again.")

    # ──────────────────────────────────────────────────────────────────────────────

    def create_description(self):
        base = Base()
        output_file = self.DESCRIPTION_FILE
        description_prompt = self.get_text("prompts/setup/create-description.txt")
        user_input = input("Enter your idea: ")
        settings = self.get_config()
        if not self.object_has_keys(settings, ["genre", "author_style", "tone"]):
            return

          # Generate the LLM prompt with the settings
        llm_prompt = self.replace_prompts_in_template(description_prompt, settings)
        # Replace the placeholder in the prompt with the user input
        llm_prompt += user_input

      
      


        print("Prompt is:")
        print(llm_prompt)

        confirmation = prompt(f"Generate description with prompt (y/n): ")
        if confirmation.lower() == "n":
            return

        # Call the LLM model with the prompt
        response = self.call_llm(llm_prompt)

        confirmation = prompt(
            # Replace the placeholder in the prompt with the user input
            f"Replace the current text in {self.DESCRIPTION_FILE} with the new text? (y/n): "
        )

        if confirmation.lower() == "y":
            base.set_text(self.DESCRIPTION_FILE, response)
            print("Description created successfully.")
        elif confirmation.lower() == "n":
            return
        else:
            print("Invalid input. Please try again.")

