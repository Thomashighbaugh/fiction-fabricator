# core/content_generation/content_generation_utils.py
from pydantic import BaseModel
from typing import List, Dict
import tomli_w
import tomli


class PlotOutline(BaseModel):
    """
    Represents a three-act plot outline for a novel.
    """

    act_one_block_one: List[str] = []
    act_one_block_two: List[str] = []
    act_one_block_three: List[str] = []
    act_two_block_one: List[str] = []
    act_two_block_two: List[str] = []
    act_two_block_three: List[str] = []
    act_three_block_one: List[str] = []
    act_three_block_two: List[str] = []
    act_three_block_three: List[str] = []

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


class ChapterOutlineMethod(BaseModel):
    """
    Represents an outline for a single chapter (27-chapter method).
    """

    chapter_number: int
    role: str
    summary: str

    def model_dump_toml(self) -> Dict:
        """Dumps the model to a TOML-compatible dictionary."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict) -> "ChapterOutlineMethod":
        """Creates a ChapterOutlineMethod instance from a dictionary."""
        return cls(**data)


class SceneOutline(BaseModel):
    """
    Represents an outline for a single scene.
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
