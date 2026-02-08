"""
Tests for MCP utility functions.
"""

import pytest
from hypothesis import given, strategies as st

from dspy_code.mcp.utils import is_closed_connection_error, format_mcp_error_message


class TestIsClosedConnectionError:
    """Tests for is_closed_connection_error helper."""

    # **Feature: dspy-code-improvements, Property 5: Closed Connection Error Detection**
    @given(
        indicator=st.sampled_from(["closed", "closedresourceerror", "Closed", "ClosedResourceError"]),
        prefix=st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=0, max_size=10),
        suffix=st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=0, max_size=10),
    )
    def test_detects_closed_in_exception_message(self, indicator: str, prefix: str, suffix: str):
        """
        Property 5: Closed Connection Error Detection
        
        For any exception with "closed" or "closedresourceerror" in its message,
        the is_closed_connection_error helper SHALL return True.
        
        **Validates: Requirements 3.2**
        """
        message = f"{prefix}{indicator}{suffix}"
        error = Exception(message)
        assert is_closed_connection_error(error) is True

    def test_detects_closed_in_exception_type_name(self):
        """Test detection via exception type name."""
        class ClosedResourceError(Exception):
            pass
        
        error = ClosedResourceError("Some error")
        assert is_closed_connection_error(error) is True

    def test_detects_closed_in_details_dict(self):
        """Test detection via details dict (MCPOperationError style)."""
        class ErrorWithDetails(Exception):
            def __init__(self, message, details):
                super().__init__(message)
                self.details = details
        
        error = ErrorWithDetails("Operation failed", {"error_type": "ClosedResourceError"})
        assert is_closed_connection_error(error) is True

    def test_detects_closed_in_cause(self):
        """Test detection via exception cause chain."""
        class ClosedError(Exception):
            pass
        
        cause = ClosedError("Connection closed")
        error = Exception("Wrapper error")
        error.__cause__ = cause
        
        assert is_closed_connection_error(error) is True

    def test_returns_false_for_unrelated_errors(self):
        """Test that unrelated errors return False."""
        error = ValueError("Some value error")
        assert is_closed_connection_error(error) is False
        
        error = ConnectionError("Connection refused")
        assert is_closed_connection_error(error) is False
        
        error = TimeoutError("Operation timed out")
        assert is_closed_connection_error(error) is False


class TestFormatMcpErrorMessage:
    """Tests for format_mcp_error_message helper."""

    def test_basic_formatting(self):
        """Test basic error message formatting."""
        error = Exception("Something went wrong")
        message = format_mcp_error_message("connect", "test-server", error, include_troubleshooting=False)
        
        assert "connect" in message
        assert "test-server" in message
        assert "Something went wrong" in message

    def test_includes_troubleshooting_for_closed_connection(self):
        """Test troubleshooting tips for closed connections."""
        error = Exception("Connection closed unexpectedly")
        message = format_mcp_error_message("list_tools", "my-server", error)
        
        assert "reconnecting" in message.lower() or "reconnect" in message.lower()

    def test_includes_troubleshooting_for_timeout(self):
        """Test troubleshooting tips for timeouts."""
        error = Exception("Operation timeout after 30s")
        message = format_mcp_error_message("call_tool", "slow-server", error)
        
        assert "timeout" in message.lower()

    def test_includes_troubleshooting_for_connection_refused(self):
        """Test troubleshooting tips for connection refused."""
        error = Exception("Connection refused (ECONNREFUSED)")
        message = format_mcp_error_message("connect", "offline-server", error)
        
        assert "refused" in message.lower()
