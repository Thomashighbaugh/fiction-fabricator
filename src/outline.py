"""
Module for generating and managing story outlines.
"""

import json
import os

import streamlit as st

from src.llm import call_g4f_api


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
        st.error(
            "Project configuration file not found. Please create a new project."
        )
        return

    # Options for outline management
    choice = st.selectbox(
        "Select an option",
        [
            "Generate Outline",
            "Edit Outline",
            "Critique & Improve Outline",
            "Save Outline",
        ],
    )

    # Generate outline
    if choice == "Generate Outline":
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
        prompt = (
            f"Generate a story outline with the following characteristics:\n"
            f"Genre: {genre}\n"
            f"Tone: {tone}\n"
            f"Point of View: {point_of_view}\n"
            f"Writing Style: {writing_style}\n"
            f"Premise: {premise}\n"
            f"Synopsis: {synopsis_text}\n"
            f"Characters: {characters}\n"
            f"World Information: {world_info}"
        )
        response = call_g4f_api(prompt)

        # Display generated outline
        st.write("Generated Outline:")
        st.write(response)

        # Save generated outline to file
        outline_data = response.split("\n\n")
        with open(outline_file, "w", encoding="utf-8") as f:
            json.dump(outline_data, f)
        st.success("Outline saved to file.")

    # Edit outline
    elif choice == "Edit Outline":
        try:
            with open(outline_file, "r", encoding="utf-8") as f:
                outline_data = json.load(f)
            modified_outline = st.text_area(
                "Edit Outline:", "\n\n".join(outline_data)
            )

            # Save modified outline
            with open(outline_file, "w", encoding="utf-8") as f:
                json.dump(modified_outline.split("\n\n"), f)
            st.success("Outline updated.")

        except FileNotFoundError:
            st.error(
                "Outline file not found. Please generate an outline first."
            )

    # Critique and improve outline
    elif choice == "Critique & Improve Outline":
        try:
            with open(outline_file, "r", encoding="utf-8") as f:
                outline_data = json.load(f)
            outline_text = "\n\n".join(outline_data)

            # Use call_g4f_api to critique and improve outline
            prompt = (
                f"Critique and improve the following outline:\n{outline_text}"
            )
            response = call_g4f_api(prompt)

            # Display critique and improvement suggestions
            st.write("Critique and Improvement Suggestions:")
            st.write(response)

        except FileNotFoundError:
            st.error(
                "Outline file not found. Please generate an outline first."
            )

    # Save outline - this seems redundant; should it be automatic on edit?
    elif choice == "Save Outline":
        try:
            with open(outline_file, "r", encoding="utf-8") as f:
                outline_data = json.load(f)
            st.write("Current Outline:")
            st.write("\n\n".join(outline_data))
            st.success("Outline saved.") 

        except FileNotFoundError:
            st.error(
                "Outline file not found. Please generate an outline first."
            )
