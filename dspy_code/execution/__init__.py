"""
Code execution engine for DSPy Code.

Provides safe execution of generated code with sandboxing and resource limits.
"""

from .engine import ExecutionEngine, ExecutionResult, ValidationResult
from .sandbox import ExecutionSandbox

__all__ = ["ExecutionEngine", "ExecutionResult", "ExecutionSandbox", "ValidationResult"]
