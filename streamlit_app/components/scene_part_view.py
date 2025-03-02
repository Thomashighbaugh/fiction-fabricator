# /home/tlh/refactored_gui_fict_fab/streamlit_app/components/scene_part_view.py
import streamlit as st
import asyncio
from typing import Optional, Dict, List
from core.content_generation.scene_part_generator import ScenePartGenerator
from core.plot_outline import ChapterOutline, SceneOutline
from core.book_spec import BookSpec


def scene_part_display(
    scene_parts_text: Dict[int, Dict[int, Dict[int, str]]], # Moved to first
    scene_part_generator: ScenePartGenerator,
    book_spec: Optional[BookSpec],
    chapter_outlines: Optional[List[ChapterOutline]],
    scene_outlines: Optional[Dict[int, List[SceneOutline]]],
):
    """
    Displays and manages scene parts text generation and enhancement
    with autosave functionality. Relies on st.session_state.scene_parts_text directly.
    """
    st.subheader("Scene Parts - Text Generation")

    if st.button(
        "Generate Scene Parts Text (All Scenes)",
        key="generate_scene_parts_button",
        disabled=st.session_state.scene_parts_text
        or not st.session_state.scene_outlines,
    ):
        if (
            st.session_state.scene_outlines
            and scene_part_generator
            and book_spec
            and chapter_outlines
        ):
            with st.spinner("Generating Scene Parts Text... This may take a while."):
                generated_scene_parts_text = {}
                for (
                    chapter_number,
                    scene_outlines_chapter,
                ) in st.session_state.scene_outlines.items():
                    generated_scene_parts_text[chapter_number] = {}
                    chapter_outline = next(
                        (
                            co
                            for co in chapter_outlines
                            if co.chapter_number == chapter_number
                        ),
                        ChapterOutline(
                            chapter_number=chapter_number,
                            summary="Placeholder Chapter Outline",
                        ),
                    )

                    for scene_outline in scene_outlines_chapter:
                        generated_scene_parts_text[chapter_number][
                            scene_outline.scene_number
                        ] = {}
                        num_parts = 3
                        for part_number in range(1, num_parts + 1):
                            generated_part = asyncio.run(
                                scene_part_generator.generate(
                                    scene_outline,
                                    part_number,
                                    book_spec,
                                    chapter_outline,
                                    scene_outline,
                                )
                            )
                            if generated_part:
                                generated_scene_parts_text[chapter_number][
                                    scene_outline.scene_number
                                ][part_number] = generated_part
                            else:
                                st.error(
                                    f"Failed to generate part {part_number} of Scene {scene_outline.scene_number}, Chapter {chapter_number}."
                                )
                st.session_state.scene_parts_text = generated_scene_parts_text
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
                    "Scene parts generated for all scenes and Project Autosaved!"
                )
                st.rerun()
        else:
            st.warning(
                "Scene Outlines, Book Specification, and Chapter Outlines are required to generate Scene Parts."
            )

    if st.session_state.scene_parts_text:
        with st.expander("Enhance Scene Parts", expanded=False):
            chapter_numbers = list(st.session_state.scene_parts_text.keys())
            if chapter_numbers:
                selected_chapter = st.selectbox(
                    "Select Chapter for Enhancement",
                    chapter_numbers,
                    key="chapter_selectbox_enhance_part",
                )
                scene_numbers = list(
                    st.session_state.scene_parts_text.get(selected_chapter, {}).keys()
                )

                if scene_numbers:
                    selected_scene = st.selectbox(
                        "Select Scene for Enhancement",
                        scene_numbers,
                        key="scene_selectbox_enhance_part",
                    )
                    part_numbers = list(
                        st.session_state.scene_parts_text.get(selected_chapter, {})
                        .get(selected_scene, {})
                        .keys()
                    )

                    if part_numbers:
                        selected_part = st.selectbox(
                            "Select Part for Enhancement",
                            part_numbers,
                            key="part_selectbox_enhance_part",
                        )

                        if st.button(
                            f"Enhance Part {selected_part} of Scene {selected_scene}, Chapter {selected_chapter}",
                            key="enhance_single_scene_part_button",
                        ):
                            if (
                                scene_part_generator
                                and book_spec
                                and chapter_outlines
                                and scene_outlines
                            ):
                                with st.spinner(
                                    f"Enhancing Part {selected_part} of Scene {selected_scene}, Chapter {selected_chapter}..."
                                ):
                                    current_part_text = (
                                        st.session_state.scene_parts_text[
                                            selected_chapter
                                        ][selected_scene][selected_part]
                                    )

                                    chapter_outline = next(
                                        (
                                            co
                                            for co in chapter_outlines
                                            if co.chapter_number == selected_chapter
                                        ),
                                        ChapterOutline(
                                            chapter_number=selected_chapter,
                                            summary="Placeholder Chapter Outline",
                                        ),
                                    )

                                    scene_outline_full = next(
                                        (
                                            so
                                            for so in scene_outlines.get(
                                                selected_chapter, []
                                            )
                                            if so.scene_number == selected_scene
                                        ),
                                        SceneOutline(
                                            scene_number=selected_scene,
                                            summary="Placeholder Scene Outline",
                                        ),
                                    )

                                    enhanced_part = asyncio.run(
                                        scene_part_generator.enhance(
                                            current_part_text,
                                            selected_part,
                                            book_spec,
                                            chapter_outline,
                                            scene_outline_full,
                                        )
                                    )

                                    if enhanced_part:
                                        st.session_state.scene_parts_text[
                                            selected_chapter
                                        ][selected_scene][selected_part] = enhanced_part
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
                                            f"Part {selected_part} of Scene {selected_scene}, Chapter {selected_chapter} enhanced and Project Autosaved!"
                                        )
                                        st.rerun()
                                    else:
                                        st.error(
                                            f"Failed to enhance Part {selected_part} of Scene {selected_scene}, Chapter {selected_chapter}."
                                        )
                            else:
                                st.error(
                                    "Generator or context data not properly initialized."
                                )
                    else:
                        st.write("No parts available to enhance in this scene yet.")
                else:
                    st.write("No scenes available to enhance in this chapter yet.")
            else:
                st.write("No chapters with scene parts available to enhance yet.")

    if st.session_state.scene_parts_text:
        st.subheader("Scene Parts Text (Generated)")
        for (
            chapter_number,
            scene_parts_chapter,
        ) in st.session_state.scene_parts_text.items():
            st.markdown(f"**Chapter {chapter_number}**")
            for scene_number, scene_parts in scene_parts_chapter.items():
                st.markdown(f"  **Scene {scene_number}:**")
                for part_number, part_text in scene_parts.items():
                    st.markdown(f"    **Part {part_number}:**")
                    st.write(part_text)