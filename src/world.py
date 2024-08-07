"""
This module focuses on managing world-building aspects 
and individual setting details within the writing project.
Provides functions to generate, edit, delete, and save world-related information.
"""

import json
import os

import streamlit as st

from src.llm import call_g4f_api


def world_management():
    """
    Provides a user interface for world-building within a writing project.
    This includes generating descriptions of the world, adding specific settings,
    editing existing ones, deleting settings, and saving all changes.
    """

    st.header("World & Settings Management")

    # Define the project paths and load project data
    project_path = os.getcwd()
    config_file = os.path.join(project_path, "config", "config.json")
    world_file = os.path.join(project_path, "world", "world.json")
    settings_dir = os.path.join(project_path, "world", "settings")

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config_data = json.load(f)

        # Load world information or initialize if it doesn't exist
        try:
            with open(world_file, "r", encoding="utf-8") as f:
                world_data = json.load(f)
        except FileNotFoundError:
            world_data = {}

        # Load existing settings
        settings_data = {}
        for filename in os.listdir(settings_dir):
            if filename.endswith(".json"):
                setting_file = os.path.join(settings_dir, filename)
                with open(setting_file, "r", encoding="utf-8") as f:
                    settings_data[filename[:-5]] = json.load(f)

    except FileNotFoundError:
        st.error("Project configuration file not found. Please create a new project.")
        return

    # Display the current project configuration
    st.write("Project configuration:")
    st.write(f"Genre: {config_data['genre']}")
    st.write(f"Tone: {config_data['tone']}")
    st.write(f"Point of View: {config_data['point_of_view']}")
    st.write(f"Writing Style: {config_data['writing_style']}")
    st.write(f"Premise: {config_data['premise']}")

    # User choices for world & settings management
    choice = st.selectbox(
        "Select an option",
        [
            "Generate World & Settings",
            "Add Setting",
            "Edit Setting",
            "Delete Setting",
            "Edit World Information",
            "Save Settings & World Information",  # Consider making saving automatic
        ],
    )

    # Generates the world and its settings using the language model (LLM)
    if choice == "Generate World & Settings":
        # Gather data from configuration and synopsis
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

        # Craft the prompt for world generation
        prompt = (
            f"Generate the world and settings for a story with the following characteristics:\n"
            f"Genre: {genre}\n"
            f"Tone: {tone}\n"
            f"Point of View: {point_of_view}\n"
            f"Writing Style: {writing_style}\n"
            f"Premise: {premise}\n"
            f"Synopsis: {synopsis_text}"
        )
        response = call_g4f_api(prompt)

        st.write("Generated World & Settings:")
        st.write(response)

        # Process the generated response
        world_sections = response.split("\n\n")
        for section in world_sections:
            section_header = section.split("\n")[0].strip()

            # Extract world information if found
            if "World Information" in section_header:
                world_details = section.split("\n")[1:]
                world_data["world_info"] = "\n".join(world_details)
                with open(world_file, "w", encoding="utf-8") as f:
                    json.dump(world_data, f)

            # Extract settings details
            elif "Settings" in section_header:
                settings = section.split("\n")[1:]
                for setting in settings:
                    setting_name = setting.split("\n")[0].strip()
                    setting_details = setting.split("\n")[1:]
                    settings_data[setting_name] = {
                        "name": setting_name,
                        "description": "\n".join(setting_details),
                    }
                    setting_file = os.path.join(settings_dir, f"{setting_name}.json")
                    with open(setting_file, "w", encoding="utf-8") as f:
                        json.dump(settings_data[setting_name], f)
        st.success("World and settings saved to files.")

    # Adds a new setting
    elif choice == "Add Setting":
        setting_name = st.text_input("Enter Setting Name:")
        setting_description = st.text_area("Enter Setting Description:")

        if setting_name:
            settings_data[setting_name] = {
                "name": setting_name,
                "description": setting_description,
            }
            setting_file = os.path.join(settings_dir, f"{setting_name}.json")
            with open(setting_file, "w", encoding="utf-8") as f:
                json.dump(settings_data[setting_name], f)
            st.success(f"Setting '{setting_name}' added.")

    # Allows for editing of existing settings
    elif choice == "Edit Setting":
        selected_setting = st.selectbox("Select Setting:", list(settings_data.keys()))
        if selected_setting:
            setting_name = selected_setting
            current_description = settings_data[setting_name]["description"]
            modified_description = st.text_area(
                "Edit Setting Description:", current_description
            )
            settings_data[setting_name]["description"] = modified_description
            setting_file = os.path.join(settings_dir, f"{setting_name}.json")
            with open(setting_file, "w", encoding="utf-8") as f:
                json.dump(settings_data[setting_name], f)
            st.success(f"Setting '{setting_name}' updated.")

    # Delete a specific setting
    elif choice == "Delete Setting":
        selected_setting = st.selectbox(
            "Select Setting to Delete:", list(settings_data.keys())
        )
        if selected_setting:
            setting_name = selected_setting
            confirm_delete = st.button(f"Delete {setting_name}?")
            if confirm_delete:
                setting_file = os.path.join(settings_dir, f"{setting_name}.json")
                os.remove(setting_file)
                del settings_data[setting_name]
                st.success(f"Setting '{setting_name}' deleted.")

    # Modify general world information
    elif choice == "Edit World Information":
        try:
            current_world_info = world_data["world_info"]
            modified_world_info = st.text_area(
                "Edit World Information:", current_world_info
            )
            world_data["world_info"] = modified_world_info
            with open(world_file, "w", encoding="utf-8") as f:
                json.dump(world_data, f)
            st.success("World information updated.")
        except KeyError:
            st.info("No world information found. Please generate world details first.")

    # Consider making saving automatic on any modifications
    elif choice == "Save Settings & World Information":
        st.write("Settings & World Information Saved.")

