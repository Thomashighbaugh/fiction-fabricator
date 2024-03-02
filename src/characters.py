import os
import json
import re
from pathlib import Path
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import print_formatted_text
from src.base import Base, style
from shutil import copyfile


class Characters(Base):
    def __init__(self):
        super().__init__()
        self.main_folder = self.path("development/characters")
        self.GENERATE_SNIPPET_PROMPT = self.get_text("prompts/characters/summarise.txt")
        self.GENERATE_SHORT_PROMPT = self.get_text(
            "prompts/characters/summarise_short.txt"
        )
        self.SEED_SUMMARY_PATH = self.path("development/outline/seed_summary.txt")
        self.PLOT_OUTLINE_PATH = self.path("development/outline/plot_outline.txt")

    # ─────────────────────────────────────────────────────────────────
    def get_setting_from_file(self, file_path):
        setting_content = self.get_text(file_path)
        if not setting_content:
            return {}
        return json.loads(setting_content)

    # ─────────────────────────────────────────────────────────────────
    def menu(self):
        print_formatted_text("\nCharacters - Select an option:")
        submenu_items = {
            "1": {
                "name": "Extract Characters from the context",
                "action": lambda: self.extract_and_create_character_entries(),
            },
            "2": {
                "name": "Create a new character",
                "action": lambda: self.create_character(),
            },
            "3": {
                "name": "Regenerate character snippets from full descriptions",
                "action": lambda: self.create_snippet_files(),
            },
            "4": {
                "name": "Compile character_all_snippets.txt file from snippets sub folders",
                "action": lambda: self.create_character_files(),
            },
            "5": {
                "name": "Regenerate character_all_summary.txt file using LLM",
                "action": lambda: self.create_short_summary(),
            },
            "6": {
                "name": "Extract and Generate Profiles",
                "action": lambda: self.extract_and_generate_profiles(),
            },
            "9": {"name": "Back (x)", "action": lambda: None},
        }

        while True:
            user_input = self.output_menu_with_prompt(submenu_items)

            if user_input == "x":
                break

            if user_input in submenu_items:
                submenu_items[user_input]["action"]()
                if user_input == "9":
                    break
            else:
                print("Invalid option. Please try again.")

    # ─────────────────────────────────────────────────────────────────
    def create_character(self):
        character_name = prompt("Enter a name for the new character: ")

        character_directory = Path(self.main_folder) / character_name
        character_directory.mkdir(parents=True, exist_ok=True)

        character_description = prompt(
            "Enter a description for the new character (optional): "
        )

        seed_summary = ""
        if self.SEED_SUMMARY_PATH.exists():
            with open(self.SEED_SUMMARY_PATH, "r") as seed_summary_file:
                seed_summary = seed_summary_file.read()

        plot_outline = ""
        if self.PLOT_OUTLINE_PATH.exists():
            with open(self.PLOT_OUTLINE_PATH, "r") as plot_outline_file:
                plot_outline = plot_outline_file.read()

        long_profile_prompt = (
            self.get_text("prompts/character/long_profile.txt")
            .replace("<CHARACTER_NAME>", character_name)
            .replace("<DESCRIPTION>", character_description)
            .replace("<SEED_SUMMARY>", seed_summary)
            .replace("<PLOT_OUTLINE>", plot_outline)
        )

        long_profile = self.get_summary_from_full(long_profile_prompt)

        long_profile_path = character_directory / "long_profile.txt"
        with open(long_profile_path, "w") as long_profile_file:
            long_profile_file.write(long_profile)

        print(f"Successfully created {character_name} directory and long_profile.txt!")

    # ─────────────────────────────────────────────────────────────────
    def get_summary_from_full(self, full_text: str) -> str:
        prompt_full = self.GENERATE_SNIPPET_PROMPT + "\n\n" + full_text
        result = self.call_llm(prompt_full)
        return result

    # ─────────────────────────────────────────────────────────────────
    def extract_and_generate_profiles(self):
        if not self.SEED_SUMMARY_PATH.exists():
            print("Error: No seed_summary.txt found in development/outline folder.")
            return

        with open(self.SEED_SUMMARY_PATH, "r") as f:
            lines = f.readlines()

        character_dict = {}
        for line in lines:
            line = line.strip("\n").split(": ")
            character_name = line[0].strip()
            character_info = line[1].strip()

            character_dict[character_name] = character_info

        for character_name, character_info in character_dict.items():
            character_directory = Path(self.main_folder) / character_name
            character_directory.mkdir(parents=True, exist_ok=True)

            character_description = (
                character_info.split("-")[-1].strip() if "-" in character_info else ""
            )

            long_profile_prompt = (
                self.get_text("prompts/character/long_profile.txt")
                .replace("<CHARACTER_NAME>", character_name)
                .replace("<DESCRIPTION>", character_description)
            )

            long_profile = self.get_summary_from_full(long_profile_prompt)

            long_profile_path = character_directory / "long_profile.txt"
            with open(long_profile_path, "w") as long_profile_file:
                long_profile_file.write(long_profile)

            print(f"\nCharacter '{character_name}' created successfully.\n")

            self.create_or_update_snippet(character_name)

    # ─────────────────────────────────────────────────────────────────
    def create_or_update_snippet(self, character_name):
        character_directory = Path(self.main_folder) / character_name
        snippet_txt_path = character_directory / "snippet.txt"

        if snippet_txt_path.exists():
            with open(snippet_txt_path, "r") as old_snippet_file:
                old_snippet = old_snippet_file.read().strip()

            new_snippet = self.get_summary_from_long_profile(old_snippet)

            if old_snippet != new_snippet:
                with open(snippet_txt_path, "w") as new_snippet_file:
                    new_snippet_file.write(new_snippet)
                    print(
                        f"\nSnippet for character '{character_name}' updated successfully.\n"
                    )
        else:
            self.create_snippet(character_name)

    # ─────────────────────────────────────────────────────────────────
    def create_snippet_files(self):
        confirmation = prompt(
            f"Call LLM with each long character profile and create the short snippet for each (y/n): "
        )
        if confirmation.lower() == "n":
            return
        for setting_folder in os.listdir(self.main_folder):
            setting_path = Path(self.main_folder) / setting_folder
            if setting_path.is_dir():
                full_txt_path = setting_path / "long_profile.txt"
                if full_txt_path.exists():
                    with open(full_txt_path, "r") as full_file:
                        full_text = full_file.read()

                    summary = self.get_summary_from_full(full_text)
                    snippet_txt_path = setting_path / "snippet.txt"
                    with open(snippet_txt_path, "w") as snippet_file:
                        snippet_file.write(summary)

    # ─────────────────────────────────────────────────────────────────
    def create_character_files(self):
        settings_all_names_path = Path(self.main_folder) / "character_all_names.txt"
        settings_all_snippets_path = (
            Path(self.main_folder) / "character_all_snippets.txt"
        )

        with open(settings_all_names_path, "w") as names_file, open(
            settings_all_snippets_path, "w"
        ) as snippets_file:
            character_names = get_character_names(
                self.main_folder
            )  # Modified this line to use the get_character_names function
            for (
                character_name
            ) in (
                character_names
            ):  # Modified this line to iterate over the character names
                setting_path = Path(self.main_folder) / character_name
                if setting_path.is_dir():
                    setting_name = character_name.replace(
                        "_", " "
                    )  # Modified this line to use the character name
                    names_file.write(f"{setting_name}\n")

                    snippet_path = setting_path / "snippet.txt"
                    if snippet_path.exists():
                        with open(snippet_path, "r") as snippet_file:
                            snippet = snippet_file.read().strip()
                            snippets_file.write(f"{setting_name}: {snippet}\n")
                        copyfile(
                            snippet_path,
                            settings_all_snippets_path / f"{character_name}.txt",
                        )  # Added this line to copy the snippet file to the character_all_snippets folder

        print(
            "Done.",
            settings_all_names_path,
            settings_all_snippets_path,
            "regenerated.",
        )

    # ─────────────────────────────────────────────────────────────────
    def create_short_summary(self):
        full_text = self.get_text("development/characters/character_all_snippets.txt")
        prompt_full = self.GENERATE_SHORT_PROMPT + "\n\n" + full_text
        result = self.call_llm(prompt_full)
        self.set_text("development/characters/character_all_summary.txt", result)

    # ─────────────────────────────────────────────────────────────────
    def create_character_folder_and_file(
        self, character_name: str, character_description: str
    ):
        character_directory = Path(self.main_folder) / character_name
        character_directory.mkdir(parents=True, exist_ok=True)

        long_profile_path = character_directory / "long_profile.txt"
        with open(long_profile_path, "w") as long_profile_file:
            long_profile_file.write(character_description)

    # ──────────────────────────────────────────────────────────────────────────────

    def extract_and_create_character_entries(self):
        # Load the prompt from the file
        extract_prompt = self.get_text("prompts/characters/extract.txt")
        settings = self.get_config()
        extract_prompt = self.replace_prompts_in_template(extract_prompt, settings)

        # Get the seed summary and plot outline texts
        seed_summary = self.get_text(self.SEED_SUMMARY_PATH)
        plot_outline = self.get_text(self.PLOT_OUTLINE_PATH)

        # Use the LLM to extract character entries from the prompt
        full_text = f"{extract_prompt}\n\n{seed_summary}\n{plot_outline}"
        character_entries = self.call_llm(full_text)

        # Parse the character entries into a dictionary of name and description
        character_dict = self.parse_character_entries(character_entries)

        # Create new character entries based on the extracted information
        for character_name, character_description in character_dict.items():
            self.create_character_folder_and_file(character_name, character_description)

    def parse_character_entries(self, character_entries: str) -> dict[str, str]:
        # Implement the parsing logic here.
        # You can use regular expressions or other text processing techniques
        # to parse the character entries into a dictionary of name and description.
        # For example, you can use the following regular expression pattern
        # to parse the character entries in the format of "Name: description":
        pattern = r"(?m)^(\w+): (.+)$"
        matches = re.findall(pattern, character_entries)
        character_dict = dict(matches)
        return character_dict
