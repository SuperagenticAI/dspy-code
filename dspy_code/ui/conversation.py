"""
Conversation history display for DSPy Code.
"""

from rich.box import ROUNDED
from rich.console import Console
from rich.table import Table

console = Console()


def show_conversation_history(history: list, max_items: int = 10):
    """
    Display conversation history in a beautiful format.

    Args:
        history: List of conversation messages
        max_items: Maximum number of items to show
    """
    if not history:
        console.print("[dim]No conversation history yet.[/dim]")
        return

    console.print()
    console.print("[bold cyan]📜 Conversation History[/bold cyan]")
    console.print()

    # Show last N items
    recent_history = history[-max_items * 2 :] if len(history) > max_items * 2 else history

    for i in range(0, len(recent_history), 2):
        # User message
        if i < len(recent_history):
            user_msg = recent_history[i]
            console.print(f"[bold cyan]You:[/bold cyan] {user_msg['content'][:100]}...")

        # Assistant response
        if i + 1 < len(recent_history):
            assistant_msg = recent_history[i + 1]
            content = assistant_msg["content"]
            if isinstance(content, dict):
                content = content.get("explanation", "Generated code")
            console.print(f"[bold green]Assistant:[/bold green] {str(content)[:100]}...")

        console.print()

    if len(history) > max_items * 2:
        console.print(f"[dim]... and {len(history) // 2 - max_items} more interactions[/dim]")
        console.print()


def show_conversation_summary(history: list):
    """
    Show a summary of the conversation.

    Args:
        history: List of conversation messages
    """
    if not history:
        return

    total_interactions = len(history) // 2

    table = Table(title="Session Summary", show_header=False, box=ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Interactions", str(total_interactions))
    table.add_row("Messages Exchanged", str(len(history)))

    # Count generated items
    generated_count = sum(1 for msg in history if isinstance(msg.get("content"), dict))
    if generated_count > 0:
        table.add_row("Code Generated", str(generated_count))

    console.print(table)
    console.print()
