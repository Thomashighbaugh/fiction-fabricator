# fiction-fabricator/src/world.py

"""
This module focuses on managing world-building aspects 
and individual setting details within the writing project.
Provides functions to generate, edit, delete, and save world-related information.
"""

import json
import os

import streamlit as st

from src.llm import call_g4f_api
from src.prompts import generate_world_settings_prompt


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

    # User input for world info - autosaved
    world_info = st.text_area("World Information:", world_data.get("world_info", ""))
    if world_info:
        world_data["world_info"] = world_info
        with open(world_file, "w", encoding="utf-8") as f:
            json.dump(world_data, f)

    # User input for setting name and description - autosaved
    setting_name = st.text_input("Setting Name:")
    setting_description = st.text_area("Setting Description:")
    if setting_name and setting_description:
        settings_data[setting_name] = {
            "name": setting_name,
            "description": setting_description,
        }
        setting_file = os.path.join(settings_dir, f"{setting_name}.json")
        with open(setting_file, "w", encoding="utf-8") as f:
            json.dump(settings_data[setting_name], f)
        st.success(f"Setting '{setting_name}' saved.")

    # Generate World & Settings button
    if st.button("Generate World & Settings"):
        # Gather data from configuration and synopsis
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

        # Craft the prompt for world generation
        prompt = generate_world_settings_prompt(
            genre, tone, point_of_view, writing_style, premise, synopsis_text
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

    # Display existing settings
    st.subheader("Existing Settings:")
    for setting_name, setting_info in settings_data.items():
        st.write(f"**{setting_name}**")
        st.write(setting_info["description"])

        # Edit setting button
        if st.button(f"Edit {setting_name}"):
            # Load the setting's current description
            current_description = setting_info["description"]

            # Display a text area for editing
            modified_description = st.text_area(
                f"Edit Setting Description for {setting_name}:",
                current_description,
                key=f"edit_{setting_name}",
            )

            # Update and save the modified setting information
            if modified_description != current_description:
                settings_data[setting_name]["description"] = modified_description
                setting_file = os.path.join(settings_dir, f"{setting_name}.json")
                with open(setting_file, "w", encoding="utf-8") as f:
                    json.dump(settings_data[setting_name], f)
                st.success(f"Setting '{setting_name}' updated.")

        # Delete setting button
        if st.button(f"Delete {setting_name}"):
            confirm_delete = st.checkbox(f"Confirm deletion of {setting_name}")
            if confirm_delete:
                setting_file = os.path.join(settings_dir, f"{setting_name}.json")
                os.remove(setting_file)
                del settings_data[setting_name]
                st.success(f"Setting '{setting_name}' deleted.")

        st.write("---")
