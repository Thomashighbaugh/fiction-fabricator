import streamlit as st
import os
import json
from llm import call_g4f_api

def title_management():
    st.header("Title Management")

    # Get project path
    project_path = os.getcwd()
    title_file = os.path.join(project_path, "title", "title.txt")

    # Options for title management
    choice = st.selectbox("Select an option", ["Generate Title", "Edit Title", "Save Title"])

    # Generate title
    if choice == "Generate Title":
        # Get user-defined configuration settings
        config_file = os.path.join(project_path, "config", "config.json")
        try:
            with open(config_file, "r") as f:
                config_data = json.load(f)
        except FileNotFoundError:
            st.error("Project configuration file not found. Please create a new project.")
            return

        genre = config_data["genre"]
        tone = config_data["tone"]
        premise = config_data["premise"]

        # Use call_g4f_api to generate titles based on user settings
        prompt = f"Generate a list of potential titles for a story with the following characteristics:\nGenre: {genre}\nTone: {tone}\nPremise: {premise}"
        response = call_g4f_api(prompt)

        # Display generated titles
        st.write("Generated Titles:")
        st.write(response)

        # Allow user to select a title
        selected_title = st.selectbox("Select a Title:", response.split("\n"))

        # Save selected title to file
        with open(title_file, "w") as f:
            f.write(selected_title)
        st.success("Title saved to file.")

    # Edit title
    elif choice == "Edit Title":
        try:
            with open(title_file, "r") as f:
                current_title = f.read()
            modified_title = st.text_input("Edit Title:", current_title)

            # Save edited title
            with open(title_file, "w") as f:
                f.write(modified_title)
            st.success("Title updated.")

        except FileNotFoundError:
            st.error("Title file not found. Please generate a title first.")

    # Save title
    elif choice == "Save Title":
        try:
            with open(title_file, "r") as f:
                title_text = f.read()
            st.write("Current Title:")
            st.write(title_text)
            st.success("Title saved.")

        except FileNotFoundError:
            st.error("Title file not found. Please generate a title first.")