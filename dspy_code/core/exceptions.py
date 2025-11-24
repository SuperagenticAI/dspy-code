"""
Custom exceptions for DSPy Code.

Provides specific exception types for better error handling and user feedback.
"""


class DSPyCLIError(Exception):
    """Base exception for DSPy Code errors."""


class ModelError(DSPyCLIError):
    """Error related to model operations."""


class ConfigurationError(DSPyCLIError):
    """Error in configuration."""


class CodeGenerationError(DSPyCLIError):
    """Error during code generation."""


class ProjectError(DSPyCLIError):
    """Error related to project operations."""


# Session Management Errors


class SessionError(DSPyCLIError):
    """Base exception for session errors."""


class SessionSaveError(SessionError):
    """Error saving session."""

    def __init__(self, message: str):
        super().__init__(f"Failed to save session: {message}")
        self.user_message = "Could not save your session. Please check file permissions."
        self.recovery_hint = "Try saving to a different location or check disk space."


class SessionNotFoundError(SessionError):
    """Session not found."""

    def __init__(self, session_name: str):
        super().__init__(f"Session not found: {session_name}")
        self.session_name = session_name
        self.user_message = f"Session '{session_name}' does not exist."
        self.recovery_hint = "Use /sessions to see available sessions."


class IncompatibleVersionError(SessionError):
    """Session version is incompatible."""

    def __init__(self, session_version: str, current_version: str):
        super().__init__(f"Session version {session_version} incompatible with {current_version}")
        self.user_message = "This session was created with a different version of DSPy Code."
        self.recovery_hint = "Try updating DSPy Code or create a new session."


class CorruptedSessionError(SessionError):
    """Session file is corrupted."""

    def __init__(self, details: str):
        super().__init__(f"Session file is corrupted: {details}")
        self.user_message = "The session file appears to be corrupted."
        self.recovery_hint = "You may need to delete this session and start fresh."


# Execution Errors


class ExecutionError(DSPyCLIError):
    """Base exception for execution errors."""


class CodeValidationError(ExecutionError):
    """Code failed validation checks."""

    def __init__(self, message: str):
        super().__init__(f"Code validation failed: {message}")
        self.user_message = "The generated code has validation errors."
        self.recovery_hint = "Use /validate to see detailed error messages."


class ExecutionTimeoutError(ExecutionError):
    """Code execution exceeded time limit."""

    def __init__(self, timeout: int):
        super().__init__(f"Execution exceeded {timeout}s timeout")
        self.timeout = timeout
        self.user_message = f"Code execution took longer than {timeout} seconds."
        self.recovery_hint = f"Try increasing timeout: /run timeout={timeout * 2}"


class ResourceLimitError(ExecutionError):
    """Code exceeded resource limits."""

    def __init__(self, resource: str, limit: str):
        super().__init__(f"{resource} exceeded limit: {limit}")
        self.user_message = f"Code exceeded {resource} limit."
        self.recovery_hint = "Try simplifying your code or reducing resource usage."


class SecurityError(ExecutionError):
    """Security violation detected."""

    def __init__(self, violation: str):
        super().__init__(f"Security violation: {violation}")
        self.user_message = "Code contains potentially dangerous operations."
        self.recovery_hint = "Remove dangerous imports or operations and try again."


# Optimization Errors


class OptimizationError(DSPyCLIError):
    """Base exception for optimization errors."""


class InsufficientDataError(OptimizationError):
    """Not enough training data provided."""

    def __init__(self, required: int, provided: int):
        super().__init__(f"Need {required} examples, got {provided}")
        self.user_message = f"Need at least {required} training examples for optimization."
        self.recovery_hint = "Provide more training examples and try again."


class OptimizationTimeoutError(OptimizationError):
    """Optimization exceeded time limit."""

    def __init__(self, timeout: int):
        super().__init__(f"Optimization exceeded {timeout}s timeout")
        self.user_message = "Optimization is taking too long."
        self.recovery_hint = "Try using a lighter budget or fewer examples."


class InvalidDataFormatError(OptimizationError):
    """Training data format is invalid."""

    def __init__(self, details: str):
        super().__init__(f"Invalid data format: {details}")
        self.user_message = "Training data format is incorrect."
        self.recovery_hint = "Check the data format and try again."


# Export/Import Errors


class ExportImportError(DSPyCLIError):
    """Base exception for export/import errors."""


class ExportError(ExportImportError):
    """Error during export operation."""

    def __init__(self, message: str):
        super().__init__(f"Export failed: {message}")
        self.user_message = "Could not export your data."
        self.recovery_hint = "Check file permissions and disk space."


class ImportError(ExportImportError):
    """Error during import operation."""

    def __init__(self, message: str):
        super().__init__(f"Import failed: {message}")
        self.user_message = "Could not import the file."
        self.recovery_hint = "Check that the file exists and is in the correct format."


class InvalidFormatError(ExportImportError):
    """File format is invalid."""

    def __init__(self, expected: str, got: str):
        super().__init__(f"Expected {expected} format, got {got}")
        self.user_message = f"File format is incorrect (expected {expected})."
        self.recovery_hint = "Make sure you're importing the right type of file."


def format_error_message(error: Exception) -> str:
    """
    Format an error message for display to user.

    Args:
        error: Exception to format

    Returns:
        Formatted error message with recovery hints
    """
    if isinstance(error, DSPyCLIError) and hasattr(error, "user_message"):
        message = error.user_message
        if hasattr(error, "recovery_hint"):
            message += f"\n\n💡 {error.recovery_hint}"
        return message
    else:
        return str(error)
