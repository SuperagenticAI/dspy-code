"""
DSPy Code Quality Scorer

Calculates quality metrics for DSPy code.
"""

from .models import IssueCategory, IssueSeverity, QualityMetrics, ValidationIssue


class QualityScorer:
    """Calculates quality scores for DSPy code."""

    def __init__(self):
        """Initialize the quality scorer."""
        self.weights = {
            "pattern_compliance": 0.35,
            "documentation": 0.20,
            "optimization_ready": 0.25,
            "production_ready": 0.20,
        }

    def calculate_metrics(self, issues: list[ValidationIssue]) -> QualityMetrics:
        """
        Calculate quality metrics based on validation issues.

        Args:
            issues: List of validation issues found in the code

        Returns:
            QualityMetrics with scores for each category
        """
        # Calculate individual scores
        pattern_score = self._calculate_pattern_compliance(issues)
        doc_score = self._calculate_documentation_score(issues)
        opt_score = self._calculate_optimization_readiness(issues)
        prod_score = self._calculate_production_readiness(issues)

        # Calculate overall grade
        overall = (
            pattern_score * self.weights["pattern_compliance"]
            + doc_score * self.weights["documentation"]
            + opt_score * self.weights["optimization_ready"]
            + prod_score * self.weights["production_ready"]
        )
        grade = self._score_to_grade(int(overall))

        return QualityMetrics(
            pattern_compliance=pattern_score,
            documentation=doc_score,
            optimization_ready=opt_score,
            production_ready=prod_score,
            overall_grade=grade,
        )

    def _calculate_pattern_compliance(self, issues: list[ValidationIssue]) -> int:
        """
        Calculate DSPy pattern compliance score (0-100).

        Checks for:
        - Proper signature structure
        - Module inheritance
        - Predictor usage
        - Anti-patterns
        """
        # Start with perfect score
        score = 100

        # Deduct points for pattern-related issues
        for issue in issues:
            if issue.category in [
                IssueCategory.SIGNATURE,
                IssueCategory.MODULE,
                IssueCategory.PREDICTOR,
                IssueCategory.ANTI_PATTERN,
            ]:
                if issue.severity == IssueSeverity.ERROR:
                    score -= 15
                elif issue.severity == IssueSeverity.WARNING:
                    score -= 8
                elif issue.severity == IssueSeverity.INFO:
                    score -= 3

        return max(0, score)

    def _calculate_documentation_score(self, issues: list[ValidationIssue]) -> int:
        """
        Calculate documentation completeness score (0-100).

        Checks for:
        - Docstrings
        - Field descriptions
        - Type hints
        """
        score = 100

        # Deduct points for documentation issues
        for issue in issues:
            if issue.category == IssueCategory.BEST_PRACTICE:
                if "docstring" in issue.message.lower() or "description" in issue.message.lower():
                    if issue.severity == IssueSeverity.ERROR:
                        score -= 12
                    elif issue.severity == IssueSeverity.WARNING:
                        score -= 7
                    elif issue.severity == IssueSeverity.INFO:
                        score -= 3

        return max(0, score)

    def _calculate_optimization_readiness(self, issues: list[ValidationIssue]) -> int:
        """
        Calculate optimization readiness score (0-100).

        Checks for:
        - Metric functions
        - Training data support
        - Proper signatures for optimization
        """
        score = 100

        # Deduct points for optimization-related issues
        for issue in issues:
            if "metric" in issue.message.lower() or "optimization" in issue.message.lower():
                if issue.severity == IssueSeverity.ERROR:
                    score -= 20
                elif issue.severity == IssueSeverity.WARNING:
                    score -= 10
                elif issue.severity == IssueSeverity.INFO:
                    score -= 5

        return max(0, score)

    def _calculate_production_readiness(self, issues: list[ValidationIssue]) -> int:
        """
        Calculate production readiness score (0-100).

        Checks for:
        - Error handling
        - Logging
        - Configuration
        - Save/load functionality
        """
        score = 100

        # Deduct points for production-related issues
        for issue in issues:
            if any(
                keyword in issue.message.lower()
                for keyword in ["error handling", "logging", "configure", "save", "load"]
            ):
                if issue.severity == IssueSeverity.ERROR:
                    score -= 15
                elif issue.severity == IssueSeverity.WARNING:
                    score -= 8
                elif issue.severity == IssueSeverity.INFO:
                    score -= 4

        return max(0, score)

    def _score_to_grade(self, score: int) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def get_score_explanation(self, metrics: QualityMetrics) -> dict:
        """
        Get explanations for each score.

        Args:
            metrics: Quality metrics to explain

        Returns:
            Dictionary with explanations for each metric
        """
        explanations = {}

        # Pattern compliance explanation
        if metrics.pattern_compliance >= 90:
            explanations["pattern_compliance"] = "Excellent DSPy pattern usage"
        elif metrics.pattern_compliance >= 70:
            explanations["pattern_compliance"] = "Good pattern usage with minor issues"
        else:
            explanations["pattern_compliance"] = "Needs improvement in DSPy patterns"

        # Documentation explanation
        if metrics.documentation >= 90:
            explanations["documentation"] = "Well documented code"
        elif metrics.documentation >= 70:
            explanations["documentation"] = "Adequate documentation, could be improved"
        else:
            explanations["documentation"] = "Missing or incomplete documentation"

        # Optimization readiness explanation
        if metrics.optimization_ready >= 90:
            explanations["optimization_ready"] = "Ready for optimization"
        elif metrics.optimization_ready >= 70:
            explanations["optimization_ready"] = "Mostly ready, add metrics for best results"
        else:
            explanations["optimization_ready"] = "Not ready for optimization"

        # Production readiness explanation
        if metrics.production_ready >= 90:
            explanations["production_ready"] = "Production ready"
        elif metrics.production_ready >= 70:
            explanations["production_ready"] = "Nearly production ready"
        else:
            explanations["production_ready"] = "Needs work before production"

        return explanations
