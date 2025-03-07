# streamlit_components/scene_outline_section_component.py
import streamlit as st
import random
import asyncio

from core.plot_outline import SceneOutline


def scene_outline_ui(session_state):
    """
    Creates the Scene Outlines section in the Streamlit application with enhanced styling.

    Args:
        session_state: Streamlit session state object.
    """
    if (
        session_state.chapter_outlines_27_method
        and len(session_state.chapter_outlines_27_method) > 0
    ):
        st.subheader("🎬 4. Scene Outlines")  # Added emoji and subheader styling
        st.caption(
            "Outline scenes for each chapter to detail the story's progression."
        )  # Added caption

        session_state.max_scenes_per_chapter = st.number_input(
            "Maximum Scenes per Chapter:",
            min_value=3,
            max_value=10,
            value=session_state.max_scenes_per_chapter,
            step=1,
        )

        chapter_options = [
            f"Chapter {co.chapter_number}: {co.role}"
            for co in session_state.chapter_outlines_27_method
        ]
        session_state.current_chapter_index = st.selectbox(
            "Select Chapter for Scene Outlines:",
            options=range(len(chapter_options)),
            format_func=lambda index: chapter_options[index],
        )
        selected_chapter_outline = session_state.chapter_outlines_27_method[
            session_state.current_chapter_index
        ]

        if st.button(
            f"✨ Generate Scene Outlines for {chapter_options[session_state.current_chapter_index]}",  # Added emoji
            disabled=session_state.scene_outlines.get(
                selected_chapter_outline.chapter_number
            ),
        ):
            with st.spinner(
                f"Generating Scene Outlines for {chapter_options[session_state.current_chapter_index]}..."
            ):
                num_scenes = random.randint(2, session_state.max_scenes_per_chapter)
                scene_outlines = asyncio.run(
                    session_state.content_generator.generate_scene_outlines(
                        selected_chapter_outline, num_scenes
                    )
                )
                if scene_outlines:
                    session_state.scene_outlines[
                        selected_chapter_outline.chapter_number
                    ] = scene_outlines
                    st.success(
                        f"Scene Outlines Generated for {chapter_options[session_state.current_chapter_index]}! 🎉"  # Added emoji
                    )
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
                        f"Failed to generate Scene Outlines for {chapter_options[session_state.current_chapter_index]}. 😞"  # Added emoji
                    )

        if session_state.scene_outlines.get(selected_chapter_outline.chapter_number):
            chapter_scene_outlines = session_state.scene_outlines[
                selected_chapter_outline.chapter_number
            ]
            with st.form(
                f"scene_outlines_chapter_{selected_chapter_outline.chapter_number}_form"
            ):
                st.subheader(
                    f"✏️ Edit Scene Outlines - {chapter_options[session_state.current_chapter_index]}"
                )  # Added subheader for edit form
                edited_scene_outlines = []
                for i, scene_outline in enumerate(chapter_scene_outlines):
                    edited_summary = st.text_area(
                        f"Scene {i + 1} Outline",
                        scene_outline.summary,
                        height=80,
                        key=f"scene_{selected_chapter_outline.chapter_number}_{i}_outline",
                    )
                    edited_scene_outlines.append(
                        SceneOutline(scene_number=i + 1, summary=edited_summary)
                    )

                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.form_submit_button(
                        f"💾 Save Scene Outlines (Chapter {selected_chapter_outline.chapter_number})"  # Added emoji
                    ):
                        session_state.scene_outlines[
                            selected_chapter_outline.chapter_number
                        ] = edited_scene_outlines
                        st.success(
                            f"Scene Outlines Saved for Chapter {selected_chapter_outline.chapter_number}! ✅"  # Added emoji
                        )
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
                        f"✨ Enhance Scene Outlines (Chapter {chapter_options[session_state.current_chapter_index]})"  # Added emoji
                    ):

                        async def enhance_scene_outlines_callback():
                            with st.spinner(
                                f"Enhancing Scene Outlines for Chapter {chapter_options[session_state.current_chapter_index]}..."
                            ):
                                enhanced_scene_outlines = await session_state.content_generator.enhance_scene_outlines(
                                    edited_scene_outlines
                                )
                                if enhanced_scene_outlines:
                                    session_state.scene_outlines[
                                        selected_chapter_outline.chapter_number
                                    ] = enhanced_scene_outlines
                                    st.success(
                                        f"Scene Outlines Enhanced for Chapter {chapter_options[session_state.current_chapter_index]}! 🚀"  # Added emoji
                                    )
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
                                        f"Failed to enhance Scene Outlines for Chapter {chapter_options[session_state.current_chapter_index]}. 😞"  # Added emoji
                                    )

                        asyncio.run(enhance_scene_outlines_callback())

            st.subheader(
                f"📖 Scene Outlines Preview - {chapter_options[session_state.current_chapter_index]}"
            )  # Added subheader for preview section
            st.caption(
                "Review the scene outlines for the selected chapter."
            )  # Added caption
            for scene_outline in session_state.scene_outlines.get(
                selected_chapter_outline.chapter_number, []
            ):
                st.markdown(f"**Scene {scene_outline.scene_number}:**")
                st.write(scene_outline.summary)
    else:
        st.info(
            "No Chapter Outlines available. Please generate them in the '3. 27 Chapter Outline' section."
        )  # Changed to st.info and more informative message
