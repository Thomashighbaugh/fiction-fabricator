# /home/tlh/refactored_gui_fict_fab/app.py
import streamlit as st
import asyncio
import os
import sys

# Add the parent directory of 'llm' to the Python path
llm_parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "llm"))
if llm_parent_dir not in sys.path:
    sys.path.insert(0, llm_parent_dir)

# Ensure components are importable after moving app.py to root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlit_app.components.book_spec_view import book_spec_display
from streamlit_app.components.plot_outline_view import plot_outline_display
from streamlit_app.components.chapter_outline_view import chapter_outlines_display
from streamlit_app.components.scene_outline_view import scene_outlines_display
from streamlit_app.components.scene_part_view import scene_part_display
from streamlit_app.components.book_text_view import book_text_display

from core.content_generation.book_spec_generator import BookSpecGenerator
from core.content_generation.plot_outline_generator import PlotOutlineGenerator
from core.content_generation.chapter_outline_generator import ChapterOutlineGenerator
from core.content_generation.scene_outline_generator import SceneOutlineGenerator
from core.content_generation.scene_part_generator import ScenePartGenerator
from core.content_generation.book_assembler import BookAssembler
from core.project_manager import ProjectManager  # import statement here
from llm.prompt_manager.prompt_manager import (
    DynamicPromptManager,
)  # changed import here
from llm.llm_client import OpenAILLMClient  # Changed to OpenAILLMClient
from utils.config import config
from core.book_spec import BookSpec
from core.plot_outline import PlotOutline, ChapterOutline, SceneOutline
from utils.logger import logger


def main():
    """Main function to run the Streamlit Fiction Fabricator application."""
    st.set_page_config(
        page_title="Fiction Fabricator",
        page_icon="🕉️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("Fiction Fabricator")

    # --- Initialize Session State ---
    if "openai_client" not in st.session_state:  # Renamed client
        st.session_state.openai_client = OpenAILLMClient()  # Changed client class
    if "prompt_manager" not in st.session_state:
        st.session_state.prompt_manager = DynamicPromptManager()  # changed class here
    if "book_spec_generator" not in st.session_state:
        st.session_state.book_spec_generator = BookSpecGenerator(
            st.session_state.prompt_manager, config.get_ollama_model_name()
        )
    if "plot_outline_generator" not in st.session_state:
        st.session_state.plot_outline_generator = PlotOutlineGenerator(
            st.session_state.prompt_manager, config.get_ollama_model_name()
        )
    if "chapter_outline_generator" not in st.session_state:
        st.session_state.chapter_outline_generator = ChapterOutlineGenerator(
            st.session_state.prompt_manager, config.get_ollama_model_name()
        )
    if "scene_outline_generator" not in st.session_state:
        st.session_state.scene_outline_generator = SceneOutlineGenerator(
            st.session_state.prompt_manager, config.get_ollama_model_name()
        )
    if "scene_part_generator" not in st.session_state:
        st.session_state.scene_part_generator = ScenePartGenerator(
            st.session_state.prompt_manager, config.get_ollama_model_name()
        )
    if "book_assembler" not in st.session_state:
        st.session_state.book_assembler = BookAssembler()
    if "project_manager" not in st.session_state:
        st.session_state.project_manager = ProjectManager()
    if "available_models" not in st.session_state:
        # Model listing no longer supported with openai, use default from config
        st.session_state.available_models = [config.get_ollama_model_name()]
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = config.get_ollama_model_name()
    st.session_state.story_idea = st.session_state.get("story_idea", "")
    st.session_state.book_spec = st.session_state.get("book_spec", None)
    st.session_state.plot_outline = st.session_state.get("plot_outline", None)
    st.session_state.chapter_outlines = st.session_state.get("chapter_outlines", [])
    st.session_state.scene_outlines = st.session_state.get("scene_outlines", {})
    st.session_state.scene_parts = st.session_state.get("scene_parts", {})
    st.session_state.project_name = st.session_state.get("project_name", "")
    st.session_state.num_chapters = st.session_state.get("num_chapters", 10)
    st.session_state.max_scenes_per_chapter = st.session_state.get(
        "max_scenes_per_chapter", 3
    )
    st.session_state.scene_parts_text = st.session_state.get("scene_parts_text", {})
    st.session_state.book_text = st.session_state.get("book_text", None)
    st.session_state.project_error = st.session_state.get(
        "project_error", None
    )  # Add project error

    # --- Sidebar ---
    with st.sidebar:
        st.header("Settings & Project")

        # **Model Selection (MANDATORY FIRST STEP)**
        # Removed model selection dropdown as list_models is not supported, using config model
        st.write(f"**Selected Model:** `{st.session_state.selected_model}`")

        # **Project Management (Available after Model Selection)**
        if (
            st.session_state.selected_model
        ):  # Only show project options if model is selected
            st.sidebar.subheader("Project Management")
            project_dir = config.get_project_directory()
            project_files = [
                f[:-5] for f in os.listdir(project_dir) if f.endswith(".json")
            ]
            project_options = ["New Project"] + project_files
            selected_project = st.selectbox(
                "Select Project", project_options, key="project_selectbox"
            )

            if selected_project == "New Project":
                project_name = st.text_input(
                    "New Project Name", value="", key="new_project_name_input"
                )
            else:
                project_name = selected_project

            st.session_state.project_name = st.text_input(
                "Project Name", value=project_name
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save Project", key="save_project_button"):
                    if st.session_state.project_name:
                        try:
                            st.session_state.project_manager.save_project(
                                st.session_state.project_name,
                                st.session_state.story_idea,
                                st.session_state.book_spec,
                                st.session_state.plot_outline,
                                st.session_state.chapter_outlines,
                                st.session_state.scene_outlines,
                                st.session_state.scene_parts,
                                st.session_state.scene_parts_text,
                                st.session_state.book_text,
                            )
                            st.success(
                                f"Project '{st.session_state.project_name}' saved!"
                            )
                            st.session_state.project_name = project_name
                            st.session_state.project_error = (
                                None  # Clear any prior errors
                            )
                        except (IOError, TypeError, ValueError) as e:
                            st.session_state.project_error = (
                                f"Error saving project: {e}"  # Save the error in session state
                            )
                    else:
                        st.warning("Please enter a project name to save.")
            with col2:
                if st.button("Load Project", key="load_project_button"):
                    if (
                        st.session_state.project_name
                        and st.session_state.project_name != "New Project"
                    ):
                        try:
                            # **AGGRESSIVELY CLEAR book_spec BEFORE LOADING**
                            st.session_state.book_spec = None

                            loaded_data = st.session_state.project_manager.load_project(
                                st.session_state.project_name
                            )
                            if loaded_data:
                                st.session_state.project_name = project_name
                                st.session_state.story_idea = loaded_data.get(
                                    "story_idea", ""
                                )
                                st.session_state.book_spec = (
                                    BookSpec(**loaded_data["book_spec"])
                                    if loaded_data.get("book_spec")
                                    else None
                                )
                                st.session_state.plot_outline = (
                                    PlotOutline(**loaded_data["plot_outline"])
                                    if loaded_data.get("plot_outline")
                                    else None
                                )
                                st.session_state.chapter_outlines = [
                                    ChapterOutline(**co)
                                    for co in (loaded_data.get("chapter_outlines") or [])
                                ]
                                scene_outlines_data = loaded_data.get(
                                    "scene_outlines", {}
                                )
                                st.session_state.scene_outlines = {
                                    int(chapter_num): [
                                        SceneOutline(**so) for so in scene_outlines
                                    ]
                                    for chapter_num, scene_outlines in (
                                        scene_outlines_data or {}
                                    ).items()
                                }
                                st.session_state.scene_parts = loaded_data.get(
                                    "scene_parts", {}
                                )
                                st.session_state.scene_parts_text = loaded_data.get(
                                    "scene_parts_text", {}
                                )
                                st.session_state.book_text = loaded_data.get(
                                    "book_text", None
                                )
                                st.success(
                                    f"Project '{st.session_state.project_name}' loaded!"
                                )
                                st.session_state.project_error = (
                                    None  # Clear any prior errors
                                )
                            else:
                                st.warning(
                                    f"No project data loaded for '{st.session_state.project_name}'."
                                )
                        except FileNotFoundError:
                            st.error(
                                f"Project file '{st.session_state.project_name}.json' not found."
                            )
                            st.session_state.project_error = f"Project file '{st.session_state.project_name}.json' not found."
                        except Exception as e:
                            st.error(f"Error loading project: {e}")
                            st.session_state.project_error = f"Error loading project: {e}"
                    else:
                        st.warning("Please enter a project name to load.")

    # --- Main Panel ---
    if (
        st.session_state.selected_model
    ):  # Only show workflow if model is selected
        col_workflow, col_display = st.columns([1, 1], gap="large")

        with col_workflow:
            st.header("Novel Generation Workflow")

            # 0. Display Project Error, if any
            if st.session_state.project_error:
                st.error(st.session_state.project_error)

            # 1. Story Idea
            with st.container():
                st.subheader("1. Story Idea")
                st.session_state.story_idea = st.text_area(
                    "Enter your story idea:",
                    value=st.session_state.story_idea,
                    height=100,
                    key="story_idea_textarea",
                    on_change=None,  # removed the callback here
                )

                # Autogenerate Book Spec
                if st.session_state.story_idea and not st.session_state.book_spec:
                    with st.spinner("Generating Book Specification..."):
                        generated_spec = asyncio.run(
                            st.session_state.book_spec_generator.generate(
                                st.session_state.story_idea, st.session_state.project_name
                            )
                        )
                    if generated_spec:
                        st.session_state.book_spec = generated_spec
                        # Autosave project after generation
                        st.session_state.project_manager.save_project(
                            st.session_state.project_name,
                            st.session_state.story_idea,
                            st.session_state.book_spec,
                            st.session_state.plot_outline,
                            st.session_state.chapter_outlines,
                            st.session_state.scene_outlines,
                            st.session_state.scene_parts,
                            st.session_state.scene_parts_text,
                            st.session_state.book_text,
                        )
                        st.success(
                            "Book Specification Generated and Project Autosaved!"
                        )
                        st.rerun()  # Refresh to show the generated spec
                    else:
                        st.error("Failed to generate Book Specification.")

            # 2. Book Specification
            with st.container():
                book_spec_display(
                    st.session_state.book_spec, st.session_state.book_spec_generator
                )

            # 3. Plot Outline
            if st.session_state.book_spec:
                with st.container():
                    plot_outline_display(
                        st.session_state.plot_outline,
                        st.session_state.plot_outline_generator,
                    )

            # 4. Chapter Outlines
            if st.session_state.plot_outline:
                with st.container():
                    chapter_outlines_display(
                        st.session_state.chapter_outlines,
                        st.session_state.chapter_outline_generator,
                    )

            # 5. Scene Outlines
            if st.session_state.chapter_outlines:
                with st.container():
                    scene_outlines_display(
                        st.session_state.scene_outlines,
                        st.session_state.scene_outline_generator,
                    )

            # 6. Scene Parts
            if st.session_state.scene_outlines:
                with st.container():
                    scene_part_display(
                        st.session_state.scene_parts_text,  # Corrected argument order
                        st.session_state.scene_part_generator,
                        st.session_state.book_spec,
                        st.session_state.chapter_outlines,
                        st.session_state.scene_outlines,
                    )

            # 7. Assemble Book Text
            if st.session_state.scene_parts_text:
                with st.container():
                    st.subheader("7. Assemble Book Text")
                    if st.button(
                        "Assemble Book Text",
                        disabled=not st.session_state.scene_parts_text,
                        key="assemble_book_button",
                    ):
                        with st.spinner("Assembling Book Text..."):
                            st.session_state.book_text = (
                                st.session_state.book_assembler.assemble_book_text(
                                    st.session_state.scene_parts_text
                                )
                            )
                        if st.session_state.book_text:
                            st.success("Book text assembled!")
                            st.download_button(
                                label="Download Book Text",
                                data=st.session_state.book_text,
                                file_name="book_text.txt",
                                mime="text/plain",
                            )
                        else:
                            st.error("Failed to assemble book text.")

        with col_display:
            st.header("Project Data Display")
            # 0. Display Project Error, if any
            if st.session_state.project_error:
                st.error(st.session_state.project_error)

            st.subheader("Story Idea")
            st.write(st.session_state.story_idea)

            if st.session_state.book_spec:
                book_spec_display(
                    st.session_state.book_spec, st.session_state.book_spec_generator
                )
            if st.session_state.plot_outline:
                plot_outline_display(
                    st.session_state.plot_outline,
                    st.session_state.plot_outline_generator,
                )
            if st.session_state.chapter_outlines:
                chapter_outlines_display(
                    st.session_state.chapter_outlines,
                    st.session_state.chapter_outline_generator,
                )
            if st.session_state.scene_outlines:
                scene_outlines_display(
                    st.session_state.scene_outlines,
                    st.session_state.scene_outline_generator,
                )
            if st.session_state.scene_parts_text:
                scene_part_display( # Corrected argument order
                    st.session_state.scene_parts_text,
                    st.session_state.scene_part_generator,
                    st.session_state.book_spec,
                    st.session_state.chapter_outlines,
                    st.session_state.scene_outlines,
                )
            if st.session_state.book_text:
                book_text_display(st.session_state.book_text)
    else:  # If no model selected, display message
        st.warning("Please select an Ollama model in the sidebar to begin.")


if __name__ == "__main__":
    main()