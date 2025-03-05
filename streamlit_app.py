# streamlit_app.py

import random
import re
import os
import asyncio

import streamlit as st
from pydantic import ValidationError

from core.book_spec import BookSpec
from core.plot_outline import ChapterOutline, SceneOutline, PlotOutline
from core.content_generator import ContentGenerator
from core import project_manager
from llm.llm_client import OllamaClient
from llm.prompt_manager import PromptManager
from utils.config import config
from utils.logger import logger


def main():
    """
    Main function to run the Streamlit Fiction Fabricator application with asyncio.
    """
    st.title("Fiction Fabricator")

    # Initialize session state variables
    if "ollama_client" not in st.session_state:
        st.session_state.ollama_client = OllamaClient(timeout=None)
    if "prompt_manager" not in st.session_state:
        st.session_state.prompt_manager = PromptManager()
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = config.get_ollama_model_name()
    if (
        "content_generator" not in st.session_state
        or st.session_state.get("content_generator") is None
    ):
        st.session_state.content_generator = ContentGenerator(
            st.session_state.prompt_manager, st.session_state.selected_model
        )
    if "project_manager" not in st.session_state:
        st.session_state.project_manager = project_manager.ProjectManager()
    if "available_models" not in st.session_state:
        st.session_state.available_models = (
            asyncio.run(st.session_state.ollama_client.list_models()) or []
        )
    if "story_idea" not in st.session_state:
        st.session_state.story_idea = ""
    if "book_spec" not in st.session_state:
        st.session_state.book_spec = None
    if "plot_outline" not in st.session_state:
        st.session_state.plot_outline = PlotOutline()
    if "chapter_outlines" not in st.session_state:
        st.session_state.chapter_outlines = []
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
    if "current_chapter_index" not in st.session_state:
        st.session_state.current_chapter_index = 0
    if "initialized" not in st.session_state:
        st.session_state.initialized = True

    # Initialize act_one_text, act_two_text, and act_three_text here
    if "act_one_text" not in st.session_state:
        st.session_state.act_one_text = ""
    if "act_two_text" not in st.session_state:
        st.session_state.act_two_text = ""
    if "act_three_text" not in st.session_state:
        st.session_state.act_three_text = ""

    # --- Sidebar ---
    with st.sidebar:
        st.header("Settings & Project")
        model_options = st.session_state.available_models
        if not model_options:
            st.warning(
                "No models found on local Ollama instance. Ensure Ollama is running and models are pulled."
            )
            model_options = [st.session_state.selected_model]
        selected_model_index = (
            model_options.index(st.session_state.selected_model)
            if st.session_state.selected_model in model_options
            else 0
        )
        st.selectbox(
            "Select Ollama Model",
            model_options,
            index=selected_model_index,
            key="model_selectbox",
        )
        if st.button("Change Model"):
            st.session_state.selected_model = st.session_state.model_selectbox
            st.session_state.content_generator = ContentGenerator(
                st.session_state.prompt_manager, st.session_state.selected_model
            )
            st.rerun()
        st.write(f"**Selected Model:** `{st.session_state.selected_model}`")
        st.sidebar.subheader("Project Management")
        project_dir = config.get_project_directory()
        project_files = [f[:-5] for f in os.listdir(project_dir) if f.endswith(".json")]
        project_options = ["New Project"] + project_files
        selected_project = st.selectbox("Select Project", project_options)
        project_name = st.text_input(
            "Project Name",
            value=(
                st.session_state.project_name
                if selected_project != "New Project"
                else ""
            ),
        )
        st.session_state.project_name = project_name
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save Project"):
                if st.session_state.project_name:
                    st.session_state.project_manager.save_project(**st.session_state)
                    st.success(f"Project '{st.session_state.project_name}' saved!")
                else:
                    st.warning("Please enter a project name to save.")
        with col2:
            if st.button("Load Project"):
                if st.session_state.project_name:
                    loaded_data = st.session_state.project_manager.load_project(
                        st.session_state.project_name
                    )
                    if loaded_data:
                        for key, value in loaded_data.items():
                            st.session_state[key] = value
                        st.session_state.plot_outline = PlotOutline(
                            **loaded_data.get("plot_outline", {})
                        )
                        st.success(f"Project '{st.session_state.project_name}' loaded!")
                    else:
                        st.warning(
                            f"No project data loaded for '{st.session_state.project_name}'."
                        )
                else:
                    st.warning("Please enter a project name to load.")

    # --- Main Panel ---
    st.header("Novel Generation Workflow")

    # 1. Story Idea
    st.subheader("1. Story Idea")
    st.session_state.story_idea = st.text_area(
        "Enter your story idea:", value=st.session_state.story_idea, height=100
    )
    if st.button(
        "Generate Book Specification", disabled=not st.session_state.story_idea
    ):
        with st.spinner("Generating Book Specification..."):
            st.session_state.book_spec = asyncio.run(
                st.session_state.content_generator.generate_book_spec(
                    st.session_state.story_idea
                )
            )
        if st.session_state.book_spec:
            st.success("Book Specification Generated!")
            if st.session_state.project_name:
                st.session_state.project_manager.save_project(**st.session_state)
        else:
            st.error("Failed to generate Book Specification.")

    # 2. Book Specification
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
                    if st.session_state.project_name:
                        st.session_state.project_manager.save_project(
                            **st.session_state
                        )

            with col2:
                if st.form_submit_button("Enhance Book Specification"):

                    async def enhance_book_spec_callback():
                        with st.spinner("Enhancing Book Specification..."):
                            enhanced_spec = await st.session_state.content_generator.enhance_book_spec(
                                st.session_state.book_spec
                            )
                            if enhanced_spec:
                                if isinstance(enhanced_spec.characters, list):
                                    st.session_state.book_spec.characters = [
                                        (
                                            item.get("name", "")
                                            if isinstance(item, dict)
                                            else str(item)
                                        )
                                        for item in enhanced_spec.characters
                                    ]
                                else:
                                    st.session_state.book_spec.characters = [
                                        str(enhanced_spec.characters)
                                    ]

                                st.session_state.book_spec.title = enhanced_spec.title
                                st.session_state.book_spec.genre = enhanced_spec.genre
                                st.session_state.book_spec.setting = (
                                    enhanced_spec.setting
                                )
                                st.session_state.book_spec.themes = enhanced_spec.themes
                                st.session_state.book_spec.tone = enhanced_spec.tone
                                st.session_state.book_spec.point_of_view = (
                                    enhanced_spec.point_of_view
                                )
                                st.session_state.book_spec.premise = (
                                    enhanced_spec.premise
                                )

                                st.success("Book Specification Enhanced!")
                                if st.session_state.project_name:
                                    st.session_state.project_manager.save_project(
                                        **st.session_state
                                    )

                            else:
                                st.error("Failed to enhance Book Specification.")

                    asyncio.run(enhance_book_spec_callback())

        if st.session_state.book_spec:
            st.json(st.session_state.book_spec.model_dump())
        else:
            st.write(
                "No Book Specification to display. Generate one using the Story Idea form."
            )

        # 3. Plot Outline Generation and Edit
    if st.session_state.book_spec:
        st.subheader("3. Plot Outline")

        # --- Generate Plot Outline Button and Confirmation (NOW FIRST) ---
        # Check if any manual input exists.
        manual_input_exists = bool(
            st.session_state.act_one_text.strip()
            or st.session_state.act_two_text.strip()
            or st.session_state.act_three_text.strip()
        )

        # Check if a generated plot outline exists.
        generated_outline_exists = bool(
            st.session_state.plot_outline
            and (
                st.session_state.plot_outline.act_one
                or st.session_state.plot_outline.act_two
                or st.session_state.plot_outline.act_three
            )
        )

        # Disable the button if manual input is present, *unless* a generated outline *also* exists.
        button_disabled = manual_input_exists and not generated_outline_exists

        if st.button("Generate Plot Outline", disabled=button_disabled):
            # Confirmation Check. Only appears IF a plot outline exists (either manual or generated)
            if st.session_state.plot_outline and (
                st.session_state.plot_outline.act_one
                or st.session_state.plot_outline.act_two
                or st.session_state.plot_outline.act_three
            ):
                if not st.checkbox(
                    "Overwrite existing Plot Outline?", key="confirm_plot_overwrite"
                ):
                    st.warning("Please confirm to overwrite the existing plot outline.")
                    st.stop()  # Stop execution if not confirmed

            # Proceed with generation (clearing any existing data)
            with st.spinner("Generating Plot Outline..."):
                st.session_state.plot_outline = (
                    PlotOutline()
                )  # Clear existing plot outline.  Important!
                st.session_state.plot_outline = asyncio.run(
                    st.session_state.content_generator.generate_plot_outline(
                        st.session_state.book_spec
                    )
                )

            if st.session_state.plot_outline:
                st.success("Plot Outline Generated!")
                if st.session_state.project_name:
                    st.session_state.project_manager.save_project(**st.session_state)
                    st.success(f"Project '{st.session_state.project_name}' saved!")
            else:
                st.error("Failed to generate Plot Outline.")

        # --- Act Outline Input Text Areas ---
        st.subheader("Act Outlines (Manual Input)")
        st.session_state.act_one_text = st.text_area(
            "Act One Plot Points",
            value="\n".join(st.session_state.plot_outline.act_one),
            height=150,
            key="act_one_input",
        )
        st.session_state.act_two_text = st.text_area(
            "Act Two Plot Points",
            value="\n".join(st.session_state.plot_outline.act_two),
            height=150,
            key="act_two_input",
        )
        st.session_state.act_three_text = st.text_area(
            "Act Three Plot Points",
            value="\n".join(st.session_state.plot_outline.act_three),
            height=150,
            key="act_three_input",
        )

        # --- Submit Buttons for Act Outlines ---
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Submit Act One", key="submit_act_one"):
                st.session_state.plot_outline.act_one = [
                    p.strip()
                    for p in st.session_state.act_one_text.splitlines()
                    if p.strip()
                ]
                if st.session_state.project_name:
                    st.session_state.project_manager.save_project(**st.session_state)
        with col2:
            if st.button("Submit Act Two", key="submit_act_two"):
                st.session_state.plot_outline.act_two = [
                    p.strip()
                    for p in st.session_state.act_two_text.splitlines()
                    if p.strip()
                ]
                if st.session_state.project_name:
                    st.session_state.project_manager.save_project(**st.session_state)
        with col3:
            if st.button("Submit Act Three", key="submit_act_three"):
                st.session_state.plot_outline.act_three = [
                    p.strip()
                    for p in st.session_state.act_three_text.splitlines()
                    if p.strip()
                ]
                if st.session_state.project_name:
                    st.session_state.project_manager.save_project(**st.session_state)

        if st.session_state.plot_outline:
            st.write("Plot Outline:")

            # Display plot outline acts and points (non-editable - unchanged)
            def format_plot_points(act_points):
                formatted_points = []
                for point in act_points:
                    cleaned_point = re.sub(r"^\d+\.\s*", "", point.strip())
                    if cleaned_point and not cleaned_point.startswith(
                        ("**", "Plot Outline:", "Act ")
                    ):
                        formatted_points.append(cleaned_point)
                return formatted_points

            st.write("**Act One: Setup**")
            for point in format_plot_points(st.session_state.plot_outline.act_one):
                st.markdown(f"- {point}")

            st.write("**Act Two: Confrontation**")
            for point in format_plot_points(st.session_state.plot_outline.act_two):
                st.markdown(f"- {point}")

            st.write("**Act Three: Resolution**")
            for point in format_plot_points(st.session_state.plot_outline.act_three):
                st.markdown(f"- {point}")

            # --- Enhance and Generate Chapters Buttons (Placed Below Plot Outline) ---
            col_enhance_chapter, col_generate_chapter = st.columns(
                2
            )  # Two columns for buttons
            with col_enhance_chapter:
                if st.button(
                    "Enhance Plot Outline",
                    key="enhance_plot_button",
                    disabled=not st.session_state.plot_outline,
                ):

                    async def enhance_plot_outline_callback():
                        with st.spinner("Enhancing Plot Outline..."):
                            enhanced_outline_raw = await st.session_state.content_generator.enhance_plot_outline(
                                "\n".join(
                                    [
                                        "Act One:\n"
                                        + "\n".join(
                                            st.session_state.plot_outline.act_one
                                        ),
                                        "Act Two:\n"
                                        + "\n".join(
                                            st.session_state.plot_outline.act_two
                                        ),
                                        "Act Three:\n"
                                        + "\n".join(
                                            st.session_state.plot_outline.act_three
                                        ),
                                    ]
                                )
                            )
                            if enhanced_outline_raw:
                                updated_plot_outline = PlotOutline(
                                    act_one=[], act_two=[], act_three=[]
                                )
                                acts = enhanced_outline_raw.split("Act ")
                                if len(acts) >= 4:
                                    updated_plot_outline.act_one = [
                                        txt.strip()
                                        for txt in acts[1]
                                        .split("Act")[0]
                                        .strip()
                                        .split("\n")
                                        if txt.strip()
                                    ]
                                    updated_plot_outline.act_two = [
                                        txt.strip()
                                        for txt in acts[2]
                                        .split("Act")[0]
                                        .strip()
                                        .split("\n")
                                        if txt.strip()
                                    ]
                                    updated_plot_outline.act_three = [
                                        txt.strip()
                                        for txt in acts[3].strip().split("\n")
                                        if txt.strip()
                                    ]
                                st.session_state.plot_outline = updated_plot_outline
                                if st.session_state.project_name:
                                    st.session_state.project_manager.save_project(
                                        **st.session_state
                                    )  # Autosave after enhance
                                st.success("Plot Outline Enhanced!")
                            else:
                                st.error("Failed to enhance Plot Outline.")

                    asyncio.run(enhance_plot_outline_callback())

            with col_generate_chapter:  # Corrected placement
                if st.button(
                    "Generate Chapter Outlines",
                    key="generate_chapter_button",
                    disabled=not st.session_state.plot_outline,
                ):
                    with st.spinner(
                        f"Generating Chapter Outlines... based on plot points"
                    ):
                        st.session_state.chapter_outlines = asyncio.run(
                            st.session_state.content_generator.generate_chapter_outlines(
                                st.session_state.plot_outline
                            )
                        )
                    if st.session_state.chapter_outlines:
                        st.success(
                            f"Chapter Outlines Generated for {len(st.session_state.chapter_outlines)} chapters!"
                        )
                        if st.session_state.project_name:
                            st.session_state.project_manager.save_project(
                                **st.session_state
                            )
                    else:
                        st.error("Failed to generate Chapter Outlines")
    # 4. Chapter Outline Generation and Edit
    if st.session_state.plot_outline:
        st.subheader("4. Chapter Outlines")

        if st.session_state.chapter_outlines:
            confirm_chapter_overwrite = st.checkbox(
                "Overwrite existing chapter outlines?",
                value=False,
                key="confirm_chapter_overwrite",
            )
        else:
            confirm_chapter_overwrite = True

        if confirm_chapter_overwrite:
            if st.button("Generate Chapter Outlines"):
                if st.session_state.chapter_outlines:
                    st.session_state.chapter_outlines = []
                with st.spinner("Generating Chapter Outlines..."):
                    st.session_state.chapter_outlines = asyncio.run(
                        st.session_state.content_generator.generate_chapter_outlines(
                            st.session_state.plot_outline
                        )
                    )
                if st.session_state.chapter_outlines:
                    st.success(
                        f"Chapter Outlines Generated for {len(st.session_state.chapter_outlines)} chapters!"
                    )
                    if st.session_state.project_name:  # Auto-save after generation
                        st.session_state.project_manager.save_project(
                            st.session_state.project_name,
                            st.session_state.story_idea,
                            st.session_state.book_spec,
                            st.session_state.plot_outline,
                            st.session_state.chapter_outlines,
                            st.session_state.scene_outlines,
                            st.session_state.scene_parts,
                        )
                        st.success(
                            f"Project '{st.session_state.project_name}' saved!"
                        )  # provide feedback of auto-save
                else:
                    st.error("Failed to generate Chapter Outlines.")
        else:
            st.info(
                "Please confirm you wish to overwrite existing chapter outlines to proceed."
            )

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
                        if st.session_state.project_name:  # Auto-save after edit
                            st.session_state.project_manager.save_project(
                                st.session_state.project_name,
                                st.session_state.story_idea,
                                st.session_state.book_spec,
                                st.session_state.plot_outline,
                                st.session_state.chapter_outlines,
                                st.session_state.scene_outlines,
                                st.session_state.scene_parts,
                            )
                            st.success(
                                f"Project '{st.session_state.project_name}' saved!"
                            )  # provide feedback of auto-save
                with col2:

                    if st.form_submit_button("Enhance Chapter Outlines"):

                        async def enhance_chapter_outlines_callback():
                            with st.spinner("Enhancing Chapter Outlines..."):
                                enhanced_chapter_outlines = await st.session_state.content_generator.enhance_chapter_outlines(
                                    edited_chapter_outlines
                                )
                                if enhanced_chapter_outlines:
                                    st.session_state.chapter_outlines = (
                                        enhanced_chapter_outlines
                                    )
                                    st.success("Chapter Outlines Enhanced!")
                                    if (
                                        st.session_state.project_name
                                    ):  # Auto-save after enhance
                                        st.session_state.project_manager.save_project(
                                            st.session_state.project_name,
                                            st.session_state.story_idea,
                                            st.session_state.book_spec,
                                            st.session_state.plot_outline,
                                            st.session_state.chapter_outlines,
                                            st.session_state.scene_outlines,
                                            st.session_state.scene_parts,
                                        )
                                        st.success(
                                            f"Project '{st.session_state.project_name}' saved!"
                                        )  # provide feedback of auto-save
                                else:
                                    st.error("Failed to enhance Chapter Outlines.")

                        asyncio.run(enhance_chapter_outlines_callback())

            # Display Chapter Outlines outside the form
            for chapter_outline in st.session_state.chapter_outlines:
                st.markdown(f"**Chapter {chapter_outline.chapter_number}:**")
                st.write(chapter_outline.summary)

    # 5. Scene Outline Generation and Edit - CHAPTER BY CHAPTER
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

        chapter_options = [
            f"Chapter {co.chapter_number}" for co in st.session_state.chapter_outlines
        ]
        st.session_state.current_chapter_index = st.selectbox(
            "Select Chapter for Scene Outlines:",
            options=range(len(chapter_options)),  # Use index for easier access
            format_func=lambda index: chapter_options[index],  # Display Chapter name
        )
        selected_chapter_outline = st.session_state.chapter_outlines[
            st.session_state.current_chapter_index
        ]

        if st.button(
            f"Generate Scene Outlines for {chapter_options[st.session_state.current_chapter_index]}",
            disabled=st.session_state.scene_outlines.get(
                selected_chapter_outline.chapter_number
            ),
        ):  # Disable if scenes already exist for chapter
            with st.spinner(
                f"Generating Scene Outlines for {chapter_options[st.session_state.current_chapter_index]}..."
            ):
                num_scenes = random.randint(2, st.session_state.max_scenes_per_chapter)
                scene_outlines = asyncio.run(
                    st.session_state.content_generator.generate_scene_outlines(
                        selected_chapter_outline, num_scenes
                    )
                )
                if scene_outlines:
                    st.session_state.scene_outlines[
                        selected_chapter_outline.chapter_number
                    ] = scene_outlines
                    st.success(
                        f"Scene Outlines Generated for {chapter_options[st.session_state.current_chapter_index]}!"
                    )
                    if st.session_state.project_name:  # Auto-save after generation
                        st.session_state.project_manager.save_project(
                            st.session_state.project_name,
                            st.session_state.story_idea,
                            st.session_state.book_spec,
                            st.session_state.plot_outline,
                            st.session_state.chapter_outlines,
                            st.session_state.scene_outlines,
                            st.session_state.scene_parts,
                        )
                        st.success(
                            f"Project '{st.session_state.project_name}' saved!"
                        )  # provide feedback of auto-save
                else:
                    st.error(
                        f"Failed to generate Scene Outlines for {chapter_options[st.session_state.current_chapter_index]}."
                    )

        # Display and Edit Scene Outlines for the selected chapter
        if st.session_state.scene_outlines.get(selected_chapter_outline.chapter_number):
            chapter_scene_outlines = st.session_state.scene_outlines[
                selected_chapter_outline.chapter_number
            ]
            with st.form(
                f"scene_outlines_chapter_{selected_chapter_outline.chapter_number}_form"
            ):
                st.markdown(
                    f"**Chapter {selected_chapter_outline.chapter_number} Scene Outlines**"
                )  # Chapter number in form header
                edited_scene_outlines = []
                for i, scene_outline in enumerate(chapter_scene_outlines):
                    edited_summary = st.text_area(
                        f"Scene {i + 1} Outline",
                        scene_outline.summary,
                        height=80,
                        key=f"scene_{selected_chapter_outline.chapter_number}_{i}_outline",
                    )
                    edited_scene_outlines.append(
                        SceneOutline(scene_number=i + 1, summary=edited_summary)
                    )

                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.form_submit_button(
                        f"Save Scene Outlines (Chapter {selected_chapter_outline.chapter_number})"
                    ):
                        st.session_state.scene_outlines[
                            selected_chapter_outline.chapter_number
                        ] = edited_scene_outlines
                        st.success(
                            f"Scene Outlines Saved for Chapter {selected_chapter_outline.chapter_number}!"
                        )
                        if st.session_state.project_name:  # Auto-save after edit
                            st.session_state.project_manager.save_project(
                                st.session_state.project_name,
                                st.session_state.story_idea,
                                st.session_state.book_spec,
                                st.session_state.plot_outline,
                                st.session_state.chapter_outlines,
                                st.session_state.scene_outlines,
                                st.session_state.scene_parts,
                            )
                            st.success(
                                f"Project '{st.session_state.project_name}' saved!"
                            )  # provide feedback of auto-save
                with col2:

                    if st.form_submit_button(
                        f"Enhance Scene Outlines (Chapter {selected_chapter_outline.chapter_number})"
                    ):

                        async def enhance_scene_outlines_callback():
                            with st.spinner(
                                f"Enhancing Scene Outlines for Chapter {selected_chapter_outline.chapter_number}..."
                            ):
                                enhanced_scene_outlines = await st.session_state.content_generator.enhance_scene_outlines(
                                    edited_scene_outlines
                                )
                                if enhanced_scene_outlines:
                                    st.session_state.scene_outlines[
                                        selected_chapter_outline.chapter_number
                                    ] = enhanced_scene_outlines
                                    st.success(
                                        f"Scene Outlines Enhanced for Chapter {selected_chapter_outline.chapter_number}!"
                                    )
                                    if (
                                        st.session_state.project_name
                                    ):  # Auto-save after enhance
                                        st.session_state.project_manager.save_project(
                                            st.session_state.project_name,
                                            st.session_state.story_idea,
                                            st.session_state.book_spec,
                                            st.session_state.plot_outline,
                                            st.session_state.chapter_outlines,
                                            st.session_state.scene_outlines,
                                            st.session_state.scene_parts,
                                        )
                                        st.success(
                                            f"Project '{st.session_state.project_name}' saved!"
                                        )  # provide feedback of auto-save
                                else:
                                    st.error(
                                        f"Failed to enhance Scene Outlines for Chapter {selected_chapter_outline.chapter_number}."
                                    )

                        asyncio.run(enhance_scene_outlines_callback())

                # Display Scene Outlines outside the form
                for scene_outline in st.session_state.scene_outlines.get(
                    selected_chapter_outline.chapter_number, []
                ):
                    st.markdown(f"**Scene {scene_outline.scene_number}:**")
                    st.write(scene_outline.summary)


if __name__ == "__main__":
    main()
