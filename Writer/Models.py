# File: Writer/Models.py
# Purpose: Defines Pydantic models for structured LLM outputs, used for reliable JSON handling.

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# For ChapterDetector.py - detecting total chapters
class TotalChapters(BaseModel):
    """Represents the total number of chapters detected in a story outline."""

    TotalChapters: int = Field(
        ...,
        description="The total number of distinct chapters detected in the outline.",
        ge=0,
    )


# For LLMEditor.py - evaluating outline/chapter completeness
class IsComplete(BaseModel):
    """Represents the boolean completeness status of an outline or chapter."""

    IsComplete: bool = Field(
        ...,
        description="Boolean indicating if the item (outline/chapter) meets quality and completeness standards.",
    )


# For StoryInfo.py - extracting final story metadata
class StoryMetadata(BaseModel):
    """Represents the overall metadata for a generated story."""

    Title: str = Field(
        ...,
        description="A compelling and concise title for the story, ideally 3-8 words.",
    )
    Summary: str = Field(
        ...,
        description="A 1-2 paragraph summary covering the main plot from beginning to end, including key conflicts and resolution.",
    )
    Tags: str = Field(
        ...,
        description="A comma-separated list of 5-10 relevant keywords or tags that categorize the story (e.g., sci-fi, adventure, romance, betrayal).",
    )
    OverallRating: int = Field(
        ...,
        ge=0,
        le=100,
        description="Your subjective overall quality score for the story based on its coherence, engagement, and creativity, from 0 to 100.",
    )


# For SceneOutliner.py - detailed scene blueprints
class SceneOutline(BaseModel):
    """Represents a detailed blueprint for a single scene within a chapter."""

    scene_number_in_chapter: int = Field(
        ..., description="Sequential number of the scene within the chapter.", ge=1
    )
    scene_title: str = Field(..., description="A brief, evocative title for the scene.")
    setting_description: str = Field(
        ...,
        description="Detailed description of the location, time of day, and prevailing atmosphere.",
    )
    characters_present: List[str] = Field(
        ..., description="Names of characters actively participating in this scene."
    )
    character_goals_moods: str = Field(
        ...,
        description="Brief description of what each key character present wants to achieve or their emotional state at the start of the scene.",
    )
    key_events_actions: List[str] = Field(
        ...,
        description="Bullet points describing the critical plot developments, actions, or discoveries that must occur in this scene.",
    )
    dialogue_points: List[str] = Field(
        ...,
        description="Key topics of conversation or specific impactful lines of dialogue.",
    )
    pacing_note: str = Field(
        ...,
        description="Suggested pacing for the scene (e.g., Fast-paced action sequence, Slow, tense dialogue exchange).",
    )
    tone: str = Field(
        ...,
        description="The dominant emotional tone the scene should convey (e.g., Suspenseful, Romantic, Tragic).",
    )
    purpose_in_chapter: str = Field(
        ...,
        description="How this scene specifically contributes to the chapter's overall objectives.",
    )
    transition_out_hook: str = Field(
        ...,
        description="How the scene should end to effectively lead into the next scene or provide a minor cliffhanger.",
    )


# Helper model to wrap a list of SceneOutline for structured LLM response
class SceneOutlinesList(BaseModel):
    """A wrapper model to return a list of SceneOutline objects."""

    scenes: List[SceneOutline] = Field(
        ..., description="A list of detailed scene outlines for a chapter."
    )


# For Evaluate.py - comparison results
class ComparisonResult(BaseModel):
    """Represents the result of a comparison for a specific criterion."""

    Winner: str = Field(..., description="Indicates the winner (A, B, or Tie).")
    Explanation: str = Field(
        ..., description="Brief explanation for the comparison result."
    )


class OutlineComparison(BaseModel):
    """Represents a comparative evaluation of two story outlines."""

    OverallThoughts: str = Field(
        ...,
        description="General comparative assessment and main reasons for preference.",
    )
    PlotComparison: ComparisonResult
    ChapterStructureComparison: ComparisonResult = Field(
        ..., alias="ChapterStructureComparison"
    )
    PacingComparison: ComparisonResult
    CharacterArcPotentialComparison: ComparisonResult = Field(
        ..., alias="CharacterArcPotentialComparison"
    )
    OriginalityEngagementComparison: ComparisonResult = Field(
        ..., alias="OriginalityEngagementComparison"
    )
    OverallWinner: str = Field(
        ..., description="Overall winner between Outline A, B, or Tie."
    )


class ChapterComparison(BaseModel):
    """Represents a comparative evaluation of two story chapters."""

    OverallThoughts: str = Field(
        ...,
        description="General comparative assessment and main reasons for preference.",
    )
    ProseQualityComparison: ComparisonResult = Field(
        ..., alias="ProseQualityComparison"
    )
    PacingFlowComparison: ComparisonResult = Field(..., alias="PacingFlowComparison")
    DialogueQualityComparison: ComparisonResult = Field(
        ..., alias="DialogueQualityComparison"
    )
    CharacterPortrayalComparison: ComparisonResult = Field(
        ..., alias="CharacterPortrayalComparison"
    )
    PlotAdvancementComparison: ComparisonResult = Field(
        ..., alias="PlotAdvancementComparison"
    )
    EngagementImpactComparison: ComparisonResult = Field(
        ..., alias="EngagementImpactComparison"
    )
    OverallWinner: str = Field(
        ..., description="Overall winner between Chapter A, B, or Tie."
    )