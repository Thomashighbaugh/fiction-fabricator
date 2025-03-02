# streamlit_app/components/book_text_view.py
import streamlit as st
from typing import Optional, Dict
import zipfile
import io
import re  # Import the regular expression library


def book_text_display(book_text: Optional[str]):
    """
    Displays the assembled book text and provides a save function
    to save the book in markdown format (chapters in separate files, zipped),
    using the book title for naming.
    """
    st.subheader("Generated Book Text")
    if book_text:
        st.markdown(book_text)

        if st.button("Save Book as Markdown"):
            if (
                book_text and st.session_state.book_spec
            ):  # Ensure book_text and book_spec are available
                book_title = st.session_state.book_spec.title
                if not book_title:
                    book_title = (
                        "untitled_book"  # Default title if book_spec.title is missing
                    )
                else:
                    book_title = sanitize_filename(
                        book_title
                    )  # Sanitize title for filename

                # Split book text into chapters
                chapters = split_book_into_chapters(book_text)

                # Create in-memory zip file
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zipf:
                    for chapter_num, chapter_text in chapters.items():
                        # Create markdown file for each chapter in memory
                        chapter_markdown = io.StringIO()
                        chapter_markdown.write(chapter_text)
                        chapter_filename = f"{book_title}_chapter_{chapter_num}.md"  # Filename with book title
                        zipf.writestr(chapter_filename, chapter_markdown.getvalue())

                zip_file = zip_buffer.getvalue()

                st.download_button(
                    label="Download Book Chapters (ZIP)",
                    data=zip_file,
                    file_name=f"{book_title}_chapters.zip",  # Zip filename with book title
                    mime="application/zip",
                    on_click=None,
                    disabled=False,
                )
            else:
                st.warning(
                    "No book text or book specification available to save."
                )  # Inform user if book_spec is missing

    else:
        st.info(
            "No book text generated yet. Generate scene parts and assemble the book to view it here."
        )


def split_book_into_chapters(book_text: str) -> Dict[int, str]:
    """
    Splits the full book text into a dictionary of chapters,
    keyed by chapter number.
    """
    chapters = {}
    chapter_split = book_text.split("# Chapter ")
    for i, chapter_content in enumerate(
        chapter_split[1:], start=1
    ):  # Start from 1 to skip preamble and number chapters from 1
        chapter_number_str, chapter_text = chapter_content.split(
            "\n", 1
        )  # split at the first newline to separate chapter number from text
        try:
            chapter_number = int(
                chapter_number_str.strip()
            )  # chapter number is the first line
        except ValueError:
            chapter_number = (
                i  # if chapter number is not properly parsed, use index as fallback
            )
        chapters[chapter_number] = (
            f"# Chapter {chapter_number}\n" + chapter_text.strip()
        )  # Re-add chapter heading to each chapter

    return chapters


def sanitize_filename(title: str) -> str:
    """
    Sanitizes a string to be used as a filename by replacing spaces and
    non-alphanumeric characters with underscores.
    """
    sanitized_title = re.sub(r"\s+", "_", title)  # Replace spaces with underscores
    sanitized_title = re.sub(
        r"[^\w.-]", "", sanitized_title
    )  # Remove non-alphanumeric, period, hyphen chars
    return sanitized_title
