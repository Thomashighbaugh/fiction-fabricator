# fiction-fabricator/src/system_prompt.py

"""
Module for managing the system prompt used in the application.
Allows the user to view and modify the system prompt.
"""

import json
import os

import streamlit as st

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

    # User input for system prompt - autosaved
    system_prompt = st.text_area(
        "System Prompt:", config_data.get("system_prompt", get_system_prompt())
    )
    if system_prompt:
        config_data["system_prompt"] = system_prompt
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f)
        st.success("System prompt saved.")
