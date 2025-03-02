# /home/tlh/refactored_gui_fict_fab/app.py
import streamlit as st
import asyncio
import os
import sys

llm_parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "llm"))
if llm_parent_dir not in sys.path:
    sys.path.insert(0, llm_parent_dir)

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
from core.project_manager import ProjectManager
from llm.prompt_manager.prompt_manager import PromptManager  # Changed import here
from llm.llm_client import OpenAILLMClient
from utils.config import config
from core.book_spec import BookSpec
from core.plot_outline import PlotOutline, ChapterOutline, SceneOutline
from utils.logger import logger


def main():
    st.set_page_config(
        page_title="Fiction Fabricator",
        page_icon="🕉️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("Fiction Fabricator")

    if "openai_client" not in st.session_state:
        st.session_state.openai_client = OpenAILLMClient()
    if "prompt_manager" not in st.session_state:
        st.session_state.prompt_manager = PromptManager()  # Changed instantiation here
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
        st.session_state.available_models = (
            asyncio.run(st.session_state.openai_client.list_models()) or []
        )
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
    st.session_state.project_error = st.session_state.get("project_error", None)

    with st.sidebar:
        st.header("Settings & Project")

        model_options = st.session_state.available_models or [
            config.get_ollama_model_name()
        ]
        model_selectbox = st.selectbox(
            "Select Model (REQUIRED)",
            model_options,
            index=(
                model_options.index(st.session_state.selected_model)
                if st.session_state.selected_model in model_options
                else 0
            ),
            key="model_selectbox",
        )
        if model_selectbox != st.session_state.selected_model:
            st.session_state.selected_model = model_selectbox
            for generator_key in [
                "book_spec_generator",
                "plot_outline_generator",
                "chapter_outline_generator",
                "scene_outline_generator",
                "scene_part_generator",
            ]:
                if generator_key in st.session_state:
                    st.session_state[generator_key].model_name = (
                        st.session_state.selected_model
                    )
            st.rerun()
        st.write(f"**Selected Model:** `{st.session_state.selected_model}`")

        if st.session_state.selected_model:
            st.sidebar.subheader("Project Management")
            project_dir = config.get_project_directory()
            logger.debug(f"Project directory for listing files: {project_dir}")
            try:
                all_files_and_dirs = os.listdir(project_dir)
                logger.debug(
                    f"Items in project directory: {all_files_and_dirs}"
                )  # Log ALL items

                project_files = []
                for item_name in all_files_and_dirs:  # Iterate through item names
                    item_path = os.path.join(
                        project_dir, item_name
                    )  # Construct full item path
                    logger.debug(
                        f"Checking item: {item_name}, path: {item_path}"
                    )  # Log each item being checked

                    if os.path.isdir(item_path):  # Check if it's a directory
                        logger.debug(f"  - Is a directory")
                        project_json_filepath = os.path.join(
                            item_path, f"{item_name}.json"
                        )  # Construct project.json path
                        logger.debug(
                            f"  - Checking for project JSON file: {project_json_filepath}"
                        )  # Log json path

                        if os.path.isfile(
                            project_json_filepath
                        ):  # Check if project.json exists
                            logger.info(
                                f"  - Found project JSON file: {project_json_filepath}"
                            )  # Info log if found
                            project_files.append(
                                item_name
                            )  # Add project directory name
                        else:
                            logger.debug(
                                f"  - Project JSON file NOT found"
                            )  # Debug log if json not found
                    else:
                        logger.debug(
                            f"  - Not a directory (ignoring)"
                        )  # Debug log if not a directory

                logger.debug(
                    f"Filtered project files (subdirectories with project.json): {project_files}"
                )  # Log final list

            except FileNotFoundError:
                logger.warning(f"Project directory not found: {project_dir}")
                project_files = []
            except Exception as e:
                logger.error(f"Error listing project directory: {e}")
                project_files = []

            st.write(f"Project Files (from listdir): {project_files}")
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
                            st.session_state.project_error = None
                        except (IOError, TypeError, ValueError) as e:
                            st.session_state.project_error = (
                                f"Error saving project: {e}"
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
                                    for co in (
                                        loaded_data.get("chapter_outlines") or []
                                    )
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
                                st.session_state.project_error = None
                            else:
                                st.warning(
                                    f"No project data loaded (empty data) for '{st.session_state.project_name}'."
                                )
                                st.session_state.project_error = f"No project data loaded for '{st.session_state.project_name}' - empty data."
                        except FileNotFoundError as e:
                            st.error(
                                f"Project file '{st.session_state.project_name}.json' not found: {e}"
                            )
                            st.session_state.project_error = f"Project file '{st.session_state.project_name}.json' not found: {e}"
                        except json.JSONDecodeError as e:
                            st.error(f"Error decoding project JSON: {e}")
                            st.session_state.project_error = (
                                f"Error decoding project JSON: {e}"
                            )
                        except Exception as e:
                            st.error(f"General error loading project: {e}")
                            st.session_state.project_error = (
                                f"General error loading project: {e}"
                            )

    if st.session_state.selected_model:
        col_workflow, col_display = st.columns([1, 1], gap="large")

        with col_workflow:
            st.header("Novel Generation Workflow")

            if st.session_state.project_error:
                st.error(st.session_state.project_error)

            with st.container():
                st.subheader("1. Story Idea")
                st.session_state.story_idea = st.text_area(
                    "Enter your story idea:",
                    value=st.session_state.story_idea,
                    height=100,
                    key="story_idea_textarea",
                    on_change=None,
                )

                if st.session_state.story_idea and not st.session_state.book_spec:
                    with st.spinner("Generating Book Specification..."):
                        generated_spec = asyncio.run(
                            st.session_state.book_spec_generator.generate(
                                st.session_state.story_idea,
                                st.session_state.project_name,
                            )
                        )
                    if generated_spec:
                        st.session_state.book_spec = generated_spec
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
                        st.rerun()
                    else:
                        st.error("Failed to generate Book Specification.")

            with st.container():
                book_spec_display(
                    st.session_state.book_spec, st.session_state.book_spec_generator
                )

            if st.session_state.book_spec:
                with st.container():
                    plot_outline_display(
                        st.session_state.plot_outline,
                        st.session_state.plot_outline_generator,
                    )

            if st.session_state.plot_outline:
                with st.container():
                    chapter_outlines_display(
                        st.session_state.chapter_outlines,
                        st.session_state.chapter_outline_generator,
                    )

            if st.session_state.chapter_outlines:
                with st.container():
                    scene_outlines_display(
                        st.session_state.scene_outlines,
                        st.session_state.scene_outline_generator,
                    )

            if st.session_state.scene_outlines:
                with st.container():
                    scene_part_display(
                        st.session_state.scene_parts_text,
                        st.session_state.scene_part_generator,
                        st.session_state.book_spec,
                        st.session_state.chapter_outlines,
                        st.session_state.scene_outlines,
                    )

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
                scene_part_display(
                    st.session_state.scene_parts_text,
                    st.session_state.scene_part_generator,
                    st.session_state.book_spec,
                    st.session_state.chapter_outlines,
                    st.session_state.scene_outlines,
                )
            if st.session_state.book_text:
                book_text_display(st.session_state.book_text)
    else:
        st.warning("Please select an Ollama model in the sidebar to begin.")


if __name__ == "__main__":
    main()
