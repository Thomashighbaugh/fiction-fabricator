"""
specialized_agents.py - Specialized agent implementations for fiction generation.
"""

from typing import Any

try:
    from lxml import etree
except ImportError:
    from xml.etree import ElementTree as etree
from src.generators.novel import generate_outline
from src.llm_client import LLMClient
from src.logger import get_logger
from src.project import Project
from src.quality_metrics import QualityEvaluator
from src.slop_detection import SlopDetectionAgent
from src.swarm.agent_role import AgentRole
from src.swarm.swarm_agent import SwarmAgent
from src.swarm.task import Task, TaskPool, TaskType

logger = get_logger(__name__)


class ArchitectAgent(SwarmAgent):
    """Plans and decomposes high-level tasks."""

    def __init__(self, llm_client: LLMClient, task_pool: TaskPool, project: Project):
        super().__init__(AgentRole.ARCHITECT, llm_client, task_pool)
        self.project = project

    def can_handle_task(self, task: Task) -> bool:
        return task.task_type == TaskType.DECOMPOSE_PROJECT

    async def process_task(self, task: Task) -> Any:
        """Analyze project and create execution plan."""
        # Get initial idea from project
        initial_idea = ""
        if self.project.book_root is not None:
            initial_idea_elem = self.project.book_root.find("initial_idea")
            if initial_idea_elem is not None:
                initial_idea = initial_idea_elem.text or ""

        # For now, just return ready status
        # Future: Could analyze and suggest chapter count, complexity estimates, etc.
        return {"analysis": "Story structure ready", "ready_for_outline": True}


class OutlinerAgent(SwarmAgent):
    """Generates outlines and summaries."""

    def __init__(self, llm_client: LLMClient, task_pool: TaskPool, project: Project):
        super().__init__(AgentRole.OUTLINER, llm_client, task_pool)
        self.project = project

    def can_handle_task(self, task: Task) -> bool:
        return task.task_type in (TaskType.GENERATE_OUTLINE, TaskType.PLAN_CHAPTERS)

    async def process_task(self, task: Task) -> Any:
        """Generate outline."""
        # Use existing novel outline generation
        # Note: This is synchronous - can be enhanced with async later
        outline_xml = generate_outline(self.llm_client, self.project, lorebook_context="")

        if outline_xml:
            return outline_xml

        raise Exception("Failed to generate outline")


class WriterAgent(SwarmAgent):
    """Generates prose content for chapters."""

    def __init__(self, llm_client: LLMClient, task_pool: TaskPool, project: Project):
        super().__init__(AgentRole.WRITER, llm_client, task_pool)
        self.project = project

    def can_handle_task(self, task: Task) -> bool:
        return task.task_type == TaskType.WRITE_CHAPTER

    async def process_task(self, task: Task) -> Any:
        """Generate chapter content."""
        chapter_id = task.context.get("chapter_id", "")
        book_root_str = task.context.get("book_root", "")

        if not book_root_str:
            raise ValueError("No book context provided")

        # Parse book root
        book_root = etree.fromstring(book_root_str)

        # Find the target chapter
        target_chapter = book_root.find(f".//chapter[@id='{chapter_id}']")
        if target_chapter is None:
            raise ValueError(f"Chapter {chapter_id} not found")

        # Get chapter details
        title = target_chapter.findtext("title", "")
        summary = target_chapter.findtext("summary", "")
        setting = target_chapter.get("setting", "")

        # Build generation prompt (similar to orchestrator.py:457-477)
        prompt = f"""
You are a novelist continuing a story. Write the full prose for this chapter based on its summary and the full book context.
Aim for substantial, detailed content (3000-6000 words).

Chapter ID: {chapter_id}
Title: {title}
Summary: {summary}
Setting: {setting}

IMPORTANT: Keep the narrative grounded in the setting described above.

Output ONLY an XML `<patch>` containing a single `<chapter>` with this structure:
<patch>
  <chapter id="{chapter_id}" setting="{setting}">
    <content>
      <paragraph id="1">First paragraph text...</paragraph>
      <paragraph id="2">Second paragraph text...</paragraph>
      ...
    </content>
  </chapter>
</patch>

Full Book Context:
```xml
{etree.tostring(book_root, encoding="unicode")}
```
"""

        # Get LLM response
        patch_xml = await self.get_llm_response(prompt, f"Writing chapter {chapter_id}")

        if not patch_xml:
            raise Exception(f"Failed to generate content for chapter {chapter_id}")

        # Apply patch to project
        self.project.apply_patch(patch_xml)

        # Count paragraphs for reporting
        word_count = len(patch_xml.split())

        return {
            "chapter_id": chapter_id,
            "word_count": word_count,
            "patch": patch_xml,
        }


class EditorAgent(SwarmAgent):
    """Edits and refines existing content."""

    def __init__(self, llm_client: LLMClient, task_pool: TaskPool, project: Project):
        super().__init__(AgentRole.EDITOR, llm_client, task_pool)
        self.project = project

    def can_handle_task(self, task: Task) -> bool:
        return task.task_type in (
            TaskType.EDIT_CHAPTER,
            TaskType.EXPAND_CHAPTER,
            TaskType.REWRITE_CHAPTER,
        )

    async def process_task(self, task: Task) -> Any:
        """Edit chapter content."""
        chapter_id = task.context.get("chapter_id", "")
        operation = task.context.get("operation", "edit")

        if self.project.book_root is None:
            raise ValueError("No book root found")

        # Get chapter
        chapter = self.project.book_root.find(f".//chapter[@id='{chapter_id}']")
        if chapter is None:
            raise ValueError(f"Chapter {chapter_id} not found")

        # Get existing content
        paragraphs = chapter.findall(".//paragraph")
        if not paragraphs:
            raise ValueError(f"Chapter {chapter_id} has no content to edit")

        existing_content = "\\n\\n".join(p.text for p in paragraphs if p.text and p.text.strip())

        # Build editing prompt based on operation
        if operation == "expand":
            instruction = "Expand this chapter with more detail, description, and dialogue. Double its length while maintaining quality and staying true to the outline."
        elif operation == "rewrite":
            instruction = "Rewrite this chapter with improved prose, better pacing, and enhanced narrative quality."
        else:
            instruction = "Edit this chapter to improve clarity, flow, and engagement."

        # Get chapter metadata
        title = chapter.findtext("title", f"Chapter {chapter_id}")
        summary = chapter.findtext("summary", "")
        setting = chapter.get("setting", "")

        editing_prompt = f"""
{instruction}

Chapter ID: {chapter_id}
Title: {title}
Summary: {summary}
Setting: {setting}

Current Content:
{existing_content}

Output ONLY an XML `<patch>` with the edited chapter in this format:
<patch>
  <chapter id="{chapter_id}" setting="{setting}">
    <content>
      <paragraph id="1">First paragraph text...</paragraph>
      <paragraph id="2">Second paragraph text...</paragraph>
      ...
    </content>
  </chapter>
</patch>

Full Book Context for reference:
```xml
{etree.tostring(self.project.book_root, encoding="unicode")}
```
"""

        # Get edited content
        patch_xml = await self.get_llm_response(editing_prompt, f"Edit chapter {chapter_id}")

        if not patch_xml:
            raise Exception(f"Failed to edit chapter {chapter_id}")

        # Apply patch
        self.project.apply_patch(patch_xml)

        return {
            "chapter_id": chapter_id,
            "operation": operation,
            "word_count": len(patch_xml.split()),
            "patch": patch_xml,
        }


class QualityAssuranceAgent(SwarmAgent):
    """Validates content quality and completeness."""

    def __init__(self, llm_client: LLMClient, task_pool: TaskPool, project: Project, enable_slop_detection: bool = True):
        super().__init__(AgentRole.QUALITY_ASSURANCE, llm_client, task_pool)
        self.project = project
        
        # Initialize quality evaluator with slop detection
        self.quality_evaluator = QualityEvaluator(enable_slop_detection=enable_slop_detection)
        
        # Initialize standalone slop detection for quick checks
        if enable_slop_detection:
            self.slop_agent = SlopDetectionAgent(sensitivity="medium")
        else:
            self.slop_agent = None

    def can_handle_task(self, task: Task) -> bool:
        return task.task_type in (
            TaskType.VALIDATE_CONTENT,
            TaskType.CHECK_QUALITY,
            TaskType.CHECK_CONTINUITY,
        )

    async def process_task(self, task: Task) -> Any:
        """Validate content quality."""
        target_type = task.context.get("target_type", "chapter")
        chapter_id = task.context.get("chapter_id", "")

        if self.project.book_root is None:
            raise ValueError("No book root found")

        if target_type == "outline":
            # Validate outline completeness
            chapters = self.project.book_root.findall(".//chapter")
            if not chapters:
                raise Exception("Outline has no chapters")

            issues = []
            for chapter in chapters:
                chapter_id_check = chapter.get("id", "")
                title = chapter.find("title")
                summary = chapter.find("summary")

                if title is None or not title.text:
                    issues.append(f"Chapter {chapter_id_check} missing title")
                if summary is None or not summary.text:
                    issues.append(f"Chapter {chapter_id_check} missing summary")

            if issues:
                raise Exception(f"Outline validation failed: {', '.join(issues)}")

            return {"valid": True, "chapter_count": len(chapters)}

        elif target_type in ("chapter", "edited_chapter"):
            # Validate chapter content
            chapter = self.project.book_root.find(f".//chapter[@id='{chapter_id}']")
            if chapter is None:
                raise ValueError(f"Chapter {chapter_id} not found")

            paragraphs = chapter.findall(".//paragraph")
            if not paragraphs:
                raise Exception(f"Chapter {chapter_id} has no content")

            # Count words
            total_words = sum(len(p.text.split()) for p in paragraphs if p.text and p.text.strip())

            # Use quality evaluator which includes slop detection
            chapter_content = "\n".join(p.text for p in paragraphs if p.text)
            quality_metrics = self.quality_evaluator.evaluate_chapter(chapter_content)
            
            # Check if quality meets thresholds
            if not quality_metrics.meets_thresholds:
                issues_str = "; ".join(quality_metrics.issues)
                raise Exception(f"Chapter {chapter_id} quality issues: {issues_str}")

            return {
                "valid": True, 
                "word_count": quality_metrics.word_count, 
                "chapter_id": chapter_id,
                "quality_score": quality_metrics.overall_score,
                "slop_detected": quality_metrics.slop_analysis.has_issues if quality_metrics.slop_analysis else False,
                "slop_score": quality_metrics.slop_analysis.overall_score if quality_metrics.slop_analysis else None
            }

        return {"valid": True}
    
    def detect_and_clean_slop(self, text: str, auto_clean: bool = False) -> dict:
        """
        Dedicated method for slop detection and cleaning.
        
        Args:
            text: Text to analyze
            auto_clean: Whether to automatically clean detected slop
            
        Returns:
            Dictionary with slop analysis results
        """
        if not self.slop_agent:
            return {"enabled": False, "message": "Slop detection is disabled"}
        
        analysis = self.slop_agent.validate_content_quality(text, auto_clean)
        
        return {
            "enabled": True,
            "has_slop": analysis.has_issues,
            "score": analysis.overall_score,
            "issues_count": len(analysis.issues),
            "cleaned_text": analysis.cleaned_text,
            "removals_count": analysis.removals_count,
            "replacements_count": analysis.replacements_count,
            "detailed_report": self.slop_agent.generate_quality_report(analysis)
        }
