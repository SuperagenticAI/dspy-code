"""
Main entry point for DSPy Code.

This module provides the interactive command-line interface for creating, managing,
and optimizing DSPy components through natural language interactions.

All commands are now SLASH COMMANDS in interactive mode!
"""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.traceback import install

from .commands import interactive_command
from .core.exceptions import DSPyCLIError
from .core.logging import setup_logging

# Install rich traceback handler for better error display
install(show_locals=True)

console = Console()


def check_safe_working_directory() -> None:
    """Check if current working directory is safe for dspy-code operations.

    SECURITY: This prevents accidental scanning of user home directories,
    system directories, and other sensitive locations.
    """
    cwd = Path.cwd().resolve()
    home = Path.home().resolve()

    # Check if running from home directory itself
    if cwd == home:
        console.print()
        console.print(
            Panel.fit(
                "[bold red]🚨 SECURITY WARNING[/bold red]\n\n"
                "[yellow]You are running dspy-code from your home directory![/yellow]\n\n"
                "This is dangerous as it may attempt to scan ALL files in your home directory,\n"
                "including personal documents, photos, and sensitive data.\n\n"
                "[bold green]Recommended actions:[/bold green]\n"
                "1. Create a dedicated project directory: [cyan]mkdir ~/my-dspy-project[/cyan]\n"
                "2. Navigate to it: [cyan]cd ~/my-dspy-project[/cyan]\n"
                "3. Create a virtual environment: [cyan]python -m venv .venv[/cyan]\n"
                "4. Activate it: [cyan]source .venv/bin/activate[/cyan]\n"
                "5. Install dspy-code: [cyan]pip install dspy-code[/cyan]\n"
                "6. Then run: [cyan]dspy-code[/cyan]\n\n"
                "[dim]Press Ctrl+C to exit, or Enter to continue at your own risk...[/dim]",
                title="⚠️  Safety Check",
                border_style="red",
            )
        )
        try:
            input()
        except KeyboardInterrupt:
            console.print("\n[green]Good choice! Please run from a project directory.[/green]")
            sys.exit(0)
        console.print(
            "[yellow]⚠️  Proceeding with limited functionality to protect your files...[/yellow]\n"
        )
        return

    # Check if running from immediate subdirectory of home (e.g., ~/Desktop, ~/Documents)
    try:
        relative = cwd.relative_to(home)
        parts = relative.parts

        if len(parts) <= 1:
            dangerous_dirs = [
                "desktop",
                "documents",
                "downloads",
                "pictures",
                "photos",
                "movies",
                "music",
                "library",
                "icloud",
                "public",
            ]

            if parts and parts[0].lower() in dangerous_dirs:
                console.print()
                console.print(
                    Panel.fit(
                        f"[bold yellow]⚠️  WARNING[/bold yellow]\n\n"
                        f"You are running dspy-code from: [cyan]{cwd}[/cyan]\n\n"
                        "This directory may contain personal files. For safety,\n"
                        "dspy-code will not scan files here.\n\n"
                        "[bold green]Recommendation:[/bold green]\n"
                        "Create a dedicated project directory for your DSPy work:\n"
                        "[cyan]mkdir ~/projects/my-dspy-project && cd ~/projects/my-dspy-project[/cyan]",
                        title="💡 Location Notice",
                        border_style="yellow",
                    )
                )
    except ValueError:
        # Not relative to home, which is fine
        pass

    # FIRST: Check if we're in an allowed temp directory (exception to system dir rules)
    allowed_temp_paths = [
        Path("/tmp"),
        Path("/var/folders"),
        Path("/private/tmp"),
        Path("/private/var/folders"),
    ]

    is_in_temp = any(
        cwd.is_relative_to(temp_path) if temp_path.exists() else False
        for temp_path in allowed_temp_paths
    )

    # If we're in a temp directory, skip system directory checks
    if is_in_temp:
        return

    # Allow user directories (e.g., /Users/username/... or /home/username/...)
    # This allows development/testing from repository root
    user_dirs = [Path("/Users"), Path("/home")]
    is_in_user_dir = any(
        cwd.is_relative_to(user_dir) if user_dir.exists() else False for user_dir in user_dirs
    )

    # Also allow if we're in the repository root (has dspy_code package)
    is_repo_root = (cwd / "dspy_code").exists() and (cwd / "dspy_code" / "__init__.py").exists()

    # If we're in a user directory or repo root, allow it (but still check for specific system dirs)
    if is_in_user_dir or is_repo_root:
        # Still block if we're in specific dangerous system subdirectories
        dangerous_system_dirs = [Path("/System"), Path("/Library"), Path("/usr")]
        for sys_dir in dangerous_system_dirs:
            if cwd == sys_dir or (cwd.is_relative_to(sys_dir) and not is_in_user_dir):
                console.print()
                console.print(
                    Panel.fit(
                        "[bold red]🚨 CRITICAL ERROR[/bold red]\n\n"
                        f"You cannot run dspy-code from system directory: [cyan]{cwd}[/cyan]\n\n"
                        "This could damage your system. Please run from a user project directory.",
                        title="❌ System Directory",
                        border_style="red",
                    )
                )
                sys.exit(1)
        # User directory or repo root is safe
        return

    # Check if running from root or other system directories (not in user dirs)
    system_dirs = [Path("/"), Path("/System"), Path("/Library"), Path("/usr")]
    for sys_dir in system_dirs:
        if cwd == sys_dir or cwd.is_relative_to(sys_dir):
            console.print()
            console.print(
                Panel.fit(
                    "[bold red]🚨 CRITICAL ERROR[/bold red]\n\n"
                    f"You cannot run dspy-code from system directory: [cyan]{cwd}[/cyan]\n\n"
                    "This could damage your system. Please run from a user project directory.",
                    title="❌ System Directory",
                    border_style="red",
                )
            )
            sys.exit(1)

    # Check /var and /private (temp dirs already handled above)
    var_path = Path("/var")
    private_path = Path("/private")

    if cwd == var_path or cwd == private_path:
        console.print()
        console.print(
            Panel.fit(
                "[bold red]🚨 CRITICAL ERROR[/bold red]\n\n"
                f"You cannot run dspy-code from: [cyan]{cwd}[/cyan]\n\n"
                "Please run from a user project directory.",
                title="❌ System Directory",
                border_style="red",
            )
        )
        sys.exit(1)
    elif cwd.is_relative_to(private_path):
        console.print()
        console.print(
            Panel.fit(
                "[bold red]🚨 CRITICAL ERROR[/bold red]\n\n"
                f"You cannot run dspy-code from system directory: [cyan]{cwd}[/cyan]\n\n"
                "Please run from a user project directory.",
                title="❌ System Directory",
                border_style="red",
            )
        )
        sys.exit(1)


def get_version():
    """Get the installed version of dspy-code."""
    try:
        import importlib.metadata

        return importlib.metadata.version("dspy-code")
    except importlib.metadata.PackageNotFoundError:
        # Fallback to __init__.py version if package not installed
        from . import __version__

        return __version__


@click.command()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option(
    "--version",
    is_flag=True,
    help="Show version information and exit",
)
@click.option(
    "--skip-safety-check",
    is_flag=True,
    hidden=True,
    help="Skip directory safety check (not recommended)",
)
def cli(verbose: bool, debug: bool, version: bool, skip_safety_check: bool):
    """
    DSPy Code - Interactive DSPy Development Environment

    🚀 Welcome to DSPy Code! This is a living playbook for DSPy.

    All commands are slash commands in interactive mode:
    • /init - Initialize or scan your DSPy project
    • /create - Generate signatures, modules, or complete programs
    • /connect - Connect to any LLM (Ollama, OpenAI, Anthropic, Gemini)
    • /optimize - Optimize with GEPA
    • /run - Execute your DSPy programs
    • /help - See all available commands

    DSPy Code adapts to YOUR installed DSPy version and gives you access
    to all DSPy features through natural language.
    """
    # Show version and exit if requested
    if version:
        from .core.version_checker import get_dspy_version

        dspy_code_version = get_version()
        dspy_version = get_dspy_version()
        console.print(
            f"[bold cyan]DSPy Code[/bold cyan] version: [green]{dspy_code_version}[/green]"
        )
        if dspy_version:
            console.print(f"[bold cyan]DSPy[/bold cyan] version: [green]{dspy_version}[/green]")
        else:
            console.print("[yellow]DSPy is not installed[/yellow]")
        sys.exit(0)

    # SECURITY: Check if running from safe directory
    if not skip_safety_check:
        check_safe_working_directory()

    # Check for project venv and warn if missing
    from .core.venv_utils import check_project_venv

    has_venv, warning = check_project_venv()
    if not has_venv and warning:
        console.print()
        console.print(
            Panel.fit(
                warning,
                title="⚠️  Virtual Environment Notice",
                border_style="yellow",
            )
        )
        console.print()

    # Setup logging
    setup_logging(verbose=verbose, debug=debug)

    # Always enter interactive mode
    try:
        interactive_command.execute(verbose=verbose, debug=debug)
    except DSPyCLIError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Goodbye![/yellow]")
        sys.exit(0)
    except Exception as e:
        if debug:
            console.print_exception()
        else:
            console.print(f"[red]Unexpected error:[/red] {e}")
            console.print("\n💡 Run with --debug flag for full traceback")
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
