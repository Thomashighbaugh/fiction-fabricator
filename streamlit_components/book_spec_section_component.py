# streamlit_components/book_spec_section_component.py
import streamlit as st
import asyncio
import json

from core.book_spec import BookSpec
from pydantic import ValidationError
from utils.logger import logger


def book_spec_ui(session_state):
    """
    Creates the Book Specification section in the Streamlit application with enhanced styling.

    Args:
        session_state: Streamlit session state object.
    """
    if session_state.book_spec:
        st.subheader("📚 2. Book Specification")  # Added emoji and subheader styling
        st.caption("Define the core elements of your novel.")  # Added caption
        with st.form("book_spec_form"):
            title = st.text_input(
                "Title", value=session_state.book_spec.title, key="title_input"
            )
            genre = st.text_input(
                "Genre", value=session_state.book_spec.genre, key="genre_input"
            )
            setting = st.text_area(
                "Setting (Detailed description of locations and time period)",
                value=(
                    json.dumps(session_state.book_spec.setting)
                    if isinstance(session_state.book_spec.setting, dict)
                    else session_state.book_spec.setting
                ),
                height=100,
                key="setting_input",
            )
            themes_str = st.text_input(
                "Themes (comma-separated)",
                value=", ".join(session_state.book_spec.themes),
                key="themes_input",
            )
            tone = st.text_input(
                "Tone", value=session_state.book_spec.tone, key="tone_input"
            )
            point_of_view = st.text_input(
                "Point of View",
                value=session_state.book_spec.point_of_view,
                key="pov_input",
            )
            characters_str = st.text_area(
                "Characters (comma-separated descriptions)",
                value="\n".join(session_state.book_spec.characters),
                height=150,
                key="characters_input",
            )
            premise = st.text_area(
                "Premise",
                value=session_state.book_spec.premise,
                height=100,
                key="premise_input",
            )
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.form_submit_button("💾 Save Book Specification"):  # Added emoji
                    session_state.book_spec.title = title
                    session_state.book_spec.genre = genre
                    if isinstance(setting, str):
                        try:
                            session_state.book_spec.setting = json.loads(setting)
                        except json.JSONDecodeError as e:
                            st.error(
                                f"Error parsing Setting as JSON, saving as string: {e}"
                            )
                            session_state.book_spec.setting = setting
                    session_state.book_spec.themes = [
                        t.strip() for t in themes_str.split(",")
                    ]
                    session_state.book_spec.tone = tone
                    session_state.book_spec.point_of_view = point_of_view
                    session_state.book_spec.characters = [
                        c.strip() for c in characters_str.split("\n")
                    ]
                    session_state.book_spec.premise = premise
                    st.success("Book Specification Saved! ✅")  # Added emoji
                    if session_state.project_name:
                        session_state.project_manager.save_project(
                            project_name=session_state.project_name,
                            story_idea=session_state.story_idea,
                            book_spec=session_state.book_spec,
                            plot_outline=session_state.plot_outline,
                            chapter_outlines=session_state.chapter_outlines,
                            chapter_outlines_27_method=session_state.chapter_outlines_27_method,
                            scene_outlines=session_state.scene_outlines,
                            scene_parts=session_state.scene_parts,
                        )

            with col2:
                if st.form_submit_button(
                    "✨ Enhance Book Specification"
                ):  # Added emoji

                    async def enhance_book_spec_callback():
                        with st.spinner("Enhancing Book Specification..."):
                            enhanced_spec = (
                                await session_state.content_generator.enhance_book_spec(
                                    session_state.book_spec
                                )
                            )
                            if enhanced_spec:
                                if isinstance(enhanced_spec.characters, list):
                                    session_state.book_spec.characters = [
                                        (
                                            item.get("name", "")
                                            if isinstance(item, dict)
                                            else str(item)
                                        )
                                        for item in enhanced_spec.characters
                                    ]
                                else:
                                    session_state.book_spec.characters = [
                                        str(enhanced_spec.characters)
                                    ]

                                session_state.book_spec.title = enhanced_spec.title
                                session_state.book_spec.genre = enhanced_spec.genre
                                session_state.book_spec.setting = enhanced_spec.setting
                                session_state.book_spec.themes = enhanced_spec.themes
                                session_state.book_spec.tone = enhanced_spec.tone
                                session_state.book_spec.point_of_view = (
                                    enhanced_spec.point_of_view
                                )
                                session_state.book_spec.premise = enhanced_spec.premise

                                st.success(
                                    "Book Specification Enhanced! 🚀"
                                )  # Added emoji
                                if session_state.project_name:
                                    session_state.project_manager.save_project(
                                        project_name=session_state.project_name,
                                        story_idea=session_state.story_idea,
                                        book_spec=session_state.book_spec,
                                        plot_outline=session_state.plot_outline,
                                        chapter_outlines=session_state.chapter_outlines,
                                        chapter_outlines_27_method=session_state.chapter_outlines_27_method,
                                        scene_outlines=session_state.scene_outlines,
                                        scene_parts=session_state.scene_parts,
                                    )

                            else:
                                st.error(
                                    "Failed to enhance Book Specification. 😞"
                                )  # Added emoji

                    asyncio.run(enhance_book_spec_callback())

        st.subheader(
            "🔍 Book Specification Preview"
        )  # Added subheader for preview section
        st.caption("Review the generated Book Spec in JSON format.")  # Added caption
        book_spec_dict = session_state.book_spec.model_dump()
        if isinstance(session_state.book_spec.setting, str):
            try:
                book_spec_dict["setting"] = json.loads(session_state.book_spec.setting)
            except json.JSONDecodeError:
                logger.warning(
                    "Setting is a string but not valid JSON, displaying as raw string."
                )
                book_spec_dict["setting"] = session_state.book_spec.setting

        st.json(
            book_spec_dict, expanded=False
        )  # Added expanded=False for better initial view
    else:
        st.info(
            "No Book Specification generated yet. Please generate one in the '1. Story Idea' section above."
        )  # Changed to st.info and more informative message
