"""
Module for managing the system prompt used in the application.
Allows the user to view and modify the system prompt.
"""

import json
import os

import streamlit as st

# Note: src.llm.call_g4f_api is NOT imported here; only prompts.get_system_prompt

from src.prompts import get_system_prompt


def system_prompt_management():
    """
    Handles the management of the system prompt,
    allowing users to view and modify it within the application.
    """

    st.header("System Prompt Management")

    # Get project path
    project_path = os.getcwd()
    config_file = os.path.join(project_path, "config", "config.json")

    # Load configuration data
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config_data = json.load(f)
    except FileNotFoundError:
        st.error("Project configuration file not found. Please create a new project.")
        return

    # Display the current system prompt loaded from the config
    st.write("Current System Prompt:")
    st.write(get_system_prompt())

    # Allow user to edit the system prompt in a text area
    new_system_prompt = st.text_area("Enter new system prompt:", get_system_prompt())

    # If the user clicks "Save System Prompt":
    if st.button("Save System Prompt"):
        # Update the 'system_prompt' key in config_data
        config_data["system_prompt"] = new_system_prompt

        # Save the entire updated config_data back to config.json
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f)

        # Provide feedback to the user confirming the save
        st.success("System prompt saved successfully!")
