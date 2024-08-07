"""
Module for managing the text generation aspects of chapters within the application.
This includes creating, modifying, and managing chapters based on the story outline.
It interacts with the LLM for generating text for scenes, summaries, and full chapters.
"""
import json
import os

import streamlit as st

from src.llm import call_g4f_api


def text_generation():
    """Provides the main interface for chapter text generation and management."""
    st.header("Text Generation")

    # Load essential project data: Configuration and Outline
    project_path = os.getcwd()
    config_data, outline_data = load_project_data(project_path)
    if config_data is None or outline_data is None:
        # Error handling already present in load_project_data
        return

    # Choices for chapter text generation and management
    choice = st.selectbox(
        "Select an option",
        [
            "Add Chapter",
            "Remove Chapter",
            "Rearrange Chapters",
            "Save Modified Outline",  # This could potentially be automated
            "Generate Scenes & Summary",
            "Edit Scenes & Summary",
            "Save Scenes & Summary",  # Also could be automated
            "Generate Chapter",
            "Edit Chapter",
            "Critique & Improve Chapter",
            "Save Chapter",  # Potentially automate saving
        ],
    )

    # Handle Outline Modification Choices
    if choice == "Add Chapter":
        outline_data = add_chapter(outline_data, project_path)

    elif choice == "Remove Chapter":
        outline_data = remove_chapter(outline_data, project_path)

    elif choice == "Rearrange Chapters":
        outline_data = rearrange_chapters(outline_data, project_path)

    elif choice == "Save Modified Outline":  # This might be redundant
        save_outline(outline_data, project_path)

    # Chapter Content Generation and Manipulation

    elif choice == "Generate Scenes & Summary":
        generate_scenes_and_summary(config_data, outline_data, project_path)

    elif choice == "Edit Scenes & Summary":
        edit_scenes_and_summary(outline_data, project_path)

    elif choice == "Save Scenes & Summary":
        save_scenes_and_summary(outline_data, project_path)

    elif choice == "Generate Chapter":
        generate_chapter(config_data, outline_data, project_path)

    elif choice == "Edit Chapter":
        edit_chapter(outline_data, project_path)

    elif choice == "Critique & Improve Chapter":
        critique_and_improve_chapter(outline_data, project_path)

    elif choice == "Save Chapter":
        save_chapter(outline_data, project_path)


def load_project_data(project_path: str):
    """Loads the configuration and outline data for the project."""
    config_file = os.path.join(project_path, "config", "config.json")
    outline_file = os.path.join(project_path, "outline", "outline.json")

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config_data = json.load(f)
        with open(outline_file, "r", encoding="utf-8") as f:
            outline_data = json.load(f)
        return config_data, outline_data

    except FileNotFoundError:
        st.error(
            "Project configuration file or outline file not found. "
            "Please create a new project or generate an outline."
        )
        return None, None


def add_chapter(outline_data: list, project_path: str):
    """Adds a new chapter title to the outline."""
    outline_file = os.path.join(project_path, "outline", "outline.json")
    new_chapter_title = st.text_input("Enter new chapter title:")
    if new_chapter_title:
        outline_data.append(new_chapter_title)
        with open(outline_file, "w", encoding="utf-8") as f:
            json.dump(outline_data, f)
        st.success("Chapter added to outline.")
    return outline_data  # Return the updated outline_data


def remove_chapter(outline_data: list, project_path: str):
    """Removes a chapter from the outline."""
    outline_file = os.path.join(project_path, "outline", "outline.json")
    selected_chapter = st.selectbox("Select chapter to remove:", outline_data)
    if selected_chapter:
        outline_data.remove(selected_chapter)
        with open(outline_file, "w", encoding="utf-8") as f:
            json.dump(outline_data, f)
        st.success("Chapter removed from outline.")
    return outline_data  # Return the updated outline data


def rearrange_chapters(outline_data: list, project_path: str):
    """Allows the user to rearrange the order of chapters."""
    outline_file = os.path.join(project_path, "outline", "outline.json")
    selected_chapter_order = st.multiselect(
        "Select chapter order:", outline_data, default=outline_data
    )
    outline_data = selected_chapter_order
    with open(outline_file, "w", encoding="utf-8") as f:
        json.dump(outline_data, f)
    st.success("Chapter order updated.")
    return outline_data  # Return the updated outline data


def save_outline(outline_data: list, project_path: str):
    """Saves the current outline. This might be redundant with autosave."""
    outline_file = os.path.join(project_path, "outline", "outline.json")
    with open(outline_file, "w", encoding="utf-8") as f:
        json.dump(outline_data, f)
    st.success("Modified Outline Saved.")


def generate_scenes_and_summary(config_data: dict, outline_data: list, project_path: str):
    """Generates detailed scenes and a summary for a selected chapter."""
    selected_chapter = st.selectbox(
        "Select chapter to generate scenes and summary:", outline_data
    )
    if selected_chapter:
        genre = config_data["genre"]
        tone = config_data["tone"]
        point_of_view = config_data["point_of_view"]
        writing_style = config_data["writing_style"]
        premise = config_data["premise"]

        synopsis_file = os.path.join(project_path, "synopsis", "synopsis.txt")
        try:
            with open(synopsis_file, "r", encoding="utf-8") as f:
                synopsis_text = f.read()
        except FileNotFoundError:
            synopsis_text = "No synopsis found."

        characters = load_characters(project_path)
        world_info = load_world_info(project_path)

        # Generate scenes and summary using the language model
        prompt = (
            f"Generate detailed scenes and a summary for the chapter '{selected_chapter}' based on the following:\n"
            f"Genre: {genre}\n"
            f"Tone: {tone}\n"
            f"Point of View: {point_of_view}\n"
            f"Writing Style: {writing_style}\n"
            f"Premise: {premise}\n"
            f"Synopsis: {synopsis_text}\n"
            f"Characters: {characters}\n"
            f"World Information: {world_info}\n"
            f"Outline: {selected_chapter}"
        )
        response = call_g4f_api(prompt)

        st.write("Generated Scenes & Summary:")
        st.write(response)

        chapters_dir = os.path.join(project_path, "chapters")
        chapter_file = os.path.join(chapters_dir, f"{selected_chapter}.txt")
        with open(chapter_file, "w", encoding="utf-8") as f:
            f.write(response)
        st.success("Scenes and summary saved to file.")


def edit_scenes_and_summary(outline_data: list, project_path: str):
    """Edits existing scenes and summary for a selected chapter."""
    chapters_dir = os.path.join(project_path, "chapters")
    selected_chapter = st.selectbox(
        "Select chapter to edit scenes and summary:", outline_data
    )
    if selected_chapter:
        chapter_file = os.path.join(chapters_dir, f"{selected_chapter}.txt")
        try:
            with open(chapter_file, "r", encoding="utf-8") as f:
                chapter_text = f.read()
            modified_chapter_text = st.text_area(
                "Edit Scenes & Summary:", chapter_text
            )
            with open(chapter_file, "w", encoding="utf-8") as f:
                f.write(modified_chapter_text)
            st.success("Scenes and summary updated.")
        except FileNotFoundError:
            st.error(
                "Scenes and summary file not found. Please generate scenes and summary first."
            )


def save_scenes_and_summary(outline_data: list, project_path: str):
    """Saves scenes and summary - consider automatic saving on edit."""
    chapters_dir = os.path.join(project_path, "chapters")
    selected_chapter = st.selectbox(
        "Select chapter to save scenes and summary:", outline_data
    )
    if selected_chapter:
        chapter_file = os.path.join(chapters_dir, f"{selected_chapter}.txt")
        try:
            with open(chapter_file, "r", encoding="utf-8") as f:
                chapter_text = f.read()
            st.write("Current Scenes & Summary:")
            st.write(chapter_text)
            st.success("Scenes and summary saved.")
        except FileNotFoundError:
            st.error(
                "Scenes and summary file not found. Please generate scenes and summary first."
            )


def generate_chapter(config_data: dict, outline_data: list, project_path: str):
    """Generates a full chapter using the LLM based on selected settings."""
    selected_chapter = st.selectbox("Select chapter to generate:", outline_data)
    if selected_chapter:
        genre = config_data["genre"]
        tone = config_data["tone"]
        point_of_view = config_data["point_of_view"]
        writing_style = config_data["writing_style"]
        premise = config_data["premise"]

        synopsis_file = os.path.join(project_path, "synopsis", "synopsis.txt")
        try:
            with open(synopsis_file, "r", encoding="utf-8") as f:
                synopsis_text = f.read()
        except FileNotFoundError:
            synopsis_text = "No synopsis found."

        characters = load_characters(project_path)
        world_info = load_world_info(project_path)

        chapters_dir = os.path.join(project_path, "chapters")
        chapter_file = os.path.join(chapters_dir, f"{selected_chapter}.txt")
        try:
            with open(chapter_file, "r", encoding="utf-8") as f:
                scenes_and_summary = f.read()
        except FileNotFoundError:
            scenes_and_summary = "No scenes and summary found."

        # Generate chapter using the language model
        prompt = (
            f"Generate a full chapter based on the following:\n"
            f"Genre: {genre}\n"
            f"Tone: {tone}\n"
            f"Point of View: {point_of_view}\n"
            f"Writing Style: {writing_style}\n"
            f"Premise: {premise}\n"
            f"Synopsis: {synopsis_text}\n"
            f"Characters: {characters}\n"
            f"World Information: {world_info}\n"
            f"Outline: {selected_chapter}\n"
            f"Scenes & Summary: {scenes_and_summary}"
        )
        response = call_g4f_api(prompt)

        st.write("Generated Chapter:")
        st.write(response)

        with open(chapter_file, "w", encoding="utf-8") as f:
            f.write(response)
        st.success("Chapter saved to file.")


def edit_chapter(outline_data: list, project_path: str):
    """Edits the text of an existing chapter."""
    chapters_dir = os.path.join(project_path, "chapters")
    selected_chapter = st.selectbox("Select chapter to edit:", outline_data)
    if selected_chapter:
        chapter_file = os.path.join(chapters_dir, f"{selected_chapter}.txt")
        try:
            with open(chapter_file, "r", encoding="utf-8") as f:
                chapter_text = f.read()
            modified_chapter_text = st.text_area("Edit Chapter:", chapter_text)

            with open(chapter_file, "w", encoding="utf-8") as f:
                f.write(modified_chapter_text)
            st.success("Chapter updated.")

        except FileNotFoundError:
            st.error("Chapter file not found. Please generate a chapter first.")


def critique_and_improve_chapter(outline_data: list, project_path: str):
    """Uses the language model to provide a critique and improvement suggestions
    for the selected chapter."""
    chapters_dir = os.path.join(project_path, "chapters")
    selected_chapter = st.selectbox(
        "Select chapter to critique and improve:", outline_data
    )
    if selected_chapter:
        chapter_file = os.path.join(chapters_dir, f"{selected_chapter}.txt")
        try:
            with open(chapter_file, "r", encoding="utf-8") as f:
                chapter_text = f.read()

            prompt = f"Critique and improve the following chapter:\n{chapter_text}"
            response = call_g4f_api(prompt)

            st.write("Critique and Improvement Suggestions:")
            st.write(response)

        except FileNotFoundError:
            st.error("Chapter file not found. Please generate a chapter first.")


def save_chapter(outline_data: list, project_path: str):
    """Saves the current chapter - could be automated to save on edits."""
    chapters_dir = os.path.join(project_path, "chapters")
    selected_chapter = st.selectbox("Select chapter to save:", outline_data)
    if selected_chapter:
        chapter_file = os.path.join(chapters_dir, f"{selected_chapter}.txt")
        try:
            with open(chapter_file, "r", encoding="utf-8") as f:
                chapter_text = f.read()
            st.write("Current Chapter:")
            st.write(chapter_text)
            st.success("Chapter saved.")
        except FileNotFoundError:
            st.error("Chapter file not found. Please generate a chapter first.")


def load_characters(project_path: str):
    """Helper function to load character data."""
    characters_dir = os.path.join(project_path, "characters")
    characters = []
    for filename in os.listdir(characters_dir):
        if filename.endswith(".json"):
            characters.append(filename[:-5])
    return characters


def load_world_info(project_path: str):
    """Helper function to load world information."""
    world_file = os.path.join(project_path, "world", "world.json")
    try:
        with open(world_file, "r", encoding="utf-8") as f:
            world_data = json.load(f)
            return world_data.get("world_info", "")
    except FileNotFoundError:
        return ""
