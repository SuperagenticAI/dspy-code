"""
MCP Usage Demo for DSPy Code

This example demonstrates how to use MCP (Model Context Protocol)
integration in DSPy Code programmatically.

Note: This is a demonstration of the concepts. In practice, you'll
use the CLI commands or interactive mode slash commands.
"""

import asyncio

# This would be imported from dspy_cli in actual usage
# from dspy_cli.core.config import ConfigManager
# from dspy_cli.mcp import MCPClientManager, MCPServerConfig, MCPTransportConfig


async def demo_mcp_filesystem():
    """
    Demo: Connect to filesystem MCP server and read a file.

    CLI equivalent:
        dspy-cli mcp add filesystem --transport stdio --command uvx --args mcp-server-filesystem
        dspy-cli mcp connect filesystem
        dspy-cli mcp tools filesystem
    """
    print("=" * 60)
    print("Demo 1: Filesystem MCP Server")
    print("=" * 60)

    # In CLI, you would run:
    print("\n1. Add filesystem server:")
    print("   $ dspy-cli mcp add filesystem --transport stdio \\")
    print("       --command uvx --args mcp-server-filesystem")

    print("\n2. Connect to server:")
    print("   $ dspy-cli mcp connect filesystem")

    print("\n3. List available tools:")
    print("   $ dspy-cli mcp tools filesystem")

    print("\n4. List resources:")
    print("   $ dspy-cli mcp resources filesystem")

    print("\n5. Read a file:")
    print("   $ dspy-cli mcp read filesystem file:///path/to/file.txt")

    print("\n" + "=" * 60)


async def demo_mcp_interactive():
    """
    Demo: Using MCP in interactive mode.

    Interactive mode commands:
        /mcp-connect filesystem
        /mcp-tools
        /mcp-call filesystem read_file {"path": "data.json"}
    """
    print("=" * 60)
    print("Demo 2: MCP in Interactive Mode")
    print("=" * 60)

    print("\n1. Start interactive mode:")
    print("   $ dspy-cli")

    print("\n2. Connect to MCP server:")
    print("   > /mcp-connect filesystem")

    print("\n3. List available tools:")
    print("   > /mcp-tools")

    print("\n4. Call a tool:")
    print('   > /mcp-call filesystem read_file {"path": "data.json"}')

    print("\n5. Read a resource:")
    print("   > /mcp-read filesystem file:///path/to/data.json")

    print("\n6. List prompts:")
    print("   > /mcp-prompts")

    print("\n7. Get a prompt:")
    print('   > /mcp-prompt myserver greeting {"name": "Alice"}')

    print("\n" + "=" * 60)


async def demo_mcp_github():
    """
    Demo: Connect to GitHub MCP server.

    Requires: GITHUB_TOKEN environment variable
    """
    print("=" * 60)
    print("Demo 3: GitHub MCP Server")
    print("=" * 60)

    print("\n1. Set environment variable:")
    print("   $ export GITHUB_TOKEN='ghp_your_token_here'")

    print("\n2. Add GitHub server:")
    print("   $ dspy-cli mcp add github --transport sse \\")
    print("       --url https://api.github.com/mcp")

    print("\n3. Connect:")
    print("   $ dspy-cli mcp connect github")

    print("\n4. List tools:")
    print("   $ dspy-cli mcp tools github")

    print("\n5. Example: Get repository info")
    print("   In interactive mode:")
    print("   > /mcp-connect github")
    print('   > /mcp-call github get_repo {"owner": "user", "repo": "project"}')

    print("\n" + "=" * 60)


async def demo_mcp_multiple_servers():
    """
    Demo: Working with multiple MCP servers simultaneously.
    """
    print("=" * 60)
    print("Demo 4: Multiple MCP Servers")
    print("=" * 60)

    print("\n1. Add multiple servers:")
    print(
        "   $ dspy-cli mcp add filesystem --transport stdio --command uvx --args mcp-server-filesystem"
    )
    print("   $ dspy-cli mcp add github --transport sse --url https://api.github.com/mcp")
    print(
        "   $ dspy-cli mcp add postgres --transport stdio --command uvx --args mcp-server-postgres"
    )

    print("\n2. List all servers:")
    print("   $ dspy-cli mcp list")

    print("\n3. Connect to multiple servers:")
    print("   $ dspy-cli mcp connect filesystem")
    print("   $ dspy-cli mcp connect github")

    print("\n4. List tools from all connected servers:")
    print("   $ dspy-cli mcp tools")

    print("\n5. List tools from specific server:")
    print("   $ dspy-cli mcp tools filesystem")

    print("\n6. In interactive mode, switch between servers:")
    print("   > /mcp-tools filesystem")
    print("   > /mcp-tools github")
    print('   > /mcp-call filesystem read_file {"path": "data.json"}')
    print('   > /mcp-call github get_repo {"owner": "user", "repo": "project"}')

    print("\n" + "=" * 60)


async def demo_mcp_in_dspy_program():
    """
    Demo: Conceptual example of using MCP data in a DSPy program.
    """
    print("=" * 60)
    print("Demo 5: Using MCP Data in DSPy Programs")
    print("=" * 60)

    print("\nConcept: Use MCP to fetch data, then process with DSPy")

    print("\n1. Fetch data via MCP:")
    print("   > /mcp-connect filesystem")
    print("   > /mcp-read filesystem file:///data/training_data.json")

    print("\n2. The data is now in context")

    print("\n3. Generate DSPy code that uses this data:")
    print('   > "Create a classifier using the data we just loaded"')

    print("\n4. The generated code will include:")
    print("   - Data loading from the MCP resource")
    print("   - DSPy signature for the task")
    print("   - Module implementation")
    print("   - Training/evaluation setup")

    print("\nExample workflow:")
    print("   1. Use MCP to access external data sources")
    print("   2. Use MCP tools to preprocess or transform data")
    print("   3. Generate DSPy programs that work with this data")
    print("   4. Use MCP prompts as templates for DSPy signatures")

    print("\n" + "=" * 60)


async def main():
    """Run all demos."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "MCP Usage Demonstrations" + " " * 19 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    await demo_mcp_filesystem()
    print("\n")

    await demo_mcp_interactive()
    print("\n")

    await demo_mcp_github()
    print("\n")

    await demo_mcp_multiple_servers()
    print("\n")

    await demo_mcp_in_dspy_program()
    print("\n")

    print("=" * 60)
    print("For more information:")
    print("  - MCP Documentation: https://modelcontextprotocol.io")
    print("  - MCP Servers: https://github.com/modelcontextprotocol/servers")
    print("  - DSPy Code Docs: Run 'dspy-cli mcp --help'")
    print("=" * 60)
    print()


if __name__ == "__main__":
    asyncio.run(main())
