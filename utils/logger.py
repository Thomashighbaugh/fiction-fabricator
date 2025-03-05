# /home/tlh/gui-fab-fict/utils/logger.py
import logging
import sys

from utils.config import config  # Import the config object


def setup_logger() -> logging.Logger:
    """
    Sets up and configures a logger for the Fiction Fabricator application.

    The logger outputs to the console and its log level is determined by the
    'LOG_LEVEL' configuration parameter.

    Returns:
        logging.Logger: A configured logger instance.
    """
    logger = logging.getLogger(__name__)
    log_level_str = config.get_log_level()  # Access the log level

    log_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    log_level = log_levels.get(log_level_str, logging.INFO)
    logger.setLevel(log_level)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(module)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()
