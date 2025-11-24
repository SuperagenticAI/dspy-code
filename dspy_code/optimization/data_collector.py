"""
Interactive data collection for optimization.

Helps users provide training examples for GEPA optimization.
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from ..core.logging import get_logger

console = Console()
logger = get_logger(__name__)


@dataclass
class Example:
    """Training example for optimization."""

    inputs: dict[str, Any]
    output: Any
    metadata: dict[str, Any] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Example":
        """Create from dictionary."""
        return cls(**data)


class DataCollector:
    """Collects training data interactively from user."""

    def __init__(self):
        self.examples: list[Example] = []

    def collect_interactive(self, min_examples: int = 10, max_examples: int = 50) -> list[Example]:
        """
        Collect training examples interactively.

        Args:
            min_examples: Minimum number of examples required
            max_examples: Maximum number of examples to collect

        Returns:
            List of collected examples
        """
        console.print()
        console.print("[bold cyan]📊 Training Data Collection[/bold cyan]\n")
        console.print("Let's collect training examples for optimization.")
        console.print(f"You'll need at least [yellow]{min_examples}[/yellow] examples.\n")

        self.examples = []

        while len(self.examples) < max_examples:
            console.print(f"[bold]Example {len(self.examples) + 1}:[/bold]")

            # Collect inputs
            inputs = self._collect_inputs()
            if inputs is None:
                break

            # Collect output
            output = self._collect_output()
            if output is None:
                break

            # Create example
            example = Example(inputs=inputs, output=output)
            self.examples.append(example)

            console.print(f"[green]✓[/green] Example {len(self.examples)} added\n")

            # Check if we have enough
            if len(self.examples) >= min_examples:
                if not Confirm.ask(f"Add more examples? (have {len(self.examples)})", default=True):
                    break

        # Validate we have enough
        if len(self.examples) < min_examples:
            console.print(f"[yellow]⚠️  Need at least {min_examples} examples[/yellow]")
            return []

        console.print(f"\n[green]✓[/green] Collected {len(self.examples)} examples")
        return self.examples

    def _collect_inputs(self) -> dict[str, Any] | None:
        """Collect input fields."""
        console.print("  [dim]Enter inputs (or 'done' to finish):[/dim]")

        inputs = {}
        while True:
            field_name = Prompt.ask("    Field name", default="done")

            if field_name.lower() == "done":
                if inputs:
                    return inputs
                else:
                    console.print("    [yellow]Need at least one input field[/yellow]")
                    continue

            field_value = Prompt.ask(f"    {field_name} value")
            inputs[field_name] = field_value

            if not Confirm.ask("    Add another input field?", default=False):
                return inputs

    def _collect_output(self) -> Any | None:
        """Collect output value."""
        output = Prompt.ask("  Expected output")
        return output

    def load_from_file(self, file_path: Path) -> list[Example]:
        """
        Load examples from JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            List of examples
        """
        try:
            with open(file_path) as f:
                data = json.load(f)

            if isinstance(data, list):
                self.examples = [Example.from_dict(item) for item in data]
            else:
                raise ValueError("JSON file must contain a list of examples")

            logger.info(f"Loaded {len(self.examples)} examples from {file_path}")
            return self.examples

        except Exception as e:
            logger.error(f"Failed to load examples: {e}")
            raise

    def save_to_file(self, file_path: Path) -> None:
        """
        Save examples to JSON file.

        Args:
            file_path: Path to save JSON file
        """
        try:
            data = [example.to_dict() for example in self.examples]

            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved {len(self.examples)} examples to {file_path}")

        except Exception as e:
            logger.error(f"Failed to save examples: {e}")
            raise

    def validate_examples(self) -> tuple[bool, list[str]]:
        """
        Validate collected examples.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        if not self.examples:
            errors.append("No examples collected")
            return False, errors

        # Check all examples have same input fields
        if len(self.examples) > 1:
            first_inputs = set(self.examples[0].inputs.keys())
            for i, example in enumerate(self.examples[1:], 2):
                if set(example.inputs.keys()) != first_inputs:
                    errors.append(f"Example {i} has different input fields")

        # Check for empty values
        for i, example in enumerate(self.examples, 1):
            if not example.inputs:
                errors.append(f"Example {i} has no inputs")
            if example.output is None or example.output == "":
                errors.append(f"Example {i} has no output")

        is_valid = len(errors) == 0
        return is_valid, errors

    def show_summary(self) -> None:
        """Display summary of collected examples."""
        if not self.examples:
            console.print("[yellow]No examples collected[/yellow]")
            return

        console.print()
        console.print("[bold cyan]Training Data Summary[/bold cyan]\n")
        console.print(f"Total examples: [green]{len(self.examples)}[/green]")

        # Show input fields
        if self.examples:
            input_fields = list(self.examples[0].inputs.keys())
            console.print(f"Input fields: [cyan]{', '.join(input_fields)}[/cyan]")

        # Show sample
        console.print("\n[bold]Sample Examples:[/bold]")
        table = Table(show_header=True)

        if self.examples:
            # Add columns for inputs
            for field in self.examples[0].inputs.keys():
                table.add_column(field, style="cyan")
            table.add_column("Output", style="green")

            # Add rows (first 3 examples)
            for example in self.examples[:3]:
                row = [str(v) for v in example.inputs.values()]
                row.append(str(example.output))
                table.add_row(*row)

        console.print(table)
        console.print()
