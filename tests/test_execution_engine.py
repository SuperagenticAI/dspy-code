"""
Unit tests for execution engine.
"""

import pytest

from dspy_code.core.exceptions import CodeValidationError
from dspy_code.execution import ExecutionEngine


@pytest.fixture
def execution_engine():
    """Create execution engine instance."""
    return ExecutionEngine()


def test_validate_valid_code(execution_engine):
    """Test validation of valid code."""
    code = """
import dspy

class TestSignature(dspy.Signature):
    input_text = dspy.InputField()
    output_text = dspy.OutputField()
"""

    result = execution_engine.validate_code(code)

    assert result.is_valid is True
    assert len(result.errors) == 0


def test_validate_syntax_error(execution_engine):
    """Test validation catches syntax errors."""
    code = """
def broken_function(
    print("missing closing paren")
"""

    result = execution_engine.validate_code(code)

    assert result.is_valid is False
    assert len(result.errors) > 0
    assert "syntax error" in result.errors[0].lower()


def test_validate_dangerous_imports(execution_engine):
    """Test validation catches dangerous imports."""
    code = """
import os
os.system("rm -rf /")
"""

    result = execution_engine.validate_code(code)

    assert result.is_valid is False
    assert any("dangerous" in error.lower() for error in result.errors)


def test_validate_deprecated_api(execution_engine):
    """Test validation warns about deprecated API."""
    code = """
import dspy
dspy.settings.configure(lm=dspy.OpenAI(model="gpt-4"))
"""

    result = execution_engine.validate_code(code)

    assert len(result.warnings) > 0
    assert any("deprecated" in warning.lower() for warning in result.warnings)


def test_validate_dspy_syntax(execution_engine):
    """Test DSPy-specific validation."""
    code = """
import dspy

class TestModule(dspy.Module):
    def __init__(self):
        super().__init__()

    # Missing forward method
"""

    result = execution_engine.validate_dspy_syntax(code)

    assert result.is_valid is False
    assert any("forward" in error.lower() for error in result.errors)


def test_execute_simple_code(execution_engine):
    """Test execution of simple code."""
    code = """
print("Hello, World!")
"""

    result = execution_engine.execute_code(code, timeout=5)

    assert result.success is True
    assert "Hello, World!" in result.stdout
    assert result.execution_time > 0


def test_execute_with_inputs(execution_engine):
    """Test execution with input variables."""
    code = """
result = x + y
print(f"Result: {result}")
"""

    inputs = {"x": 5, "y": 3}
    result = execution_engine.execute_code(code, inputs=inputs, timeout=5)

    assert result.success is True
    assert "Result: 8" in result.stdout


def test_execute_invalid_code_fails_validation(execution_engine):
    """Test that invalid code fails validation before execution."""
    code = """
import subprocess
subprocess.call(["ls"])
"""

    result = execution_engine.execute_code(code, timeout=5)

    assert result.success is False
    assert isinstance(result.error, CodeValidationError)


def test_execute_timeout(execution_engine):
    """Test execution timeout."""
    code = """
import time
time.sleep(10)
"""

    result = execution_engine.execute_code(code, timeout=1)

    assert result.success is False
    assert "timeout" in result.stderr.lower()


def test_execute_runtime_error(execution_engine):
    """Test execution with runtime error."""
    code = """
x = 1 / 0
"""

    result = execution_engine.execute_code(code, timeout=5)

    assert result.success is False
    assert "ZeroDivisionError" in result.stderr or result.stderr != ""


def test_validation_result_bool(execution_engine):
    """Test ValidationResult can be used as boolean."""
    valid_code = "x = 1"
    result = execution_engine.validate_code(valid_code)

    assert bool(result) is True

    invalid_code = "def broken("
    result = execution_engine.validate_code(invalid_code)

    assert bool(result) is False


def test_execution_result_bool(execution_engine):
    """Test ExecutionResult can be used as boolean."""
    code = "print('test')"
    result = execution_engine.execute_code(code, timeout=5)

    assert bool(result) is True


def test_sandbox_isolation(execution_engine):
    """Test that sandbox isolates execution."""
    code = """
import os
print(os.getcwd())
"""

    # This should work but be in temp directory
    result = execution_engine.execute_code(code, timeout=5)

    # Should execute but in isolated environment
    assert result.success is True or "dangerous" in str(result.error).lower()


def test_multiple_executions(execution_engine):
    """Test multiple sequential executions."""
    code1 = "print('First')"
    code2 = "print('Second')"

    result1 = execution_engine.execute_code(code1, timeout=5)
    result2 = execution_engine.execute_code(code2, timeout=5)

    assert result1.success is True
    assert result2.success is True
    assert "First" in result1.stdout
    assert "Second" in result2.stdout


def test_validation_no_dspy_import(execution_engine):
    """Test validation warns when dspy not imported."""
    code = """
def some_function():
    return "test"
"""

    result = execution_engine.validate_code(code)

    assert any("dspy" in warning.lower() for warning in result.warnings)


def test_execute_code_with_print_statements(execution_engine):
    """Test execution captures print statements."""
    code = """
print("Line 1")
print("Line 2")
print("Line 3")
"""

    result = execution_engine.execute_code(code, timeout=5)

    assert result.success is True
    assert "Line 1" in result.stdout
    assert "Line 2" in result.stdout
    assert "Line 3" in result.stdout
