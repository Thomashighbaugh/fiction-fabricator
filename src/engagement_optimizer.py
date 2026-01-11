# -*- coding: utf-8 -*-
"""
engagement_optimizer.py - Reader engagement optimization system
"""
import re
import json
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class EmotionalBeat(str, Enum):
    """Types of emotional beats in narrative."""
    SETUP = "setup"
    TENSION_BUILD = "tension_build"
    CONFLICT = "conflict"
    CLIMAX = "climax"
    RELEASE = "release"
    RESOLUTION = "resolution"
    CLIFFHANGER = "cliffhanger"


@dataclass
class EmotionalBeatData:
    """Data class for emotional beat analysis."""
    beat_type: EmotionalBeat
    position: float
    intensity: float
    description: str


@dataclass
class EngagementAnalysis:
    """Results of engagement analysis."""
    has_cliffhanger: bool
    cliffhanger_strength: float
    emotional_arc_score: float
    tension_cycles: List[Dict]
    suggestions: List[str]
    overall_engagement_score: float


class EngagementOptimizer:
    """Analyzes and optimizes reader engagement in content."""

    def __init__(self):
        self.cliffhanger_patterns = [
            r'(?i)(?:sudden|abrupt|unexpected)\s+(?:noise|sound|movement|discovery)',
            r'(?i)(?:what|huh|who)(?:\'s)?\s+there',
            r'(?i)(?:then|but)\s+(?:suddenly|everything changed)',
            r'(?i)just as.*(?:was about to|going to)',
            r'(?i)couldn\'t have(?:\s+known|\s+guessed)',
            r'(?i)(?:the|a|an)\s+(?:door|sound|voice|figure)\s+(?:opened|called|appeared)',
            r'\.\.\.$',
        ]

    def analyze_chapter_engagement(self, content_text: str, chapter_context: Dict | None = None) -> EngagementAnalysis:
        """
        Analyze chapter for engagement elements.

        Args:
            content_text: The prose content of the chapter
            chapter_context: Additional context about the chapter (position, etc.)

        Returns:
            EngagementAnalysis with findings and suggestions
        """
        cliffhanger_analysis = self._analyze_cliffhanger(content_text)
        emotional_arc = self._analyze_emotional_arc(content_text)
        tension_cycles = self._analyze_tension_cycles(content_text)
        suggestions = self._generate_engagement_suggestions(
            cliffhanger_analysis, emotional_arc, tension_cycles, chapter_context
        )

        overall_score = self._calculate_overall_engagement_score(
            cliffhanger_analysis['has_cliffhanger'],
            cliffhanger_analysis['strength'],
            emotional_arc['score'],
            len(tension_cycles)
        )

        return EngagementAnalysis(
            has_cliffhanger=cliffhanger_analysis['has_cliffhanger'],
            cliffhanger_strength=cliffhanger_analysis['strength'],
            emotional_arc_score=emotional_arc['score'],
            tension_cycles=tension_cycles,
            suggestions=suggestions,
            overall_engagement_score=overall_score
        )

    def _analyze_cliffhanger(self, text: str) -> Dict:
        """
        Analyze if the chapter ends with a cliffhanger.
        Returns analysis dict with has_cliffhanger and strength (0-1).
        """
        if not text or not text.strip():
            return {'has_cliffhanger': False, 'strength': 0.0}

        sentences = re.split(r'[.!?]+', text.strip())
        if not sentences:
            return {'has_cliffhanger': False, 'strength': 0.0}

        last_sentence = sentences[-1].strip()
        last_paragraph = self._get_last_paragraph(text)

        cliffhanger_indicators = 0

        for pattern in self.cliffhanger_patterns:
            if re.search(pattern, last_sentence):
                cliffhanger_indicators += 1

        if '...' in last_sentence:
            cliffhanger_indicators += 1

        if re.search(r'[?!]+$', last_paragraph.strip()):
            cliffhanger_indicators += 1

        if self._has_unresolved_question(last_paragraph):
            cliffhanger_indicators += 1

        if self._has_sudden_action(last_paragraph):
            cliffhanger_indicators += 1

        has_cliffhanger = cliffhanger_indicators >= 2
        strength = min(1.0, cliffhanger_indicators / 3.0)

        return {
            'has_cliffhanger': has_cliffhanger,
            'strength': strength
        }

    def _analyze_emotional_arc(self, text: str) -> Dict:
        """
        Analyze the emotional arc of the chapter.
        Returns dict with score (0-1) and beat data.
        """
        sentences = re.split(r'[.!?]+', text.strip())
        if not sentences:
            return {'score': 0.0, 'beats': []}

        beats = []
        total_sentences = len(sentences)

        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue

            position = i / total_sentences
            beat_type = self._detect_emotional_beat(sentence, position)
            intensity = self._measure_emotional_intensity(sentence)

            if beat_type:
                beats.append({
                    'type': beat_type,
                    'position': position,
                    'intensity': intensity,
                    'sentence': sentence[:50] + '...' if len(sentence) > 50 else sentence
                })

        score = self._evaluate_emotional_arc_quality(beats, total_sentences)

        return {
            'score': score,
            'beats': beats
        }

    def _detect_emotional_beat(self, sentence: str, position: float) -> str | None:
        """
        Detect the type of emotional beat in a sentence.
        """
        sentence_lower = sentence.lower()

        if position < 0.2:
            return EmotionalBeat.SETUP

        tension_words = ['worried', 'feared', 'tense', 'anxious', 'nervous', 'danger', 'threat',
                       'rising', 'building', 'growing', 'increasing']
        if any(word in sentence_lower for word in tension_words):
            return EmotionalBeat.TENSION_BUILD

        conflict_words = ['fight', 'argued', 'clashed', 'struggled', 'battle', 'war',
                        'angry', 'furious', 'rage', 'violence', 'confronted']
        if any(word in sentence_lower for word in conflict_words):
            return EmotionalBeat.CONFLICT

        climax_words = ['exploded', 'shattered', 'crashed', 'screamed', 'died', 'dying',
                      'everything changed', 'nothing would ever be the same', 'ultimate', 'final']
        if any(word in sentence_lower for word in climax_words):
            return EmotionalBeat.CLIMAX

        release_words = ['sighed', 'relaxed', 'calmed', 'peaceful', 'relief', 'safe',
                       'finally', 'over', 'done', 'settled']
        if any(word in sentence_lower for word in release_words):
            return EmotionalBeat.RELEASE

        resolution_words = ['learned', 'understood', 'realized', 'accepted', 'moved on',
                         'changed', 'grown', 'forgiven', 'together']
        if any(word in sentence_lower for word in resolution_words):
            return EmotionalBeat.RESOLUTION

        return None

    def _measure_emotional_intensity(self, sentence: str) -> float:
        """
        Measure the emotional intensity of a sentence (0-1).
        """
        high_intensity_words = ['screamed', 'shouted', 'cried', 'terrified', 'horrified',
                             'ecstatic', 'overwhelmed', 'devastated', 'exploded', 'shattered']
        medium_intensity_words = ['worried', 'angry', 'happy', 'excited', 'nervous',
                               'calm', 'relieved', 'confused', 'surprised']

        sentence_lower = sentence.lower()

        if any(word in sentence_lower for word in high_intensity_words):
            return 0.8
        elif any(word in sentence_lower for word in medium_intensity_words):
            return 0.5

        return 0.2

    def _evaluate_emotional_arc_quality(self, beats: List[Dict], total_sentences: int) -> float:
        """
        Evaluate the quality of the emotional arc.
        Returns score from 0-1.
        """
        if not beats:
            return 0.0

        beat_types = [b['type'] for b in beats]
        unique_beats = set(beat_types)

        if len(unique_beats) < 3:
            return 0.3

        has_climax = EmotionalBeat.CLIMAX in unique_beats
        has_resolution = EmotionalBeat.RESOLUTION in unique_beats
        has_tension = EmotionalBeat.TENSION_BUILD in unique_beats

        score = 0.0

        if has_tension:
            score += 0.3
        if has_climax:
            score += 0.4
        if has_resolution:
            score += 0.2
        if len(unique_beats) >= 5:
            score += 0.1

        return min(1.0, score)

    def _analyze_tension_cycles(self, text: str) -> List[Dict]:
        """
        Identify tension/release cycles in the chapter.
        Returns list of cycle data.
        """
        sentences = re.split(r'[.!?]+', text.strip())
        if not sentences:
            return []

        cycles = []
        current_tension = 0.0
        in_tension = False

        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue

            sentence_tension = self._measure_tension_level(sentence)

            if sentence_tension > 0.5 and not in_tension:
                cycles.append({
                    'start_position': i,
                    'peak_tension': sentence_tension,
                    'type': 'tension_rise'
                })
                in_tension = True
            elif sentence_tension < 0.3 and in_tension:
                if cycles:
                    cycles[-1]['end_position'] = i
                    cycles[-1]['type'] = 'complete'
                in_tension = False

            current_tension = sentence_tension

        return cycles

    def _measure_tension_level(self, sentence: str) -> float:
        """
        Measure the tension level of a sentence (0-1).
        """
        high_tension_words = ['danger', 'death', 'kill', 'threat', 'escape', 'urgent',
                           'impossible', 'now', 'suddenly', 'terror', 'panic', 'die']
        medium_tension_words = ['worried', 'feared', 'nervous', 'anxious', 'concerned',
                              'hesitated', 'uncertain', 'risk']

        sentence_lower = sentence.lower()

        high_count = sum(1 for word in high_tension_words if word in sentence_lower)
        medium_count = sum(1 for word in medium_tension_words if word in sentence_lower)

        tension_score = (high_count * 0.4) + (medium_count * 0.2)
        return min(1.0, tension_score)

    def _generate_engagement_suggestions(self, cliffhanger: Dict, emotional_arc: Dict,
                                       tension_cycles: List, context: Dict | None = None) -> List[str]:
        """
        Generate suggestions to improve engagement.
        """
        suggestions = []

        if not cliffhanger['has_cliffhanger']:
            suggestions.append(
                "Consider ending with a cliffhanger: introduce an unexpected discovery, "
                "abrupt action, or unresolved question to hook readers for the next chapter."
            )
        elif cliffhanger['strength'] < 0.5:
            suggestions.append(
                "The chapter ending could be stronger. Consider making the cliffhanger more dramatic "
                "or raising the stakes of the unresolved situation."
            )

        if emotional_arc['score'] < 0.5:
            suggestions.append(
                "The emotional arc needs development. Ensure the chapter has clear tension buildup, "
                "climax, and resolution points. Consider adding more emotional variety."
            )

        if len(tension_cycles) < 2:
            suggestions.append(
                "Add tension/release cycles throughout the chapter. Short moments of relief make "
                "high-tension moments more impactful and maintain reader engagement."
            )

        if emotional_arc['beats']:
            climax_beats = [b for b in emotional_arc['beats'] if b['type'] == EmotionalBeat.CLIMAX]
            if not climax_beats:
                suggestions.append(
                    "The chapter lacks a clear climax. Add a moment of peak tension or emotional "
                    "intensity that resolves the chapter's primary conflict."
                )

        if context and context.get('is_last_chapter'):
            if cliffhanger['has_cliffhanger']:
                suggestions.append(
                    "As the final chapter, consider providing more resolution rather than a cliffhanger. "
                    "Readers expect closure at story's end."
                )

        return suggestions

    def _calculate_overall_engagement_score(self, has_cliffhanger: bool,
                                          cliffhanger_strength: float,
                                          emotional_score: float,
                                          cycle_count: int) -> float:
        """
        Calculate overall engagement score (0-1).
        """
        scores = []

        if has_cliffhanger:
            scores.append(cliffhanger_strength)
        else:
            scores.append(0.0)

        scores.append(emotional_score)
        scores.append(min(1.0, cycle_count / 3.0))

        return round(sum(scores) / len(scores), 2)

    def _get_last_paragraph(self, text: str) -> str:
        """Get the last paragraph of the text."""
        paragraphs = re.split(r'\n\n+', text.strip())
        return paragraphs[-1] if paragraphs else ""

    def _has_unresolved_question(self, text: str) -> bool:
        """Check if text contains unresolved questions."""
        return bool(re.search(r'(?:who|what|where|when|why|how)\s+(?:was|is|did|would|could)', text, re.IGNORECASE))

    def _has_sudden_action(self, text: str) -> bool:
        """Check if text indicates sudden action."""
        sudden_action_words = ['suddenly', 'instantly', 'abruptly', 'without warning', 'shock', 'startled']
        return any(word in text.lower() for word in sudden_action_words)

    def generate_cliffhanger_suggestion(self, content_text: str, chapter_summary: str = "",
                                       next_chapter_summary: str = "") -> str | None:
        """
        Generate a suggested cliffhanger ending for a chapter.

        Args:
            content_text: Current chapter content
            chapter_summary: Summary of this chapter
            next_chapter_summary: Summary of next chapter (for context)

        Returns:
            Suggested ending paragraph
        """
        current_ending = self._get_last_paragraph(content_text)
        current_sentences = re.split(r'[.!?]+', current_ending)
        last_sentence = current_sentences[-1] if current_sentences else ""

        suggestion = f"""
Based on the chapter's content, here are cliffhanger suggestions:

**Current ending:** {last_sentence if last_sentence else '(No clear ending)'}

**Cliffhanger options to consider:**

1. **Unresolved Mystery:**
   End with a discovery that raises more questions than answers.
   - Someone appears who shouldn't be there
   - A crucial object goes missing
   - A lie is revealed at the worst moment

2. **Imminent Danger:**
   Cut off right before disaster strikes.
   - A threat reveals itself
   - A trap springs
   - Time runs out

3. **Shocking Revelation:**
   Drop a truth that changes everything.
   - A character's secret is exposed
   - An ally shows their true colors
   - The real enemy is revealed

4. **Abrupt Action:**
   End mid-action with no resolution.
   - A chase begins
   - An attack comes from nowhere
   - A critical decision is interrupted

**Choose based on:**
- What best serves your story's tone and genre
- What naturally grows from the chapter's events
- What creates genuine curiosity, not artificial suspense
"""

        return suggestion

    def create_engagement_prompt(self, content_text: str, chapter_summary: str,
                              genre_guidance: str = "", current_word_count: int = 0) -> str:
        """
        Create a prompt for LLM to improve engagement.

        Args:
            content_text: Current chapter content
            chapter_summary: Summary of the chapter
            genre_guidance: Genre-specific guidance
            current_word_count: Current word count to preserve or exceed

        Returns:
            Prompt for LLM
        """
        analysis = self.analyze_chapter_engagement(content_text)

        word_count_instruction = f"""
**CRITICAL WORD COUNT REQUIREMENT:**
- Current chapter word count: {current_word_count:,} words
- You MUST maintain or EXCEED this word count
- Do NOT shorten the chapter
- If anything, add more detail, description, and depth to increase engagement while maintaining length
- Engagement should come from more compelling content, not fewer words
""" if current_word_count > 0 else ""

        prompt = f"""
You are enhancing reader engagement for a chapter.

**Chapter Summary:**
{chapter_summary}

{genre_guidance}

**Current Engagement Analysis:**
- Has cliffhanger: {'Yes' if analysis.has_cliffhanger else 'No'} (strength: {analysis.cliffhanger_strength:.0%})
- Emotional arc score: {analysis.emotional_arc_score:.0%}
- Tension cycles found: {len(analysis.tension_cycles)}
- Overall engagement: {analysis.overall_engagement_score:.0%}

**Suggestions for improvement:**
{chr(10).join(f'- {s}' for s in analysis.suggestions)}

**Instructions:**
1. Strengthen the chapter's engagement based on the suggestions above
2. Add or enhance a cliffhanger ending if appropriate
3. Ensure tension/release cycles flow naturally - these should be deliberate rises and falls in tension that serve the narrative, not artificial pacing
4. Maintain the chapter's core plot and character development
5. Make improvements feel organic, not forced

6. CRITICAL: {f'Maintain at least {current_word_count:,} words' if current_word_count > 0 else 'Maintain substantial chapter length'} - do not shorten the chapter.

Focus on making the chapter ending particularly compelling to draw readers forward.
"""
        return prompt
