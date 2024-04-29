import json

from src.llmconnection import call_g4f_api
from src.prompts import get_character_prompt


def generate_characters(updated_synopsis, genre, tone, style, pov, premise):
    """
    Generates and manages characters for the novel with an interactive list,
    including character details and traits.
    """

    prompt = get_character_prompt(updated_synopsis, genre, tone, style, pov, premise)
    response = call_g4f_api(prompt)
    characters_text = response

    # Assuming the API returns characters in a list format with "-" as delimiter
    characters_list = [
        line.strip() for line in characters_text.split("\n") if line.strip()  # Remove empty lines
    ]

    # Extract character names and details
    characters_dict = {}
    for character in characters_list:
        if " - " in character:  # Check for the delimiter
            name, details = character.split(" - ", 1)
            characters_dict[name.strip()] = {
                "details": details.strip(),
                "traits": [],  # Initialize empty list for traits
            }

    return characters_dict

def manage_characters(characters_dict, updated_synopsis, genre, tone, style, pov, premise):
    """
    Provides an interactive menu for adding, editing, and deleting characters.
    """

    while True:
        print("\nCharacters:")
        for i, name in enumerate(characters_dict.keys()):
            print(f"{i+1}. {name}")

        choice = input("\nChoose action (add, edit, delete, generate, done): ")

        if choice.lower() == 'done':
            break

        elif choice.lower() == 'add':
            new_name = input("Enter new character name: ")
            new_details = input("Enter details for new character: ")
            characters_dict[new_name] = {"details": new_details, "traits": []}

        elif choice.lower() == 'edit':
            try:
                edit_index = int(input("Enter number of character to edit: ")) - 1
                name_to_edit = list(characters_dict.keys())[edit_index]
                new_details = input(f"Enter new details for {name_to_edit}: ")
                characters_dict[name_to_edit]["details"] = new_details
            except (ValueError, IndexError):
                print("Invalid character number. Please try again.")

        elif choice.lower() == 'delete':
            try:
                delete_index = int(input("Enter number of character to delete: ")) - 1
                name_to_delete = list(characters_dict.keys())[delete_index]
                del characters_dict[name_to_delete]
            except (ValueError, IndexError):
                print("Invalid character number. Please try again.")

        elif choice.lower() == 'generate':
            characters_dict.update(generate_characters(updated_synopsis, genre, tone, style, pov, premise))

        else:
            print("Invalid choice. Please try again.")

    return json.dumps(characters_dict, indent=4)
