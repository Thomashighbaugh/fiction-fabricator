# Explanation of Changes:
# - Added type hints for the class methods.
# - Added comments for better readability and understanding of the code.

import os
import glob
from source.bookchainelements.basebookchainelement import BaseBookChainElement

class JoinBook(BaseBookChainElement):
    def __init__(self, book_path: str):
        super().__init__(book_path)
        self.done: bool = False  # Indicates if the book joining process is complete

    def is_done(self) -> bool:  # Method to check if the book joining process is complete
        return self.done

    def step(self, llm_connection):  # Method to execute the book joining process
        # Define the path for the full book file.
        fullbook_path: str = os.path.join(self.book_path, "output", "fullbook.md")

        # Check if the full book file already exists.
        if os.path.exists(fullbook_path):
            print(f"Full book already exists at {fullbook_path}. Skipping.")
            self.done = True  # Mark the process as done
            return  # Exit the function if the full book already exists.

        # Open the full book file.
        with open(fullbook_path, "w") as fullbook_file:
            # Get the book title.
            book_title: str = self.get_book_title()  # Get the title of the book

            # Write the title to the full book file.
            fullbook_file.write(f"# {book_title}\n\n")

            # Get the table of contents.
            toc: str = self.get_toc()  # Get the table of contents

            # Write the table of contents to the full book file.
            fullbook_file.write(f"{toc}\n\n")

            # Get the chapter paths.
            chapter_paths: list = self.get_chapter_paths()  # Get the paths of all the chapters

            # Sort the chapter paths based on the chapter number.
            chapter_paths = sorted(chapter_paths, key=lambda x: int(x.split("_")[-1].replace(".txt", "")))

            # Iterate through the sorted chapter paths.
            for chapter_path in chapter_paths:
                print(f"Adding {chapter_path} to full book.")

                # Open the chapter file.
                with open(chapter_path, "r") as chapter_file:
                    # Read the chapter file.
                    chapter_text: str = chapter_file.read()  # Read the text from the chapter file

                    # Write the chapter text to the full book file.
                    fullbook_file.write(f"{chapter_text}\n\n")

        # Mark the process as done.
        self.done = True  # Mark the process as done