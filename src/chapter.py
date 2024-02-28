import json
import os
from pathlib import Path
import re
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import print_formatted_text
from src.base import Base, style


class Chapter(Base):
    def __init__(self, chapter_folder_name):
        super().__init__()

        self.chapter_folder_name = chapter_folder_name
        self.book_folder = self.path("book")
        self.chapter_outline = self.get_text(f"development/outline/chapter_outline.txt")
        self.working_chapter_folder = self.path("book") + "/" + chapter_folder_name
        self.WRITE_SCENE_PROMPT = self.get_text("prompts/scenes/write_scene.txt")

    
    def menu(self):
        print_formatted_text("\nSelect a chapter to work on:")
        submenu_items = {
            "1": {"name": "Split scenes from chapter_seed.txt into separate seed files", "action": lambda: self.split_scenes()},
            "2": {"name": "Write scene based on seed in chapter_seed.txt", "action": lambda: self.write_scene()},
            "3": {"name": "Auto copy edit an individual scene", "action": lambda: self.edit_scene()},
            "4": {"name": "Combine scenes into one file", "action": lambda: self.combine_scenes_into_chapter()},
            "5": {"name": "Copy edit scenes_combined file (full chapter) for consistency. Output consistent file.", "action": lambda: self.copy_edit_combined_scenes()},
            "10": {"name": "Do it all! Split into scenes, write scenes and copy edit, ", "action": lambda: self.do_it_all()},
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


    def do_it_all(self):
        self.split_scenes()
        scene_seed_list = self.get_list_of_files(self.working_chapter_folder, "scene_*[0-9]_seed.txt")
        for scene_seed in scene_seed_list:
            self.write_scene(scene_seed)
        scene_file = self.get_list_of_files(self.working_chapter_folder, "scene_*[0-9].txt")
        for scene in scene_file:
            self.edit_scene(scene)
        self.combine_scenes_into_chapter()


    def split_scenes(self):
        content = self.get_text(self.working_chapter_folder + "/chapter_seed.txt")
        scene_blocks = re.split(r'\n{2,}', content)
        scene_counter = 0
        for block in scene_blocks:
            if re.match(r'Chapter (.*), Scene:', block):
                scene_counter += 1
                file_name = f'scene_{scene_counter:02d}0_seed.txt'
                with open(self.working_chapter_folder +"/"+ file_name, 'w') as scene_file:
                    scene_file.write(block.strip())


    def get_character_list(self):
        return self.get_list_from_subfolder("development/characters")
    
    def get_settings_list(self):
        return self.get_list_from_subfolder("development/settings")
    
    def get_list_from_subfolder(self, folder_name):
        f_list = []
        folder_path = self.path(folder_name)
        for f in sorted(os.listdir(folder_path)):
            full_path = os.path.join(folder_path, f)
            if os.path.isdir(full_path):
                f_list.append(f)
        return f_list
    

    def get_scene_breakdown(self, chapter_seed, character_list, settings_list):
        character_string = ", ".join(character_list)
        settings_string = ", ".join(settings_list)
        prompt = (
            f"Please return the list of characters and settings from the scene description below.\n\n"
            f"{chapter_seed}\n\n"
            f"Only return characters that also appear in this list. Return them with the underlined in their name:\n"
            f"Characters: {character_string}\n"
            f"Only return settings that also appear in this list.  Return them with the underlined in their name:\n"
            f"Settings: {settings_string}\n"
            f"Please return the characters and settings in this format. Return only the json and nothing else."
            f"{{\"characters\": [\"character1\", \"character2\"], \"settings\": [\"setting1\", \"setting2\"]}}"
        )
        response = self.call_llm(prompt, temperature=0)
        return json.loads(response)


    def write_scene(self, scene_seed_file=None):
        if scene_seed_file is None:
            menu = self.get_menu_from_files(self.working_chapter_folder, "scene_*_seed.txt")
            print("Select a scene to write:")
            user_input = self.output_menu_with_prompt(menu)
            if user_input == "x":
                return  
            scene_seed_file = menu[user_input]["name"]

        scene_file = self.working_chapter_folder + "/" + scene_seed_file.replace("_seed.txt", ".txt")
        scene_prompt = self.working_chapter_folder + "/" + scene_seed_file.replace("_seed.txt", "_prompt.txt")
        chapter_seed = self.working_chapter_folder + "/" + scene_seed_file
        chapter_seed_text = self.get_text(chapter_seed)

        character_list = self.get_character_list()
        settings_list = self.get_settings_list()

        breakdown = self.get_scene_breakdown(chapter_seed_text, character_list, settings_list)
        required_characters = breakdown["characters"]
        required_settings = breakdown["settings"]

        character_texts = []
        for character in required_characters:
            if character in character_list:
                character_texts.append(character.replace("_"," ") + "\n" +self.get_text(f"development/characters/{character}/long_profile.txt"))
            else:
                print(f"Character {character} not found in character list. Please add it first.")

        setting_texts = []
        for setting in required_settings:
            if setting in settings_list:
                setting_texts.append(setting.replace("_"," ") + "\n" +self.get_text(f"development/settings/{setting}/full.txt"))
            else:
                print(f"Setting {setting} not found in settings list. Please add it first.")

        config = self.get_config()
        config["characters"] = "\n\n".join(character_texts)
        config["settings"] = "\n\n".join(setting_texts)
        config["scene"] = chapter_seed_text
        config["chapter_outline"] = self.chapter_outline

        full_prompt = self.replace_prompts_in_template(self.WRITE_SCENE_PROMPT, config)

        response = self.call_llm(full_prompt, temperature=0.9)

        if os.path.isfile(scene_file):
            confirmation = prompt(f"Replace the current text in {scene_file} (if it exists) with the new text? (y/n): ")
        else:
            confirmation = "y"

        if confirmation.lower() == "y":
            self.set_text(scene_file, response)
            self.set_text(scene_prompt, full_prompt)
            print("Text updated.")
        elif confirmation.lower() == "n":
            return
        else:
            print("Invalid input. Please try again.")


    def get_files_from_folder(self, folder, file_pattern):
        f_list = []
        for f in sorted(os.listdir(folder)):
            full_path = os.path.join(folder, f)
            if os.path.isfile(full_path) and re.match(file_pattern, f):
                f_list.append(f)
        return f_list

    def combine_scenes_into_chapter(self):
        scene_files = self.get_files_from_folder(self.working_chapter_folder, "scene_\d{3}\.txt")
        chapter_text = ""
        for scene_file in scene_files:
            chapter_text += self.get_text(self.working_chapter_folder + "/" + scene_file).strip() + "\n\n---\n\n"
        self.set_text(self.working_chapter_folder + "/chapter_scenes_combined.txt", chapter_text)
        print("Scenes combined into chapter.")
        
    
    def copy_edit_combined_scenes(self):
        text = self.get_text(self.working_chapter_folder + "/chapter_scenes_combined.txt")
        PROMPT = self.get_text("prompts/scenes/edit_combined_scenes.txt")
        full_prompt =  text + "\n\n\n" + PROMPT
        response = self.call_llm(full_prompt, temperature=0.5)
        revise_prompt = text + "\n\n\nPlease edit the text above using the suggested changes listed below.\n\n\n" + response
        response_edited = self.call_llm(revise_prompt, temperature=0.8)
        self.set_text(self.working_chapter_folder + "/chapter_scenes_consistent.txt", response_edited)


    def edit_scene(self, scene_file=None):
        if scene_file is None:
            menu = self.get_menu_from_files(self.working_chapter_folder, "scene_*[0-9].txt")
            print("Select a scene to auto edit:")
            user_input = self.output_menu_with_prompt(menu)
            if user_input == "x":
                return  
            scene_file = menu[user_input]["name"]
        scene_prompt = self.get_text("prompts/scenes/edit_scene.txt")
        voice_prompt = self.get_text("development/config/author_style.txt")
        scene_text = self.get_text(self.working_chapter_folder + "/" + scene_file)
        full_prompt = scene_text + "\n\n\n" + scene_prompt
        
        response = self.call_llm(full_prompt, temperature=0.5)
        revise_prompt = scene_text + "\n\n\nYou have the writing style: " + voice_prompt +"\n\nPlease edit the text above using the suggested changes listed below.\n\n\n" + response
        response_edited = self.call_llm(revise_prompt, temperature=0.8)
        self.set_text(self.working_chapter_folder + "/" + scene_file, response_edited)
        print("Scene updated.")
        
        
