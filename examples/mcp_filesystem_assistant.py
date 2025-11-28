"""
Filesystem MCP Assistant Example
================================

This example shows how to use the **filesystem MCP server** together with
DSPy Code to build a small "Project Files Assistant".

It demonstrates how to:
- Connect to the `filesystem` MCP server
- List and read files via MCP
- Wrap MCP calls in a DSPy module for higher-level reasoning

Prerequisites
-------------
1. Node.js installed (for `npx` - the MCP server will be installed automatically when used)
2. Ollama installed and running locally (for the LM - no API keys needed)
   - Install: https://ollama.ai
   - Start: `ollama serve`
   - Pull model: `ollama pull llama3.1:8b`

3. Add a `filesystem` server to your `dspy_config.yaml`, for example:

   mcp_servers:
     filesystem:
       name: filesystem
       description: "Local filesystem access"
       enabled: true
       auto_connect: false
       transport:
         type: stdio
         command: npx
         args:
           - -y
           - "@modelcontextprotocol/server-filesystem"
           - /path/to/your/project
       timeout_seconds: 30
       retry_attempts: 3

3. Run this script from the root of your project:

   python examples/mcp_filesystem_assistant.py
"""

from __future__ import annotations

import asyncio

import dspy

from dspy_code.core.config import ConfigManager
from dspy_code.mcp import MCPClientManager


class FileSummarySignature(dspy.Signature):
    """Summarize a small collection of files for a given question."""

    question = dspy.InputField(desc="What you want to understand about these files")
    file_summaries = dspy.InputField(desc="Short summaries of the files")
    answer = dspy.OutputField(desc="Concise answer based on the code in those files")


class ProjectFilesAssistant(dspy.Module):
    """
    Simple assistant that:
    - Uses the filesystem MCP server to read project files
    - Uses DSPy to answer a question about those files
    """

    def __init__(self, mcp_manager: MCPClientManager, server_name: str = "filesystem"):
        super().__init__()
        self.mcp = mcp_manager
        self.server_name = server_name
        self.summarizer = dspy.ChainOfThought(FileSummarySignature)

    async def _read_file_via_mcp(self, path: str) -> str:
        """
        Read a file via MCP filesystem tool.

        Note: The filesystem MCP server exposes tools, not resources.
        We need to call a tool (like 'read_file' or 'readFile') with a path argument.
        """
        # Try common tool names - adjust based on what /mcp-tools shows
        tool_names = ["read_file", "readFile", "filesystem.readFile"]

        for tool_name in tool_names:
            try:
                result = await self.mcp.call_tool(self.server_name, tool_name, {"path": path})
                # Extract text from result
                if result.content:
                    contents = []
                    for content in result.content:
                        if hasattr(content, "text") and content.text:
                            contents.append(content.text)
                    if contents:
                        return "\n".join(contents)
                # Also check structuredContent
                if result.structuredContent:
                    if isinstance(result.structuredContent, dict):
                        if "content" in result.structuredContent:
                            return str(result.structuredContent["content"])
                        if "text" in result.structuredContent:
                            return str(result.structuredContent["text"])
            except Exception:
                # Try next tool name
                continue

        # If all tool names failed, raise an error
        raise ValueError(
            f"Could not read file '{path}'. "
            f"Tried tool names: {tool_names}. "
            f"Run '/mcp-tools {self.server_name}' to see available tools."
        )

    async def forward(self, question: str, paths: list[str]) -> str:
        file_summaries: list[str] = []

        for path in paths:
            # Use relative path from project root (must be inside allowed directories)
            print(f"📂 Reading via MCP: {path}")
            try:
                text = await self._read_file_via_mcp(path)
                if not text.strip():
                    print(f"   ⚠️  Empty file: {path}")
                    continue

                # Show confirmation that we actually read content
                print(f"   ✅ Read {len(text)} characters from {path}")

                # Keep a short slice to stay efficient
                snippet = text[:2000]
                file_summaries.append(f"File: {path}\n\n{snippet}")
            except Exception as e:
                print(f"   ❌ Failed to read {path}: {e}")
                import traceback

                traceback.print_exc()
                continue

        joined = "\n\n---\n\n".join(file_summaries) if file_summaries else "No content loaded."
        result = self.summarizer(question=question, file_summaries=joined)
        return result.answer


async def run_demo() -> None:
    print("=" * 60)
    print("📂 Filesystem MCP Assistant Demo")
    print("=" * 60)
    print()

    print("1) Loading MCP configuration...")
    config_manager = ConfigManager()
    mcp_manager = MCPClientManager(config_manager)

    print("2) Connecting to 'filesystem' MCP server...")
    await mcp_manager.connect("filesystem")
    print("   ✅ Connected\n")

    # Configure DSPy to use Ollama locally (no API key needed)
    # In practice, you would have done `/model` or `/connect` in the CLI.
    print("3) Configuring DSPy LM (using Ollama locally)...")
    print("   ⚠️ In the interactive CLI, DSPy Code wires this to your connected model.")
    print("   💡 Make sure Ollama is running: ollama serve")
    lm = dspy.LM(model="ollama/llama3.1:8b", api_base="http://localhost:11434")
    dspy.configure(lm=lm)
    print("   ✅ LM configured\n")

    assistant = ProjectFilesAssistant(mcp_manager, server_name="filesystem")

    # Example: inspect a couple of files in this repo
    paths = [
        "dspy_code/main.py",
        "dspy_code/commands/interactive_command.py",
    ]
    question = "Briefly explain what these files do and how they fit into the CLI."

    print("4) Asking Project Files Assistant:")
    print(f"   ❓ {question}")
    print()

    answer = await assistant(question=question, paths=paths)

    print("✨ Assistant answer:")
    print("-" * 60)
    print(answer)
    print("-" * 60)
    print()

    await mcp_manager.cleanup()
    print("✅ Done. You can now adapt this pattern to your own projects.")


if __name__ == "__main__":
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
