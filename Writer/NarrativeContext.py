#!/usr/bin/python3

from typing import Optional, List, Dict, Any

class ScenePiece:
    """
    Holds the content and summary for a single, small generated piece of a scene.
    This is the most granular level of generated text.
    """
    def __init__(self, piece_number: int, content: str, summary: str):
        self.piece_number: int = piece_number
        self.content: str = content
        self.summary: str = summary

    def to_dict(self) -> Dict[str, Any]:
        return {
            "piece_number": self.piece_number,
            "content": self.content,
            "summary": self.summary,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScenePiece':
        return cls(data["piece_number"], data["content"], data["summary"])


class SceneContext:
    """
    Holds contextual information for a single scene, including its component pieces.
    """
    def __init__(self, scene_number: int, initial_outline: str):
        self.scene_number: int = scene_number
        self.initial_outline: str = initial_outline # The outline specific to this scene
        self.pieces: List[ScenePiece] = [] # A scene is now composed of smaller pieces
        self.final_summary: Optional[str] = None # A final, holistic summary of the assembled scene
        self.key_points_for_next_scene: List[str] = [] # Key takeaways to carry forward

    @property
    def generated_content(self) -> str:
        """Returns the full, assembled text of the scene from its pieces."""
        return "\n\n".join(piece.content for piece in sorted(self.pieces, key=lambda p: p.piece_number))

    def add_piece(self, piece_content: str, piece_summary: str):
        """Adds a new generated piece to the scene."""
        piece_number = len(self.pieces) + 1
        new_piece = ScenePiece(piece_number=piece_number, content=piece_content, summary=piece_summary)
        self.pieces.append(new_piece)

    def get_summary_of_all_pieces(self) -> str:
        """Concatenates the summaries of all pieces to provide running context."""
        return " ".join(piece.summary for piece in sorted(self.pieces, key=lambda p: p.piece_number))

    def set_final_summary(self, summary: str):
        """Sets the final, holistic summary after the scene is fully assembled."""
        self.final_summary = summary

    def add_key_point(self, point: str):
        self.key_points_for_next_scene.append(point)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_number": self.scene_number,
            "initial_outline": self.initial_outline,
            "pieces": [piece.to_dict() for piece in self.pieces],
            "final_summary": self.final_summary,
            "key_points_for_next_scene": self.key_points_for_next_scene,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SceneContext':
        scene = cls(data["scene_number"], data["initial_outline"])
        scene.pieces = [ScenePiece.from_dict(p_data) for p_data in data.get("pieces", [])]
        scene.final_summary = data.get("final_summary")
        scene.key_points_for_next_scene = data.get("key_points_for_next_scene", [])
        return scene


class ChapterContext:
    """
    Holds contextual information for a single chapter, including its scenes.
    """
    def __init__(self, chapter_number: int, initial_outline: str):
        self.chapter_number: int = chapter_number
        self.initial_outline: str = initial_outline # The outline for the entire chapter
        self.generated_content: Optional[str] = None # Full generated text of the chapter
        self.scenes: List[SceneContext] = []
        self.summary: Optional[str] = None # Summary of what happened in this chapter
        self.theme_elements: List[str] = [] # Themes specific or emphasized in this chapter
        self.character_arcs_progress: Dict[str, str] = {} # CharacterName: ProgressNote

    def add_scene(self, scene_context: SceneContext):
        self.scenes.append(scene_context)

    def get_scene(self, scene_number: int) -> Optional[SceneContext]:
        for scene in self.scenes:
            if scene.scene_number == scene_number:
                return scene
        return None

    def get_last_scene_summary(self) -> Optional[str]:
        if self.scenes:
            return self.scenes[-1].final_summary
        return None

    def set_generated_content(self, content: str):
        self.generated_content = content

    def set_summary(self, summary: str):
        self.summary = summary

    def add_theme_element(self, theme: str):
        self.theme_elements.append(theme)

    def update_character_arc(self, character_name: str, progress_note: str):
        self.character_arcs_progress[character_name] = progress_note

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chapter_number": self.chapter_number,
            "initial_outline": self.initial_outline,
            "generated_content": self.generated_content,
            "scenes": [scene.to_dict() for scene in self.scenes],
            "summary": self.summary,
            "theme_elements": self.theme_elements,
            "character_arcs_progress": self.character_arcs_progress,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChapterContext':
        chapter = cls(data["chapter_number"], data["initial_outline"])
        chapter.generated_content = data.get("generated_content")
        chapter.scenes = [SceneContext.from_dict(s_data) for s_data in data.get("scenes", [])]
        chapter.summary = data.get("summary")
        chapter.theme_elements = data.get("theme_elements", [])
        chapter.character_arcs_progress = data.get("character_arcs_progress", {})
        return chapter


class NarrativeContext:
    """
    Manages and stores the overall narrative context for the entire novel.
    This includes premise, themes, and records of generated chapters and scenes.
    """
    def __init__(self, initial_prompt: str, style_guide: str, overall_theme: Optional[str] = None):
        self.initial_prompt: str = initial_prompt
        self.style_guide: str = style_guide # The guiding principles for the novel's tone and prose
        self.story_elements_markdown: Optional[str] = None # From StoryElements.py
        self.base_novel_outline_markdown: Optional[str] = None # The rough overall outline
        self.expanded_novel_outline_markdown: Optional[str] = None # Detailed, chapter-by-chapter
        self.base_prompt_important_info: Optional[str] = None # Extracted by OutlineGenerator

        self.overall_theme: Optional[str] = overall_theme
        self.motifs: List[str] = []
        self.chapters: List[ChapterContext] = []
        self.generation_log: List[str] = [] # Log of significant generation events or decisions

    def set_story_elements(self, elements_md: str):
        self.story_elements_markdown = elements_md

    def set_base_novel_outline(self, outline_md: str):
        self.base_novel_outline_markdown = outline_md

    def set_expanded_novel_outline(self, outline_md: str):
        self.expanded_novel_outline_markdown = outline_md

    def set_base_prompt_important_info(self, info: str):
        self.base_prompt_important_info = info

    def add_motif(self, motif: str):
        self.motifs.append(motif)

    def add_chapter(self, chapter_context: ChapterContext):
        self.chapters.append(chapter_context)
        self.chapters.sort(key=lambda c: c.chapter_number) # Keep chapters sorted

    def get_chapter(self, chapter_number: int) -> Optional[ChapterContext]:
        for chapter in self.chapters:
            if chapter.chapter_number == chapter_number:
                return chapter
        return None

    def get_previous_chapter_summary(self, current_chapter_number: int) -> Optional[str]:
        if current_chapter_number <= 1:
            return None
        prev_chapter = self.get_chapter(current_chapter_number - 1)
        if prev_chapter:
            return prev_chapter.summary
        return None

    def get_all_previous_chapter_summaries(self, current_chapter_number: int) -> List[Dict[str, Any]]:
        summaries = []
        for i in range(1, current_chapter_number):
            chapter = self.get_chapter(i)
            if chapter and chapter.summary:
                summaries.append({
                    "chapter_number": chapter.chapter_number,
                    "summary": chapter.summary
                })
        return summaries

    def get_full_story_summary_so_far(self, current_chapter_number: Optional[int] = None) -> str:
        """
        Concatenates summaries of all chapters up to (but not including) current_chapter_number.
        If current_chapter_number is None, summarizes all chapters.
        """
        relevant_chapters = self.chapters
        if current_chapter_number is not None:
            relevant_chapters = [ch for ch in self.chapters if ch.chapter_number < current_chapter_number]

        full_summary = ""
        if self.overall_theme:
            full_summary += f"Overall Theme: {self.overall_theme}\n"
        if self.motifs:
            full_summary += f"Key Motifs: {', '.join(self.motifs)}\n"

        full_summary += "\nPrevious Chapter Summaries:\n"
        for chapter in relevant_chapters:
            if chapter.summary:
                full_summary += f"\nChapter {chapter.chapter_number} Summary:\n{chapter.summary}\n"
            if chapter.character_arcs_progress:
                full_summary += f"Character Arc Notes for Chapter {chapter.chapter_number}:\n"
                for char, prog in chapter.character_arcs_progress.items():
                    full_summary += f"  - {char}: {prog}\n"
        return full_summary

    def log_event(self, event_description: str):
        self.generation_log.append(event_description)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "initial_prompt": self.initial_prompt,
            "style_guide": self.style_guide,
            "story_elements_markdown": self.story_elements_markdown,
            "base_novel_outline_markdown": self.base_novel_outline_markdown,
            "expanded_novel_outline_markdown": self.expanded_novel_outline_markdown,
            "base_prompt_important_info": self.base_prompt_important_info,
            "overall_theme": self.overall_theme,
            "motifs": self.motifs,
            "chapters": [chapter.to_dict() for chapter in self.chapters],
            "generation_log": self.generation_log,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NarrativeContext':
        # Import here to avoid circular dependency with Prompts.py
        from Writer.Prompts import LITERARY_STYLE_GUIDE
        # Provide a default style guide if it's missing from older JSON files
        style_guide = data.get("style_guide", LITERARY_STYLE_GUIDE)
        context = cls(data["initial_prompt"], style_guide, data.get("overall_theme"))
        context.story_elements_markdown = data.get("story_elements_markdown")
        context.base_novel_outline_markdown = data.get("base_novel_outline_markdown")
        context.expanded_novel_outline_markdown = data.get("expanded_novel_outline_markdown")
        context.base_prompt_important_info = data.get("base_prompt_important_info")
        context.motifs = data.get("motifs", [])
        context.chapters = [ChapterContext.from_dict(ch_data) for ch_data in data.get("chapters", [])]
        context.generation_log = data.get("generation_log", [])
        return context

    def get_context_for_chapter_generation(self, chapter_number: int) -> str:
        """
        Prepares a string of context to be injected into prompts for chapter generation.
        Includes original prompt, overall theme, motifs, and summaries of previous chapters.
        """
        context_str = f"The original user prompt (the source of truth) for the story is:\n---BEGIN PROMPT---\n{self.initial_prompt}\n---END PROMPT---\n\n"

        if self.overall_theme:
            context_str += f"Recall the novel's central theme: {self.overall_theme}\n"
        if self.motifs:
            context_str += f"Remember to weave in the following motifs: {', '.join(self.motifs)}\n"

        if self.base_prompt_important_info:
            context_str += f"\nImportant context from the initial story idea:\n{self.base_prompt_important_info}\n"

        previous_chapter_summaries = self.get_all_previous_chapter_summaries(chapter_number)
        if previous_chapter_summaries:
            context_str += "\nSummary of events from previous chapters:\n"
            for ch_summary_info in previous_chapter_summaries:
                context_str += f"Chapter {ch_summary_info['chapter_number']}:\n{ch_summary_info['summary']}\n\n"

        prev_chapter = self.get_chapter(chapter_number - 1)
        if prev_chapter:
            if prev_chapter.character_arcs_progress:
                context_str += f"Character development notes from the end of Chapter {prev_chapter.chapter_number}:\n"
                for char, prog in prev_chapter.character_arcs_progress.items():
                    context_str += f"  - {char}: {prog}\n"
            if prev_chapter.scenes and prev_chapter.scenes[-1].key_points_for_next_scene:
                context_str += f"Key points to carry over from the last scene of Chapter {prev_chapter.chapter_number}:\n"
                for point in prev_chapter.scenes[-1].key_points_for_next_scene:
                    context_str += f"  - {point}\n"

        return context_str.strip() if context_str else "This is the first chapter, so begin the story!"

    def get_context_for_scene_generation(self, chapter_number: int, scene_number: int) -> str:
        """
        Prepares a string of context for scene generation.
        Includes chapter context and previous scene summary within the same chapter.
        """
        context_str = f"The original user prompt (the source of truth) for the story is:\n---BEGIN PROMPT---\n{self.initial_prompt}\n---END PROMPT---\n\n"

        chapter_ctx = self.get_chapter(chapter_number)
        if not chapter_ctx:
            return "Error: Chapter context not found."

        context_str += f"Currently writing Chapter {chapter_number}, Scene {scene_number}.\n"
        if chapter_ctx.summary:
             context_str += f"So far in this chapter:\n{chapter_ctx.summary}\n"
        elif chapter_ctx.initial_outline:
             context_str += f"The outline for this chapter is:\n{chapter_ctx.initial_outline}\n"

        if chapter_ctx.theme_elements:
            context_str += f"Themes to emphasize in this chapter: {', '.join(chapter_ctx.theme_elements)}\n"

        if scene_number > 1:
            prev_scene = chapter_ctx.get_scene(scene_number - 1)
            if prev_scene and prev_scene.final_summary:
                context_str += f"\nSummary of the previous scene (Scene {prev_scene.scene_number}):\n{prev_scene.final_summary}\n"
                if prev_scene.key_points_for_next_scene:
                    context_str += "Key points to address from the previous scene:\n"
                    for point in prev_scene.key_points_for_next_scene:
                        context_str += f"  - {point}\n"
            else:
                 context_str += f"\nThis is Scene {scene_number}. The previous scene's summary is not available.\n"
        else:
            context_str += f"\nThis is the first scene of Chapter {chapter_number}.\n"
            if chapter_number > 1:
                prev_chapter_summary = self.get_previous_chapter_summary(chapter_number)
                if prev_chapter_summary:
                     context_str += f"To remind you, Chapter {chapter_number-1} ended with:\n{prev_chapter_summary}\n"

        return context_str.strip()
