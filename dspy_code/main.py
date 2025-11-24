"""
Main entry point for DSPy Code.

This module provides the interactive command-line interface for creating, managing,
and optimizing DSPy components through natural language interactions.

All commands are now SLASH COMMANDS in interactive mode!
"""

import sys

import click
from rich.console import Console
from rich.traceback import install

from .commands import interactive_command
from .core.exceptions import DSPyCLIError
from .core.logging import setup_logging

# Install rich traceback handler for better error display
install(show_locals=True)

console = Console()


@click.command()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--debug", is_flag=True, help="Enable debug mode")
def cli(verbose: bool, debug: bool):
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
