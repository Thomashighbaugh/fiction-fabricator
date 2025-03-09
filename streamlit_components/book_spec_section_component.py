# streamlit_components/book_spec_section_component.py
import streamlit as st
import asyncio
import tomli  # Import tomli
import tomli_w

from core.book_spec import BookSpec
from pydantic import ValidationError
from utils.logger import logger


def book_spec_ui(session_state):
    """
    Creates the Book Specification section.
    """
    if session_state.book_spec:
        st.subheader("📚 2. Book Specification")
        st.caption("Define the core elements of your novel.")
        with st.form("book_spec_form"):
            title = st.text_input(
                "Title", value=session_state.book_spec.title, key="title_input"
            )
            genre = st.text_input(
                "Genre", value=session_state.book_spec.genre, key="genre_input"
            )
            setting = st.text_area(
                "Setting (Detailed description of locations and time period)",
                value=session_state.book_spec.setting,
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
                if st.form_submit_button("💾 Save Book Specification"):
                    session_state.book_spec.title = title
                    session_state.book_spec.genre = genre
                    session_state.book_spec.setting = setting  #  string
                    session_state.book_spec.themes = [
                        t.strip() for t in themes_str.split(",")
                    ]
                    session_state.book_spec.tone = tone
                    session_state.book_spec.point_of_view = point_of_view
                    session_state.book_spec.characters = [
                        c.strip() for c in characters_str.split("\n")
                    ]
                    session_state.book_spec.premise = premise
                    st.success("Book Specification Saved! ✅")
                    # Manual Save now only on button
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
                if st.form_submit_button("✨ Enhance Book Specification"):

                    async def enhance_book_spec_callback():
                        with st.spinner("Enhancing Book Specification..."):
                            enhanced_spec = (
                                await session_state.content_generator.enhance_book_spec(
                                    session_state.book_spec, session_state
                                )
                            )  # Pass session_state
                            if enhanced_spec:
                                session_state.book_spec = (
                                    enhanced_spec  # Update session_state
                                )
                                st.success("Book Specification Enhanced! 🚀")
                                # REMOVED redundant save: session_state.project_manager.save_project(...)
                            else:
                                st.error("Failed to enhance Book Specification. 😞")

                    asyncio.run(enhance_book_spec_callback())

        st.subheader("🔍 Book Specification Preview")
        st.caption("Review the generated Book Spec in TOML format.")
        st.text_area(
            label="Book Spec Preview",
            value=tomli_w.dumps(session_state.book_spec.model_dump()),  # Show TOML
            height=300,
        )

    else:
        st.info(
            "No Book Specification generated yet. Please generate one in the '1. Story Idea' section above."
        )
