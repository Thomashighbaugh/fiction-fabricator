"""
content_enhancements.py - Advanced content analysis and enhancement tools
"""
import re
from collections import Counter
from dataclasses import dataclass
from enum import Enum


class DialogueTag(str, Enum):
    """Types of dialogue tags."""

    SAID = "said"
    ASKED = "asked"
    REPLIED = "replied"
    ANSWERED = "answered"
    WHISPERED = "whispered"
    SHOUTED = "shouted"
    SCREAMED = "screamed"
    MURMURED = "murmured"
    MUTTERED = "muttered"
    MUMBLED = "mumbled"
    EXCLAIMED = "exclaimed"
    CRIED = "cried"
    GROWLED = "growled"
    SNAPPED = "snapped"
    BARKED = "barked"
    GASPED = "gasped"
    TAGLESS = "tagless"


@dataclass
class SubBeatValidation:
    """Results of sub-beat validation."""

    is_valid: bool
    coherence_score: float  # 0-1
    comprehensiveness_score: float  # 0-1
    issues: list[str]
    suggestions: list[str]


@dataclass
class DialogueTagAnalysis:
    """Analysis of dialogue tag usage."""

    tag_counts: dict[str, int]
    total_dialogue_lines: int
    variety_score: float  # 0-1, higher is better
    overused_tags: list[tuple[str, int]]  # (tag, count) for tags used too frequently
    suggestions: list[str]


@dataclass
class SentenceVarietyAnalysis:
    """Detailed sentence variety analysis."""

    sentence_lengths: list[int]
    avg_length: float
    median_length: float
    std_dev: float
    length_distribution: dict[str, int]  # short, medium, long, very_long
    variety_score: float  # 0-1
    patterns: list[str]  # Repeated patterns detected
    suggestions: list[str]


class ContentEnhancer:
    """Advanced content analysis and enhancement tools."""

    def __init__(self):
        self.dialogue_tag_alternatives = {
            "said": [
                "replied",
                "answered",
                "responded",
                "observed",
                "noted",
                "continued",
                "went on",
                "added",
                "commented",
                "remarked",
            ],
            "asked": ["inquired", "questioned", "wondered", "queried"],
            "replied": ["responded", "answered", "returned", "countered"],
            "answered": ["responded", "replied", "explained", "elaborated"],
            "whispered": ["murmured", "breathed", "hissed", "muttered", "said quietly"],
            "shouted": ["yelled", "called out", "bellowed", "roared"],
            "screamed": ["shrieked", "howled", "cried out", "wailed"],
            "murmured": ["whispered", "muttered", "breathed", "said softly"],
            "growled": ["grumbled", "snarled", "hissed"],
            "snapped": ["barked", "bit out", "shot back"],
        }

    def validate_sub_beats(self, sub_beats: list[str], chapter_summary: str) -> SubBeatValidation:
        """
        Validate that sub-beats are coherent and comprehensive.

        Args:
            sub_beats: List of sub-beat descriptions
            chapter_summary: Overall chapter summary for context

        Returns:
            SubBeatValidation with scores and suggestions
        """
        if not sub_beats:
            return SubBeatValidation(
                is_valid=False,
                coherence_score=0.0,
                comprehensiveness_score=0.0,
                issues=["No sub-beats provided"],
                suggestions=["Add sub-beats to define chapter structure"],
            )

        issues = []
        suggestions = []
        coherence_score = 0.0
        comprehensiveness_score = 0.0

        # Check 1: Logical flow between sub-beats
        coherence_score = self._check_sub_beat_flow(sub_beats)
        if coherence_score < 0.5:
            issues.append("Sub-beats lack logical flow")
            suggestions.append("Ensure each sub-beat naturally follows from the previous one")

        # Check 2: Coverage of chapter summary
        summary_words = set(chapter_summary.lower().split())
        beat_words = set()
        for beat in sub_beats:
            beat_words.update(beat.lower().split())

        coverage = len(summary_words & beat_words) / len(summary_words) if summary_words else 0
        comprehensiveness_score = coverage

        if coverage < 0.6:
            issues.append(f"Sub-beats cover only {coverage:.0%} of chapter summary elements")
            suggestions.append("Ensure sub-beats collectively address all key events in summary")

        # Check 3: Appropriate detail level
        too_vague = [b for b in sub_beats if len(b.split()) < 3]
        if too_vague:
            issues.append(f"{len(too_vague)} sub-beat(s) are too vague")
            suggestions.append(
                "Add more detail to vague sub-beats (e.g., specify actions, emotions, settings)"
            )

        # Check 4: Avoid redundancy
        unique_beats = set(b.lower() for b in sub_beats)
        if len(unique_beats) < len(sub_beats):
            duplicate_count = len(sub_beats) - len(unique_beats)
            issues.append(f"{duplicate_count} duplicate sub-beat(s)")
            suggestions.append("Remove redundant sub-beats or merge similar ones")

        # Check 5: Logical progression
        progression_score = self._check_logical_progression(sub_beats)
        coherence_score = (coherence_score + progression_score) / 2

        if progression_score < 0.5:
            issues.append("Sub-beats don't show clear progression")
            suggestions.append(
                "Ensure sub-beats move the story forward with clear cause-and-effect"
            )

        is_valid = coherence_score >= 0.6 and comprehensiveness_score >= 0.6

        return SubBeatValidation(
            is_valid=is_valid,
            coherence_score=coherence_score,
            comprehensiveness_score=comprehensiveness_score,
            issues=issues,
            suggestions=suggestions,
        )

    def _check_sub_beat_flow(self, sub_beats: list[str]) -> float:
        """Check how well sub-beats flow into each other."""
        if len(sub_beats) < 2:
            return 1.0

        flow_score = 0.0
        transitions = 0

        for i in range(len(sub_beats) - 1):
            current = sub_beats[i].lower()
            next_beat = sub_beats[i + 1].lower()

            # Good transition indicators
            transition_words = ["then", "next", "after", "following", "before", "when"]
            has_transition = any(
                current.endswith(tw) or next_beat.startswith(tw) for tw in transition_words
            )

            # Check for contradiction
            contradiction_words = [
                ("not", "never"),
                ("cannot", "can"),
                ("didn't", "did"),
                ("doesn't", "does"),
                ("won't", "will"),
            ]
            has_contradiction = any(
                neg1 in current and neg2 in next_beat for neg1, neg2 in contradiction_words
            )

            if has_transition and not has_contradiction:
                flow_score += 1.0
            elif not has_contradiction:
                flow_score += 0.5

            transitions += 1

        return flow_score / transitions if transitions > 0 else 1.0

    def _check_logical_progression(self, sub_beats: list[str]) -> float:
        """Check if sub-beats show logical story progression."""
        if not sub_beats:
            return 0.0

        # Look for progression indicators
        action_verbs_start = set()
        action_verbs_end = set()
        for beat in sub_beats:
            words = beat.lower().split()
            if words:
                # First word often indicates action
                first_word = words[0].strip(".,!?;")
                last_word = words[-1].strip(".,!?;")
                if len(first_word) > 2:
                    action_verbs_start.add(first_word)
                if len(last_word) > 2:
                    action_verbs_end.add(last_word)

        # Check for variety in progression
        progression_score = min(1.0, len(action_verbs_start) / len(sub_beats) * 2)

        return progression_score

    def predict_word_count(self, sub_beats: list[str], words_per_sub_beat: int = 150) -> dict:
        """
        Predict word count from sub-beat count.

        Args:
            sub_beats: List of sub-beats
            words_per_sub_beat: Average words per sub-beat (default 150)

        Returns:
            Dict with predicted count and confidence
        """
        base_count = len(sub_beats) * words_per_sub_beat

        # Adjust based on sub-beat complexity
        avg_beat_length = (
            sum(len(b.split()) for b in sub_beats) / len(sub_beats) if sub_beats else 0
        )

        complexity_multiplier = 1.0
        if avg_beat_length > 8:
            complexity_multiplier = 1.3  # More complex beats need more words
        elif avg_beat_length > 5:
            complexity_multiplier = 1.1
        elif avg_beat_length < 4:
            complexity_multiplier = 0.9

        predicted_count = int(base_count * complexity_multiplier)

        # Calculate confidence based on sub-beat count
        confidence = min(0.95, 0.7 + (len(sub_beats) / 50))

        return {
            "predicted_words": predicted_count,
            "confidence": confidence,
            "sub_beat_count": len(sub_beats),
            "words_per_sub_beat": words_per_sub_beat,
            "complexity_multiplier": complexity_multiplier,
        }

    def generate_chapter_hooks(
        self, chapter_summary: str, next_chapter_summary: str = ""
    ) -> dict[str, str]:
        """
        Generate hooks that connect current chapter to the next.

        Args:
            chapter_summary: Summary of current chapter
            next_chapter_summary: Summary of next chapter (if available)

        Returns:
            Dict of hook types and their generated hooks
        """
        hooks = {}

        # Hook type 1: Narrative hook (unresolved situation)
        hooks["narrative"] = self._generate_narrative_hook(chapter_summary, next_chapter_summary)

        # Hook type 2: Emotional hook (character in emotional state)
        hooks["emotional"] = self._generate_emotional_hook(chapter_summary)

        # Hook type 3: Mystery hook (question or revelation)
        hooks["mystery"] = self._generate_mystery_hook(chapter_summary)

        # Hook type 4: Action hook (immediate consequence)
        hooks["action"] = self._generate_action_hook(chapter_summary, next_chapter_summary)

        # Hook type 5: Character hook (character's decision/realization)
        hooks["character"] = self._generate_character_hook(chapter_summary)

        return hooks

    def _generate_narrative_hook(self, chapter_summary: str, next_chapter_summary: str = "") -> str:
        """Generate a narrative continuity hook."""
        if next_chapter_summary:
            return f"""
This sets up a narrative bridge to the next chapter where {next_chapter_summary[:100]}...
Consider ending with a moment that naturally leads into this next development.
"""
        else:
            return """
End with a narrative bridge that suggests consequences of current events.
Create a sense of "what happens next?" without explicitly stating it.
"""

    def _generate_emotional_hook(self, chapter_summary: str) -> str:
        """Generate an emotional state hook."""
        return """
Place the main character in a compelling emotional state at chapter's end.
Consider: anxiety, hope, determination, confusion, or emotional conflict.
Let this emotional state drive curiosity about how they'll handle what's next.
"""

    def _generate_mystery_hook(self, chapter_summary: str) -> str:
        """Generate a mystery/intrigue hook."""
        return """
Introduce a subtle question or revelation at the chapter's end.
Options:
- A character notices something they can't explain
- A clue is discovered but its meaning is unclear
- A hint about a larger mystery or conspiracy
- An unexpected connection between seemingly unrelated elements
"""

    def _generate_action_hook(self, chapter_summary: str, next_chapter_summary: str = "") -> str:
        """Generate an action-oriented hook."""
        if next_chapter_summary:
            return f"""
Set up an immediate action that connects to the next chapter.
The final action should naturally lead into: {next_chapter_summary[:100]}...
Consider: an interrupted action, a decision to act, or a consequence unfolding.
"""
        else:
            return """
End with an action that has immediate consequences.
The final action should create tension: a chase begins, a trap springs, a choice must be made.
"""

    def _generate_character_hook(self, chapter_summary: str) -> str:
        """Generate a character development hook."""
        return """
Show a character making a crucial decision or having a realization.
This sets up their internal conflict or motivation for the next chapter.
Consider:
- A character realizes they've been wrong about something
- A character chooses between two options
- A character commits to a course of action
"""

    def analyze_dialogue_tags(self, content_text: str) -> DialogueTagAnalysis:
        """
        Analyze dialogue tag usage for variety and overuse.

        Args:
            content_text: Prose content to analyze

        Returns:
            DialogueTagAnalysis with counts and suggestions
        """
        # Extract dialogue with tags
        dialogue_pattern = r'"([^"]*)"\s+([a-z]+)'
        matches = re.findall(dialogue_pattern, content_text.lower())

        if not matches:
            return DialogueTagAnalysis(
                tag_counts={},
                total_dialogue_lines=0,
                variety_score=0.0,
                overused_tags=[],
                suggestions=["No dialogue tags found - consider adding some for clarity"],
            )

        tag_counts = Counter(tag for _, tag in matches)
        total_lines = len(matches)

        # Calculate variety score (0-1)
        unique_tags = len(tag_counts)
        max_possible_variety = min(10, total_lines)  # Diminishing returns after 10
        variety_score = unique_tags / max_possible_variety if max_possible_variety > 0 else 0

        # Find overused tags (used > 20% of total)
        threshold = max(2, total_lines * 0.2)
        overused_tags = [(tag, count) for tag, count in tag_counts.items() if count > threshold]
        overused_tags.sort(key=lambda x: x[1], reverse=True)

        # Generate suggestions
        suggestions = []

        if variety_score < 0.4:
            suggestions.append(
                f"Dialogue tag variety is low ({unique_tags} unique tags for {total_lines} lines). "
                "Consider using alternatives to common tags like 'said'."
            )

        for tag, count in overused_tags:
            percentage = (count / total_lines) * 100
            suggestions.append(
                f"'{tag}' is overused ({count} times, {percentage:.0%} of dialogue). "
                f"Consider these alternatives: {', '.join(self.dialogue_tag_alternatives.get(tag, [])[:3])}"
            )

        # Check for tagless dialogue (might be intentional or missing)
        tagless_pattern = r'"([^"]*)"\s*[.!?]"'
        tagless_matches = re.findall(tagless_pattern, content_text)
        tagless_ratio = len(tagless_matches) / total_lines if total_lines > 0 else 0

        if tagless_ratio > 0.3:
            suggestions.append(
                f"{tagless_ratio:.0%} of dialogue lines are tagless. "
                "Consider if this is intentional or if tags would improve clarity."
            )

        return DialogueTagAnalysis(
            tag_counts=dict(tag_counts),
            total_dialogue_lines=total_lines,
            variety_score=variety_score,
            overused_tags=overused_tags,
            suggestions=suggestions,
        )

    def analyze_sentence_variety_detailed(self, content_text: str) -> SentenceVarietyAnalysis:
        """
        Detailed sentence variety analysis.

        Args:
            content_text: Prose content to analyze

        Returns:
            SentenceVarietyAnalysis with detailed metrics
        """
        # Split into sentences
        sentences = re.split(r"[.!?]+", content_text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return SentenceVarietyAnalysis(
                sentence_lengths=[],
                avg_length=0,
                median_length=0,
                std_dev=0,
                length_distribution={},
                variety_score=0.0,
                patterns=[],
                suggestions=["No sentences to analyze"],
            )

        # Calculate lengths
        sentence_lengths = [len(s.split()) for s in sentences]

        # Statistics
        avg_length = sum(sentence_lengths) / len(sentence_lengths)
        sorted_lengths = sorted(sentence_lengths)
        median_length = sorted_lengths[len(sorted_lengths) // 2]

        # Standard deviation
        variance = sum((l - avg_length) ** 2 for l in sentence_lengths) / len(sentence_lengths)
        std_dev = variance**0.5

        # Length distribution
        distribution = {
            "short": sum(1 for l in sentence_lengths if l < 10),
            "medium": sum(1 for l in sentence_lengths if 10 <= l < 25),
            "long": sum(1 for l in sentence_lengths if 25 <= l < 40),
            "very_long": sum(1 for l in sentence_lengths if l >= 40),
        }

        # Variety score (0-1)
        # Ideal: 25% short, 45% medium, 20% long, 10% very_long
        total = len(sentence_lengths)
        if total > 0:
            ideal = {"short": 0.25, "medium": 0.45, "long": 0.20, "very_long": 0.10}

            actual_ratios = {k: v / total for k, v in distribution.items()}

            # Calculate deviation from ideal
            deviation = sum(abs(actual_ratios[k] - ideal[k]) for k in ideal)

            variety_score = max(0, 1.0 - deviation * 2)
        else:
            variety_score = 0.0

        # Detect patterns
        patterns = []
        patterns.extend(self._detect_repeated_structures(sentences))
        patterns.extend(self._detect_sentence_start_patterns(sentences))

        # Generate suggestions
        suggestions = []

        if variety_score < 0.5:
            suggestions.append(
                "Sentence variety is low. Aim for mix of 25% short, 45% medium, "
                "20% long, and 10% very long sentences."
            )

        # Check distribution issues
        if distribution["short"] / total > 0.40:
            suggestions.append(
                "Too many short sentences (<10 words). Combine some to create variety."
            )

        if distribution["very_long"] / total > 0.15:
            suggestions.append(
                "Too many very long sentences (40+ words). Break some up for readability."
            )

        if std_dev < 5:
            suggestions.append("Sentence lengths are too uniform. Vary them more for better flow.")

        if patterns:
            suggestions.append(
                f"Detected {len(patterns)} repetitive sentence patterns. "
                "Vary sentence structure to avoid monotony."
            )

        return SentenceVarietyAnalysis(
            sentence_lengths=sentence_lengths,
            avg_length=avg_length,
            median_length=median_length,
            std_dev=std_dev,
            length_distribution=distribution,
            variety_score=variety_score,
            patterns=patterns,
            suggestions=suggestions,
        )

    def _detect_repeated_structures(self, sentences: list[str]) -> list[str]:
        """Detect repeated sentence structures."""
        structures = []

        for sentence in sentences:
            words = sentence.lower().split()
            if len(words) < 3:
                continue

            # Simple structure: subject-verb pattern
            if len(words) >= 3 and len(words) <= 8:
                structure = " ".join([words[0], words[1]])
                structures.append(structure)

        # Find repeats
        structure_counts = Counter(structures)
        repeated = [
            f"'{structure}' appears {count} times"
            for structure, count in structure_counts.items()
            if count > 2
        ]

        return repeated[:5]  # Return top 5

    def _detect_sentence_start_patterns(self, sentences: list[str]) -> list[str]:
        """Detect repeated sentence starting patterns."""
        starts = []

        for sentence in sentences:
            words = sentence.split()
            if words:
                first_two = " ".join(words[:2]).lower()
                starts.append(first_two)

        start_counts = Counter(starts)
        repeated = [
            f"Sentences starting with '{start}' appear {count} times"
            for start, count in start_counts.items()
            if count > 2
        ]

        return repeated[:5]  # Return top 5

    def generate_improvement_prompt(
        self,
        sub_beat_validation: SubBeatValidation | None = None,
        word_count_prediction: dict | None = None,
        dialogue_analysis: DialogueTagAnalysis | None = None,
        sentence_analysis: SentenceVarietyAnalysis | None = None,
    ) -> str:
        """
        Generate a comprehensive improvement prompt for LLM.

        Args:
            sub_beat_validation: Sub-beat validation results
            word_count_prediction: Word count prediction data
            dialogue_analysis: Dialogue tag analysis
            sentence_analysis: Sentence variety analysis

        Returns:
            Formatted prompt for LLM improvements
        """
        prompt_parts = ["IMPROVEMENT SUGGESTIONS:\n"]

        if sub_beat_validation:
            prompt_parts.append("\n### Sub-Beat Quality:")
            if not sub_beat_validation.is_valid:
                prompt_parts.append("Issues:")
                for issue in sub_beat_validation.issues:
                    prompt_parts.append(f"  - {issue}")
                prompt_parts.append("\nSuggestions:")
                for suggestion in sub_beat_validation.suggestions:
                    prompt_parts.append(f"  - {suggestion}")

        if word_count_prediction:
            prompt_parts.append("\n### Word Count Prediction:")
            prompt_parts.append(
                f"Predicted: {word_count_prediction['predicted_words']} words "
                f"(confidence: {word_count_prediction['confidence']:.0%})"
            )
            if word_count_prediction["predicted_words"] < 2000:
                prompt_parts.append("  Consider expanding to reach minimum word count.")

        if dialogue_analysis and dialogue_analysis.suggestions:
            prompt_parts.append("\n### Dialogue Tag Variety:")
            for suggestion in dialogue_analysis.suggestions:
                prompt_parts.append(f"  - {suggestion}")

        if sentence_analysis and sentence_analysis.suggestions:
            prompt_parts.append("\n### Sentence Variety:")
            for suggestion in sentence_analysis.suggestions:
                prompt_parts.append(f"  - {suggestion}")

        return "\n".join(prompt_parts)

    def get_quick_suggestions(self, content_text: str, chapter_summary: str = "") -> list[str]:
        """
        Get quick improvement suggestions for content.

        Args:
            content_text: Prose content
            chapter_summary: Chapter summary (optional)

        Returns:
            List of prioritized suggestions
        """
        suggestions = []

        # Check dialogue tags
        dialogue_analysis = self.analyze_dialogue_tags(content_text)
        if dialogue_analysis.suggestions:
            suggestions.extend(dialogue_analysis.suggestions[:2])

        # Check sentence variety
        sentence_analysis = self.analyze_sentence_variety_detailed(content_text)
        if sentence_analysis.suggestions:
            suggestions.extend(sentence_analysis.suggestions[:2])

        # Check for repeated words
        words = re.findall(r"\b\w+\b", content_text.lower())
        word_counts = Counter(words)
        repeated_words = [(w, c) for w, c in word_counts.items() if c > 5 and len(w) > 4]
        repeated_words.sort(key=lambda x: x[1], reverse=True)

        if repeated_words:
            top_repeat = repeated_words[0]
            suggestions.append(
                f"Word '{top_repeat[0]}' appears {top_repeat[1]} times. "
                "Consider using synonyms or rephrasing."
            )

        return suggestions[:5]  # Return top 5 suggestions
