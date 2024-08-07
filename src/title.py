# fiction-fabricator/src/title.py

"""
Module for generating, editing, and managing story titles.
"""

import json
import os

import streamlit as st

from src.llm import call_g4f_api
from src.prompts import generate_title_prompt


def title_management():
    """
    Manages the generation, editing, and saving of story titles.
    """
    st.header("Title Management")

    # Get project path
    project_path = os.getcwd()
    title_file = os.path.join(project_path, "title", "title.txt")

    # Load existing title if it exists
    try:
        with open(title_file, "r", encoding="utf-8") as f:
            current_title = f.read()
    except FileNotFoundError:
        current_title = ""

    # User input for title - autosaved
    title_text = st.text_input("Title:", current_title)
    if title_text:
        with open(title_file, "w", encoding="utf-8") as f:
            f.write(title_text)

    # Generate Title button
    if st.button("Generate Title"):
        # Get user-defined configuration settings
        config_file = os.path.join(project_path, "config", "config.json")
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except FileNotFoundError:
            st.error(
                "Project configuration file not found. Please create a new project."
            )
            return

        genre = config_data.get("genre", "")
        tone = config_data.get("tone", "")
        premise = config_data.get("premise", "")

        # Use call_g4f_api to generate titles based on user settings
        prompt = generate_title_prompt(genre, tone, premise)
        response = call_g4f_api(prompt)

        # Display generated titles
        st.write("Generated Titles:")
        st.write(response)

        # Allow user to select a title and autosave
        selected_title = st.selectbox("Select a Title:", response.split("\n"))
        if selected_title:
            with open(title_file, "w", encoding="utf-8") as f:
                f.write(selected_title)
            st.success("Title saved to file.")
            st.text_input("Title:", selected_title, key="selected_title")
