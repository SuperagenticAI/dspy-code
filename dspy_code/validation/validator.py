"""
Main DSPy code validator.
"""

import ast
from pathlib import Path

from .models import IssueCategory, IssueSeverity, QualityMetrics, ValidationIssue, ValidationReport
from .module_validator import ModuleValidator
from .predictor_validator import PredictorValidator
from .signature_validator import SignatureValidator


class DSPyValidator:
    """Main validator for DSPy code."""

    def __init__(self):
        """Initialize the validator."""
        self.signature_validator = SignatureValidator()
        self.module_validator = ModuleValidator()
        self.predictor_validator = PredictorValidator()
        self.validators = []
        # Will be populated with specific validators

    def validate_code(self, code: str, filename: str = "generated.py") -> ValidationReport:
        """
        Validate DSPy code.

        Args:
            code: Python code to validate
            filename: Name of the file being validated

        Returns:
            ValidationReport with issues and metrics
        """
        report = ValidationReport(code_file=filename)

        try:
            # Parse the code
            tree = ast.parse(code)

            # Run all validators
            report = self._validate_ast(tree, code, filename)

            # Calculate quality metrics
            report.metrics = self._calculate_metrics(report)

            # Generate suggestions
            report.suggestions = self._generate_suggestions(report)

            # Add learning resources
            report.learning_resources = self._get_learning_resources(report)

        except SyntaxError as e:
            # Handle syntax errors
            report.issues.append(
                ValidationIssue(
                    severity=IssueSeverity.ERROR,
                    category=IssueCategory.ANTI_PATTERN,
                    line=e.lineno or 0,
                    message=f"Syntax error: {e.msg}",
                    suggestion="Fix the syntax error before validation can proceed",
                    example=None,
                )
            )

        return report

    def validate_file(self, filepath: str) -> ValidationReport:
        """
        Validate a DSPy code file.

        Args:
            filepath: Path to the file to validate

        Returns:
            ValidationReport with issues and metrics
        """
        path = Path(filepath)
        if not path.exists():
            report = ValidationReport(code_file=filepath)
            report.issues.append(
                ValidationIssue(
                    severity=IssueSeverity.ERROR,
                    category=IssueCategory.ANTI_PATTERN,
                    line=0,
                    message=f"File not found: {filepath}",
                    suggestion="Check the file path and try again",
                )
            )
            return report

        code = path.read_text()
        return self.validate_code(code, filepath)

    def _validate_ast(self, tree: ast.AST, code: str, filename: str) -> ValidationReport:
        """
        Validate the AST.

        Args:
            tree: Parsed AST
            code: Original code
            filename: Filename

        Returns:
            ValidationReport with issues
        """
        report = ValidationReport(code_file=filename)

        # Basic validation - check for DSPy imports
        has_dspy_import = self._check_dspy_import(tree)
        if not has_dspy_import:
            report.issues.append(
                ValidationIssue(
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.BEST_PRACTICE,
                    line=1,
                    message="No DSPy import found",
                    suggestion="Add 'import dspy' at the top of your file",
                    example="import dspy",
                )
            )

        # Check for signature classes
        signatures = self._find_signatures(tree)
        if not signatures:
            report.issues.append(
                ValidationIssue(
                    severity=IssueSeverity.INFO,
                    category=IssueCategory.SIGNATURE,
                    line=1,
                    message="No DSPy signatures found",
                    suggestion="Consider defining a signature for your task",
                    example="class MySignature(dspy.Signature):\n    input = dspy.InputField()\n    output = dspy.OutputField()",
                )
            )
        else:
            # Validate each signature
            code_lines = code.split("\n")
            for sig in signatures:
                sig_issues = self.signature_validator.validate(sig, code_lines)
                report.issues.extend(sig_issues)

        # Check for module classes
        modules = self._find_modules(tree)
        if not modules:
            report.issues.append(
                ValidationIssue(
                    severity=IssueSeverity.INFO,
                    category=IssueCategory.MODULE,
                    line=1,
                    message="No DSPy modules found",
                    suggestion="Consider creating a module that inherits from dspy.Module",
                    example="class MyModule(dspy.Module):\n    def __init__(self):\n        super().__init__()\n    def forward(self, input):\n        pass",
                )
            )
        else:
            # Validate each module
            code_lines = code.split("\n")
            for mod in modules:
                mod_issues = self.module_validator.validate(mod, code_lines)
                report.issues.extend(mod_issues)

        # Validate predictor usage
        predictor_issues = self.predictor_validator.validate(tree, code.split("\n"))
        report.issues.extend(predictor_issues)

        return report

    def _check_dspy_import(self, tree: ast.AST) -> bool:
        """Check if dspy is imported."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "dspy":
                        return True
            elif isinstance(node, ast.ImportFrom):
                if node.module == "dspy":
                    return True
        return False

    def _find_signatures(self, tree: ast.AST) -> list[ast.ClassDef]:
        """Find DSPy signature classes."""
        signatures = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if inherits from dspy.Signature
                for base in node.bases:
                    if isinstance(base, ast.Attribute):
                        if base.attr == "Signature":
                            signatures.append(node)
                    elif isinstance(base, ast.Name):
                        if base.id == "Signature":
                            signatures.append(node)
        return signatures

    def _find_modules(self, tree: ast.AST) -> list[ast.ClassDef]:
        """Find DSPy module classes."""
        modules = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if inherits from dspy.Module
                for base in node.bases:
                    if isinstance(base, ast.Attribute):
                        if base.attr == "Module":
                            modules.append(node)
                    elif isinstance(base, ast.Name):
                        if base.id == "Module":
                            modules.append(node)
        return modules

    def _calculate_metrics(self, report: ValidationReport) -> QualityMetrics:
        """Calculate quality metrics from validation report."""
        # Simple scoring for now
        error_count = len(report.errors)
        warning_count = len(report.warnings)

        # Pattern compliance: penalize errors heavily, warnings moderately
        pattern_compliance = max(0, 100 - (error_count * 20) - (warning_count * 5))

        # Documentation: check for docstrings (simplified)
        documentation = 75  # Default score

        # Optimization ready: check for metric functions (simplified)
        optimization_ready = 70  # Default score

        # Production ready: based on errors and warnings
        production_ready = max(0, 100 - (error_count * 15) - (warning_count * 3))

        overall_score = (
            pattern_compliance + documentation + optimization_ready + production_ready
        ) // 4
        grade = QualityMetrics.calculate_grade(overall_score)

        return QualityMetrics(
            pattern_compliance=pattern_compliance,
            documentation=documentation,
            optimization_ready=optimization_ready,
            production_ready=production_ready,
            overall_grade=grade,
        )

    def _generate_suggestions(self, report: ValidationReport) -> list[str]:
        """Generate improvement suggestions."""
        suggestions = []

        if report.errors:
            suggestions.append("Fix all errors before proceeding to production")

        if report.warnings:
            suggestions.append("Address warnings to improve code quality")

        if report.metrics and report.metrics.optimization_ready < 80:
            suggestions.append("Add optimization workflow for better performance")

        if report.metrics and report.metrics.documentation < 80:
            suggestions.append("Improve documentation with docstrings and comments")

        return suggestions

    def _get_learning_resources(self, report: ValidationReport) -> list[str]:
        """Get relevant learning resources."""
        resources = []

        # Add resources based on issues found
        categories = {issue.category for issue in report.issues}

        if IssueCategory.SIGNATURE in categories:
            resources.append("/explain signature - Learn about DSPy signatures")

        if IssueCategory.MODULE in categories:
            resources.append("/explain module - Learn about DSPy modules")

        if IssueCategory.PREDICTOR in categories:
            resources.append("/predictors - See all predictor types")

        resources.append("/examples - Browse complete DSPy programs")

        return resources
