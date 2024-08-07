# fiction-fabricator/src/character.py

"""
Module for managing character information within a writing project.
"""

import json
import os

import streamlit as st

from src.llm import call_g4f_api
from src.prompts import generate_characters_prompt


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

    # Character input - autosaved
    character_name = st.text_input("Character Name:")
    character_description = st.text_area("Character Description:")
    if character_name and character_description:
        character_data[character_name] = {
            "name": character_name,
            "description": character_description,
        }
        character_file = os.path.join(characters_dir, f"{character_name}.json")
        with open(character_file, "w", encoding="utf-8") as f:
            json.dump(character_data[character_name], f)
        st.success(f"Character '{character_name}' saved.")

    # Generate characters button
    if st.button("Generate Characters"):
        # Get user-defined configuration settings
        genre = config_data.get("genre", "")
        tone = config_data.get("tone", "")
        point_of_view = config_data.get("point_of_view", "")
        writing_style = config_data.get("writing_style", "")
        premise = config_data.get("premise", "")
        synopsis_file = os.path.join(project_path, "synopsis", "synopsis.txt")

        try:
            with open(synopsis_file, "r", encoding="utf-8") as f:
                synopsis_text = f.read()
        except FileNotFoundError:
            synopsis_text = ""  # Use an empty string if synopsis is not found

        # Generate characters using the language model (LLM)
        prompt = generate_characters_prompt(
            genre, tone, point_of_view, writing_style, premise, synopsis_text
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

    # Display existing characters
    st.subheader("Existing Characters:")
    for character_name, character_info in character_data.items():
        st.write(f"**{character_name}**")
        st.write(character_info["description"])

        # Edit character button
        if st.button(f"Edit {character_name}"):
            # Load the character's current description
            current_description = character_info["description"]

            # Display a text area for editing
            modified_description = st.text_area(
                f"Edit Character Description for {character_name}:",
                current_description,
                key=f"edit_{character_name}",
            )

            # Update and save the modified character information
            if modified_description != current_description:
                character_data[character_name]["description"] = modified_description
                character_file = os.path.join(characters_dir, f"{character_name}.json")
                with open(character_file, "w", encoding="utf-8") as f:
                    json.dump(character_data[character_name], f)
                st.success(f"Character '{character_name}' updated.")

        # Delete character button
        if st.button(f"Delete {character_name}"):
            confirm_delete = st.checkbox(f"Confirm deletion of {character_name}")
            if confirm_delete:
                character_file = os.path.join(characters_dir, f"{character_name}.json")
                os.remove(character_file)
                del character_data[character_name]
                st.success(f"Character '{character_name}' deleted.")

        st.write("---")
