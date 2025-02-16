# streamlit_app.py
import random
import os

import streamlit as st
from pydantic import ValidationError

from core.book_spec import BookSpec
from core.plot_outline import ChapterOutline, SceneOutline
from core.content_generator import ContentGenerator
from core import project_manager
from llm.llm_client import OllamaClient
from llm.prompt_manager import PromptManager
from utils.config import config


def main():
    """
    Main function to run the Streamlit Fiction Fabricator application.

    Sets up the Streamlit interface, handles user interactions, and orchestrates
    the novel generation process using backend modules.
    """
    st.title("Fiction Fabricator")

    # Initialize session state variables
    if "ollama_client" not in st.session_state:
        st.session_state.ollama_client = OllamaClient()
    if "prompt_manager" not in st.session_state:
        st.session_state.prompt_manager = PromptManager()
    if "content_generator" not in st.session_state:
        st.session_state.content_generator = ContentGenerator(
            st.session_state.ollama_client, st.session_state.prompt_manager
        )
    if "project_manager" not in st.session_state:
        st.session_state.project_manager = project_manager.ProjectManager()
    if "available_models" not in st.session_state:
        st.session_state.available_models = (
            st.session_state.ollama_client.list_models() or []
        )
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = config.get_ollama_model_name()
    if "story_idea" not in st.session_state:
        st.session_state.story_idea = ""
    if "book_spec" not in st.session_state:
        st.session_state.book_spec = None
    if "plot_outline" not in st.session_state:
        st.session_state.plot_outline = None
    if "chapter_outlines" not in st.session_state:
        st.session_state.chapter_outlines = []  # Initialize as an empty list
    if "scene_outlines" not in st.session_state:
        st.session_state.scene_outlines = {}
    if "scene_parts" not in st.session_state:
        st.session_state.scene_parts = {}
    if "project_name" not in st.session_state:
        st.session_state.project_name = ""
    if "num_chapters" not in st.session_state:
        st.session_state.num_chapters = 10
    if "max_scenes_per_chapter" not in st.session_state:
        st.session_state.max_scenes_per_chapter = 3

    # --- Sidebar for Settings and Project Management ---
    with st.sidebar:
        st.header("Settings & Project")

        # Model Selection
        model_options = st.session_state.available_models
        if not model_options:
            st.warning(
                "No models found on local Ollama instance. Ensure Ollama is running and models are pulled."
            )
            model_options = [st.session_state.selected_model]
        st.session_state.selected_model = st.selectbox(
            "Select Ollama Model",
            model_options,
            index=model_options.index(st.session_state.selected_model)
            if st.session_state.selected_model in model_options
            else 0,
        )

        st.sidebar.subheader("Project Management")

        # Project Selection
        project_dir = config.get_project_directory()
        project_files = [
            f[:-5] for f in os.listdir(project_dir) if f.endswith(".json")
        ]  # project name equals file name without extension
        project_options = ["New Project"] + project_files
        selected_project = st.selectbox("Select Project", project_options)

        new_project_name = ""
        if selected_project == "New Project":
            new_project_name = st.text_input("New Project Name", value=st.session_state.project_name)
            project_name = new_project_name
        else:
            project_name = selected_project
            
        st.session_state.project_name = st.text_input("Project Name", value=project_name)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save Project"):
                if st.session_state.project_name:
                    try:
                        st.session_state.project_manager.save_project(
                            st.session_state.project_name,
                            st.session_state.book_spec,
                            st.session_state.plot_outline,
                            st.session_state.chapter_outlines,
                            st.session_state.scene_outlines,
                            st.session_state.scene_parts,
                        )
                        st.success(f"Project '{st.session_state.project_name}' saved!")
                    except (IOError, ValueError, ValidationError) as e:
                        st.error(f"Error saving project: {e}")
                else:
                    st.warning("Please enter a project name to save.")
        with col2:
            if st.button("Load Project"):
                if st.session_state.project_name:
                    try:
                        loaded_data = st.session_state.project_manager.load_project(
                            st.session_state.project_name
                        )
                        if loaded_data:
                            # Convert loaded data to proper objects
                            st.session_state.book_spec = (
                                BookSpec(**loaded_data["book_spec"]) if loaded_data.get("book_spec") else None
                            )
                            st.session_state.plot_outline = (
                                PlotOutline(**loaded_data["plot_outline"]) if loaded_data.get("plot_outline") else None
                            )
                            st.session_state.chapter_outlines = [
                                ChapterOutline(**co) for co in loaded_data.get("chapter_outlines", [])
                            ]
                            st.session_state.scene_outlines = {
                                int(chapter_num): [SceneOutline(**so) for so in scene_outlines]
                                for chapter_num, scene_outlines in (loaded_data.get("scene_outlines", {})).items()
                            }
                            st.session_state.scene_parts = loaded_data.get("scene_parts", {})
                            st.success(f"Project '{st.session_state.project_name}' loaded!")
                        else:
                            st.warning(
                                f"No project data loaded for '{st.session_state.project_name}'."
                            )
                    except FileNotFoundError:
                        st.error(
                            f"Project file '{st.session_state.project_name}.json' not found."
                        )
                    except (IOError, ValueError, ValidationError) as e:
                        st.error(f"Error loading project: {e}")
                else:
                    st.warning("Please enter a project name to load.")

    # --- Main Panel for Content Generation Workflow ---
    st.header("Novel Generation Workflow")

    # 1. Story Idea Input
    st.subheader("1. Story Idea")
    st.session_state.story_idea = st.text_area(
        "Enter your story idea:", value=st.session_state.story_idea, height=100
    )
    if st.button(
        "Generate Book Specification", disabled=not st.session_state.story_idea
    ):
        with st.spinner("Generating Book Specification..."):
            st.session_state.prompt_manager.book_spec = None
            if st.session_state.book_spec:
                st.session_state.prompt_manager.book_spec = BookSpec(
                    **st.session_state.book_spec.model_dump()
                )
            st.session_state.book_spec = (
                st.session_state.content_generator.generate_book_spec(
                    st.session_state.story_idea
                )
            )
        if st.session_state.book_spec:
            st.success("Book Specification Generated!")
        else:
            st.error("Failed to generate Book Specification.")

    # 2. Book Specification Display and Edit
    if st.session_state.book_spec:
        st.subheader("2. Book Specification")
        with st.form("book_spec_form"):
            title = st.text_input(
                "Title", value=st.session_state.book_spec.title, key="title_input"
            )
            genre = st.text_input(
                "Genre", value=st.session_state.book_spec.genre, key="genre_input"
            )
            setting = st.text_area(
                "Setting",
                value=st.session_state.book_spec.setting,
                height=100,
                key="setting_input",
            )
            themes_str = st.text_input(
                "Themes (comma-separated)",
                value=", ".join(st.session_state.book_spec.themes),
                key="themes_input",
            )
            tone = st.text_input(
                "Tone", value=st.session_state.book_spec.tone, key="tone_input"
            )
            point_of_view = st.text_input(
                "Point of View",
                value=st.session_state.book_spec.point_of_view,
                key="pov_input",
            )
            characters_str = st.text_area(
                "Characters (comma-separated descriptions)",
                value="\n".join(st.session_state.book_spec.characters),
                height=150,
                key="characters_input",
            )
            premise = st.text_area(
                "Premise",
                value=st.session_state.book_spec.premise,
                height=100,
                key="premise_input",
            )
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.form_submit_button("Save Book Specification"):
                    # Update only if book_spec exists to prevent errors
                    if st.session_state.book_spec:
                        st.session_state.book_spec.title = title
                        st.session_state.book_spec.genre = genre
                        st.session_state.book_spec.setting = setting
                        st.session_state.book_spec.themes = [
                            t.strip() for t in themes_str.split(",")
                        ]
                        st.session_state.book_spec.tone = tone
                        st.session_state.book_spec.point_of_view = point_of_view
                        st.session_state.book_spec.characters = [
                            c.strip() for c in characters_str.split("\n")
                        ]
                        st.session_state.book_spec.premise = premise
                        st.success("Book Specification Saved!")

            with col2:
                if st.form_submit_button(
                    "Enhance Book Specification", on_click=None, disabled=False
                ):
                    with st.spinner("Enhancing Book Specification..."):
                        enhanced_spec = (
                            st.session_state.content_generator.enhance_book_spec(
                                st.session_state.book_spec
                            )
                        )
                        if enhanced_spec:
                            # Update the existing BookSpec in session state with the enhanced values
                            # Ensure that enhanced_spec.characters is a list of strings
                            if isinstance(enhanced_spec.characters, list):
                                st.session_state.book_spec.characters = [
                                    item.get("name", "")
                                    if isinstance(item, dict)
                                    else str(item)
                                    for item in enhanced_spec.characters
                                ]
                            else:
                                # Handle cases where enhanced_spec.characters is not a list
                                st.session_state.book_spec.characters = [
                                    str(enhanced_spec.characters)
                                ]

                            st.session_state.book_spec.title = enhanced_spec.title
                            st.session_state.book_spec.genre = enhanced_spec.genre
                            st.session_state.book_spec.setting = enhanced_spec.setting
                            st.session_state.book_spec.themes = enhanced_spec.themes
                            st.session_state.book_spec.tone = enhanced_spec.tone
                            st.session_state.book_spec.point_of_view = (
                                enhanced_spec.point_of_view
                            )
                            st.session_state.book_spec.premise = enhanced_spec.premise

                            st.success("Book Specification Enhanced!")
                        else:
                            st.error("Failed to enhance Book Specification.")

        if st.session_state.book_spec:
            st.json(
                st.session_state.book_spec.model_dump()
            )  # Use model_dump (Pydantic v2)
        else:
            st.write(
                "No Book Specification to display. Generate one using the Story Idea form."
            )

    # 3. Plot Outline Generation and Edit
    if (
        st.session_state.book_spec is not None
        and getattr(st.session_state.book_spec, "title", None) is not None
    ):  # and st.session_state.book_spec.title : #Checking if book spec is valid before rendering section
        st.subheader("3. Plot Outline")
        if st.button(
            "Generate Plot Outline", disabled=st.session_state.plot_outline is not None
        ):
            with st.spinner("Generating Plot Outline..."):
                st.session_state.plot_outline = (
                    st.session_state.content_generator.generate_plot_outline(
                        st.session_state.book_spec
                    )
                )
            if st.session_state.plot_outline:
                st.success("Plot Outline Generated!")
            else:
                st.error("Failed to generate Plot Outline.")

        if st.session_state.plot_outline:
            with st.form("plot_outline_form"):
                st.session_state.plot_outline.act_one = st.text_area(
                    "Act One: Setup",
                    st.session_state.plot_outline.act_one,
                    height=150,
                )
                st.session_state.plot_outline.act_two = st.text_area(
                    "Act Two: Confrontation",
                    st.session_state.plot_outline.act_two,
                    height=200,
                )
                st.session_state.plot_outline.act_three = st.text_area(
                    "Act Three: Resolution",
                    st.session_state.plot_outline.act_three,
                    height=150,
                )
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.form_submit_button("Save Plot Outline"):
                        st.success("Plot Outline Saved!")
                with col2:
                    if st.form_submit_button("Enhance Plot Outline"):
                        with st.spinner("Enhancing Plot Outline..."):
                            enhanced_outline_raw = (
                                st.session_state.content_generator.enhance_plot_outline(
                                    "\n".join(
                                        [
                                            "Act One:\n"
                                            + st.session_state.plot_outline.act_one,
                                            "Act Two:\n"
                                            + st.session_state.plot_outline.act_two,
                                            "Act Three:\n"
                                            + st.session_state.plot_outline.act_three,
                                        ]
                                    )
                                )
                            )
                            if enhanced_outline_raw:
                                st.session_state.plot_outline = enhanced_outline_raw
                                st.success("Plot Outline Enhanced!")
                            else:
                                st.error("Failed to enhance Plot Outline.")
            st.write("Plot Outline:")
            st.text(
                f"Act One: {st.session_state.plot_outline.act_one}\n\n"
                f"Act Two: {st.session_state.plot_outline.act_two}\n\n"
                f"Act Three: {st.session_state.plot_outline.act_three}"
            )

    # 4. Chapter Outline Generation and Edit
    if st.session_state.plot_outline:
        st.subheader("4. Chapter Outlines")
        num_chapters_input = st.number_input(
            "Number of Chapters:",
            min_value=3,
            max_value=50,
            value=st.session_state.num_chapters,
            step=1,
        )
        st.session_state.num_chapters = int(num_chapters_input)
        if st.button(
            "Generate Chapter Outlines",
            disabled=st.session_state.chapter_outlines is not None
            and len(st.session_state.chapter_outlines) > 0,
        ):
            with st.spinner("Generating Chapter Outlines..."):
                st.session_state.chapter_outlines = (
                    st.session_state.content_generator.generate_chapter_outlines(
                        st.session_state.plot_outline, st.session_state.num_chapters
                    )
                )
            if st.session_state.chapter_outlines:
                st.success(
                    f"Chapter Outlines Generated for {len(st.session_state.chapter_outlines)} chapters!"
                )
            else:
                st.error("Failed to generate Chapter Outlines.")

        # Display, Edit and Enhance Chapter Outlines
        if st.session_state.chapter_outlines:
            # Initialize edited_chapter_outlines with the current state
            edited_chapter_outlines = st.session_state.chapter_outlines.copy()
            with st.form("chapter_outlines_form"):
                for i, chapter_outline in enumerate(edited_chapter_outlines):
                    st.markdown(f"**Chapter {chapter_outline.chapter_number}:**")
                    edited_summary = st.text_area(
                        "Summary",
                        chapter_outline.summary,
                        height=100,
                        key=f"chapter_{i}_summary",
                    )
                    edited_chapter_outlines[i] = ChapterOutline(
                        chapter_number=chapter_outline.chapter_number,
                        summary=edited_summary,
                    )

                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.form_submit_button("Save Chapter Outlines"):
                        st.session_state.chapter_outlines = edited_chapter_outlines
                        st.success("Chapter Outlines Saved!")
                with col2:
                    if st.form_submit_button("Enhance Chapter Outlines"):
                        with st.spinner("Enhancing Chapter Outlines..."):
                            enhanced_chapter_outlines = (
                                st.session_state.content_generator.enhance_chapter_outlines(
                                    edited_chapter_outlines
                                )
                            )
                        if enhanced_chapter_outlines:
                            st.session_state.chapter_outlines = (
                                enhanced_chapter_outlines
                            )
                            st.success("Chapter Outlines Enhanced!")
                        else:
                            st.error("Failed to enhance Chapter Outlines.")

            # Display Chapter Outlines outside the form
            for chapter_outline in st.session_state.chapter_outlines:
                st.markdown(f"**Chapter {chapter_outline.chapter_number}:**")
                st.write(chapter_outline.summary)

    # 5. Scene Outline Generation and Edit
    if st.session_state.chapter_outlines and len(st.session_state.chapter_outlines) > 0:
        st.subheader("5. Scene Outlines")
        max_scenes_input = st.number_input(
            "Maximum Scenes per Chapter:",
            min_value=3,
            max_value=10,
            value=st.session_state.max_scenes_per_chapter,
            step=1,
        )
        st.session_state.max_scenes_per_chapter = int(max_scenes_input)

        if st.button(
            "Generate Scene Outlines (All Chapters)",
            disabled=st.session_state.scene_outlines is not None
            and len(st.session_state.scene_outlines) > 0,
        ):
            with st.spinner("Generating Scene Outlines for All Chapters..."):
                st.session_state.scene_outlines = {}
                for chapter_outline in st.session_state.chapter_outlines:
                    num_scenes = random.randint(
                        2, st.session_state.max_scenes_per_chapter
                    )
                    scene_outlines = (
                        st.session_state.content_generator.generate_scene_outlines(
                            chapter_outline,
                            num_scenes
                        )
                    )
                    if scene_outlines:
                        st.session_state.scene_outlines[
                            chapter_outline.chapter_number
                        ] = scene_outlines
                st.success(
                    f"Scene Outlines Generated for All Chapters with random number of scenes between 2 and {st.session_state.max_scenes_per_chapter}!"
                )

        # Display and Edit Scene Outlines
        if st.session_state.scene_outlines:
            for chapter_number, scene_outlines in st.session_state.scene_outlines.items():
                with st.form(f"scene_outlines_chapter_{chapter_number}_form"):
                    st.markdown(f"**Chapter {chapter_number}**")
                    edited_scene_outlines = []
                    for i, scene_outline in enumerate(scene_outlines):
                        edited_summary = st.text_area(
                            f"Scene {i + 1} Outline",
                            scene_outline.summary,
                            height=80,
                            key=f"scene_{chapter_number}_{i}_outline",
                        )
                        edited_scene_outlines.append(
                            SceneOutline(scene_number=i + 1, summary=edited_summary)
                        )

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if st.form_submit_button(
                            f"Save Scene Outlines (Chapter {chapter_number})"
                        ):
                            st.session_state.scene_outlines[
                                chapter_number
                            ] = edited_scene_outlines
                            st.success(
                                f"Scene Outlines Saved for Chapter {chapter_number}!"
                            )
                    with col2:
                        if st.form_submit_button(
                            f"Enhance Scene Outlines (Chapter {chapter_number})"
                        ):
                            with st.spinner(
                                f"Enhancing Scene Outlines for Chapter {chapter_number}..."
                            ):
                                enhanced_scene_outlines = (
                                    st.session_state.content_generator.enhance_scene_outlines(
                                        edited_scene_outlines
                                    )
                                )
                                if enhanced_scene_outlines:
                                    st.session_state.scene_outlines[
                                        chapter_number
                                    ] = enhanced_scene_outlines
                                    st.success(
                                        f"Scene Outlines Enhanced for Chapter {chapter_number}!"
                                    )
                                else:
                                    st.error(
                                        f"Failed to enhance Scene Outlines for Chapter {chapter_number}."
                                    )

                # Display Scene Outlines outside the form
                for scene_outline in st.session_state.scene_outlines.get(
                    chapter_number, []
                ):
                    st.markdown(f"**Scene {scene_outline.scene_number}:**")
                    st.write(scene_outline.summary)


if __name__ == "__main__":
    main()