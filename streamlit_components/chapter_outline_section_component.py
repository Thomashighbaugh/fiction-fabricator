# streamlit_components/chapter_outline_section_component.py
import streamlit as st
import asyncio

from core.content_generator import ChapterOutlineMethod


def chapter_outline_ui(session_state):
    """
    Creates the Chapter Outline section in the Streamlit application with enhanced styling.

    Args:
        session_state: Streamlit session state object.
    """
    if session_state.book_spec:
        st.subheader("📜 3. 27 Chapter Outline")  # Added emoji and subheader styling
        st.caption(
            "Generate and refine your chapter outlines using the 27-chapter method."
        )  # Added caption

        if st.button("✨ Generate 27 Chapter Outline"):  # Added emoji
            with st.spinner("Generating 27 Chapter Outline..."):
                session_state.chapter_outlines_27_method = asyncio.run(
                    session_state.content_generator.generate_chapter_outline_27_method(
                        session_state.book_spec
                    )
                )
            if session_state.chapter_outlines_27_method:
                st.success("27 Chapter Outline Generated! 🎉")  # Added emoji
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
                st.error("Failed to generate 27 Chapter Outline. 😞")  # Added emoji

        if session_state.chapter_outlines_27_method:
            with st.form("chapter_27_outlines_form"):
                st.subheader(
                    "✏️ Edit 27 Chapter Outlines"
                )  # Added subheader for edit form
                edited_chapter_outlines_27_method = list(
                    session_state.chapter_outlines_27_method
                )
                for i, chapter_outline in enumerate(edited_chapter_outlines_27_method):
                    st.markdown(
                        f"**Chapter {chapter_outline.chapter_number}: {chapter_outline.role}**"
                    )
                    edited_summary = st.text_area(
                        "Summary",
                        chapter_outline.summary,
                        height=100,
                        key=f"chapter_27_{i}_summary",
                    )
                    edited_chapter_outlines_27_method[i] = ChapterOutlineMethod(
                        chapter_number=chapter_outline.chapter_number,
                        role=chapter_outline.role,
                        summary=edited_summary,
                    )
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.form_submit_button(
                        "💾 Save 27 Chapter Outlines"
                    ):  # Added emoji
                        session_state.chapter_outlines_27_method = (
                            edited_chapter_outlines_27_method
                        )
                        st.success("27 Chapter Outlines Saved! ✅")  # Added emoji
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
                        "✨ Enhance 27 Chapter Outlines"
                    ):  # Added emoji

                        async def enhance_chapter_outlines_27_method_callback():
                            with st.spinner("Enhancing 27 Chapter Outlines..."):
                                enhanced_chapter_outlines_27_method = await session_state.content_generator.enhance_chapter_outlines_27_method(
                                    edited_chapter_outlines_27_method
                                )
                                if enhanced_chapter_outlines_27_method:
                                    session_state.chapter_outlines_27_method = (
                                        enhanced_chapter_outlines_27_method
                                    )
                                    st.success(
                                        "27 Chapter Outlines Enhanced! 🚀"
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
                                        "Failed to enhance 27 Chapter Outlines. 😞"
                                    )  # Added emoji

                        asyncio.run(enhance_chapter_outlines_27_method_callback())

            st.subheader(
                "📖 27 Chapter Outline Preview"
            )  # Added subheader for preview section
            st.caption("Review your 27 chapter outlines below.")  # Added caption
            for chapter_outline in session_state.chapter_outlines_27_method:
                st.markdown(
                    f"**Chapter {chapter_outline.chapter_number}: {chapter_outline.role}**"
                )
                st.write(chapter_outline.summary)
    else:
        st.info(
            "No Book Specification available. Please generate one in the '1. Story Idea' section."
        )  # Changed to st.info and more informative message
