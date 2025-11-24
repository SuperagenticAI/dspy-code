"""
Create command for generating DSPy components through interactive task definition.
"""

import json
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from ..core.config import ConfigManager
from ..core.directory_utils import ensure_output_directory
from ..core.exceptions import CodeGenerationError
from ..core.logging import get_logger
from ..models.code_generator import CodeGenerator
from ..models.model_manager import ModelManager
from ..models.task_collector import GoldExample, TaskCollector

console = Console()
logger = get_logger(__name__)


def execute(
    task: str | None = None,
    collect_examples: bool = False,
    reasoning_pattern: str | None = None,
    auto_optimize: bool = False,
    output_path: str | None = None,
    verbose: bool = False,
) -> None:
    """
    Execute the create command to generate DSPy components.

    Args:
        task: Task description
        collect_examples: Whether to collect gold examples
        reasoning_pattern: Reasoning pattern (predict, cot, react)
        auto_optimize: Whether to auto-optimize with GEPA
        output_path: Output file path
        verbose: Enable verbose output
    """
    logger.info("Starting interactive DSPy component creation...")

    # Check if we're in a DSPy project
    config_manager = ConfigManager()
    if not config_manager.is_project_initialized():
        console.print("[red]Error:[/red] No dspy_config.yaml found in current directory.")
        console.print("Run 'dspy-cli init' to create a configuration file.")
        return

    try:
        # Initialize components
        model_manager = ModelManager(config_manager)
        task_collector = TaskCollector(model_manager)
        code_generator = CodeGenerator(model_manager)

        # Show welcome message
        _show_welcome_message()

        # Step 1: Collect task definition
        console.print("\n[bold blue]Step 1: Task Definition[/bold blue]")
        task_definition = task_collector.collect_task_definition(initial_task=task)

        # Step 2: Collect gold examples (optional)
        examples = []
        if collect_examples or Confirm.ask(
            "\nWould you like to provide example inputs and outputs?", default=False
        ):
            console.print("\n[bold blue]Step 2: Gold Examples Collection[/bold blue]")
            examples = task_collector.collect_gold_examples(task_definition)

        # Step 3: Select reasoning pattern
        console.print("\n[bold blue]Step 3: Reasoning Pattern Selection[/bold blue]")
        pattern = task_collector.select_reasoning_pattern(
            task_definition, initial_pattern=reasoning_pattern
        )

        # Step 4: Generate code
        console.print("\n[bold blue]Step 4: Code Generation[/bold blue]")
        with console.status("[bold green]Generating DSPy components..."):
            generated_program = code_generator.generate_from_task(
                task_definition, examples, pattern
            )

        # Step 5: Save generated code
        output_file = _save_generated_code(
            generated_program, task_definition.description, output_path, config_manager
        )

        # Step 6: Show results
        _show_generation_results(generated_program, output_file, examples)

        # Step 7: Optional optimization
        if auto_optimize or (
            examples
            and Confirm.ask("\nWould you like to optimize this program with GEPA?", default=False)
        ):
            console.print("\n[bold blue]Step 5: GEPA Optimization[/bold blue]")
            _run_optimization(output_file, examples, config_manager)

        # Show next steps
        _show_next_steps(output_file)

    except Exception as e:
        logger.error(f"Failed to create DSPy component: {e}")
        raise CodeGenerationError(f"Failed to create DSPy component: {e}")


def _show_welcome_message() -> None:
    """Show welcome message and instructions."""
    welcome_text = """
[bold]Welcome to DSPy Code Interactive Component Creator![/bold]

This tool will guide you through creating DSPy components by:
1. Understanding your task through natural language
2. Optionally collecting example inputs/outputs
3. Selecting the appropriate reasoning pattern
4. Generating optimized DSPy code
5. Optionally optimizing with GEPA

Let's get started!
"""

    console.print(Panel(welcome_text, title="DSPy Code Create", border_style="blue"))


def _save_generated_code(
    generated_program: Any,
    task_description: str,
    output_path: str | None,
    config_manager: ConfigManager,
) -> Path:
    """Save the generated code to a file."""

    if output_path:
        output_file = Path(output_path)
        # Ensure parent directory exists for custom output paths
        output_file.parent.mkdir(parents=True, exist_ok=True)
    else:
        # Generate filename from task description
        safe_name = "".join(c if c.isalnum() or c in "_ " else "" for c in task_description)
        safe_name = "_".join(safe_name.split())[:50].lower()

        # Use on-demand directory creation
        output_dir = ensure_output_directory(config_manager)

        output_file = output_dir / f"{safe_name}.py"

        # Ensure unique filename
        counter = 1
        while output_file.exists():
            output_file = output_dir / f"{safe_name}_{counter}.py"
            counter += 1

    complete_code = f"""\"\"\"
{generated_program.documentation}

Generated by DSPy Code
Task: {task_description}
Reasoning Pattern: {generated_program.reasoning_pattern.type}
\"\"\"

{chr(10).join(generated_program.imports)}

{generated_program.signature_code}

{generated_program.module_code}

{generated_program.program_code}

if __name__ == "__main__":
    # Example usage
{chr(10).join("    " + line for line in generated_program.examples)}
"""

    output_file.write_text(complete_code)

    return output_file


def _show_generation_results(
    generated_program: Any, output_file: Path, examples: list[GoldExample]
) -> None:
    """Show the results of code generation."""

    console.print("\n[green]✓[/green] DSPy component generated successfully!")
    console.print(f"[blue]Output file:[/blue] {output_file}")

    # Show component details
    table = Table(title="Generated Component Details")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Reasoning Pattern", generated_program.reasoning_pattern.type.title())
    table.add_row(
        "Input Fields",
        str(len([f for f in generated_program.signature_code.split("\n") if "InputField" in f])),
    )
    table.add_row(
        "Output Fields",
        str(len([f for f in generated_program.signature_code.split("\n") if "OutputField" in f])),
    )
    table.add_row("Gold Examples", str(len(examples)))
    table.add_row("Dependencies", ", ".join(generated_program.dependencies))

    console.print(table)


def _run_optimization(
    output_file: Path, examples: list[GoldExample], config_manager: ConfigManager
) -> None:
    """Run GEPA optimization on the generated program."""
    try:
        from ..commands.optimize_command import execute as run_optimize

        # Save examples to temporary file
        examples_file = output_file.parent / f"{output_file.stem}_examples.jsonl"

        with open(examples_file, "w") as f:
            for example in examples:
                json.dump({"input": example.inputs, "output": example.outputs}, f)
                f.write("\n")

        # Run optimization
        run_optimize(
            program_path=str(output_file),
            examples_file=str(examples_file),
            max_iterations=config_manager.config.gepa_config.max_iterations,
            metric=config_manager.config.gepa_config.evaluation_metric,
            verbose=True,
        )

    except ImportError:
        console.print(
            "[yellow]GEPA optimization not available. Install with: pip install gepa[/yellow]"
        )
    except Exception as e:
        console.print(f"[red]Optimization failed:[/red] {e}")


def _show_next_steps(output_file: Path) -> None:
    """Show next steps to the user."""
    console.print("\n[bold]Next Steps:[/bold]")
    console.print("1. Test your component:")
    console.print(f"   [cyan]dspy-cli run {output_file} --interactive[/cyan]")
    console.print("\n2. Optimize performance:")
    console.print(f"   [cyan]dspy-cli optimize {output_file}[/cyan]")
    console.print("\n3. Export for sharing:")
    console.print(f"   [cyan]dspy-cli export {output_file}[/cyan]")
    console.print("\n4. View the generated code:")
    console.print(f"   [cyan]cat {output_file}[/cyan]")
