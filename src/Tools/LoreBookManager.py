#!/usr/bin/python3
import os
import json
import termcolor
from Writer.PrintUtils import Logger
import Writer.Interface.Wrapper
import Writer.Prompts
from Writer.LLMUtils import get_llm_selection_menu_for_tool

class LoreBookManager:
    def __init__(self, interface: Writer.Interface.Wrapper.Interface, logger: Logger):
        self.interface = interface
        self.logger = logger
        self.lorebooks_dir = "Generated_Content/LoreBooks"
        os.makedirs(self.lorebooks_dir, exist_ok=True)

    def main_menu(self):
        while True:
            self.logger.Log("\n--- Lorebook Manager ---", 5)
            print("1. Create a new lorebook")
            print("2. Add an entry to an existing lorebook")
            print("3. Edit an entry in an existing lorebook")
            print("4. Remove an entry from an existing lorebook")
            print("5. Delete a lorebook")
            print("6. Generate a new lorebook from a prompt")
            print("7. Back to main menu")
            choice = input("Enter your choice: ").strip()

            if choice == '1':
                self.create_lorebook()
            elif choice == '2':
                self.add_entry()
            elif choice == '3':
                self.edit_entry()
            elif choice == '4':
                self.remove_entry()
            elif choice == '5':
                self.delete_lorebook()
            elif choice == '6':
                self.generate_lorebook_from_prompt()
            elif choice == '7':
                break
            else:
                self.logger.Log("Invalid choice. Please try again.", 6)

    def create_lorebook(self):
        lorebook_name = input("Enter the name for the new lorebook: ").strip()
        if not lorebook_name:
            self.logger.Log("Lorebook name cannot be empty.", 6)
            return
        
        file_path = os.path.join(self.lorebooks_dir, f"{lorebook_name}.json")
        if os.path.exists(file_path):
            self.logger.Log(f"Lorebook '{lorebook_name}' already exists.", 6)
            return

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=4)
        self.logger.Log(f"Successfully created lorebook '{lorebook_name}'.", 5)

    def select_lorebook(self):
        lorebooks = [f for f in os.listdir(self.lorebooks_dir) if f.endswith('.json')]
        if not lorebooks:
            self.logger.Log("No lorebooks found.", 6)
            return None

        self.logger.Log("Available lorebooks:", 5)
        for i, name in enumerate(lorebooks):
            print(f"{i + 1}. {name}")

        while True:
            choice = input("Select a lorebook by number: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(lorebooks):
                return os.path.abspath(os.path.join(self.lorebooks_dir, lorebooks[int(choice) - 1]))
            self.logger.Log("Invalid selection.", 6)

    def _select_and_load_lorebook(self):
        lorebook_file_path = self.select_lorebook()
        if not lorebook_file_path:
            return None, None

        try:
            with open(lorebook_file_path, 'r', encoding='utf-8') as f:
                entries = json.load(f)
            return lorebook_file_path, entries
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.Log(f"Error loading lorebook: {e}", 7)
            return None, None

    def add_entry(self):
        lorebook_file_path, entries = self._select_and_load_lorebook()
        if not lorebook_file_path:
            return

        entry_name = input("Enter the name for the new entry: ").strip()
        if not entry_name:
            self.logger.Log("Entry name cannot be empty.", 6)
            return

        print("How would you like to create the entry content?")
        print("1. Manual Entry")
        print("2. Generate with LLM")
        choice = input("Enter your choice: ").strip()

        new_entry_content = ""
        if choice == '1':
            new_entry_content = input("Enter the content for your lorebook entry:\n")
            enhance = input("Would you like to enhance this entry with an LLM? (y/n): ").strip().lower()
            if enhance == 'y':
                model = get_llm_selection_menu_for_tool(self.logger, "Lorebook Enhancement")
                if not model:
                    self.logger.Log("Model selection cancelled. Saving manual entry.", 4)
                else:
                    messages = [
                        self.interface.BuildSystemQuery(Writer.Prompts.LOREBOOK_ENTRY_ENHANCEMENT),
                        self.interface.BuildUserQuery(new_entry_content)
                    ]
                    _, enhanced_json = self.interface.SafeGenerateJSON(self.logger, messages, model, _RequiredAttribs=["content"])
                    new_entry_content = enhanced_json.get("content", new_entry_content)
        
        elif choice == '2':
            entry_content_prompt = input("Enter a prompt to generate the content for this entry: ").strip()
            model = get_llm_selection_menu_for_tool(self.logger, "Lorebook Generation")
            if not model:
                self.logger.Log("Model selection cancelled.", 6)
                return

            messages = [
                self.interface.BuildSystemQuery(Writer.Prompts.LOREBOOK_ENTRY_GENERATION),
                self.interface.BuildUserQuery(f"Generate a lorebook entry for '{entry_name}' based on the following prompt: {entry_content_prompt}")
            ]
            
            _, generated_json = self.interface.SafeGenerateJSON(self.logger, messages, model, _RequiredAttribs=["content"])
            new_entry_content = generated_json.get("content", "No content generated.")
        
        else:
            self.logger.Log("Invalid choice.", 6)
            return

        new_entry = {
            "name": entry_name,
            "content": new_entry_content
        }
        entries.append(new_entry)

        with open(lorebook_file_path, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=4)
        self.logger.Log(f"Successfully added entry '{entry_name}' to '{os.path.basename(lorebook_file_path)}'.", 5)

    def edit_entry(self):
        lorebook_file_path, entries = self._select_and_load_lorebook()
        if not lorebook_file_path:
            return

        if not entries:
            self.logger.Log("This lorebook has no entries to edit.", 6)
            return

        self.logger.Log("Select an entry to edit:", 5)
        for i, entry in enumerate(entries):
            print(f"{i + 1}. {entry['name']}")

        choice = input("Enter your choice: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(entries):
            entry_index = int(choice) - 1
            selected_entry = entries[entry_index]
            
            self.logger.Log(f"Current content for '{selected_entry['name']}':", 3)
            print(selected_entry['content'])
            
            model = get_llm_selection_menu_for_tool(self.logger, "Lorebook Editing")
            if not model:
                self.logger.Log("Model selection cancelled.", 6)
                return

            edit_prompt = input("Enter a prompt to edit this entry: ").strip()

            if edit_prompt:
                messages = [
                    self.interface.BuildSystemQuery(Writer.Prompts.LOREBOOK_ENTRY_EDITING),
                    self.interface.BuildUserQuery(f"Edit the following lorebook entry for '{selected_entry['name']}' based on the prompt: '{edit_prompt}'.\n\nOriginal Content:\n{selected_entry['content']}")
                ]
                _, edited_json = self.interface.SafeGenerateJSON(self.logger, messages, model, _RequiredAttribs=["content"])
                entries[entry_index]['content'] = edited_json.get("content", selected_entry['content'])
            else:
                self.logger.Log("Edit prompt cannot be empty.", 6)

            with open(lorebook_file_path, 'w', encoding='utf-8') as f:
                json.dump(entries, f, indent=4)
            self.logger.Log(f"Successfully updated entry '{selected_entry['name']}'.", 5)
        else:
            self.logger.Log("Invalid selection.", 6)

    def remove_entry(self):
        lorebook_file_path, entries = self._select_and_load_lorebook()
        if not lorebook_file_path:
            return

        if not entries:
            self.logger.Log("This lorebook has no entries to remove.", 6)
            return

        self.logger.Log("Select an entry to remove:", 5)
        for i, entry in enumerate(entries):
            print(f"{i + 1}. {entry['name']}")

        choice = input("Enter your choice: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(entries):
            entry_index = int(choice) - 1
            removed_entry = entries.pop(entry_index)
            
            with open(lorebook_file_path, 'w', encoding='utf-8') as f:
                json.dump(entries, f, indent=4)
            self.logger.Log(f"Successfully removed entry '{removed_entry['name']}'.", 5)
        else:
            self.logger.Log("Invalid selection.", 6)

    def delete_lorebook(self):
        lorebook_file_path = self.select_lorebook()
        if not lorebook_file_path:
            return

        confirm = input(f"Are you sure you want to delete '{os.path.basename(lorebook_file_path)}'? (y/n): ").strip().lower()
        if confirm == 'y':
            os.remove(lorebook_file_path)
            self.logger.Log(f"Successfully deleted lorebook '{os.path.basename(lorebook_file_path)}'.", 5)

    def generate_lorebook_from_prompt(self, prompt: str = None):
        if not prompt:
            prompt = input("Enter a prompt to generate a new lorebook from scratch: ").strip()
        
        if not prompt:
            self.logger.Log("Prompt cannot be empty.", 6)
            return None
        
        model = get_llm_selection_menu_for_tool(self.logger, "Lorebook Generation")
        if not model:
            self.logger.Log("Model selection cancelled.", 6)
            return None

        messages = [
            self.interface.BuildSystemQuery(Writer.Prompts.LOREBOOK_GENERATION),
            self.interface.BuildUserQuery(prompt)
        ]

        _, lorebook_data = self.interface.SafeGenerateJSON(self.logger, messages, model, _RequiredAttribs=["lorebook_name", "entries"])
        
        if not lorebook_data:
            self.logger.Log("Failed to get valid JSON for the lorebook.", 7)
            return None

        try:
            lorebook_name = lorebook_data.get("lorebook_name", "Generated Lorebook")
            entries = lorebook_data.get("entries", [])

            safe_name = "".join(c for c in lorebook_name if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')
            file_path = os.path.join(self.lorebooks_dir, f"{safe_name}.json")

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(entries, f, indent=4)
            
            self.logger.Log(f"Successfully generated and saved new lorebook '{file_path}'.", 5)
            return file_path
        except Exception as e:
            self.logger.Log(f"Failed to decode or save the lorebook: {e}", 7)
            return None
