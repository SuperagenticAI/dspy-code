"""
SSE (Server-Sent Events) transport implementation for MCP connections.

Handles remote MCP servers accessible via HTTP with Server-Sent Events.
"""

from typing import Any

import httpx
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from mcp.client.sse import sse_client
from mcp.shared.message import SessionMessage

from ..config import MCPTransportConfig
from ..exceptions import MCPTransportError


async def create_sse_transport(
    config: MCPTransportConfig,
    timeout: float = 5.0,
    sse_read_timeout: float = 300.0,
) -> tuple[
    MemoryObjectReceiveStream[SessionMessage | Exception], MemoryObjectSendStream[SessionMessage]
]:
    """
    Create SSE transport streams for MCP communication.

    Args:
        config: Transport configuration with SSE-specific settings
        timeout: HTTP timeout for regular operations (default: 5 seconds)
        sse_read_timeout: Timeout for SSE read operations (default: 300 seconds)

    Returns:
        Tuple of (read_stream, write_stream) for MCP communication

    Raises:
        MCPTransportError: If transport creation fails
    """
    if not config.url:
        raise MCPTransportError(
            "SSE transport requires 'url' field",
            transport_type="sse",
            details={"config": config.to_dict()},
        )

    # Resolve environment variables in configuration
    resolved_config = config.resolve_env_vars()

    # Prepare headers
    headers: dict[str, Any] | None = None
    if resolved_config.headers:
        headers = resolved_config.headers.copy()

    # Prepare authentication
    auth: httpx.Auth | None = None
    if resolved_config.auth_type and resolved_config.auth_token:
        if resolved_config.auth_type == "bearer":
            # Add Bearer token to headers
            if headers is None:
                headers = {}
            headers["Authorization"] = f"Bearer {resolved_config.auth_token}"
        elif resolved_config.auth_type == "basic":
            # Use httpx BasicAuth
            # Assuming auth_token is in format "username:password"
            if ":" in resolved_config.auth_token:
                username, password = resolved_config.auth_token.split(":", 1)
                auth = httpx.BasicAuth(username, password)
            else:
                raise MCPTransportError(
                    "Basic auth requires token in format 'username:password'",
                    transport_type="sse",
                    details={"auth_type": resolved_config.auth_type},
                )

    try:
        # Create the SSE client context manager
        # Note: This returns an async context manager, not the streams directly
        # The caller needs to use it with async with
        return sse_client(
            url=resolved_config.url,
            headers=headers,
            timeout=timeout,
            sse_read_timeout=sse_read_timeout,
            auth=auth,
        )
    except httpx.HTTPError as e:
        raise MCPTransportError(
            f"HTTP error connecting to SSE endpoint: {e}",
            transport_type="sse",
            details={"url": resolved_config.url, "error": str(e), "error_type": type(e).__name__},
        )
    except Exception as e:
        raise MCPTransportError(
            f"Failed to create SSE transport: {e}",
            transport_type="sse",
            details={"url": resolved_config.url, "error": str(e), "error_type": type(e).__name__},
        )
