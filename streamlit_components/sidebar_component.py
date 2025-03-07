# streamlit_components/sidebar_component.py
import streamlit as st

from core.content_generator import ContentGenerator
from llm.llm_client import OllamaClient
from llm.prompt_manager import PromptManager
from utils.config import config
import asyncio
import os


def create_sidebar(session_state):
    """
    Creates and displays the sidebar in the Streamlit application with enhanced styling.

    Args:
        session_state: Streamlit session state object.
    """
    with st.sidebar:
        st.header("⚙️ Settings & Project")  # Added emoji and header styling
        model_options = session_state.available_models
        if not model_options:
            st.warning(
                "No models found on local Ollama instance. Ensure Ollama is running and models are pulled."
            )
            model_options = [session_state.selected_model]
        selected_model_index = (
            model_options.index(session_state.selected_model)
            if session_state.selected_model in model_options
            else 0
        )
        st.selectbox(  # Removed 'value' parameter for compatibility
            "Select Ollama Model",
            model_options,
            index=selected_model_index,
            key="model_selectbox",
        )
        if st.button("Change Model"):
            session_state.selected_model = (
                st.session_state.model_selectbox
            )  # Update session_state here on button click
            session_state.content_generator = ContentGenerator(
                session_state.prompt_manager, session_state.selected_model
            )
            st.rerun()
        st.caption(
            f"Selected Model: `{session_state.selected_model}`"
        )  # Changed to caption

        st.sidebar.subheader("Project Management")  # Subheader for project management
        project_dir = config.get_project_directory()
        project_files = [f[:-5] for f in os.listdir(project_dir) if f.endswith(".json")]
        project_options = ["New Project"] + project_files
        selected_project = st.selectbox("Select Project", project_options)

        if selected_project == "New Project":
            project_name = st.text_input(
                "Project Name",
                value="",
                key="project_name_input",
            )
            session_state.project_name = project_name
            session_state.new_project_requested = True
        else:
            session_state.project_name = selected_project
            session_state.new_project_requested = False

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Project"):  # Added emoji
                if session_state.project_name:
                    session_state.project_manager.save_project(
                        session_state.project_name,
                        story_idea=session_state.story_idea,
                        book_spec=session_state.book_spec,
                        plot_outline=session_state.plot_outline,
                        chapter_outlines=session_state.chapter_outlines,
                        chapter_outlines_27_method=session_state.chapter_outlines_27_method,
                        scene_outlines=session_state.scene_outlines,
                        scene_parts=session_state.scene_parts,
                    )
                    st.success(f"Project '{session_state.project_name}' saved!")
                else:
                    st.warning("Please enter a project name to save.")
        with col2:
            if st.button("Load Project"):  # Added emoji
                if session_state.project_name:
                    loaded_data = session_state.project_manager.load_project(
                        session_state.project_name
                    )
                    if loaded_data:
                        for key, value in loaded_data.items():
                            session_state[key] = value

                        session_state.book_spec = BookSpec(
                            **loaded_data.get("book_spec", {})
                        )
                        session_state.plot_outline = PlotOutline(
                            **loaded_data.get("plot_outline", {})
                        )
                        session_state.chapter_outlines_27_method = [
                            ChapterOutlineMethod(**co)
                            for co in loaded_data.get("chapter_outlines_27_method", [])
                        ]
                        session_state.project_loaded = True
                        st.success(f"Project '{session_state.project_name}' loaded!")
                    else:
                        st.warning(
                            f"No project data loaded for '{session_state.project_name}'."
                        )
                else:
                    st.warning("Please select or enter a project name to load.")
