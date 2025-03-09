# streamlit_components/story_idea_section_component.py
import streamlit as st
import asyncio


def story_idea_ui(session_state):
    """
    Creates the Story Idea input section in the Streamlit application.
    """
    st.subheader("💡 1. Story Idea")
    st.caption("Start by describing your novel's core concept.")
    session_state.story_idea = st.text_area(
        "Enter your story idea:", value=session_state.story_idea, height=100
    )
    if st.button(
        "✨ Generate Book Specification",
        disabled=not session_state.story_idea,
    ):
        with st.spinner("Generating Book Specification..."):
            session_state.book_spec = asyncio.run(
                session_state.content_generator.generate_book_spec(
                    session_state.story_idea, session_state  # Pass session_state
                )
            )
        if session_state.book_spec:
            st.success("Book Specification Generated! 🎉")
            # REMOVED redundant save:  session_state.project_manager.save_project(...)
        else:
            st.error("Failed to generate Book Specification. 😞")
