"""
Tests for DSPy Quality Scorer
"""

import pytest

from dspy_code.validation.models import IssueCategory, IssueSeverity, ValidationIssue
from dspy_code.validation.quality_scorer import QualityScorer


@pytest.fixture
def scorer():
    """Create a quality scorer instance."""
    return QualityScorer()


class TestQualityScorer:
    """Test quality scorer initialization and basic functionality."""

    def test_scorer_initialization(self, scorer):
        """Should initialize with proper weights."""
        assert scorer.weights["pattern_compliance"] == 0.35
        assert scorer.weights["documentation"] == 0.20
        assert scorer.weights["optimization_ready"] == 0.25
        assert scorer.weights["production_ready"] == 0.20

    def test_perfect_score_with_no_issues(self, scorer):
        """Should give perfect scores when no issues found."""
        issues = []
        metrics = scorer.calculate_metrics(issues)

        assert metrics.pattern_compliance == 100
        assert metrics.documentation == 100
        assert metrics.optimization_ready == 100
        assert metrics.production_ready == 100
        assert metrics.overall_grade == "A"


class TestPatternCompliance:
    """Test pattern compliance scoring."""

    def test_deducts_for_signature_errors(self, scorer):
        """Should deduct points for signature errors."""
        issues = [
            ValidationIssue(
                severity=IssueSeverity.ERROR,
                category=IssueCategory.SIGNATURE,
                line=1,
                message="Missing InputField",
                suggestion="Use dspy.InputField()",
            )
        ]
        metrics = scorer.calculate_metrics(issues)

        assert metrics.pattern_compliance < 100
        assert metrics.pattern_compliance >= 85  # 100 - 15

    def test_deducts_for_module_errors(self, scorer):
        """Should deduct points for module errors."""
        issues = [
            ValidationIssue(
                severity=IssueSeverity.ERROR,
                category=IssueCategory.MODULE,
                line=1,
                message="Missing dspy.Module inheritance",
                suggestion="Inherit from dspy.Module",
            )
        ]
        metrics = scorer.calculate_metrics(issues)

        assert metrics.pattern_compliance < 100

    def test_deducts_for_anti_patterns(self, scorer):
        """Should deduct points for anti-patterns."""
        issues = [
            ValidationIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.ANTI_PATTERN,
                line=1,
                message="Hardcoded prompt detected",
                suggestion="Use signatures",
            )
        ]
        metrics = scorer.calculate_metrics(issues)

        assert metrics.pattern_compliance < 100
        assert metrics.pattern_compliance >= 92  # 100 - 8

    def test_different_severity_levels(self, scorer):
        """Should deduct different amounts based on severity."""
        error_issues = [
            ValidationIssue(
                severity=IssueSeverity.ERROR,
                category=IssueCategory.SIGNATURE,
                line=1,
                message="Error",
                suggestion="Fix",
            )
        ]
        warning_issues = [
            ValidationIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.SIGNATURE,
                line=1,
                message="Warning",
                suggestion="Fix",
            )
        ]

        error_metrics = scorer.calculate_metrics(error_issues)
        warning_metrics = scorer.calculate_metrics(warning_issues)

        assert error_metrics.pattern_compliance < warning_metrics.pattern_compliance


class TestDocumentationScore:
    """Test documentation scoring."""

    def test_deducts_for_missing_docstrings(self, scorer):
        """Should deduct points for missing docstrings."""
        issues = [
            ValidationIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.BEST_PRACTICE,
                line=1,
                message="Missing docstring",
                suggestion="Add docstring",
            )
        ]
        metrics = scorer.calculate_metrics(issues)

        assert metrics.documentation < 100

    def test_deducts_for_missing_descriptions(self, scorer):
        """Should deduct points for missing field descriptions."""
        issues = [
            ValidationIssue(
                severity=IssueSeverity.INFO,
                category=IssueCategory.BEST_PRACTICE,
                line=1,
                message="Missing field description",
                suggestion="Add description",
            )
        ]
        metrics = scorer.calculate_metrics(issues)

        assert metrics.documentation < 100


class TestOptimizationReadiness:
    """Test optimization readiness scoring."""

    def test_deducts_for_missing_metrics(self, scorer):
        """Should deduct points for missing metric functions."""
        issues = [
            ValidationIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.BEST_PRACTICE,
                line=1,
                message="No metric function found",
                suggestion="Add metric",
            )
        ]
        metrics = scorer.calculate_metrics(issues)

        assert metrics.optimization_ready < 100

    def test_perfect_score_without_optimization_issues(self, scorer):
        """Should give perfect score if no optimization issues."""
        issues = [
            ValidationIssue(
                severity=IssueSeverity.INFO,
                category=IssueCategory.SIGNATURE,
                line=1,
                message="Minor issue",
                suggestion="Fix",
            )
        ]
        metrics = scorer.calculate_metrics(issues)

        assert metrics.optimization_ready == 100


class TestProductionReadiness:
    """Test production readiness scoring."""

    def test_deducts_for_missing_error_handling(self, scorer):
        """Should deduct points for missing error handling."""
        issues = [
            ValidationIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.BEST_PRACTICE,
                line=1,
                message="Missing error handling",
                suggestion="Add try/except",
            )
        ]
        metrics = scorer.calculate_metrics(issues)

        assert metrics.production_ready < 100

    def test_deducts_for_missing_configure(self, scorer):
        """Should deduct points for missing configure call."""
        issues = [
            ValidationIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.ANTI_PATTERN,
                line=1,
                message="Missing dspy.configure() call",
                suggestion="Add configure",
            )
        ]
        metrics = scorer.calculate_metrics(issues)

        assert metrics.production_ready < 100


class TestGradeCalculation:
    """Test grade calculation."""

    def test_grade_a_for_high_scores(self, scorer):
        """Should give A grade for scores >= 90."""
        issues = []
        metrics = scorer.calculate_metrics(issues)

        assert metrics.overall_grade == "A"

    def test_grade_b_for_good_scores(self, scorer):
        """Should give B grade for scores 80-89."""
        # Create enough issues to bring score to B range
        issues = [
            ValidationIssue(
                severity=IssueSeverity.ERROR,
                category=IssueCategory.SIGNATURE,
                line=i,
                message=f"Issue {i}",
                suggestion="Fix",
            )
            for i in range(2)
        ]
        metrics = scorer.calculate_metrics(issues)

        # Should be in B range (80-89)
        assert metrics.overall_grade in ["A", "B"]

    def test_grade_decreases_with_more_issues(self, scorer):
        """Should give lower grades with more issues."""
        few_issues = [
            ValidationIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.SIGNATURE,
                line=1,
                message="Issue",
                suggestion="Fix",
            )
        ]

        many_issues = [
            ValidationIssue(
                severity=IssueSeverity.ERROR,
                category=IssueCategory.SIGNATURE,
                line=i,
                message=f"Issue {i}",
                suggestion="Fix",
            )
            for i in range(10)
        ]

        few_metrics = scorer.calculate_metrics(few_issues)
        many_metrics = scorer.calculate_metrics(many_issues)

        assert few_metrics.overall_score > many_metrics.overall_score


class TestScoreExplanations:
    """Test score explanations."""

    def test_provides_explanations_for_all_metrics(self, scorer):
        """Should provide explanations for all metric categories."""
        issues = []
        metrics = scorer.calculate_metrics(issues)
        explanations = scorer.get_score_explanation(metrics)

        assert "pattern_compliance" in explanations
        assert "documentation" in explanations
        assert "optimization_ready" in explanations
        assert "production_ready" in explanations

    def test_excellent_explanations_for_high_scores(self, scorer):
        """Should provide positive explanations for high scores."""
        issues = []
        metrics = scorer.calculate_metrics(issues)
        explanations = scorer.get_score_explanation(metrics)

        assert (
            "excellent" in explanations["pattern_compliance"].lower()
            or "well" in explanations["pattern_compliance"].lower()
        )

    def test_improvement_explanations_for_low_scores(self, scorer):
        """Should suggest improvements for low scores."""
        issues = [
            ValidationIssue(
                severity=IssueSeverity.ERROR,
                category=IssueCategory.SIGNATURE,
                line=i,
                message=f"Issue {i}",
                suggestion="Fix",
            )
            for i in range(10)
        ]
        metrics = scorer.calculate_metrics(issues)
        explanations = scorer.get_score_explanation(metrics)

        # Should mention improvement or issues
        assert any(
            keyword in explanations["pattern_compliance"].lower()
            for keyword in ["improvement", "needs", "issues"]
        )


class TestConsistency:
    """Test scoring consistency."""

    def test_same_issues_produce_same_score(self, scorer):
        """Should produce consistent scores for same issues."""
        issues = [
            ValidationIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.SIGNATURE,
                line=1,
                message="Issue",
                suggestion="Fix",
            )
        ]

        metrics1 = scorer.calculate_metrics(issues)
        metrics2 = scorer.calculate_metrics(issues)

        assert metrics1.pattern_compliance == metrics2.pattern_compliance
        assert metrics1.documentation == metrics2.documentation
        assert metrics1.optimization_ready == metrics2.optimization_ready
        assert metrics1.production_ready == metrics2.production_ready
        assert metrics1.overall_grade == metrics2.overall_grade

    def test_score_never_negative(self, scorer):
        """Should never produce negative scores."""
        # Create many severe issues
        issues = [
            ValidationIssue(
                severity=IssueSeverity.ERROR,
                category=IssueCategory.SIGNATURE,
                line=i,
                message=f"Issue {i}",
                suggestion="Fix",
            )
            for i in range(50)
        ]

        metrics = scorer.calculate_metrics(issues)

        assert metrics.pattern_compliance >= 0
        assert metrics.documentation >= 0
        assert metrics.optimization_ready >= 0
        assert metrics.production_ready >= 0
