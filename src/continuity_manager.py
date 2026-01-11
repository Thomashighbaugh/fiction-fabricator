# -*- coding: utf-8 -*-
"""
continuity_manager.py - Tracks continuity across chapters and validates references
"""
import re
import json
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum


class EntityType(str, Enum):
    """Types of entities to track for continuity."""
    CHARACTER = "character"
    PLACE = "place"
    OBJECT = "object"
    CONCEPT = "concept"


@dataclass
class Entity:
    """Represents a tracked entity (character, place, object, concept)."""
    name: str
    entity_type: EntityType
    first_chapter_id: str
    first_position: int  # Word position in chapter
    attributes: Dict[str, str] = field(default_factory=dict)
    aliases: List[str] = field(default_factory=list)


@dataclass
class WorldRule:
    """Represents a rule about the story world."""
    rule_name: str
    rule_text: str
    chapter_established: str
    violations: List[Dict] = field(default_factory=list)


@dataclass
class ContinuityIssue:
    """Represents a continuity problem."""
    issue_type: str
    severity: str  # 'warning', 'error', 'critical'
    chapter_id: str
    entity_name: str
    description: str
    suggestion: str


class ContinuityManager:
    """Manages continuity tracking across chapters."""

    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.world_rules: Dict[str, WorldRule] = {}
        self.chapter_context: Dict[str, Set[str]] = {}
        self.issues: List[ContinuityIssue] = []

    def analyze_chapter_for_continuity(self, chapter_id: str, content_text: str,
                                     chapter_summary: str = "") -> List[ContinuityIssue]:
        """
        Analyze a chapter for continuity issues.

        Args:
            chapter_id: Chapter identifier
            content_text: Prose content to analyze
            chapter_summary: Chapter summary for context

        Returns:
            List of continuity issues found
        """
        chapter_issues = []

        # Extract proper nouns and track first mentions
        proper_nouns = self._extract_proper_nouns(content_text)
        
        # Check for entities mentioned before introduction
        for noun in proper_nouns:
            entity_key = self._normalize_entity_name(noun)
            
            if entity_key in self.entities:
                # Entity exists - check for consistency
                entity = self.entities[entity_key]
                self._check_entity_consistency(entity, noun, content_text, chapter_issues)
            else:
                # New entity - record first mention
                position = content_text.lower().find(noun.lower())
                if position >= 0:
                    entity_type = self._classify_entity(noun, chapter_summary, content_text)
                    self.entities[entity_key] = Entity(
                        name=noun,
                        entity_type=entity_type,
                        first_chapter_id=chapter_id,
                        first_position=position,
                        attributes={},
                        aliases=[]
                    )
                    self.chapter_context.setdefault(chapter_id, set()).add(entity_key)

        # Check for references to entities that don't exist (if not first chapter)
        if chapter_id != "1":
            known_entities = set(self.entities.keys())
            for noun in proper_nouns:
                entity_key = self._normalize_entity_name(noun)
                # Check if this looks like an existing entity (case-insensitive, with aliases)
                if not self._is_known_entity(entity_key, noun):
                    # Might be an issue, but could just be a new entity
                    pass

        # Check world rule violations
        self._check_world_rule_compliance(chapter_id, content_text, chapter_issues)

        # Track issues
        self.issues.extend(chapter_issues)

        return chapter_issues

    def _extract_proper_nouns(self, text: str) -> List[str]:
        """
        Extract potential proper nouns from text.
        Uses simple heuristics + capitalization patterns.
        """
        # Pattern: capitalized words that aren't at start of sentence
        # and appear to be names/places
        proper_nouns = set()

        # Match capitalized words mid-sentence
        mid_sentence_caps = re.findall(r'(?:^|[.!?]\s+)([A-Z][a-zA-Z]+)', text)
        for match in mid_sentence_caps:
            word = match.group(1)
            # Filter out common words that get capitalized
            if word.lower() not in ['the', 'and', 'but', 'or', 'when', 'where', 'then', 'so', 'because']:
                if len(word) > 2:
                    proper_nouns.add(word)

        # Match quoted names (e.g., "John")
        quoted_names = re.findall(r'"([A-Z][a-zA-Z]+)"', text)
        proper_nouns.update(quoted_names)

        return list(proper_nouns)

    def _normalize_entity_name(self, name: str) -> str:
        """Normalize entity name for consistent tracking."""
        return name.lower().strip()

    def _classify_entity(self, name: str, summary: str, content: str) -> EntityType:
        """
        Classify an entity as character, place, object, or concept.
        """
        name_lower = name.lower()

        # Place indicators
        place_indicators = ['street', 'road', 'city', 'town', 'room', 'house', 'building',
                         'forest', 'mountain', 'river', 'sea', 'lake', 'castle',
                         'palace', 'temple', 'shop', 'store', 'restaurant', 'cafe']
        if any(ind in name_lower for ind in place_indicators):
            return EntityType.PLACE

        # Character indicators (verbs/actions associated with people)
        char_indicators = ['walked', 'said', 'shouted', 'ran', 'thought', 'felt', 'saw']
        text_lower = content.lower()
        if any(f'{name_lower} {ind}' in text_lower for ind in char_indicators):
            return EntityType.CHARACTER

        # Object/concept - default
        return EntityType.OBJECT

    def _is_known_entity(self, entity_key: str, original_name: str) -> bool:
        """Check if entity is known (including aliases)."""
        if entity_key in self.entities:
            return True
        
        # Check if it's an alias of a known entity
        for entity in self.entities.values():
            if original_name.lower() in [a.lower() for a in entity.aliases]:
                return True
        
        return False

    def _check_entity_consistency(self, entity: Entity, current_name: str,
                                 content_text: str, issues: List[ContinuityIssue]):
        """
        Check if entity is used consistently.
        """
        # Check for spelling variations that might be unintentional
        variations = self._find_spelling_variations(entity.name, content_text)
        
        if variations:
            issues.append(ContinuityIssue(
                issue_type="spelling_variation",
                severity="warning",
                chapter_id=entity.first_chapter_id,
                entity_name=entity.name,
                description=f"'{current_name}' appears to be a spelling variation of known entity '{entity.name}'",
                suggestion=f"Consider using consistent spelling: '{entity.name}'"
            ))

    def _find_spelling_variations(self, original_name: str, text: str) -> List[str]:
        """Find potential spelling variations of an entity name."""
        variations = []
        text_lower = text.lower()
        original_lower = original_name.lower()

        # Simple Levenshtein-like approximation
        for word in re.findall(r'\b[A-Z][a-z]+\b', text):
            word_lower = word.lower()
            if word_lower != original_lower and len(word_lower) == len(original_lower):
                # Same length, different - possible typo
                mismatches = sum(1 for a, b in zip(word_lower, original_lower) if a != b)
                if mismatches <= 1 and mismatches / len(original_lower) < 0.3:
                    variations.append(word)

        return variations

    def add_world_rule(self, rule_name: str, rule_text: str, chapter_id: str):
        """
        Add a world rule established in a chapter.

        Args:
            rule_name: Short identifier for the rule
            rule_text: Description of the rule
            chapter_id: Chapter where rule was established
        """
        self.world_rules[rule_name] = WorldRule(
            rule_name=rule_name,
            rule_text=rule_text,
            chapter_established=chapter_id,
            violations=[]
        )

    def _check_world_rule_compliance(self, chapter_id: str, content_text: str,
                                    issues: List[ContinuityIssue]):
        """Check if chapter violates any established world rules."""
        if not self.world_rules:
            return

        content_lower = content_text.lower()

        for rule_name, rule in self.world_rules.items():
            # Simple heuristic: if rule contains keywords and content contradicts
            # This is simplified - real implementation would be more sophisticated
            rule_text_lower = rule.rule_text.lower()
            
            # Check for potential contradictions (very basic)
            if "cannot" in rule_text_lower and "can" in content_lower:
                # Might be a contradiction
                pass  # Would need NLP to properly detect

    def get_entity_report(self) -> str:
        """Generate a report of all tracked entities."""
        if not self.entities:
            return "No entities tracked yet."

        lines = ["Continuity Report - Tracked Entities:\n"]
        
        # Group by type
        by_type: Dict[EntityType, List[Entity]] = {
            EntityType.CHARACTER: [],
            EntityType.PLACE: [],
            EntityType.OBJECT: [],
            EntityType.CONCEPT: []
        }

        for entity in self.entities.values():
            by_type[entity.entity_type].append(entity)

        for entity_type, entities in by_type.items():
            if entities:
                lines.append(f"\n{entity_type.value.title()}s:")
                for entity in entities:
                    lines.append(
                        f"  - {entity.name} (first mentioned: Chapter {entity.first_chapter_id})"
                    )
                    if entity.attributes:
                        lines.append(f"    Attributes: {json.dumps(entity.attributes, indent=6)}")
                    if entity.aliases:
                        lines.append(f"    Aliases: {', '.join(entity.aliases)}")

        return "\n".join(lines)

    def get_issues_report(self) -> str:
        """Generate a report of continuity issues."""
        if not self.issues:
            return "No continuity issues found."

        lines = ["Continuity Issues Report:\n"]
        
        for issue in self.issues:
            lines.append(
                f"[{issue.severity.upper()}] Chapter {issue.chapter_id}: {issue.description}"
            )
            lines.append(f"  Entity: {issue.entity_name}")
            lines.append(f"  Suggestion: {issue.suggestion}\n")

        return "\n".join(lines)

    def save_to_file(self, filepath: str):
        """Save continuity data to JSON file."""
        data = {
            'entities': {
                name: {
                    'type': entity.entity_type,
                    'first_chapter': entity.first_chapter_id,
                    'first_position': entity.first_position,
                    'attributes': entity.attributes,
                    'aliases': entity.aliases
                }
                for name, entity in self.entities.items()
            },
            'world_rules': {
                name: {
                    'rule_text': rule.rule_text,
                    'chapter_established': rule.chapter_established,
                    'violations': rule.violations
                }
                for name, rule in self.world_rules.items()
            },
            'issues': [
                {
                    'type': issue.issue_type,
                    'severity': issue.severity,
                    'chapter_id': issue.chapter_id,
                    'entity_name': issue.entity_name,
                    'description': issue.description,
                    'suggestion': issue.suggestion
                }
                for issue in self.issues
            ]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def load_from_file(self, filepath: str):
        """Load continuity data from JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Load entities
            for name, entity_data in data.get('entities', {}).items():
                self.entities[name] = Entity(
                    name=name,
                    entity_type=EntityType(entity_data['type']),
                    first_chapter_id=entity_data['first_chapter'],
                    first_position=entity_data['first_position'],
                    attributes=entity_data.get('attributes', {}),
                    aliases=entity_data.get('aliases', [])
                )

            # Load world rules
            for name, rule_data in data.get('world_rules', {}).items():
                self.world_rules[name] = WorldRule(
                    rule_name=name,
                    rule_text=rule_data['rule_text'],
                    chapter_established=rule_data['chapter_established'],
                    violations=rule_data.get('violations', [])
                )

            # Load issues
            self.issues = [
                ContinuityIssue(**issue_data)
                for issue_data in data.get('issues', [])
            ]

        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Failed to load continuity data: {e}")
