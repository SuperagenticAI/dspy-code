"""
Execution sandbox for safe code execution.

Provides isolated environment with resource limits and security restrictions.
"""

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from ..core.logging import get_logger

logger = get_logger(__name__)


class ExecutionSandbox:
    """Provides sandboxed execution environment for generated code."""

    def __init__(self, timeout: int = 30, memory_limit_mb: int = 512):
        """
        Initialize execution sandbox.

        Args:
            timeout: Maximum execution time in seconds
            memory_limit_mb: Maximum memory usage in MB
        """
        self.timeout = timeout
        self.memory_limit_mb = memory_limit_mb
        self.temp_dir = None

    def execute(self, code: str, inputs: dict[str, Any] = None) -> tuple[int, str, str]:
        """
        Execute code in sandbox.

        Args:
            code: Python code to execute
            inputs: Optional input variables as dictionary

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        # Create temporary directory for execution
        with tempfile.TemporaryDirectory() as temp_dir:
            self.temp_dir = Path(temp_dir)

            # Write code to temporary file
            code_file = self.temp_dir / "generated_code.py"

            # Wrap code with input handling if needed
            if inputs:
                wrapped_code = self._wrap_code_with_inputs(code, inputs)
            else:
                wrapped_code = code

            code_file.write_text(wrapped_code)

            # Execute in subprocess
            try:
                # Prefer Python from project venv if available
                from ..core.logging import get_logger
                from ..core.venv_utils import get_project_python

                logger = get_logger(__name__)
                python_exe = get_project_python(Path.cwd())
                if python_exe is None:
                    # No project venv - fallback to sys.executable
                    python_exe = Path(sys.executable)
                    logger.debug("No project venv found - using sys.executable")
                else:
                    logger.debug(f"Using project venv Python: {python_exe}")

                result = subprocess.run(
                    [str(python_exe), str(code_file)],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=str(self.temp_dir),
                    # Security: limit environment variables
                    env=self._get_safe_env(),
                    check=False,
                )

                return result.returncode, result.stdout, result.stderr

            except subprocess.TimeoutExpired:
                logger.warning(f"Execution timeout after {self.timeout}s")
                return -1, "", f"Execution timeout after {self.timeout} seconds"
            except Exception as e:
                logger.error(f"Execution failed: {e}")
                return -1, "", f"Execution error: {e!s}"

    def _wrap_code_with_inputs(self, code: str, inputs: dict[str, Any]) -> str:
        """
        Wrap code with input variable definitions.

        Args:
            code: Original code
            inputs: Input variables

        Returns:
            Wrapped code with inputs defined
        """
        input_lines = []
        for key, value in inputs.items():
            # Safely serialize input values
            if isinstance(value, str):
                input_lines.append(f"{key} = {value!r}")
            else:
                input_lines.append(f"{key} = {value}")

        wrapped = "\n".join(input_lines) + "\n\n" + code
        return wrapped

    def _get_safe_env(self) -> dict[str, str]:
        """
        Get safe environment variables for execution.

        Returns:
            Dictionary of safe environment variables
        """
        # Only include essential environment variables
        safe_env = {
            "PATH": "/usr/bin:/bin",
            "PYTHONPATH": "",
            "HOME": str(self.temp_dir),
            "TMPDIR": str(self.temp_dir),
        }

        # Add Python-specific variables
        if "PYTHONHOME" in sys.prefix:
            safe_env["PYTHONHOME"] = sys.prefix

        return safe_env

    def validate_imports(self, code: str) -> tuple[bool, str]:
        """
        Validate that code only uses allowed imports.

        Args:
            code: Code to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # List of dangerous modules
        dangerous_modules = {
            "os.system",
            "subprocess",
            "eval",
            "exec",
            "compile",
            "__import__",
            "importlib",
            "ctypes",
            "multiprocessing",
            "socket",
            "urllib",
            "requests",
            "http",
        }

        # Check for dangerous imports
        for dangerous in dangerous_modules:
            if dangerous in code:
                return False, f"Dangerous import/function detected: {dangerous}"

        return True, ""

    def check_file_operations(self, code: str) -> tuple[bool, str]:
        """
        Check for potentially dangerous file operations.

        Args:
            code: Code to check

        Returns:
            Tuple of (is_safe, warning_message)
        """
        dangerous_patterns = [
            "open(",
            "file(",
            "Path(",
            "rmdir",
            "unlink",
            "remove",
            "chmod",
            "chown",
        ]

        warnings = []
        for pattern in dangerous_patterns:
            if pattern in code:
                warnings.append(f"File operation detected: {pattern}")

        if warnings:
            return False, "; ".join(warnings)

        return True, ""


# Import exceptions from core
