"""
MCP configuration models for DSPy Code.

Defines configuration structures for MCP servers and transport settings.
"""

import os
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class MCPTransportConfig:
    """Transport-specific configuration for MCP connections."""

    type: str  # "stdio", "sse", "websocket"

    # Stdio-specific fields
    command: str | None = None
    args: list[str] | None = None
    env: dict[str, str] | None = None

    # HTTP/WebSocket-specific fields
    url: str | None = None
    headers: dict[str, str] | None = None

    # Authentication fields
    auth_type: str | None = None  # "bearer", "basic", "oauth"
    auth_token: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MCPTransportConfig":
        """Create from dictionary."""
        return cls(**data)

    def validate(self) -> None:
        """Validate transport-specific required fields."""
        if self.type not in ["stdio", "sse", "websocket"]:
            raise ValueError(
                f"Invalid transport type: {self.type}. Must be 'stdio', 'sse', or 'websocket'"
            )

        if self.type == "stdio":
            if not self.command:
                raise ValueError("Stdio transport requires 'command' field")

        elif self.type in ["sse", "websocket"]:
            if not self.url:
                raise ValueError(f"{self.type.upper()} transport requires 'url' field")

    def resolve_env_vars(self) -> "MCPTransportConfig":
        """Resolve environment variable references in configuration.

        Replaces ${VAR_NAME} patterns with actual environment variable values.
        """
        resolved = MCPTransportConfig(
            type=self.type,
            command=self.command,
            args=self.args[:] if self.args else None,
            env=self.env.copy() if self.env else None,
            url=self.url,
            headers=self.headers.copy() if self.headers else None,
            auth_type=self.auth_type,
            auth_token=self.auth_token,
        )

        # Resolve environment variables in env dict
        if resolved.env:
            for key, value in resolved.env.items():
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    env_var = value[2:-1]
                    resolved.env[key] = os.getenv(env_var, value)

        # Resolve environment variables in headers
        if resolved.headers:
            for key, value in resolved.headers.items():
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    env_var = value[2:-1]
                    resolved.headers[key] = os.getenv(env_var, value)

        # Resolve environment variables in auth_token
        if (
            resolved.auth_token
            and resolved.auth_token.startswith("${")
            and resolved.auth_token.endswith("}")
        ):
            env_var = resolved.auth_token[2:-1]
            resolved.auth_token = os.getenv(env_var, resolved.auth_token)

        # Resolve environment variables in URL
        if resolved.url and "${" in resolved.url:
            import re

            def replace_env_var(match):
                env_var = match.group(1)
                return os.getenv(env_var, match.group(0))

            resolved.url = re.sub(r"\$\{([^}]+)\}", replace_env_var, resolved.url)

        return resolved


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""

    name: str
    description: str | None = None
    transport: MCPTransportConfig = field(default_factory=lambda: MCPTransportConfig(type="stdio"))
    enabled: bool = True
    auto_connect: bool = False
    timeout_seconds: int = 30
    retry_attempts: int = 3

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MCPServerConfig":
        """Create from dictionary."""
        # Extract transport data and create MCPTransportConfig
        transport_data = data.pop("transport", {})
        if isinstance(transport_data, dict):
            transport = MCPTransportConfig.from_dict(transport_data)
        else:
            transport = transport_data

        return cls(transport=transport, **data)

    def validate(self) -> None:
        """Validate server configuration."""
        if not self.name:
            raise ValueError("Server name is required")

        if self.timeout_seconds <= 0:
            raise ValueError("Timeout must be positive")

        if self.retry_attempts < 0:
            raise ValueError("Retry attempts cannot be negative")

        # Validate transport configuration
        self.transport.validate()

    def resolve_env_vars(self) -> "MCPServerConfig":
        """Resolve environment variable references in configuration."""
        resolved_transport = self.transport.resolve_env_vars()

        return MCPServerConfig(
            name=self.name,
            description=self.description,
            transport=resolved_transport,
            enabled=self.enabled,
            auto_connect=self.auto_connect,
            timeout_seconds=self.timeout_seconds,
            retry_attempts=self.retry_attempts,
        )
