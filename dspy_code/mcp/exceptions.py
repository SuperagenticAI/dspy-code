"""
MCP-specific exceptions for DSPy Code.

Provides detailed error handling for MCP client operations with user-friendly
messages and troubleshooting guidance.
"""

from typing import Any

from ..core.exceptions import DSPyCLIError


class MCPError(DSPyCLIError):
    """Base class for MCP-related errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.details = details or {}

    def get_troubleshooting_message(self) -> str:
        """Get troubleshooting guidance for this error."""
        return "For more information, run with --verbose flag for detailed logs."


class MCPConnectionError(MCPError):
    """Error connecting to MCP server."""

    def __init__(
        self,
        message: str,
        server_name: str | None = None,
        transport_type: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, details)
        self.server_name = server_name
        self.transport_type = transport_type

    def get_troubleshooting_message(self) -> str:
        """Get troubleshooting guidance for connection errors."""
        tips = ["Troubleshooting:"]

        if self.transport_type == "stdio":
            tips.extend(
                [
                    "  1. Ensure the server command is installed and in your PATH",
                    "  2. Verify the command and arguments in your configuration",
                    "  3. Check that any required environment variables are set",
                    "  4. Try running the command manually to test it works",
                ]
            )
        elif self.transport_type == "sse":
            tips.extend(
                [
                    "  1. Verify the server URL is correct and accessible",
                    "  2. Check your network connection",
                    "  3. Ensure any required authentication tokens are valid",
                    "  4. Verify SSL certificates if using HTTPS",
                ]
            )
        elif self.transport_type == "websocket":
            tips.extend(
                [
                    "  1. Verify the WebSocket URL is correct",
                    "  2. Check your network connection and firewall settings",
                    "  3. Ensure the server supports WebSocket connections",
                    "  4. Verify any required authentication",
                ]
            )
        else:
            tips.append("  1. Check your server configuration")
            tips.append("  2. Verify the transport type is correct")

        tips.append("  5. Run with --verbose for detailed logs")

        return "\n".join(tips)


class MCPConfigurationError(MCPError):
    """Error in MCP server configuration."""

    def __init__(
        self,
        message: str,
        server_name: str | None = None,
        config_field: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, details)
        self.server_name = server_name
        self.config_field = config_field

    def get_troubleshooting_message(self) -> str:
        """Get troubleshooting guidance for configuration errors."""
        tips = [
            "Troubleshooting:",
            "  1. Check your dspy_config.yaml file for syntax errors",
            "  2. Verify all required fields are present",
            "  3. Ensure field values are of the correct type",
            "  4. Check for typos in field names",
        ]

        if self.config_field:
            tips.append(f"  5. Review the '{self.config_field}' field in your configuration")

        tips.append("  6. See documentation for configuration examples")

        return "\n".join(tips)


class MCPOperationError(MCPError):
    """Error during MCP operation (tool call, resource read, etc.)."""

    def __init__(
        self,
        message: str,
        operation: str | None = None,
        server_name: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, details)
        self.operation = operation
        self.server_name = server_name

    def get_troubleshooting_message(self) -> str:
        """Get troubleshooting guidance for operation errors."""
        tips = ["Troubleshooting:"]

        if self.operation == "tool_call":
            tips.extend(
                [
                    "  1. Verify the tool name is correct",
                    "  2. Check that all required arguments are provided",
                    "  3. Ensure argument types match the tool's input schema",
                    "  4. Try listing tools to see available options",
                ]
            )
        elif self.operation == "resource_read":
            tips.extend(
                [
                    "  1. Verify the resource URI is correct",
                    "  2. Check that the resource exists on the server",
                    "  3. Ensure you have permission to access the resource",
                    "  4. Try listing resources to see available options",
                ]
            )
        elif self.operation == "prompt_get":
            tips.extend(
                [
                    "  1. Verify the prompt name is correct",
                    "  2. Check that all required arguments are provided",
                    "  3. Ensure argument types match the prompt's schema",
                    "  4. Try listing prompts to see available options",
                ]
            )
        else:
            tips.extend(
                [
                    "  1. Check the operation parameters",
                    "  2. Verify the server is still connected",
                    "  3. Try reconnecting to the server",
                ]
            )

        tips.append("  5. Run with --verbose for detailed error information")

        return "\n".join(tips)


class MCPTransportError(MCPError):
    """Error in MCP transport layer."""

    def __init__(
        self, message: str, transport_type: str | None = None, details: dict[str, Any] | None = None
    ):
        super().__init__(message, details)
        self.transport_type = transport_type

    def get_troubleshooting_message(self) -> str:
        """Get troubleshooting guidance for transport errors."""
        tips = ["Troubleshooting:"]

        if self.transport_type == "stdio":
            tips.extend(
                [
                    "  1. Check that the process launched successfully",
                    "  2. Verify stdin/stdout are not being used by other processes",
                    "  3. Ensure the process hasn't crashed or exited unexpectedly",
                    "  4. Check process logs for error messages",
                ]
            )
        elif self.transport_type == "sse":
            tips.extend(
                [
                    "  1. Verify the HTTP connection is stable",
                    "  2. Check for network timeouts or interruptions",
                    "  3. Ensure the server is sending valid SSE events",
                    "  4. Try increasing the timeout setting",
                ]
            )
        elif self.transport_type == "websocket":
            tips.extend(
                [
                    "  1. Verify the WebSocket connection is stable",
                    "  2. Check for network interruptions",
                    "  3. Ensure the server is responding to ping/pong",
                    "  4. Try reconnecting to the server",
                ]
            )
        else:
            tips.extend(
                ["  1. Check the transport configuration", "  2. Verify network connectivity"]
            )

        tips.append("  5. Run with --verbose for detailed transport logs")

        return "\n".join(tips)


class MCPTimeoutError(MCPError):
    """Operation timed out."""

    def __init__(
        self,
        message: str,
        operation: str | None = None,
        timeout_seconds: int | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, details)
        self.operation = operation
        self.timeout_seconds = timeout_seconds

    def get_troubleshooting_message(self) -> str:
        """Get troubleshooting guidance for timeout errors."""
        tips = [
            "Troubleshooting:",
            "  1. The operation took longer than expected",
            "  2. Try increasing the timeout setting in your configuration",
            "  3. Check if the server is responding slowly",
            "  4. Verify your network connection is stable",
        ]

        if self.timeout_seconds:
            tips.append(f"  5. Current timeout: {self.timeout_seconds} seconds")

        tips.append("  6. Consider retrying the operation")

        return "\n".join(tips)


def format_mcp_error(error: MCPError, verbose: bool = False) -> str:
    """Format an MCP error for display to the user.

    Args:
        error: The MCP error to format
        verbose: Whether to include detailed information

    Returns:
        Formatted error message
    """
    lines = [f"Error: {error!s}"]

    # Add error-specific details
    if isinstance(error, MCPConnectionError):
        if error.server_name:
            lines.append(f"Server: {error.server_name}")
        if error.transport_type:
            lines.append(f"Transport: {error.transport_type}")

    elif isinstance(error, MCPConfigurationError):
        if error.server_name:
            lines.append(f"Server: {error.server_name}")
        if error.config_field:
            lines.append(f"Field: {error.config_field}")

    elif isinstance(error, MCPOperationError):
        if error.operation:
            lines.append(f"Operation: {error.operation}")
        if error.server_name:
            lines.append(f"Server: {error.server_name}")

    elif isinstance(error, MCPTransportError):
        if error.transport_type:
            lines.append(f"Transport: {error.transport_type}")

    elif isinstance(error, MCPTimeoutError):
        if error.operation:
            lines.append(f"Operation: {error.operation}")
        if error.timeout_seconds:
            lines.append(f"Timeout: {error.timeout_seconds}s")

    # Add details if verbose
    if verbose and error.details:
        lines.append("\nDetails:")
        for key, value in error.details.items():
            lines.append(f"  {key}: {value}")

    # Add troubleshooting guidance
    lines.append("")
    lines.append(error.get_troubleshooting_message())

    return "\n".join(lines)
