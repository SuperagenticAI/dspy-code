"""
Interactive task collection for DSPy Code.
"""

import json
from dataclasses import dataclass, field
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

from ..core.logging import get_logger
from ..validation import InputValidator, ValidationError

console = Console()
logger = get_logger(__name__)


@dataclass
class FieldDefinition:
    """Definition of an input or output field."""

    name: str
    type: str
    description: str
    constraints: dict[str, Any] | None = None


@dataclass
class TaskDefinition:
    """Complete task definition."""

    description: str
    input_fields: list[FieldDefinition]
    output_fields: list[FieldDefinition]
    complexity: str = "simple"  # simple, complex, multi-step
    domain: str | None = None


@dataclass
class GoldExample:
    """Gold standard example with input/output pair."""

    inputs: dict[str, Any]
    outputs: dict[str, Any]
    explanation: str | None = None


@dataclass
class ReasoningPattern:
    """Reasoning pattern configuration."""

    type: str  # predict, chain_of_thought, react
    config: dict[str, Any] = field(default_factory=dict)


class TaskCollector:
    """Collects task definitions through interactive prompts."""

    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.validator = InputValidator()

    def collect_task_definition(self, initial_task: str | None = None) -> TaskDefinition:
        """
        Collect complete task definition through interactive prompts.

        Args:
            initial_task: Optional initial task description

        Returns:
            Complete task definition
        """
        logger.info("Collecting task definition")

        # Get task description
        if initial_task:
            task_description = initial_task
            console.print(f"[blue]Task:[/blue] {task_description}")
        else:
            task_description = self._collect_task_description()

        # Validate task description
        try:
            task_description = self.validator.validate_task_description(task_description)
        except ValidationError as e:
            console.print(f"[red]Invalid task description:[/red] {e}")
            task_description = self._collect_task_description()

        # Collect input fields
        input_fields = self._collect_fields("input")

        # Collect output fields
        output_fields = self._collect_fields("output")

        # Determine complexity
        complexity = self._determine_complexity(task_description, input_fields, output_fields)

        # Optional domain detection
        domain = self._detect_domain(task_description)

        task_def = TaskDefinition(
            description=task_description,
            input_fields=input_fields,
            output_fields=output_fields,
            complexity=complexity,
            domain=domain,
        )

        # Show summary and confirm
        self._show_task_summary(task_def)

        if not Confirm.ask("Does this look correct?", default=True):
            console.print("[yellow]Let's refine the task definition...[/yellow]")
            return self.collect_task_definition()

        return task_def

    def collect_gold_examples(self, task_def: TaskDefinition) -> list[GoldExample]:
        """
        Collect gold examples for the task.

        Args:
            task_def: Task definition

        Returns:
            List of gold examples
        """
        logger.info("Collecting gold examples")

        console.print("\n[bold]Gold Examples Collection[/bold]")
        console.print("Provide example inputs and expected outputs for your task.")
        console.print("These examples help generate better code and enable optimization.")

        examples = []
        example_num = 1

        while True:
            console.print(f"\n[bold cyan]Example {example_num}[/bold cyan]")

            # Collect inputs
            inputs = {}
            console.print("[bold]Input values:[/bold]")
            for field in task_def.input_fields:
                value = Prompt.ask(f"{field.name} ({field.description})")
                # Convert to appropriate type
                inputs[field.name] = self._convert_field_value(value, field.type)

            # Collect outputs
            outputs = {}
            console.print("[bold]Expected output values:[/bold]")
            for field in task_def.output_fields:
                value = Prompt.ask(f"{field.name} ({field.description})")
                outputs[field.name] = self._convert_field_value(value, field.type)

            # Optional explanation
            explanation = None
            if Confirm.ask("Add explanation for this example?", default=False):
                explanation = Prompt.ask("Explanation")

            # Validate example
            try:
                validated_inputs = self.validator.validate_example_input(
                    inputs, [field.__dict__ for field in task_def.input_fields]
                )
                validated_outputs = self.validator.validate_example_output(
                    outputs, [field.__dict__ for field in task_def.output_fields]
                )

                example = GoldExample(
                    inputs=validated_inputs, outputs=validated_outputs, explanation=explanation
                )
                examples.append(example)

                console.print(f"[green]✓[/green] Example {example_num} added")
                example_num += 1

            except ValidationError as e:
                console.print(f"[red]Invalid example:[/red] {e}")
                if Confirm.ask("Try again?", default=True):
                    continue

            # Ask for more examples
            if len(examples) >= 5:
                console.print(
                    f"[blue]You have {len(examples)} examples. That's usually enough![/blue]"
                )

            if not Confirm.ask("Add another example?", default=len(examples) < 3):
                break

        if examples:
            self._show_examples_summary(examples)

        return examples

    def select_reasoning_pattern(
        self, task_def: TaskDefinition, initial_pattern: str | None = None
    ) -> ReasoningPattern:
        """
        Select appropriate reasoning pattern for the task.

        Args:
            task_def: Task definition
            initial_pattern: Optional initial pattern selection

        Returns:
            Selected reasoning pattern
        """
        logger.info("Selecting reasoning pattern")

        if initial_pattern:
            # Validate provided pattern
            try:
                pattern_type = self.validator.validate_reasoning_pattern(initial_pattern)
                console.print(f"[blue]Using reasoning pattern:[/blue] {pattern_type}")
                return ReasoningPattern(type=pattern_type)
            except ValidationError as e:
                console.print(f"[red]Invalid pattern:[/red] {e}")

        # Show pattern options
        console.print("\n[bold]Reasoning Pattern Selection[/bold]")
        console.print("Choose how the model should approach your task:")

        patterns = {
            "1": {
                "type": "predict",
                "name": "Direct Prediction",
                "description": "Fast, straightforward prediction without explanation",
                "best_for": "Simple classification, quick responses",
            },
            "2": {
                "type": "chain_of_thought",
                "name": "Chain of Thought",
                "description": "Step-by-step reasoning with explanations",
                "best_for": "Complex reasoning, analysis tasks",
            },
            "3": {
                "type": "react",
                "name": "ReAct (Reasoning + Acting)",
                "description": "Can use tools and external data sources",
                "best_for": "Tasks requiring external information",
            },
        }

        # Show pattern table
        table = Table(title="Available Reasoning Patterns")
        table.add_column("Option", style="cyan")
        table.add_column("Pattern", style="white")
        table.add_column("Description", style="white")
        table.add_column("Best For", style="green")

        for key, pattern in patterns.items():
            table.add_row(key, pattern["name"], pattern["description"], pattern["best_for"])

        console.print(table)

        # Get recommendation
        recommendation = self._recommend_pattern(task_def)
        console.print(f"\n[blue]Recommendation:[/blue] {recommendation}")

        # Get user choice
        choice = Prompt.ask("Select reasoning pattern", choices=list(patterns.keys()), default="2")

        selected_pattern = patterns[choice]
        pattern_type = selected_pattern["type"]

        # Get pattern-specific configuration
        config = self._get_pattern_config(pattern_type, task_def)

        console.print(f"[green]✓[/green] Selected: {selected_pattern['name']}")

        return ReasoningPattern(type=pattern_type, config=config)

    def _collect_task_description(self) -> str:
        """Collect task description from user."""
        console.print("\n[bold]Task Description[/bold]")
        console.print("Describe what you want your DSPy component to do.")
        console.print("Be specific about the input and desired output.")

        examples = [
            "Classify customer support emails into categories (billing, technical, general)",
            "Extract key information from research papers (title, authors, abstract)",
            "Generate product descriptions from specifications",
            "Analyze sentiment of social media posts",
        ]

        console.print("\n[blue]Examples:[/blue]")
        for example in examples:
            console.print(f"  • {example}")

        return Prompt.ask("\nWhat task do you want to accomplish?")

    def _collect_fields(self, field_type: str) -> list[FieldDefinition]:
        """Collect field definitions (input or output)."""
        console.print(f"\n[bold]{field_type.title()} Fields[/bold]")
        console.print(f"Define the {field_type} fields for your task.")

        fields = []
        field_num = 1

        while True:
            console.print(f"\n[cyan]{field_type.title()} Field {field_num}[/cyan]")

            # Field name
            while True:
                name = Prompt.ask("Field name")
                try:
                    name = self.validator.validate_field_name(name)
                    break
                except ValidationError as e:
                    console.print(f"[red]Invalid field name:[/red] {e}")

            # Field type
            while True:
                type_hint = Prompt.ask("Field type", default="str")
                try:
                    field_type_validated = self.validator.validate_field_type(type_hint)
                    break
                except ValidationError as e:
                    console.print(f"[red]Invalid field type:[/red] {e}")

            # Field description
            while True:
                description = Prompt.ask("Field description")
                try:
                    description = self.validator.validate_field_description(description)
                    break
                except ValidationError as e:
                    console.print(f"[red]Invalid description:[/red] {e}")

            field = FieldDefinition(name=name, type=field_type_validated, description=description)
            fields.append(field)

            console.print(f"[green]✓[/green] Added {field_type} field: {name}")
            field_num += 1

            # Ask for more fields
            if not Confirm.ask(f"Add another {field_type} field?", default=field_num <= 2):
                break

        return fields

    def _convert_field_value(self, value: str, field_type: str) -> Any:
        """Convert string value to appropriate type."""
        if field_type in ("int", "integer"):
            try:
                return int(value)
            except ValueError:
                return value
        elif field_type == "float":
            try:
                return float(value)
            except ValueError:
                return value
        elif field_type in ("bool", "boolean"):
            return value.lower() in ("true", "1", "yes", "on")
        elif field_type == "list":
            try:
                return json.loads(value) if value.startswith("[") else value.split(",")
            except json.JSONDecodeError:
                return value.split(",")
        else:
            return value

    def _determine_complexity(
        self,
        description: str,
        input_fields: list[FieldDefinition],
        output_fields: list[FieldDefinition],
    ) -> str:
        """Determine task complexity based on description and fields."""
        # Simple heuristics for complexity
        total_fields = len(input_fields) + len(output_fields)

        if total_fields <= 3 and len(description.split()) <= 20:
            return "simple"
        elif total_fields <= 6 and len(description.split()) <= 50:
            return "complex"
        else:
            return "multi-step"

    def _detect_domain(self, description: str) -> str | None:
        """Detect task domain from description."""
        domains = {
            "classification": ["classify", "categorize", "label", "tag"],
            "extraction": ["extract", "parse", "find", "identify"],
            "generation": ["generate", "create", "write", "produce"],
            "analysis": ["analyze", "evaluate", "assess", "review"],
            "translation": ["translate", "convert", "transform"],
        }

        description_lower = description.lower()

        for domain, keywords in domains.items():
            if any(keyword in description_lower for keyword in keywords):
                return domain

        return None

    def _recommend_pattern(self, task_def: TaskDefinition) -> str:
        """Recommend reasoning pattern based on task definition."""
        if task_def.complexity == "simple" and len(task_def.output_fields) == 1:
            return "Direct Prediction - Your task seems straightforward"
        elif task_def.domain in ["analysis", "complex"]:
            return "Chain of Thought - Your task benefits from step-by-step reasoning"
        elif "external" in task_def.description.lower() or "search" in task_def.description.lower():
            return "ReAct - Your task might need external information"
        else:
            return "Chain of Thought - Good default for most tasks"

    def _get_pattern_config(self, pattern_type: str, task_def: TaskDefinition) -> dict[str, Any]:
        """Get pattern-specific configuration."""
        config = {}

        if pattern_type == "chain_of_thought":
            config["reasoning_steps"] = IntPrompt.ask(
                "Number of reasoning steps", default=3, show_default=True
            )
        elif pattern_type == "react":
            config["max_iterations"] = IntPrompt.ask(
                "Maximum tool iterations", default=5, show_default=True
            )

        return config

    def _show_task_summary(self, task_def: TaskDefinition) -> None:
        """Show task definition summary."""
        summary = f"""
[bold]Task Summary[/bold]

Description: {task_def.description}
Complexity: {task_def.complexity}
Domain: {task_def.domain or "General"}

Input Fields ({len(task_def.input_fields)}):
{chr(10).join(f"  • {f.name} ({f.type}): {f.description}" for f in task_def.input_fields)}

Output Fields ({len(task_def.output_fields)}):
{chr(10).join(f"  • {f.name} ({f.type}): {f.description}" for f in task_def.output_fields)}
"""

        console.print(Panel(summary, title="Task Definition", border_style="blue"))

    def _show_examples_summary(self, examples: list[GoldExample]) -> None:
        """Show examples summary."""
        console.print("\n[bold]Examples Summary[/bold]")
        console.print(f"Collected {len(examples)} gold examples:")

        for i, example in enumerate(examples[:3], 1):  # Show first 3
            console.print(f"\n[cyan]Example {i}:[/cyan]")
            console.print(f"  Inputs: {example.inputs}")
            console.print(f"  Outputs: {example.outputs}")
            if example.explanation:
                console.print(f"  Explanation: {example.explanation}")

        if len(examples) > 3:
            console.print(f"\n... and {len(examples) - 3} more examples")
