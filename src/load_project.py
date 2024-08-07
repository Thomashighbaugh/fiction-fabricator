import streamlit as st
import os
import json
from system_prompt import system_prompt_management
from prompts import generate_synopsis_prompt, generate_characters_prompt, generate_world_settings_prompt, generate_title_prompt, generate_outline_prompt, generate_scenes_summary_prompt, generate_chapter_prompt, critique_improve_prompt
from llm import call_g4f_api

def load_existing_project():
    st.header("Load Existing Project")

    # Display list of existing project directories
    project_directories = [
        directory
        for directory in os.listdir(os.getcwd())
        if os.path.isdir(os.path.join(os.getcwd(), directory))
    ]

    # Allow user to select a project
    selected_project = st.selectbox("Select Project:", project_directories)

    # Load project data 
    if selected_project:
        project_path = os.path.join(os.getcwd(), selected_project)

        # Load configuration data
        config_file = os.path.join(project_path, "config", "config.json")
        try:
            with open(config_file, "r") as f:
                config_data = json.load(f)
            st.success(f"Project '{selected_project}' loaded successfully!")
            st.write(f"Project configuration: {config_data}")
            # Modify System Prompt before proceeding
            system_prompt_management()

        except FileNotFoundError:
            st.error(f"Project configuration file not found for '{selected_project}'.")

        # Load synopsis data
        synopsis_file = os.path.join(project_path, "synopsis", "synopsis.txt")
        try:
            with open(synopsis_file, "r") as f:
                synopsis_text = f.read()
            st.write(f"Synopsis: {synopsis_text}")
        except FileNotFoundError:
            st.info(f"Synopsis file not found for '{selected_project}'.")

        # Load character data
        characters_dir = os.path.join(project_path, "characters")
        character_data = {}
        for filename in os.listdir(characters_dir):
            if filename.endswith(".json"):
                character_file = os.path.join(characters_dir, filename)
                with open(character_file, "r") as f:
                    character_data[filename[:-5]] = json.load(f)
        st.write(f"Characters: {character_data}")

        # Load world data
        world_file = os.path.join(project_path, "world", "world.json")
        try:
            with open(world_file, "r") as f:
                world_data = json.load(f)
            st.write(f"World: {world_data}")
        except FileNotFoundError:
            st.info(f"World file not found for '{selected_project}'.")

        # Load title data
        title_file = os.path.join(project_path, "title", "title.txt")
        try:
            with open(title_file, "r") as f:
                title_text = f.read()
            st.write(f"Title: {title_text}")
        except FileNotFoundError:
            st.info(f"Title file not found for '{selected_project}'.")

        # Load outline data
        outline_file = os.path.join(project_path, "outline", "outline.json")
        try:
            with open(outline_file, "r") as f:
                outline_data = json.load(f)
            st.write(f"Outline: {outline_data}")
        except FileNotFoundError:
            st.info(f"Outline file not found for '{selected_project}'.")

        # Load chapter data
        chapters_dir = os.path.join(project_path, "chapters")
        chapter_data = {}
        for filename in os.listdir(chapters_dir):
            if filename.endswith(".txt"):
                chapter_file = os.path.join(chapters_dir, filename)
                with open(chapter_file, "r") as f:
                    chapter_data[filename[:-4]] = f.read()
        st.write(f"Chapters: {chapter_data}")
