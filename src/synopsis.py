import streamlit as st
import os
import json
from llm import call_g4f_api

def synopsis_management():
    st.header("Synopsis Management")

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

    # Display configuration settings
    st.write("Project configuration:")
    st.write(f"Genre: {config_data['genre']}")
    st.write(f"Tone: {config_data['tone']}")
    st.write(f"Point of View: {config_data['point_of_view']}")
    st.write(f"Writing Style: {config_data['writing_style']}")
    st.write(f"Premise: {config_data['premise']}")

    # Options for synopsis management
    choice = st.selectbox("Select an option", ["Generate Synopsis", "Modify Synopsis", "Critique & Improve Synopsis", "Save Synopsis"])

    # Generate synopsis
    if choice == "Generate Synopsis":
        # Get user-defined configuration settings
        genre = config_data["genre"]
        tone = config_data["tone"]
        point_of_view = config_data["point_of_view"]
        writing_style = config_data["writing_style"]
        premise = config_data["premise"]

        # Use call_g4f_api to generate synopsis based on user settings
        prompt = f"Generate a synopsis for a story with the following characteristics:\nGenre: {genre}\nTone: {tone}\nPoint of View: {point_of_view}\nWriting Style: {writing_style}\nPremise: {premise}"
        response = call_g4f_api(prompt)

        # Display generated synopsis
        st.write("Generated Synopsis:")
        st.write(response)

        # Save synopsis to file
        synopsis_file = os.path.join(project_path, "synopsis", "synopsis.txt")
        with open(synopsis_file, "w") as f:
            f.write(response)
        st.success("Synopsis saved to file.")

    # Modify synopsis
    elif choice == "Modify Synopsis":
        synopsis_file = os.path.join(project_path, "synopsis", "synopsis.txt")
        try:
            with open(synopsis_file, "r") as f:
                synopsis_text = f.read()
            modified_synopsis = st.text_area("Modify Synopsis:", synopsis_text)

            # Save modified synopsis
            with open(synopsis_file, "w") as f:
                f.write(modified_synopsis)
            st.success("Synopsis updated.")

        except FileNotFoundError:
            st.error("Synopsis file not found. Please generate a synopsis first.")

    # Critique and improve synopsis
    elif choice == "Critique & Improve Synopsis":
        synopsis_file = os.path.join(project_path, "synopsis", "synopsis.txt")
        try:
            with open(synopsis_file, "r") as f:
                synopsis_text = f.read()
            
            # Use call_g4f_api to critique and improve synopsis
            prompt = f"Critique and improve the following synopsis:\n{synopsis_text}"
            response = call_g4f_api(prompt)

            # Display critique and improvement suggestions
            st.write("Critique and Improvement Suggestions:")
            st.write(response)

        except FileNotFoundError:
            st.error("Synopsis file not found. Please generate a synopsis first.")

    # Save synopsis
    elif choice == "Save Synopsis":
        synopsis_file = os.path.join(project_path, "synopsis", "synopsis.txt")
        try:
            with open(synopsis_file, "r") as f:
                synopsis_text = f.read()
            st.write("Current Synopsis:")
            st.write(synopsis_text)
            st.success("Synopsis saved.")

        except FileNotFoundError:
            st.error("Synopsis file not found. Please generate a synopsis first.")