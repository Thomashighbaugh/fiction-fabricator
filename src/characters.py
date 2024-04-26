import json

from src.llmconnection import call_g4f_api
from src.prompts import get_character_prompt


def generate_characters(updated_synopsis, genre, tone, style, pov, premise):
    """
    Generates and manages characters for the novel with an interactive list,
    including character details, traits, and relationships.
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
                "relationships": {},  # Initialize empty dictionary for relationships
            }

    while True:
        print("\nCharacters:")
        for i, name in enumerate(characters_dict.keys()):
            print(f"{i+1}. {name}")

        choice = input("\nChoose action (add, edit, relationships, delete, done): ")

        if choice.lower() == 'done':
            break

        elif choice.lower() == 'add':
            new_name = input("Enter new character name: ")
            new_details = input("Enter details for new character: ")
            characters_dict[new_name] = {"details": new_details, "traits": [], "relationships": {}}

        elif choice.lower() == 'edit':
            try:
                edit_index = int(input("Enter number of character to edit: ")) - 1
                name_to_edit = list(characters_dict.keys())[edit_index]
                new_details = input(f"Enter new details for {name_to_edit}: ")
                characters_dict[name_to_edit]["details"] = new_details
            except (ValueError, IndexError):
                print("Invalid character number. Please try again.")

        elif choice.lower() == 'relationships':
            while True:
                character1 = input("Enter first character's name (or 'back'): ")
                if character1.lower() == 'back':
                    break
                if character1 not in characters_dict:
                    print("Character not found. Please try again.")
                    continue

                character2 = input("Enter second character's name: ")
                if character2 not in characters_dict:
                    print("Character not found. Please try again.")
                    continue

                relationship = input(f"Describe relationship between {character1} and {character2}: ")
                characters_dict[character1]["relationships"][character2] = relationship
                characters_dict[character2]["relationships"][character1] = relationship

        elif choice.lower() == 'delete':
            try:
                delete_index = int(input("Enter number of character to delete: ")) - 1
                name_to_delete = list(characters_dict.keys())[delete_index]
                del characters_dict[name_to_delete]
            except (ValueError, IndexError):
                print("Invalid character number. Please try again.")

        else:
            print("Invalid choice. Please try again.")

    return json.dumps(characters_dict, indent=4)
