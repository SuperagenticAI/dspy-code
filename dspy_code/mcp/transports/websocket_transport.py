"""
WebSocket transport implementation for MCP connections.

Handles remote MCP servers that require bidirectional real-time communication.
"""

from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream

try:
    from mcp.client.websocket import websocket_client

    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False

from mcp.shared.message import SessionMessage

from ..config import MCPTransportConfig
from ..exceptions import MCPTransportError


async def create_websocket_transport(
    config: MCPTransportConfig,
) -> tuple[
    MemoryObjectReceiveStream[SessionMessage | Exception], MemoryObjectSendStream[SessionMessage]
]:
    """
    Create WebSocket transport streams for MCP communication.

    Args:
        config: Transport configuration with WebSocket-specific settings

    Returns:
        Tuple of (read_stream, write_stream) for MCP communication

    Raises:
        MCPTransportError: If transport creation fails or websockets not installed
    """
    if not WEBSOCKET_AVAILABLE:
        raise MCPTransportError(
            "WebSocket transport requires 'websockets' package. "
            "Install with: pip install dspy-cli[mcp-ws]",
            transport_type="websocket",
            details={"missing_package": "websockets"},
        )

    if not config.url:
        raise MCPTransportError(
            "WebSocket transport requires 'url' field",
            transport_type="websocket",
            details={"config": config.to_dict()},
        )

    # Resolve environment variables in configuration
    resolved_config = config.resolve_env_vars()

    # Validate WebSocket URL
    if not resolved_config.url.startswith(("ws://", "wss://")):
        raise MCPTransportError(
            f"WebSocket URL must start with 'ws://' or 'wss://': {resolved_config.url}",
            transport_type="websocket",
            details={"url": resolved_config.url},
        )

    try:
        # Create the WebSocket client context manager
        # Note: This returns an async context manager, not the streams directly
        # The caller needs to use it with async with
        return websocket_client(url=resolved_config.url)
    except Exception as e:
        raise MCPTransportError(
            f"Failed to create WebSocket transport: {e}",
            transport_type="websocket",
            details={"url": resolved_config.url, "error": str(e), "error_type": type(e).__name__},
        )
