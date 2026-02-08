# MCP API Reference

This page documents the Model Context Protocol (MCP) integration modules.

## Client Manager

::: dspy_code.mcp.client_manager
    options:
      members:
        - MCPClientManager

## Session Wrapper

::: dspy_code.mcp.session_wrapper
    options:
      members:
        - MCPSessionWrapper

## Configuration

::: dspy_code.mcp.config
    options:
      members:
        - MCPServerConfig
        - MCPTransportConfig

## Retry Controller

::: dspy_code.mcp.retry
    options:
      members:
        - RetryController
        - RetryConfig

## Utilities

::: dspy_code.mcp.utils
    options:
      members:
        - is_closed_connection_error
        - format_mcp_error_message

## Exceptions

::: dspy_code.mcp.exceptions
    options:
      members:
        - MCPError
        - MCPConnectionError
        - MCPConfigurationError
        - MCPOperationError
        - MCPTimeoutError
        - MCPTransportError
