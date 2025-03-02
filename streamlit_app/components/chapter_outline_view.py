# streamlit_app/components/chapter_outline_view.py
import streamlit as st
import asyncio
from core.plot_outline import ChapterOutline
from typing import List, Optional
from core.content_generation.chapter_outline_generator import ChapterOutlineGenerator


def chapter_outlines_display(
    chapter_outlines: Optional[List[ChapterOutline]],
    chapter_outline_generator: ChapterOutlineGenerator,
):
    """
    Displays ChapterOutlines and provides UI for generation and enhancement
    with autosave functionality.
    """
    st.subheader("Chapter Outlines")

    if not chapter_outlines:
        num_chapters = st.number_input(
            "Number of Chapters",
            min_value=3,
            max_value=50,
            value=(
                st.session_state.num_chapters
                if "num_chapters" in st.session_state
                else 10
            ),
            key="num_chapters_input",
        )
        st.session_state.num_chapters = int(num_chapters)
        if st.button(
            "Generate Chapter Outlines",
            disabled=st.session_state.chapter_outlines
            or not st.session_state.plot_outline,
            key="generate_chapter_outlines_button",
        ):
            if st.session_state.plot_outline and chapter_outline_generator:
                with st.spinner("Generating Chapter Outlines..."):
                    generated_outlines = asyncio.run(
                        chapter_outline_generator.generate(
                            st.session_state.plot_outline, st.session_state.num_chapters
                        )
                    )
                if generated_outlines:
                    st.session_state.chapter_outlines = generated_outlines
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
                        f"Chapter Outlines Generated for {len(st.session_state.chapter_outlines)} chapters and Project Autosaved!"
                    )
                    st.rerun()
                else:
                    st.error("Failed to generate Chapter Outlines.")
            else:
                st.warning("Plot Outline is required to generate Chapter Outlines.")

    else:
        with st.expander("Edit Chapter Outlines", expanded=True):
            edited_chapter_outlines = [co.model_copy() for co in chapter_outlines]
            with st.form("chapter_outlines_form"):
                for i, chapter_outline in enumerate(edited_chapter_outlines):
                    st.markdown(f"**Chapter {chapter_outline.chapter_number}:**")
                    edited_summary = st.text_area(
                        "Summary",
                        chapter_outline.summary,
                        height=100,
                        key=f"chapter_{i}_summary",
                    )
                    edited_chapter_outlines[i].summary = edited_summary

                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.form_submit_button(
                        "Save Chapter Outlines (Manual Edit)",
                        key="save_chapter_outlines_button",
                    ):
                        st.session_state.chapter_outlines = edited_chapter_outlines
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
                            "Chapter Outlines Saved (Manual Edit) and Project Autosaved!"
                        )
                with col2:
                    if st.form_submit_button(
                        "Enhance Chapter Outlines",
                        key="enhance_chapter_outlines_button",
                    ):
                        with st.spinner("Enhancing Chapter Outlines..."):
                            enhanced_chapter_outlines = asyncio.run(
                                chapter_outline_generator.enhance(
                                    edited_chapter_outlines
                                )
                            )
                        if enhanced_chapter_outlines:
                            st.session_state.chapter_outlines = (
                                enhanced_chapter_outlines
                            )
                            # Autosave project after enhancement
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
                                "Chapter Outlines Enhanced and Project Autosaved!"
                            )
                            st.rerun()
                        else:
                            st.error("Failed to enhance Chapter Outlines.")

        for chapter_outline in chapter_outlines:
            st.markdown(f"**Chapter {chapter_outline.chapter_number}:**")
            st.write(chapter_outline.summary)
