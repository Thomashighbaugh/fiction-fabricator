"""
batch_generator.py - Smart batching for content generation with continuity awareness
"""
from dataclasses import dataclass


@dataclass
class Chapter:
    """Represents a chapter with its metadata."""

    id: str
    title: str
    summary: str
    setting: str
    characters: set[str]
    word_count_target: int
    complexity_score: float


@dataclass
class Batch:
    """Represents a batch of chapters to generate together."""

    chapters: list[Chapter]
    shared_characters: set[str]
    priority: float
    estimated_tokens: int


class BatchGenerator:
    """Intelligently groups chapters for generation with continuity awareness."""

    def __init__(self, max_batch_tokens: int = 8000):
        """
        Initialize batch generator.

        Args:
            max_batch_tokens: Maximum tokens per batch (default 8000 for good quality)
        """
        self.max_batch_tokens = max_batch_tokens
        self.estimated_tokens_per_word = 1.3  # Rough estimate for generation
        self.min_chapters_per_batch = 1
        self.max_chapters_per_batch = 5

    def create_smart_batches(self, chapters: list[Chapter]) -> list[Batch]:
        """
        Create smart batches considering character overlap and continuity.

        Args:
            chapters: List of all chapters to process

        Returns:
            List of Batch objects with optimal chapter groupings
        """
        if not chapters:
            return []

        # Sort chapters by ID
        sorted_chapters = sorted(chapters, key=lambda c: int(c.id))

        batches = []
        current_batch = []
        current_chars = set()
        current_tokens = 0

        for chapter in sorted_chapters:
            # Calculate estimated tokens for this chapter
            chapter_tokens = int(chapter.word_count_target * self.estimated_tokens_per_word)

            # Check if adding this chapter would exceed token limit
            if current_tokens + chapter_tokens > self.max_batch_tokens:
                # Finalize current batch
                if current_batch:
                    batch = Batch(
                        chapters=current_batch,
                        shared_characters=current_chars.copy(),
                        priority=self._calculate_batch_priority(current_batch),
                        estimated_tokens=current_tokens,
                    )
                    batches.append(batch)

                    # Start new batch
                    current_batch = [chapter]
                    current_chars = chapter.characters.copy()
                    current_tokens = chapter_tokens
                else:
                    # Chapter too large - create single chapter batch
                    batch = Batch(
                        chapters=[chapter],
                        shared_characters=chapter.characters.copy(),
                        priority=self._calculate_batch_priority([chapter]),
                        estimated_tokens=chapter_tokens,
                    )
                    batches.append(batch)
            else:
                # Add to current batch
                current_batch.append(chapter)
                current_chars.update(chapter.characters)
                current_tokens += chapter_tokens

        # Don't forget the last batch
        if current_batch:
            batch = Batch(
                chapters=current_batch,
                shared_characters=current_chars.copy(),
                priority=self._calculate_batch_priority(current_batch),
                estimated_tokens=current_tokens,
            )
            batches.append(batch)

        return batches

    def _calculate_batch_priority(self, chapters: list[Chapter]) -> float:
        """
        Calculate priority score for a batch.
        Higher priority batches should be processed first.
        """
        if not chapters:
            return 0.0

        score = 0.0

        # Priority 1: More chapters = slightly higher priority (efficiency)
        score += len(chapters) * 10

        # Priority 2: Higher complexity = higher priority
        avg_complexity = sum(c.complexity_score for c in chapters) / len(chapters)
        score += avg_complexity * 5

        # Priority 3: More shared characters = higher priority (continuity)
        total_unique_chars = len(set().union(*[c.characters for c in chapters]))
        avg_chars_per_chap = total_unique_chars / len(chapters)
        score += avg_chars_per_chap * 2

        # Priority 4: Earlier chapters = higher priority
        if chapters:
            first_chapter_num = min(int(c.id) for c in chapters)
            score += (100 - first_chapter_num) * 0.1

        return score

    def extract_chapters_from_xml(self, book_root) -> list[Chapter]:
        """
        Extract chapter metadata from XML structure.

        Args:
            book_root: The root book XML element

        Returns:
            List of Chapter objects with metadata
        """
        if book_root is None:
            return []

        chapters = []
        chapter_elements = book_root.findall(".//chapter")

        for chap_elem in chapter_elements:
            chapter_id = chap_elem.get("id", "")

            if not chapter_id:
                continue

            # Extract characters present in this chapter
            characters = self._extract_characters_from_chapter(chap_elem)

            # Calculate complexity score
            complexity_score = self._calculate_chapter_complexity(chap_elem, characters)

            # Estimate word count target
            word_count_target = self._estimate_word_count_target(chap_elem, complexity_score)

            chapter = Chapter(
                id=chapter_id,
                title=chap_elem.findtext("title", "Untitled"),
                summary=chap_elem.findtext("summary", ""),
                setting=chap_elem.get("setting", ""),
                characters=characters,
                word_count_target=word_count_target,
                complexity_score=complexity_score,
            )
            chapters.append(chapter)

        return chapters

    def _extract_characters_from_chapter(self, chapter_elem) -> set[str]:
        """Extract character names mentioned in chapter summary."""
        summary = chapter_elem.findtext("summary", "")

        # Get all character names from book
        book_root = chapter_elem.getroottree().getroot()
        chars_elem = book_root.find("characters")

        all_char_names = set()
        if chars_elem is not None:
            for char_elem in chars_elem.findall("character"):
                char_name = char_elem.findtext("name", "")
                if char_name:
                    all_char_names.add(char_name.lower())

        # Check which characters appear in this chapter's summary
        summary_lower = summary.lower()
        chapter_chars = {name for name in all_char_names if name in summary_lower}

        return chapter_chars

    def _calculate_chapter_complexity(self, chapter_elem, characters: set[str]) -> float:
        """
        Calculate complexity score for a chapter (0-1 scale).
        Considers: character count, summary length, setting complexity.
        """
        score = 0.0

        # Factor 1: Number of characters
        char_count = len(characters)
        if char_count > 0:
            score += min(0.3, char_count * 0.05)

        # Factor 2: Summary length (longer = more complex)
        summary = chapter_elem.findtext("summary", "")
        summary_words = len(summary.split())
        score += min(0.2, summary_words * 0.002)

        # Factor 3: Setting description length
        setting = chapter_elem.get("setting", "")
        if len(setting) > 30:
            score += 0.2

        # Factor 4: Presence of plot beats
        plot_beats = chapter_elem.find("plot_beats")
        if plot_beats is not None and len(plot_beats.findall("beat")) > 3:
            score += 0.3

        return min(1.0, score)

    def _estimate_word_count_target(self, chapter_elem, complexity_score: float) -> int:
        """
        Estimate target word count based on chapter complexity.
        """
        base_target = 4500  # Default target

        # Adjust for complexity
        complexity_multiplier = 1.0 + complexity_score * 0.5  # 1.0 to 1.5
        target = int(base_target * complexity_multiplier)

        # Clamp to reasonable bounds
        return max(2000, min(8000, target))

    def optimize_batch_order(self, batches: list[Batch]) -> list[Batch]:
        """
        Reorder batches for optimal generation order.
        Prioritizes batches with higher priority scores.
        """
        # Sort by priority (descending)
        sorted_batches = sorted(batches, key=lambda b: b.priority, reverse=True)
        return sorted_batches

    def get_batch_summary(self, batch: Batch) -> str:
        """Generate a summary of a batch."""
        if not batch.chapters:
            return "Empty batch"

        chapter_ids = ", ".join([f"Ch {c.id}" for c in batch.chapters])
        shared = ", ".join(sorted(batch.shared_characters)) if batch.shared_characters else "None"

        summary_lines = [
            "Batch Summary:",
            f"  Chapters: {chapter_ids}",
            f"  Total chapters: {len(batch.chapters)}",
            f"  Shared characters: {shared}",
            f"  Estimated tokens: {batch.estimated_tokens}",
            f"  Priority score: {batch.priority:.1f}",
        ]

        return "\n".join(summary_lines)
