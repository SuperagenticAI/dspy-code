"""
Initialize command for creating new DSPy projects.
"""

import shutil
from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm, Prompt

from ..core.config import ConfigManager, ProjectConfig
from ..core.exceptions import ProjectError
from ..core.logging import get_logger

console = Console()
logger = get_logger(__name__)


def execute(
    project_name: str | None = None,
    path: str | None = None,
    model_provider: str | None = None,
    model_name: str | None = None,
    api_key: str | None = None,
    fresh: bool = False,
    verbose: bool = False,
) -> None:
    """
    Execute the init command to create a new DSPy project.

    Args:
        project_name: Name of the project
        path: Project directory path
        model_provider: Default model provider
        model_name: Default model name
        api_key: API key for cloud providers
        fresh: Create full project structure (directories, README, examples)
        verbose: Enable verbose output
    """
    logger.info("Initializing new DSPy project...")

    # Determine project directory
    if path:
        project_dir = Path(path).resolve()
    else:
        project_dir = Path.cwd()

    # Get project name
    if not project_name:
        default_name = project_dir.name if project_dir.name != "." else "my-dspy-project"
        project_name = Prompt.ask("Project name", default=default_name, show_default=True)

    # Check if directory exists and has content
    if project_dir.exists() and any(project_dir.iterdir()):
        if not Confirm.ask(f"Directory '{project_dir}' is not empty. Continue?"):
            console.print("[yellow]Project initialization cancelled.[/yellow]")
            return

    # Create project directory
    project_dir.mkdir(parents=True, exist_ok=True)

    # Check if already a DSPy project
    config_manager = ConfigManager(project_dir)
    if config_manager.is_project_initialized():
        if not Confirm.ask("This directory already contains a DSPy project. Reinitialize?"):
            console.print("[yellow]Project initialization cancelled.[/yellow]")
            return

    try:
        # Create configuration
        config = ProjectConfig.create_default(project_name)

        # Configure model if provided
        if model_provider:
            _configure_model(config, model_provider, model_name, api_key)
        else:
            # Interactive model configuration
            _interactive_model_setup(config)

        # Create project based on mode
        if fresh:
            _create_full_project(project_dir, config, config_manager)
            console.print(
                f"[green]✓[/green] DSPy project '{project_name}' initialized successfully!"
            )
            console.print(f"[blue]Project directory:[/blue] {project_dir}")
            console.print(
                "[blue]Created:[/blue] Full project structure with directories, README, and examples"
            )
            console.print(
                "[blue]Config files:[/blue] dspy_config.yaml (active), dspy_config_example.yaml (reference)"
            )
        else:
            _create_minimal_project(project_dir, config, config_manager)
            console.print(
                f"[green]✓[/green] DSPy project '{project_name}' initialized successfully!"
            )
            console.print(f"[blue]Project directory:[/blue] {project_dir}")
            console.print(
                "[blue]Created:[/blue] dspy_config.yaml (minimal), dspy_config_example.yaml (reference)"
            )
            console.print("[dim]Directories will be created as needed[/dim]")

        # Build codebase index with entertaining messages
        _build_codebase_index(project_dir, config_manager)

        # Show next steps
        _show_next_steps(project_name, fresh)

    except Exception as e:
        logger.error(f"Failed to initialize project: {e}")
        raise ProjectError(f"Failed to initialize project: {e}")


def _create_minimal_project(
    project_dir: Path, config: ProjectConfig, config_manager: ConfigManager
) -> None:
    """
    Create a minimal DSPy project with only the configuration file.

    This is the default initialization mode that creates only what's necessary
    to start using dspy-cli. Additional directories will be created on-demand
    when commands need them.

    Args:
        project_dir: The project directory path
        config: The project configuration to save
        config_manager: The config manager instance
    """
    # Save minimal configuration
    config_manager._config = config
    config_manager.save_config(minimal=True)

    # Copy example configuration file for reference
    _copy_example_config(project_dir)


def _create_full_project(
    project_dir: Path, config: ProjectConfig, config_manager: ConfigManager
) -> None:
    """
    Create a full DSPy project with complete directory structure and example files.

    This mode creates the traditional project structure with all directories,
    README, .gitignore, and example files. Use this when starting a new project
    from scratch.

    Args:
        project_dir: The project directory path
        config: The project configuration to save
        config_manager: The config manager instance
    """
    # Create directory structure
    _create_project_structure(project_dir)

    # Save minimal configuration
    config_manager._config = config
    config_manager.save_config(minimal=True)

    # Copy example configuration file for reference
    _copy_example_config(project_dir)

    # Create example files
    _create_example_files(project_dir)


def _copy_example_config(project_dir: Path) -> None:
    """Copy the example configuration file and .env.example to the project directory."""
    try:
        # Get the path to the example config in the package
        import pkg_resources

        example_config_path = pkg_resources.resource_filename(
            "dspy_cli", "templates/dspy_config_example.yaml"
        )
        example_env_path = pkg_resources.resource_filename("dspy_cli", "templates/.env.example")
        example_config_source = Path(example_config_path)
        example_env_source = Path(example_env_path)
    except Exception:
        # Fallback: try relative path from this file
        example_config_source = (
            Path(__file__).parent.parent / "templates" / "dspy_config_example.yaml"
        )
        example_env_source = Path(__file__).parent.parent / "templates" / ".env.example"

    # Copy config example
    if example_config_source.exists():
        example_dest = project_dir / "dspy_config_example.yaml"
        shutil.copy2(example_config_source, example_dest)
    else:
        logger.warning("Could not find example configuration file")

    # Copy .env example
    if example_env_source.exists():
        env_dest = project_dir / ".env.example"
        shutil.copy2(example_env_source, env_dest)
    else:
        logger.warning("Could not find .env.example file")


def _create_project_structure(project_dir: Path) -> None:
    """Create the basic project directory structure."""
    directories = ["src", "data", "examples", "tests", "generated", "docs"]

    for dir_name in directories:
        (project_dir / dir_name).mkdir(exist_ok=True)

    # Create __init__.py files
    (project_dir / "src" / "__init__.py").touch()
    (project_dir / "tests" / "__init__.py").touch()


def _configure_model(
    config: ProjectConfig, provider: str, model_name: str | None, api_key: str | None
) -> None:
    """Configure model settings."""
    if provider == "ollama":
        if model_name:
            config.models.ollama_models = [model_name]
        config.default_model = model_name or "llama2"

    elif provider == "openai":
        if api_key:
            config.models.openai_api_key = api_key
        if model_name:
            config.models.openai_model = model_name
        config.default_model = model_name or config.models.openai_model

    elif provider == "anthropic":
        if api_key:
            config.models.anthropic_api_key = api_key
        if model_name:
            config.models.anthropic_model = model_name
        config.default_model = model_name or config.models.anthropic_model

    elif provider == "gemini":
        if api_key:
            config.models.gemini_api_key = api_key
        if model_name:
            config.models.gemini_model = model_name
        config.default_model = model_name or config.models.gemini_model


def _interactive_model_setup(config: ProjectConfig) -> None:
    """Interactive model configuration setup."""
    console.print("\n[bold]Model Configuration[/bold]")
    console.print("Configure at least one language model to use with DSPy Code.")

    # Ask about model preference
    provider_choices = {
        "1": ("ollama", "Local models via Ollama (free, private)"),
        "2": ("openai", "OpenAI GPT models (requires API key)"),
        "3": ("anthropic", "Anthropic Claude models (requires API key)"),
        "4": ("gemini", "Google Gemini models (requires API key)"),
        "5": ("skip", "Skip for now (configure later)"),
    }

    console.print("\nAvailable model providers:")
    for key, (provider, description) in provider_choices.items():
        console.print(f"  {key}. {description}")

    choice = Prompt.ask(
        "Choose a model provider", choices=list(provider_choices.keys()), default="1"
    )

    provider, _ = provider_choices[choice]

    if provider == "skip":
        console.print(
            "[yellow]Model configuration skipped. Configure later by editing dspy_config.yaml or using '/connect' in interactive mode.[/yellow]"
        )
        return

    if provider == "ollama":
        endpoint = Prompt.ask("Ollama endpoint", default="http://localhost:11434")
        config.models.ollama_endpoint = endpoint

        model = Prompt.ask("Model name", default="llama2")
        config.models.ollama_models = [model]
        config.default_model = model

    else:
        # Cloud providers need API keys
        api_key = Prompt.ask(f"{provider.title()} API key", password=True)

        if provider == "openai":
            config.models.openai_api_key = api_key
            model = Prompt.ask("Model name", default="gpt-4")
            config.models.openai_model = model
            config.default_model = model

        elif provider == "anthropic":
            config.models.anthropic_api_key = api_key
            model = Prompt.ask("Model name", default="claude-3-sonnet-20240229")
            config.models.anthropic_model = model
            config.default_model = model

        elif provider == "gemini":
            config.models.gemini_api_key = api_key
            model = Prompt.ask("Model name", default="gemini-pro")
            config.models.gemini_model = model
            config.default_model = model


def _create_example_files(project_dir: Path) -> None:
    """Create example files and documentation."""

    # Create README.md
    readme_content = f"""# {project_dir.name}

A DSPy project created with DSPy Code.

## Getting Started

1. Create your first DSPy component:
   ```bash
   dspy-cli create
   ```

2. Test your component:
   ```bash
   dspy-cli run generated/your_program.py --interactive
   ```

3. Optimize your component:
   ```bash
   dspy-cli optimize generated/your_program.py
   ```

## Project Structure

- `src/` - Your custom source code
- `data/` - Training and test datasets
- `examples/` - Example inputs and outputs
- `generated/` - DSPy Code generated components
- `tests/` - Test files
- `docs/` - Documentation

## Configuration

Edit `dspy_config.yaml` to configure models and settings.

## Learn More

- [DSPy Documentation](https://dspy-docs.vercel.app/)
- [DSPy Code Guide](https://github.com/dspy-cli/dspy-cli)
"""

    (project_dir / "README.md").write_text(readme_content)

    # Create .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# DSPy Code
dspy_config.yaml
*.log

# API Keys (never commit these!)
.env
*.key
"""

    (project_dir / ".gitignore").write_text(gitignore_content)

    # Create example data file
    example_data = """# Example Gold Examples
# Format: JSON lines with input/output pairs

{"input": {"text": "Hello world"}, "output": {"sentiment": "neutral"}}
{"input": {"text": "I love this!"}, "output": {"sentiment": "positive"}}
{"input": {"text": "This is terrible"}, "output": {"sentiment": "negative"}}
"""

    (project_dir / "examples" / "sample_data.jsonl").write_text(example_data)


def _build_codebase_index(project_dir: Path, config_manager: ConfigManager) -> None:
    """Build codebase index with entertaining messages and jokes."""
    import random
    import time

    from rich.progress import Progress, SpinnerColumn, TextColumn

    # Fun jokes and messages for indexing
    jokes = [
        "🤖 Teaching the AI to read your code... It promises not to judge your variable names!",
        "📚 Scanning your codebase... Found 3 TODOs from 2 years ago. Should we talk about them?",
        "🔍 Indexing files... Your code is beautiful! (The AI made me say that)",
        "🧠 Building knowledge graph... Even understanding that one recursive function you wrote!",
        "⚡ Creating search index... Faster than you can say 'where did I put that function?'",
        "🎯 Analyzing project structure... Yes, we see the 'temporary_final_v3_FINAL.py' file",
        "🚀 Optimizing embeddings... Making your code searchable at the speed of thought!",
        "💡 Learning your patterns... We promise to forget the embarrassing commits",
        "🎨 Mapping your masterpiece... Even the parts you copied from Stack Overflow!",
        "🔮 Preparing RAG system... No, not that kind of rag. The smart AI kind!",
    ]

    console.print()
    console.print("[bold cyan]📖 Building Codebase Knowledge Base[/bold cyan]")
    console.print(
        "[dim]Indexing YOUR installed DSPy version + your project for intelligent Q&A[/dim]"
    )
    console.print()

    # Show what will be indexed
    console.print("[bold]What's being indexed:[/bold]")
    console.print("  • [cyan]Your installed DSPy[/cyan] - Your actual DSPy version for Q&A")
    console.print("  • [cyan]Your installed GEPA[/cyan] - GEPA optimizer (if installed)")
    console.print("  • [cyan]Your project code[/cyan] - Your DSPy programs and modules")
    console.print("  • [cyan]MCP servers[/cyan] - Any configured MCP servers")
    console.print()
    console.print("[dim]💡 This makes the CLI adapt to YOUR DSPy version![/dim]")
    console.print()

    # Show a random joke
    console.print(f"[yellow]{random.choice(jokes)}[/yellow]")
    console.print()

    try:
        from ..rag import CodebaseRAG

        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
        ) as progress:
            task = progress.add_task("Discovering codebases...", total=None)

            # Initialize and build index
            rag = CodebaseRAG(config_manager=config_manager)

            # Update progress messages
            progress.update(task, description="📚 Indexing your installed DSPy...")
            time.sleep(0.3)

            progress.update(task, description="🧬 Indexing your installed GEPA...")
            time.sleep(0.3)

            progress.update(task, description="📁 Scanning your project files...")
            time.sleep(0.3)

            progress.update(
                task, description="🔍 Extracting code structure (classes, functions, signatures)..."
            )
            index = rag.indexer.build_index()

            progress.update(task, description="💾 Saving index to cache...")
            time.sleep(0.3)

            progress.update(task, description="✓ Index built successfully!")

        # Fun completion message
        completion_messages = [
            "🎉 Done! Your code is now searchable. We've memorized everything (the good and the bad)!",
            "✨ Index ready! Now I can find that function faster than you can!",
            "🚀 All set! Your codebase is now part of my knowledge... I've seen things...",
            "💪 Index complete! Ready to generate DSPy code that actually fits your project!",
            "🎊 Finished! I now know your code better than you do. Just kidding... or am I?",
        ]

        console.print()
        console.print(f"[green]{random.choice(completion_messages)}[/green]")
        console.print()

        # Show what users can now do
        console.print("[bold cyan]💡 You can now ask questions about:[/bold cyan]")
        console.print(
            '  • [green]DSPy concepts[/green] - "How do Signatures work?" (from YOUR DSPy version)'
        )
        console.print('  • [green]GEPA optimization[/green] - "How does GEPA evolve prompts?"')
        console.print('  • [green]Your project code[/green] - "What modules do I have?"')
        console.print('  • [green]Code examples[/green] - "Show me a ChainOfThought example"')
        console.print()
        console.print("[dim]The CLI uses YOUR installed DSPy version to answer questions![/dim]")
        console.print()

    except PermissionError as e:
        logger.warning(f"Permission error building codebase index: {e}")
        console.print("[yellow]⚠️  Could not build codebase index (permission denied)[/yellow]")
        console.print()
        console.print("[dim]This can happen if:[/dim]")
        console.print("[dim]  • Installed packages are in a restricted directory[/dim]")
        console.print("[dim]  • Running in a sandboxed environment[/dim]")
        console.print()
        console.print("[green]✓ DSPy Code will still work![/green]")
        console.print("[dim]You just won't be able to ask questions about DSPy internals[/dim]")
        console.print()
    except Exception as e:
        logger.warning(f"Failed to build codebase index: {e}")
        console.print("[yellow]⚠️  Could not build codebase index (this is optional)[/yellow]")
        console.print()
        console.print("[green]✓ DSPy Code will still work![/green]")
        console.print(
            "[dim]Core features (code generation, validation, optimization) are available[/dim]"
        )
        console.print("[dim]You just won't be able to ask questions about DSPy internals[/dim]")
        console.print()


def _show_next_steps(project_name: str, fresh: bool = False) -> None:
    """Show next steps to the user."""
    console.print("\n[bold]Next Steps:[/bold]")
    console.print("1. Review and customize your configuration:")
    console.print("   [cyan]cat dspy_config.yaml[/cyan]")
    console.print("   [dim]See dspy_config_example.yaml for all available options[/dim]")

    console.print("\n2. Create your first DSPy component:")
    console.print("   [cyan]dspy-cli create[/cyan]")

    console.print("\n3. Test model connectivity:")
    console.print("   [cyan]dspy-cli models test <model-name>[/cyan]")

    if fresh:
        console.print("\n4. Explore the project structure:")
        console.print("   - src/ - Your custom source code")
        console.print("   - data/ - Training and test datasets")
        console.print("   - examples/ - Example inputs and outputs")
        console.print("   - generated/ - DSPy Code generated components")

    console.print("\n4. Learn more:" if not fresh else "\n5. Learn more:")
    console.print("   [cyan]dspy-cli --help[/cyan]")
