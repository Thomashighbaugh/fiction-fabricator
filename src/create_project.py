"""
Module for creating new writing projects.
Handles project setup, directory creation,
and initialization of project configuration files.
"""
import json
import os

import streamlit as st

from src.system_prompt import system_prompt_management

# Consider removing these unused imports for better readability:
# from src.prompts import (generate_synopsis_prompt, generate_characters_prompt, 
#    generate_world_settings_prompt, generate_title_prompt, generate_outline_prompt, 
#    generate_scenes_summary_prompt, generate_chapter_prompt, critique_improve_prompt,) 
# from src.llm import call_g4f_api


def create_new_project():
    """
    Guides the user through creating a new writing project,
    including setting up directories and basic configurations.
    """
    st.header("Create New Project")

    # Get project name from user input
    project_name = st.text_input("Enter Project Name:")

    # Validate the project name and create the project directory
    if project_name:
        project_path = os.path.join(os.getcwd(), project_name)
        if not os.path.exists(project_path):
            os.makedirs(project_path, exist_ok=True)  # Ensure all parent dirs are created if needed 
            st.success(f"Project '{project_name}' created successfully!")

            # Create subdirectories for the project
            create_project_subdirectories(project_path)

            # Initialize configuration file
            initialize_project_config(project_path)

            # Display initial project information
            st.write(f"Project directory: {project_path}")

            # Prompt for initial configuration settings
            get_initial_config_settings(project_path)

        else:
            st.error(f"Project '{project_name}' already exists.")


def create_project_subdirectories(project_path: str):
    """Creates the necessary subdirectories for a new project.

    Args:
        project_path (str): The path to the root of the project directory.
    """

    os.makedirs(os.path.join(project_path, "config"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "synopsis"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "characters"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "world"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "title"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "outline"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "chapters"), exist_ok=True)
    st.success("Project subdirectories created.")

def initialize_project_config(project_path: str):
    """Initializes a basic config file for the new project. 
    
    Args:
        project_path: Path to the project directory
    """
    config_file = os.path.join(project_path, "config", "config.json")
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump({}, f)  # Start with an empty dictionary in the config
    st.success("Project configuration initialized.")


def get_initial_config_settings(project_path: str):
    """Prompts the user for initial project configuration settings.

    Args:
        project_path (str): The path to the project directory. 
    """
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

    config_file = os.path.join(project_path, "config", "config.json")
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config_data, f)
    st.success("Configuration settings saved.")

    # Modify the System Prompt 
    system_prompt_management()
