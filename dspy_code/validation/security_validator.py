"""
Security validation for DSPy Code.

This module provides security checks for code execution, file operations,
and user inputs to prevent malicious activities.
"""

import ast
import re
from pathlib import Path
from typing import Any

from .exceptions import SecurityError


class SecurityValidator:
    """Provides security validation and checks for DSPy Code operations."""

    # Patterns that indicate potential security risks
    DANGEROUS_PATTERNS = [
        # Code execution
        r"eval\s*\(",
        r"exec\s*\(",
        r"compile\s*\(",
        r"__import__\s*\(",
        # File operations
        r"open\s*\(",
        r"file\s*\(",
        r"with\s+open\s*\(",
        # System operations
        r"os\.system\s*\(",
        r"os\.popen\s*\(",
        r"os\.spawn\w*\s*\(",
        r"subprocess\.",
        r"commands\.",
        # Dynamic attribute access
        r"getattr\s*\(",
        r"setattr\s*\(",
        r"delattr\s*\(",
        r"hasattr\s*\(",
        # Introspection
        r"globals\s*\(",
        r"locals\s*\(",
        r"vars\s*\(",
        r"dir\s*\(",
        # Network operations
        r"urllib\.",
        r"requests\.",
        r"http\.",
        r"socket\.",
        # Dangerous built-ins
        r"input\s*\(",
        r"raw_input\s*\(",
        r"reload\s*\(",
    ]

    # Modules that should not be imported in generated code
    DANGEROUS_MODULES = {
        "os",
        "sys",
        "subprocess",
        "commands",
        "importlib",
        "imp",
        "urllib",
        "urllib2",
        "urllib3",
        "requests",
        "http",
        "httplib",
        "socket",
        "socketserver",
        "ftplib",
        "smtplib",
        "telnetlib",
        "pickle",
        "cPickle",
        "marshal",
        "shelve",
        "dbm",
        "gdbm",
        "sqlite3",
        "mysql",
        "psycopg2",
        "pymongo",
        "ctypes",
        "cffi",
        "pty",
        "tty",
        "termios",
        "__builtin__",
        "builtins",
        "__main__",
    }

    # File extensions that are considered safe for reading
    SAFE_FILE_EXTENSIONS = {
        ".txt",
        ".md",
        ".json",
        ".yaml",
        ".yml",
        ".csv",
        ".tsv",
        ".py",
        ".pyx",
        ".pyi",
        ".ipynb",
    }

    # Maximum file size for reading (in bytes)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    def __init__(self):
        self.dangerous_regex = re.compile("|".join(self.DANGEROUS_PATTERNS), re.IGNORECASE)

    def validate_code_execution_safety(self, code: str) -> dict[str, Any]:
        """
        Validate that code is safe for execution.

        Args:
            code: The code to validate

        Returns:
            Dictionary with security analysis results

        Raises:
            SecurityError: If code contains dangerous patterns
        """
        if not code or not code.strip():
            return {"safe": True, "issues": []}

        issues = []

        # Check for dangerous patterns
        dangerous_matches = self.dangerous_regex.findall(code)
        if dangerous_matches:
            issues.extend([f"Dangerous pattern found: {match}" for match in dangerous_matches])

        # Parse and analyze AST
        try:
            tree = ast.parse(code)
            ast_issues = self._analyze_ast_security(tree)
            issues.extend(ast_issues)
        except SyntaxError:
            # If code doesn't parse, it's not executable, so it's safe in that sense
            pass

        # Check for suspicious string patterns
        string_issues = self._check_suspicious_strings(code)
        issues.extend(string_issues)

        if issues:
            raise SecurityError(
                f"Code contains {len(issues)} security issue(s): {'; '.join(issues[:3])}",
                risk_level="high" if len(issues) > 5 else "medium",
            )

        return {"safe": True, "issues": []}

    def validate_file_access_safety(self, file_path: Path, operation: str = "read") -> bool:
        """
        Validate that file access is safe.

        Args:
            file_path: Path to the file
            operation: Type of operation (read, write, execute)

        Returns:
            True if safe, False otherwise

        Raises:
            SecurityError: If file access is dangerous
        """
        if not isinstance(file_path, Path):
            file_path = Path(file_path)

        # Check for path traversal
        if ".." in file_path.parts:
            raise SecurityError("Path traversal detected", risk_level="high")

        # Check if path is absolute (should be relative for safety)
        if file_path.is_absolute():
            raise SecurityError("Absolute paths not allowed", risk_level="medium")

        # Check file extension for read operations
        if operation == "read" and file_path.suffix not in self.SAFE_FILE_EXTENSIONS:
            raise SecurityError(
                f"File extension '{file_path.suffix}' not in safe list", risk_level="medium"
            )

        # Check file size for read operations
        if operation == "read" and file_path.exists():
            try:
                file_size = file_path.stat().st_size
                if file_size > self.MAX_FILE_SIZE:
                    raise SecurityError(
                        f"File too large ({file_size} bytes, max {self.MAX_FILE_SIZE})",
                        risk_level="medium",
                    )
            except OSError:
                raise SecurityError("Cannot access file information", risk_level="low")

        # Check for write operations in sensitive directories
        if operation in ("write", "execute"):
            sensitive_dirs = {".git", ".ssh", ".kiro", "__pycache__"}
            if any(part.startswith(".") and part in sensitive_dirs for part in file_path.parts):
                raise SecurityError(
                    "Write access to sensitive directory not allowed", risk_level="high"
                )

        return True

    def validate_command_execution_safety(self, command: str) -> bool:
        """
        Validate that a command is safe to execute.

        Args:
            command: The command to validate

        Returns:
            True if safe, False otherwise

        Raises:
            SecurityError: If command is dangerous
        """
        if not command or not command.strip():
            raise SecurityError("Empty command not allowed")

        command = command.strip()

        # List of dangerous commands
        dangerous_commands = {
            "rm",
            "del",
            "format",
            "fdisk",
            "mkfs",
            "dd",
            "sudo",
            "su",
            "chmod",
            "chown",
            "chgrp",
            "wget",
            "curl",
            "nc",
            "netcat",
            "telnet",
            "ssh",
            "scp",
            "rsync",
            "python",
            "python3",
            "node",
            "ruby",
            "perl",
            "bash",
            "sh",
            "zsh",
            "powershell",
            "cmd",
            "command",
        }

        # Extract the base command
        base_command = command.split()[0].lower()

        if base_command in dangerous_commands:
            raise SecurityError(f"Command '{base_command}' not allowed", risk_level="high")

        # Check for command chaining
        if any(op in command for op in ["&&", "||", ";", "|", ">", "<", "`"]):
            raise SecurityError("Command chaining not allowed", risk_level="high")

        # Check for variable substitution
        if "$" in command or "${" in command:
            raise SecurityError("Variable substitution not allowed", risk_level="medium")

        return True

    def validate_api_key_security(self, api_key: str, provider: str) -> bool:
        """
        Validate API key security and format.

        Args:
            api_key: The API key to validate
            provider: The provider name

        Returns:
            True if secure, False otherwise

        Raises:
            SecurityError: If API key has security issues
        """
        if not api_key or not api_key.strip():
            raise SecurityError("API key cannot be empty")

        api_key = api_key.strip()

        # Check for obviously fake or test keys
        fake_patterns = [
            r"test",
            r"fake",
            r"dummy",
            r"example",
            r"placeholder",
            r"your_key_here",
            r"insert_key",
            r"api_key_here",
        ]

        for pattern in fake_patterns:
            if re.search(pattern, api_key, re.IGNORECASE):
                raise SecurityError(
                    "API key appears to be a placeholder or test key", risk_level="low"
                )

        # Check for minimum length requirements
        min_lengths = {"openai": 40, "anthropic": 90, "gemini": 30, "default": 20}

        min_length = min_lengths.get(provider.lower(), min_lengths["default"])
        if len(api_key) < min_length:
            raise SecurityError(
                f"API key too short for {provider} (minimum {min_length} characters)",
                risk_level="medium",
            )

        # Check for suspicious characters
        if not re.match(r"^[a-zA-Z0-9\-_]+$", api_key):
            raise SecurityError("API key contains suspicious characters", risk_level="medium")

        return True

    def validate_user_input_safety(self, user_input: str, input_type: str = "general") -> str:
        """
        Validate and sanitize user input for security.

        Args:
            user_input: The user input to validate
            input_type: Type of input (general, code, path, etc.)

        Returns:
            Sanitized user input

        Raises:
            SecurityError: If input contains dangerous content
        """
        if not user_input:
            return ""

        # Remove null bytes and control characters
        sanitized = user_input.replace("\x00", "")
        sanitized = re.sub(r"[\x01-\x08\x0B\x0C\x0E-\x1F\x7F]", "", sanitized)

        # Check for dangerous patterns based on input type
        if input_type == "code":
            if self.dangerous_regex.search(sanitized):
                raise SecurityError(
                    "User input contains potentially dangerous code patterns", risk_level="high"
                )

        elif input_type == "path":
            if ".." in sanitized or sanitized.startswith("/"):
                raise SecurityError("Path input contains dangerous patterns", risk_level="high")

        elif input_type == "command":
            self.validate_command_execution_safety(sanitized)

        # Check for excessively long input (potential DoS)
        max_lengths = {"general": 10000, "code": 50000, "path": 500, "command": 1000}

        max_length = max_lengths.get(input_type, max_lengths["general"])
        if len(sanitized) > max_length:
            raise SecurityError(
                f"Input too long ({len(sanitized)} chars, max {max_length})", risk_level="medium"
            )

        return sanitized

    def _analyze_ast_security(self, tree: ast.AST) -> list[str]:
        """Analyze AST for security issues."""
        issues = []

        for node in ast.walk(tree):
            # Check for dangerous function calls
            if isinstance(node, ast.Call):
                func_name = self._get_function_name(node.func)
                if func_name in {"eval", "exec", "compile", "__import__"}:
                    issues.append(f"Dangerous function call: {func_name}")

            # Check for dangerous imports
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in self.DANGEROUS_MODULES:
                        issues.append(f"Dangerous import: {alias.name}")

            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module in self.DANGEROUS_MODULES:
                    issues.append(f"Dangerous import from: {node.module}")

            # Check for attribute access to dangerous modules
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name) and node.value.id in self.DANGEROUS_MODULES:
                    issues.append(f"Access to dangerous module: {node.value.id}")

        return issues

    def _check_suspicious_strings(self, code: str) -> list[str]:
        """Check for suspicious string patterns in code."""
        issues = []

        # Check for hardcoded credentials patterns
        credential_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
        ]

        for pattern in credential_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append("Hardcoded credentials detected")
                break

        # Check for SQL injection patterns
        sql_patterns = [
            r"SELECT\s+.*\s+FROM\s+.*\s+WHERE\s+.*\+",
            r"INSERT\s+INTO\s+.*\s+VALUES\s+.*\+",
            r"UPDATE\s+.*\s+SET\s+.*\+",
            r"DELETE\s+FROM\s+.*\s+WHERE\s+.*\+",
        ]

        for pattern in sql_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append("Potential SQL injection pattern")
                break

        # Check for shell injection patterns
        shell_patterns = [
            r"os\.system\s*\(\s*.*\+",
            r"subprocess\.\w+\s*\(\s*.*\+",
            r"commands\.\w+\s*\(\s*.*\+",
        ]

        for pattern in shell_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append("Potential shell injection pattern")
                break

        return issues

    def _get_function_name(self, func_node: ast.AST) -> str | None:
        """Extract function name from AST node."""
        if isinstance(func_node, ast.Name):
            return func_node.id
        elif isinstance(func_node, ast.Attribute):
            return func_node.attr
        return None
