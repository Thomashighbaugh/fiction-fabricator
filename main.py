# fiction-fabricator/main.py

"""
Main module for the Fiction Fabricator application.
"""

import os

import streamlit as st

# Import modules for menu options
from src.create_project import create_new_project
from src.load_project import load_existing_project
from src.synopsis import synopsis_management
from src.character import character_management
from src.world import world_management
from src.title import title_management
from src.outline import outline_management
from src.text_generation import text_generation
from src.export import export_management
from src.system_prompt import system_prompt_management


# Define main menu function
def main():
    """
    Main function to display the application and handle user interaction.
    """

    st.title("Fiction Fabricator")

    # Set the project directory to the user's home directory
    project_dir = os.path.expanduser("~")
    os.chdir(project_dir)

    # Display menu options in the sidebar
    choice = st.sidebar.selectbox(
        "Navigation",
        [
            "Create New Project",
            "Load Existing Project",
            "System Prompt",
            "Premise",
            "Genre",
            "Tone",
            "Point of View",
            "Writing Style",
            "Synopsis",
            "Character",
            "World",
            "Title",
            "Outline",
            "Text Generation",
            "Export",
            "Quit",
        ],
    )

    # Process user selection
    if choice == "Create New Project":
        create_new_project()
    elif choice == "Load Existing Project":
        load_existing_project()
    elif choice == "System Prompt":
        system_prompt_management()
    elif choice == "Synopsis":
        synopsis_management()
    elif choice == "Character":
        character_management()
    elif choice == "World":
        world_management()
    elif choice == "Title":
        title_management()
    elif choice == "Outline":
        outline_management()
    elif choice == "Text Generation":
        text_generation()
    elif choice == "Export":
        export_management()
    elif choice == "Quit":
        st.write("Exiting Fiction Fabricator...")
        exit()


# Execute main function if the script is run directly
if __name__ == "__main__":
    main()
