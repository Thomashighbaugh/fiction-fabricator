# core/book_spec.py
# fiction_fabricator/src/core/book_spec.py
from typing import List, Dict, Optional # Import Dict, Optional

from pydantic import BaseModel, field_validator
import json


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
    setting: Dict[str, str] # Setting is now a dictionary
    """Detailed description of the novel's setting(s), as a dictionary with keys like 'location' and 'time_period'."""


    themes: List[str]
    """List of major themes explored in the novel, particularly dark and erotic themes."""
    tone: str
    """The overall tone of the novel (e.g., gritty, suspenseful, sensual, melancholic)."""
    point_of_view: str
    """The narrative point of view (e.g., first-person, third-person limited, third-person omniscient)."""
    characters: List[str]
    """Detailed descriptions of 2-3 main characters, including motivations and flaws related to dark and erotic elements."""
    premise: str
    """A concise and intriguing premise that sets up the central conflict and hints at the dark and erotic nature of the story."""