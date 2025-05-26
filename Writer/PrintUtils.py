# File: AIStoryWriter/Writer/PrintUtils.py
# Purpose: Utilities for logging and colored console output.

"""
Logging and Printing Utilities.

This module provides a `Logger` class for:
- Writing timestamped log messages to both a file and the console.
- Coloring console output based on log level using `termcolor`.
- Saving Langchain message histories (LLM interactions) to separate debug files
  in both JSON and Markdown formats.
- Saving the final generated story to disk.
"""

import termcolor
import datetime
import os
import json
from typing import List, Dict, Any, Optional

# Import Config directly to check DEBUG flags if needed within Logger,
# e.g., for conditional printing of verbose stream chunks.
import Writer.Config as Config


class Logger:
    """
    Handles logging of messages to file and console, and saving debug information.
    """

    _LOG_LEVEL_COLORS: Dict[int, str] = {
        0: "white",  # General Info / Startup
        1: "light_grey",  # Minor Info / Steps
        2: "blue",  # Debug Info
        3: "cyan",  # Key Process Info
        4: "magenta",  # Important Milestones
        5: "green",  # Success / Completion
        6: "yellow",  # Warnings
        7: "red",  # Errors / Critical Issues
    }
    _DEFAULT_COLOR = "white"

    def __init__(self, log_dir_base: str = "Logs"):
        """
        Initializes the Logger, creating necessary log directories and files.

        Args:
            log_dir_base (str): The base directory name for storing all generation logs.
                                Default is "Logs".
        """
        current_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_session_dir = os.path.join(
            log_dir_base, f"Generation_{current_timestamp}"
        )
        self.langchain_debug_dir = os.path.join(self.log_session_dir, "LangchainDebug")

        os.makedirs(self.langchain_debug_dir, exist_ok=True)

        self.main_log_path = os.path.join(self.log_session_dir, "Main.log")

        try:
            # Open in append mode, create if not exists, with UTF-8 encoding
            self.log_file_handle = open(self.main_log_path, "a", encoding="utf-8")
        except IOError as e:
            print(
                f"CRITICAL: Could not open main log file at {self.main_log_path}. Error: {e}"
            )
            self.log_file_handle = None  # Indicate failure

        self.langchain_interaction_id: int = 0
        self.log_items_buffer: List[str] = (
            []
        )  # Could be used for batch writing if needed

        self.Log(
            f"Logger initialized. Log session directory: {self.log_session_dir}", 0
        )

    def save_langchain_interaction(
        self, interaction_label: str, messages: List[Dict[str, Any]]
    ) -> None:
        """
        Saves a list of LLM messages (an interaction chain) to JSON and Markdown files
        for debugging purposes.

        Args:
            interaction_label (str): A label for this interaction (e.g., function_name.model_name).
                                     This will be part of the filename.
            messages (List[Dict[str, Any]]): The list of message dictionaries.
        """
        if not self.log_file_handle:  # Don't attempt if main log failed
            print(
                f"WARNING: Main log file not open. Skipping SaveLangchain for {interaction_label}."
            )
            return

        # Sanitize label for filename
        safe_label = "".join(
            c if c.isalnum() or c in [".", "_"] else "_" for c in interaction_label
        )
        base_filename = f"{self.langchain_interaction_id:03d}_{safe_label}"
        self.langchain_interaction_id += 1

        json_filepath = os.path.join(self.langchain_debug_dir, f"{base_filename}.json")
        md_filepath = os.path.join(self.langchain_debug_dir, f"{base_filename}.md")

        try:
            # Save JSON version
            with open(json_filepath, "w", encoding="utf-8") as f_json:
                json.dump(messages, f_json, indent=2, ensure_ascii=False)

            # Save Markdown version
            md_content = f"# Langchain Interaction: {interaction_label}\n*(ID: {base_filename})*\n\n---\n"
            for msg in messages:
                role = msg.get("role", "unknown_role")
                content = str(msg.get("content", ""))  # Ensure content is string

                # Basic sanitization for Markdown: escape backticks inside content if not part of a code block
                # This is a simplified approach. A robust solution might need a Markdown library.
                # For now, just replace them to avoid breaking the triple-backtick code block.
                safe_content = content.replace("`", "\\`")

                md_content += (
                    f"\n\n## Role: `{role}`\n\n```text\n{safe_content}\n```\n\n---\n"
                )

            with open(md_filepath, "w", encoding="utf-8") as f_md:
                f_md.write(md_content)

            self.Log(
                f"Saved Langchain interaction '{interaction_label}' to {base_filename}.[json|md]",
                0,
            )
        except IOError as e:
            self.Log(
                f"ERROR: Could not write Langchain debug files for {interaction_label}. Error: {e}",
                7,
            )
        except Exception as e:  # Catch any other unexpected errors during saving
            self.Log(
                f"UNEXPECTED ERROR during SaveLangchain for {interaction_label}: {e}", 7
            )

    def save_artifact(
        self, content: str, filename: str, subdirectory: Optional[str] = None
    ) -> None:
        """
        Saves arbitrary text content (like a generated story, outline, etc.) to a file
        within the current log session directory.

        Args:
            content (str): The text content to save.
            filename (str): The desired filename (e.g., "FinalStory.md", "DetailedOutline.txt").
            subdirectory (Optional[str]): If specified, creates and saves within this subdirectory
                                          of the log_session_dir.
        """
        if not self.log_file_handle:
            print(
                f"WARNING: Main log file not open. Skipping SaveArtifact for {filename}."
            )
            return

        save_path_dir = self.log_session_dir
        if subdirectory:
            save_path_dir = os.path.join(self.log_session_dir, subdirectory)
            os.makedirs(save_path_dir, exist_ok=True)

        filepath = os.path.join(save_path_dir, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            self.Log(f"Saved artifact to: {filepath}", 1)
        except IOError as e:
            self.Log(f"ERROR: Could not write artifact '{filename}'. Error: {e}", 7)
        except Exception as e:
            self.Log(f"UNEXPECTED ERROR during SaveArtifact for {filename}: {e}", 7)

    def Log(self, item: str, level: int, stream: bool = False) -> None:
        """
        Logs a message to the main log file and prints a colored version to the console.

        Args:
            item (str): The message string to log.
            level (int): The log level (0-7). Higher numbers indicate more severity/importance.
            stream (bool): If True, indicates this is part of a streamed output (e.g., LLM chunks).
                           Affects console printing if DEBUG_LEVEL is low.
        """
        # Python's datetime.now() gives microsecond precision. strftime format for milliseconds:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[
            :-3
        ]  # Format to milliseconds

        # Ensure level is within bounds for coloring
        safe_level = max(0, min(level, max(self._LOG_LEVEL_COLORS.keys())))

        log_entry_raw = f"[{str(safe_level).ljust(2)}] [{timestamp}] {item}"

        if self.log_file_handle:
            try:
                self.log_file_handle.write(log_entry_raw + "\n")
                self.log_file_handle.flush()  # Ensure it's written immediately for live monitoring
            except IOError as e:
                # If writing to log file fails, print a critical error to console
                # This should not happen if __init__ was successful
                print(
                    f"CRITICAL FILE ERROR: Could not write to main log. Original message: {log_entry_raw}. Error: {e}"
                )

        # Add to buffer if needed (not currently used for batching, but structure is there)
        self.log_items_buffer.append(log_entry_raw)

        # Console output
        color = self._LOG_LEVEL_COLORS.get(safe_level, self._DEFAULT_COLOR)

        # For streamed content, only print to console if DEBUG is enabled and DEBUG_LEVEL is high enough
        # Config.DEBUG is a boolean, Config.DEBUG_LEVEL is an int (0: off, 1: some, 2: all)
        should_print_to_console = True
        if stream:  # This is a chunk of a streamed response
            if (
                not Config.DEBUG or Config.DEBUG_LEVEL < 2
            ):  # Only print stream chunks if high debug level
                should_print_to_console = False

        if should_print_to_console:
            try:
                print(termcolor.colored(log_entry_raw, color))
            except Exception as e:  # termcolor might fail in some environments
                print(f"Termcolor formatting failed: {e}. Raw log: {log_entry_raw}")
                print(log_entry_raw)  # Print raw if coloring fails

    def close(self) -> None:
        """
        Closes the main log file. Should be called at the end of the application.
        """
        if self.log_file_handle and not self.log_file_handle.closed:
            self.Log("Closing logger.", 0)
            self.log_file_handle.close()
            self.log_file_handle = None

    def __del__(self) -> None:
        """
        Ensures the log file is closed when the Logger instance is garbage collected.
        """
        self.close()
