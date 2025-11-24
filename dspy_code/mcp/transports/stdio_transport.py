"""
Stdio transport implementation for MCP connections.

Handles local MCP server processes that communicate via standard input/output.
"""

import sys

from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.shared.message import SessionMessage

from ..config import MCPTransportConfig
from ..exceptions import MCPTransportError


async def create_stdio_transport(
    config: MCPTransportConfig,
) -> tuple[
    MemoryObjectReceiveStream[SessionMessage | Exception], MemoryObjectSendStream[SessionMessage]
]:
    """
    Create stdio transport streams for MCP communication.

    Args:
        config: Transport configuration with stdio-specific settings

    Returns:
        Tuple of (read_stream, write_stream) for MCP communication

    Raises:
        MCPTransportError: If transport creation fails
    """
    if not config.command:
        raise MCPTransportError(
            "Stdio transport requires 'command' field",
            transport_type="stdio",
            details={"config": config.to_dict()},
        )

    # Resolve environment variables in configuration
    resolved_config = config.resolve_env_vars()

    # Build server parameters
    server_params = StdioServerParameters(
        command=resolved_config.command,
        args=resolved_config.args or [],
        env=resolved_config.env,
    )

    try:
        # Create the stdio client context manager
        # Note: This returns an async context manager, not the streams directly
        # The caller needs to use it with async with
        return stdio_client(server_params, errlog=sys.stderr)
    except OSError as e:
        raise MCPTransportError(
            f"Failed to launch stdio process: {e}",
            transport_type="stdio",
            details={
                "command": resolved_config.command,
                "args": resolved_config.args,
                "error": str(e),
                "errno": e.errno if hasattr(e, "errno") else None,
            },
        )
    except Exception as e:
        raise MCPTransportError(
            f"Failed to create stdio transport: {e}",
            transport_type="stdio",
            details={
                "command": resolved_config.command,
                "args": resolved_config.args,
                "error": str(e),
                "error_type": type(e).__name__,
            },
        )
