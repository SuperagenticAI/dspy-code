"""
GitHub MCP Triage Assistant Example
===================================

This example shows how to use a **GitHub MCP server** together with DSPy Code
to build a small "Issue & PR Triage Copilot".

It demonstrates how to:
- Connect to a `github` MCP server
- Call tools to fetch issues/PRs
- Wrap MCP calls in a DSPy module that summarizes and suggests next actions

Prerequisites
-------------
1. Ollama installed and running locally (for the LM - no API keys needed)
   - Install: https://ollama.ai
   - Start: `ollama serve`
   - Pull model: `ollama pull llama3.1:8b`

2. Set a GitHub token with appropriate repo access:

   export GITHUB_TOKEN="ghp_your_token_here"

3. Configure a `github` MCP server in `dspy_config.yaml`, for example:

   mcp_servers:
     github:
       name: github
       description: "GitHub API access"
       enabled: true
       auto_connect: false
       transport:
         type: sse
         url: https://api.github.com/mcp
         headers:
           Authorization: "Bearer ${GITHUB_TOKEN}"
           Accept: "application/vnd.github.v3+json"
       timeout_seconds: 60
       retry_attempts: 3

   (You can copy this from examples/mcp_config_examples.yaml and adjust.)

3. Run this script from the root of your project:

   python examples/mcp_github_triage_assistant.py
"""

from __future__ import annotations

import asyncio
from typing import Any

import dspy

from dspy_code.core.config import ConfigManager
from dspy_code.mcp import MCPClientManager


class GitHubTriageSignature(dspy.Signature):
    """Summarize GitHub issues/PRs and suggest next actions."""

    repo = dspy.InputField(desc="Repository (owner/name)")
    items = dspy.InputField(desc="Raw issue/PR data as JSON-like text")
    triage_summary = dspy.OutputField(
        desc="High-level summary plus prioritized next actions for the team"
    )


class GitHubTriageAssistant(dspy.Module):
    """
    Triage assistant that:
    - Uses the GitHub MCP server to fetch issues/PRs
    - Uses DSPy to summarize and suggest next actions

    Note: The exact tool names and schemas depend on your GitHub MCP server.
    This example assumes a tool like `list_issues` that accepts simple arguments.
    """

    def __init__(self, mcp_manager: MCPClientManager, server_name: str = "github"):
        super().__init__()
        self.mcp = mcp_manager
        self.server_name = server_name
        self.triage = dspy.ChainOfThought(GitHubTriageSignature)

    async def _fetch_items(self, owner: str, repo: str) -> Any:
        """
        Fetch recent issues from GitHub via MCP.

        Adjust `tool_name` and `arguments` to match your MCP GitHub server's schema.
        """
        tool_name = "list_issues"
        print(f"🐙 Calling MCP tool '{tool_name}' on {owner}/{repo} ...")
        result = await self.mcp.call_tool(
            self.server_name,
            tool_name,
            {
                "owner": owner,
                "repo": repo,
                "state": "open",
                "limit": 20,
            },
        )
        return result  # Often this will be a dict with a `results` field

    async def forward(self, owner: str, repo: str) -> str:
        raw = await self._fetch_items(owner, repo)

        # Keep it simple: stringify the structure for the language model
        text_blob = repr(raw)
        full_name = f"{owner}/{repo}"

        result = self.triage(repo=full_name, items=text_blob)
        return result.triage_summary


async def run_demo() -> None:
    print("=" * 60)
    print("🐙 GitHub MCP Triage Assistant Demo")
    print("=" * 60)
    print()

    print("1) Loading MCP configuration...")
    config_manager = ConfigManager()
    mcp_manager = MCPClientManager(config_manager)

    print("2) Connecting to 'github' MCP server...")
    await mcp_manager.connect("github")
    print("   ✅ Connected\n")

    # Configure DSPy to use Ollama locally (no API key needed)
    print("3) Configuring DSPy LM (using Ollama locally)...")
    print("   ⚠️ In the interactive CLI, DSPy Code wires this to your connected model.")
    print("   💡 Make sure Ollama is running: ollama serve")
    lm = dspy.LM(model="ollama/llama3.1:8b", api_base="http://localhost:11434")
    dspy.configure(lm=lm)
    print("   ✅ LM configured\n")

    assistant = GitHubTriageAssistant(mcp_manager, server_name="github")

    # Example repo – replace with your own
    owner = "superagentic-ai"
    repo = "dspy-code"

    print("4) Running triage for repository:")
    print(f"   📦 {owner}/{repo}")
    print()

    summary = await assistant(owner=owner, repo=repo)

    print("✨ Triage summary:")
    print("-" * 60)
    print(summary)
    print("-" * 60)
    print()

    await mcp_manager.cleanup()
    print("✅ Done. You can now adapt this pattern to your own GitHub projects.")


if __name__ == "__main__":
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
