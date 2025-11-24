"""
Configuration command for managing project settings.
"""

import yaml
from rich.console import Console
from rich.prompt import Confirm
from rich.syntax import Syntax
from rich.table import Table

from ..core.config import ConfigManager
from ..core.exceptions import ConfigurationError
from ..core.logging import get_logger

console = Console()
logger = get_logger(__name__)


def show_config(verbose: bool = False) -> None:
    """
    Display current project configuration.

    Args:
        verbose: Enable verbose output
    """
    logger.info("Displaying project configuration")

    # Check if we're in a DSPy project
    config_manager = ConfigManager()
    if not config_manager.is_project_initialized():
        console.print("[red]Error:[/red] Not in a DSPy project directory.")
        console.print("Run 'dspy-cli init' to initialize a new project.")
        return

    try:
        config = config_manager.config

        # Show basic project info
        console.print("[bold]Project Configuration[/bold]")
        console.print(f"[blue]Name:[/blue] {config.name}")
        console.print(f"[blue]Version:[/blue] {config.version}")
        console.print(f"[blue]DSPy Version:[/blue] {config.dspy_version}")
        console.print(f"[blue]Default Model:[/blue] {config.default_model or 'None'}")
        console.print(f"[blue]Output Directory:[/blue] {config.output_directory}")

        # Show model configurations
        console.print("\n[bold]Model Configurations[/bold]")
        models_table = Table()
        models_table.add_column("Provider", style="cyan")
        models_table.add_column("Configuration", style="white")
        models_table.add_column("Status", style="green")

        models = config.models

        # Ollama
        ollama_status = "✓ Configured" if models.ollama_models else "Not configured"
        ollama_config = f"Endpoint: {models.ollama_endpoint}, Models: {', '.join(models.ollama_models) if models.ollama_models else 'None'}"
        models_table.add_row("Ollama", ollama_config, ollama_status)

        # OpenAI
        openai_status = "✓ Configured" if models.openai_api_key else "Not configured"
        openai_config = (
            f"Model: {models.openai_model}, API Key: {'***' if models.openai_api_key else 'None'}"
        )
        models_table.add_row("OpenAI", openai_config, openai_status)

        # Anthropic
        anthropic_status = "✓ Configured" if models.anthropic_api_key else "Not configured"
        anthropic_config = f"Model: {models.anthropic_model}, API Key: {'***' if models.anthropic_api_key else 'None'}"
        models_table.add_row("Anthropic", anthropic_config, anthropic_status)

        # Gemini
        gemini_status = "✓ Configured" if models.gemini_api_key else "Not configured"
        gemini_config = (
            f"Model: {models.gemini_model}, API Key: {'***' if models.gemini_api_key else 'None'}"
        )
        models_table.add_row("Gemini", gemini_config, gemini_status)

        console.print(models_table)

        # Show GEPA configuration
        console.print("\n[bold]GEPA Optimizer Configuration[/bold]")
        gepa_table = Table()
        gepa_table.add_column("Parameter", style="cyan")
        gepa_table.add_column("Value", style="white")

        gepa = config.gepa_config
        gepa_table.add_row("Max Iterations", str(gepa.max_iterations))
        gepa_table.add_row("Population Size", str(gepa.population_size))
        gepa_table.add_row("Mutation Rate", str(gepa.mutation_rate))
        gepa_table.add_row("Crossover Rate", str(gepa.crossover_rate))
        gepa_table.add_row("Evaluation Metric", gepa.evaluation_metric)

        console.print(gepa_table)

        if verbose:
            # Show full configuration as YAML
            console.print("\n[bold]Full Configuration (YAML)[/bold]")

            # Convert config to dict for display (hide sensitive data)
            config_dict = {
                "name": config.name,
                "version": config.version,
                "dspy_version": config.dspy_version,
                "default_model": config.default_model,
                "output_directory": config.output_directory,
                "models": {
                    "ollama_endpoint": models.ollama_endpoint,
                    "ollama_models": models.ollama_models,
                    "openai_model": models.openai_model,
                    "openai_api_key": "***" if models.openai_api_key else None,
                    "anthropic_model": models.anthropic_model,
                    "anthropic_api_key": "***" if models.anthropic_api_key else None,
                    "gemini_model": models.gemini_model,
                    "gemini_api_key": "***" if models.gemini_api_key else None,
                },
                "gepa_config": {
                    "max_iterations": gepa.max_iterations,
                    "population_size": gepa.population_size,
                    "mutation_rate": gepa.mutation_rate,
                    "crossover_rate": gepa.crossover_rate,
                    "evaluation_metric": gepa.evaluation_metric,
                },
                "template_preferences": config.template_preferences,
            }

            yaml_content = yaml.dump(config_dict, default_flow_style=False, indent=2)
            syntax = Syntax(yaml_content, "yaml", theme="monokai", line_numbers=True)
            console.print(syntax)

        # Show configuration file location
        console.print(f"\n[blue]Configuration file:[/blue] {config_manager.config_path}")

    except Exception as e:
        logger.error(f"Failed to show configuration: {e}")
        raise ConfigurationError(f"Failed to show configuration: {e}")


def reset_config(skip_confirmation: bool = False, verbose: bool = False) -> None:
    """
    Reset configuration to defaults.

    Args:
        skip_confirmation: Skip confirmation prompt
        verbose: Enable verbose output
    """
    logger.info("Resetting project configuration")

    # Check if we're in a DSPy project
    config_manager = ConfigManager()
    if not config_manager.is_project_initialized():
        console.print("[red]Error:[/red] Not in a DSPy project directory.")
        console.print("Run 'dspy-cli init' to initialize a new project.")
        return

    try:
        # Confirm reset
        if not skip_confirmation:
            console.print(
                "[yellow]Warning:[/yellow] This will reset all configuration to defaults."
            )
            console.print("This includes model configurations and API keys.")

            if not Confirm.ask("Are you sure you want to reset the configuration?"):
                console.print("[yellow]Configuration reset cancelled.[/yellow]")
                return

        # Get current project name
        current_name = config_manager.config.name

        # Reset configuration
        config_manager.reset_config()

        console.print("[green]✓[/green] Configuration reset to defaults")

        if verbose:
            console.print(f"[blue]Project name preserved:[/blue] {current_name}")
            console.print(f"[blue]Configuration file:[/blue] {config_manager.config_path}")

        # Show next steps
        console.print("\n[bold]Next Steps:[/bold]")
        console.print("1. Configure models:")
        console.print(
            "   Edit dspy_config.yaml or run '/connect <provider> <model>' in interactive mode"
        )
        console.print("\n2. View configuration:")
        console.print("   [cyan]dspy-cli config show[/cyan]")

    except Exception as e:
        logger.error(f"Failed to reset configuration: {e}")
        raise ConfigurationError(f"Failed to reset configuration: {e}")
