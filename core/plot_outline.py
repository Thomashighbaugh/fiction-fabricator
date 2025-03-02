# core/plot_outline.py
from pydantic import BaseModel


class PlotOutline(BaseModel):
    """
    Represents a three-act plot outline for a novel.

    This Pydantic model defines the structure for storing the three acts
    of a plot outline: Act One (Setup), Act Two (Confrontation), and
    Act Three (Resolution). Each act is represented as a string containing
    a summary of the plot points within that act.
    """

    act_one: str
    """Summary of Act One: Setup - Introduction of characters, setting, and initial conflict."""
    act_two: str
    """Summary of Act Two: Confrontation - Development of conflict, rising stakes, and obstacles."""
    act_three: str
    """Summary of Act Three: Resolution - Climax, resolution of conflict, and thematic closure."""


class ChapterOutline(BaseModel):
    """
    Represents an outline for a single chapter in the novel.

    This Pydantic model defines the structure for a chapter outline,
    including the chapter number and a summary of the chapter's events.
    """

    chapter_number: int
    """The chapter number (e.g., 1, 2, 3...)."""
    summary: str
    """A summary of the key events and developments within this chapter."""


class SceneOutline(BaseModel):
    """
    Represents an outline for a single scene within a chapter.

    This Pydantic model defines the structure for a scene outline,
    including the scene number and a summary of the scene's events,
    setting, and characters involved.
    """

    scene_number: int
    """The scene number within the chapter (e.g., 1, 2, 3...)."""
    summary: str
    """A summary of the key events, setting, and characters in this scene."""
