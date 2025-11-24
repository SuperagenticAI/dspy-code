"""
Welcome screen and branding for DSPy Code.
"""

from rich.align import Align
from rich.box import DOUBLE, ROUNDED
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


# ASCII Art for DSPy Code (bold, dotted style)
DSPY_ASCII_ART = """
   ██████╗ ███████╗██████╗ ██╗   ██╗     ██████╗ ██████╗ ██████╗ ███████╗
   ██╔══██╗██╔════╝██╔══██╗╚██╗ ██╔╝    ██╔════╝██╔═══██╗██╔══██╗██╔════╝
   ██║  ██║███████╗██████╔╝ ╚████╔╝     ██║     ██║   ██║██║  ██║█████╗
   ██║  ██║╚════██║██╔═══╝   ╚██╔╝      ██║     ██║   ██║██║  ██║██╔══╝
   ██████╔╝███████║██║        ██║       ╚██████╗╚██████╔╝██████╔╝███████╗
   ╚═════╝ ╚══════╝╚═╝        ╚═╝        ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝
"""


def create_gradient_text(text: str, colors: list) -> Text:
    """
    Create text with smooth gradient colors across the entire text.

    Args:
        text: The text to colorize
        colors: List of colors for the gradient

    Returns:
        Rich Text object with gradient
    """
    result = Text()

    # Get all non-whitespace characters for gradient calculation
    all_chars = [c for c in text if c not in ("\n", " ")]
    total_chars = len(all_chars)

    if total_chars == 0:
        return Text(text)

    char_index = 0
    for char in text:
        if char == "\n":
            result.append("\n")
        elif char == " ":
            result.append(" ")
        else:
            # Calculate position in gradient (0.0 to 1.0)
            position = char_index / max(total_chars - 1, 1)

            # Map position to color index
            color_float = position * (len(colors) - 1)
            color_index = int(color_float)

            # Get the color
            color = colors[min(color_index, len(colors) - 1)]
            result.append(char, style=f"bold {color}")

            char_index += 1

    return result


def show_welcome_screen(model_name: str = "Not configured"):
    """
    Display a beautiful welcome screen with ASCII art and instructions.

    Args:
        model_name: The currently configured model name
    """
    console.clear()

    # Add some spacing
    console.print()

    # Create beautiful gradient colors for the ASCII art
    # Rainbow gradient: cyan -> blue -> magenta -> red -> yellow
    gradient_colors = [
        "cyan",
        "bright_cyan",
        "blue",
        "bright_blue",
        "magenta",
        "bright_magenta",
        "red",
        "bright_red",
        "yellow",
        "bright_yellow",
    ]

    # Show ASCII art with gradient in a panel
    ascii_text = create_gradient_text(DSPY_ASCII_ART, gradient_colors)
    ascii_panel = Panel(
        Align.center(ascii_text), border_style="bright_cyan", box=DOUBLE, padding=(1, 4)
    )
    console.print(ascii_panel)

    # Welcome message with gradient
    welcome_text = Text()
    welcome_text.append("✨ ", style="bright_yellow")
    welcome_text.append("Welcome to ", style="white")
    welcome_text.append("D", style="bright_cyan")
    welcome_text.append("S", style="bright_blue")
    welcome_text.append("P", style="bright_magenta")
    welcome_text.append("y", style="bright_red")
    welcome_text.append(" ", style="white")
    welcome_text.append("C", style="bright_yellow")
    welcome_text.append("o", style="bright_green")
    welcome_text.append("d", style="bright_cyan")
    welcome_text.append("e", style="bright_blue")
    welcome_text.append(" - Your AI-Powered DSPy Development Assistant: ", style="white")
    welcome_text.append("C", style="bright_cyan")
    welcome_text.append("l", style="bright_blue")
    welcome_text.append("a", style="bright_magenta")
    welcome_text.append("u", style="bright_red")
    welcome_text.append("d", style="bright_yellow")
    welcome_text.append("e", style="bright_green")
    welcome_text.append(" ", style="white")
    welcome_text.append("C", style="bright_cyan")
    welcome_text.append("o", style="bright_blue")
    welcome_text.append("d", style="bright_magenta")
    welcome_text.append("e", style="bright_red")
    welcome_text.append(" ", style="white")
    welcome_text.append("f", style="bright_yellow")
    welcome_text.append("o", style="bright_green")
    welcome_text.append("r", style="bright_cyan")
    welcome_text.append(" ", style="white")
    welcome_text.append("D", style="bright_blue")
    welcome_text.append("S", style="bright_magenta")
    welcome_text.append("P", style="bright_red")
    welcome_text.append("y", style="bright_yellow")
    welcome_text.append(" ✨", style="bright_yellow")

    console.print(Align.center(welcome_text))
    console.print()

    # Model info
    model_info = Text()
    model_info.append("🤖 Current Model: ", style="dim")
    model_info.append(
        model_name, style="bold green" if model_name != "Not configured" else "bold yellow"
    )
    console.print(Align.center(model_info))
    console.print()

    # Create info panels
    quick_start = """
[bold cyan]⚡ Quick Start:[/bold cyan]

[yellow]/demo[/yellow]      - Run a working example
[yellow]/help[/yellow]      - Show all commands
[yellow]/sessions[/yellow]  - Manage sessions
[yellow]/mcp[/yellow]       - Connect to MCP servers
[yellow]/optimize[/yellow]  - Optimize your programs
[yellow]/exit[/yellow]      - Quit interactive mode

[dim]💡 Start with /demo to see what's possible![/dim]
"""

    example_prompts = """
[bold cyan]📝 Try These Examples:[/bold cyan]

[green]"Create a sentiment analysis program"[/green]
[dim]→ Full program with ChainOfThought[/dim]

[green]"Build a RAG system with retrieval"[/green]
[dim]→ Auto-generates retrieval pipeline[/dim]

[green]"Make a ReAct agent with tools"[/green]
[dim]→ Generates agent with tool support[/dim]

[green]"Optimize my program with GEPA"[/green]
[dim]→ Runs genetic optimization[/dim]
"""

    features = """
[bold cyan]✨ Latest Features:[/bold cyan]

[green]•[/green] Session Management (auto-save)
[green]•[/green] MCP Server Integration
[green]•[/green] GEPA Optimization
[green]•[/green] Code Execution & Validation
[green]•[/green] Export/Import Programs
[green]•[/green] Package Building
[green]•[/green] All DSPy Predictors

[dim]Type /help to see all commands[/dim]
"""

    # Display panels in columns
    panels = [
        Panel(quick_start, border_style="yellow", box=ROUNDED, padding=(1, 2)),
        Panel(example_prompts, border_style="green", box=ROUNDED, padding=(1, 2)),
        Panel(features, border_style="cyan", box=ROUNDED, padding=(1, 2)),
    ]

    console.print(Columns(panels, equal=True, expand=True))
    console.print()

    # Tips section
    tips = Panel(
        "[bold]💡 Pro Tips:[/bold]\n\n"
        "• [cyan]Sessions Auto-Save[/cyan] - Your work is automatically saved every 30s\n"
        "• [cyan]Use MCP Servers[/cyan] - Connect to external tools with /mcp connect\n"
        "• [cyan]Optimize Programs[/cyan] - Use /optimize to improve performance with GEPA\n"
        "• [cyan]Execute & Test[/cyan] - Run code with /run and validate with /validate\n"
        "• [cyan]Export Packages[/cyan] - Share your work with /package export\n"
        "• [cyan]Load Sessions[/cyan] - Resume previous work with /load <session-name>\n\n"
        "[dim]Need help? Type /help anytime![/dim]",
        title="[bold magenta]Pro Tips[/bold magenta]",
        border_style="magenta",
        box=ROUNDED,
        padding=(1, 2),
    )
    console.print(tips)
    console.print()

    # Prominent help reminder
    help_reminder = Text()
    help_reminder.append("👉 ", style="bold yellow")
    help_reminder.append("New here? Type ", style="white")
    help_reminder.append("/help", style="bold cyan")
    help_reminder.append(" to see all available commands!", style="white")
    help_reminder.append(" 👈", style="bold yellow")
    console.print(Align.center(help_reminder))
    console.print()

    # Ready prompt
    ready_text = Text()
    ready_text.append("🚀 ", style="bold")
    ready_text.append("Ready to build amazing DSPy programs? ", style="bold white")
    ready_text.append("Try: ", style="dim")
    ready_text.append("/demo", style="bold yellow")
    ready_text.append(" or describe your task!", style="dim")
    console.print(Align.center(ready_text))
    console.print()

    # Separator
    console.print("─" * console.width, style="dim")
    console.print()


def show_compact_header():
    """Show a compact header for subsequent interactions."""
    header = Text()
    header.append("DSPy Code", style="bold cyan")
    header.append(" | ", style="dim")
    header.append("Interactive Mode", style="dim")
    console.print(header)
    console.print("─" * console.width, style="dim")
    console.print()
