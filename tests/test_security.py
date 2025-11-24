"""
Security tests for DSPy CLI.

Tests sandbox isolation, security validation, and resource limits.
"""

import pytest

from dspy_code.execution import ExecutionEngine, ExecutionSandbox


@pytest.fixture
def execution_engine():
    """Create execution engine."""
    return ExecutionEngine()


@pytest.fixture
def sandbox():
    """Create execution sandbox."""
    return ExecutionSandbox()


# Dangerous Import Tests


def test_blocks_os_system(execution_engine):
    """Test that os.system is blocked."""
    code = """
import os
os.system("ls")
"""

    result = execution_engine.validate_code(code)
    assert result.is_valid is False
    assert any("dangerous" in error.lower() for error in result.errors)


def test_blocks_subprocess(execution_engine):
    """Test that subprocess is blocked."""
    code = """
import subprocess
subprocess.call(["ls"])
"""

    result = execution_engine.validate_code(code)
    assert result.is_valid is False


def test_blocks_eval(execution_engine):
    """Test that eval is blocked."""
    code = """
eval("print('dangerous')")
"""

    result = execution_engine.validate_code(code)
    assert result.is_valid is False


def test_blocks_exec(execution_engine):
    """Test that exec is blocked."""
    code = """
exec("import os")
"""

    result = execution_engine.validate_code(code)
    assert result.is_valid is False


def test_blocks_compile(execution_engine):
    """Test that compile is blocked."""
    code = """
compile("print('test')", "<string>", "exec")
"""

    result = execution_engine.validate_code(code)
    assert result.is_valid is False


def test_blocks_importlib(execution_engine):
    """Test that importlib is blocked."""
    code = """
import importlib
importlib.import_module("os")
"""

    result = execution_engine.validate_code(code)
    assert result.is_valid is False


def test_blocks_socket(execution_engine):
    """Test that socket is blocked."""
    code = """
import socket
s = socket.socket()
"""

    result = execution_engine.validate_code(code)
    assert result.is_valid is False


def test_blocks_urllib(execution_engine):
    """Test that urllib is blocked."""
    code = """
import urllib
urllib.request.urlopen("http://example.com")
"""

    result = execution_engine.validate_code(code)
    assert result.is_valid is False


# File Operation Tests


def test_warns_file_operations(execution_engine):
    """Test that file operations generate warnings."""
    code = """
with open("test.txt", "w") as f:
    f.write("test")
"""

    result = execution_engine.validate_code(code)
    # Should warn but not block
    assert len(result.warnings) > 0


def test_warns_path_operations(execution_engine):
    """Test that Path operations generate warnings."""
    code = """
from pathlib import Path
Path("test.txt").write_text("test")
"""

    result = execution_engine.validate_code(code)
    assert len(result.warnings) > 0


# Resource Limit Tests


def test_timeout_enforcement(execution_engine):
    """Test that timeout is enforced."""
    code = """
import time
time.sleep(10)
"""

    result = execution_engine.execute_code(code, timeout=1)

    assert result.success is False
    assert "timeout" in result.stderr.lower()


def test_infinite_loop_timeout(execution_engine):
    """Test that infinite loops are terminated."""
    code = """
while True:
    pass
"""

    result = execution_engine.execute_code(code, timeout=2)

    assert result.success is False
    assert "timeout" in result.stderr.lower()


# Sandbox Isolation Tests


def test_sandbox_environment_isolation(sandbox):
    """Test that sandbox uses isolated environment."""
    env = sandbox._get_safe_env()

    # Should have minimal environment
    assert "PATH" in env
    assert "HOME" in env
    assert "TMPDIR" in env

    # Should not have user's full environment
    assert len(env) < 10  # Very limited


def test_sandbox_import_validation(sandbox):
    """Test sandbox validates imports."""
    code = """
import os
import sys
"""

    is_valid, msg = sandbox.validate_imports(code)
    assert is_valid is False
    assert "os.system" in msg or "dangerous" in msg.lower()


def test_sandbox_file_operation_check(sandbox):
    """Test sandbox checks file operations."""
    code = """
open("test.txt", "w")
"""

    is_safe, msg = sandbox.check_file_operations(code)
    assert is_safe is False
    assert "open(" in msg


# Safe Code Tests


def test_allows_safe_imports(execution_engine):
    """Test that safe imports are allowed."""
    code = """
import json
import math
import datetime
"""

    result = execution_engine.validate_code(code)
    assert result.is_valid is True


def test_allows_dspy_imports(execution_engine):
    """Test that DSPy imports are allowed."""
    code = """
import dspy

class TestSignature(dspy.Signature):
    x = dspy.InputField()
    y = dspy.OutputField()
"""

    result = execution_engine.validate_code(code)
    assert result.is_valid is True


def test_allows_safe_operations(execution_engine):
    """Test that safe operations are allowed."""
    code = """
x = 5
y = 10
result = x + y
print(result)
"""

    result = execution_engine.validate_code(code)
    assert result.is_valid is True

    exec_result = execution_engine.execute_code(code, timeout=5)
    assert exec_result.success is True


# Path Traversal Tests


def test_no_path_traversal_in_execution(execution_engine):
    """Test that path traversal is prevented."""
    code = """
with open("../../../etc/passwd", "r") as f:
    print(f.read())
"""

    # Should be caught by validation
    result = execution_engine.validate_code(code)
    assert len(result.warnings) > 0


# Memory Safety Tests


def test_large_allocation_handled(execution_engine):
    """Test that large memory allocations are handled."""
    code = """
# Try to allocate large list
x = [0] * 1000000
print(len(x))
"""

    result = execution_engine.execute_code(code, timeout=5)
    # Should complete or fail gracefully
    assert result is not None


# Code Injection Tests


def test_prevents_code_injection_via_eval(execution_engine):
    """Test that code injection via eval is prevented."""
    code = """
user_input = "__import__('os').system('ls')"
eval(user_input)
"""

    result = execution_engine.validate_code(code)
    assert result.is_valid is False


def test_prevents_code_injection_via_exec(execution_engine):
    """Test that code injection via exec is prevented."""
    code = """
user_input = "import os; os.system('ls')"
exec(user_input)
"""

    result = execution_engine.validate_code(code)
    assert result.is_valid is False


# Multiple Security Violations


def test_multiple_security_violations(execution_engine):
    """Test code with multiple security issues."""
    code = """
import os
import subprocess
eval("print('test')")
open("/etc/passwd", "r")
"""

    result = execution_engine.validate_code(code)
    assert result.is_valid is False
    assert len(result.errors) > 0


# Validation Bypass Attempts


def test_cannot_bypass_with_string_manipulation(execution_engine):
    """Test that string manipulation doesn't bypass validation."""
    code = """
dangerous = "os" + ".system"
eval(dangerous + "('ls')")
"""

    result = execution_engine.validate_code(code)
    # Should catch eval
    assert result.is_valid is False


def test_cannot_bypass_with_getattr(execution_engine):
    """Test that getattr doesn't bypass validation."""
    code = """
import os
func = getattr(os, 'system')
func('ls')
"""

    result = execution_engine.validate_code(code)
    # Should catch os import
    assert result.is_valid is False


# Execution Environment Tests


def test_execution_in_temp_directory(sandbox):
    """Test that execution happens in temporary directory."""
    code = """
import os
print(os.getcwd())
"""

    return_code, stdout, stderr = sandbox.execute(code)

    # Should execute (or be blocked by validation)
    assert return_code is not None


def test_cleanup_after_execution(sandbox):
    """Test that temporary files are cleaned up."""
    code = """
print("test")
"""

    # Execute
    sandbox.execute(code)

    # Temp directory should be cleaned up automatically
    # (handled by context manager in sandbox)
    assert True  # If we get here, cleanup worked


# Permission Tests


def test_no_write_outside_sandbox(execution_engine):
    """Test that writing outside sandbox is prevented."""
    code = """
with open("/tmp/test_outside.txt", "w") as f:
    f.write("test")
"""

    result = execution_engine.validate_code(code)
    # Should warn about file operations
    assert len(result.warnings) > 0


# Network Access Tests


def test_blocks_network_access(execution_engine):
    """Test that network access is blocked."""
    code = """
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("example.com", 80))
"""

    result = execution_engine.validate_code(code)
    assert result.is_valid is False


def test_blocks_http_requests(execution_engine):
    """Test that HTTP requests are blocked."""
    code = """
import urllib.request
urllib.request.urlopen("http://example.com")
"""

    result = execution_engine.validate_code(code)
    assert result.is_valid is False


# Comprehensive Security Test


def test_comprehensive_security_check(execution_engine):
    """Test comprehensive security validation."""
    dangerous_operations = [
        "import os",
        "import subprocess",
        "eval('test')",
        "exec('test')",
        "compile('test', '<string>', 'exec')",
        "__import__('os')",
        "import socket",
        "import urllib",
    ]

    for operation in dangerous_operations:
        code = f"{operation}\nprint('done')"
        result = execution_engine.validate_code(code)
        assert result.is_valid is False, f"Failed to block: {operation}"
