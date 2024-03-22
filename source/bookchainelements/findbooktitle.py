# Explanation of Changes:
# - Added type hints for the class and method parameters.
# - Removed unused imports.
# - Reordered the imports to follow PEP 8 guidelines.
# - Added comments to improve code readability.
# - Removed unnecessary print statements.

import os
from enum import Enum

from source.bookchainelements.basebookchainelement import BaseBookChainElement
from source.prompttemplate import PromptTemplate


class FindBookTitleSteps(str, Enum):
    set_system_message = "set system message"
    suggest_book_titles = "suggest book titles"
    rank_book_titles = "rank book titles"


class FindBookTitle(BaseBookChainElement):
    def __init__(self, book_path: str):
        super().__init__(book_path)
        self.current_step = FindBookTitleSteps.set_system_message
        self.done = False
        self.messages = []

    def is_done(self) -> bool:
        return self.done

    def step(self, llm_connection):
        # If the book titles file already exists, then we are done.
        if os.path.exists(self.title_path):
            # Skip FindBookTitle if the file already exists.
            self.done = True
            return

        # Print the current step.
        print(f'FindBookTitle step: "{self.current_step}"')

        # Set the system message.
        if self.current_step == FindBookTitleSteps.set_system_message:
            system_message = PromptTemplate.get_template("find_book_title_system_message")
            self.messages += [{"role": "system", "content": system_message}]
            self.current_step = FindBookTitleSteps.suggest_book_titles

        # Suggest initial list of book titles. Loads the initial description.
        elif self.current_step == FindBookTitleSteps.suggest_book_titles:
            with open(self.description_path, "r") as f:
                description = f.read()
            prompt = PromptTemplate.get_template("find_book_description_prompt").format(
                description
            )
            self.messages += [{"role": "user", "content": prompt}]
            response_message = llm_connection.chat(self.messages)
            self.messages += [response_message]
            self.current_step = FindBookTitleSteps.rank_book_titles

        # Rank the book titles.
        elif self.current_step == FindBookTitleSteps.rank_book_titles:
            prompt = PromptTemplate.get_template("rank_book_titles")
            self.messages += [{"role": "user", "content": prompt}]
            response_message = llm_connection.chat(self.messages)
            self.messages += [response_message]

            # Write the book titles to a file.
            book_titles = response_message["content"]
            with open(self.title_path, "w") as f:
                f.write(book_titles)

            self.done = True

        else:
            raise ValueError("current_step is None. This should not happen.")
