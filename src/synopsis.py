# fiction-fabricator/src/synopsis.py

"""
Module dedicated to managing story synopses within a writing project. 
Provides functionality for generating, viewing, modifying, 
critiquing, and saving synopsis information.
"""

import json
import os

import streamlit as st

from src.llm import call_g4f_api
from src.prompts import generate_synopsis_prompt


def synopsis_management():
    """
    Provides an interactive interface for managing a story synopsis.
    Allows the user to generate a new synopsis, view the existing one,
    make modifications, get AI-powered critiques and improvement suggestions,
    and save the synopsis to the project files.
    """
    st.header("Synopsis Management")

    # Get the current project path
    project_path = os.getcwd()
    config_file = os.path.join(project_path, "config", "config.json")
    synopsis_file = os.path.join(project_path, "synopsis", "synopsis.txt")

    # Load configuration data - important to have for synopsis generation
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config_data = json.load(f)
    except FileNotFoundError:
        st.error("Project configuration file not found. Please create a new project.")
        return

    # Display relevant configuration settings
    st.write("Project configuration:")
    st.write(f"Genre: {config_data['genre']}")
    st.write(f"Tone: {config_data['tone']}")
    st.write(f"Point of View: {config_data['point_of_view']}")
    st.write(f"Writing Style: {config_data['writing_style']}")
    st.write(f"Premise: {config_data['premise']}")

    # User input for synopsis - autosaved
    synopsis_text = st.text_area("Synopsis:", "")
    if synopsis_text:
        with open(synopsis_file, "w", encoding="utf-8") as f:
            f.write(synopsis_text)

    # Generate synopsis button
    if st.button("Generate Synopsis"):
        genre = config_data.get("genre", "")
        tone = config_data.get("tone", "")
        point_of_view = config_data.get("point_of_view", "")
        writing_style = config_data.get("writing_style", "")
        premise = config_data.get("premise", "")

        # Generate the synopsis using the language model
        prompt = generate_synopsis_prompt(
            genre, tone, point_of_view, writing_style, premise
        )
        response = call_g4f_api(prompt)

        # Display the generated synopsis and autosave
        st.write("Generated Synopsis:")
        st.text_area("Synopsis:", response, key="generated_synopsis")
        with open(synopsis_file, "w", encoding="utf-8") as f:
            f.write(response)
        st.success("Synopsis saved to file.")

    # Critique and improve synopsis button
    if st.button("Critique & Improve Synopsis"):
        try:
            with open(synopsis_file, "r", encoding="utf-8") as f:
                synopsis_text = f.read()

            prompt = f"Critique and improve the following synopsis:\n{synopsis_text}"
            response = call_g4f_api(prompt)

            # Display critique and suggestions
            st.write("Critique and Improvement Suggestions:")
            st.write(response)

        except FileNotFoundError:
            st.error("Synopsis file not found. Please generate a synopsis first.")
