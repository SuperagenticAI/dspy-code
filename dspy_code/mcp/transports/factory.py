"""
Transport factory for creating MCP transport instances.

Provides a unified interface for creating different transport types.
"""

from contextlib import asynccontextmanager
from typing import Any

from ..config import MCPTransportConfig
from ..exceptions import MCPTransportError
from .sse_transport import create_sse_transport
from .stdio_transport import create_stdio_transport
from .websocket_transport import create_websocket_transport


class MCPTransportFactory:
    """Factory for creating MCP transport instances based on configuration."""

    @staticmethod
    @asynccontextmanager
    async def create_transport(config: MCPTransportConfig, **kwargs: Any):
        """
        Create transport streams based on configuration.

        This is an async context manager that yields (read_stream, write_stream).

        Args:
            config: Transport configuration specifying type and settings
            **kwargs: Additional transport-specific options

        Yields:
            Tuple of (read_stream, write_stream) for MCP communication

        Raises:
            MCPTransportError: If transport type is unsupported or creation fails

        Example:
            async with MCPTransportFactory.create_transport(config) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
        """
        # Validate configuration
        config.validate()

        # Route to appropriate transport creator based on type
        if config.type == "stdio":
            transport_cm = create_stdio_transport(config)
        elif config.type == "sse":
            timeout = kwargs.get("timeout", 5.0)
            sse_read_timeout = kwargs.get("sse_read_timeout", 300.0)
            transport_cm = create_sse_transport(config, timeout, sse_read_timeout)
        elif config.type == "websocket":
            transport_cm = create_websocket_transport(config)
        else:
            raise MCPTransportError(
                f"Unsupported transport type: {config.type}",
                transport_type=config.type,
                details={"supported_types": ["stdio", "sse", "websocket"]},
            )

        # Use the transport context manager
        async with transport_cm as (read_stream, write_stream):
            yield read_stream, write_stream
