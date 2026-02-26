"""
quality_metrics.py - Quality evaluation system for generated content
"""
import re
from dataclasses import dataclass

from src import config


@dataclass
class QualityMetrics:
    """Data class holding quality metrics for a chapter."""

    word_count: int
    dialogue_ratio: float
    sentence_variety_score: float
    vocabulary_richness_score: float
    overall_score: float
    meets_thresholds: bool
    issues: list[str]


class QualityEvaluator:
    """Evaluates content quality against defined thresholds."""

    def __init__(self, thresholds: dict | None = None):
        self.thresholds = thresholds or {
            "min_words": config.MIN_WORDS_PER_CHAPTER,
            "min_dialogue_ratio": config.MIN_DIALOGUE_RATIO,
            "max_dialogue_ratio": config.MAX_DIALOGUE_RATIO,
            "min_sentence_variety": config.MIN_SENTENCE_VARIETY_SCORE,
            "min_vocabulary_richness": config.MIN_VOCABULARY_RICHNESS_SCORE,
        }

    def evaluate_chapter(
        self, content_text: str, chapter_context: dict | None = None
    ) -> QualityMetrics:
        """
        Evaluates a chapter's content quality.

        Args:
            content_text: The prose content of the chapter
            chapter_context: Optional dict with chapter summary, beats, and subbeats for dialogue appropriateness check

        Returns:
            QualityMetrics object with all metrics and evaluation results
        """
        if not content_text or not content_text.strip():
            return QualityMetrics(
                word_count=0,
                dialogue_ratio=0.0,
                sentence_variety_score=0.0,
                vocabulary_richness_score=0.0,
                overall_score=0.0,
                meets_thresholds=False,
                issues=["Empty content"],
            )

        issues = []

        word_count = self._count_words(content_text)
        if word_count < self.thresholds["min_words"]:
            issues.append(
                f"Word count ({word_count}) below minimum ({self.thresholds['min_words']})"
            )

        dialogue_ratio = self._calculate_dialogue_ratio(content_text)

        # Check if dialogue is expected for this chapter based on context
        dialogue_expected = True
        if chapter_context:
            dialogue_expected = self._is_dialogue_expected(chapter_context)

        # Only check dialogue ratio if dialogue is expected for this chapter
        if dialogue_expected:
            if dialogue_ratio < self.thresholds["min_dialogue_ratio"]:
                issues.append(
                    f"Dialogue ratio ({dialogue_ratio:.2%}) below minimum ({self.thresholds['min_dialogue_ratio']:.2%})"
                )
            elif dialogue_ratio > self.thresholds["max_dialogue_ratio"]:
                issues.append(
                    f"Dialogue ratio ({dialogue_ratio:.2%}) above maximum ({self.thresholds['max_dialogue_ratio']:.2%})"
                )

        sentence_variety_score = self._evaluate_sentence_variety(content_text)
        if sentence_variety_score < self.thresholds["min_sentence_variety"]:
            issues.append(
                f"Sentence variety score ({sentence_variety_score:.1f}/10) below threshold"
            )

        vocabulary_richness_score = self._evaluate_vocabulary_richness(content_text)
        if vocabulary_richness_score < self.thresholds["min_vocabulary_richness"]:
            issues.append(
                f"Vocabulary richness score ({vocabulary_richness_score:.1f}/10) below threshold"
            )

        overall_score = self._calculate_overall_score(
            word_count, dialogue_ratio, sentence_variety_score, vocabulary_richness_score
        )

        meets_thresholds = len(issues) == 0

        return QualityMetrics(
            word_count=word_count,
            dialogue_ratio=dialogue_ratio,
            sentence_variety_score=sentence_variety_score,
            vocabulary_richness_score=vocabulary_richness_score,
            overall_score=overall_score,
            meets_thresholds=meets_thresholds,
            issues=issues,
        )

    def _is_dialogue_expected(self, chapter_context: dict) -> bool:
        """
        Determine if dialogue is expected for a chapter based on its context.

        Uses LLM self-reflection to analyze chapter summary, beats, and subbeats
        to determine if dialogue is appropriate or if the chapter type legitimately
        doesn't require dialogue (e.g., action scenes, internal monologue, descriptive passages).

        Args:
            chapter_context: Dict with 'summary', 'beats', and 'subbeats' keys

        Returns:
            bool: True if dialogue is expected, False if dialogue is legitimately not required
        """
        summary = chapter_context.get("summary", "")
        beats = chapter_context.get("beats", [])
        subbeats = chapter_context.get("subbeats", [])

        # Build context string for LLM analysis
        context_str = f"Chapter Summary: {summary}\n\n"
        if beats:
            context_str += "Plot Beats:\n" + "\n".join(f"- {beat}" for beat in beats) + "\n\n"
        if subbeats:
            context_str += "Sub-beats:\n" + "\n".join(f"- {sb}" for sb in subbeats)

        # Use LLM to determine if dialogue is expected
        # For now, use keyword-based heuristics as fallback
        context_lower = context_str.lower()

        # Keywords indicating dialogue is likely NOT required
        non_dialogue_keywords = [
            "internal monologue",
            "solitary",
            "alone",
            "introspection",
            "flashback",
            "memory",
            "dream",
            "nightmare",
            "internal struggle",
            "internal conflict",
            "contemplation",
            "meditation",
            "reflection",
            "solitude",
            "descriptive passage",
            "scene description",
            "setting the scene",
            "travel",
            "journey",
            "pursuit",
            "chase",
            "battle",
            "combat",
            "fight scene",
            "action sequence",
            "exploration",
            "discovery",
            "observation",
            "planning",
            "strategy",
            "preparation",
        ]

        # Keywords indicating dialogue IS expected
        dialogue_keywords = [
            "conversation",
            "dialogue",
            "discussion",
            "debate",
            "argument",
            "confrontation",
            "negotiation",
            "meeting",
            "gathering",
            "council",
            "conference",
            "interrogation",
            "questioning",
            "interview",
            "confession",
            "revelation",
            "declaration",
            "interact",
            "speak with",
            "talk to",
            "tell",
            "exchange",
            "banter",
            "quarrel",
        ]

        non_dialogue_count = sum(1 for kw in non_dialogue_keywords if kw in context_lower)
        dialogue_count = sum(1 for kw in dialogue_keywords if kw in context_lower)

        # If context strongly indicates no dialogue is needed, return False
        if non_dialogue_count >= 2 and dialogue_count == 0:
            return False

        # Default to expecting dialogue
        return True

    def _count_words(self, text: str) -> int:
        """Count words in the text."""
        words = re.findall(r"\b\w+\b", text)
        return len(words)

    def _calculate_dialogue_ratio(self, text: str) -> float:
        """
        Calculate the ratio of dialogue to total text.
        Dialogue is detected as text within quotation marks.
        """
        quoted_text = re.findall(r'"([^"]*)"', text)
        quoted_text.extend(re.findall(r"'([^']*)'", text))

        dialogue_words = sum(self._count_words(quote) for quote in quoted_text)
        total_words = self._count_words(text)

        if total_words == 0:
            return 0.0
        return dialogue_words / total_words

    def _evaluate_sentence_variety(self, text: str) -> float:
        """
        Evaluate sentence variety on a 1-10 scale.
        Considers distribution of short (<10 words), medium (10-25), and long (>25) sentences.
        """
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return 0.0

        short_count = 0
        medium_count = 0
        long_count = 0

        for sentence in sentences:
            word_count = self._count_words(sentence)
            if word_count < 10:
                short_count += 1
            elif word_count <= 25:
                medium_count += 1
            else:
                long_count += 1

        total = len(sentences)
        short_ratio = short_count / total
        medium_ratio = medium_count / total
        long_ratio = long_count / total

        ideal_short = 0.25
        ideal_medium = 0.45
        ideal_long = 0.30

        variance = (
            abs(short_ratio - ideal_short)
            + abs(medium_ratio - ideal_medium)
            + abs(long_ratio - ideal_long)
        )

        score = max(0, 10 - (variance * 20))
        return round(score, 1)

    def _evaluate_vocabulary_richness(self, text: str) -> float:
        """
        Evaluate vocabulary richness on a 1-10 scale.
        Based on the ratio of unique words to total words.
        """
        words = re.findall(r"\b\w+\b", text.lower())

        if not words:
            return 0.0

        unique_words = set(words)
        unique_ratio = len(unique_words) / len(words)

        score = 0
        if unique_ratio >= 0.70:
            score = 9
        elif unique_ratio >= 0.65:
            score = 8
        elif unique_ratio >= 0.60:
            score = 7
        elif unique_ratio >= 0.55:
            score = 6
        elif unique_ratio >= 0.50:
            score = 5
        elif unique_ratio >= 0.45:
            score = 4
        elif unique_ratio >= 0.40:
            score = 3
        elif unique_ratio >= 0.35:
            score = 2
        else:
            score = 1

        return float(score)

    def _calculate_overall_score(
        self,
        word_count: int,
        dialogue_ratio: float,
        sentence_variety: float,
        vocabulary_richness: float,
    ) -> float:
        """
        Calculate an overall quality score (1-10) based on all metrics.
        """
        scores = []

        if word_count >= self.thresholds["min_words"]:
            scores.append(8)
        else:
            scores.append(word_count / self.thresholds["min_words"] * 8)

        if (
            self.thresholds["min_dialogue_ratio"]
            <= dialogue_ratio
            <= self.thresholds["max_dialogue_ratio"]
        ):
            scores.append(8)
        else:
            distance = min(
                abs(dialogue_ratio - self.thresholds["min_dialogue_ratio"]),
                abs(dialogue_ratio - self.thresholds["max_dialogue_ratio"]),
            )
            scores.append(max(2, 8 - (distance * 20)))

        scores.append(sentence_variety)
        scores.append(vocabulary_richness)

        overall = sum(scores) / len(scores)
        return round(overall, 1)

    def generate_quality_report(
        self, metrics: QualityMetrics, dialogue_expected: bool = True
    ) -> str:
        """
        Generate a human-readable quality report.

        Args:
            metrics: QualityMetrics object
            dialogue_expected: Whether dialogue was expected for this chapter

        Returns:
            Formatted string report
        """
        report = []
        report.append(f"Word Count: {metrics.word_count:,} (min: {self.thresholds['min_words']:,})")

        # Only show dialogue ratio requirements if dialogue was expected
        if dialogue_expected:
            report.append(
                f"Dialogue Ratio: {metrics.dialogue_ratio:.1%} (range: {self.thresholds['min_dialogue_ratio']:.1%}-{self.thresholds['max_dialogue_ratio']:.1%})"
            )
        else:
            report.append(
                f"Dialogue Ratio: {metrics.dialogue_ratio:.1%} (dialogue not required for this chapter type)"
            )

        report.append(
            f"Sentence Variety: {metrics.sentence_variety_score}/10 (min: {self.thresholds['min_sentence_variety']})"
        )
        report.append(
            f"Vocabulary Richness: {metrics.vocabulary_richness_score}/10 (min: {self.thresholds['min_vocabulary_richness']})"
        )
        report.append(f"Overall Score: {metrics.overall_score}/10")

        if metrics.issues:
            report.append("\nIssues:")
            for issue in metrics.issues:
                report.append(f"  - {issue}")
        else:
            report.append("\n✓ All quality thresholds met")

        return "\n".join(report)
