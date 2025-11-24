"""
Models command for managing language model configurations.
"""

from rich.console import Console
from rich.table import Table

from ..core.config import ConfigManager
from ..core.exceptions import ModelError
from ..core.logging import get_logger
from ..models.model_manager import ModelManager

# from ..validation import ConfigValidator  # Not implemented yet

console = Console()
logger = get_logger(__name__)


def add_model(
    provider_type: str,
    model_name: str,
    api_key: str | None = None,
    endpoint: str | None = None,
    verbose: bool = False,
) -> None:
    """
    Add a new model configuration.

    Args:
        provider_type: Type of model provider (ollama, openai, anthropic, gemini)
        model_name: Name of the model
        api_key: API key for cloud providers
        endpoint: Endpoint URL for Ollama
        verbose: Enable verbose output
    """
    logger.info(f"Adding {provider_type} model: {model_name}")

    # Check if we're in a DSPy project
    config_manager = ConfigManager()
    if not config_manager.is_project_initialized():
        console.print("[red]Error:[/red] Not in a DSPy project directory.")


def list_models(verbose: bool = False) -> None:
    """
    List all configured models.

    Args:
        verbose: Enable verbose output
    """
    logger.info("Listing configured models")

    # Check if we're in a DSPy project
    config_manager = ConfigManager()
    if not config_manager.is_project_initialized():
        console.print("[red]Error:[/red] Not in a DSPy project directory.")
        console.print("Run 'dspy-cli init' to initialize a new project.")
        return

    try:
        config = config_manager.config
        models = config.models

        # Create table
        table = Table(title="Configured Models")
        table.add_column("Provider", style="cyan")
        table.add_column("Model", style="white")
        table.add_column("Status", style="green")
        table.add_column("Default", style="yellow")

        # Add Ollama models
        if models.ollama_models:
            for model in models.ollama_models:
                is_default = "✓" if config.default_model == model else ""
                table.add_row("Ollama", model, "Configured", is_default)

        # Add cloud models
        cloud_providers = [
            ("OpenAI", models.openai_model, models.openai_api_key),
            ("Anthropic", models.anthropic_model, models.anthropic_api_key),
            ("Gemini", models.gemini_model, models.gemini_api_key),
        ]

        for provider, model, api_key in cloud_providers:
            if api_key:
                is_default = "✓" if config.default_model == model else ""
                status = "Configured" if api_key else "Not configured"
                table.add_row(provider, model, status, is_default)

        console.print(table)

        if verbose:
            console.print(f"\n[blue]Default model:[/blue] {config.default_model or 'None'}")
            console.print(f"[blue]Ollama endpoint:[/blue] {models.ollama_endpoint}")

        # Show configuration hints
        if not any(
            [
                models.ollama_models,
                models.openai_api_key,
                models.anthropic_api_key,
                models.gemini_api_key,
            ]
        ):
            console.print("\n[yellow]No models configured.[/yellow]")
            console.print(
                "Add models by editing dspy_config.yaml or using /connect in interactive mode."
            )

    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise ModelError(f"Failed to list models: {e}")


def test_model(model_name: str, verbose: bool = False) -> None:
    """
    Test connectivity to a specific model.

    Args:
        model_name: Name of the model to test
        verbose: Enable verbose output
    """
    logger.info(f"Testing model connectivity: {model_name}")

    # Check if we're in a DSPy project
    config_manager = ConfigManager()
    if not config_manager.is_project_initialized():
        console.print("[red]Error:[/red] Not in a DSPy project directory.")
        console.print("Run 'dspy-cli init' to initialize a new project.")
        return

    try:
        # Initialize model manager
        model_manager = ModelManager(config_manager)

        with console.status(f"[bold green]Testing {model_name}..."):
            # Test model connectivity
            success, message = model_manager.test_model(model_name)

        if success:
            console.print(f"[green]✓[/green] {model_name}: {message}")
        else:
            console.print(f"[red]✗[/red] {model_name}: {message}")

        if verbose and success:
            # Get model info
            model_info = model_manager.get_model_info(model_name)
            if model_info:
                console.print(f"[blue]Provider:[/blue] {model_info.get('provider', 'Unknown')}")
                console.print(f"[blue]Type:[/blue] {model_info.get('type', 'Unknown')}")
                if "endpoint" in model_info:
                    console.print(f"[blue]Endpoint:[/blue] {model_info['endpoint']}")

    except Exception as e:
        logger.error(f"Failed to test model: {e}")
        console.print(f"[red]✗[/red] {model_name}: Connection failed - {e}")


def set_default_model(model_name: str, verbose: bool = False) -> None:
    """
    Set the default model for the current project.

    Args:
        model_name: Name of the model to set as default
        verbose: Enable verbose output
    """
    logger.info(f"Setting default model: {model_name}")

    # Check if we're in a DSPy project
    config_manager = ConfigManager()
    if not config_manager.is_project_initialized():
        console.print("[red]Error:[/red] Not in a DSPy project directory.")
        console.print("Run 'dspy-cli init' to initialize a new project.")
        return

    try:
        # Verify model exists
        model_manager = ModelManager(config_manager)
        if not model_manager.is_model_configured(model_name):
            console.print(f"[red]Error:[/red] Model '{model_name}' is not configured.")
            console.print(
                "Define it in dspy_config.yaml or connect via /connect in interactive mode first."
            )
            return

        # Update configuration
        config_manager.update_config(default_model=model_name)

        console.print(f"[green]✓[/green] Default model set to: {model_name}")

        if verbose:
            console.print(f"[blue]Previous default:[/blue] {config_manager.config.default_model}")

    except Exception as e:
        logger.error(f"Failed to set default model: {e}")
        raise ModelError(f"Failed to set default model: {e}")
