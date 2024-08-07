"""
Module for managing character information within a writing project.
"""

import json
import os

import streamlit as st

from src.llm import call_g4f_api


def character_management():
    """
    Provides an interface for managing characters in a writing project.
    Allows users to generate, add, edit, delete, and save character information.
    """

    st.header("Character Management")

    # Get the current working directory as the project path
    project_path = os.getcwd()
    config_file = os.path.join(project_path, "config", "config.json")
    characters_dir = os.path.join(project_path, "characters")

    # Load project configuration and existing character data
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config_data = json.load(f)
        character_data = {}
        for filename in os.listdir(characters_dir):
            if filename.endswith(".json"):
                character_file = os.path.join(characters_dir, filename)
                with open(character_file, "r", encoding="utf-8") as f:
                    character_data[filename[:-5]] = json.load(f)
    except FileNotFoundError:
        st.error("Project configuration file not found. Please create a new project.")
        return

    # Display the loaded project configuration settings
    st.write("Project configuration:")
    st.write(f"Genre: {config_data['genre']}")
    st.write(f"Tone: {config_data['tone']}")
    st.write(f"Point of View: {config_data['point_of_view']}")
    st.write(f"Writing Style: {config_data['writing_style']}")
    st.write(f"Premise: {config_data['premise']}")

    # Provide options for character management
    choice = st.selectbox(
        "Select an option",
        [
            "Generate Characters",
            "Add Character",
            "Edit Character",
            "Delete Character",
            "Save Characters",  # This seems redundant given autosave on other options
        ],
    )

    # Generate characters based on project configuration
    if choice == "Generate Characters":
        # Get user-defined configuration settings
        genre = config_data["genre"]
        tone = config_data["tone"]
        point_of_view = config_data["point_of_view"]
        writing_style = config_data["writing_style"]
        premise = config_data["premise"]
        synopsis_file = os.path.join(project_path, "synopsis", "synopsis.txt")

        try:
            with open(synopsis_file, "r", encoding="utf-8") as f:
                synopsis_text = f.read()
        except FileNotFoundError:
            synopsis_text = "No synopsis found."

        # Generate characters using the language model (LLM)
        prompt = (
            f"Generate characters for a story with the following characteristics:\n"
            f"Genre: {genre}\n"
            f"Tone: {tone}\n"
            f"Point of View: {point_of_view}\n"
            f"Writing Style: {writing_style}\n"
            f"Premise: {premise}\n"
            f"Synopsis: {synopsis_text}"
        )
        response = call_g4f_api(prompt)

        # Display generated characters
        st.write("Generated Characters:")
        st.write(response)

        # Save generated characters to individual JSON files
        characters = response.split("\n\n")
        for character in characters:
            character_name = character.split("\n")[0].strip()
            character_details = character.split("\n")[1:]
            character_data[character_name] = {
                "name": character_name,
                "description": "\n".join(character_details),
            }
            character_file = os.path.join(characters_dir, f"{character_name}.json")
            with open(character_file, "w", encoding="utf-8") as f:
                json.dump(character_data[character_name], f)
        st.success("Characters saved to files.")

    # Add a new character manually
    elif choice == "Add Character":
        character_name = st.text_input("Enter Character Name:")
        character_description = st.text_area("Enter Character Description:")

        # Save the new character to a JSON file
        if character_name:
            character_data[character_name] = {
                "name": character_name,
                "description": character_description,
            }
            character_file = os.path.join(characters_dir, f"{character_name}.json")
            with open(character_file, "w", encoding="utf-8") as f:
                json.dump(character_data[character_name], f)
            st.success(f"Character '{character_name}' added.")

    # Edit an existing character's information
    elif choice == "Edit Character":
        selected_character = st.selectbox(
            "Select Character:", list(character_data.keys())
        )
        if selected_character:
            character_name = selected_character
            current_description = character_data[character_name]["description"]
            modified_description = st.text_area(
                "Edit Character Description:", current_description
            )

            # Update and save the modified character information
            character_data[character_name]["description"] = modified_description
            character_file = os.path.join(characters_dir, f"{character_name}.json")
            with open(character_file, "w", encoding="utf-8") as f:
                json.dump(character_data[character_name], f)
            st.success(f"Character '{character_name}' updated.")

    # Delete an existing character
    elif choice == "Delete Character":
        selected_character = st.selectbox(
            "Select Character to Delete:", list(character_data.keys())
        )
        if selected_character:
            character_name = selected_character
            confirm_delete = st.button(f"Delete {character_name}?")
            if confirm_delete:
                character_file = os.path.join(characters_dir, f"{character_name}.json")
                os.remove(character_file)
                del character_data[character_name]
                st.success(f"Character '{character_name}' deleted.")

    # Redundant save option (consider removing as changes are saved immediately)
    elif choice == "Save Characters":
        st.write("Characters Saved.")
