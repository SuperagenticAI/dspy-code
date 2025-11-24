"""
Core functionality for DSPy Code.
"""

from .config import GepaConfig, ModelConfig, ProjectConfig
from .exceptions import (
    CodeGenerationError,
    CodeValidationError,
    ConfigurationError,
    DSPyCLIError,
    ProjectError,
)
from .logging import setup_logging

__all__ = [
    "CodeGenerationError",
    "CodeValidationError",
    "ConfigurationError",
    "DSPyCLIError",
    "GepaConfig",
    "ModelConfig",
    "ProjectConfig",
    "ProjectError",
    "setup_logging",
]
