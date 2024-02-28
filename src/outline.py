import json
import os
import re
from src.base import Base, style
from prompt_toolkit import prompt


class Outline(Base):
    def __init__(self):
        super().__init__()

        self.main_folder = self.path("development/scenes")
        self.GENERATE_SCENES_PROMPT = self.get_text(
            "prompts/scenes/write_chapter_scenes.txt"
        )
        self.GENERATE_SHORT_PROMPT = self.get_text("prompts/outline/short_summary.txt")

    def get_setting_from_file(self, file_path):
        setting_content = self.get_text(file_path)
        if not setting_content:
            return {}
        return json.loads(setting_content)

    def get_characters(self):
        character_files = [
            "development/characters/all_character_names.txt",
            "development/characters/all_character_snippets.txt",
        ]
        characters = []
        for file in character_files:
            content = self.get_text(file)
            lines = content.strip().split("\n")
            for line in lines:
                name, description = line.split(":")
                characters.append((name.strip(), description.strip()))
        return characters

    def menu(self):
        """
        Show the menu options for the Outline class.
        """
        print("\nOutline - Select an option:")
        submenu_items = {
            "1": {
                "name": "Generate novel idea/seed based on your config",
                "action": lambda: self.generate_idea(),
            },
            "2": {
                "name": "Generate a Plot Outline from Your Seed",
                "action": lambda: self.generate_plot_outline(),
            },
            "3": {
                "name": "Split the Plot Outline into Individual Chapter Files",
                "action": lambda: self.split_plot_outline_into_chapters(),
            },
            "4": {
                "name": "Generate chapter_summary.txt from a chapter_outline.txt",
                "action": lambda: self.generate_chapter_summary(),
            },
            "5": {
                "name": "Generate scenes (chapter_seed.txt) for a chapter in chapter_outline.txt",
                "action": lambda: self.define_scenes_for_chapter(),
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

    def generate_idea(self):
        """
        Generate a novel seed based on the config settings.
        """
        output_file = "development/outline/seed_summary.txt"
        summary_prompt = self.get_text("prompts/outline/summary.txt")
        settings = self.get_config()
        if not self.object_has_keys(settings, ["genre", "author_style", "themes"]):
            return
        llm_prompt = self.replace_prompts_in_template(summary_prompt, settings)

        print("Prompt is:")
        print(style.GREEN + llm_prompt)

        confirmation = prompt(f"Call LLM with prompt (y/n): ")
        if confirmation.lower() == "n":
            return

        response = self.call_llm(llm_prompt)

        confirmation = prompt(
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

    def generate_plot_outline(self):
        """
        Generate a plot outline from the seed based on the config settings.
        """

        settings = self.get_setting_from_file("development/settings/settings_summary.txt")
        characters = self.get_characters()
        plot_outline_prompt = self.get_text("prompts/outline/outline.txt")
        settings = self.get_config()
        if not self.object_has_keys(
            settings, ["seed_summary", "genre", "author_style", "themes", "tone"]
        ):
            return

        num_chapters = prompt(
            "Enter the number of chapters for the plot outline (or x to exit): "
        )
        if num_chapters == "x":
            return

        chapters_str = ""
        for i in range(1, int(num_chapters) + 1):
            chapter_str = f"Chapter {i}:\n\n"
            chapters_str += chapter_str

        settings["characters"] = characters
        settings["num_chapters"] = num_chapters
        llm_prompt = self.replace_prompts_in_template(plot_outline_prompt, settings)
        llm_prompt += chapters_str

        print("Prompt is:")
        print(style.GREEN + llm_prompt)

        confirmation = prompt(f"Call LLM with prompt (y/n): ")
        if confirmation.lower() == "n":
            return

        response = self.call_llm(llm_prompt)

        confirmation = prompt(
            f"Replace the current text in development/outline/plot_outline.txt with the new text? (y/n): "
        )

        if confirmation.lower() == "y":
            self.set_text("development/outline/plot_outline.txt", response)
            print("Text updated.")
        elif confirmation.lower() == "n":
            return
        else:
            print("Invalid input. Please try again.")

    # ──────────────────────────────────────────────────────

    def split_plot_outline_into_chapters(self):
        """
        Split the plot_outline into individual files for each chapter.
        Each chapter will be saved in its own subdirectory named after the chapter number.
        The chapter file itself will be called 'chapter_outline.txt'.
        """
        plot_outline = self.get_text("development/outline/plot_outline.txt")
        chapter_regex = r"Chapter (\d+):"
        matches = re.findall(chapter_regex, plot_outline, re.MULTILINE | re.DOTALL)

        num_chapters = len(matches)
        if num_chapters == 0:
            print("No chapters found in the plot outline.")
            return

        current_directory = os.getcwd()
        os.chdir("development/outline")

        for i, chapter in enumerate(matches, start=1):
            chapter_number = str(i).zfill(3)
            chapter_directory = f"{chapter_number}"
            os.mkdir(chapter_directory)
            os.chdir(chapter_directory)

            chapter_filename = f"chapter_outline.txt"
            with open(chapter_filename, "w") as f:
                f.write(chapter)

            print(
                f"Created directory '{chapter_directory}' and wrote Chapter {i} to {chapter_filename}"
            )

            os.chdir("..")  # Go back up one level

        os.chdir(current_directory)

    def generate_chapter_summary(self):
        """
        Generate chapter_summary.txt from full chapter_outline.txt.
        """
        full_text = self.get_text("development/outline/chapter_outline.txt")
        prompt_full = self.GENERATE_SHORT_PROMPT + "\n\n" + full_text
        result = self.call_llm(prompt_full)
        self.set_text("development/outline/chapter_summary.txt", result)


# ──────────────────────────────────────────────────────────────────────────────


def define_scenes_for_chapter(self):
    """
    Define scenes for a specific chapter based on the chapter outline.
    """
    chapter_summaries = self.get_text("development/outline/chapter_summary.txt")
    print("Choose which chapter to define scenes for:")
    print(chapter_summaries)

    prompts = self.get_config()
    prompts["chapter_outline"] = {}

    user_input = prompt("Chapter roman numeral/name (or 9 to exit): ")
    chapter_index = int(user_input) - 1
    chapter_key = list(
        self.get_text("development/outline/".format(chapter_index + 1)).keys()
    )[0]

    if chapter_index >= len(chapter_summaries) or chapter_index < 0:
        print("Invalid chapter index.")
        return

    chapter_data = self.get_text(
        "development/outline/{}/{}".format(chapter_index + 1, chapter_key)
    )
    chapter_title = chapter_data[: -len(chapter_key) - len(".txt")]

    self.set_config({"current_chapter": chapter_index})
    self.print_message(f"\nDefining scenes for Chapter {chapter_title}")

    scene_count = prompt("How many scenes would you like to write for this chapter? ")

    for _ in range(int(scene_count)):
        scene_number = prompt(
            "Scene number (or 'next' to move to next scene without writing): "
        )
        if scene_number != "next":
            scene_prompt = self.get_text("prompts/scenes/write_single_scene.txt")
            self.set_config({"current_scene": scene_number})
            self.run_interactive_generation(scene_prompt, chapter_data)
        else:
            break


# ──────────────────────────────────────────────────────────────────────────────


def generate_chapter_summary(self):
    """
    Generate chapter_summary.txt from full chapter_outline.txt.
    """
    chapter_number = prompt("Chapter number (or x to exit): ")
    if chapter_number == "x":
        return

    chapter_dir = f"development/outline/chapter_{chapter_number:03}"
    full_text = self.get_text(f"{chapter_dir}/chapter_outline.txt")
    prompt_full = self.GENERATE_SHORT_PROMPT + "\n\n" + full_text
    result = self.call_llm(prompt_full)

    # Create the directory if it doesn't exist yet
    if not os.path.exists(chapter_dir):
        os.mkdir(chapter_dir)

    # Save the generated chapter summary in the corresponding chapter directory
    chapter_summary_file = f"{chapter_dir}/chapter_summary.txt"
    with open(chapter_summary_file, "w") as f:
        f.write(result)

    print(
        f"Chapter {chapter_number} summary generated and saved at {chapter_summary_file}"
    )
