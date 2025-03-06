# core/content_generation/content_generation_utils.py
from pydantic import BaseModel
from typing import List


class PlotOutline(BaseModel):
    """
    Represents a three-act plot outline for a novel, with acts and blocks as lists of plot points,
    following the 27 chapter methodology structure.
    """

    act_one_block_one: List[str] = []
    act_one_block_two: List[str] = []
    act_one_block_three: List[str] = []
    """Act One: Setup - Divided into three blocks representing different phases of setup."""

    act_two_block_one: List[str] = []
    act_two_block_two: List[str] = []
    act_two_block_three: List[str] = []
    """Act Two: Confrontation - Divided into three blocks representing different phases of confrontation."""

    act_three_block_one: List[str] = []
    act_three_block_two: List[str] = []
    act_three_block_three: List[str] = []
    """Act Three: Resolution - Divided into three blocks representing different phases of resolution."""


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


class ChapterOutlineMethod(BaseModel):
    """
    Represents an outline for a single chapter in the novel,
    specifically for the 27 chapter methodology.

    This Pydantic model defines the structure for a chapter outline,
    including the chapter number, its role in the 27 chapter methodology
    and a summary of the chapter's events.
    """

    chapter_number: int
    """The chapter number (e.g., 1 to 27)."""
    role: str
    """The role of this chapter in the 27 chapter methodology (e.g., "Introduction", "Inciting Incident", etc.)."""
    summary: str


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