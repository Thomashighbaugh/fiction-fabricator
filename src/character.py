import streamlit as st
import os
import json
from llm import call_g4f_api

def character_management():
    st.header("Character Management")

    # Get project path
    project_path = os.getcwd()
    config_file = os.path.join(project_path, "config", "config.json")
    characters_dir = os.path.join(project_path, "characters")

    # Load configuration and character data
    try:
        with open(config_file, "r") as f:
            config_data = json.load(f)
        character_data = {}
        for filename in os.listdir(characters_dir):
            if filename.endswith(".json"):
                character_file = os.path.join(characters_dir, filename)
                with open(character_file, "r") as f:
                    character_data[filename[:-5]] = json.load(f)
    except FileNotFoundError:
        st.error("Project configuration file not found. Please create a new project.")
        return

    # Display configuration settings
    st.write("Project configuration:")
    st.write(f"Genre: {config_data['genre']}")
    st.write(f"Tone: {config_data['tone']}")
    st.write(f"Point of View: {config_data['point_of_view']}")
    st.write(f"Writing Style: {config_data['writing_style']}")
    st.write(f"Premise: {config_data['premise']}")

    # Options for character management
    choice = st.selectbox("Select an option", ["Generate Characters", "Add Character", "Edit Character", "Delete Character", "Save Characters"])

    # Generate characters
    if choice == "Generate Characters":
        # Get user-defined configuration settings
        genre = config_data["genre"]
        tone = config_data["tone"]
        point_of_view = config_data["point_of_view"]
        writing_style = config_data["writing_style"]
        premise = config_data["premise"]
        synopsis_file = os.path.join(project_path, "synopsis", "synopsis.txt")
        try:
            with open(synopsis_file, "r") as f:
                synopsis_text = f.read()
        except FileNotFoundError:
            synopsis_text = "No synopsis found."

        # Use call_g4f_api to generate characters based on user settings
        prompt = f"Generate characters for a story with the following characteristics:\nGenre: {genre}\nTone: {tone}\nPoint of View: {point_of_view}\nWriting Style: {writing_style}\nPremise: {premise}\nSynopsis: {synopsis_text}"
        response = call_g4f_api(prompt)

        # Display generated characters
        st.write("Generated Characters:")
        st.write(response)

        # Save generated characters to files
        characters = response.split("\n\n")
        for i, character in enumerate(characters):
            character_name = character.split("\n")[0].strip()
            character_details = character.split("\n")[1:]
            character_data[character_name] = {"name": character_name, "description": "\n".join(character_details)}
            character_file = os.path.join(characters_dir, f"{character_name}.json")
            with open(character_file, "w") as f:
                json.dump(character_data[character_name], f)
        st.success("Characters saved to files.")

    # Add character
    elif choice == "Add Character":
        character_name = st.text_input("Enter Character Name:")
        character_description = st.text_area("Enter Character Description:")

        # Save new character to file
        if character_name:
            character_data[character_name] = {"name": character_name, "description": character_description}
            character_file = os.path.join(characters_dir, f"{character_name}.json")
            with open(character_file, "w") as f:
                json.dump(character_data[character_name], f)
            st.success(f"Character '{character_name}' added.")

    # Edit character
    elif choice == "Edit Character":
        selected_character = st.selectbox("Select Character:", list(character_data.keys()))
        if selected_character:
            character_name = selected_character
            current_description = character_data[character_name]["description"]
            modified_description = st.text_area("Edit Character Description:", current_description)

            # Save edited character
            character_data[character_name]["description"] = modified_description
            character_file = os.path.join(characters_dir, f"{character_name}.json")
            with open(character_file, "w") as f:
                json.dump(character_data[character_name], f)
            st.success(f"Character '{character_name}' updated.")

    # Delete character
    elif choice == "Delete Character":
        selected_character = st.selectbox("Select Character to Delete:", list(character_data.keys()))
        if selected_character:
            character_name = selected_character
            confirm_delete = st.button(f"Delete {character_name}?")
            if confirm_delete:
                character_file = os.path.join(characters_dir, f"{character_name}.json")
                os.remove(character_file)
                del character_data[character_name]
                st.success(f"Character '{character_name}' deleted.")

    # Save characters
    elif choice == "Save Characters":
        st.write("Characters Saved.")