# fiction-fabricator/src/export.py

"""
Module for handling export functionality within the writing application.
Allows the user to export a table of contents or chapters in Markdown format.
"""
import json
import os

import streamlit as st


def export_management():
    """
    Provides options for exporting project data, including table of contents
    and individual chapters as Markdown files.
    """
    st.header("Export")

    # Get project path
    project_path = os.getcwd()
    outline_file = os.path.join(project_path, "outline", "outline.json")
    chapters_dir = os.path.join(project_path, "chapters")

    # Options for export
    choice = st.selectbox(
        "Select an option", ["Table of Contents", "Export to Markdown"]
    )

    if choice == "Table of Contents":
        try:
            # Attempt to load the outline data
            with open(outline_file, "r", encoding="utf-8") as f:
                outline_data = json.load(f)

            # Generate the table of contents (TOC) text
            toc_text = "# Table of Contents\n\n"
            for i, chapter in enumerate(outline_data):
                toc_text += f"{i+1}. {chapter}\n"
            st.write(toc_text)

            # Allow the user to download the TOC as a Markdown file
            st.download_button(
                label="Download Table of Contents",
                data=toc_text,
                file_name="table_of_contents.md",
                mime="text/markdown",
            )

        except FileNotFoundError:
            st.error("Outline file not found. Please generate an outline first.")

    elif choice == "Export to Markdown":
        # Allow user to select from available chapter files
        chapter_files = [f for f in os.listdir(chapters_dir) if f.endswith(".txt")]
        selected_chapter = st.selectbox("Select chapter to export:", chapter_files)

        if selected_chapter:
            chapter_file = os.path.join(chapters_dir, selected_chapter)

            try:
                # Attempt to open and read the selected chapter file
                with open(chapter_file, "r", encoding="utf-8") as f:
                    chapter_text = f.read()

                # Provide a download button for the selected chapter in Markdown format
                st.download_button(
                    label=f"Download {selected_chapter[:-4]}",
                    data=chapter_text,
                    file_name=selected_chapter,
                    mime="text/markdown",
                )
            except FileNotFoundError:
                st.error(f"Chapter file '{selected_chapter}' not found.")
