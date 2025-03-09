# fiction_fabricator/src/utils/file_handler.py
import os
import tomli
import tomli_w

from utils.logger import logger


def save_toml(data: dict, filepath: str) -> None:
    """
    Saves data to a TOML file.

    Args:
        data (dict): The data to be saved as TOML.
        filepath (str): The path to the file.
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:  # Note: "wb" for tomli-w
            tomli_w.dump(data, f)
        logger.info(f"TOML data saved to: {filepath}")
    except Exception as e:
        logger.error(f"Error saving TOML to {filepath}: {e}")
        raise


def load_toml(filepath: str) -> dict:
    """
    Loads data from a TOML file.

    Args:
        filepath (str): The path to the TOML file.

    Returns:
        dict: The data loaded from the TOML file.

    Raises:
        FileNotFoundError: If the file does not exist.
        TOMLDecodeError: If the file content is not valid TOML.
    """
    try:
        with open(filepath, "rb") as f:  # Note: "rb" for tomli
            data = tomli.load(f)
        logger.info(f"TOML data loaded from: {filepath}")
        return data
    except FileNotFoundError:
        logger.error(f"TOML file not found: {filepath}")
        raise
    except tomli.TOMLDecodeError as e:
        logger.error(f"Error decoding TOML from {filepath}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading TOML from {filepath}: {e}")
        raise


def save_markdown(text: str, filepath: str) -> None:
    """
    Saves text content to a Markdown file.  (No changes needed)
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
