# core/output_formatter.py
from typing import Dict, List
import zipfile
import os

from core.book_spec import BookSpec
from core.plot_outline import PlotOutline, ChapterOutline, SceneOutline
from core.content_generator import ChapterOutlineMethod
from utils.file_handler import save_markdown
from utils.logger import logger
from utils.config import config


class OutputFormatter:
    """
    Handles the formatting and output of project data to Markdown files and a zip archive.
    """

    def __init__(self):
        pass  # Nothing needed

    def generate_markdown_files(
        self,
        project_name: str,
        project_directory: str,
        story_idea: str,
        book_spec: BookSpec,
        plot_outline: PlotOutline,
        chapter_outlines_27_method: List[ChapterOutlineMethod],
        scene_outlines: Dict[int, List[SceneOutline]],
        scene_parts: Dict[int, Dict[int, str]],
    ) -> None:
        """
        Generates individual Markdown files for each component of the project.
        """
        output_dir = os.path.join(project_directory, project_name)
        os.makedirs(output_dir, exist_ok=True)

        # Save story idea
        save_markdown(story_idea, os.path.join(output_dir, "story_idea.md"))

        # Save book spec
        book_spec_md = f"# Book Specification\n\n"
        book_spec_md += f"**Title:** {book_spec.title}\n\n"
        book_spec_md += f"**Genre:** {book_spec.genre}\n\n"
        book_spec_md += f"**Setting:** {book_spec.setting}\n\n"
        book_spec_md += f"**Themes:** {', '.join(book_spec.themes)}\n\n"
        book_spec_md += f"**Tone:** {book_spec.tone}\n\n"
        book_spec_md += f"**Point of View:** {book_spec.point_of_view}\n\n"
        book_spec_md += f"**Characters:**\n"
        for char in book_spec.characters:
            book_spec_md += f"  - {char}\n"
        book_spec_md += f"\n**Premise:** {book_spec.premise}\n"
        save_markdown(book_spec_md, os.path.join(output_dir, "book_spec.md"))

        # Save plot outline.
        plot_outline_md = f"# Plot Outline\n\n"
        if plot_outline:
            plot_outline_md += f"## Act One:\n\n"
            for item in plot_outline.act_one:
                plot_outline_md += f"- {item}\n"
            plot_outline_md += f"\n## Act Two:\n\n"
            for item in plot_outline.act_two:
                plot_outline_md += f"- {item}\n"
            plot_outline_md += f"\n## Act Three:\n\n"
            for item in plot_outline.act_three:
                plot_outline_md += f"- {item}\n"

        save_markdown(plot_outline_md, os.path.join(output_dir, "plot_outline.md"))
        # Save chapter outlines (27-method)
        chapter_outlines_md = f"# Chapter Outlines (27-Chapter Method)\n\n"
        for co in chapter_outlines_27_method:
            chapter_outlines_md += (
                f"## Chapter {co.chapter_number}: {co.role}\n\n"
            )
            chapter_outlines_md += f"{co.summary}\n\n"
        save_markdown(
            chapter_outlines_md, os.path.join(output_dir, "chapter_outlines.md")
        )

        # Save scene parts
        for chapter_num, scenes in scene_outlines.items():
            chapter_dir = os.path.join(output_dir, f"chapter_{chapter_num}")
            os.makedirs(chapter_dir, exist_ok=True)
            for scene in scenes:
                scene_file_path = os.path.join(
                    chapter_dir, f"scene_{scene.scene_number}.md"
                )
                scene_md = f"# Scene {scene.scene_number}\n\n"
                scene_md += f"**Outline:** {scene.summary}\n\n"

                if scene.scene_number in scene_parts.get(chapter_num, {}):
                    for part_num, part_text in scene_parts[chapter_num][
                        scene.scene_number
                    ].items():
                        scene_md += f"## Part {part_num}\n\n"
                        scene_md += f"{part_text}\n\n"
                save_markdown(scene_md, scene_file_path)

    def create_zip_archive(self, project_name: str, project_directory: str) -> str:
        """
        Creates a zip archive containing all generated Markdown files.
        Returns the path to the created zip file.
        """
        zip_file_path = os.path.join(project_directory, f"{project_name}.zip")
        output_dir = os.path.join(project_directory, project_name)

        with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(
                        file_path, output_dir
                    )  # Relative path for archive
                    zipf.write(file_path, arcname)
        logger.info("zip file created at: %s", zip_file_path)
        return zip_file_path