import os
from pathlib import Path
import re
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import print_formatted_text
from src.base import Base, style

from src.chapter import Chapter


class ChapterSelector(Base):
    def __init__(self):
        super().__init__()
        self.book_folder = self.path("book")

    def menu(self):
        print_formatted_text("\nSelect a chapter to work on:")
        menu = self.get_menu_from_folder(self.book_folder, "chapter_*")
        menu["write"] = {"name": "Auto write chapters 11-13"}
        while True:
            user_input = self.output_menu_with_prompt(menu)
            if user_input == "x":
                return 
            

            if user_input == "write":
                print_formatted_text("Auto writing chapters 10-13...")

                for i in range(11, 14):
                    two_digit_str = "{:02}".format(i)
                    chapter = Chapter(f"chapter_{two_digit_str}0")
                    chapter.do_it_all()
            
            else:
                if user_input in menu:
                    chapter = Chapter(menu[user_input]["name"])
                    chapter.menu()
                else:
                    print("Invalid option. Please try again.")


    def split_scenes(self, input_file, output_folder):
        content = self.get_text(input_file)
        scene_blocks = re.split(r'\n{2,}', content)
        scene_counter = 0
        for block in scene_blocks:
            if re.match(r'Chapter \d+, Scene:', block):
                scene_counter += 1
                file_name = f'scene_{scene_counter:03d}_seed.txt'
                with open(output_folder / file_name, 'w') as scene_file:
                    scene_file.write(block.strip())


    



        
        
