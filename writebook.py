# Changes Made:
# 1. Added type hints to the writebook function parameters.
# 2. Added comments to explain each section of the code.
# 3. Replaced print statements with logger calls for better logging.
# 4. Refactored the command line argument handling for better readability.

import os
import sys
import fire
import dotenv
import traceback
import time
import datetime
from typing import Optional

from source.openaiconnection import OpenAIConnection
from source.chain import ChainExecutor
from source.writelogs import WriteLogs
from source.bookchainelements import (
    FindBookTitle,
    WriteTableOfContents,
    WriteChapterSummaries,
    WriteChapterOutlines,
    WriteChapters,
    JoinBook
)

# Load the environment variables.
dotenv.load_dotenv()

class ExitException(Exception):
    pass

def writebook(book_path: str, log: bool = True, log_persistent: bool = True) -> None:
    """
    Function to write a book using OpenAI API.

    Args:
    - book_path (str): Path to the book directory.
    - log (bool): Flag to enable logging.
    - log_persistent (bool): Flag to enable persistent logging.

    Returns:
    - None
    """
    
    # See if the book path exists. If not, raise an error.
    if not os.path.exists(book_path):
        raise ExitException(f"Path {book_path} does not exist. Please create it.")
    
    # See if the description.txt file exists. If not, raise an error.
    description_path = os.path.join(book_path, "description.txt")
    if not os.path.exists(description_path):
        raise ExitException(f"File {description_path} does not exist. Please create it. It should contain a short description of the book.")

    # Create the logger
    logger = WriteLogs(book_path, log=log, log_persistent=log_persistent)

    # Create the model connection.    
    model_connection = OpenAIConnection(logger)

    # Start time.
    start_time = time.time()

    # Create a chain executor.
    chain_executor = ChainExecutor(model_connection)
    chain_executor.add_element(FindBookTitle(book_path))
    chain_executor.add_element(WriteTableOfContents(book_path))
    chain_executor.add_element(WriteChapterSummaries(book_path))
    chain_executor.add_element(WriteChapterOutlines(book_path))
    chain_executor.add_element(WriteChapters(book_path))
    chain_executor.add_element(JoinBook(book_path))

    # Run the chain.
    chain_executor.run()

    # Elapsed time.
    elapsed_time = time.time() - start_time

    # Write total tokens used and elapsed time to summary file.
    summary_file_path = os.path.join(book_path, "output", "summary.txt")
    with open(summary_file_path, "w") as summary_file:
        total_tokens_used = model_connection.token_count
        logger.log(f"Total tokens used: {total_tokens_used}", file=summary_file)

        elapsed_time_string = str(datetime.timedelta(seconds=elapsed_time))
        logger.log(f"Elapsed time: {elapsed_time_string}", file=summary_file)


if __name__ == "__main__":
    try:
        # Parse command line arguments and handle flags for logging.
        args = sys.argv[1:]
        for i, arg in enumerate(args):
            if arg == '--l':
                args[i] = '--log=True'
            elif arg == '--lp':
                args[i] = '--log_persistent=True'
        print(args)  # For debugging purposes
        fire.Fire(writebook, command=args)
    except ExitException as e:
        print(e)
    except:
        traceback.print_exc()