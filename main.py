import streamlit as st
import os

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
from src.llm import call_g4f_api

# Define main menu function
def main():
    st.title("Fiction Fabricator")

    # Display menu options
    choice = st.sidebar.selectbox("Select an option", ["Create New Project", "Load Existing Project", "Quit"])

    # Process user selection
    if choice == "Create New Project":
        create_new_project()
    elif choice == "Load Existing Project":
        load_existing_project()
    elif choice == "Quit":
        st.write("Exiting Fiction Fabricator...")
        exit()

# Execute main function
if __name__ == "__main__":
    main()
