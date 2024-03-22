# Changes made:
# - Added comments to improve code readability.
# - Removed unnecessary imports.

import os
from enum import Enum
from source.bookchainelements.basebookchainelement import BaseBookChainElement
from source.prompttemplate import PromptTemplate

# Enum class for different steps in the WriteChapters process
class WriteChaptersSteps(str, Enum):
    set_system_message = "set system message"
    write_chapters = "write chapters"

# Class for writing chapters in a book
class WriteChapters(BaseBookChainElement):
    def __init__(self, book_path: str):
        super().__init__(book_path)
        self.current_step: WriteChaptersSteps = WriteChaptersSteps.set_system_message
        self.done: bool = False
        self.messages: list = []

    def is_done(self) -> bool:
        return self.done

    def chapter_exists(self, chapter_path: str) -> bool:
        """
        Checks if the chapter file already exists.
        Args:
            chapter_path (str): Path to the chapter file.
        Returns:
            bool: True if the chapter file exists, False otherwise.
        """
        return os.path.exists(chapter_path)

    def step(self, llm_connection):
        print(f"WriteChapters step: \"{self.current_step}\"")

        current_step = self.current_step
        self.current_step = None

        # Set the system message.
        if current_step == WriteChaptersSteps.set_system_message:
            system_message = PromptTemplate.get_template("write_chapters_system_message")
            self.messages += [{"role": "system", "content": system_message}]
            self.current_step = WriteChaptersSteps.write_chapters

        # Write chapters
        elif current_step == WriteChaptersSteps.write_chapters:
            # Get the book title.
            book_title = self.get_book_title()

            # Get the chapter summaries.
            chapter_outline_paths = self.get_chapter_outline_paths()
            for chapter_index, chapter_outline_path in enumerate(chapter_outline_paths):
                print(f"Working on chapter {chapter_index + 1}/{len(chapter_outline_paths)}...")

                chapter_path = chapter_outline_path.replace("chapteroutline_", "chapterfull_")
                if self.chapter_exists(chapter_path):
                    print(f"Chapter {chapter_path} already exists. Skipping.")
                    continue

                # Get the chapter summary path.
                chapter_summary_path = chapter_outline_path.replace("chapteroutline_", "chapter_")

                # Get the chapter summary.
                with open(chapter_summary_path, "r") as f:
                    chapter_summary = f.read()

                # Get the outline.
                with open(chapter_outline_path, "r") as f:
                    chapter_outlines = f.read()
                    chapter_outlines_lines = chapter_outlines.split("\n")

                # Open the chapter file.
                chapter_file = open(chapter_path, "w")

                # Create the prompt.
                prompt = PromptTemplate.get_template("write_chapter").format(chapter_summary, chapter_outlines)
                self.messages += [{"role": "user", "content": prompt}]

                for chapter_outlines_line_index, chapter_outlines_line in enumerate(chapter_outlines_lines):
                    print(f"Working on chapter outline line {chapter_outlines_line_index + 1}/{len(chapter_outlines_lines)}...")

                    # Create the prompt.
                    prompt = PromptTemplate.get_template("write_chapter_line").format(chapter_outlines_line)
                    self.messages += [{"role": "user", "content": prompt}]

                    # Get the response.
                    response_message = llm_connection.chat(self.messages, long=True)

                    self.messages += [response_message]

                    # Write to a file.
                    chapter = response_message["content"]
                    chapter_file.write(chapter)
                    chapter_file.write("\n\n")

                    # Flush the file.
                    chapter_file.flush()

                # Close the file.
                chapter_file.close()

            # Done.
            self.done = True

        elif current_step is None:
            raise ValueError("current_step is None. This should not happen.")
