# utils/config.py
import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


class Config(BaseSettings):
    """
    Configuration manager for the Fiction Fabricator application.
    """

    project_directory: str = "data"
    log_level: str = "INFO"
    ollama_model_name: str = "mistral"  # Default to Mistral as a common Ollama model
    ollama_base_url: str = (
        "http://localhost:11434"  # This is only used by the old client
    )
    openai_base_url: str = "http://localhost:11434/v1"

    @field_validator("log_level")
    @classmethod
    def log_level_must_be_valid(cls, v: str) -> str:
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(
                f"Invalid log level: {v}.  Must be one of: {allowed_levels}"
            )
        return v.upper()

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def get_project_directory(self) -> str:
        return self.project_directory

    def get_log_level(self) -> str:
        return self.log_level

    def get_ollama_model_name(self) -> str:
        return self.ollama_model_name
    
    def get_openai_base_url(self) -> str:
        return self.openai_base_url

    def get_ollama_base_url(self) -> str:
        return self.ollama_base_url

    def set_ollama_model_name(self, model_name: str) -> None:
        self.ollama_model_name = model_name


config = Config()