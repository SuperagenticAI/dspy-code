"""
DSPy Signature Validator

Validates DSPy signature classes for best practices and correctness.
"""

import ast

from .models import IssueCategory, IssueSeverity, ValidationIssue


class SignatureValidator:
    """Validates DSPy signature classes."""

    def __init__(self):
        """Initialize the signature validator."""

    def validate(
        self, signature_node: ast.ClassDef, code_lines: list[str]
    ) -> list[ValidationIssue]:
        """
        Validate a DSPy signature class.

        Args:
            signature_node: AST node for the signature class
            code_lines: Lines of source code for context

        Returns:
            List of validation issues found
        """
        issues = []

        # Check if signature has docstring
        docstring_issue = self._check_docstring(signature_node)
        if docstring_issue:
            issues.append(docstring_issue)

        # Validate fields
        field_issues = self._validate_fields(signature_node, code_lines)
        issues.extend(field_issues)

        return issues

    def _check_docstring(self, signature_node: ast.ClassDef) -> ValidationIssue | None:
        """Check if signature has a docstring."""
        has_docstring = (
            signature_node.body
            and isinstance(signature_node.body[0], ast.Expr)
            and isinstance(signature_node.body[0].value, ast.Constant)
            and isinstance(signature_node.body[0].value.value, str)
        )

        if not has_docstring:
            return ValidationIssue(
                severity=IssueSeverity.INFO,
                category=IssueCategory.SIGNATURE,
                line=signature_node.lineno,
                message=f"Signature '{signature_node.name}' missing docstring",
                suggestion="Add a docstring explaining the signature's purpose",
                example=f'class {signature_node.name}(dspy.Signature):\n    """Describe what this signature does."""\n    ...',
            )

        return None

    def _validate_fields(
        self, signature_node: ast.ClassDef, code_lines: list[str]
    ) -> list[ValidationIssue]:
        """Validate signature fields."""
        issues = []

        for node in signature_node.body:
            # Skip docstring
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                continue

            # Check for field assignments
            if isinstance(node, ast.AnnAssign):
                field_issues = self._validate_field_assignment(
                    node, signature_node.name, code_lines
                )
                issues.extend(field_issues)
            elif isinstance(node, ast.Assign):
                # Plain assignment without type hint
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        issues.append(
                            ValidationIssue(
                                severity=IssueSeverity.WARNING,
                                category=IssueCategory.SIGNATURE,
                                line=node.lineno,
                                message=f"Field '{target.id}' missing type hint",
                                suggestion=f"Add type hint: {target.id}: str = dspy.InputField()",
                                example=f"{target.id}: str = dspy.InputField(desc='Description')",
                            )
                        )

        return issues

    def _validate_field_assignment(
        self, node: ast.AnnAssign, signature_name: str, code_lines: list[str]
    ) -> list[ValidationIssue]:
        """Validate a field assignment."""
        issues = []

        if not isinstance(node.target, ast.Name):
            return issues

        field_name = node.target.id

        # Check if using InputField or OutputField
        is_dspy_field = self._is_dspy_field(node.value)

        if not is_dspy_field:
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.ERROR,
                    category=IssueCategory.SIGNATURE,
                    line=node.lineno,
                    message=f"Field '{field_name}' not using dspy.InputField or dspy.OutputField",
                    suggestion="Use dspy.InputField() or dspy.OutputField()",
                    example=f"{field_name}: str = dspy.InputField(desc='Description')",
                    docs_link="https://dspy-docs.vercel.app/docs/building-blocks/signatures",
                )
            )
            return issues

        # Check for description parameter
        has_desc = self._has_description(node.value)
        if not has_desc:
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.SIGNATURE,
                    line=node.lineno,
                    message=f"Field '{field_name}' missing description",
                    suggestion="Add desc parameter to help the LM understand the field",
                    example=f"{field_name}: str = dspy.InputField(desc='Description of {field_name}')",
                )
            )

        return issues

    def _is_dspy_field(self, node: ast.expr | None) -> bool:
        """Check if node is a DSPy field (InputField or OutputField)."""
        if node is None:
            return False

        if isinstance(node, ast.Call):
            func = node.func

            # Check for dspy.InputField() or dspy.OutputField()
            if isinstance(func, ast.Attribute):
                if func.attr in ["InputField", "OutputField"]:
                    return True

            # Check for InputField() or OutputField() (imported directly)
            elif isinstance(func, ast.Name):
                if func.id in ["InputField", "OutputField"]:
                    return True

        return False

    def _has_description(self, node: ast.expr | None) -> bool:
        """Check if field call has desc parameter."""
        if not isinstance(node, ast.Call):
            return False

        # Check keyword arguments
        for keyword in node.keywords:
            if keyword.arg == "desc":
                return True

        return False

    def get_field_info(self, signature_node: ast.ClassDef) -> dict:
        """
        Extract field information from signature.

        Returns:
            Dict with field names and types
        """
        fields = {"input_fields": [], "output_fields": [], "other_fields": []}

        for node in signature_node.body:
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                field_name = node.target.id
                field_type = self._get_field_type(node.value)

                if field_type == "input":
                    fields["input_fields"].append(field_name)
                elif field_type == "output":
                    fields["output_fields"].append(field_name)
                else:
                    fields["other_fields"].append(field_name)

        return fields

    def _get_field_type(self, node: ast.expr | None) -> str:
        """Determine if field is input, output, or other."""
        if not isinstance(node, ast.Call):
            return "other"

        func = node.func

        if isinstance(func, ast.Attribute):
            if func.attr == "InputField":
                return "input"
            elif func.attr == "OutputField":
                return "output"
        elif isinstance(func, ast.Name):
            if func.id == "InputField":
                return "input"
            elif func.id == "OutputField":
                return "output"

        return "other"
