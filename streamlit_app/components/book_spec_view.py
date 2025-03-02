# streamlit_app/components/book_spec_view.py
import streamlit as st
import asyncio
from core.book_spec import BookSpec
from typing import Optional
from core.content_generation.book_spec_generator import BookSpecGenerator
from utils.logger import logger


def book_spec_display(
    book_spec: Optional[BookSpec], book_spec_generator: BookSpecGenerator
):
    """
    Displays the BookSpec data, provides editing capabilities, and automatically generates the book spec upon entering a story idea.
    """
    st.subheader("Book Specification")

    story_idea_input = st.session_state.story_idea  # Get story idea from session state

    if book_spec:  # If book_spec exists, display the editable fields
        st.write("### Edit Book Specification")

        # Initialize individual component states if they don't exist
        if "book_spec_title" not in st.session_state:
            st.session_state.book_spec_title = book_spec.title
        if "book_spec_genre" not in st.session_state:
            st.session_state.book_spec_genre = book_spec.genre
        if "book_spec_setting" not in st.session_state:
            st.session_state.book_spec_setting = book_spec.setting
        if "book_spec_themes" not in st.session_state:
            st.session_state.book_spec_themes = ", ".join(book_spec.themes)
        if "book_spec_tone" not in st.session_state:
            st.session_state.book_spec_tone = book_spec.tone
        if "book_spec_point_of_view" not in st.session_state:
            st.session_state.book_spec_point_of_view = book_spec.point_of_view
        if "book_spec_characters" not in st.session_state:
            st.session_state.book_spec_characters = "\n".join(book_spec.characters)
        if "book_spec_premise" not in st.session_state:
            st.session_state.book_spec_premise = book_spec.premise

        # Create input fields for each spec element
        st.session_state.book_spec_title = st.text_input(
            "Title", value=st.session_state.book_spec_title, key="title_input"
        )
        st.session_state.book_spec_genre = st.text_input(
            "Genre", value=st.session_state.book_spec_genre, key="genre_input"
        )
        st.session_state.book_spec_setting = st.text_area(
            "Setting",
            value=st.session_state.book_spec_setting,
            height=100,
            key="setting_input",
        )
        st.session_state.book_spec_themes = st.text_input(
            "Themes (comma-separated)",
            value=st.session_state.book_spec_themes,
            key="themes_input",
        )
        st.session_state.book_spec_tone = st.text_input(
            "Tone", value=st.session_state.book_spec_tone, key="tone_input"
        )
        st.session_state.book_spec_point_of_view = st.text_input(
            "Point of View",
            value=st.session_state.book_spec_point_of_view,
            key="point_of_view_input",
        )
        st.session_state.book_spec_characters = st.text_area(
            "Characters (one description per line)",
            value=st.session_state.book_spec_characters,
            height=150,
            key="characters_input",
        )
        st.session_state.book_spec_premise = st.text_area(
            "Premise",
            value=st.session_state.book_spec_premise,
            height=100,
            key="premise_input",
        )

        col_save, _ = st.columns([1, 3])  # Removed enhance column
        with col_save:
            if st.button("Save Book Spec (Manual Edit)", key="save_book_spec_button"):
                # Update book_spec with current input values
                st.session_state.book_spec = BookSpec(
                    title=st.session_state.book_spec_title,
                    genre=st.session_state.book_spec_genre,
                    setting=st.session_state.book_spec_setting,
                    themes=[
                        theme.strip()
                        for theme in st.session_state.book_spec_themes.split(",")
                    ],
                    tone=st.session_state.book_spec_tone,
                    point_of_view=st.session_state.book_spec_point_of_view,
                    characters=[
                        char.strip()
                        for char in st.session_state.book_spec_characters.splitlines()
                    ],
                    premise=st.session_state.book_spec_premise,
                )
                # Autosave project after manual edit save
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
                    "Book Specification Saved (Manual Edit) and Project Autosaved!"
                )

        st.json(
            st.session_state.book_spec.model_dump()
            if st.session_state.book_spec
            else {}
        )
