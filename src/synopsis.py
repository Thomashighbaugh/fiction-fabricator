"""
Module dedicated to managing story synopses within a writing project. 
Provides functionality for generating, viewing, modifying, 
critiquing, and saving synopsis information.
"""

import json
import os

import streamlit as st

from src.llm import call_g4f_api


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

    # User choices for synopsis management - consider a more streamlined design?
    choice = st.selectbox(
        "Select an option",
        ["Generate Synopsis", "Modify Synopsis", "Critique & Improve Synopsis", "Save Synopsis"]
    )

    # Generates a new synopsis based on the project configuration
    if choice == "Generate Synopsis": 
        genre = config_data["genre"]
        tone = config_data["tone"]
        point_of_view = config_data["point_of_view"]
        writing_style = config_data["writing_style"]
        premise = config_data["premise"]

        # Generate the synopsis using the language model
        prompt = (
            f"Generate a synopsis for a story with the following characteristics:\n"
            f"Genre: {genre}\n"
            f"Tone: {tone}\n"
            f"Point of View: {point_of_view}\n"
            f"Writing Style: {writing_style}\n"
            f"Premise: {premise}"
        )
        response = call_g4f_api(prompt)

        # Display the generated synopsis
        st.write("Generated Synopsis:")
        st.write(response)

        # Save the generated synopsis to the synopsis file (could be optional?)
        with open(synopsis_file, "w", encoding="utf-8") as f:
            f.write(response)
        st.success("Synopsis saved to file.")

    # Modify an existing synopsis 
    elif choice == "Modify Synopsis":
        # Try to open an existing synopsis, handle if not found
        try:
            with open(synopsis_file, "r", encoding="utf-8") as f:
                synopsis_text = f.read()
                modified_synopsis = st.text_area(
                    "Modify Synopsis:", synopsis_text
                )

            # Save modified synopsis (consider autosave on text area change)
            with open(synopsis_file, "w", encoding="utf-8") as f:
                f.write(modified_synopsis)
            st.success("Synopsis updated.")

        except FileNotFoundError:
            st.error("Synopsis file not found. Please generate a synopsis first.")

    # Get critique and improvement suggestions using the language model 
    elif choice == "Critique & Improve Synopsis": 
        try:
            with open(synopsis_file, "r", encoding="utf-8") as f:
                synopsis_text = f.read()

            prompt = f"Critique and improve the following synopsis:\n{synopsis_text}"
            response = call_g4f_api(prompt)

            # Display critique and suggestions
            st.write("Critique and Improvement Suggestions:")
            st.write(response)

        except FileNotFoundError:
            st.error(
                "Synopsis file not found. Please generate a synopsis first."
            )

    # Redundant saving option - optimize for automatic saving after generation/edits
    elif choice == "Save Synopsis":  
        try:
            with open(synopsis_file, "r", encoding="utf-8") as f:
                synopsis_text = f.read()
            st.write("Current Synopsis:")
            st.write(synopsis_text)
            st.success("Synopsis saved.")

        except FileNotFoundError:
            st.error(
                "Synopsis file not found. Please generate a synopsis first."
            )
