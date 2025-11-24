"""
Test the /models command to verify it works correctly.
"""

from dspy_cli.commands.slash_commands import SlashCommandHandler
from dspy_cli.core.config import ConfigManager
from dspy_cli.models.dspy_reference_loader import DSPyReferenceLoader
from dspy_cli.models.llm_connector import LLMConnector
from rich.console import Console

console = Console()


def test_models_command():
    """Test the /models command."""

    console.print("\n[bold magenta]Testing /models Command[/bold magenta]\n")

    # Initialize components
    config_manager = ConfigManager()
    llm_connector = LLMConnector(config_manager)
    reference_loader = DSPyReferenceLoader()
    slash_handler = SlashCommandHandler(llm_connector, reference_loader, [])

    # Test 1: List all models
    console.print("[bold cyan]Test 1: /models (list all)[/bold cyan]")
    console.print("─" * 60)
    slash_handler.handle_command("/models")

    # Test 2: List Ollama models only
    console.print("\n[bold cyan]Test 2: /models ollama[/bold cyan]")
    console.print("─" * 60)
    slash_handler.handle_command("/models ollama")

    # Test 3: List cloud providers
    console.print("\n[bold cyan]Test 3: /models cloud[/bold cyan]")
    console.print("─" * 60)
    slash_handler.handle_command("/models cloud")

    console.print("\n[bold green]✅ All tests completed![/bold green]\n")


if __name__ == "__main__":
    test_models_command()
