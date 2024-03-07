import json
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import print_formatted_text
from src.base import Base


class Book_Config(Base):
    def __init__(self):
        super().__init__()

        self.CONTEXT_FILE = "context.json"
        self.load_context()

    def load_context(self):
        # Load the context from the json file
        with open(self.CONTEXT_FILE, "r") as f:
            self.context = json.load(f)

        # Assign the settings to the attributes
        self.genre = self.context["genre"]
        self.author_style = self.context["author_style"]
        self.tone = self.context["tone"]
        self.description = self.context["description"]
        self.themes = self.context["themes"]

    def save_context(self):
        # Update the context with the current settings
        self.context["genre"] = self.genre
        self.context["author_style"] = self.author_style
        self.context["tone"] = self.tone
        self.context["description"] = self.description
        self.context["themes"] = self.themes

        # Save the context to the json file
        with open(self.CONTEXT_FILE, "w") as f:
            json.dump(self.context, f, indent=4)

    def menu(self):
        print_formatted_text("\nSelect a config to edit:")
        submenu_items = {
            "1": {
                "name": "Genre",
                "action": lambda: self.edit_text("Genre", self.genre),
            },
            "2": {
                "name": "Author Style",
                "action": lambda: self.edit_text("Author style", self.author_style),
            },
            "3": {
                "name": "Tone",
                "action": lambda: self.edit_text("Tone", self.tone),
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

        def edit_text(self, description, text):
            # Display the current text, prompt for new text, and update the attribute if confirmed
            print_formatted_text(f"\n{description}:")
            print_formatted_text(text)

            new_text = prompt("Enter the new text or x to cancel the update: ")
            if new_text == "x":
                return

            confirmation = prompt(
                f"Replace the current text with the new text? (y/n): "
            )

            if confirmation.lower() == "y":
                # Update the attribute with the new text
                setattr(self, description.lower(), new_text)
                # Save the context to the json file
                self.save_context()
                print("Text updated.")
            elif confirmation.lower() == "n":
                return
            else:
                print("Invalid input. Please try again.")

    # ──────────────────────────────────────────────────────────────────────────────

    def generate_themes(self):
        """
        Generate a novel themes based on the config settings.
        """
        output_file = self.themes
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
        output_file = self.description
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
            f"Replace the current text in {self.description} with the new text? (y/n): "
        )

        if confirmation.lower() == "y":
            base.set_text(self.description, response)
            print("Description created successfully.")
        elif confirmation.lower() == "n":
            return
        else:
            print("Invalid input. Please try again.")
