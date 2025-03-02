# streamlit_app/components/plot_outline_view.py
import streamlit as st
import asyncio
from core.plot_outline import PlotOutline
from typing import Optional
from core.content_generation.plot_outline_generator import PlotOutlineGenerator


def plot_outline_display(
    plot_outline: Optional[PlotOutline], plot_outline_generator: PlotOutlineGenerator
):
    """
    Displays the Plot Outline data, provides editing capabilities,
    and includes "Generate" and "Enhance" buttons with autosave.
    """
    st.subheader("Plot Outline")

    if not plot_outline:
        if st.button(
            "Generate Plot Outline",
            key="generate_plot_outline_button",
            disabled=st.session_state.plot_outline is not None
            or st.session_state.book_spec is None,
        ):
            if st.session_state.book_spec and plot_outline_generator:
                with st.spinner("Generating Plot Outline..."):
                    generated_outline = asyncio.run(
                        plot_outline_generator.generate(st.session_state.book_spec)
                    )
                if generated_outline:
                    st.session_state.plot_outline = generated_outline
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
                    st.success("Plot Outline Generated and Project Autosaved!")
                    st.rerun()
                else:
                    st.error("Failed to generate Plot Outline.")
            else:
                st.warning(
                    "Book Specification is required to generate Plot Outline. Please generate Book Spec first."
                )
    else:
        with st.expander("Edit Plot Outline", expanded=True):
            with st.form("plot_outline_form"):
                plot_outline.act_one = st.text_area(
                    "Act One: Setup",
                    plot_outline.act_one,
                    height=150,
                    key="act_one_input",
                )
                plot_outline.act_two = st.text_area(
                    "Act Two: Confrontation",
                    plot_outline.act_two,
                    height=200,
                    key="act_two_input",
                )
                plot_outline.act_three = st.text_area(
                    "Act Three: Resolution",
                    plot_outline.act_three,
                    height=150,
                    key="act_three_input",
                )

                col_save_enhance, _ = st.columns([3, 1])
                with col_save_enhance:
                    if st.form_submit_button(
                        "Save Plot Outline (Manual Edit)",
                        key="save_plot_outline_button",
                    ):
                        st.session_state.plot_outline = PlotOutline(
                            act_one=plot_outline.act_one,
                            act_two=plot_outline.act_two,
                            act_three=plot_outline.act_three,
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
                            "Plot Outline Saved (Manual Edit) and Project Autosaved!"
                        )
                with _:
                    if st.form_submit_button(
                        "Enhance Plot Outline", key="enhance_plot_outline_button"
                    ):
                        if plot_outline and plot_outline_generator:
                            with st.spinner("Enhancing Plot Outline..."):
                                enhanced_outline_raw = asyncio.run(
                                    plot_outline_generator.enhance(
                                        "\n".join(
                                            [
                                                "Act One:\n" + plot_outline.act_one,
                                                "Act Two:\n" + plot_outline.act_two,
                                                "Act Three:\n" + plot_outline.act_three,
                                            ]
                                        )
                                    )
                                )
                            if enhanced_outline_raw:
                                st.session_state.plot_outline = enhanced_outline_raw
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
                                    "Plot Outline Enhanced and Project Autosaved!"
                                )
                                st.rerun()
                            else:
                                st.error("Failed to enhance Plot Outline.")
                        else:
                            st.warning("No Plot Outline available to enhance.")

        st.write("Plot Outline:")
        if plot_outline:
            st.text(
                f"Act One: {plot_outline.act_one}\n\n"
                f"Act Two: {plot_outline.act_two}\n\n"
                f"Act Three: {plot_outline.act_three}"
            )
        else:
            st.info("No Plot Outline generated yet.")
