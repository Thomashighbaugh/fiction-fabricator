import streamlit as st
import os
import json

def export_management():
    st.header("Export")

    # Get project path
    project_path = os.getcwd()
    outline_file = os.path.join(project_path, "outline", "outline.json")
    chapters_dir = os.path.join(project_path, "chapters")

    # Options for export
    choice = st.selectbox("Select an option", ["Table of Contents", "Export to Markdown"])

    # Table of contents
    if choice == "Table of Contents":
        try:
            with open(outline_file, "r") as f:
                outline_data = json.load(f)
            toc_text = "# Table of Contents\n\n"
            for i, chapter in enumerate(outline_data):
                toc_text += f"{i+1}. {chapter}\n"
            st.write(toc_text)

            # Allow user to download table of contents
            st.download_button(
                label="Download Table of Contents",
                data=toc_text,
                file_name="table_of_contents.md",
                mime="text/markdown"
            )
        except FileNotFoundError:
            st.error("Outline file not found. Please generate an outline first.")

    # Export to Markdown
    elif choice == "Export to Markdown":
        selected_chapter = st.selectbox("Select chapter to export:", os.listdir(chapters_dir))
        if selected_chapter.endswith(".txt"):
            chapter_file = os.path.join(chapters_dir, selected_chapter)
            try:
                with open(chapter_file, "r") as f:
                    chapter_text = f.read()

                # Allow user to download chapter
                st.download_button(
                    label=f"Download {selected_chapter[:-4]}",
                    data=chapter_text,
                    file_name=selected_chapter,
                    mime="text/markdown"
                )

            except FileNotFoundError:
                st.error(f"Chapter file '{selected_chapter}' not found.")