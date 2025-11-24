"""
Demo of Slash Commands functionality.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def show_demo():
    """Show slash commands demo."""

    console.print("\n[bold magenta]✨ DSPy Code Slash Commands Demo ✨[/bold magenta]\n")

    # Demo 1: Available Commands
    console.print("[bold cyan]📚 Available Slash Commands:[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Command", style="yellow", width=25)
    table.add_column("Description", style="white")
    table.add_column("Example", style="dim")

    commands = [
        ("/connect", "Connect to a model", "/connect ollama llama2"),
        ("/models", "List available models", "/models ollama"),
        ("/status", "Check connection", "/status"),
        ("/disconnect", "Disconnect model", "/disconnect"),
        ("/reference", "View DSPy docs", "/reference signature"),
        ("/history", "View conversation", "/history"),
        ("/help", "Show help", "/help"),
    ]

    for cmd, desc, example in commands:
        table.add_row(cmd, desc, example)

    console.print(table)
    console.print()

    # Demo 2: Model Connection Flow
    console.print("[bold cyan]🔌 Model Connection Flow:[/bold cyan]\n")

    flow = """
[bold]Step 1: List available models[/bold]
/models ollama

[dim]Output:[/dim]
🖥️  Local Models (Ollama):
┌─────────┬────────────┬───────┐
│ Model   │ Status     │ Type  │
├─────────┼────────────┼───────┤
│ llama2  │ Available  │ Local │
│ mistral │ Available  │ Local │
└─────────┴────────────┴───────┘

[bold]Step 2: Connect to a model[/bold]
/connect ollama llama2

[dim]Output:[/dim]
ℹ Connecting to ollama/llama2...
✓ Connected to llama2!
ℹ The CLI will now use this model to understand your requests.

[bold]Step 3: Check status[/bold]
/status

[dim]Output:[/dim]
Connection Status
─────────────────
Status    ✓ Connected
Model     llama2
Type      ollama

[bold]Step 4: Start creating![/bold]
Create a signature for email classification

[dim]CLI uses llama2 + DSPy reference docs to generate perfect code![/dim]
"""

    panel = Panel(flow, border_style="cyan", padding=(1, 2))
    console.print(panel)
    console.print()

    # Demo 3: Reference Documentation
    console.print("[bold cyan]📖 Reference Documentation:[/bold cyan]\n")

    ref_examples = """
[bold yellow]/reference[/bold yellow]
  Shows all DSPy reference documentation

[bold yellow]/reference signature[/bold yellow]
  Shows signature patterns and examples

[bold yellow]/reference module[/bold yellow]
  Shows module patterns and examples

[bold yellow]/reference optimize[/bold yellow]
  Shows GEPA optimization examples

[bold yellow]/reference chain of thought[/bold yellow]
  Shows Chain of Thought reasoning pattern

[dim]The reference docs are automatically injected into model prompts
to ensure accurate, DSPy-compliant code generation![/dim]
"""

    console.print(ref_examples)
    console.print()

    # Demo 4: Conversation History
    console.print("[bold cyan]💬 Conversation History:[/bold cyan]\n")

    history_demo = """
[bold yellow]/history[/bold yellow]
  Shows recent conversation (last 5 interactions)

[bold yellow]/history all[/bold yellow]
  Shows all conversation from current session

[dim]Example output:[/dim]

📜 Conversation History

[bold cyan]You:[/bold cyan] Create a signature for email classification...
[bold green]Assistant:[/bold green] I'll help you create a DSPy Signature!...

[bold cyan]You:[/bold cyan] Now create a module using chain of thought...
[bold green]Assistant:[/bold green] I'll create a DSPy Module for you!...

Session Summary
───────────────────────
Total Interactions    2
Messages Exchanged    4
Code Generated        2
"""

    console.print(history_demo)
    console.print()

    # Demo 5: Fancy Input Box
    console.print("[bold cyan]✨ Fancy Input Box:[/bold cyan]\n")

    input_demo = """
[dim]The CLI now features a beautiful input box:[/dim]

╭─ ✨ Your Message (Message #1) ─────────────────────────────╮
│ Type your request here... (or /help for commands)         │
╰────────────────────────────────────────────────────────────╯
  → _

[dim]Features:[/dim]
• Shows message count
• Hints about slash commands
• Beautiful gradient colors
• Professional appearance
"""

    panel = Panel(input_demo, border_style="green", padding=(1, 2))
    console.print(panel)
    console.print()

    # Demo 6: Try It Now
    console.print("[bold cyan]🚀 Try It Now:[/bold cyan]\n")

    console.print("1. Start the CLI:")
    console.print("   [cyan]$ dspy-cli[/cyan]")
    console.print()
    console.print("2. List available models:")
    console.print("   [yellow]/models ollama[/yellow]")
    console.print()
    console.print("3. Connect to a model:")
    console.print("   [yellow]/connect ollama llama2[/yellow]")
    console.print()
    console.print("4. View DSPy reference:")
    console.print("   [yellow]/reference signature[/yellow]")
    console.print()
    console.print("5. Start creating:")
    console.print('   [green]"Create a signature for sentiment analysis"[/green]')
    console.print()
    console.print("6. View your conversation:")
    console.print("   [yellow]/history[/yellow]")
    console.print()

    # Documentation
    console.print("[bold cyan]📚 Documentation:[/bold cyan]\n")
    console.print("• [cyan]docs/SLASH_COMMANDS.md[/cyan] - Complete slash commands reference")
    console.print("• [cyan]docs/MODEL_CONNECTION_GUIDE.md[/cyan] - Model setup guide")
    console.print("• [cyan]/help[/cyan] in CLI - Interactive help")
    console.print()


if __name__ == "__main__":
    show_demo()
