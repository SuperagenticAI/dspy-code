"""
Utility functions for MCP client operations.
"""

from typing import Any


def is_closed_connection_error(error: Exception) -> bool:
    """
    Check if an exception indicates a closed connection.
    
    This helper consolidates the logic for detecting closed connection errors
    across different exception types and error formats.
    
    Args:
        error: The exception to check
        
    Returns:
        True if the error indicates a closed connection, False otherwise
    """
    # Indicators that suggest a closed connection
    closed_indicators = ["closed", "closedresourceerror"]
    
    # Check exception type name
    error_type = type(error).__name__.lower()
    if any(indicator in error_type for indicator in closed_indicators):
        return True
    
    # Check exception message
    error_str = str(error).lower()
    if any(indicator in error_str for indicator in closed_indicators):
        return True
    
    # Check details dict for MCPOperationError and similar
    if hasattr(error, "details") and isinstance(error.details, dict):
        details_error_type = str(error.details.get("error_type", "")).lower()
        if any(indicator in details_error_type for indicator in closed_indicators):
            return True
    
    # Check the cause chain
    if error.__cause__ is not None:
        cause_type = type(error.__cause__).__name__.lower()
        if any(indicator in cause_type for indicator in closed_indicators):
            return True
    
    return False


def format_mcp_error_message(
    operation: str,
    server_name: str,
    error: Exception,
    include_troubleshooting: bool = True
) -> str:
    """
    Format a user-friendly error message for MCP operations.
    
    Args:
        operation: The operation that failed (e.g., "connect", "list_tools")
        server_name: Name of the MCP server
        error: The exception that occurred
        include_troubleshooting: Whether to include troubleshooting tips
        
    Returns:
        Formatted error message string
    """
    message = f"MCP {operation} failed for server '{server_name}': {error}"
    
    if include_troubleshooting:
        tips = []
        
        if is_closed_connection_error(error):
            tips.append("The connection was closed. Try reconnecting with /mcp-connect")
        
        error_str = str(error).lower()
        if "timeout" in error_str:
            tips.append("The operation timed out. Check if the server is running")
        if "refused" in error_str or "econnrefused" in error_str:
            tips.append("Connection refused. Verify the server is running and accessible")
        if "not found" in error_str:
            tips.append("Server not found. Check the server configuration in dspy_config.yaml")
        
        if tips:
            message += "\n\nTroubleshooting tips:\n" + "\n".join(f"  • {tip}" for tip in tips)
    
    return message
