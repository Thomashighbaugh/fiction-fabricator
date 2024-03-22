import os
import sys
import fire
import dotenv
import traceback
import time
import datetime
from typing import Optional

# Importing custom modules for book writing process.
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

# Load the environment variables from the .env file.
dotenv.load_dotenv()

# Custom exception for early termination of the script with an error message.
class ExitException(Exception):
    pass

# Function to orchestrate the book writing process using the OpenAI API.
def writebook(book_path: str, log: bool = True, log_persistent: bool = True) -> None:
    """
    Orchestrates the process of writing a book by executing a series of steps (chain elements).
    
    Args:
        book_path (str): The directory path where the book will be written.
        log (bool, optional): Enables logging of the process. Defaults to True.
        log_persistent (bool, optional): Enables persistent logging across sessions. Defaults to True.
    
    Raises:
        ExitException: If the book_path or description.txt does not exist.
    
    Returns:
        None
    """
    
    # Check if the book path exists, raise an error if it does not.
    if not os.path.exists(book_path):
        raise ExitException(f"Path {book_path} does not exist. Please create it.")
    
    # Check if the description.txt file exists, raise an error if it does not.
    description_path = os.path.join(book_path, "description.txt")
    if not os.path.exists(description_path):
        raise ExitException(f"File {description_path} does not exist. Please create it. It should contain a short description of the book.")

    # Initialize the logger for the book writing process.
    logger = WriteLogs(book_path, log=log, log_persistent=log_persistent)

    # Establish a connection to the OpenAI model.
    model_connection = OpenAIConnection(logger)

    # Record the start time of the book writing process.
    start_time = time.time()

    # Initialize the chain executor with the model connection.
    chain_executor = ChainExecutor(model_connection)
    # Add each step of the book writing process to the chain executor.
    chain_executor.add_element(FindBookTitle(book_path))
    chain_executor.add_element(WriteTableOfContents(book_path))
    chain_executor.add_element(WriteChapterSummaries(book_path))
    chain_executor.add_element(WriteChapterOutlines(book_path))
    chain_executor.add_element(WriteChapters(book_path))
    chain_executor.add_element(JoinBook(book_path))

    # Execute the chain of steps to write the book.
    chain_executor.run()

    # Calculate the elapsed time of the book writing process.
    elapsed_time = time.time() - start_time

    # Write the total tokens used and elapsed time to the summary file.
    summary_file_path = os.path.join(book_path, "output", "summary.txt")
    with open(summary_file_path, "w") as summary_file:
#        total_tokens_used = model_connection.token_count
        #logger.log(f"Total tokens used: {total_tokens_used}", file=summary_file)

        elapsed_time_string = str(datetime.timedelta(seconds=elapsed_time))
        #logger.log(f"Elapsed time: {elapsed_time_string}", file=summary_file)

# Entry point of the script.
if __name__ == "__main__":
    try:
        # Parse command line arguments and convert flags for logging.
        args = sys.argv[1:]
        for i, arg in enumerate(args):
            if arg == '--l':
                args[i] = '--log=True'
            elif arg == '--lp':
                args[i] = '--log_persistent=True'
        # Use logger instead of print for debugging purposes.
        #logger.log(str(args))  # Uncomment this line to enable logging of arguments.
        # Execute the writebook function with the parsed arguments.
        fire.Fire(writebook, command=args)
    except ExitException as e:
        # Use logger instead of print for error reporting.
        #logger.log(str(e))  # Uncomment this line to enable logging of the exception.
        pass  # Handle the custom ExitException without printing the message.
    except:
        # Log the full traceback for any other exceptions that occur.
        traceback.print_exc()
