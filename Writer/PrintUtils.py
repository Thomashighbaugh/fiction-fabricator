#!/usr/bin/python3

import os
import json
import datetime
import termcolor
import Writer.Config


class Logger:

    def __init__(self, _LogfilePrefix="Logs"):
        """
        Initializes the logger, creating a unique directory for each run.
        """
        # Make Paths For Log
        log_dir_name = f"{Writer.Config.PROJECT_NAME}_" + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_dir_path = os.path.join(_LogfilePrefix, log_dir_name)
        
        self.LangchainDebugPath = os.path.join(log_dir_path, "LangchainDebug")
        os.makedirs(self.LangchainDebugPath, exist_ok=True)

        # Setup Log Path
        self.LogDirPrefix = log_dir_path
        self.LogPath = os.path.join(log_dir_path, "Main.log")
        self.File = open(self.LogPath, "a", encoding='utf-8')
        self.LangchainID = 0

    def SaveLangchain(self, _LangChainID: str, _LangChain: list):
        """
        Saves the entire language chain object as both JSON and Markdown for debugging.
        """
        # Sanitize the ID for use in file paths
        safe_id = "".join(c for c in _LangChainID if c.isalnum() or c in ('-', '_')).rstrip()
        
        # Calculate Filepath For This Langchain
        this_log_path_json = os.path.join(self.LangchainDebugPath, f"{self.LangchainID}_{safe_id}.json")
        this_log_path_md = os.path.join(self.LangchainDebugPath, f"{self.LangchainID}_{safe_id}.md")
        langchain_debug_title = f"{self.LangchainID}_{safe_id}"
        self.LangchainID += 1

        # Generate and Save JSON Version
        try:
            with open(this_log_path_json, "w", encoding='utf-8') as f:
                json.dump(_LangChain, f, indent=4, sort_keys=True)
        except Exception as e:
            self.Log(f"Failed to write Langchain JSON log for {langchain_debug_title}. Error: {e}", 7)

        # Now, Save Markdown Version
        try:
            with open(this_log_path_md, "w", encoding='utf-8') as f:
                markdown_version = f"# Debug LangChain {langchain_debug_title}\n**Note: '```' tags have been removed in this version.**\n"
                for message in _LangChain:
                    role = message.get('role', 'unknown')
                    content = message.get('content', '[NO CONTENT]')
                    markdown_version += f"\n\n\n## Role: {role}\n"
                    markdown_version += f"```\n{str(content).replace('```', '')}\n```"
                f.write(markdown_version)
        except Exception as e:
            self.Log(f"Failed to write Langchain Markdown log for {langchain_debug_title}. Error: {e}", 7)
            
        self.Log(f"Wrote LangChain debug logs for {langchain_debug_title}", 1)


    def SaveStory(self, _StoryContent: str):
        """Saves the given story to disk."""
        story_path = os.path.join(self.LogDirPrefix, "Story.md")
        try:
            with open(story_path, "w", encoding='utf-8') as f:
                f.write(_StoryContent)
            self.Log(f"Wrote final story to disk at {story_path}", 5)
        except Exception as e:
            self.Log(f"Failed to write final story to disk. Error: {e}", 7)


    def Log(self, _Item, _Level: int = 1):
        """Logs an item to the console and the log file with appropriate color-coding."""
        # Create Log Entry
        log_entry = f"[{str(_Level).ljust(2)}] [{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}] {_Item}"

        # Write it to file
        self.File.write(log_entry + "\n")
        self.File.flush() # Ensure logs are written immediately

        # Now color and print it to the console
        color_map = {
            0: "white",   # Verbose debug
            1: "grey",    # Info
            2: "blue",    # Process start/end
            3: "cyan",    # Sub-process info
            4: "magenta", # Important info
            5: "green",   # Success/completion
            6: "yellow",  # Warning
            7: "red",     # Error/Critical
        }
        color = color_map.get(_Level, "white")
        
        try:
            print(termcolor.colored(log_entry, color))
        except Exception:
            # Fallback for environments that don't support color
            print(log_entry)


    def __del__(self):
        if self.File and not self.File.closed:
            self.File.close()
