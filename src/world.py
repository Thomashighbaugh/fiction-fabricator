import streamlit as st
import os
import json
from llm import call_g4f_api

def world_management():
    st.header("World & Settings Management")

    # Get project path
    project_path = os.getcwd()
    config_file = os.path.join(project_path, "config", "config.json")
    world_file = os.path.join(project_path, "world", "world.json")
    settings_dir = os.path.join(project_path, "world", "settings")

    # Load configuration and world data
    try:
        with open(config_file, "r") as f:
            config_data = json.load(f)
        try:
            with open(world_file, "r") as f:
                world_data = json.load(f)
        except FileNotFoundError:
            world_data = {}
        settings_data = {}
        for filename in os.listdir(settings_dir):
            if filename.endswith(".json"):
                setting_file = os.path.join(settings_dir, filename)
                with open(setting_file, "r") as f:
                    settings_data[filename[:-5]] = json.load(f)
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

    # Options for world and settings management
    choice = st.selectbox("Select an option", ["Generate World & Settings", "Add Setting", "Edit Setting", "Delete Setting", "Edit World Information", "Save Settings & World Information"])

    # Generate world and settings
    if choice == "Generate World & Settings":
        # Get user-defined configuration settings
        genre = config_data["genre"]
        tone = config_data["tone"]
        point_of_view = config_data["point_of_view"]
        writing_style = config_data["writing_style"]
        premise = config_data["premise"]
        synopsis_file = os.path.join(project_path, "synopsis", "synopsis.txt")
        try:
            with open(synopsis_file, "r") as f:
                synopsis_text = f.read()
        except FileNotFoundError:
            synopsis_text = "No synopsis found."

        # Use call_g4f_api to generate world and settings based on user settings
        prompt = f"Generate the world and settings for a story with the following characteristics:\nGenre: {genre}\nTone: {tone}\nPoint of View: {point_of_view}\nWriting Style: {writing_style}\nPremise: {premise}\nSynopsis: {synopsis_text}"
        response = call_g4f_api(prompt)

        # Display generated world and settings
        st.write("Generated World & Settings:")
        st.write(response)

        # Save generated world and settings to files
        world_sections = response.split("\n\n")
        for section in world_sections:
            section_header = section.split("\n")[0].strip()
            if "World Information" in section_header:
                world_details = section.split("\n")[1:]
                world_data["world_info"] = "\n".join(world_details)
                with open(world_file, "w") as f:
                    json.dump(world_data, f)
            elif "Settings" in section_header:
                settings = section.split("\n")[1:]
                for setting in settings:
                    setting_name = setting.split("\n")[0].strip()
                    setting_details = setting.split("\n")[1:]
                    settings_data[setting_name] = {"name": setting_name, "description": "\n".join(setting_details)}
                    setting_file = os.path.join(settings_dir, f"{setting_name}.json")
                    with open(setting_file, "w") as f:
                        json.dump(settings_data[setting_name], f)
        st.success("World and settings saved to files.")

    # Add setting
    elif choice == "Add Setting":
        setting_name = st.text_input("Enter Setting Name:")
        setting_description = st.text_area("Enter Setting Description:")

        # Save new setting to file
        if setting_name:
            settings_data[setting_name] = {"name": setting_name, "description": setting_description}
            setting_file = os.path.join(settings_dir, f"{setting_name}.json")
            with open(setting_file, "w") as f:
                json.dump(settings_data[setting_name], f)
            st.success(f"Setting '{setting_name}' added.")

    # Edit setting
    elif choice == "Edit Setting":
        selected_setting = st.selectbox("Select Setting:", list(settings_data.keys()))
        if selected_setting:
            setting_name = selected_setting
            current_description = settings_data[setting_name]["description"]
            modified_description = st.text_area("Edit Setting Description:", current_description)

            # Save edited setting
            settings_data[setting_name]["description"] = modified_description
            setting_file = os.path.join(settings_dir, f"{setting_name}.json")
            with open(setting_file, "w") as f:
                json.dump(settings_data[setting_name], f)
            st.success(f"Setting '{setting_name}' updated.")

    # Delete setting
    elif choice == "Delete Setting":
        selected_setting = st.selectbox("Select Setting to Delete:", list(settings_data.keys()))
        if selected_setting:
            setting_name = selected_setting
            confirm_delete = st.button(f"Delete {setting_name}?")
            if confirm_delete:
                setting_file = os.path.join(settings_dir, f"{setting_name}.json")
                os.remove(setting_file)
                del settings_data[setting_name]
                st.success(f"Setting '{setting_name}' deleted.")

    # Edit world information
    elif choice == "Edit World Information":
        try:
            current_world_info = world_data["world_info"]
            modified_world_info = st.text_area("Edit World Information:", current_world_info)
            world_data["world_info"] = modified_world_info
            with open(world_file, "w") as f:
                json.dump(world_data, f)
            st.success("World information updated.")
        except KeyError:
            st.info("No world information found. Please generate world details first.")

    # Save settings & world information
    elif choice == "Save Settings & World Information":
        st.write("Settings & World Information Saved.")