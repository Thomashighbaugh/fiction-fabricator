# -*- coding: utf-8 -*-
"""
rollback_manager.py - Version control and automatic regeneration with attempt tracking
"""
import shutil
import copy
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class GenerationStatus(str, Enum):
    """Status of a generation attempt."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REJECTED = "rejected"


@dataclass
class GenerationAttempt:
    """Tracks a single generation attempt with its results."""
    attempt_number: int
    timestamp: str
    chapter_id: str
    status: GenerationStatus
    prompt_variation: str
    result_patch_path: Optional[str] = None
    quality_metrics: Optional[Dict] = None
    error_message: Optional[str] = None


@dataclass
class BestSelection:
    """Tracks the best version among multiple attempts."""
    chapter_id: str
    best_attempt_number: int
    best_patch_path: str | None
    selection_reason: str
    quality_scores: Dict[int, float] = field(default_factory=dict)


class RollbackManager:
    """Manages versioning and automatic regeneration with best selection."""

    def __init__(self, project_dir: Path, max_attempts: int = 3):
        """
        Initialize rollback manager.

        Args:
            project_dir: Project directory for storing versions
            max_attempts: Maximum regeneration attempts (default 3)
        """
        self.project_dir = project_dir
        self.max_attempts = max_attempts
        self.versions_dir = project_dir / "versions"
        self.attempts_file = project_dir / "generation_attempts.json"
        
        self.attempts: Dict[str, List[GenerationAttempt]] = {}  # chapter_id -> attempts
        self.best_selections: Dict[str, BestSelection] = {}  # chapter_id -> best version
        
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure versioning directories exist."""
        self.versions_dir.mkdir(parents=True, exist_ok=True)

    def save_version_before_generation(self, chapter_id: str, patch_xml: str) -> str:
        """
        Save current version before generating new content.

        Args:
            chapter_id: Chapter being regenerated
            patch_xml: Current patch content

        Returns:
            Path to saved version file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{chapter_id}_pre_gen_{timestamp}.xml"
        filepath = self.versions_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(patch_xml)

        return str(filepath)

    def record_generation_attempt(self, chapter_id: str, attempt_num: int,
                                  prompt_variation: str, status: GenerationStatus,
                                  result_patch: Optional[str] = None,
                                  quality_metrics: Optional[Dict] = None,
                                  error_msg: Optional[str] = None):
        """
        Record a generation attempt.

        Args:
            chapter_id: Chapter identifier
            attempt_num: Which attempt number (1, 2, 3...)
            prompt_variation: How the prompt was modified for this attempt
            status: Success/failure status
            result_patch: Path to resulting patch (if successful)
            quality_metrics: Quality evaluation results
            error_msg: Error message if failed
        """
        attempt = GenerationAttempt(
            attempt_number=attempt_num,
            timestamp=datetime.now().isoformat(),
            chapter_id=chapter_id,
            status=status,
            prompt_variation=prompt_variation,
            result_patch_path=result_patch,
            quality_metrics=quality_metrics,
            error_message=error_msg
        )

        if chapter_id not in self.attempts:
            self.attempts[chapter_id] = []
        
        self.attempts[chapter_id].append(attempt)
        self._save_attempts()

    def _save_attempts(self):
        """Save attempts data to JSON file."""
        import json
        
        data = {
            chapter_id: [
                {
                    'attempt_number': a.attempt_number,
                    'timestamp': a.timestamp,
                    'status': a.status,
                    'prompt_variation': a.prompt_variation,
                    'result_patch_path': a.result_patch_path,
                    'quality_metrics': a.quality_metrics,
                    'error_message': a.error_message
                }
                for a in attempts
            ]
            for chapter_id, attempts in self.attempts.items()
        }

        with open(self.attempts_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def load_attempts(self):
        """Load attempts from JSON file."""
        import json
        
        try:
            with open(self.attempts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.attempts = {}
            for chapter_id, attempts_data in data.items():
                self.attempts[chapter_id] = [
                    GenerationAttempt(**a) for a in attempts_data
                ]

        except FileNotFoundError:
            self.attempts = {}
        except json.JSONDecodeError:
            self.attempts = {}

    def select_best_version(self, chapter_id: str, 
                            scoring_function = None) -> Optional[str]:
        """
        Select the best version among all attempts.

        Args:
            chapter_id: Chapter to select best version for
            scoring_function: Function that takes a patch path and returns a score

        Returns:
            Path to best version, or None if no successful attempts
        """
        if chapter_id not in self.attempts:
            return None

        attempts = self.attempts[chapter_id]
        successful_attempts = [a for a in attempts if a.status == GenerationStatus.SUCCESS]
        
        if not successful_attempts:
            return None

        if len(successful_attempts) == 1:
            return successful_attempts[0].result_patch_path

        # Score each attempt
        scores = {}
        for attempt in successful_attempts:
            if attempt.result_patch_path and Path(attempt.result_patch_path).exists():
                if scoring_function:
                    try:
                        score = scoring_function(attempt.result_patch_path)
                        scores[attempt.attempt_number] = score
                    except Exception as e:
                        scores[attempt.attempt_number] = 0.0
                else:
                    # Default: prefer later attempts (assuming iterative improvement)
                    scores[attempt.attempt_number] = attempt.attempt_number

        if not scores:
            return successful_attempts[-1].result_patch_path

        # Select best
        best_attempt_num = max(scores.keys(), key=lambda k: scores[k])
        best_attempt = next((a for a in successful_attempts if a.attempt_number == best_attempt_num), None)
        
        if not best_attempt:
            return None
        
        # Record selection
        self.best_selections[chapter_id] = BestSelection(
            chapter_id=chapter_id,
            best_attempt_number=best_attempt_num,
            best_patch_path=best_attempt.result_patch_path,
            selection_reason=f"Highest score: {scores[best_attempt_num]:.2f}",
            quality_scores=scores
        )

        return best_attempt.result_patch_path

    def get_prompt_variations(self, base_prompt: str, 
                              attempt_num: int, chapter_id: str) -> str:
        """
        Generate different prompt variations for retry attempts.

        Args:
            base_prompt: Original prompt
            attempt_num: Which attempt number
            chapter_id: Chapter being generated

        Returns:
            Modified prompt for this attempt
        """
        variations = {
            1: base_prompt,  # First attempt = original
            2: self._add_emphasis_variation(base_prompt, chapter_id),
            3: self._add_style_variation(base_prompt, chapter_id),
            4: self._add_detail_variation(base_prompt, chapter_id),
            5: self._add_clarity_variation(base_prompt, chapter_id),
        }

        return variations.get(attempt_num, base_prompt)

    def _add_emphasis_variation(self, prompt: str, chapter_id: str) -> str:
        """Add emphasis on key elements."""
        emphasis_text = """
ADDITIONAL FOCUS FOR ATTEMPT 2:
- Place particular emphasis on maintaining continuity with previous chapters
- Ensure character voices are distinct and consistent
- Pay special attention to dialogue quality and naturalness
"""
        return prompt + emphasis_text

    def _add_style_variation(self, prompt: str, chapter_id: str) -> str:
        """Add style variation instructions."""
        style_text = """
ADDITIONAL STYLE GUIDANCE FOR ATTEMPT 3:
- Vary sentence structure more extensively
- Use more evocative and precise vocabulary
- Balance descriptive passages with action
- Ensure pacing flows smoothly
"""
        return prompt + style_text

    def _add_detail_variation(self, prompt: str, chapter_id: str) -> str:
        """Add detail/depth variation instructions."""
        detail_text = """
ADDITIONAL DETAIL FOCUS FOR ATTEMPT 4:
- Expand scenes with more sensory details
- Add character internal thoughts and reactions
- Include environmental and atmospheric descriptions
- Deepen character interactions
"""
        return prompt + detail_text

    def _add_clarity_variation(self, prompt: str, chapter_id: str) -> str:
        """Add clarity/coherence variation instructions."""
        clarity_text = """
ADDITIONAL CLARITY GUIDANCE FOR ATTEMPT 5:
- Ensure cause-and-effect relationships are clear
- Smooth transitions between scenes
- Make character motivations explicit
- Avoid vague or ambiguous descriptions
"""
        return prompt + clarity_text

    def rollback_to_version(self, chapter_id: str, version_num: int) -> Optional[str]:
        """
        Rollback to a specific previous version.

        Args:
            chapter_id: Chapter to rollback
            version_num: Version number to restore (1=first, 2=second...)

        Returns:
            Path to restored version, or None if not found
        """
        attempts = self.attempts.get(chapter_id, [])
        
        if version_num < 1 or version_num > len(attempts):
            return None

        target_attempt = attempts[version_num - 1]  # 1-indexed
        
        if target_attempt.status != GenerationStatus.SUCCESS or not target_attempt.result_patch_path:
            return None

        return target_attempt.result_patch_path

    def get_attempts_summary(self, chapter_id: str) -> str:
        """Generate a summary of all attempts for a chapter."""
        if chapter_id not in self.attempts:
            return f"No attempts recorded for Chapter {chapter_id}."

        attempts = self.attempts[chapter_id]
        lines = [f"Generation Attempts for Chapter {chapter_id}:\n"]

        for attempt in attempts:
            status_emoji = {
                GenerationStatus.SUCCESS: "✓",
                GenerationStatus.FAILED: "✗",
                GenerationStatus.REJECTED: "⊘",
                GenerationStatus.PENDING: "⏳"
            }.get(attempt.status, "?")

            status_text = attempt.status.value.upper()
            
            lines.append(
                f"  {status_emoji} Attempt {attempt.attempt_number}: {status_text}"
            )
            lines.append(f"      Time: {attempt.timestamp}")
            
            if attempt.prompt_variation:
                lines.append(f"      Variation: {attempt.prompt_variation[:50]}...")
            
            if attempt.error_message:
                lines.append(f"      Error: {attempt.error_message}")
            
            if attempt.quality_metrics:
                lines.append(f"      Quality Score: {attempt.quality_metrics.get('overall_score', 'N/A'):.1f}")

        # Best selection
        if chapter_id in self.best_selections:
            best = self.best_selections[chapter_id]
            lines.append(f"\n  ★ Best Version: Attempt {best.best_attempt_number}")
            lines.append(f"      Reason: {best.selection_reason}")
            lines.append(f"      Path: {best.best_patch_path}")

        return "\n".join(lines)

    def cleanup_old_versions(self, keep_count: int = 3):
        """
        Clean up old versions, keeping only the most recent N.

        Args:
            keep_count: Number of most recent versions to keep per chapter
        """
        import glob

        # Find all version files
        version_files = list(self.versions_dir.glob("*.xml"))
        
        if len(version_files) <= keep_count:
            return

        # Group by chapter
        by_chapter = {}
        for filepath in version_files:
            chapter_id = filepath.stem.split('_')[0]
            if chapter_id not in by_chapter:
                by_chapter[chapter_id] = []
            by_chapter[chapter_id].append(filepath)

        # Keep only N most recent per chapter
        for chapter_id, files in by_chapter.items():
            # Sort by modification time
            files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            files_to_delete = files[keep_count:]
            
            for filepath in files_to_delete:
                try:
                    filepath.unlink()
                except Exception as e:
                    pass  # Silently fail

    def get_all_chapters_needing_regeneration(self, 
                                          quality_threshold: float = 6.0) -> List[str]:
        """
        Get list of chapters with quality below threshold.

        Args:
            quality_threshold: Minimum quality score to accept

        Returns:
            List of chapter IDs needing regeneration
        """
        chapters_to_regenerate = []

        for chapter_id, attempts in self.attempts.items():
            successful_attempts = [a for a in attempts if a.status == GenerationStatus.SUCCESS]
            
            for attempt in successful_attempts:
                if attempt.quality_metrics:
                    overall_score = attempt.quality_metrics.get('overall_score', 0.0)
                    if overall_score < quality_threshold:
                        chapters_to_regenerate.append(chapter_id)
                        break  # Only add once per chapter

        return chapters_to_regenerate

    def regenerate_with_rollback(self, chapter_id: str, prompt_template: str,
                                 llm_generator, quality_evaluator,
                                 max_attempts: Optional[int] = None) -> str:
        """
        Complete regeneration flow with automatic rollback and best selection.

        Args:
            chapter_id: Chapter to regenerate
            prompt_template: Base prompt template
            llm_generator: Function to call LLM (takes prompt, returns patch_xml)
            quality_evaluator: Function to evaluate quality (takes patch_xml, returns metrics)
            max_attempts: Maximum attempts (default to configured value)

        Returns:
            Path to best version selected
        """
        max_attempts = max_attempts or self.max_attempts
        self.console.print(f"[cyan]Starting regeneration for Chapter {chapter_id} (max {max_attempts} attempts)[/cyan]")

        # Save current version first
        current_patch = self._get_current_patch(chapter_id)
        if current_patch:
            saved_path = self.save_version_before_generation(chapter_id, current_patch)
            self.console.print(f"[dim]Saved current version: {saved_path}[/dim]")

        best_version = None

        for attempt_num in range(1, max_attempts + 1):
            self.console.print(f"\n[cyan]Attempt {attempt_num}/{max_attempts}[/cyan]")

            # Get prompt variation
            prompt = self.get_prompt_variations(prompt_template, attempt_num, chapter_id)

            # Generate
            try:
                result_patch = llm_generator(prompt, attempt_num)
                
                if result_patch:
                    # Evaluate quality
                    quality_metrics = quality_evaluator(result_patch)
                    
                    # Record attempt
                    status = GenerationStatus.SUCCESS
                    if quality_metrics.get('overall_score', 0) < 6.0:
                        status = GenerationStatus.REJECTED
                    
                    self.record_generation_attempt(
                        chapter_id=chapter_id,
                        attempt_num=attempt_num,
                        prompt_variation=f"Variation {attempt_num}",
                        status=status,
                        result_patch=result_patch,
                        quality_metrics=quality_metrics
                    )

                    self.console.print(f"  Quality Score: {quality_metrics.get('overall_score', 0):.1f}")
                    
                    if status == GenerationStatus.REJECTED:
                        self.console.print("[yellow]  Below threshold - will continue to next attempt[/yellow]")
                    else:
                        self.console.print("[green]  Accepted![/green]")
                        # Acceptable, but might still try for better
                else:
                    self.record_generation_attempt(
                        chapter_id=chapter_id,
                        attempt_num=attempt_num,
                        prompt_variation=f"Variation {attempt_num}",
                        status=GenerationStatus.FAILED,
                        error_msg="No patch generated"
                    )
                    self.console.print("[red]  Failed - no patch generated[/red]")

            except Exception as e:
                self.record_generation_attempt(
                    chapter_id=chapter_id,
                    attempt_num=attempt_num,
                    prompt_variation=f"Variation {attempt_num}",
                    status=GenerationStatus.FAILED,
                    error_msg=str(e)
                )
                self.console.print(f"[red]  Error: {e}[/red]")

        # Select best version
        best_version = self.select_best_version(chapter_id, scoring_function=self._simple_quality_score)
        
        if best_version:
            self.console.print(f"\n[bold green]Selected best version: {best_version}[/bold green]")
            return best_version
        else:
            self.console.print(f"\n[yellow]No successful attempts for Chapter {chapter_id}[/yellow]")
            return None

    def _get_current_patch(self, chapter_id: str):
        """Get current patch for a chapter from project."""
        # This would need to be implemented based on project structure
        # For now, return None
        return None

    def _simple_quality_score(self, patch_path: str) -> float:
        """
        Simple quality scoring function for version selection.
        In production, this would properly parse and evaluate the patch.
        """
        # Placeholder - would parse patch and run quality evaluation
        return 5.0

    def set_console(self, console):
        """Set console for output."""
        self.console = console
