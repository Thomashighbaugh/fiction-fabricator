# streamlit_app/components/scene_outline_view.py
import streamlit as st
import asyncio
from core.plot_outline import SceneOutline
from typing import List, Optional, Dict
from core.content_generation.scene_outline_generator import SceneOutlineGenerator
import random


def scene_outlines_display(
    scene_outlines: Optional[Dict[int, List[SceneOutline]]],
    scene_outline_generator: SceneOutlineGenerator,
):
    """
    Displays SceneOutlines and provides UI for generation and enhancement
    with autosave functionality.
    """
    st.subheader("Scene Outlines")

    if not scene_outlines:
        max_scenes_per_chapter = st.number_input(
            "Maximum Scenes per Chapter",
            min_value=2,
            max_value=10,
            value=(
                st.session_state.max_scenes_per_chapter
                if "max_scenes_per_chapter" in st.session_state
                else 3
            ),
            key="max_scenes_per_chapter_input",
        )
        st.session_state.max_scenes_per_chapter = int(max_scenes_per_chapter)

        if st.button(
            "Generate Scene Outlines (All Chapters)",
            key="generate_all_scene_outlines_button",
            disabled=st.session_state.scene_outlines
            or not st.session_state.chapter_outlines,
        ):
            if st.session_state.chapter_outlines and scene_outline_generator:
                with st.spinner("Generating Scene Outlines for All Chapters..."):
                    generated_scene_outlines = {}
                    for chapter_outline in st.session_state.chapter_outlines:
                        num_scenes = random.randint(
                            2, st.session_state.max_scenes_per_chapter
                        )
                        chapter_scene_outlines = asyncio.run(
                            scene_outline_generator.generate(
                                chapter_outline, num_scenes
                            )
                        )
                        if chapter_scene_outlines:
                            generated_scene_outlines[chapter_outline.chapter_number] = (
                                chapter_scene_outlines
                            )
                    st.session_state.scene_outlines = generated_scene_outlines
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
                        f"Scene Outlines Generated for All Chapters (up to {st.session_state.max_scenes_per_chapter} scenes per chapter) and Project Autosaved!"
                    )
                    st.rerun()
            else:
                st.error("Failed to generate Scene Outlines.")
        else:
            st.warning("Chapter Outlines are required to generate Scene Outlines.")

    else:
        for chapter_number, outlines in scene_outlines.items():
            with st.expander(
                f"Edit Scene Outlines - Chapter {chapter_number}", expanded=True
            ):
                edited_scene_outlines = [so.model_copy() for so in outlines]
                with st.form(f"scene_outlines_form_chapter_{chapter_number}"):
                    st.markdown(f"**Chapter {chapter_number}**")
                    for i, scene_outline in enumerate(edited_scene_outlines):
                        edited_summary = st.text_area(
                            f"Scene {i + 1} Outline",
                            scene_outline.summary,
                            height=80,
                            key=f"scene_outline_{chapter_number}_{i}",
                        )
                        edited_scene_outlines[i].summary = edited_summary

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if st.form_submit_button(
                            f"Save Scene Outlines (Manual Edit - Chapter {chapter_number})",
                            key=f"save_scene_outlines_chapter_{chapter_number}_button",
                        ):
                            st.session_state.scene_outlines[chapter_number] = (
                                edited_scene_outlines
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
                                f"Scene Outlines Saved (Manual Edit - Chapter {chapter_number}) and Project Autosaved!"
                            )
                    with col2:
                        if st.form_submit_button(
                            f"Enhance Scene Outlines (Chapter {chapter_number})",
                            key=f"enhance_scene_outlines_chapter_{chapter_number}_button",
                        ):
                            if scene_outline_generator:
                                with st.spinner(
                                    f"Enhancing Scene Outlines for Chapter {chapter_number}..."
                                ):
                                    enhanced_scene_outlines = asyncio.run(
                                        scene_outline_generator.enhance(
                                            edited_scene_outlines
                                        )
                                    )
                                if enhanced_scene_outlines:
                                    st.session_state.scene_outlines[chapter_number] = (
                                        enhanced_scene_outlines
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
                                        f"Scene Outlines Enhanced for Chapter {chapter_number} and Project Autosaved!"
                                    )
                                    st.rerun()
                                else:
                                    st.error(
                                        f"Failed to enhance Scene Outlines for Chapter {chapter_number}."
                                    )
                            else:
                                st.error("Scene Outline Generator not initialized.")

            st.markdown(f"**Chapter {chapter_number} Scenes:**")
            for scene_outline in outlines:
                st.markdown(f"  **Scene {scene_outline.scene_number}:**")
                st.write(scene_outline.summary)
