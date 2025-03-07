# streamlit_app.py
import streamlit as st
from PIL import Image
import asyncio
import json
import os
import random
import re

from core.book_spec import BookSpec
from core.plot_outline import ChapterOutline, SceneOutline, PlotOutline
from core.content_generator import ChapterOutlineMethod
from core.content_generator import ContentGenerator
from core import project_manager
from llm.llm_client import OllamaClient
from llm.prompt_manager import PromptManager
from utils.config import config
from utils.logger import logger

# Import component functions from streamlit_components directory
from streamlit_components.sidebar_component import create_sidebar
from streamlit_components.story_idea_section_component import story_idea_ui
from streamlit_components.book_spec_section_component import book_spec_ui
from streamlit_components.chapter_outline_section_component import (
    chapter_outline_ui,
)  # Corrected import path
from streamlit_components.scene_outline_section_component import scene_outline_ui
from streamlit_components.scene_part_section_component import (
    scene_part_ui,
)  # Import the new component
import utils.app as utils


def main():
    im = Image.open("./assets/icon.png")

    st.set_page_config(layout="wide", page_title="Fiction Fabricator", page_icon=im)
    utils.local_css("./assets/styles.css")
    utils.remote_css("https://fonts.googleapis.com/icon?family=Material+Icons")

    st.title("Fiction Fabricator")  # Added title with emoji

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
    if "chapter_outlines_27_method" not in st.session_state:
        st.session_state.chapter_outlines_27_method = []
    if "chapter_outlines" not in st.session_state:
        st.session_state.chapter_outlines = []
    if "scene_outlines" not in st.session_state:
        st.session_state.scene_outlines = {}
    if "scene_parts" not in st.session_state:
        st.session_state.scene_parts = {}
    if "project_name" not in st.session_state:
        st.session_state.project_name = ""
    if "num_chapters" not in st.session_state:
        st.session_state.num_chapters = 27
    if "max_scenes_per_chapter" not in st.session_state:
        st.session_state.max_scenes_per_chapter = 3
    if "current_chapter_index" not in st.session_state:
        st.session_state.current_chapter_index = 0
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
    if "project_loaded" not in st.session_state:
        st.session_state.project_loaded = False
    if "new_project_requested" not in st.session_state:
        st.session_state.new_project_requested = False

    if "act_one_text" not in st.session_state:
        st.session_state.act_one_text = ""
    if "act_two_text" not in st.session_state:
        st.session_state.act_two_text = ""
    if "act_three_text" not in st.session_state:
        st.session_state.act_three_text = ""

    # Create sidebar using the component function
    create_sidebar(st.session_state)
    # Main panel layout using columns
    st.header("Novel Generation Workflow")  # Main header with emoji
    story_idea_ui(st.session_state)
    book_spec_ui(st.session_state)
    chapter_outline_ui(st.session_state)  # Corrected function name
    scene_outline_ui(st.session_state)
    scene_part_ui(st.session_state)  # Call the new scene part component


if __name__ == "__main__":
    main()
