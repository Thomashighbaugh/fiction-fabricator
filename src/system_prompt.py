import streamlit as st
import os
import json
from src.llm import call_g4f_api
from src.prompts import get_system_prompt

def system_prompt_management():
    st.header("System Prompt Management")

    # Get project path
    project_path = os.getcwd()
    config_file = os.path.join(project_path, "config", "config.json")

    # Load configuration data
    try:
        with open(config_file, "r") as f:
            config_data = json.load(f)
    except FileNotFoundError:
        st.error("Project configuration file not found. Please create a new project.")
        return

    # Display current system prompt
    st.write("Current System Prompt:")
    st.write(get_system_prompt())

    # Allow user to edit the system prompt
    new_system_prompt = st.text_area("Enter new system prompt:", get_system_prompt())

    # Save the new system prompt
    if st.button("Save System Prompt"):
        config_data["system_prompt"] = new_system_prompt
        with open(config_file, "w") as f:
            json.dump(config_data, f)
        st.success("System prompt saved successfully!")
