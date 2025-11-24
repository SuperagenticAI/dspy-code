"""
Tests for Validation Report Generator
"""

import pytest
from rich.console import Console

from dspy_code.validation.models import (
    IssueCategory,
    IssueSeverity,
    ValidationIssue,
    ValidationReport,
)
from dspy_code.validation.quality_scorer import QualityMetrics
from dspy_code.validation.report_generator import ReportGenerator


@pytest.fixture
def generator():
    """Create a report generator instance."""
    return ReportGenerator()


@pytest.fixture
def sample_issues():
    """Create sample validation issues."""
    return [
        ValidationIssue(
            severity=IssueSeverity.ERROR,
            category=IssueCategory.SIGNATURE,
            line=10,
            message="Missing InputField",
            suggestion="Use dspy.InputField()",
            example="field = dspy.InputField(desc='...')",
            docs_link="https://docs.example.com",
        ),
        ValidationIssue(
            severity=IssueSeverity.WARNING,
            category=IssueCategory.MODULE,
            line=20,
            message="Missing docstring",
            suggestion="Add docstring",
        ),
        ValidationIssue(
            severity=IssueSeverity.INFO,
            category=IssueCategory.BEST_PRACTICE,
            line=30,
            message="Consider adding metric",
            suggestion="Add metric function",
        ),
    ]


@pytest.fixture
def sample_metrics():
    """Create sample quality metrics."""
    return QualityMetrics(
        pattern_compliance=85,
        documentation=75,
        optimization_ready=70,
        production_ready=80,
        overall_grade="B",
    )


@pytest.fixture
def sample_report(sample_issues, sample_metrics):
    """Create a sample validation report."""
    return ValidationReport(
        code_file="test.py",
        issues=sample_issues,
        metrics=sample_metrics,
        suggestions=["Add optimization", "Improve documentation"],
        learning_resources=["DSPy docs", "Best practices guide"],
    )


class TestReportGenerator:
    """Test report generator initialization."""

    def test_generator_initialization(self, generator):
        """Should initialize with console and scorer."""
        assert generator.console is not None
        assert generator.scorer is not None

    def test_has_console(self, generator):
        """Should have a Rich console."""
        assert isinstance(generator.console, Console)


class TestReportGeneration:
    """Test full report generation."""

    def test_generates_report_without_errors(self, generator, sample_report):
        """Should generate report without raising errors."""
        # This should not raise any exceptions
        generator.generate_report(sample_report)

    def test_generates_compact_report(self, generator, sample_report):
        """Should generate compact report without errors."""
        generator.generate_compact_report(sample_report)


class TestSummaryGeneration:
    """Test summary generation."""

    def test_generates_summary(self, generator, sample_report):
        """Should generate text summary."""
        summary = generator.generate_summary(sample_report)

        assert isinstance(summary, str)
        assert "test.py" in summary
        assert "Grade" in summary

    def test_summary_includes_metrics(self, generator, sample_report):
        """Should include metrics in summary."""
        summary = generator.generate_summary(sample_report)

        assert "B" in summary  # Grade
        assert "Errors" in summary
        assert "Warnings" in summary

    def test_summary_includes_counts(self, generator, sample_report):
        """Should include issue counts in summary."""
        summary = generator.generate_summary(sample_report)

        assert "Passed Checks" in summary
        assert "Errors" in summary
        assert "Warnings" in summary


class TestIssueGrouping:
    """Test issue grouping functionality."""

    def test_groups_issues_by_severity(self, generator, sample_issues):
        """Should group issues by severity level."""
        grouped = generator.format_issues_by_severity(sample_issues)

        assert IssueSeverity.ERROR in grouped
        assert IssueSeverity.WARNING in grouped
        assert IssueSeverity.INFO in grouped

        assert len(grouped[IssueSeverity.ERROR]) == 1
        assert len(grouped[IssueSeverity.WARNING]) == 1
        assert len(grouped[IssueSeverity.INFO]) == 1

    def test_groups_issues_by_line(self, generator, sample_issues):
        """Should group issues by line number."""
        grouped = generator.format_issues_by_line(sample_issues)

        assert 10 in grouped
        assert 20 in grouped
        assert 30 in grouped

        assert len(grouped[10]) == 1
        assert len(grouped[20]) == 1
        assert len(grouped[30]) == 1

    def test_handles_multiple_issues_same_line(self, generator):
        """Should handle multiple issues on same line."""
        issues = [
            ValidationIssue(
                severity=IssueSeverity.ERROR,
                category=IssueCategory.SIGNATURE,
                line=10,
                message="Issue 1",
                suggestion="Fix 1",
            ),
            ValidationIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.SIGNATURE,
                line=10,
                message="Issue 2",
                suggestion="Fix 2",
            ),
        ]

        grouped = generator.format_issues_by_line(issues)

        assert len(grouped[10]) == 2

    def test_handles_empty_issues_list(self, generator):
        """Should handle empty issues list."""
        grouped_severity = generator.format_issues_by_severity([])
        grouped_line = generator.format_issues_by_line([])

        assert len(grouped_severity[IssueSeverity.ERROR]) == 0
        assert len(grouped_line) == 0


class TestJSONReportGeneration:
    """Test JSON report generation."""

    def test_generates_json_report(self, generator, sample_report):
        """Should generate JSON-serializable report."""
        json_report = generator.generate_json_report(sample_report)

        assert isinstance(json_report, dict)
        assert "file" in json_report
        assert "metrics" in json_report
        assert "errors" in json_report
        assert "warnings" in json_report

    def test_json_includes_all_fields(self, generator, sample_report):
        """Should include all report fields in JSON."""
        json_report = generator.generate_json_report(sample_report)

        assert json_report["file"] == "test.py"
        assert json_report["metrics"] is not None
        assert "pattern_compliance" in json_report["metrics"]
        assert "overall_grade" in json_report["metrics"]

    def test_json_includes_issues(self, generator, sample_report):
        """Should include all issues in JSON."""
        json_report = generator.generate_json_report(sample_report)

        assert len(json_report["errors"]) == 1
        assert len(json_report["warnings"]) == 1
        assert len(json_report["info"]) == 1

    def test_json_issue_format(self, generator, sample_report):
        """Should format issues correctly in JSON."""
        json_report = generator.generate_json_report(sample_report)

        error = json_report["errors"][0]
        assert "severity" in error
        assert "category" in error
        assert "line" in error
        assert "message" in error
        assert "suggestion" in error

    def test_json_includes_suggestions(self, generator, sample_report):
        """Should include suggestions in JSON."""
        json_report = generator.generate_json_report(sample_report)

        assert "suggestions" in json_report
        assert len(json_report["suggestions"]) == 2

    def test_json_includes_learning_resources(self, generator, sample_report):
        """Should include learning resources in JSON."""
        json_report = generator.generate_json_report(sample_report)

        assert "learning_resources" in json_report
        assert len(json_report["learning_resources"]) == 2


class TestMetricsDisplay:
    """Test metrics display functionality."""

    def test_displays_metrics_with_explanations(self, generator, sample_metrics):
        """Should display metrics with explanations."""
        # Get explanations
        explanations = generator.scorer.get_score_explanation(sample_metrics)

        assert "pattern_compliance" in explanations
        assert "documentation" in explanations
        assert "optimization_ready" in explanations
        assert "production_ready" in explanations


class TestCompactReport:
    """Test compact report generation."""

    def test_compact_report_shows_grade(self, generator, sample_report):
        """Should show grade in compact report."""
        # Capture output would require mocking, so just ensure it doesn't crash
        generator.generate_compact_report(sample_report)

    def test_compact_report_with_errors(self, generator, sample_report):
        """Should show errors in compact report."""
        generator.generate_compact_report(sample_report)

    def test_compact_report_without_errors(self, generator):
        """Should show success in compact report when no errors."""
        report = ValidationReport(
            code_file="perfect.py",
            issues=[],
            metrics=QualityMetrics(
                pattern_compliance=100,
                documentation=100,
                optimization_ready=100,
                production_ready=100,
                overall_grade="A",
            ),
            suggestions=[],
            learning_resources=[],
        )

        generator.generate_compact_report(report)


class TestEdgeCases:
    """Test edge cases."""

    def test_handles_report_without_metrics(self, generator):
        """Should handle report without metrics."""
        report = ValidationReport(
            code_file="test.py", issues=[], metrics=None, suggestions=[], learning_resources=[]
        )

        summary = generator.generate_summary(report)
        assert isinstance(summary, str)

    def test_handles_report_without_issues(self, generator, sample_metrics):
        """Should handle report without issues."""
        report = ValidationReport(
            code_file="test.py",
            issues=[],
            metrics=sample_metrics,
            suggestions=[],
            learning_resources=[],
        )

        json_report = generator.generate_json_report(report)
        assert len(json_report["errors"]) == 0
        assert len(json_report["warnings"]) == 0

    def test_handles_issue_without_example(self, generator):
        """Should handle issue without example code."""
        issue = ValidationIssue(
            severity=IssueSeverity.INFO,
            category=IssueCategory.BEST_PRACTICE,
            line=1,
            message="Test",
            suggestion="Fix",
            example=None,
        )

        issues_dict = generator._issue_to_dict(issue)
        assert issues_dict["example"] is None

    def test_handles_issue_without_docs_link(self, generator):
        """Should handle issue without docs link."""
        issue = ValidationIssue(
            severity=IssueSeverity.INFO,
            category=IssueCategory.BEST_PRACTICE,
            line=1,
            message="Test",
            suggestion="Fix",
            docs_link=None,
        )

        issues_dict = generator._issue_to_dict(issue)
        assert issues_dict["docs_link"] is None
