# Explanation for changes:
# 1. Moved imports to the top for better organization and readability.
# 2. Added type hints for function parameters and return types.
# 3. Added comments for better code readability and understanding.

import os
import glob

from source.chain import BaseChainElement


class BaseBookChainElement(BaseChainElement):
    def __init__(self, book_path: str):
        """
        Initialize the BaseBookChainElement with the book path and set up necessary file paths.
        Args:
        - book_path (str): The path to the book directory.
        """
        self.book_path = book_path
        self.description_path = os.path.join(self.book_path, "description.txt")
        self.title_path = os.path.join(self.book_path, "output", "book_titles.txt")
        self.toc_path = os.path.join(self.book_path, "output", "toc.txt")

        # Create the output directory if it does not exist.
        if not os.path.exists(os.path.join(self.book_path, "output")):
            os.makedirs(os.path.join(self.book_path, "output"))

    def get_book_title(self) -> str:
        """
        Get the title of the book from the specified file.
        Returns:
        - str: The title of the book.
        """
        with open(self.title_path, "r") as f:
            title = f.read()

        # Get the first line and remove the number.
        title = title.split("\n")[0]
        title = title.replace("1. ", "")
        return title

    def get_book_description(self) -> str:
        """
        Get the description of the book from the specified file.
        Returns:
        - str: The description of the book.
        """
        with open(self.description_path, "r") as f:
            description = f.read()
        return description

    def get_toc(self) -> str:
        """
        Get the table of contents of the book from the specified file.
        Returns:
        - str: The table of contents of the book.
        """
        with open(self.toc_path, "r") as f:
            toc = f.read()
        return toc

    def _get_summary_or_outline_paths(self, pattern: str) -> list:
        """
        Get the paths of either chapter summary or outline files based on the specified pattern.
        Args:
        - pattern (str): The pattern to match the file paths.
        Returns:
        - list: List of file paths matching the specified pattern.
        """
        summary_paths = glob.glob(os.path.join(self.book_path, "output", pattern))
        summary_paths = sorted(summary_paths)
        return summary_paths

    def get_chapter_summary_paths(self) -> list:
        """
        Get the paths of chapter summary files.
        Returns:
        - list: List of paths to chapter summary files.
        """
        return self._get_summary_or_outline_paths("chapter_*.txt")

    def get_chapter_outline_paths(self) -> list:
        """
        Get the paths of chapter outline files.
        Returns:
        - list: List of paths to chapter outline files.
        """
        return self._get_summary_or_outline_paths("chapteroutline_*.txt")

    def get_chapter_paths(self) -> list:
        """
        Get the paths of full chapter files.
        Returns:
        - list: List of paths to full chapter files.
        """
        chapter_paths = glob.glob(os.path.join(self.book_path, "output", "chapterfull_*.txt"))
        chapter_paths = sorted(chapter_paths)
        return chapter_paths