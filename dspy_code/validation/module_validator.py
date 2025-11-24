"""
DSPy Module Validator

Validates DSPy module classes for best practices and correctness.
"""

import ast

from .models import IssueCategory, IssueSeverity, ValidationIssue


class ModuleValidator:
    """Validates DSPy module classes."""

    def __init__(self):
        """Initialize the module validator."""

    def validate(self, module_node: ast.ClassDef, code_lines: list[str]) -> list[ValidationIssue]:
        """
        Validate a DSPy module class.

        Args:
            module_node: AST node for the module class
            code_lines: Lines of source code for context

        Returns:
            List of validation issues found
        """
        issues = []

        # Check if module has docstring
        docstring_issue = self._check_docstring(module_node)
        if docstring_issue:
            issues.append(docstring_issue)

        # Check for dspy.Module inheritance
        inheritance_issue = self._check_inheritance(module_node)
        if inheritance_issue:
            issues.append(inheritance_issue)
            # If not inheriting from dspy.Module, skip other checks
            return issues

        # Check for __init__ method
        init_issues = self._check_init_method(module_node)
        issues.extend(init_issues)

        # Check for forward method
        forward_issue = self._check_forward_method(module_node)
        if forward_issue:
            issues.append(forward_issue)

        return issues

    def _check_docstring(self, module_node: ast.ClassDef) -> ValidationIssue | None:
        """Check if module has a docstring."""
        has_docstring = (
            module_node.body
            and isinstance(module_node.body[0], ast.Expr)
            and isinstance(module_node.body[0].value, ast.Constant)
            and isinstance(module_node.body[0].value.value, str)
        )

        if not has_docstring:
            return ValidationIssue(
                severity=IssueSeverity.INFO,
                category=IssueCategory.MODULE,
                line=module_node.lineno,
                message=f"Module '{module_node.name}' missing docstring",
                suggestion="Add a docstring explaining the module's purpose",
                example=f'class {module_node.name}(dspy.Module):\n    """Describe what this module does."""\n    ...',
            )

        return None

    def _check_inheritance(self, module_node: ast.ClassDef) -> ValidationIssue | None:
        """Check if module inherits from dspy.Module."""
        inherits_from_module = False

        for base in module_node.bases:
            if isinstance(base, ast.Attribute):
                if base.attr == "Module":
                    inherits_from_module = True
                    break
            elif isinstance(base, ast.Name):
                if base.id == "Module":
                    inherits_from_module = True
                    break

        if not inherits_from_module:
            return ValidationIssue(
                severity=IssueSeverity.ERROR,
                category=IssueCategory.MODULE,
                line=module_node.lineno,
                message=f"Module '{module_node.name}' must inherit from dspy.Module",
                suggestion="Add dspy.Module as base class",
                example=f"class {module_node.name}(dspy.Module):\n    ...",
                docs_link="https://dspy-docs.vercel.app/docs/building-blocks/modules",
            )

        return None

    def _check_init_method(self, module_node: ast.ClassDef) -> list[ValidationIssue]:
        """Check __init__ method."""
        issues = []

        # Find __init__ method
        init_method = None
        for node in module_node.body:
            if isinstance(node, ast.FunctionDef) and node.name == "__init__":
                init_method = node
                break

        if not init_method:
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.MODULE,
                    line=module_node.lineno,
                    message=f"Module '{module_node.name}' missing __init__ method",
                    suggestion="Add __init__ method to initialize predictors",
                    example="def __init__(self):\n    super().__init__()\n    self.predictor = dspy.Predict(Signature)",
                )
            )
            return issues

        # Check for super().__init__() call
        has_super_init = self._has_super_init(init_method)
        if not has_super_init:
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.ERROR,
                    category=IssueCategory.MODULE,
                    line=init_method.lineno,
                    message="__init__ method must call super().__init__()",
                    suggestion="Add super().__init__() as first line in __init__",
                    example="def __init__(self):\n    super().__init__()\n    # Your initialization code",
                )
            )

        return issues

    def _has_super_init(self, init_method: ast.FunctionDef) -> bool:
        """Check if __init__ calls super().__init__()."""
        for node in ast.walk(init_method):
            if isinstance(node, ast.Call):
                # Check for super().__init__()
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == "__init__":
                        if isinstance(node.func.value, ast.Call):
                            if isinstance(node.func.value.func, ast.Name):
                                if node.func.value.func.id == "super":
                                    return True
        return False

    def _check_forward_method(self, module_node: ast.ClassDef) -> ValidationIssue | None:
        """Check for forward method."""
        has_forward = False

        for node in module_node.body:
            if isinstance(node, ast.FunctionDef) and node.name == "forward":
                has_forward = True
                break

        if not has_forward:
            return ValidationIssue(
                severity=IssueSeverity.ERROR,
                category=IssueCategory.MODULE,
                line=module_node.lineno,
                message=f"Module '{module_node.name}' missing forward() method",
                suggestion="Add forward() method to define module behavior",
                example="def forward(self, input):\n    return self.predictor(input=input)",
                docs_link="https://dspy-docs.vercel.app/docs/building-blocks/modules",
            )

        return None

    def get_module_info(self, module_node: ast.ClassDef) -> dict:
        """
        Extract module information.

        Returns:
            Dict with module details
        """
        info = {
            "name": module_node.name,
            "has_init": False,
            "has_forward": False,
            "predictors": [],
            "methods": [],
        }

        for node in module_node.body:
            if isinstance(node, ast.FunctionDef):
                info["methods"].append(node.name)
                if node.name == "__init__":
                    info["has_init"] = True
                    # Look for predictor assignments
                    info["predictors"] = self._find_predictors(node)
                elif node.name == "forward":
                    info["has_forward"] = True

        return info

    def _find_predictors(self, init_method: ast.FunctionDef) -> list[str]:
        """Find predictor assignments in __init__."""
        predictors = []

        for node in ast.walk(init_method):
            if isinstance(node, ast.Assign):
                # Check if assigning a DSPy predictor
                if isinstance(node.value, ast.Call):
                    if self._is_predictor_call(node.value):
                        for target in node.targets:
                            if isinstance(target, ast.Attribute):
                                predictors.append(target.attr)

        return predictors

    def _is_predictor_call(self, call_node: ast.Call) -> bool:
        """Check if call is creating a DSPy predictor."""
        predictor_names = [
            "Predict",
            "ChainOfThought",
            "ReAct",
            "ProgramOfThought",
            "CodeAct",
            "MultiChainComparison",
            "BestOfN",
            "Refine",
            "KNN",
            "Parallel",
        ]

        func = call_node.func

        if isinstance(func, ast.Attribute):
            if func.attr in predictor_names:
                return True
        elif isinstance(func, ast.Name):
            if func.id in predictor_names:
                return True

        return False
