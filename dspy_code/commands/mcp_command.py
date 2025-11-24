"""
MCP command handlers for DSPy Code.

Provides CLI commands for managing MCP server connections and operations.
"""

import asyncio
import json

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..core.config import ConfigManager
from ..mcp import (
    MCPClientManager,
    MCPError,
    MCPServerConfig,
    MCPTransportConfig,
)
from ..mcp.exceptions import format_mcp_error

console = Console()


def run_async(coro):
    """Helper to run async functions in sync context."""
    return asyncio.run(coro)


def display_server_table(servers: list) -> None:
    """Display servers in a formatted table."""
    table = Table(title="MCP Servers")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Transport", style="yellow")
    table.add_column("Status", style="green")
    table.add_column("Enabled", style="blue")

    for server in servers:
        status = "🟢 Connected" if server["connected"] else "⚪ Disconnected"
        enabled = "✓" if server["enabled"] else "✗"

        table.add_row(
            server["name"], server.get("description", ""), server["transport_type"], status, enabled
        )

    console.print(table)


def display_tools_table(tools_by_server: dict[str, list]) -> None:
    """Display tools in a formatted table."""
    for server_name, tools in tools_by_server.items():
        table = Table(title=f"Tools from '{server_name}'")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="white")

        for tool in tools:
            table.add_row(tool.name, tool.description or "")

        console.print(table)
        console.print()


def display_resources_table(resources_by_server: dict[str, list]) -> None:
    """Display resources in a formatted table."""
    for server_name, resources in resources_by_server.items():
        table = Table(title=f"Resources from '{server_name}'")
        table.add_column("URI", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Type", style="yellow")

        for resource in resources:
            table.add_row(str(resource.uri), resource.name or "", resource.mimeType or "")

        console.print(table)
        console.print()


def display_prompts_table(prompts_by_server: dict[str, list]) -> None:
    """Display prompts in a formatted table."""
    for server_name, prompts in prompts_by_server.items():
        table = Table(title=f"Prompts from '{server_name}'")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="white")

        for prompt in prompts:
            table.add_row(prompt.name, prompt.description or "")

        console.print(table)
        console.print()


# Command implementations


async def add_server_async(
    name: str,
    transport_type: str,
    command: str | None,
    args: list | None,
    url: str | None,
    description: str | None,
    verbose: bool,
) -> None:
    """Add a new MCP server configuration."""
    config_manager = ConfigManager()
    client_manager = MCPClientManager(config_manager)

    try:
        # Build transport config
        transport_config = MCPTransportConfig(type=transport_type)

        if transport_type == "stdio":
            if not command:
                raise click.UsageError("--command is required for stdio transport")
            transport_config.command = command
            transport_config.args = list(args) if args else []
        elif transport_type in ["sse", "websocket"]:
            if not url:
                raise click.UsageError(f"--url is required for {transport_type} transport")
            transport_config.url = url

        # Build server config
        server_config = MCPServerConfig(
            name=name, description=description, transport=transport_config
        )

        # Add server
        await client_manager.add_server(server_config)

        console.print(f"[green]✓[/green] Server '{name}' added successfully")
        console.print("\nNext steps:")
        console.print(f"  1. Connect to the server: [cyan]dspy-cli mcp connect {name}[/cyan]")
        console.print(f"  2. List available tools: [cyan]dspy-cli mcp tools {name}[/cyan]")

    except MCPError as e:
        console.print(f"[red]{format_mcp_error(e, verbose)}[/red]")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
        raise click.Abort()


async def remove_server_async(name: str, confirm: bool, verbose: bool) -> None:
    """Remove an MCP server configuration."""
    config_manager = ConfigManager()
    client_manager = MCPClientManager(config_manager)

    try:
        # Confirm removal
        if not confirm:
            if not click.confirm(f"Remove server '{name}'?"):
                console.print("Cancelled")
                return

        await client_manager.remove_server(name)
        console.print(f"[green]✓[/green] Server '{name}' removed successfully")

    except MCPError as e:
        console.print(f"[red]{format_mcp_error(e, verbose)}[/red]")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
        raise click.Abort()


async def list_servers_async(verbose: bool) -> None:
    """List all configured MCP servers."""
    config_manager = ConfigManager()
    client_manager = MCPClientManager(config_manager)

    try:
        servers = await client_manager.list_servers()

        if not servers:
            console.print("[yellow]No MCP servers configured[/yellow]")
            console.print("\nAdd a server with: [cyan]dspy-cli mcp add[/cyan]")
            return

        display_server_table(servers)

        if verbose:
            console.print("\n[bold]Detailed Information:[/bold]")
            for server in servers:
                if server["connected"] and "status" in server:
                    console.print(f"\n[cyan]{server['name']}[/cyan]:")
                    console.print(json.dumps(server["status"], indent=2))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
        raise click.Abort()


async def connect_server_async(name: str, verbose: bool) -> None:
    """Connect to an MCP server."""
    config_manager = ConfigManager()
    client_manager = MCPClientManager(config_manager)

    try:
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
        ) as progress:
            task = progress.add_task(f"Connecting to '{name}'...", total=None)

            session = await client_manager.connect(name)

            progress.update(task, completed=True)

        console.print(f"[green]✓[/green] Connected to '{name}'")

        # Display capabilities
        status = session.get_status()
        if status.get("capabilities"):
            caps = status["capabilities"]
            console.print("\n[bold]Server Capabilities:[/bold]")
            if caps.get("tools"):
                console.print("  • Tools")
            if caps.get("resources"):
                console.print("  • Resources")
            if caps.get("prompts"):
                console.print("  • Prompts")

        console.print(f"\nTry: [cyan]dspy-cli mcp tools {name}[/cyan]")

    except MCPError as e:
        console.print(f"[red]{format_mcp_error(e, verbose)}[/red]")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
        raise click.Abort()
    finally:
        await client_manager.cleanup()


async def disconnect_server_async(name: str, verbose: bool) -> None:
    """Disconnect from an MCP server."""
    config_manager = ConfigManager()
    client_manager = MCPClientManager(config_manager)

    try:
        await client_manager.disconnect(name)
        console.print(f"[green]✓[/green] Disconnected from '{name}'")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
        raise click.Abort()
    finally:
        await client_manager.cleanup()


async def list_tools_async(server: str | None, verbose: bool) -> None:
    """List tools from MCP servers."""
    config_manager = ConfigManager()
    client_manager = MCPClientManager(config_manager)

    try:
        # Connect if needed
        if server:
            session = await client_manager.get_session(server)
            if not session:
                console.print(f"Connecting to '{server}'...")
                await client_manager.connect(server)

        # List tools
        tools_by_server = await client_manager.list_tools(server)

        if not tools_by_server:
            console.print("[yellow]No tools available[/yellow]")
            return

        display_tools_table(tools_by_server)

        if verbose:
            console.print("\n[bold]Tool Details:[/bold]")
            for server_name, tools in tools_by_server.items():
                for tool in tools:
                    console.print(f"\n[cyan]{tool.name}[/cyan] ({server_name}):")
                    if tool.inputSchema:
                        console.print(json.dumps(tool.inputSchema, indent=2))

    except MCPError as e:
        console.print(f"[red]{format_mcp_error(e, verbose)}[/red]")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
        raise click.Abort()
    finally:
        await client_manager.cleanup()


async def list_resources_async(server: str | None, verbose: bool) -> None:
    """List resources from MCP servers."""
    config_manager = ConfigManager()
    client_manager = MCPClientManager(config_manager)

    try:
        # Connect if needed
        if server:
            session = await client_manager.get_session(server)
            if not session:
                console.print(f"Connecting to '{server}'...")
                await client_manager.connect(server)

        # List resources
        resources_by_server = await client_manager.list_resources(server)

        if not resources_by_server:
            console.print("[yellow]No resources available[/yellow]")
            return

        display_resources_table(resources_by_server)

    except MCPError as e:
        console.print(f"[red]{format_mcp_error(e, verbose)}[/red]")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
        raise click.Abort()
    finally:
        await client_manager.cleanup()


async def list_prompts_async(server: str | None, verbose: bool) -> None:
    """List prompts from MCP servers."""
    config_manager = ConfigManager()
    client_manager = MCPClientManager(config_manager)

    try:
        # Connect if needed
        if server:
            session = await client_manager.get_session(server)
            if not session:
                console.print(f"Connecting to '{server}'...")
                await client_manager.connect(server)

        # List prompts
        prompts_by_server = await client_manager.list_prompts(server)

        if not prompts_by_server:
            console.print("[yellow]No prompts available[/yellow]")
            return

        display_prompts_table(prompts_by_server)

        if verbose:
            console.print("\n[bold]Prompt Details:[/bold]")
            for server_name, prompts in prompts_by_server.items():
                for prompt in prompts:
                    console.print(f"\n[cyan]{prompt.name}[/cyan] ({server_name}):")
                    if prompt.arguments:
                        console.print("Arguments:")
                        for arg in prompt.arguments:
                            console.print(f"  • {arg.name}: {arg.description or 'No description'}")

    except MCPError as e:
        console.print(f"[red]{format_mcp_error(e, verbose)}[/red]")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
        raise click.Abort()
    finally:
        await client_manager.cleanup()


# Click command definitions


def add_server(
    name: str,
    transport_type: str,
    command: str | None = None,
    args: tuple | None = None,
    url: str | None = None,
    description: str | None = None,
    verbose: bool = False,
) -> None:
    """Add a new MCP server configuration."""
    run_async(
        add_server_async(
            name, transport_type, command, list(args) if args else None, url, description, verbose
        )
    )


def remove_server(name: str, confirm: bool = False, verbose: bool = False) -> None:
    """Remove an MCP server configuration."""
    run_async(remove_server_async(name, confirm, verbose))


def list_servers(verbose: bool = False) -> None:
    """List all configured MCP servers."""
    run_async(list_servers_async(verbose))


def connect_server(name: str, verbose: bool = False) -> None:
    """Connect to an MCP server."""
    run_async(connect_server_async(name, verbose))


def disconnect_server(name: str, verbose: bool = False) -> None:
    """Disconnect from an MCP server."""
    run_async(disconnect_server_async(name, verbose))


def list_tools(server: str | None = None, verbose: bool = False) -> None:
    """List tools from MCP servers."""
    run_async(list_tools_async(server, verbose))


def list_resources(server: str | None = None, verbose: bool = False) -> None:
    """List resources from MCP servers."""
    run_async(list_resources_async(server, verbose))


def list_prompts(server: str | None = None, verbose: bool = False) -> None:
    """List prompts from MCP servers."""
    run_async(list_prompts_async(server, verbose))
