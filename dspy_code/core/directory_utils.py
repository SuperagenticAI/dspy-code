"""
Directory utilities for on-demand directory creation.

This module provides helper functions to create directories only when needed,
supporting flexible project structures where not all directories need to exist upfront.
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config import ConfigManager


def ensure_output_directory(config_manager: "ConfigManager") -> Path:
    """
    Ensure the output directory exists, creating it if needed.

    This function reads the output directory path from the project configuration
    and creates it if it doesn't exist. This allows commands to work without
    requiring a full project structure to be initialized upfront.

    Args:
        config_manager: The ConfigManager instance containing project configuration

    Returns:
        Path: The path to the output directory (guaranteed to exist)

    Example:
        >>> from dspy_cli.core.config import ConfigManager
        >>> config_manager = ConfigManager()
        >>> output_dir = ensure_output_directory(config_manager)
        >>> # output_dir now exists and can be used to save files
    """
    output_dir = Path(config_manager.config.output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def ensure_directory(path: Path) -> Path:
    """
    Ensure a directory exists, creating it if needed.

    This is a general-purpose utility for creating any directory path.
    It creates all parent directories as needed and doesn't raise an error
    if the directory already exists.

    Args:
        path: The directory path to ensure exists

    Returns:
        Path: The same path (guaranteed to exist)

    Example:
        >>> from pathlib import Path
        >>> data_dir = ensure_directory(Path("data/examples"))
        >>> # data/examples now exists
    """
    path.mkdir(parents=True, exist_ok=True)
    return path
