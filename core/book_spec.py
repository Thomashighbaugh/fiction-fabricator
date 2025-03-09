# core/book_spec.py
from typing import List, Dict, Union, Any
from pydantic import BaseModel, field_validator


class BookSpec(BaseModel):
    """
    Represents the specification for a novel.
    """

    title: str
    genre: str
    setting: Union[Dict[str, str], str]
    themes: List[str]
    tone: str
    point_of_view: str
    characters: List[Union[str, Dict[str, str]]]  # Changed to List[Dict[str, str]]
    premise: str

    @field_validator("setting")
    @classmethod
    def validate_setting(cls, value):
        if isinstance(value, str):
            return value
        elif isinstance(value, dict):
            return value
        else:
            raise ValueError("Setting must be either a string or a dictionary.")

    def model_dump_toml(self) -> Dict:
        """Dumps the model to a TOML-compatible dictionary."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict) -> "BookSpec":
        """Creates a BookSpec instance from a dictionary."""
        return cls(**data)