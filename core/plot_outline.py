# core/plot_outline.py
from typing import List, Dict

from pydantic import BaseModel


class PlotOutline(BaseModel):
    """
    Represents a three-act plot outline for a novel.
    """

    act_one: List[str] = []
    act_two: List[str] = []
    act_three: List[str] = []

    def model_dump_toml(self) -> Dict:
        """Dumps the model to a TOML-compatible dictionary."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict) -> "PlotOutline":
        """Creates a PlotOutline instance from a dictionary."""
        return cls(**data)


class ChapterOutline(BaseModel):
    """
    Represents an outline for a single chapter.
    """

    chapter_number: int
    summary: str

    def model_dump_toml(self) -> Dict:
        """Dumps the model to a TOML-compatible dictionary."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict) -> "ChapterOutline":
        """Creates a ChapterOutline instance from a dictionary."""
        return cls(**data)

class SceneOutline(BaseModel):
    """
    Represents an outline for a single scene within a chapter.
    """

    scene_number: int
    summary: str

    def model_dump_toml(self) -> Dict:
        """Dumps the model to a TOML-compatible dictionary."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict) -> "SceneOutline":
        """Creates a SceneOutline instance from a dictionary."""
        return cls(**data)