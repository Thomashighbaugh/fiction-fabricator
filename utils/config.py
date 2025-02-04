# utils/config.py
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Configuration manager for the Fiction Fabricator application.

    Loads configurations from environment variables and provides access
    to them through getter methods. Uses a singleton pattern to ensure
    only one configuration instance exists throughout the application.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        Initializes the configuration by loading environment variables.
        """
        self.project_directory = os.getenv("PROJECT_DIRECTORY", "data")
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.ollama_model_name = os.getenv("OLLAMA_MODEL_NAME", "llama2")


    def get_project_directory(self) -> str:
        """
        Returns the configured project directory.

        Returns:
            str: The directory where project data will be stored.
        """
        return self.project_directory

    def get_log_level(self) -> str:
        """
        Returns the configured log level.

        Returns:
            str: The log level for the application (e.g., "DEBUG", "INFO", "WARNING").
        """
        return self.log_level

    def get_ollama_model_name(self) -> str:
        """
        Returns the configured Ollama model name.

        Returns:
            str: The name of the Ollama model to be used.
        """
        return self.ollama_model_name

    def set_ollama_model_name(self, model_name: str) -> None:
        """
        Sets the configured Ollama model name.

        Args:
            str: The name of the Ollama model to be used.
        """
        self.ollama_model_name = model_name


# Instantiate the Config singleton
config = Config()