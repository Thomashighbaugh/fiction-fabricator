"""
Logging configuration for Fiction Fabricator.

Provides centralized logging setup with file and console handlers.

## Usage Pattern

For error handling in Fiction Fabricator:

```python
from src.logger import get_logger

logger = get_logger(__name__)

try:
    # operation
    pass
except SomeError as e:
    # Log to file for debugging/troubleshooting
    logger.error(f"Operation failed: {e}", exc_info=True)
    # Display to user via console (keep existing rich console output)
    console.print(f"[red]Error: {e}[/red]")
```

**Key principle**: This is an interactive CLI application.
- **console.print**: User-facing errors (must see these)
- **logger.error**: Supplemental file logging (for debugging)
- Both should be used together in error handlers
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging(
    log_dir: Path | None = None,
    log_level: str = "INFO",
    enable_console: bool = True,
    enable_file: bool = True,
) -> logging.Logger:
    """
    Configure logging for Fiction Fabricator.

    Args:
        log_dir: Directory for log files (default: ./logs)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_console: Whether to log to console
        enable_file: Whether to log to file

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("fiction_fabricator")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    simple_formatter = logging.Formatter("%(levelname)s: %(message)s")

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)

    # File handler
    if enable_file:
        if log_dir is None:
            log_dir = Path.cwd() / "logs"

        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "fiction_fabricator.log"

        # Rotating file handler (10MB max, keep 5 backups)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)  # All messages to file
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"fiction_fabricator.{name}")
    return logging.getLogger("fiction_fabricator")
