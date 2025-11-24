"""
DSPy Best Practices Checker

Checks for DSPy best practices and optimization readiness.
"""

import ast

from .models import IssueCategory, IssueSeverity, ValidationIssue


class BestPracticesChecker:
    """Checks DSPy best practices."""

    def check(self, tree: ast.AST, code_lines: list[str]) -> list[ValidationIssue]:
        """Check for best practices."""
        issues = []

        # Check for metric functions
        if not self._has_metric_function(tree):
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.INFO,
                    category=IssueCategory.BEST_PRACTICE,
                    line=1,
                    message="No metric function found",
                    suggestion="Add a metric function for optimization",
                    example="def accuracy(example, prediction):\n    return example.answer == prediction.answer",
                )
            )

        # Check for error handling
        if not self._has_error_handling(tree):
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.INFO,
                    category=IssueCategory.BEST_PRACTICE,
                    line=1,
                    message="No error handling found",
                    suggestion="Add try/except blocks for robustness",
                    example="try:\n    result = module(input=input)\nexcept Exception as e:\n    print(f'Error: {e}')",
                )
            )

        return issues

    def _has_metric_function(self, tree: ast.AST) -> bool:
        """Check if code has a metric function."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Common metric function names
                if node.name in ["metric", "accuracy", "f1", "precision", "recall"]:
                    return True
                # Check if function has 'example' and 'prediction' parameters
                if len(node.args.args) >= 2:
                    param_names = [arg.arg for arg in node.args.args]
                    if "example" in param_names and "prediction" in param_names:
                        return True
        return False

    def _has_error_handling(self, tree: ast.AST) -> bool:
        """Check if code has error handling."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                return True
        return False
