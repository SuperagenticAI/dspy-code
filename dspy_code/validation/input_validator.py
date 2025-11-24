"""
Input validation for task collection.

Provides validation methods for user input during interactive task collection.
"""

from typing import Any


class ValidationError(Exception):
    """Raised when validation fails."""


class InputValidator:
    """Validates user input during task collection."""

    def validate_task_description(self, description: str) -> str:
        """Validate task description."""
        if not description or not description.strip():
            raise ValidationError("Task description cannot be empty")
        return description.strip()

    def validate_field_name(self, name: str) -> str:
        """Validate field name."""
        if not name or not name.strip():
            raise ValidationError("Field name cannot be empty")

        # Check for valid Python identifier
        name = name.strip()
        if not name.isidentifier():
            raise ValidationError(f"'{name}' is not a valid Python identifier")

        return name

    def validate_field_type(self, type_hint: str) -> str:
        """Validate field type."""
        if not type_hint or not type_hint.strip():
            raise ValidationError("Field type cannot be empty")

        # Accept common types
        valid_types = ["str", "int", "float", "bool", "list", "dict", "Any"]
        type_hint = type_hint.strip()

        # Basic validation - just check it's not empty
        # More complex type validation could be added here
        return type_hint

    def validate_field_description(self, description: str) -> str:
        """Validate field description."""
        if not description or not description.strip():
            raise ValidationError("Field description cannot be empty")
        return description.strip()

    def validate_example_input(
        self, inputs: dict[str, Any], field_defs: list[dict]
    ) -> dict[str, Any]:
        """Validate example input against field definitions."""
        # Basic validation - ensure all required fields are present
        field_names = {f["name"] for f in field_defs}
        input_names = set(inputs.keys())

        missing = field_names - input_names
        if missing:
            raise ValidationError(f"Missing required input fields: {', '.join(missing)}")

        return inputs

    def validate_example_output(
        self, outputs: dict[str, Any], field_defs: list[dict]
    ) -> dict[str, Any]:
        """Validate example output against field definitions."""
        # Basic validation - ensure all required fields are present
        field_names = {f["name"] for f in field_defs}
        output_names = set(outputs.keys())

        missing = field_names - output_names
        if missing:
            raise ValidationError(f"Missing required output fields: {', '.join(missing)}")

        return outputs

    def validate_reasoning_pattern(self, pattern: str) -> str:
        """Validate reasoning pattern."""
        if not pattern or not pattern.strip():
            raise ValidationError("Reasoning pattern cannot be empty")

        pattern = pattern.strip().lower()

        # Valid reasoning patterns
        valid_patterns = [
            "predict",
            "chain_of_thought",
            "cot",
            "react",
            "program_of_thought",
            "pot",
        ]

        if pattern not in valid_patterns:
            raise ValidationError(
                f"Invalid reasoning pattern '{pattern}'. "
                f"Valid patterns: {', '.join(valid_patterns)}"
            )

        # Normalize pattern names
        if pattern == "cot":
            pattern = "chain_of_thought"
        elif pattern == "pot":
            pattern = "program_of_thought"

        return pattern
