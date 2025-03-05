# fiction_fabricator/src/utils/file_handler.py
import json
import os

from utils.logger import logger


def save_json(data: dict, filepath: str) -> None:
    """
    Saves data to a JSON file.

    Args:
        data (dict): The data to be saved as JSON.
        filepath (str): The path to the file where the JSON data will be saved.
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        logger.info(f"JSON data saved to: {filepath}")
    except Exception as e:
        logger.error(f"Error saving JSON to {filepath}: {e}")
        raise


def load_json(filepath: str) -> dict:
    """
    Loads data from a JSON file.

    Args:
        filepath (str): The path to the JSON file to be loaded.

    Returns:
        dict: The data loaded from the JSON file.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        JSONDecodeError: If the file content is not valid JSON.
        Exception: For other potential file reading errors.
    """
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        logger.info(f"JSON data loaded from: {filepath}")
        return data
    except FileNotFoundError:
        logger.error(f"JSON file not found: {filepath}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {filepath}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading JSON from {filepath}: {e}")
        raise


def save_markdown(text: str, filepath: str) -> None:
    """
    Saves text content to a Markdown file.

    Args:
        text (str): The text content to be saved in Markdown format.
        filepath (str): The path to the file where the Markdown content will be saved.
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            f.write(text)
        logger.info(f"Markdown content saved to: {filepath}")
    except Exception as e:
        logger.error(f"Error saving Markdown to {filepath}: {e}")
        raise
