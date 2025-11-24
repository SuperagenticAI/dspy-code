"""
Run command for executing DSPy programs.
"""

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from ..core.config import ConfigManager
from ..core.exceptions import DSPyCLIError
from ..core.logging import get_logger

console = Console()
logger = get_logger(__name__)


def execute(
    program_path: str,
    inputs: dict[str, Any] | None = None,
    interactive: bool = False,
    test_file: str | None = None,
    verbose: bool = False,
) -> None:
    """
    Execute DSPy programs with inputs.

    Args:
        program_path: Path to the DSPy program file
        inputs: Input key-value pairs
        interactive: Enable interactive input mode
        test_file: Path to test dataset file
        verbose: Enable verbose output
    """
    logger.info(f"Executing DSPy program: {program_path}")

    # Check if we're in a DSPy project
    config_manager = ConfigManager()
    if not config_manager.is_project_initialized():
        console.print("[red]Error:[/red] No dspy_config.yaml found in current directory.")
        console.print("Run 'dspy-cli init' to create a configuration file.")
        return

    try:
        program_file = Path(program_path)
        if not program_file.exists():
            raise DSPyCLIError(f"Program file not found: {program_path}")

        # Load the program module
        program_module = _load_program_module(program_file)

        # Find the main program class or function
        program_class = _find_program_class(program_module)

        if test_file:
            # Run with test dataset
            _run_with_test_file(program_class, test_file, verbose)
        elif interactive:
            # Interactive mode
            _run_interactive(program_class, verbose)
        elif inputs:
            # Run with provided inputs
            _run_with_inputs(program_class, inputs, verbose)
        else:
            # Show usage and prompt for mode
            _show_usage_and_prompt(program_class, program_file)

    except Exception as e:
        logger.error(f"Failed to execute program: {e}")
        raise DSPyCLIError(f"Failed to execute program: {e}")


def _load_program_module(program_file: Path):
    """Load a Python module from file."""
    spec = importlib.util.spec_from_file_location("program", program_file)
    if spec is None or spec.loader is None:
        raise DSPyCLIError(f"Cannot load module from {program_file}")

    module = importlib.util.module_from_spec(spec)
    sys.modules["program"] = module
    spec.loader.exec_module(module)

    return module


def _find_program_class(module):
    """Find the main DSPy program class in the module."""
    # Look for classes that inherit from dspy.Module
    import dspy

    program_classes = []
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, type) and issubclass(obj, dspy.Module) and obj != dspy.Module:
            program_classes.append(obj)

    if not program_classes:
        raise DSPyCLIError("No DSPy Module class found in program")

    if len(program_classes) > 1:
        console.print("[yellow]Multiple DSPy Module classes found. Using the first one.[/yellow]")

    return program_classes[0]


def _run_with_inputs(program_class, inputs: dict[str, Any], verbose: bool) -> None:
    """Run program with provided inputs."""
    try:
        # Initialize program
        program = program_class()

        if verbose:
            console.print(f"[blue]Program:[/blue] {program_class.__name__}")
            console.print(f"[blue]Inputs:[/blue] {inputs}")

        # Execute program
        with console.status("[bold green]Running program..."):
            result = program(**inputs)

        # Display results
        _display_results(inputs, result, verbose)

    except Exception as e:
        console.print(f"[red]Execution failed:[/red] {e}")
        if verbose:
            console.print_exception()


def _run_interactive(program_class, verbose: bool) -> None:
    """Run program in interactive mode."""
    console.print(f"\n[bold]Interactive Mode - {program_class.__name__}[/bold]")

    try:
        # Initialize program
        program = program_class()

        # Get signature to understand required inputs
        signature = getattr(program, "signature", None)
        if signature is None:
            # Try to get from predictor
            predictor = getattr(program, "predictor", None)
            if predictor:
                signature = getattr(predictor, "signature", None)

        if signature:
            input_fields = _extract_input_fields(signature)
        else:
            console.print(
                "[yellow]Could not determine input fields. Please provide inputs manually.[/yellow]"
            )
            input_fields = []

        while True:
            console.print("\n" + "=" * 50)

            # Collect inputs
            inputs = {}

            if input_fields:
                console.print("[bold]Enter inputs:[/bold]")
                for field_name, field_info in input_fields.items():
                    description = field_info.get("desc", f"Input for {field_name}")
                    value = Prompt.ask(f"{field_name} ({description})")
                    inputs[field_name] = value
            else:
                # Manual input collection
                console.print("[bold]Enter inputs (key=value format, empty line to finish):[/bold]")
                while True:
                    line = Prompt.ask("Input (or press Enter to finish)", default="")
                    if not line:
                        break

                    if "=" in line:
                        key, value = line.split("=", 1)
                        inputs[key.strip()] = value.strip()
                    else:
                        console.print("[red]Invalid format. Use key=value[/red]")

            if not inputs:
                console.print("[yellow]No inputs provided.[/yellow]")
                continue

            # Execute program
            try:
                with console.status("[bold green]Running program..."):
                    result = program(**inputs)

                # Display results
                _display_results(inputs, result, verbose)

            except Exception as e:
                console.print(f"[red]Execution failed:[/red] {e}")
                if verbose:
                    console.print_exception()

            # Ask to continue
            if Prompt.ask("\nRun again?", choices=["y", "n"], default="y") != "y":
                break

    except KeyboardInterrupt:
        console.print("\n[yellow]Interactive session ended.[/yellow]")


def _run_with_test_file(program_class, test_file: str, verbose: bool) -> None:
    """Run program with test dataset file."""
    test_path = Path(test_file)
    if not test_path.exists():
        raise DSPyCLIError(f"Test file not found: {test_file}")

    try:
        # Load test data
        test_cases = []
        with open(test_path) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                try:
                    test_case = json.loads(line)
                    test_cases.append(test_case)
                except json.JSONDecodeError as e:
                    console.print(f"[yellow]Warning: Invalid JSON on line {line_num}: {e}[/yellow]")

        if not test_cases:
            console.print("[yellow]No valid test cases found in file.[/yellow]")
            return

        console.print(f"[blue]Running {len(test_cases)} test cases...[/blue]")

        # Initialize program
        program = program_class()

        # Run test cases
        results = []
        for i, test_case in enumerate(test_cases, 1):
            inputs = test_case.get("input", {})
            expected = test_case.get("output", {})

            try:
                with console.status(f"[bold green]Running test case {i}/{len(test_cases)}..."):
                    result = program(**inputs)

                results.append(
                    {
                        "case": i,
                        "inputs": inputs,
                        "expected": expected,
                        "actual": result,
                        "success": True,
                    }
                )

            except Exception as e:
                results.append(
                    {
                        "case": i,
                        "inputs": inputs,
                        "expected": expected,
                        "actual": None,
                        "error": str(e),
                        "success": False,
                    }
                )

        # Display test results
        _display_test_results(results, verbose)

    except Exception as e:
        console.print(f"[red]Test execution failed:[/red] {e}")
        if verbose:
            console.print_exception()


def _extract_input_fields(signature) -> dict[str, dict[str, Any]]:
    """Extract input fields from DSPy signature."""
    input_fields = {}

    # This is a simplified extraction - in a real implementation,
    # you'd need to properly parse the DSPy signature
    if hasattr(signature, "__annotations__"):
        for name, annotation in signature.__annotations__.items():
            if hasattr(annotation, "desc"):
                input_fields[name] = {"desc": annotation.desc}
            else:
                input_fields[name] = {"desc": f"Input field {name}"}

    return input_fields


def _display_results(inputs: dict[str, Any], result: Any, verbose: bool) -> None:
    """Display execution results."""
    console.print("\n[bold green]Results:[/bold green]")

    # Create results table
    table = Table(title="Execution Results")
    table.add_column("Type", style="cyan")
    table.add_column("Content", style="white")

    # Add inputs
    if verbose:
        for key, value in inputs.items():
            table.add_row(f"Input: {key}", str(value))

    # Add outputs
    if hasattr(result, "__dict__"):
        # DSPy result object
        for key, value in result.__dict__.items():
            if not key.startswith("_"):
                table.add_row(f"Output: {key}", str(value))
    elif isinstance(result, dict):
        # Dictionary result
        for key, value in result.items():
            table.add_row(f"Output: {key}", str(value))
    else:
        # Simple result
        table.add_row("Output", str(result))

    console.print(table)


def _display_test_results(results: list, verbose: bool) -> None:
    """Display test execution results."""
    successful = sum(1 for r in results if r["success"])
    total = len(results)

    console.print(f"\n[bold]Test Results: {successful}/{total} passed[/bold]")

    # Summary table
    table = Table(title="Test Summary")
    table.add_column("Case", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Details", style="white")

    for result in results:
        case_num = result["case"]
        if result["success"]:
            status = "[green]✓ PASS[/green]"
            details = "Executed successfully"
        else:
            status = "[red]✗ FAIL[/red]"
            details = result.get("error", "Unknown error")

        table.add_row(str(case_num), status, details)

    console.print(table)

    if verbose and results:
        # Show detailed results for first few cases
        console.print("\n[bold]Detailed Results (first 3 cases):[/bold]")
        for result in results[:3]:
            case_panel = f"""
Case {result["case"]}:
Inputs: {result["inputs"]}
Expected: {result.get("expected", "N/A")}
Actual: {result.get("actual", result.get("error", "N/A"))}
"""
            console.print(Panel(case_panel, title=f"Case {result['case']}", border_style="blue"))


def _show_usage_and_prompt(program_class, program_file: Path) -> None:
    """Show usage information and prompt for execution mode."""
    console.print(f"\n[bold]DSPy Program: {program_class.__name__}[/bold]")
    console.print(f"[blue]File:[/blue] {program_file}")

    console.print("\n[bold]Execution Options:[/bold]")
    console.print("1. Interactive mode - Enter inputs interactively")
    console.print("2. Command line inputs - Provide inputs as arguments")
    console.print("3. Test file - Run with a test dataset")

    console.print("\n[bold]Examples:[/bold]")
    console.print(f"[cyan]dspy-cli run {program_file} --interactive[/cyan]")
    console.print(
        f"[cyan]dspy-cli run {program_file} --input key1=value1 --input key2=value2[/cyan]"
    )
    console.print(f"[cyan]dspy-cli run {program_file} --test-file examples/test_data.jsonl[/cyan]")

    # Offer to run interactively
    from rich.prompt import Confirm

    if Confirm.ask("\nWould you like to run in interactive mode now?", default=True):
        _run_interactive(program_class, verbose=True)
