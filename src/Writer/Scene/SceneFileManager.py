#!/usr/bin/python3
# File: Writer/Scene/SceneFileManager.py
# Purpose: Manages individual scene and chapter file creation and stitching

import os
import json
import re
from typing import List, Dict, Any
from Writer.NarrativeContext import NarrativeContext, ChapterContext, SceneContext
from Writer.PrintUtils import Logger


class SceneFileManager:
    """Manages the creation and organization of individual scene and chapter files."""
    
    def __init__(self, logger: Logger, base_output_dir: str, story_name: str):
        self.logger = logger
        self.base_output_dir = base_output_dir
        self.story_name = story_name
        self.story_dir = os.path.join(base_output_dir, story_name)
        self.scenes_dir = os.path.join(self.story_dir, "scenes")
        self.chapters_dir = os.path.join(self.story_dir, "chapters")
        
        # Create directories
        os.makedirs(self.scenes_dir, exist_ok=True)
        os.makedirs(self.chapters_dir, exist_ok=True)
        
        self.logger.Log(f"Initialized SceneFileManager for '{story_name}'", 3)
        self.logger.Log(f"Scenes directory: {self.scenes_dir}", 2)
        self.logger.Log(f"Chapters directory: {self.chapters_dir}", 2)

    def save_scene_file(self, scene_context: SceneContext, chapter_num: int, word_count: int = None) -> str:
        """Saves an individual scene to its own markdown file."""
        scene_filename = f"Chapter_{chapter_num:02d}_Scene_{scene_context.scene_number:02d}.md"
        scene_path = os.path.join(self.scenes_dir, scene_filename)
        
        if word_count is None:
            word_count = len(scene_context.generated_content.split())
        
        # Create scene metadata
        scene_metadata = f"""---
title: Chapter {chapter_num}, Scene {scene_context.scene_number}
chapter: {chapter_num}
scene: {scene_context.scene_number}
word_count: {word_count}
outline: |
  {scene_context.initial_outline}
summary: |
  {scene_context.final_summary or 'No summary available'}
key_points: {scene_context.key_points_for_next_scene}
pieces_count: {len(scene_context.pieces)}
---

"""
        
        # Create scene content with header
        scene_content = f"# Chapter {chapter_num}, Scene {scene_context.scene_number}\n\n"
        scene_content += scene_context.generated_content
        
        # Add piece breakdown if available
        if scene_context.pieces:
            scene_content += f"\n\n---\n\n## Scene Breakdown\n\n"
            for i, piece in enumerate(scene_context.pieces, 1):
                piece_word_count = len(piece['content'].split())
                scene_content += f"### Piece {i} ({piece_word_count} words)\n\n"
                if piece.get('summary'):
                    scene_content += f"**Summary:** {piece['summary']}\n\n"
                scene_content += f"{piece['content']}\n\n"
        
        # Write the complete scene file
        full_content = scene_metadata + scene_content
        
        try:
            with open(scene_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            self.logger.Log(f"Saved scene file: {scene_filename} ({word_count} words)", 3)
            return scene_path
        except Exception as e:
            self.logger.Log(f"Error saving scene file {scene_filename}: {e}", 7)
            return None

    def stitch_chapter_from_scenes(self, chapter_context: ChapterContext) -> str:
        """Stitches together all scenes in a chapter to create a chapter file."""
        chapter_filename = f"Chapter_{chapter_context.chapter_number:02d}.md"
        chapter_path = os.path.join(self.chapters_dir, chapter_filename)
        
        # Calculate total word count
        total_words = len(chapter_context.generated_content.split())
        
        # Create chapter metadata
        chapter_metadata = f"""---
title: Chapter {chapter_context.chapter_number}
chapter: {chapter_context.chapter_number}
word_count: {total_words}
scenes_count: {len(chapter_context.scenes)}
outline: |
  {chapter_context.initial_outline}
summary: |
  {chapter_context.summary or 'No summary available'}
---

"""
        
        # Create chapter content
        chapter_content = f"# Chapter {chapter_context.chapter_number}\n\n"
        
        # Add chapter content (already stitched from scenes)
        chapter_content += chapter_context.generated_content
        
        # Add scene breakdown section
        if chapter_context.scenes:
            chapter_content += f"\n\n---\n\n## Scene Breakdown\n\n"
            for i, scene in enumerate(chapter_context.scenes, 1):
                scene_word_count = len(scene.generated_content.split())
                chapter_content += f"### Scene {i} ({scene_word_count} words)\n\n"
                if scene.final_summary:
                    chapter_content += f"**Summary:** {scene.final_summary}\n\n"
                if scene.key_points_for_next_scene:
                    chapter_content += f"**Key Points:** {', '.join(scene.key_points_for_next_scene)}\n\n"
                chapter_content += f"**Outline:** {scene.initial_outline}\n\n"
        
        # Write the complete chapter file
        full_content = chapter_metadata + chapter_content
        
        try:
            with open(chapter_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            self.logger.Log(f"Saved chapter file: {chapter_filename} ({total_words} words)", 4)
            return chapter_path
        except Exception as e:
            self.logger.Log(f"Error saving chapter file {chapter_filename}: {e}", 7)
            return None

    def stitch_book_from_chapters(self, narrative_context: NarrativeContext, title: str = None) -> str:
        """Stitches together all chapters to create the final book file."""
        if not title:
            title = self.story_name.replace('_', ' ').title()
        
        book_filename = f"{self.story_name}_Complete_Book.md"
        book_path = os.path.join(self.story_dir, book_filename)
        
        # Calculate total statistics
        total_words = 0
        total_scenes = 0
        for chapter in narrative_context.chapters:
            total_words += len(chapter.generated_content.split())
            total_scenes += len(chapter.scenes)
        
        # Create book metadata
        book_metadata = f"""---
title: {title}
total_chapters: {len(narrative_context.chapters)}
total_scenes: {total_scenes}
total_word_count: {total_words}
story_type: {narrative_context.story_type or 'unknown'}
generated_by: Fiction Fabricator
generation_date: {self._get_current_timestamp()}
initial_prompt: |
  {narrative_context.initial_prompt}
---

"""
        
        # Create book content
        book_content = f"# {title}\n\n"
        
        # Add table of contents
        book_content += "## Table of Contents\n\n"
        for chapter in narrative_context.chapters:
            chapter_title = f"Chapter {chapter.chapter_number}"
            book_content += f"- [{chapter_title}](#chapter-{chapter.chapter_number})\n"
        book_content += "\n"
        
        # Add all chapter content
        for chapter in narrative_context.chapters:
            book_content += f"## Chapter {chapter.chapter_number}\n\n"
            book_content += chapter.generated_content
            book_content += "\n\n---\n\n"
        
        # Add appendix with generation statistics
        book_content += "## Generation Statistics\n\n"
        book_content += f"- **Total Word Count:** {total_words:,} words\n"
        book_content += f"- **Total Chapters:** {len(narrative_context.chapters)}\n"
        book_content += f"- **Total Scenes:** {total_scenes}\n"
        book_content += f"- **Story Type:** {narrative_context.story_type or 'Unknown'}\n"
        book_content += f"- **Generated:** {self._get_current_timestamp()}\n\n"
        
        # Chapter breakdown
        book_content += "### Chapter Breakdown\n\n"
        for chapter in narrative_context.chapters:
            chapter_words = len(chapter.generated_content.split())
            book_content += f"- **Chapter {chapter.chapter_number}:** {chapter_words:,} words, {len(chapter.scenes)} scenes\n"
        
        # Write the complete book file
        full_content = book_metadata + book_content
        
        try:
            with open(book_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            self.logger.Log(f"Saved complete book: {book_filename} ({total_words:,} words)", 5)
            return book_path
        except Exception as e:
            self.logger.Log(f"Error saving book file {book_filename}: {e}", 7)
            return None

    def create_generation_report(self, narrative_context: NarrativeContext) -> str:
        """Creates a detailed generation report with all files and statistics."""
        report_filename = f"{self.story_name}_Generation_Report.md"
        report_path = os.path.join(self.story_dir, report_filename)
        
        # Collect file statistics
        scene_files = []
        chapter_files = []
        
        for chapter in narrative_context.chapters:
            chapter_file = f"Chapter_{chapter.chapter_number:02d}.md"
            chapter_files.append(chapter_file)
            
            for scene in chapter.scenes:
                scene_file = f"Chapter_{chapter.chapter_number:02d}_Scene_{scene.scene_number:02d}.md"
                scene_files.append(scene_file)
        
        # Create report content
        report_content = f"""# Generation Report: {self.story_name.replace('_', ' ').title()}

## Summary
- **Generation Date:** {self._get_current_timestamp()}
- **Total Chapters:** {len(narrative_context.chapters)}
- **Total Scenes:** {sum(len(ch.scenes) for ch in narrative_context.chapters)}
- **Total Word Count:** {sum(len(ch.generated_content.split()) for ch in narrative_context.chapters):,} words

## File Structure

### Complete Book
- `{self.story_name}_Complete_Book.md` - The complete stitched book

### Individual Chapters ({len(chapter_files)} files)
```
chapters/
"""
        
        for chapter_file in chapter_files:
            report_content += f"├── {chapter_file}\n"
        
        report_content += f"""```

### Individual Scenes ({len(scene_files)} files)
```
scenes/
"""
        
        for scene_file in scene_files:
            report_content += f"├── {scene_file}\n"
        
        report_content += """```

## Chapter Details

"""
        
        for chapter in narrative_context.chapters:
            chapter_words = len(chapter.generated_content.split())
            report_content += f"### Chapter {chapter.chapter_number} ({chapter_words:,} words)\n\n"
            
            if chapter.scenes:
                for scene in chapter.scenes:
                    scene_words = len(scene.generated_content.split())
                    report_content += f"- **Scene {scene.scene_number}:** {scene_words:,} words\n"
                    if scene.final_summary:
                        report_content += f"  - Summary: {scene.final_summary[:100]}...\n"
            report_content += "\n"
        
        report_content += """
## Error Resilience Features

This generation process creates individual files for each scene and chapter to prevent data loss:

1. **Scene Files:** Each scene is saved individually with full metadata
2. **Chapter Files:** Chapters are stitched from scenes and saved separately  
3. **Complete Book:** Final book is assembled from all chapters
4. **Incremental Progress:** If generation fails, completed scenes/chapters are preserved

## File Recovery

If the generation process is interrupted:
- Individual scene files in `scenes/` contain all completed scenes
- Individual chapter files in `chapters/` contain all completed chapters  
- The complete book file can be manually reconstructed from chapter files
- All files include metadata for easy identification and reconstruction
"""
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            self.logger.Log(f"Saved generation report: {report_filename}", 4)
            return report_path
        except Exception as e:
            self.logger.Log(f"Error saving generation report: {e}", 7)
            return None

    def _get_current_timestamp(self) -> str:
        """Returns current timestamp in readable format."""
        import datetime
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def get_all_output_files(self) -> Dict[str, List[str]]:
        """Returns a dictionary of all generated files organized by type."""
        files = {
            'scenes': [],
            'chapters': [], 
            'book': [],
            'reports': []
        }
        
        try:
            # List scene files
            if os.path.exists(self.scenes_dir):
                files['scenes'] = [f for f in os.listdir(self.scenes_dir) if f.endswith('.md')]
            
            # List chapter files
            if os.path.exists(self.chapters_dir):
                files['chapters'] = [f for f in os.listdir(self.chapters_dir) if f.endswith('.md')]
            
            # List book and report files
            if os.path.exists(self.story_dir):
                for f in os.listdir(self.story_dir):
                    if f.endswith('_Complete_Book.md'):
                        files['book'].append(f)
                    elif f.endswith('_Generation_Report.md'):
                        files['reports'].append(f)
        
        except Exception as e:
            self.logger.Log(f"Error listing output files: {e}", 6)
        
        return files