"""
Module for loading existing writing projects.
"""

import json
import os

import streamlit as st

from src.system_prompt import system_prompt_management

# The following imports seem unused, consider removing them if not needed:
# from src.prompts import generate_synopsis_prompt, generate_characters_prompt, \
#    generate_world_settings_prompt, generate_title_prompt, generate_outline_prompt, \
#    generate_scenes_summary_prompt, generate_chapter_prompt, critique_improve_prompt
# from src.llm import call_g4f_api


def load_existing_project():
    """
    Provides functionality to load existing projects and display their data.
    """
    st.header("Load Existing Project")

    # Get a list of potential project directories
    project_directories = [
        directory
        for directory in os.listdir(os.getcwd())
        if os.path.isdir(os.path.join(os.getcwd(), directory))
    ]

    # Allow user to select a project from the found directories
    selected_project = st.selectbox("Select Project:", project_directories)

    if selected_project:
        project_path = os.path.join(os.getcwd(), selected_project)
        config_file = os.path.join(project_path, "config", "config.json")

        # Load project configuration data
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            st.success(f"Project '{selected_project}' loaded successfully!")
            st.write(f"Project configuration: {config_data}")

            # Allow system prompt modification after loading the project
            system_prompt_management()
        except FileNotFoundError:
            st.error(f"Project configuration file not found for '{selected_project}'.")
            # It's a good practice to return here to prevent further execution
            #  if the config file is missing
            return

        # Define paths for other project files
        synopsis_file = os.path.join(project_path, "synopsis", "synopsis.txt")
        characters_dir = os.path.join(project_path, "characters")
        world_file = os.path.join(project_path, "world", "world.json")
        title_file = os.path.join(project_path, "title", "title.txt")
        outline_file = os.path.join(project_path, "outline", "outline.json")
        chapters_dir = os.path.join(project_path, "chapters")

        # Load and display (or handle if not found) each project data component:

        # Synopsis:
        try:
            with open(synopsis_file, "r", encoding="utf-8") as f:
                synopsis_text = f.read()
            st.write(f"Synopsis: {synopsis_text}")
        except FileNotFoundError:
            st.info(f"Synopsis file not found for '{selected_project}'.")

        # Characters:
        try:
            character_data = {}
            for filename in os.listdir(characters_dir):
                if filename.endswith(".json"):
                    character_file = os.path.join(characters_dir, filename)
                    with open(character_file, "r", encoding="utf-8") as f:
                        character_data[filename[:-5]] = json.load(f)
            st.write(f"Characters: {character_data}")
        except FileNotFoundError:
            st.info(f"No characters found for '{selected_project}'.")

        # World Data
        try:
            with open(world_file, "r", encoding="utf-8") as f:
                world_data = json.load(f)
            st.write(f"World: {world_data}")
        except FileNotFoundError:
            st.info(f"World file not found for '{selected_project}'.")

        # Title:
        try:
            with open(title_file, "r", encoding="utf-8") as f:
                title_text = f.read()
            st.write(f"Title: {title_text}")
        except FileNotFoundError:
            st.info(f"Title file not found for '{selected_project}'.")

        # Outline
        try:
            with open(outline_file, "r", encoding="utf-8") as f:
                outline_data = json.load(f)
            st.write(f"Outline: {outline_data}")
        except FileNotFoundError:
            st.info(f"Outline file not found for '{selected_project}'.")

        # Chapters:
        try:
            chapter_data = {}
            for filename in os.listdir(chapters_dir):
                if filename.endswith(".txt"):
                    chapter_file = os.path.join(chapters_dir, filename)
                    with open(chapter_file, "r", encoding="utf-8") as f:
                        chapter_data[filename[:-4]] = f.read()
            st.write(f"Chapters: {chapter_data}")
        except FileNotFoundError:
            st.info(f"No chapters found for '{selected_project}'.")
