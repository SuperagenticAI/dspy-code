"""
MCP Client Manager for DSPy Code.

Manages MCP client connections and operations across multiple servers.
"""

from contextlib import AsyncExitStack
from typing import Any

from mcp import types
from mcp.client.session import ClientSession

from ..core.config import ConfigManager
from .config import MCPServerConfig
from .exceptions import (
    MCPConfigurationError,
    MCPConnectionError,
    MCPOperationError,
)
from .session_wrapper import MCPSessionWrapper
from .transports.factory import MCPTransportFactory


class MCPClientManager:
    """
    Manages MCP client connections and operations.

    Handles connection lifecycle, session management, and routing of
    operations to appropriate servers.
    """

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the MCP client manager.

        Args:
            config_manager: DSPy Code configuration manager
        """
        self.config_manager = config_manager
        self.sessions: dict[str, MCPSessionWrapper] = {}
        self.server_configs: dict[str, MCPServerConfig] = {}
        self._exit_stack: AsyncExitStack | None = None
        self._load_server_configs()

    def _load_server_configs(self) -> None:
        """Load MCP server configurations from project config."""
        mcp_servers = self.config_manager.get_mcp_servers()

        for server_name, server_data in mcp_servers.items():
            try:
                config = MCPServerConfig.from_dict(server_data)
                config.validate()
                self.server_configs[server_name] = config
            except Exception as e:
                # Log warning but don't fail - skip invalid configs
                print(f"Warning: Invalid MCP server config '{server_name}': {e}")

    async def add_server(self, config: MCPServerConfig) -> None:
        """
        Add a new MCP server configuration.

        Args:
            config: Server configuration to add

        Raises:
            MCPConfigurationError: If configuration is invalid
        """
        # Validate configuration
        try:
            config.validate()
        except Exception as e:
            raise MCPConfigurationError(
                f"Invalid server configuration: {e}",
                server_name=config.name,
                details={"error": str(e)},
            )

        # Store in memory
        self.server_configs[config.name] = config

        # Persist to config file
        self.config_manager.add_mcp_server(config.name, config.to_dict())

    async def remove_server(self, server_name: str) -> None:
        """
        Remove an MCP server configuration.

        Args:
            server_name: Name of server to remove

        Raises:
            MCPConfigurationError: If server doesn't exist
        """
        if server_name not in self.server_configs:
            raise MCPConfigurationError(
                f"Server '{server_name}' not found", server_name=server_name
            )

        # Disconnect if connected
        if server_name in self.sessions:
            await self.disconnect(server_name)

        # Remove from memory
        del self.server_configs[server_name]

        # Remove from config file
        self.config_manager.remove_mcp_server(server_name)

    async def list_servers(self) -> list[dict[str, Any]]:
        """
        List all configured servers with their status.

        Returns:
            List of server information dictionaries
        """
        servers = []

        for server_name, config in self.server_configs.items():
            server_info = {
                "name": server_name,
                "description": config.description,
                "transport_type": config.transport.type,
                "enabled": config.enabled,
                "auto_connect": config.auto_connect,
                "connected": server_name in self.sessions,
            }

            # Add status if connected
            if server_name in self.sessions:
                session = self.sessions[server_name]
                server_info["status"] = session.get_status()

            servers.append(server_info)

        return servers

    async def connect(self, server_name: str) -> MCPSessionWrapper:
        """
        Connect to an MCP server.

        Args:
            server_name: Name of server to connect to

        Returns:
            MCPSessionWrapper for the connected session

        Raises:
            MCPConfigurationError: If server not configured
            MCPConnectionError: If connection fails
        """
        # Check if server is configured
        if server_name not in self.server_configs:
            raise MCPConfigurationError(
                f"Server '{server_name}' not configured", server_name=server_name
            )

        # Check if already connected
        if server_name in self.sessions:
            return self.sessions[server_name]

        config = self.server_configs[server_name]

        # Check if server is enabled
        if not config.enabled:
            raise MCPConnectionError(
                f"Server '{server_name}' is disabled",
                server_name=server_name,
                transport_type=config.transport.type,
            )

        try:
            # Create exit stack if not exists
            if self._exit_stack is None:
                self._exit_stack = AsyncExitStack()
                await self._exit_stack.__aenter__()

            # Create transport
            transport_cm = MCPTransportFactory.create_transport(
                config.transport, timeout=config.timeout_seconds
            )

            # Enter transport context
            read_stream, write_stream = await self._exit_stack.enter_async_context(transport_cm)

            # Create client session
            session = ClientSession(read_stream, write_stream)
            session_cm = session.__aenter__()
            await self._exit_stack.enter_async_context(session_cm)

            # Wrap session
            wrapper = MCPSessionWrapper(server_name, config, session)

            # Initialize session
            await wrapper.initialize()

            # Store session
            self.sessions[server_name] = wrapper

            return wrapper

        except Exception as e:
            raise MCPConnectionError(
                f"Failed to connect to server '{server_name}': {e}",
                server_name=server_name,
                transport_type=config.transport.type,
                details={"error": str(e), "error_type": type(e).__name__},
            )

    async def disconnect(self, server_name: str) -> None:
        """
        Disconnect from an MCP server.

        Args:
            server_name: Name of server to disconnect from
        """
        if server_name in self.sessions:
            session = self.sessions[server_name]
            await session.close()
            del self.sessions[server_name]

    async def get_session(self, server_name: str) -> MCPSessionWrapper | None:
        """
        Get active session for a server.

        Args:
            server_name: Name of server

        Returns:
            MCPSessionWrapper if connected, None otherwise
        """
        return self.sessions.get(server_name)

    async def list_tools(self, server_name: str | None = None) -> dict[str, list[types.Tool]]:
        """
        List tools from one or all connected servers.

        Args:
            server_name: Optional server name to filter by

        Returns:
            Dictionary mapping server names to tool lists

        Raises:
            MCPOperationError: If listing tools fails
        """
        results: dict[str, list[types.Tool]] = {}

        if server_name:
            # List tools from specific server
            session = await self._get_connected_session(server_name)
            tools = await session.list_tools()
            results[server_name] = tools
        else:
            # List tools from all connected servers
            for name, session in self.sessions.items():
                try:
                    tools = await session.list_tools()
                    results[name] = tools
                except Exception as e:
                    print(f"Warning: Failed to list tools from '{name}': {e}")

        return results

    async def call_tool(
        self, server_name: str, tool_name: str, arguments: dict[str, Any] | None = None
    ) -> types.CallToolResult:
        """
        Invoke a tool on a connected server.

        Args:
            server_name: Name of server
            tool_name: Name of tool to call
            arguments: Tool arguments

        Returns:
            CallToolResult with tool output

        Raises:
            MCPOperationError: If tool call fails
        """
        session = await self._get_connected_session(server_name)
        return await session.call_tool(tool_name, arguments)

    async def list_resources(
        self, server_name: str | None = None
    ) -> dict[str, list[types.Resource]]:
        """
        List resources from one or all connected servers.

        Args:
            server_name: Optional server name to filter by

        Returns:
            Dictionary mapping server names to resource lists
        """
        results: dict[str, list[types.Resource]] = {}

        if server_name:
            session = await self._get_connected_session(server_name)
            resources = await session.list_resources()
            results[server_name] = resources
        else:
            for name, session in self.sessions.items():
                try:
                    resources = await session.list_resources()
                    results[name] = resources
                except Exception as e:
                    print(f"Warning: Failed to list resources from '{name}': {e}")

        return results

    async def read_resource(self, server_name: str, uri: str) -> types.ReadResourceResult:
        """
        Read a resource from a connected server.

        Args:
            server_name: Name of server
            uri: Resource URI

        Returns:
            ReadResourceResult with resource content
        """
        session = await self._get_connected_session(server_name)
        return await session.read_resource(uri)

    async def list_prompts(self, server_name: str | None = None) -> dict[str, list[types.Prompt]]:
        """
        List prompts from one or all connected servers.

        Args:
            server_name: Optional server name to filter by

        Returns:
            Dictionary mapping server names to prompt lists
        """
        results: dict[str, list[types.Prompt]] = {}

        if server_name:
            session = await self._get_connected_session(server_name)
            prompts = await session.list_prompts()
            results[server_name] = prompts
        else:
            for name, session in self.sessions.items():
                try:
                    prompts = await session.list_prompts()
                    results[name] = prompts
                except Exception as e:
                    print(f"Warning: Failed to list prompts from '{name}': {e}")

        return results

    async def get_prompt(
        self, server_name: str, prompt_name: str, arguments: dict[str, str] | None = None
    ) -> types.GetPromptResult:
        """
        Get a prompt from a connected server.

        Args:
            server_name: Name of server
            prompt_name: Name of prompt
            arguments: Optional prompt arguments

        Returns:
            GetPromptResult with prompt messages
        """
        session = await self._get_connected_session(server_name)
        return await session.get_prompt(prompt_name, arguments)

    async def cleanup(self) -> None:
        """Cleanup all connections and resources."""
        # Close all sessions
        for server_name in list(self.sessions.keys()):
            await self.disconnect(server_name)

        # Cleanup exit stack
        if self._exit_stack:
            await self._exit_stack.__aexit__(None, None, None)
            self._exit_stack = None

    async def _get_connected_session(self, server_name: str) -> MCPSessionWrapper:
        """
        Get a connected session, raising error if not connected.

        Args:
            server_name: Name of server

        Returns:
            MCPSessionWrapper for the server

        Raises:
            MCPOperationError: If server is not connected
        """
        session = self.sessions.get(server_name)
        if not session:
            raise MCPOperationError(
                f"Server '{server_name}' is not connected. Use 'mcp connect {server_name}' first.",
                operation="get_session",
                server_name=server_name,
            )
        return session
