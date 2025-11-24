"""
Enhanced input prompts for DSPy Code.
"""

from pathlib import Path

from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

console = Console()

# Command history storage (persists across calls)
_command_history: list[str] = []
_history_index: int = -1
_history_file = Path.home() / ".dspy_code_history"


# Load history from file on module import
def _load_history():
    """Load command history from file."""
    global _command_history
    if _history_file.exists():
        try:
            with open(_history_file, encoding="utf-8") as f:
                _command_history = [line.strip() for line in f if line.strip()]
                # Keep only last 1000
                if len(_command_history) > 1000:
                    _command_history = _command_history[-1000:]
        except Exception:
            _command_history = []


def _save_history():
    """Save command history to file."""
    try:
        with open(_history_file, "w", encoding="utf-8") as f:
            for item in _command_history:
                f.write(f"{item}\n")
    except Exception:
        pass  # Silently fail if can't save


# Load history on module import
_load_history()


def get_user_input(
    show_examples: bool = False, conversation_count: int = 0, history: list[str] | None = None
) -> str:
    """
    Get user input with a beautiful fancy text box.

    Args:
        show_examples: Whether to show example prompts
        conversation_count: Number of messages in conversation

    Returns:
        User's input string
    """

    if show_examples:
        # Show example prompts in a subtle way
        examples = Text()
        examples.append("💭 ", style="dim")
        examples.append("Try: ", style="dim italic")
        examples.append('"Create a signature for..." ', style="dim cyan")
        examples.append("or ", style="dim")
        examples.append('"Build a module using..." ', style="dim green")
        examples.append("or ", style="dim")
        examples.append('"/help" for commands', style="dim yellow")
        console.print(examples)
        console.print()

    # Create a fancy input box
    input_header = Text()
    input_header.append("✨ ", style="bright_yellow")
    input_header.append("Your Message", style="bold cyan")
    if conversation_count > 0:
        input_header.append(f" (Message #{conversation_count + 1})", style="dim")

    # Show the fancy input box
    input_panel = Panel(
        "[dim]Type your request here... (or /help for commands)[/dim]",
        title=input_header,
        border_style="cyan",
        box=ROUNDED,
        padding=(0, 1),
    )
    console.print(input_panel)

    # Get input with styled prompt and history support
    prompt_text = Text()
    prompt_text.append("  ", style="")
    prompt_text.append("→ ", style="bright_cyan")

    # Load history from file if needed
    if not _command_history:
        _load_history()

    # Try readline for history on Unix/Mac systems (built-in, no extra dependency)
    try:
        import readline

        # Set up readline history file
        if _history_file.exists():
            try:
                readline.read_history_file(str(_history_file))
                # Also sync to global history
                try:
                    for i in range(1, readline.get_current_history_length() + 1):
                        hist_item = readline.get_history_item(i)
                        if hist_item and hist_item not in _command_history:
                            _command_history.append(hist_item)
                except Exception:
                    pass
            except Exception:
                pass

        # Configure readline
        readline.set_history_length(1000)

        # Add existing history to readline (if not already there)
        for item in _command_history:
            try:
                # Check if already in readline history
                current_len = readline.get_current_history_length()
                found = False
                for i in range(1, current_len + 1):
                    if readline.get_history_item(i) == item:
                        found = True
                        break
                if not found:
                    readline.add_history(item)
            except Exception:
                pass

        # IMPORTANT: Use input() instead of Prompt.ask() so readline works
        # Print the prompt manually, then use input() which integrates with readline
        console.print(prompt_text, end="")
        user_input = input()

        # Add to history
        if user_input.strip():
            # Add to readline history
            try:
                readline.add_history(user_input.strip())
            except Exception:
                pass

            # Also add to global history
            if not _command_history or _command_history[-1] != user_input.strip():
                _command_history.append(user_input.strip())
                if len(_command_history) > 1000:
                    _command_history.pop(0)

            # Save history to file
            try:
                readline.write_history_file(str(_history_file))
                _save_history()
            except Exception:
                _save_history()  # Fallback to our save method

        return user_input

    except (ImportError, AttributeError):
        # Fallback for Windows or systems without readline
        # Use simple input with manual history tracking
        # Note: Arrow keys won't work on Windows without readline, but history is still saved

        user_input = Prompt.ask(prompt_text, console=console)

        # Add to history
        if user_input.strip():
            if not _command_history or _command_history[-1] != user_input.strip():
                _command_history.append(user_input.strip())
                if len(_command_history) > 1000:
                    _command_history.pop(0)
                # Save history to file
                _save_history()

        return user_input


def show_assistant_header():
    """Show the assistant response header."""
    console.print()
    header = Text()
    header.append("🤖 ", style="bold")
    header.append("DSPy Assistant", style="bold green")
    console.print(header)
    console.print()


def show_code_panel(code: str, title: str = "Generated Code", language: str = "python"):
    """
    Display generated code in a beautiful panel.

    Args:
        code: The code to display
        title: Panel title
        language: Programming language for syntax highlighting
    """
    from rich.syntax import Syntax

    syntax = Syntax(code, language, theme="monokai", line_numbers=True, background_color="default")

    panel = Panel(
        syntax, title=f"[bold green]{title}[/bold green]", border_style="green", padding=(1, 2)
    )

    console.print(panel)


def show_success_message(message: str):
    """Show a success message."""
    text = Text()
    text.append("✓ ", style="bold green")
    text.append(message, style="green")
    console.print(text)


def show_info_message(message: str):
    """Show an info message."""
    text = Text()
    text.append("ℹ ", style="bold cyan")
    text.append(message, style="cyan")
    console.print(text)


def show_warning_message(message: str):
    """Show a warning message."""
    text = Text()
    text.append("⚠ ", style="bold yellow")
    text.append(message, style="yellow")
    console.print(text)


def show_error_message(message: str):
    """Show an error message."""
    text = Text()
    text.append("✗ ", style="bold red")
    text.append(message, style="red")
    console.print(text)


def show_thinking_message(message: str):
    """Show a thinking/processing message."""
    text = Text()
    text.append("💭 ", style="bold magenta")
    text.append(message, style="dim")
    console.print(text)


def show_next_steps(steps: list):
    """Show suggested next steps."""
    console.print()
    console.print("[bold cyan]💡 Next Steps:[/bold cyan]")
    for step in steps:
        console.print(f"  [dim]→[/dim] {step}")
    console.print()
