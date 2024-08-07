# fiction-fabricator/src/outline.py

"""
Module for generating and managing story outlines.
"""

import json
import os

import streamlit as st

from src.llm import call_g4f_api
from src.prompts import generate_outline_prompt


def outline_management():
    """
    Manages the generation, editing, critique, and saving of story outlines.
    """
    st.header("Outline Generation")

    # Get project path
    project_path = os.getcwd()
    config_file = os.path.join(project_path, "config", "config.json")
    outline_file = os.path.join(project_path, "outline", "outline.json")

    # Load configuration data
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config_data = json.load(f)
    except FileNotFoundError:
        st.error("Project configuration file not found. Please create a new project.")
        return

    # Load existing outline if it exists
    try:
        with open(outline_file, "r", encoding="utf-8") as f:
            outline_data = json.load(f)
    except FileNotFoundError:
        outline_data = []

    # User input for outline - autosaved
    outline_text = st.text_area("Outline:", "\n\n".join(outline_data))
    if outline_text:
        outline_data = outline_text.split("\n\n")
        with open(outline_file, "w", encoding="utf-8") as f:
            json.dump(outline_data, f)

    # Generate Outline button
    if st.button("Generate Outline"):
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

        characters_dir = os.path.join(project_path, "characters")
        characters = []
        for filename in os.listdir(characters_dir):
            if filename.endswith(".json"):
                characters.append(filename[:-5])

        world_file = os.path.join(project_path, "world", "world.json")
        try:
            with open(world_file, "r", encoding="utf-8") as f:
                world_data = json.load(f)
                world_info = world_data.get("world_info", "")
        except FileNotFoundError:
            world_info = ""

        # Use call_g4f_api to generate outline based on user settings
        prompt = generate_outline_prompt(
            genre,
            tone,
            point_of_view,
            writing_style,
            premise,
            synopsis_text,
            characters,
            world_info,
        )
        response = call_g4f_api(prompt)

        # Display generated outline and autosave
        st.write("Generated Outline:")
        st.text_area("Outline:", response, key="generated_outline")
        outline_data = response.split("\n\n")
        with open(outline_file, "w", encoding="utf-8") as f:
            json.dump(outline_data, f)
        st.success("Outline saved to file.")

    # Critique and Improve Outline button
    if st.button("Critique & Improve Outline"):
        try:
            with open(outline_file, "r", encoding="utf-8") as f:
                outline_data = json.load(f)
            outline_text = "\n\n".join(outline_data)

            # Use call_g4f_api to critique and improve outline
            prompt = f"Critique and improve the following outline:\n{outline_text}"
            response = call_g4f_api(prompt)

            # Display critique and improvement suggestions
            st.write("Critique and Improvement Suggestions:")
            st.write(response)

        except FileNotFoundError:
            st.error("Outline file not found. Please generate an outline first.")
