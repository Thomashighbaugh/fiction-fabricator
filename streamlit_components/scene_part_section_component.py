# streamlit_components/scene_part_section_component.py
import streamlit as st
import asyncio


def scene_part_ui(session_state):
    """
    Creates the Scene Part Generation section.
    """
    if session_state.scene_outlines and session_state.chapter_outlines_27_method:
        st.subheader("✍️ 5. Scene Part Generation")
        st.caption("Generate parts of scenes to gradually build your novel's text.")

        chapter_options = [
            f"Chapter {co.chapter_number}: {co.role}"
            for co in session_state.chapter_outlines_27_method
        ]
        selected_chapter_index = st.selectbox(
            "Select Chapter for Scene Part Generation:",
            options=range(len(chapter_options)),
            format_func=lambda index: chapter_options[index],
            key="scene_part_chapter_selectbox",
        )
        selected_chapter_outline = session_state.chapter_outlines_27_method[
            selected_chapter_index
        ]

        scene_options = [
            f"Scene {so.scene_number}: {so.summary[:50]}..."
            for so in session_state.scene_outlines.get(
                selected_chapter_outline.chapter_number, []
            )
        ]
        if scene_options:
            selected_scene_index = st.selectbox(
                "Select Scene for Part Generation:",
                options=range(len(scene_options)),
                format_func=lambda index: scene_options[index],
                key="scene_part_scene_selectbox",
            )
            selected_scene_outline = session_state.scene_outlines[
                selected_chapter_outline.chapter_number
            ][selected_scene_index]

            part_number = st.number_input(
                "Part Number:",
                min_value=1,
                value=1,
                step=1,
                key="scene_part_number_input",
            )

            if st.button("✨ Generate Scene Part", key="generate_scene_part_button"):
                with st.spinner(
                    f"Generating Part {part_number} of Scene {selected_scene_outline.scene_number}..."
                ):
                    scene_part_text = asyncio.run(
                        session_state.content_generator.generate_scene_part(
                            scene_outline=selected_scene_outline,
                            part_number=part_number,
                            book_spec=session_state.book_spec,
                            chapter_outline=selected_chapter_outline,
                            scene_outline_full=selected_scene_outline,
                            session_state=session_state,  # Pass session_state
                        )
                    )
                    if scene_part_text:
                        st.session_state.scene_parts.setdefault(
                            selected_chapter_outline.chapter_number, {}
                        ).setdefault(selected_scene_outline.scene_number, {})[
                            part_number
                        ] = scene_part_text
                        st.success(
                            f"Part {part_number} of Scene {selected_scene_outline.scene_number} Generated! 🎉"
                        )
                        # REMOVED redundant save:  session_state.project_manager.save_project()
                    else:
                        st.error(
                            f"Failed to generate Part {part_number} of Scene {selected_scene_outline.scene_number}. 😞"
                        )

            if (
                st.session_state.scene_parts.get(
                    selected_chapter_outline.chapter_number, {}
                )
                .get(selected_scene_outline.scene_number, {})
                .get(part_number)
            ):
                st.subheader(
                    f"📝 Part {part_number} of Scene {selected_scene_outline.scene_number} Preview"
                )
                st.write(
                    st.session_state.scene_parts[
                        selected_chapter_outline.chapter_number
                    ][selected_scene_outline.scene_number][part_number]
                )
        else:
            st.info(
                "Generate Scene Outlines first in '4. Scene Outlines' section to generate Scene Parts."
            )