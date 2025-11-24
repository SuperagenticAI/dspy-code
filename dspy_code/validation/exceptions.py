"""
Custom exceptions for validation and security errors.
"""


class ValidationError(Exception):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: str = None, value: str = None):
        self.field = field
        self.value = value
        super().__init__(message)


class SecurityError(Exception):
    """Raised when security validation fails."""

    def __init__(self, message: str, risk_level: str = "medium"):
        self.risk_level = risk_level
        super().__init__(message)


class ConfigurationError(ValidationError):
    """Raised when configuration validation fails."""


class CodeValidationError(ValidationError):
    """Raised when generated code validation fails."""

    def __init__(self, message: str, code_snippet: str = None, line_number: int = None):
        self.code_snippet = code_snippet
        self.line_number = line_number
        super().__init__(message)
