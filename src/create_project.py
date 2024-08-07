import streamlit as st
import os
import json
from system_prompt import system_prompt_management
from prompts import (
    generate_synopsis_prompt,
    generate_characters_prompt,
    generate_world_settings_prompt,
    generate_title_prompt,
    generate_outline_prompt,
    generate_scenes_summary_prompt,
    generate_chapter_prompt,
    critique_improve_prompt,
)
from llm import call_g4f_api


def create_new_project():
    st.header("Create New Project")

    # Get project name from user
    project_name = st.text_input("Enter Project Name:")

    # Create project directory if it doesn't exist
    if project_name:
        project_path = os.path.join(os.getcwd(), project_name)
        if not os.path.exists(project_path):
            os.mkdir(project_path)
            st.success(f"Project '{project_name}' created successfully!")
        else:
            st.error(f"Project '{project_name}' already exists.")

    # Create subdirectories for project files
    os.mkdir(os.path.join(project_path, "config"))
    os.mkdir(os.path.join(project_path, "synopsis"))
    os.mkdir(os.path.join(project_path, "characters"))
    os.mkdir(os.path.join(project_path, "world"))
    os.mkdir(os.path.join(project_path, "title"))
    os.mkdir(os.path.join(project_path, "outline"))
    os.mkdir(os.path.join(project_path, "chapters"))

    # Initialize configuration file (config.json)
    config_file = os.path.join(project_path, "config", "config.json")
    with open(config_file, "w") as f:
        f.write("{}")
        st.success("Project configuration initialized.")

    # Display initial project information
    st.write(f"Project directory: {project_path}")

    # Prompt user to enter initial configuration settings
    genre = st.text_input("Genre:")
    tone = st.text_input("Tone:")
    point_of_view = st.text_input("Point of View:")
    writing_style = st.text_input("Writing Style:")
    premise = st.text_area("Premise/General Idea:")

    # Save configuration settings to config.json
    config_data = {
        "genre": genre,
        "tone": tone,
        "point_of_view": point_of_view,
        "writing_style": writing_style,
        "premise": premise,
    }
    # Modify the System Prompt
    system_prompt_management()

    with open(config_file, "w") as f:
        json.dump(config_data, f)
        st.success("Configuration settings saved.")
