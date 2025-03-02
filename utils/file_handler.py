# utils/file_handler.py
import json
import os

from utils.logger import logger


def save_json(data: dict, filepath: str) -> None:
    """
    Saves data to a JSON file.
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)  # Ensure directory exists
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)  # Save JSON with indentation for readability
        logger.info("JSON data saved to: %s", filepath)  # Lazy format
    except Exception as e:
        logger.error("Error saving JSON to %s: %s", filepath, e)  # Lazy format
        raise  # Re-raise the exception for handling higher up if needed


def load_json(filepath: str) -> dict:
    """
    Loads data from a JSON file.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info("JSON data loaded from: %s", filepath)  # Lazy format
        return data
    except FileNotFoundError:
        logger.error("JSON file not found: %s", filepath)  # Lazy format
        raise
    except json.JSONDecodeError as e:
        logger.error("Error decoding JSON from %s: %s", filepath, e)  # Lazy format
        raise
    except Exception as e:
        logger.error("Error loading JSON from %s: %s", filepath, e)  # Lazy format
        raise


def save_markdown(text: str, filepath: str) -> None:
    """
    Saves text content to a Markdown file.
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)  # Ensure directory exists
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
        logger.info("Markdown content saved to: %s", filepath)  # Lazy format
    except Exception as e:
        logger.error("Error saving Markdown to %s: %s", filepath, e)  # Lazy format
        raise  # Re-raise the exception