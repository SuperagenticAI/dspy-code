"""
Tests for DSPy code validation.
"""

import pytest

from dspy_code.validation import DSPyValidator, ValidationIssue, ValidationReport
from dspy_code.validation.models import IssueCategory, IssueSeverity


class TestDSPyValidator:
    """Test DSPy validator."""

    def test_validator_initialization(self):
        """Test validator can be initialized."""
        validator = DSPyValidator()
        assert validator is not None

    def test_validate_empty_code(self):
        """Test validating empty code."""
        validator = DSPyValidator()
        report = validator.validate_code("", "test.py")

        assert isinstance(report, ValidationReport)
        assert report.code_file == "test.py"

    def test_validate_simple_dspy_code(self):
        """Test validating simple DSPy code."""
        code = """
import dspy

class MySignature(dspy.Signature):
    input = dspy.InputField()
    output = dspy.OutputField()

class MyModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(MySignature)

    def forward(self, input):
        return self.predictor(input=input)
"""
        validator = DSPyValidator()
        report = validator.validate_code(code, "test.py")

        assert isinstance(report, ValidationReport)
        assert report.metrics is not None
        assert report.metrics.overall_grade in ["A", "B", "C", "D", "F"]

    def test_validate_code_without_dspy_import(self):
        """Test validating code without DSPy import."""
        code = """
def my_function():
    pass
"""
        validator = DSPyValidator()
        report = validator.validate_code(code, "test.py")

        # Should have warning about missing DSPy import
        assert len(report.warnings) > 0
        assert any("DSPy import" in issue.message for issue in report.warnings)

    def test_validate_code_with_syntax_error(self):
        """Test validating code with syntax error."""
        code = """
import dspy
def broken_function(
"""
        validator = DSPyValidator()
        report = validator.validate_code(code, "test.py")

        # Should have syntax error
        assert len(report.errors) > 0
        assert any("Syntax error" in issue.message for issue in report.errors)

    def test_validation_report_properties(self):
        """Test validation report properties."""
        report = ValidationReport(code_file="test.py")

        # Add some issues
        report.issues.append(
            ValidationIssue(
                severity=IssueSeverity.ERROR,
                category=IssueCategory.SIGNATURE,
                line=10,
                message="Test error",
                suggestion="Fix it",
            )
        )

        report.issues.append(
            ValidationIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.MODULE,
                line=20,
                message="Test warning",
                suggestion="Improve it",
            )
        )

        assert len(report.errors) == 1
        assert len(report.warnings) == 1
        assert report.has_errors()

    def test_quality_metrics_grade_calculation(self):
        """Test quality metrics grade calculation."""
        from dspy_code.validation.models import QualityMetrics

        assert QualityMetrics.calculate_grade(95) == "A"
        assert QualityMetrics.calculate_grade(85) == "B"
        assert QualityMetrics.calculate_grade(75) == "C"
        assert QualityMetrics.calculate_grade(65) == "D"
        assert QualityMetrics.calculate_grade(55) == "F"

    def test_validate_file_not_found(self):
        """Test validating non-existent file."""
        validator = DSPyValidator()
        report = validator.validate_file("nonexistent.py")

        assert len(report.errors) > 0
        assert any("not found" in issue.message for issue in report.errors)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
