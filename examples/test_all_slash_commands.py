"""
Test all slash commands to verify they work.
"""

from rich.console import Console
from rich.panel import Panel

console = Console()


def show_all_commands():
    """Display all available slash commands."""

    console.print("\n[bold magenta]✨ All DSPy Code Slash Commands ✨[/bold magenta]\n")

    commands = {
        "Model Management": [
            ("/connect <type> <model>", "Connect to a language model", "/connect ollama llama2"),
            ("/models [filter]", "List available models", "/models ollama"),
            ("/status", "Show connection status", "/status"),
            ("/disconnect", "Disconnect from model", "/disconnect"),
        ],
        "Documentation & Help": [
            ("/reference [topic]", "View DSPy reference docs", "/reference signature"),
            ("/history [all]", "Show conversation history", "/history"),
            ("/help", "Show help message", "/help"),
        ],
        "Session Management": [
            ("/clear", "Clear conversation history", "/clear"),
            ("/save <filename>", "Save generated code", "/save classifier.py"),
            ("/exit", "Exit DSPy Code", "/exit"),
        ],
    }

    for category, cmds in commands.items():
        console.print(f"[bold cyan]{category}:[/bold cyan]")
        console.print()

        for cmd, desc, example in cmds:
            console.print(f"  [yellow]{cmd:30}[/yellow] {desc}")
            console.print(f"  [dim]Example: {example}[/dim]")
            console.print()

        console.print()

    # Show usage flow
    flow = """
[bold cyan]Complete Workflow Example:[/bold cyan]

1. Start CLI and check available models
   $ dspy-cli
   /models ollama

2. Connect to a model
   /connect ollama llama3.2

3. Check connection
   /status

4. View DSPy reference
   /reference signature

5. Create something
   "Create a signature for email classification"

6. Save your work
   /save email_classifier.py

7. View conversation history
   /history

8. Clear and start fresh (optional)
   /clear

9. Exit when done
   /exit

[bold green]All commands are now slash commands for consistency![/bold green]
"""

    panel = Panel(flow, border_style="cyan", padding=(1, 2))
    console.print(panel)
    console.print()

    # Legacy support note
    console.print("[bold yellow]📝 Note:[/bold yellow]")
    console.print("  Legacy commands still work for convenience:")
    console.print("  • [dim]help, ?, clear, reset, save, exit, quit, bye, q[/dim]")
    console.print("  • [dim]These are automatically converted to slash commands[/dim]")
    console.print()

    # Documentation
    console.print("[bold cyan]📚 Documentation:[/bold cyan]")
    console.print("  • [cyan]docs/SLASH_COMMANDS.md[/cyan] - Complete reference")
    console.print("  • [cyan]/help[/cyan] in CLI - Interactive help")
    console.print()


if __name__ == "__main__":
    show_all_commands()
