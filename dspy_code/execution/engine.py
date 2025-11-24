"""
Execution engine for DSPy Code.

Handles code validation, execution, and result processing.
"""

import ast
import time
from dataclasses import dataclass, field
from typing import Any

from ..core.exceptions import CodeValidationError, ExecutionTimeoutError
from ..core.logging import get_logger
from .sandbox import ExecutionSandbox

logger = get_logger(__name__)


@dataclass
class ValidationResult:
    """Result of code validation."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        """Allow using as boolean."""
        return self.is_valid


@dataclass
class ExecutionResult:
    """Result of code execution."""

    success: bool
    output: Any
    stdout: str
    stderr: str
    execution_time: float
    error: Exception | None = None
    resource_usage: dict[str, float] = field(default_factory=dict)

    def __bool__(self) -> bool:
        """Allow using as boolean."""
        return self.success


class ExecutionEngine:
    """Manages code validation and execution."""

    def __init__(self, config_manager=None):
        """
        Initialize execution engine.

        Args:
            config_manager: Optional configuration manager
        """
        self.config_manager = config_manager
        self.sandbox = ExecutionSandbox()

    def validate_code(self, code: str) -> ValidationResult:
        """
        Validate code for syntax and security issues.

        Args:
            code: Python code to validate

        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []

        # 1. Check syntax
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
            return ValidationResult(is_valid=False, errors=errors)

        # 2. Check for dangerous imports
        is_safe, msg = self.sandbox.validate_imports(code)
        if not is_safe:
            errors.append(msg)

        # 3. Check for file operations (warning only)
        has_file_ops, msg = self.sandbox.check_file_operations(code)
        if not has_file_ops:
            warnings.append(msg)

        # 4. Check for DSPy imports
        if "import dspy" not in code and "from dspy" not in code:
            warnings.append("Code doesn't import dspy - may not be a valid DSPy module")

        # 5. Check for common issues
        if "dspy.settings.configure" in code:
            warnings.append(
                "Using deprecated dspy.settings.configure - use dspy.configure() instead"
            )

        if "dspy.OpenAI" in code or "dspy.Anthropic" in code:
            warnings.append("Using deprecated model classes - use dspy.LM() instead")

        is_valid = len(errors) == 0

        logger.debug(
            f"Validation result: valid={is_valid}, errors={len(errors)}, warnings={len(warnings)}"
        )

        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)

    def execute_code(
        self, code: str, inputs: dict[str, Any] = None, timeout: int = 30
    ) -> ExecutionResult:
        """
        Execute code with given inputs in sandbox.

        Args:
            code: Python code to execute
            inputs: Optional input variables
            timeout: Maximum execution time in seconds

        Returns:
            ExecutionResult with output and metrics
        """
        # Validate first
        validation = self.validate_code(code)
        if not validation.is_valid:
            return ExecutionResult(
                success=False,
                output=None,
                stdout="",
                stderr="\n".join(validation.errors),
                execution_time=0.0,
                error=CodeValidationError("Code validation failed"),
            )

        # Update sandbox timeout
        self.sandbox.timeout = timeout

        # Execute
        start_time = time.time()

        try:
            return_code, stdout, stderr = self.sandbox.execute(code, inputs)
            execution_time = time.time() - start_time

            success = return_code == 0

            # Parse output if successful
            output = stdout if success else None

            # Check for timeout
            if "timeout" in stderr.lower():
                error = ExecutionTimeoutError(f"Execution exceeded {timeout}s")
            else:
                error = None if success else Exception(stderr)

            result = ExecutionResult(
                success=success,
                output=output,
                stdout=stdout,
                stderr=stderr,
                execution_time=execution_time,
                error=error,
                resource_usage={"time": execution_time},
            )

            logger.debug(f"Execution completed: success={success}, time={execution_time:.2f}s")

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Execution failed: {e}")

            return ExecutionResult(
                success=False,
                output=None,
                stdout="",
                stderr=str(e),
                execution_time=execution_time,
                error=e,
            )

    def execute_interactive(self, code: str) -> ExecutionResult:
        """
        Execute code with interactive input prompts.

        Args:
            code: Python code to execute

        Returns:
            ExecutionResult
        """
        # For now, just execute without inputs
        # In future, could parse code to find required inputs and prompt user
        return self.execute_code(code)

    def run_tests(self, code: str, test_cases: list[dict[str, Any]]) -> list[ExecutionResult]:
        """
        Execute code against multiple test cases.

        Args:
            code: Python code to test
            test_cases: List of test cases with inputs and expected outputs

        Returns:
            List of ExecutionResult for each test case
        """
        results = []

        for i, test_case in enumerate(test_cases):
            logger.debug(f"Running test case {i + 1}/{len(test_cases)}")

            inputs = test_case.get("inputs", {})
            result = self.execute_code(code, inputs)
            results.append(result)

        return results

    def validate_dspy_syntax(self, code: str) -> ValidationResult:
        """
        Validate DSPy-specific syntax and patterns.

        Args:
            code: Code to validate

        Returns:
            ValidationResult with DSPy-specific checks
        """
        errors = []
        warnings = []

        # Check for Signature class
        if "class" in code and "Signature" in code:
            if "dspy.Signature" not in code:
                warnings.append("Signature class should inherit from dspy.Signature")

        # Check for Module class
        if "class" in code and "Module" in code:
            if "dspy.Module" not in code:
                warnings.append("Module class should inherit from dspy.Module")

            # Check for forward method
            if "def forward" not in code:
                errors.append("DSPy Module must implement forward() method")

        # Check for field definitions
        if "InputField" in code or "OutputField" in code:
            if "dspy.InputField" not in code and "dspy.OutputField" not in code:
                warnings.append("Use dspy.InputField() and dspy.OutputField() for fields")

        is_valid = len(errors) == 0

        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)
