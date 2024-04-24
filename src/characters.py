import json

from src.openaiconnection import call_g4f_api
from src.prompts import get_character_prompt


def generate_characters(updated_synopsis, genre, tone, style, pov, premise):
    """
    Generates a list of characters for the novel based on the provided information.
    """

    prompt = get_character_prompt(updated_synopsis, genre, tone, style, pov, premise)
    response = call_g4f_api(prompt)
    characters_text = response

    # Assuming the API returns characters in a list format
    characters = characters_text.split("\n")

    # Convert the list of characters into a dictionary with details and traits
    characters_dict = {}
    for character in characters:
        name, *details = character.split(" - ")
        characters_dict[name] = {
            "details": " ".join(details),
            "traits": [],  # Initialize empty list for traits
            "relationships": {},  # Initialize empty dictionary for relationships
        }

    # Character Trait Selection
    for character_name, character_data in characters_dict.items():
        print(f"\nCharacter: {character_name}")
        while True:
            add_trait = input("Enter a trait to add (or 'done' to finish): ")
            if add_trait.lower() == "done":
                break
            character_data["traits"].append(add_trait)

    # Character Relationship Editor (Interactive Text-Based)
    print("\nCharacter Relationship Editor:")
    while True:
        character1 = input("Enter the first character's name (or 'done' to finish): ")
        if character1.lower() == "done":
            break  # Exit the loop if 'done' is entered
        if character1 not in characters_dict:
            print("Character not found. Please try again.")
            continue

        character2 = input("Enter the second character's name: ")
        if character2 not in characters_dict:
            print("Character not found. Please try again.")
            continue

        relationship = input(f"Describe the relationship between {character1} and {character2}: ")
        characters_dict[character1]["relationships"][character2] = relationship
        characters_dict[character2]["relationships"][character1] = relationship

    return json.dumps(characters_dict, indent=4)
