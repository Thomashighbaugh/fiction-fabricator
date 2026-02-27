"""
slop_detection.py - AI slop detection and removal system

This module provides comprehensive detection and mitigation of AI-generated "slop" - 
generic, clichéd, or low-quality content patterns commonly produced by LLMs.
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum

from src import config


class SlopCategory(Enum):
    """Categories of AI slop patterns."""
    GENERIC_PHRASES = "generic_phrases"
    CLICHES = "cliches"  
    OVERUSED_WORDS = "overused_words"
    AI_PATTERNS = "ai_patterns"
    WEAK_PROSE = "weak_prose"
    REDUNDANCY = "redundancy"
    FILLER_CONTENT = "filler_content"


@dataclass
class SlopIssue:
    """Represents a detected slop issue."""
    category: SlopCategory
    pattern: str
    matches: List[Tuple[int, str]]  # (position, matched_text)
    severity: float  # 0.0 (minor) to 1.0 (severe)
    suggestion: str
    context: str = ""


@dataclass
class SlopAnalysis:
    """Results of slop detection analysis."""
    issues: List[SlopIssue]
    overall_score: float  # 0.0 (heavy slop) to 10.0 (clean prose)
    cleaned_text: Optional[str] = None
    removals_count: int = 0
    replacements_count: int = 0
    
    @property
    def has_issues(self) -> bool:
        """Check if any slop issues were detected."""
        return len(self.issues) > 0
    
    @property 
    def severity_score(self) -> float:
        """Calculate average severity of all issues."""
        if not self.issues:
            return 0.0
        return sum(issue.severity for issue in self.issues) / len(self.issues)


class SlopDetector:
    """Main slop detection engine."""
    
    def __init__(self, sensitivity: str = "medium"):
        """
        Initialize slop detector.
        
        Args:
            sensitivity: Detection sensitivity - "low", "medium", "high", "strict"
        """
        self.sensitivity = sensitivity
        self.sensitivity_threshold = self._get_sensitivity_threshold(sensitivity)
        
        # Load slop pattern databases
        self._generic_phrases = self._load_generic_phrases()
        self._cliches = self._load_cliches()
        self._overused_words = self._load_overused_words()
        self._ai_patterns = self._load_ai_patterns()
        self._weak_prose_patterns = self._load_weak_prose_patterns()
        self._redundancy_patterns = self._load_redundancy_patterns()
        self._filler_patterns = self._load_filler_patterns()
    
    def _get_sensitivity_threshold(self, sensitivity: str) -> float:
        """Get minimum severity threshold for reporting issues."""
        thresholds = {
            "low": 0.8,      # Only report severe slop
            "medium": 0.5,   # Report moderate to severe slop  
            "high": 0.3,     # Report mild to severe slop
            "strict": 0.1    # Report all potential slop
        }
        return thresholds.get(sensitivity, 0.5)
    
    def analyze_text(self, text: str, auto_clean: bool = False) -> SlopAnalysis:
        """
        Analyze text for slop patterns.
        
        Args:
            text: Text to analyze
            auto_clean: Whether to automatically clean detected slop
            
        Returns:
            SlopAnalysis with detected issues and metrics
        """
        if not text or not text.strip():
            return SlopAnalysis(issues=[], overall_score=10.0)
        
        issues = []
        
        # Run all detection methods
        issues.extend(self._detect_generic_phrases(text))
        issues.extend(self._detect_cliches(text))
        issues.extend(self._detect_overused_words(text))
        issues.extend(self._detect_ai_patterns(text))
        issues.extend(self._detect_weak_prose(text))
        issues.extend(self._detect_redundancy(text))
        issues.extend(self._detect_filler_content(text))
        
        # Filter by sensitivity threshold
        filtered_issues = [
            issue for issue in issues 
            if issue.severity >= self.sensitivity_threshold
        ]
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(text, filtered_issues)
        
        # Auto-clean if requested
        cleaned_text = None
        removals_count = 0
        replacements_count = 0
        
        if auto_clean and filtered_issues:
            cleaned_text, removals_count, replacements_count = self._clean_text(text, filtered_issues)
        
        return SlopAnalysis(
            issues=filtered_issues,
            overall_score=overall_score,
            cleaned_text=cleaned_text,
            removals_count=removals_count,
            replacements_count=replacements_count
        )
    
    def _detect_generic_phrases(self, text: str) -> List[SlopIssue]:
        """Detect generic, overused phrases."""
        issues = []
        
        for pattern, severity, suggestion in self._generic_phrases:
            matches = []
            for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
                matches.append((match.start(), match.group()))
            
            if matches:
                issues.append(SlopIssue(
                    category=SlopCategory.GENERIC_PHRASES,
                    pattern=pattern,
                    matches=matches,
                    severity=severity,
                    suggestion=suggestion
                ))
        
        return issues
    
    def _detect_cliches(self, text: str) -> List[SlopIssue]:
        """Detect clichéd expressions."""
        issues = []
        
        for pattern, severity, suggestion in self._cliches:
            matches = []
            for match in re.finditer(pattern, text, re.IGNORECASE):
                matches.append((match.start(), match.group()))
            
            if matches:
                issues.append(SlopIssue(
                    category=SlopCategory.CLICHES,
                    pattern=pattern,
                    matches=matches,
                    severity=severity,
                    suggestion=suggestion
                ))
        
        return issues
    
    def _detect_overused_words(self, text: str) -> List[SlopIssue]:
        """Detect overused words and suggest alternatives."""
        issues = []
        word_counts = {}
        
        # Count word frequency (excluding common words)
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        for word in words:
            if len(word) > 3:  # Skip very short words
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Check for overused words
        text_length = len(words)
        for word, count in word_counts.items():
            frequency = count / text_length
            
            # Flag words used too frequently
            if count > 5 and frequency > 0.02:  # More than 2% of all words
                if word in self._overused_words:
                    matches = []
                    for match in re.finditer(rf'\b{re.escape(word)}\b', text, re.IGNORECASE):
                        matches.append((match.start(), match.group()))
                    
                    severity = min(0.9, frequency * 10)  # Scale severity with frequency
                    suggestion = f"Used {count} times. Consider alternatives: {', '.join(self._overused_words[word])}"
                    
                    issues.append(SlopIssue(
                        category=SlopCategory.OVERUSED_WORDS,
                        pattern=word,
                        matches=matches,
                        severity=severity,
                        suggestion=suggestion
                    ))
        
        return issues
    
    def _detect_ai_patterns(self, text: str) -> List[SlopIssue]:
        """Detect patterns characteristic of AI-generated text."""
        issues = []
        
        for pattern, severity, suggestion in self._ai_patterns:
            matches = []
            for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
                matches.append((match.start(), match.group()))
            
            if matches:
                issues.append(SlopIssue(
                    category=SlopCategory.AI_PATTERNS,
                    pattern=pattern,
                    matches=matches,
                    severity=severity,
                    suggestion=suggestion
                ))
        
        return issues
    
    def _detect_weak_prose(self, text: str) -> List[SlopIssue]:
        """Detect weak prose patterns."""
        issues = []
        
        for pattern, severity, suggestion in self._weak_prose_patterns:
            matches = []
            for match in re.finditer(pattern, text, re.IGNORECASE):
                matches.append((match.start(), match.group()))
            
            if matches:
                issues.append(SlopIssue(
                    category=SlopCategory.WEAK_PROSE,
                    pattern=pattern,
                    matches=matches,
                    severity=severity,
                    suggestion=suggestion
                ))
        
        return issues
    
    def _detect_redundancy(self, text: str) -> List[SlopIssue]:
        """Detect redundant expressions."""
        issues = []
        
        for pattern, severity, suggestion in self._redundancy_patterns:
            matches = []
            for match in re.finditer(pattern, text, re.IGNORECASE):
                matches.append((match.start(), match.group()))
            
            if matches:
                issues.append(SlopIssue(
                    category=SlopCategory.REDUNDANCY,
                    pattern=pattern,
                    matches=matches,
                    severity=severity,
                    suggestion=suggestion
                ))
        
        return issues
    
    def _detect_filler_content(self, text: str) -> List[SlopIssue]:
        """Detect filler content and unnecessary elaboration."""
        issues = []
        
        for pattern, severity, suggestion in self._filler_patterns:
            matches = []
            for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
                matches.append((match.start(), match.group()))
            
            if matches:
                issues.append(SlopIssue(
                    category=SlopCategory.FILLER_CONTENT,
                    pattern=pattern,
                    matches=matches,
                    severity=severity,
                    suggestion=suggestion
                ))
        
        return issues
    
    def _calculate_overall_score(self, text: str, issues: List[SlopIssue]) -> float:
        """Calculate overall slop score (0-10, higher is better)."""
        if not issues:
            return 10.0
        
        text_length = len(text.split())
        if text_length == 0:
            return 0.0
        
        # Calculate penalty based on issue density and severity
        total_penalty = 0.0
        for issue in issues:
            # Penalty scales with severity and frequency
            issue_penalty = issue.severity * len(issue.matches)
            # Normalize by text length
            total_penalty += issue_penalty / max(1, text_length / 100)
        
        # Convert to 0-10 scale
        score = max(0.0, 10.0 - total_penalty)
        return round(score, 1)
    
    def _clean_text(self, text: str, issues: List[SlopIssue]) -> Tuple[str, int, int]:
        """
        Automatically clean text by removing/replacing slop patterns.
        
        Returns:
            Tuple of (cleaned_text, removals_count, replacements_count)
        """
        cleaned = text
        removals = 0
        replacements = 0
        
        # Sort issues by position (reverse order to preserve positions during replacement)
        all_matches = []
        for issue in issues:
            for pos, match_text in issue.matches:
                all_matches.append((pos, match_text, issue))
        
        all_matches.sort(key=lambda x: x[0], reverse=True)
        
        # Apply fixes
        for pos, match_text, issue in all_matches:
            if issue.category in [SlopCategory.FILLER_CONTENT, SlopCategory.REDUNDANCY]:
                # Remove filler content
                cleaned = cleaned[:pos] + cleaned[pos + len(match_text):]
                removals += 1
            elif issue.suggestion and "Consider:" in issue.suggestion:
                # Replace with first suggested alternative
                alternatives = issue.suggestion.split("Consider:")[1].strip().split(",")
                if alternatives:
                    replacement = alternatives[0].strip()
                    cleaned = cleaned[:pos] + replacement + cleaned[pos + len(match_text):]
                    replacements += 1
        
        return cleaned, removals, replacements
    
    def generate_report(self, analysis: SlopAnalysis) -> str:
        """Generate human-readable slop detection report."""
        if not analysis.has_issues:
            return f"✓ No slop detected! Overall score: {analysis.overall_score}/10"
        
        report = [f"AI Slop Detection Report (Score: {analysis.overall_score}/10)"]
        report.append("=" * 50)
        
        # Group issues by category
        issues_by_category = {}
        for issue in analysis.issues:
            if issue.category not in issues_by_category:
                issues_by_category[issue.category] = []
            issues_by_category[issue.category].append(issue)
        
        for category, category_issues in issues_by_category.items():
            report.append(f"\n{category.value.replace('_', ' ').title()}:")
            for issue in category_issues:
                severity_indicator = "🔴" if issue.severity >= 0.7 else "🟡" if issue.severity >= 0.4 else "🟢"
                report.append(f"  {severity_indicator} {len(issue.matches)} occurrence(s) of '{issue.pattern}'")
                report.append(f"     {issue.suggestion}")
        
        if analysis.cleaned_text:
            report.append(f"\nAuto-cleaning results:")
            report.append(f"  - Removed {analysis.removals_count} filler phrases")
            report.append(f"  - Replaced {analysis.replacements_count} weak expressions")
        
        return "\n".join(report)
    
    # Pattern databases - these would ideally be loaded from external files
    
    def _load_generic_phrases(self) -> List[Tuple[str, float, str]]:
        """Load generic phrase patterns with severity and suggestions."""
        return [
            # Opening cliches
            (r'\bit was a dark and stormy night\b', 0.9, "Consider a more original opening"),
            (r'\bonce upon a time\b', 0.7, "Consider a more engaging opening"),
            (r'\bin a world where\b', 0.6, "Consider showing rather than telling"),
            (r'\blong ago\b', 0.5, "Consider a more specific time reference"),
            
            # Transition cliches
            (r'\bmeanwhile, back at\b', 0.7, "Consider a smoother transition"),
            (r'\bsuddenly\b', 0.6, "Consider building tension more naturally"),
            (r'\bwithout warning\b', 0.5, "Consider foreshadowing the event"),
            
            # Generic descriptions
            (r'\bbeyond his wildest dreams\b', 0.8, "Consider more specific description"),
            (r'\blike nothing he had ever seen\b', 0.7, "Consider concrete comparisons"),
            (r'\btime seemed to stand still\b', 0.6, "Consider more original time description"),
            
            # AI-generated hedging
            (r'\bit\'s worth noting that\b', 0.5, "Remove unnecessary hedging"),
            (r'\bit\'s important to understand\b', 0.5, "Show importance through action"),
            (r'\bone might argue\b', 0.4, "Consider direct statement"),
        ]
    
    def _load_cliches(self) -> List[Tuple[str, float, str]]:
        """Load clichéd expressions."""
        return [
            (r'\bbite the bullet\b', 0.6, "Consider: face the challenge, confront the problem"),
            (r'\bbreak the ice\b', 0.5, "Consider: start the conversation, ease the tension"),
            (r'\bcatch-22\b', 0.5, "Consider: impossible situation, no-win scenario"),
            (r'\bevery cloud has a silver lining\b', 0.7, "Consider more original optimism"),
            (r'\bfit as a fiddle\b', 0.6, "Consider: healthy, robust, energetic"),
            (r'\bgood as gold\b', 0.5, "Consider: reliable, trustworthy, valuable"),
            (r'\bheart of gold\b', 0.6, "Consider: kind, generous, caring"),
            (r'\bkill two birds with one stone\b', 0.5, "Consider: solve both problems, accomplish multiple goals"),
            (r'\bpiece of cake\b', 0.5, "Consider: easy, simple, effortless"),
            (r'\braining cats and dogs\b', 0.7, "Consider: pouring, torrential, heavy downpour"),
            (r'\btime heals all wounds\b', 0.6, "Consider showing healing process"),
            (r'\bwhen pigs fly\b', 0.6, "Consider: never, impossible, not happening"),
        ]
    
    def _load_overused_words(self) -> Dict[str, List[str]]:
        """Load overused words with suggested alternatives."""
        return {
            "very": ["extremely", "remarkably", "exceptionally", "tremendously"],
            "really": ["truly", "genuinely", "absolutely", "thoroughly"],
            "quite": ["rather", "somewhat", "fairly", "moderately"],
            "pretty": ["fairly", "reasonably", "somewhat", "rather"],
            "thing": ["object", "item", "matter", "element", "aspect"],
            "stuff": ["items", "belongings", "materials", "matters"],
            "good": ["excellent", "superb", "outstanding", "remarkable"],
            "bad": ["terrible", "awful", "dreadful", "atrocious"],
            "big": ["enormous", "massive", "gigantic", "immense"],
            "small": ["tiny", "minute", "minuscule", "petite"],
            "walk": ["stroll", "saunter", "stride", "march", "pace"],
            "look": ["gaze", "peer", "observe", "examine", "study"],
            "said": ["whispered", "declared", "announced", "murmured", "stated"],
        }
    
    def _load_ai_patterns(self) -> List[Tuple[str, float, str]]:
        """Load AI-specific pattern indicators."""
        return [
            # List-like structures in prose
            (r'\bfirst,.*?second,.*?third\b', 0.7, "Avoid numbered lists in narrative prose"),
            (r'\bon one hand.*?on the other hand\b', 0.6, "Consider more natural perspective shifts"),
            
            # Excessive qualification
            (r'\bperhaps.*?maybe.*?possibly\b', 0.5, "Choose one qualifier or be more definitive"),
            (r'\bmight.*?could.*?would\b', 0.4, "Use concrete language where possible"),
            
            # Meta-commentary
            (r'\bit\'s clear that\b', 0.6, "Show rather than tell clarity"),
            (r'\bobviously\b', 0.5, "Remove obvious statements"),
            (r'\bneedless to say\b', 0.7, "If needless to say, don't say it"),
            
            # Parenthetical asides (in fiction)
            (r'\([^)]*\)', 0.4, "Consider integrating asides into narrative flow"),
        ]
    
    def _load_weak_prose_patterns(self) -> List[Tuple[str, float, str]]:
        """Load weak prose pattern indicators."""
        return [
            # Weak verb constructions
            (r'\bwas/were \w+ing\b', 0.5, "Consider active voice: 'She ran' vs 'She was running'"),
            (r'\bthere was/were\b', 0.4, "Consider stronger sentence openings"),
            (r'\bit is/was\b', 0.3, "Consider more direct constructions"),
            
            # Filter words
            (r'\bseemed to\b', 0.4, "Consider direct action: 'She frowned' vs 'She seemed to frown'"),
            (r'\bappeared to\b', 0.4, "Consider showing directly"),
            (r'\bkind of\b', 0.5, "Consider more precise description"),
            (r'\bsort of\b', 0.5, "Consider more precise description"),
            
            # Weak sentence openings
            (r'^\s*And then\b', 0.6, "Consider stronger transitions"),
            (r'^\s*So then\b', 0.6, "Consider natural flow without explicit connectors"),
            (r'^\s*But then\b', 0.5, "Consider varied sentence structures"),
        ]
    
    def _load_redundancy_patterns(self) -> List[Tuple[str, float, str]]:
        """Load redundant expression patterns."""
        return [
            (r'\bfree gift\b', 0.7, "Remove 'free' (gifts are free by definition)"),
            (r'\bunexpected surprise\b', 0.7, "Remove 'unexpected' (surprises are unexpected)"),
            (r'\badvanced warning\b', 0.6, "Use 'warning' or 'advance notice'"),
            (r'\bfuture plans\b', 0.6, "Use 'plans' (plans are for the future)"),
            (r'\bpast history\b', 0.6, "Use 'history' (history is always past)"),
            (r'\btrue fact\b', 0.6, "Use 'fact' (facts are true)"),
            (r'\bclose proximity\b', 0.5, "Use 'proximity' or 'close'"),
            (r'\bend result\b', 0.4, "Use 'result' or 'outcome'"),
            (r'\bexact same\b', 0.4, "Use 'same' or 'identical'"),
            (r'\brepeat again\b', 0.6, "Use 'repeat'"),
        ]
    
    def _load_filler_patterns(self) -> List[Tuple[str, float, str]]:
        """Load filler content patterns."""
        return [
            # Empty expressions
            (r'\bas you know\b', 0.5, "Remove if truly known to reader"),
            (r'\bas I mentioned before\b', 0.6, "Remove unnecessary references"),
            (r'\bto tell the truth\b', 0.5, "Narration should always be truthful"),
            (r'\bto be honest\b', 0.5, "Implies dishonesty elsewhere"),
            (r'\bbasically\b', 0.4, "Usually unnecessary filler"),
            
            # Throat clearing
            (r'\bwell, actually\b', 0.5, "Consider direct statement"),
            (r'\bthe fact of the matter is\b', 0.7, "State the matter directly"),
            (r'\bwhat I mean to say is\b', 0.6, "Say what you mean directly"),
            
            # Excessive elaboration
            (r'\bso to speak\b', 0.4, "Often unnecessary qualification"),
            (r'\bif you will\b', 0.4, "Usually unnecessary"),
            (r'\bfor all intents and purposes\b', 0.5, "Consider: essentially, effectively"),
        ]


class SlopDetectionAgent:
    """Enhanced quality assurance agent with slop detection capabilities."""
    
    def __init__(self, sensitivity: str = "medium"):
        """
        Initialize slop detection agent.
        
        Args:
            sensitivity: Detection sensitivity level
        """
        self.detector = SlopDetector(sensitivity)
    
    def validate_content_quality(self, content: str, auto_clean: bool = False) -> SlopAnalysis:
        """
        Validate content for slop patterns.
        
        Args:
            content: Text content to analyze
            auto_clean: Whether to automatically clean detected issues
            
        Returns:
            SlopAnalysis with detected issues and quality metrics
        """
        return self.detector.analyze_text(content, auto_clean)
    
    def generate_quality_report(self, analysis: SlopAnalysis) -> str:
        """Generate a comprehensive quality report including slop analysis."""
        return self.detector.generate_report(analysis)