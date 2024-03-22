from enum import Enum
import os

from source.bookchainelements.basebookchainelement import BaseBookChainElement
from source.prompttemplate import PromptTemplate


class WriteChapterSummariesSteps(str, Enum):
    set_system_message = "set system message"
    write_summaries = "write summaries"


class WriteChapterSummaries(BaseBookChainElement):
    """Class for writing chapter summaries of a book."""

    def __init__(self, book_path: str):
        """
        Initialize the WriteChapterSummaries object.

        Args:
            book_path (str): The path to the book.
        """
        super().__init__(book_path)
        self.current_step = WriteChapterSummariesSteps.set_system_message
        self.done = False
        self.messages = []

    def is_done(self) -> bool:
        """
        Check if the writing of chapter summaries is done.

        Returns:
            bool: True if done, False otherwise.
        """
        return self.done

    def step(self, llm_connection):
        """
        Perform the next step in writing chapter summaries.

        Args:
            llm_connection: The connection to the language model.
        """
        # Commented out the check for the existence of the table of contents file, as it is not used.
        # if os.path.exists(self.toc_path):
        #     print("Table of contents already exists. Skipping.")
        #     self.done = True
        #     return

        print(f"WriteTableOfContents step: \"{self.current_step}\"")

        current_step = self.current_step
        # Removed the unnecessary assignment of 'current_step' to 'None'.
        # self.current_step = None

        # Set the system message.
        if current_step == WriteChapterSummariesSteps.set_system_message:
            system_message = PromptTemplate.get_template("write_chaptersummary_system_message")
            self.messages += [{"role": "system", "content": system_message}]
            self.current_step = WriteChapterSummariesSteps.write_summaries

        # Suggest initial table of contents.
        elif current_step == WriteChapterSummariesSteps.write_summaries:

            # Get the book title.
            book_title = self.get_book_title()

            # Get the book description.
            description = self.get_book_description()

            # Get the table of contents.
            toc = self.get_toc()
            chapter_titles = toc.split("\n")
            chapter_titles = [title for title in chapter_titles if title.strip() != ""]

            for chapter_index, chapter_title in enumerate(chapter_titles):

                summary_path = os.path.join(self.book_path, "output", f"chapter_{chapter_index}.txt")
                if os.path.exists(summary_path):
                    print(f"Summary for chapter {chapter_index + 1} already exists. Skipping.")
                    continue

                print(f"Writing summary for chapter {chapter_index + 1} of {len(chapter_titles)}")

                prompt = PromptTemplate.get_template("write_chapter_summary").format(book_title, description, chapter_title)
                self.messages += [{"role": "user", "content": prompt}]
                response_message = llm_connection.chat(self.messages)
                self.messages = self.messages[:-1]

                # Write to a file.
                summary = response_message["content"]
                with open(summary_path, "w") as f:
                    f.write(summary)

            # Done.
            self.done = True

        # Added a try-except block to handle the case when 'current_step' is None.
        try:
            if current_step is None:
                raise ValueError("current_step is None. This should not happen.")
        except ValueError as e:
            print(e)
