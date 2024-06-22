import streamlit as st
import os
import json
from llm import call_g4f_api

def text_generation():
    st.header("Text Generation")

    # Get project path
    project_path = os.getcwd()
    config_file = os.path.join(project_path, "config", "config.json")
    outline_file = os.path.join(project_path, "outline", "outline.json")
    chapters_dir = os.path.join(project_path, "chapters")

    # Load configuration data and outline
    try:
        with open(config_file, "r") as f:
            config_data = json.load(f)
        with open(outline_file, "r") as f:
            outline_data = json.load(f)
    except FileNotFoundError:
        st.error("Project configuration file or outline file not found. Please create a new project or generate an outline.")
        return

    # Options for text generation
    choice = st.selectbox("Select an option", ["Add Chapter", "Remove Chapter", "Rearrange Chapters", "Save Modified Outline", "Generate Scenes & Summary", "Edit Scenes & Summary", "Save Scenes & Summary", "Generate Chapter", "Edit Chapter", "Critique & Improve Chapter", "Save Chapter"])

    # Add chapter
    if choice == "Add Chapter":
        new_chapter_title = st.text_input("Enter new chapter title:")
        if new_chapter_title:
            outline_data.append(new_chapter_title)
            with open(outline_file, "w") as f:
                json.dump(outline_data, f)
            st.success("Chapter added to outline.")

    # Remove chapter
    elif choice == "Remove Chapter":
        selected_chapter = st.selectbox("Select chapter to remove:", outline_data)
        if selected_chapter:
            outline_data.remove(selected_chapter)
            with open(outline_file, "w") as f:
                json.dump(outline_data, f)
            st.success("Chapter removed from outline.")

    # Rearrange chapters
    elif choice == "Rearrange Chapters":
        selected_chapter_order = st.multiselect("Select chapter order:", outline_data, default=outline_data)
        outline_data = selected_chapter_order
        with open(outline_file, "w") as f:
            json.dump(outline_data, f)
        st.success("Chapter order updated.")

    # Save modified outline
    elif choice == "Save Modified Outline":
        st.write("Modified Outline Saved.")

    # Generate scenes and summary
    elif choice == "Generate Scenes & Summary":
        selected_chapter = st.selectbox("Select chapter to generate scenes and summary:", outline_data)
        if selected_chapter:
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

            characters_dir = os.path.join(project_path, "characters")
            characters = []
            for filename in os.listdir(characters_dir):
                if filename.endswith(".json"):
                    characters.append(filename[:-5])

            world_file = os.path.join(project_path, "world", "world.json")
            try:
                with open(world_file, "r") as f:
                    world_data = json.load(f)
                    world_info = world_data.get("world_info", "")
            except FileNotFoundError:
                world_info = ""

            # Use call_g4f_api to generate scenes and summary
            prompt = f"Generate detailed scenes and a summary for the chapter '{selected_chapter}' based on the following:\nGenre: {genre}\nTone: {tone}\nPoint of View: {point_of_view}\nWriting Style: {writing_style}\nPremise: {premise}\nSynopsis: {synopsis_text}\nCharacters: {characters}\nWorld Information: {world_info}\nOutline: {selected_chapter}"
            response = call_g4f_api(prompt)

            # Display generated scenes and summary
            st.write("Generated Scenes & Summary:")
            st.write(response)

            # Save generated scenes and summary to file
            chapter_file = os.path.join(chapters_dir, f"{selected_chapter}.txt")
            with open(chapter_file, "w") as f:
                f.write(response)
            st.success("Scenes and summary saved to file.")

    # Edit scenes and summary
    elif choice == "Edit Scenes & Summary":
        selected_chapter = st.selectbox("Select chapter to edit scenes and summary:", outline_data)
        if selected_chapter:
            chapter_file = os.path.join(chapters_dir, f"{selected_chapter}.txt")
            try:
                with open(chapter_file, "r") as f:
                    chapter_text = f.read()
                modified_chapter_text = st.text_area("Edit Scenes & Summary:", chapter_text)

                # Save modified scenes and summary
                with open(chapter_file, "w") as f:
                    f.write(modified_chapter_text)
                st.success("Scenes and summary updated.")

            except FileNotFoundError:
                st.error("Scenes and summary file not found. Please generate scenes and summary first.")

    # Save scenes and summary
    elif choice == "Save Scenes & Summary":
        selected_chapter = st.selectbox("Select chapter to save scenes and summary:", outline_data)
        if selected_chapter:
            chapter_file = os.path.join(chapters_dir, f"{selected_chapter}.txt")
            try:
                with open(chapter_file, "r") as f:
                    chapter_text = f.read()
                st.write("Current Scenes & Summary:")
                st.write(chapter_text)
                st.success("Scenes and summary saved.")

            except FileNotFoundError:
                st.error("Scenes and summary file not found. Please generate scenes and summary first.")

    # Generate chapter
    elif choice == "Generate Chapter":
        selected_chapter = st.selectbox("Select chapter to generate:", outline_data)
        if selected_chapter:
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

            characters_dir = os.path.join(project_path, "characters")
            characters = []
            for filename in os.listdir(characters_dir):
                if filename.endswith(".json"):
                    characters.append(filename[:-5])

            world_file = os.path.join(project_path, "world", "world.json")
            try:
                with open(world_file, "r") as f:
                    world_data = json.load(f)
                    world_info = world_data.get("world_info", "")
            except FileNotFoundError:
                world_info = ""

            chapter_file = os.path.join(chapters_dir, f"{selected_chapter}.txt")
            try:
                with open(chapter_file, "r") as f:
                    scenes_and_summary = f.read()
            except FileNotFoundError:
                scenes_and_summary = "No scenes and summary found."

            # Use call_g4f_api to generate chapter based on user settings
            prompt = f"Generate a full chapter based on the following:\nGenre: {genre}\nTone: {tone}\nPoint of View: {point_of_view}\nWriting Style: {writing_style}\nPremise: {premise}\nSynopsis: {synopsis_text}\nCharacters: {characters}\nWorld Information: {world_info}\nOutline: {selected_chapter}\nScenes & Summary: {scenes_and_summary}"
            response = call_g4f_api(prompt)

            # Display generated chapter
            st.write("Generated Chapter:")
            st.write(response)

            # Save generated chapter to file
            with open(chapter_file, "w") as f:
                f.write(response)
            st.success("Chapter saved to file.")

    # Edit chapter
    elif choice == "Edit Chapter":
        selected_chapter = st.selectbox("Select chapter to edit:", outline_data)
        if selected_chapter:
            chapter_file = os.path.join(chapters_dir, f"{selected_chapter}.txt")
            try:
                with open(chapter_file, "r") as f:
                    chapter_text = f.read()
                modified_chapter_text = st.text_area("Edit Chapter:", chapter_text)

                # Save modified chapter
                with open(chapter_file, "w") as f:
                    f.write(modified_chapter_text)
                st.success("Chapter updated.")

            except FileNotFoundError:
                st.error("Chapter file not found. Please generate a chapter first.")

    # Critique and improve chapter
    elif choice == "Critique & Improve Chapter":
        selected_chapter = st.selectbox("Select chapter to critique and improve:", outline_data)
        if selected_chapter:
            chapter_file = os.path.join(chapters_dir, f"{selected_chapter}.txt")
            try:
                with open(chapter_file, "r") as f:
                    chapter_text = f.read()

                # Use call_g4f_api to critique and improve chapter
                prompt = f"Critique and improve the following chapter:\n{chapter_text}"
                response = call_g4f_api(prompt)

                # Display critique and improvement suggestions
                st.write("Critique and Improvement Suggestions:")
                st.write(response)

            except FileNotFoundError:
                st.error("Chapter file not found. Please generate a chapter first.")

    # Save chapter
    elif choice == "Save Chapter":
        selected_chapter = st.selectbox("Select chapter to save:", outline_data)
        if selected_chapter:
            chapter_file = os.path.join(chapters_dir, f"{selected_chapter}.txt")
            try:
                with open(chapter_file, "r") as f:
                    chapter_text = f.read()
                st.write("Current Chapter:")
                st.write(chapter_text)
                st.success("Chapter saved.")

            except FileNotFoundError:
                st.error("Chapter file not found. Please generate a chapter first.")