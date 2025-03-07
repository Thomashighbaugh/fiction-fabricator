# streamlit_components/story_idea_section_component.py
import streamlit as st
import asyncio


def story_idea_ui(session_state):
    """
    Creates the Story Idea input section in the Streamlit application with enhanced styling.

    Args:
        session_state: Streamlit session state object.
    """
    st.subheader("💡 1. Story Idea")  # Added emoji and subheader styling
    st.caption("Start by describing your novel's core concept.")  # Added caption
    session_state.story_idea = st.text_area(
        "Enter your story idea:", value=session_state.story_idea, height=100
    )
    if st.button(
        "✨ Generate Book Specification",
        disabled=not session_state.story_idea,  # Added emoji
    ):
        with st.spinner("Generating Book Specification..."):
            session_state.book_spec = asyncio.run(
                session_state.content_generator.generate_book_spec(
                    session_state.story_idea
                )
            )
        if session_state.book_spec:
            st.success("Book Specification Generated! 🎉")  # Added emoji
            if session_state.project_name and session_state.new_project_requested:
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
            st.error("Failed to generate Book Specification. 😞")
