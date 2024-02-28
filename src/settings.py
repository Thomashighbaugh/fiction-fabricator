import os
from pathlib import Path
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import print_formatted_text
from src.base import Base, style


class Settings(Base):
    def __init__(self):
        super().__init__()

        self.main_folder = self.path("development/settings")
        self.GENERATE_SNIPPET_PROMPT = self.get_text("prompts/settings/summarise.txt")
        self.GENERATE_SHORT_PROMPT = self.get_text("prompts/settings/summarise_short.txt")
        self.GENERATE_SETTING_PROMPT = self.get_text("prompts/settings/write_setting.txt")

    
    def menu(self):
        print_formatted_text("\nSettings/Locations - Select an option:")
        submenu_items = {
            "1": {"name": "Write full setting/location description based on seed", "action": lambda: self.write_setting_for_seed()},
            "2": {"name": "Regenerate ONE setting snippet from full description using LLM", "action": lambda: self.create_snippet()},
            "3": {"name": "Regenerate ALL setting snippets from full descriptions using LLM", "action": lambda: self.create_snippet_files()},
            "4": {"name": "Compile settings summary/overview files from sub folders", "action": lambda: self.create_setting_files()},
            "5": {"name": "Create short summary file using LLM", "action": lambda: self.create_short_summary()},
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

    

    def create_short_summary(self):
        full_text = self.get_text("development/settings/settings_all_snippets.txt")
        prompt_full = self.GENERATE_SHORT_PROMPT + "\n\n" + full_text
        result = self.call_llm(prompt_full)
        self.set_text("development/settings/settings_summary.txt", result)


    def get_summary_from_full(self, full_text: str) -> str:
        prompt_full = self.GENERATE_SNIPPET_PROMPT + "\n\n" + full_text
        result = self.call_llm(prompt_full)
        return result


    def create_snippet(self):
        menu = self.get_menu_from_folder(self.main_folder)

        user_input = self.output_menu_with_prompt(menu)
        if user_input == "x":
            return
        
        base_path = Path(self.main_folder) / menu[user_input]["name"]

        full_txt_path =  base_path / "full.txt"
        with open(full_txt_path, "r") as full_file:
            full_text = full_file.read()
        summary = self.get_summary_from_full(full_text)
        snippet_txt_path = base_path / "snippet.txt"
        with open(snippet_txt_path, "w") as snippet_file:
            snippet_file.write(summary)


    def create_snippet_files(self):
        confirmation = prompt(f"Call LLM with each setting/location and create the setting snippet for each (y/n): ")
        if confirmation.lower() == "n":
            return
        for setting_folder in os.listdir(self.main_folder):
            setting_path = Path(self.main_folder) / setting_folder
            if setting_path.is_dir():
                full_txt_path = setting_path / "full.txt"
                if full_txt_path.exists():
                    with open(full_txt_path, "r") as full_file:
                        full_text = full_file.read()

                    summary = self.get_summary_from_full(full_text)
                    snippet_txt_path = setting_path / "snippet.txt"
                    with open(snippet_txt_path, "w") as snippet_file:
                        snippet_file.write(summary)
    


    def create_setting_files(self):
        settings_all_names_path = Path(self.main_folder) / "settings_all_names.txt"
        settings_all_snippets_path = Path(self.main_folder) / "settings_all_snippets.txt"
        
        with open(settings_all_names_path, "w") as names_file, open(settings_all_snippets_path, "w") as snippets_file:
            for setting_folder in os.listdir(self.main_folder):
                setting_path = Path(self.main_folder) / setting_folder
                if setting_path.is_dir():
                    setting_name = setting_folder.replace("_", " ")
                    names_file.write(f"{setting_name}\n")
                    
                    snippet_path = setting_path / "snippet.txt"
                    if snippet_path.exists():
                        with open(snippet_path, "r") as snippet_file:
                            snippet = snippet_file.read().strip()
                            snippets_file.write(f"{setting_name}: {snippet}\n")

        print("Done.", settings_all_names_path, settings_all_snippets_path, "regenerated.")


    def write_setting_for_seed(self):
        prompts = self.get_config()
        prompts["chapter_outline"] = self.get_text("development/outline/chapter_outline.txt")
        prompts["settings_all_snippets"] = self.get_text("development/settings/settings_all_snippets.txt")
        prompts["character_all_snippets"] = self.get_text("development/characters/character_all_snippets.txt")
        seeds = self.get_text("development/settings/settings_seed.txt")
        
        print("Choose a setting to develop or you will be able to enter your own seed:")
        print(seeds)
        user_input = prompt("Enter the name of an existing setting or enter a short description of a new setting (or x to exit): ")
        prompts["seed"] = user_input
        if user_input == "x":
            return
        
        user_input = prompt("Give the setting a name (or x to exit): ")
        if user_input == "x":
            return
        
        setting_name = user_input.strip()
        llm_prompt = self.replace_prompts_in_template(self.GENERATE_SETTING_PROMPT, prompts)
        result = self.call_llm(llm_prompt)

        folder_name = setting_name.replace(" ", "_")
        full_path = f"development/settings/{folder_name}/full.txt"
        full_path_prompt = f"development/settings/{folder_name}/full_prompt.txt"

        user_input = prompt("Overwrite existing setting/location in "+full_path+"? (y/n): ")
        
        if user_input == "y":
            self.set_text(full_path, result)
            self.set_text(full_path_prompt, llm_prompt)

