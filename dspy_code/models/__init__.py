"""
Core models and data structures for DSPy Code.
"""

from .code_generator import CodeGenerator
from .model_manager import ModelManager
from .task_collector import GoldExample, ReasoningPattern, TaskCollector, TaskDefinition

__all__ = [
    "CodeGenerator",
    "GoldExample",
    "ModelManager",
    "ReasoningPattern",
    "TaskCollector",
    "TaskDefinition",
]
