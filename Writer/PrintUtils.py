# File: AIStoryWriter/Writer/PrintUtils.py
# Purpose: Provides logging utilities with timestamping, leveling, and file output.
#          Includes functionality to save Langchain message history for debugging.

import termcolor  # type: ignore
import datetime
import os
import json
from typing import List, Dict, Optional, IO

# Attempt to import Config for DEBUG_LEVEL, handle if not available during early init
try:
    from .. import Config
except ImportError:
    # Mock Config if it's not available (e.g., if PrintUtils is used standalone for some reason)
    class MockConfig:
        DEBUG = False
        DEBUG_LEVEL = 0

    Config = MockConfig()  # type: ignore


class Logger:
    """
    Handles logging of messages to console and file with different levels.
    Also supports saving Langchain message sequences for debugging.
    """

    def __init__(self, log_file_prefix: str = "Logs", log_to_console: bool = True):
        self.log_to_console = log_to_console
        self.log_dir_prefix: str = ""
        self.log_path: str = ""
        self.file_handler: Optional[IO[str]] = None
        self.langchain_log_id_counter: int = 0
        self.log_items_buffer: List[str] = []  # In-memory buffer for recent logs

        self._initialize_logging(log_file_prefix)

    def _initialize_logging(self, log_file_prefix: str) -> None:
        """Sets up the log directory and main log file."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.log_dir_prefix = os.path.join(
                log_file_prefix, f"Generation_{timestamp}"
            )

            langchain_debug_dir = os.path.join(self.log_dir_prefix, "LangchainDebug")
            os.makedirs(langchain_debug_dir, exist_ok=True)

            self.log_path = os.path.join(self.log_dir_prefix, "Main.log")
            self.file_handler = open(self.log_path, "a", encoding="utf-8")

            self.Log(f"Logger initialized. Log directory: {self.log_dir_prefix}", 0)
        except OSError as e:
            # Fallback if directory creation fails (e.g. permissions)
            print(
                f"Error initializing logger directory: {e}. Logging to console only.",
                file=sys.stderr,
            )
            self.file_handler = None
            self.log_dir_prefix = ""  # Ensure no file operations are attempted

    def SaveLangchain(
        self, langchain_id_suffix: str, langchain_messages: List[Dict[str, str]]
    ) -> None:
        """
        Saves a Langchain message sequence to JSON and Markdown files for debugging.

        Args:
            langchain_id_suffix: A descriptive suffix for the log files (e.g., "ModuleName.FunctionName").
            langchain_messages: The list of message dictionaries to save.
        """
        if (
            not self.log_dir_prefix or not self.file_handler
        ):  # Logging to file disabled or failed
            if Config.DEBUG:
                print(
                    f"Debug (Console Only): Would save Langchain for {langchain_id_suffix}. Messages: {len(langchain_messages)}",
                    file=sys.stderr,
                )
            return

        current_log_id = self.langchain_log_id_counter
        self.langchain_log_id_counter += 1

        # Sanitize langchain_id_suffix to be a valid filename part
        safe_suffix = "".join(
            c if c.isalnum() or c in [".", "_"] else "_" for c in langchain_id_suffix
        )
        base_filename = f"{current_log_id:03d}_{safe_suffix}"[
            :200
        ]  # Cap filename length

        json_file_path = os.path.join(
            self.log_dir_prefix, "LangchainDebug", f"{base_filename}.json"
        )
        md_file_path = os.path.join(
            self.log_dir_prefix, "LangchainDebug", f"{base_filename}.md"
        )

        try:
            # Save JSON version
            with open(json_file_path, "w", encoding="utf-8") as f_json:
                json.dump(langchain_messages, f_json, indent=2, ensure_ascii=False)

            # Save Markdown version
            md_content = [f"# Debug LangChain: {base_filename}\n"]
            md_content.append(f"**Source Suffix:** `{langchain_id_suffix}`\n")
            md_content.append(
                f"**Timestamp:** `{datetime.datetime.now().isoformat()}`\n"
            )
            md_content.append("---\n")

            for msg_idx, message in enumerate(langchain_messages):
                role = message.get("role", "unknown_role")
                content = str(message.get("content", ""))  # Ensure content is string

                md_content.append(f"## Message {msg_idx + 1}: Role `{role}`\n")
                # Use text block for content to handle ``` within content
                md_content.append("```text")
                md_content.append(content if content.strip() else "[EMPTY CONTENT]")
                md_content.append("```\n")

            with open(md_file_path, "w", encoding="utf-8") as f_md:
                f_md.write("\n".join(md_content))

            self.Log(
                f"Saved Langchain debug data for '{base_filename}'", 1
            )  # Lowered log level for this
        except IOError as e:
            self.Log(f"Error saving Langchain debug data for '{base_filename}': {e}", 6)
        except Exception as e_gen:  # Catch any other unexpected error
            self.Log(
                f"Unexpected error saving Langchain debug for '{base_filename}': {e_gen}",
                7,
            )

    def SaveStory(
        self, story_content: str, filename: str = "Generated_Story.md"
    ) -> None:
        """Saves the provided story content to a file in the log directory."""
        if not self.log_dir_prefix or not self.file_handler:
            if Config.DEBUG:
                print(
                    f"Debug (Console Only): Would save story '{filename}'. Content length: {len(story_content)}",
                    file=sys.stderr,
                )
            return

        # Sanitize filename
        safe_filename = "".join(
            c if c.isalnum() or c in [".", "_", "-"] else "_" for c in filename
        )
        story_file_path = os.path.join(self.log_dir_prefix, safe_filename)

        try:
            with open(story_file_path, "w", encoding="utf-8") as f_story:
                f_story.write(story_content)
            self.Log(f"Story content saved to: {story_file_path}", 2)
        except IOError as e:
            self.Log(f"Error saving story content to '{story_file_path}': {e}", 6)

    def Log(self, item: str, level: int, stream_chunk: bool = False) -> None:
        """
        Logs a message to the console (if enabled) and to the main log file.

        Args:
            item: The message string to log.
            level: An integer indicating the log level (0-7).
                   Higher numbers indicate higher severity or importance.
                   0: Trace/Verbose, 1: Debug, 2: Info, 3: Notice,
                   4: Warning, 5: Error, 6: Critical, 7: Fatal/Alert
            stream_chunk: If True, indicates this is part of a streamed response.
                          May be handled differently for console output to avoid clutter.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[
            :-3
        ]  # Milliseconds
        log_entry = f"[{level}] [{timestamp}] {item}"

        # Write to file if handler is available
        if self.file_handler and not self.file_handler.closed:
            try:
                self.file_handler.write(log_entry + "\n")
                self.file_handler.flush()  # Ensure it's written immediately for tailing
            except Exception as e:
                # If file logging fails, print an error to console and disable file handler
                if self.log_to_console:
                    print(
                        f"CRITICAL: Failed to write to log file '{self.log_path}': {e}. Further file logging disabled.",
                        file=sys.stderr,
                    )
                self.file_handler.close()  # type: ignore # Close it to prevent further attempts
                self.file_handler = None

        # Add to in-memory buffer (e.g., for showing recent logs on error)
        self.log_items_buffer.append(log_entry)
        if len(self.log_items_buffer) > 200:  # Keep last 200 logs
            self.log_items_buffer.pop(0)

        # Print to console if enabled
        if self.log_to_console:
            # Conditional printing for stream chunks to reduce console noise
            # Only print stream chunks if DEBUG mode is on and DEBUG_LEVEL is high enough
            if stream_chunk and not (Config.DEBUG and Config.DEBUG_LEVEL > 1):
                return  # Skip console output for this stream chunk

            color_map = {
                0: "grey",  # Trace
                1: "cyan",  # Debug (was grey, changed for better visibility)
                2: "green",  # Info
                3: "blue",  # Notice
                4: "yellow",  # Warning
                5: "red",  # Error
                6: "magenta",  # Critical (was yellow)
                7: "red",  # Fatal (attrs=['bold'] could be added)
            }
            attrs_map = {7: ["bold"]}

            color = color_map.get(level, "white")  # Default to white
            attrs = attrs_map.get(level)

            try:
                colored_log_entry = termcolor.colored(log_entry, color, attrs=attrs)
                print(colored_log_entry)
            except Exception:  # termcolor might not be available or fail
                print(log_entry)

    def GetRecentLogs(self, count: int = 20) -> List[str]:
        """Returns the most recent 'count' log entries from the buffer."""
        return self.log_items_buffer[-count:]

    def Close(self) -> None:
        """Closes the log file handler if it's open."""
        if self.file_handler and not self.file_handler.closed:
            self.Log("Logger shutting down. Closing log file.", 0)
            self.file_handler.close()
            self.file_handler = None

    def __del__(self) -> None:
        self.Close()


# Example usage (typically not run directly from here)
if __name__ == "__main__":
    # This is for testing PrintUtils.py itself
    Config.DEBUG = True  # Enable debug mode for this test
    Config.DEBUG_LEVEL = 2  # Show stream chunks

    test_logger = Logger(log_file_prefix="TestLogs")
    test_logger.Log("This is a trace message (level 0).", 0)
    test_logger.Log("This is a debug message (level 1).", 1)
    test_logger.Log("This is an info message (level 2).", 2)
    test_logger.Log("This is a notice message (level 3).", 3)
    test_logger.Log("This is a warning message (level 4).", 4)
    test_logger.Log("This is an error message (level 5).", 5)
    test_logger.Log("This is a critical message (level 6).", 6)
    test_logger.Log("This is a fatal message (level 7).", 7)

    test_logger.Log("Simulating a stream chunk...", 2, stream_chunk=True)
    test_logger.Log("Another stream chunk...", 2, stream_chunk=True)

    mock_langchain_messages = [
        {"role": "system", "content": "You are an assistant."},
        {"role": "user", "content": "Hello, world!"},
        {"role": "assistant", "content": "Hello to you too! ```code``` example."},
    ]
    test_logger.SaveLangchain("Test.ExampleFunction", mock_langchain_messages)
    test_logger.SaveStory("# My Test Story\n\nOnce upon a time...", "TestStory.md")

    print("\nRecent logs:")
    for entry in test_logger.GetRecentLogs(5):
        print(entry)

    test_logger.Close()
    print("Test logger closed. Check TestLogs directory.")
