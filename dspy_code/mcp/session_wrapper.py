"""
MCP Session Wrapper for DSPy Code.

Wraps the MCP SDK's ClientSession with DSPy Code-specific functionality.
"""

from collections.abc import Callable
from datetime import datetime
from typing import Any

from mcp import types
from mcp.client.session import ClientSession
from pydantic import AnyUrl

from .config import MCPServerConfig
from .exceptions import MCPOperationError, MCPTimeoutError


class MCPSessionWrapper:
    """
    Wraps MCP ClientSession with DSPy Code-specific functionality.

    Provides simplified API for common operations, progress tracking,
    error translation, and connection status management.
    """

    def __init__(self, server_name: str, config: MCPServerConfig, session: ClientSession):
        """
        Initialize the session wrapper.

        Args:
            server_name: Name of the MCP server
            config: Server configuration
            session: MCP ClientSession instance
        """
        self.server_name = server_name
        self.config = config
        self.session = session
        self.capabilities: types.ServerCapabilities | None = None
        self.connected_at: datetime = datetime.now()
        self.last_activity: datetime = datetime.now()
        self._initialized = False

    async def initialize(self) -> types.InitializeResult:
        """
        Initialize the MCP session with handshake.

        Returns:
            InitializeResult with server capabilities

        Raises:
            MCPOperationError: If initialization fails
        """
        try:
            result = await self.session.initialize()
            self.capabilities = result.capabilities
            self._initialized = True
            self.last_activity = datetime.now()
            return result
        except Exception as e:
            raise MCPOperationError(
                f"Failed to initialize session: {e}",
                operation="initialize",
                server_name=self.server_name,
                details={"error": str(e), "error_type": type(e).__name__},
            )

    async def list_tools(self) -> list[types.Tool]:
        """
        List available tools from the server.

        Returns:
            List of Tool objects

        Raises:
            MCPOperationError: If listing tools fails
        """
        self._check_initialized()

        try:
            result = await self.session.list_tools()
            self.last_activity = datetime.now()
            return result.tools
        except Exception as e:
            raise MCPOperationError(
                f"Failed to list tools: {e}",
                operation="list_tools",
                server_name=self.server_name,
                details={"error": str(e), "error_type": type(e).__name__},
            )

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
        progress_callback: Callable[[float, float | None], None] | None = None,
    ) -> types.CallToolResult:
        """
        Call a tool with optional progress tracking.

        Args:
            name: Tool name
            arguments: Tool arguments
            progress_callback: Optional callback for progress updates (progress, total)

        Returns:
            CallToolResult with tool output

        Raises:
            MCPOperationError: If tool call fails
            MCPTimeoutError: If tool call times out
        """
        self._check_initialized()

        # Wrap progress callback to match MCP SDK signature
        mcp_progress_callback = None
        if progress_callback:

            async def _progress_wrapper(
                progress_token: str | int, progress: float, total: float | None = None
            ):
                progress_callback(progress, total)

            mcp_progress_callback = _progress_wrapper

        try:
            from datetime import timedelta

            timeout = timedelta(seconds=self.config.timeout_seconds)

            result = await self.session.call_tool(
                name=name,
                arguments=arguments,
                read_timeout_seconds=timeout,
                progress_callback=mcp_progress_callback,
            )
            self.last_activity = datetime.now()
            return result
        except TimeoutError as e:
            raise MCPTimeoutError(
                f"Tool call timed out: {name}",
                operation="tool_call",
                timeout_seconds=self.config.timeout_seconds,
                details={"tool_name": name, "arguments": arguments, "error": str(e)},
            )
        except Exception as e:
            raise MCPOperationError(
                f"Failed to call tool '{name}': {e}",
                operation="tool_call",
                server_name=self.server_name,
                details={
                    "tool_name": name,
                    "arguments": arguments,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )

    async def list_resources(self) -> list[types.Resource]:
        """
        List available resources from the server.

        Returns:
            List of Resource objects

        Raises:
            MCPOperationError: If listing resources fails
        """
        self._check_initialized()

        try:
            result = await self.session.list_resources()
            self.last_activity = datetime.now()
            return result.resources
        except Exception as e:
            raise MCPOperationError(
                f"Failed to list resources: {e}",
                operation="list_resources",
                server_name=self.server_name,
                details={"error": str(e), "error_type": type(e).__name__},
            )

    async def read_resource(self, uri: str) -> types.ReadResourceResult:
        """
        Read a resource from the server.

        Args:
            uri: Resource URI

        Returns:
            ReadResourceResult with resource content

        Raises:
            MCPOperationError: If reading resource fails
        """
        self._check_initialized()

        try:
            # Convert string URI to AnyUrl
            any_url = AnyUrl(uri)
            result = await self.session.read_resource(any_url)
            self.last_activity = datetime.now()
            return result
        except Exception as e:
            raise MCPOperationError(
                f"Failed to read resource '{uri}': {e}",
                operation="resource_read",
                server_name=self.server_name,
                details={"uri": uri, "error": str(e), "error_type": type(e).__name__},
            )

    async def list_resource_templates(self) -> list[types.ResourceTemplate]:
        """
        List available resource templates from the server.

        Returns:
            List of ResourceTemplate objects

        Raises:
            MCPOperationError: If listing templates fails
        """
        self._check_initialized()

        try:
            result = await self.session.list_resource_templates()
            self.last_activity = datetime.now()
            return result.resourceTemplates
        except Exception as e:
            raise MCPOperationError(
                f"Failed to list resource templates: {e}",
                operation="list_resource_templates",
                server_name=self.server_name,
                details={"error": str(e), "error_type": type(e).__name__},
            )

    async def subscribe_resource(self, uri: str) -> types.EmptyResult:
        """
        Subscribe to resource updates.

        Args:
            uri: Resource URI to subscribe to

        Returns:
            EmptyResult

        Raises:
            MCPOperationError: If subscription fails
        """
        self._check_initialized()

        try:
            any_url = AnyUrl(uri)
            result = await self.session.subscribe_resource(any_url)
            self.last_activity = datetime.now()
            return result
        except Exception as e:
            raise MCPOperationError(
                f"Failed to subscribe to resource '{uri}': {e}",
                operation="subscribe_resource",
                server_name=self.server_name,
                details={"uri": uri, "error": str(e), "error_type": type(e).__name__},
            )

    async def unsubscribe_resource(self, uri: str) -> types.EmptyResult:
        """
        Unsubscribe from resource updates.

        Args:
            uri: Resource URI to unsubscribe from

        Returns:
            EmptyResult

        Raises:
            MCPOperationError: If unsubscription fails
        """
        self._check_initialized()

        try:
            any_url = AnyUrl(uri)
            result = await self.session.unsubscribe_resource(any_url)
            self.last_activity = datetime.now()
            return result
        except Exception as e:
            raise MCPOperationError(
                f"Failed to unsubscribe from resource '{uri}': {e}",
                operation="unsubscribe_resource",
                server_name=self.server_name,
                details={"uri": uri, "error": str(e), "error_type": type(e).__name__},
            )

    async def list_prompts(self) -> list[types.Prompt]:
        """
        List available prompts from the server.

        Returns:
            List of Prompt objects

        Raises:
            MCPOperationError: If listing prompts fails
        """
        self._check_initialized()

        try:
            result = await self.session.list_prompts()
            self.last_activity = datetime.now()
            return result.prompts
        except Exception as e:
            raise MCPOperationError(
                f"Failed to list prompts: {e}",
                operation="list_prompts",
                server_name=self.server_name,
                details={"error": str(e), "error_type": type(e).__name__},
            )

    async def get_prompt(
        self, name: str, arguments: dict[str, str] | None = None
    ) -> types.GetPromptResult:
        """
        Get a prompt from the server.

        Args:
            name: Prompt name
            arguments: Optional prompt arguments

        Returns:
            GetPromptResult with prompt messages

        Raises:
            MCPOperationError: If getting prompt fails
        """
        self._check_initialized()

        try:
            result = await self.session.get_prompt(name=name, arguments=arguments)
            self.last_activity = datetime.now()
            return result
        except Exception as e:
            raise MCPOperationError(
                f"Failed to get prompt '{name}': {e}",
                operation="prompt_get",
                server_name=self.server_name,
                details={
                    "prompt_name": name,
                    "arguments": arguments,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )

    async def send_ping(self) -> types.EmptyResult:
        """
        Send a ping to check connection health.

        Returns:
            EmptyResult

        Raises:
            MCPOperationError: If ping fails
        """
        self._check_initialized()

        try:
            result = await self.session.send_ping()
            self.last_activity = datetime.now()
            return result
        except Exception as e:
            raise MCPOperationError(
                f"Failed to ping server: {e}",
                operation="ping",
                server_name=self.server_name,
                details={"error": str(e), "error_type": type(e).__name__},
            )

    async def close(self) -> None:
        """
        Close the session gracefully.

        This should be called when done with the session to clean up resources.
        """
        # The actual session cleanup is handled by the context manager
        # This method is here for explicit cleanup if needed
        self._initialized = False

    def is_connected(self) -> bool:
        """
        Check if session is initialized and connected.

        Returns:
            True if session is connected and initialized
        """
        return self._initialized

    def get_status(self) -> dict[str, Any]:
        """
        Get session status information.

        Returns:
            Dictionary with status information
        """
        return {
            "server_name": self.server_name,
            "connected": self._initialized,
            "connected_at": self.connected_at.isoformat() if self._initialized else None,
            "last_activity": self.last_activity.isoformat() if self._initialized else None,
            "transport_type": self.config.transport.type,
            "capabilities": {
                "tools": self.capabilities.tools is not None if self.capabilities else False,
                "resources": self.capabilities.resources is not None
                if self.capabilities
                else False,
                "prompts": self.capabilities.prompts is not None if self.capabilities else False,
            }
            if self.capabilities
            else None,
        }

    def _check_initialized(self) -> None:
        """
        Check if session is initialized.

        Raises:
            MCPOperationError: If session is not initialized
        """
        if not self._initialized:
            raise MCPOperationError(
                "Session not initialized. Call initialize() first.",
                operation="check_initialized",
                server_name=self.server_name,
            )
