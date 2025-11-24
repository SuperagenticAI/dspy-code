"""
Logging configuration for DSPy Code.
"""

import logging
from pathlib import Path

from rich.logging import RichHandler


def setup_logging(verbose: bool = False, debug: bool = False, log_file: Path | None = None) -> None:
    """
    Setup logging configuration for DSPy Code.

    Args:
        verbose: Enable verbose output
        debug: Enable debug mode
        log_file: Optional log file path
    """
    # Determine log level
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING

    # Create formatters
    console_formatter = logging.Formatter("%(message)s")

    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler with Rich
    console_handler = RichHandler(
        console=None, show_time=debug, show_path=debug, markup=True, rich_tracebacks=True
    )
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always debug level for file
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Set specific logger levels
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
