# core/book_spec.py
from pydantic import BaseModel


class BookSpec(BaseModel):
    """
    Represents the specification for a novel.

    This Pydantic model defines the structure for storing and validating
    the book specification, including title, genre, setting, themes, tone,
    point of view, characters, and premise.
    """

    title: str
    """The title of the novel."""
    genre: str
    """The genre and subgenres of the novel (e.g., Dark Fantasy, Erotic Thriller)."""
    setting: str
    """Detailed description of the novel's setting(s), including location and time period."""
    themes: list[str] # changed to list[str] to remove need for import
    """List of major themes explored in the novel, particularly dark and erotic themes."""
    tone: str
    """The overall tone of the novel (e.g., gritty, suspenseful, sensual, melancholic)."""
    point_of_view: str
    """The narrative point of view (e.g., first-person, third-person limited, third-person omniscient)."""
    characters: list[str] # changed to list[str] to remove need for import
    """Detailed descriptions of 2-3 main characters, including motivations and flaws related to dark and erotic elements."""
    premise: str
    """A concise and intriguing premise that sets up the central conflict and hints at the dark and erotic nature of the story."""