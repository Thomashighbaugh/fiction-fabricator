# core/content_generation/book_assembler.py
from typing import Dict


class BookAssembler:
    """
    Assembles the generated scene parts into a complete book text, ordered by chapter, scene, and part number.
    """

    def assemble_book_text(
        self, scene_parts_text: Dict[int, Dict[int, Dict[int, str]]]
    ) -> str:
        """
        Assembles scene parts into a formatted book text.
        """
        full_book_text = ""
        for chapter_num in sorted(scene_parts_text.keys()):
            full_book_text += f"# Chapter {chapter_num}\n\n"  # Chapter heading

            scene_parts_chapter = scene_parts_text[chapter_num]
            for scene_num in sorted(scene_parts_chapter.keys()):
                full_book_text += f"## Scene {scene_num}\n\n"  # Scene heading

                scene_parts = scene_parts_chapter[scene_num]
                for part_num in sorted(scene_parts.keys()):
                    part_text = scene_parts[part_num]
                    full_book_text += part_text + "\n\n"  # Add part text and spacing

        return full_book_text.strip()  # Remove leading/trailing whitespace
