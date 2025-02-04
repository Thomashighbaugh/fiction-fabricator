import streamlit as st
import json
from typing import List

from core.book_spec import BookSpec
from core.plot_outline import ChapterOutline, PlotOutline, SceneOutline
from core.content_generator import ContentGenerator
from core.project_manager import ProjectManager
from llm.llm_client import OllamaClient
from llm.prompt_manager import PromptManager
from utils.config import config
from utils.logger import logger
from pydantic import ValidationError


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
        st.session_state.project_manager = ProjectManager()
    if "available_models" not in st.session_state:
        st.session_state.available_models = st.session_state.ollama_client.list_models() or []
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = config.get_ollama_model_name()
    if "story_idea" not in st.session_state:
        st.session_state.story_idea = ""
    if "book_spec" not in st.session_state:
        st.session_state.book_spec = None
    if "plot_outline" not in st.session_state:
        st.session_state.plot_outline = None
    if "chapter_outlines" not in st.session_state:
        st.session_state.chapter_outlines = None
    if "scene_outlines" not in st.session_state:
        st.session_state.scene_outlines = {}
    if "scene_parts" not in st.session_state:
        st.session_state.scene_parts = {}
    if "project_name" not in st.session_state:
        st.session_state.project_name = ""
    if "num_chapters" not in st.session_state:
        st.session_state.num_chapters = 10
    if "num_scenes_per_chapter" not in st.session_state:
        st.session_state.num_scenes_per_chapter = 3

    # --- Sidebar for Settings and Project Management ---
    with st.sidebar:
        st.header("Settings & Project")

        # Model Selection
        model_options = st.session_state.available_models
        if not model_options:
            st.warning("No models found on local Ollama instance. Ensure Ollama is running and models are pulled.")
            model_options = [st.session_state.selected_model]
        st.session_state.selected_model = st.selectbox(
            "Select Ollama Model",
            model_options,
            index=model_options.index(st.session_state.selected_model) if st.session_state.selected_model in model_options else 0,
        )

        st.sidebar.subheader("Project Management") # Fixed the error here using st.sidebar.subheader
        st.session_state.project_name = st.text_input("Project Name", st.session_state.project_name)

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
                    except Exception as e:
                        st.error(f"Error saving project: {e}")
                else:
                    st.warning("Please enter a project name to save.")
        with col2:
            if st.button("Load Project"):
                if st.session_state.project_name:
                    try:
                        loaded_data = st.session_state.project_manager.load_project(st.session_state.project_name)
                        if loaded_data:
                            st.session_state.book_spec = loaded_data.get('book_spec')
                            st.session_state.plot_outline = loaded_data.get('plot_outline')
                            st.session_state.chapter_outlines = loaded_data.get('chapter_outlines')
                            st.session_state.scene_outlines = loaded_data.get('scene_outlines')
                            st.session_state.scene_parts = loaded_data.get('scene_parts')
                            st.success(f"Project '{st.session_state.project_name}' loaded!")
                        else:
                            st.warning(f"No project data loaded for '{st.session_state.project_name}'.")
                    except FileNotFoundError:
                        st.error(f"Project file '{st.session_state.project_name}.json' not found.")
                    except Exception as e:
                        st.error(f"Error loading project: {e}")
                else:
                    st.warning("Please enter a project name to load.")

    # --- Main Panel for Content Generation Workflow ---
    st.header("Novel Generation Workflow")

    # 1. Story Idea Input
    st.subheader("1. Story Idea")
    st.session_state.story_idea = st.text_area("Enter your story idea:", value=st.session_state.story_idea, height=100)
    if st.button("Generate Book Specification", disabled=not st.session_state.story_idea):
        with st.spinner("Generating Book Specification..."):
            st.session_state.prompt_manager.book_spec = None
            st.session_state.prompt_manager.book_spec = BookSpec(**st.session_state.book_spec.dict()) if st.session_state.book_spec else None
            st.session_state.book_spec = st.session_state.content_generator.generate_book_spec(st.session_state.story_idea)
        if st.session_state.book_spec:
            st.success("Book Specification Generated!")
        else:
            st.error("Failed to generate Book Specification.")

    # 2. Book Specification Display and Edit
    if st.session_state.book_spec:
        st.subheader("2. Book Specification")
        with st.form("book_spec_form"):
            st.session_state.book_spec.title = st.text_input("Title", st.session_state.book_spec.title)
            st.session_state.book_spec.genre = st.text_input("Genre", st.session_state.book_spec.genre)
            st.session_state.book_spec.setting = st.text_area("Setting", st.session_state.book_spec.setting, height=100)
            st.session_state.book_spec.themes = [theme.strip() for theme in st.text_input("Themes (comma-separated)", ", ".join(st.session_state.book_spec.themes)).split(",")]
            st.session_state.book_spec.tone = st.text_input("Tone", st.session_state.book_spec.tone)
            st.session_state.book_spec.point_of_view = st.text_input("Point of View", st.session_state.book_spec.point_of_view)
            st.session_state.book_spec.characters = [char.strip() for char in st.text_area("Characters (comma-separated descriptions)", "\n".join(st.session_state.book_spec.characters), height=150).split("\n")]
            st.session_state.book_spec.premise = st.text_area("Premise", st.session_state.book_spec.premise, height=100)
            col1, col2 = st.columns([3, 1])
            with col1:
                st.form_submit_button("Save Book Specification")

            with col2:
               if st.form_submit_button("Enhance Book Specification", on_click=None, disabled=False):
                   with st.spinner("Enhancing Book Specification..."):
                       enhanced_spec = st.session_state.content_generator.enhance_book_spec(st.session_state.book_spec)
                       if enhanced_spec:
                           st.session_state.book_spec = enhanced_spec
                           st.success("Book Specification Enhanced!")
                       else:
                           st.error("Failed to enhance Book Specification.")

        st.json(st.session_state.book_spec.dict())

    # 3. Plot Outline Generation and Edit
    if st.session_state.book_spec:
        st.subheader("3. Plot Outline")
        if st.button("Generate Plot Outline", disabled=st.session_state.plot_outline is not None):
            with st.spinner("Generating Plot Outline..."):
                st.session_state.plot_outline = st.session_state.content_generator.generate_plot_outline(st.session_state.book_spec)
            if st.session_state.plot_outline:
                st.success("Plot Outline Generated!")
            else:
                 st.error("Failed to generate Plot Outline.")

        if st.session_state.plot_outline:
            with st.form("plot_outline_form"):
                st.session_state.plot_outline.act_one = st.text_area("Act One: Setup", st.session_state.plot_outline.act_one, height=150)
                st.session_state.plot_outline.act_two = st.text_area("Act Two: Confrontation", st.session_state.plot_outline.act_two, height=200)
                st.session_state.plot_outline.act_three = st.text_area("Act Three: Resolution", st.session_state.plot_outline.act_three, height=150)
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.form_submit_button("Save Plot Outline")
                with col2:
                    if st.form_submit_button("Enhance Plot Outline"):
                        with st.spinner("Enhancing Plot Outline..."):
                            enhanced_outline_raw = st.session_state.content_generator.enhance_plot_outline(
                                "\n".join([
                                    "Act One:\n" + st.session_state.plot_outline.act_one,
                                    "Act Two:\n" + st.session_state.plot_outline.act_two,
                                    "Act Three:\n" + st.session_state.plot_outline.act_three
                                ])
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
        num_chapters_input = st.number_input("Number of Chapters:", min_value=3, max_value=50, value=st.session_state.num_chapters, step=1)
        st.session_state.num_chapters = int(num_chapters_input)
        if st.button("Generate Chapter Outlines", disabled=st.session_state.chapter_outlines is not None):
            with st.spinner("Generating Chapter Outlines..."):
                st.session_state.chapter_outlines = st.session_state.content_generator.generate_chapter_outlines(
                    st.session_state.plot_outline, st.session_state.num_chapters
                )
            if st.session_state.chapter_outlines:
                 st.success("Chapter Outlines Generated!")
            else:
                st.error("Failed to generate Chapter Outlines.")

        if st.session_state.chapter_outlines:
            with st.form("chapter_outlines_form"):
                edited_chapter_outlines = []
                for i, chapter_outline in enumerate(st.session_state.chapter_outlines):
                    edited_summary = st.text_area(f"Chapter {i+1} Outline", chapter_outline.summary, height=100, key=f"chapter_{i}_outline")
                    edited_chapter_outlines.append(ChapterOutline(chapter_number=i+1, summary=edited_summary))
                st.session_state.chapter_outlines = edited_chapter_outlines

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.form_submit_button("Save Chapter Outlines")
                with col2:
                    if st.form_submit_button("Enhance Chapter Outlines"):
                         with st.spinner("Enhancing Chapter Outlines..."):
                            enhanced_chapter_outlines = st.session_state.content_generator.enhance_chapter_outlines(
                                st.session_state.chapter_outlines
                            )
                            if enhanced_chapter_outlines:
                                st.session_state.chapter_outlines = enhanced_chapter_outlines
                                st.success("Chapter Outlines Enhanced!")
                            else:
                                st.error("Failed to enhance Chapter Outlines.")

            if st.session_state.chapter_outlines:
                st.write("Chapter Outlines:")
                for chapter_outline in st.session_state.chapter_outlines:
                    st.markdown(f"**Chapter {chapter_outline.chapter_number}:**")
                    st.text(chapter_outline.summary)

    # 5. Scene Outline Generation and Edit (First Chapter only for now - expandable later)
    if st.session_state.chapter_outlines:
        st.subheader("5. Scene Outlines (Chapter 1)")
        num_scenes_input = st.number_input("Scenes per Chapter 1:", min_value=1, max_value=10, value=st.session_state.num_scenes_per_chapter, step=1)
        st.session_state.num_scenes_per_chapter = int(num_scenes_input)

        chapter_one_outline = st.session_state.chapter_outlines[0]

        if st.button("Generate Scene Outlines (Chapter 1)", disabled=st.session_state.scene_outlines.get(1) is not None):
            with st.spinner("Generating Scene Outlines for Chapter 1..."):
                scene_outlines_chapter_1 = st.session_state.content_generator.generate_scene_outlines(
                    chapter_one_outline, st.session_state.num_scenes_per_chapter
                )
                if scene_outlines_chapter_1:
                    st.session_state.scene_outlines[1] = scene_outlines_chapter_1
                    st.success("Scene Outlines Generated for Chapter 1!")
                else:
                    st.error("Failed to generate Scene Outlines for Chapter 1.")

        if st.session_state.scene_outlines.get(1):
            with st.form("scene_outlines_chapter_1_form"):
                edited_scene_outlines_chapter_1 = []
                for i, scene_outline in enumerate(st.session_state.scene_outlines[1]):
                    edited_summary = st.text_area(f"Scene {i+1} Outline", scene_outline.summary, height=80, key=f"scene_1_{i}_outline")
                    edited_scene_outlines_chapter_1.append(SceneOutline(scene_number=i+1, summary=edited_summary))
                st.session_state.scene_outlines[1] = edited_scene_outlines_chapter_1

                col1, col2 = st.columns([3, 1])
                with col1:
                     st.form_submit_button("Save Scene Outlines (Chapter 1)")
                with col2:
                     if st.form_submit_button("Enhance Scene Outlines (Chapter 1)"):
                        with st.spinner("Enhancing Scene Outlines for Chapter 1..."):
                            enhanced_scene_outlines_chapter_1 = st.session_state.content_generator.enhance_scene_outlines(
                                st.session_state.scene_outlines[1]
                            )
                            if enhanced_scene_outlines_chapter_1:
                                st.session_state.scene_outlines[1] = enhanced_scene_outlines_chapter_1
                                st.success("Scene Outlines Enhanced for Chapter 1!")
                            else:
                                st.error("Failed to enhance Scene Outlines for Chapter 1.")

            if st.session_state.scene_outlines.get(1):
                st.write("Scene Outlines for Chapter 1:")
                for scene_outline in st.session_state.scene_outlines[1]:
                    st.markdown(f"**Scene {scene_outline.scene_number}:**")
                    st.text(scene_outline.summary)


if __name__ == "__main__":
    main()